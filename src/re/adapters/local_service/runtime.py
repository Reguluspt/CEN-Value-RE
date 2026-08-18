"""Tauri-supervised loopback runtime contract for the local Flask service."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from ipaddress import ip_address
from threading import Thread
from typing import Any

from werkzeug.serving import make_server

from .bootstrap import LaunchSession
from .flask_app import create_local_service_app


def validate_loopback_host(host: str) -> str:
    """Return a canonical loopback IP or reject the bind target."""
    if not isinstance(host, str) or not host.strip():
        raise ValueError("local service host must be a loopback IP address")
    try:
        address = ip_address(host.strip())
    except ValueError as exc:
        raise ValueError("local service host must be a loopback IP address") from exc
    if not address.is_loopback:
        raise ValueError("local service must not bind to a LAN/public/wildcard address")
    return address.compressed


@dataclass(frozen=True, slots=True)
class LocalServiceConfig:
    """Listener configuration. Port 0 requests an OS-assigned ephemeral port."""

    host: str = "127.0.0.1"
    port: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "host", validate_loopback_host(self.host))
        if isinstance(self.port, bool) or not isinstance(self.port, int):
            raise TypeError("local service port must be an integer")
        if not 0 <= self.port <= 65535:
            raise ValueError("local service port must be between 0 and 65535")


class LocalServiceState(str, Enum):
    NEW = "NEW"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"


@dataclass(frozen=True, slots=True)
class LocalServiceBootstrap:
    """One-launch bootstrap envelope delivered out-of-band to Tauri."""

    base_url: str
    launch_id: str
    bearer_token: str = field(repr=False)

    def public_metadata(self) -> dict[str, str]:
        """Return log-safe metadata. The bearer token is deliberately omitted."""
        return {"base_url": self.base_url, "launch_id": self.launch_id}


class LocalServiceRuntime:
    """Own one listener and exactly one launch session.

    Application capabilities are injected at composition time and are handed to
    the Flask adapter only when the one-launch listener is created. The runtime
    does not construct persistence or business services itself.

    A stopped runtime cannot be restarted. A new desktop launch must construct a
    new runtime, which necessarily creates a new launch ID and bearer token.
    """

    __slots__ = (
        "_config",
        "_manual_cases",
        "_manual_workbench",
        "_session",
        "_server",
        "_thread",
        "_state",
    )

    def __init__(
        self,
        config: LocalServiceConfig | None = None,
        *,
        manual_cases=None,
        manual_workbench=None,
    ) -> None:
        self._config = config or LocalServiceConfig()
        self._manual_cases = manual_cases
        self._manual_workbench = manual_workbench
        self._session: LaunchSession | None = None
        self._server: Any | None = None
        self._thread: Thread | None = None
        self._state = LocalServiceState.NEW

    @property
    def state(self) -> LocalServiceState:
        return self._state

    def start(self) -> LocalServiceBootstrap:
        if self._state is not LocalServiceState.NEW:
            raise RuntimeError("local service runtime can only be started once")

        session, credential = LaunchSession.issue()
        app = create_local_service_app(
            session,
            manual_cases=self._manual_cases,
            manual_workbench=self._manual_workbench,
        )
        server = make_server(
            self._config.host,
            self._config.port,
            app,
            threaded=True,
        )
        actual_port = int(server.server_port)
        thread = Thread(
            target=server.serve_forever,
            name="cenvalue-re-local-service",
            daemon=True,
        )

        self._session = session
        self._server = server
        self._thread = thread
        self._state = LocalServiceState.RUNNING
        thread.start()

        host_for_url = f"[{self._config.host}]" if ":" in self._config.host else self._config.host
        return LocalServiceBootstrap(
            base_url=f"http://{host_for_url}:{actual_port}",
            launch_id=credential.launch_id,
            bearer_token=credential.bearer_token,
        )

    def shutdown(self) -> None:
        """Revoke the launch session before closing the listener."""
        if self._state is LocalServiceState.STOPPED:
            return
        if self._state is LocalServiceState.NEW:
            self._state = LocalServiceState.STOPPED
            return

        assert self._session is not None
        assert self._server is not None
        assert self._thread is not None

        self._session.revoke()
        self._server.shutdown()
        self._thread.join(timeout=5)
        self._server.server_close()
        self._state = LocalServiceState.STOPPED
