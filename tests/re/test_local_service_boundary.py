"""E0-PR-006 acceptance tests for the local-service bootstrap boundary."""

from __future__ import annotations

import ast
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from src.re.adapters.local_service import (
    AUTHORIZATION_HEADER,
    LAUNCH_ID_HEADER,
    LaunchSession,
    LocalServiceConfig,
    LocalServiceRuntime,
    LocalServiceState,
    SessionDecision,
    create_local_service_app,
    validate_loopback_host,
)

RE_ROOT = Path(__file__).resolve().parents[2] / "src" / "re"


def _auth_headers(launch_id: str, bearer_token: str) -> dict[str, str]:
    return {
        LAUNCH_ID_HEADER: launch_id,
        AUTHORIZATION_HEADER: f"Bearer {bearer_token}",
    }


def _json(client_response):
    return client_response.get_json()


@pytest.mark.parametrize(
    "host",
    ("0.0.0.0", "::", "192.168.1.10", "10.0.0.5", "8.8.8.8", "localhost"),
)
def test_non_loopback_or_hostname_bind_targets_are_rejected(host: str) -> None:
    with pytest.raises(ValueError):
        LocalServiceConfig(host=host)


@pytest.mark.parametrize("host", ("127.0.0.1", "127.0.0.2", "::1"))
def test_numeric_loopback_bind_targets_are_accepted(host: str) -> None:
    assert validate_loopback_host(host)


def test_port_validation_fails_closed() -> None:
    for value in (-1, 65536):
        with pytest.raises(ValueError):
            LocalServiceConfig(port=value)
    for value in (True, "5000", 1.5):
        with pytest.raises(TypeError):
            LocalServiceConfig(port=value)  # type: ignore[arg-type]


def test_each_launch_uses_unique_non_default_credentials_and_repr_redacts_token() -> None:
    first_session, first = LaunchSession.issue()
    second_session, second = LaunchSession.issue()

    assert first.launch_id != second.launch_id
    assert first.bearer_token != second.bearer_token
    assert len(first.bearer_token) >= 40
    assert first.bearer_token not in repr(first)
    assert first_session.authorize(
        launch_id=first.launch_id,
        bearer_token=first.bearer_token,
    ) is SessionDecision.VALID
    assert second_session.authorize(
        launch_id=second.launch_id,
        bearer_token=second.bearer_token,
    ) is SessionDecision.VALID


def test_missing_invalid_stale_and_revoked_session_decisions() -> None:
    session, current = LaunchSession.issue()
    old_session, old = LaunchSession.issue()

    assert session.authorize(launch_id=None, bearer_token=None) is SessionDecision.REQUIRED
    assert session.authorize(
        launch_id=current.launch_id,
        bearer_token="wrong-token",
    ) is SessionDecision.INVALID
    assert session.authorize(
        launch_id=old.launch_id,
        bearer_token=old.bearer_token,
    ) is SessionDecision.STALE

    old_session.revoke()
    assert old_session.authorize(
        launch_id=old.launch_id,
        bearer_token=old.bearer_token,
    ) is SessionDecision.REVOKED


def test_live_health_requires_current_session_and_does_not_disclose_secret() -> None:
    session, credential = LaunchSession.issue()
    client = create_local_service_app(session).test_client()

    missing = client.get("/api/re/health/live")
    assert missing.status_code == 401
    assert _json(missing)["error"]["code"] == "RE_SESSION_REQUIRED"

    response = client.get(
        "/api/re/health/live",
        headers=_auth_headers(credential.launch_id, credential.bearer_token),
    )
    assert response.status_code == 200
    payload = _json(response)
    assert payload == {"service": "cenvalue-re", "status": "ok"}
    assert credential.bearer_token not in response.get_data(as_text=True)

    lan_response = client.get(
        "/api/re/health/live",
        headers=_auth_headers(credential.launch_id, credential.bearer_token),
        environ_base={"REMOTE_ADDR": "192.168.1.50"},
    )
    assert lan_response.status_code == 403
    assert _json(lan_response)["error"]["code"] == "RE_LOOPBACK_REQUIRED"


def test_protected_health_rejects_unauthenticated_invalid_and_stale_sessions() -> None:
    session, current = LaunchSession.issue()
    _, stale = LaunchSession.issue()
    client = create_local_service_app(session).test_client()

    missing = client.get("/api/re/health/session")
    assert missing.status_code == 401
    assert _json(missing)["error"]["code"] == "RE_SESSION_REQUIRED"

    invalid = client.get(
        "/api/re/health/session",
        headers=_auth_headers(current.launch_id, "not-the-secret"),
    )
    assert invalid.status_code == 401
    assert _json(invalid)["error"]["code"] == "RE_SESSION_INVALID"

    stale_response = client.get(
        "/api/re/health/session",
        headers=_auth_headers(stale.launch_id, stale.bearer_token),
    )
    assert stale_response.status_code == 401
    assert _json(stale_response)["error"]["code"] == "RE_SESSION_STALE"


def test_protected_health_accepts_only_current_credentials_and_never_returns_token() -> None:
    session, credential = LaunchSession.issue()
    client = create_local_service_app(session).test_client()

    response = client.get(
        "/api/re/health/session",
        headers=_auth_headers(credential.launch_id, credential.bearer_token),
    )
    assert response.status_code == 200
    payload = _json(response)
    assert payload["launch_id"] == credential.launch_id
    assert credential.bearer_token not in response.get_data(as_text=True)

    session.revoke()
    revoked = client.get(
        "/api/re/health/session",
        headers=_auth_headers(credential.launch_id, credential.bearer_token),
    )
    assert revoked.status_code == 401
    assert _json(revoked)["error"]["code"] == "RE_SESSION_REVOKED"


def test_no_http_bootstrap_or_shutdown_route_exists() -> None:
    session, credential = LaunchSession.issue()
    app = create_local_service_app(session)
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/api/re/bootstrap" not in rules
    assert "/api/re/shutdown" not in rules
    assert credential.bearer_token not in repr(app.url_map)


def test_structured_not_found_does_not_leak_secret() -> None:
    session, credential = LaunchSession.issue()
    client = create_local_service_app(session).test_client()
    response = client.get(
        "/api/re/does-not-exist",
        headers=_auth_headers(credential.launch_id, credential.bearer_token),
    )
    assert response.status_code == 404
    payload = _json(response)
    assert payload["error"]["code"] == "RE_NOT_FOUND"
    assert set(payload["error"]) == {"code", "message"}
    assert credential.bearer_token not in response.get_data(as_text=True)


def test_live_runtime_binds_loopback_ephemeral_port_and_serves_protected_health() -> None:
    runtime = LocalServiceRuntime(LocalServiceConfig(host="127.0.0.1", port=0))
    bootstrap = runtime.start()
    try:
        assert runtime.state is LocalServiceState.RUNNING
        assert bootstrap.base_url.startswith("http://127.0.0.1:")
        assert bootstrap.bearer_token not in repr(bootstrap)
        assert "bearer_token" not in bootstrap.public_metadata()

        live_request = Request(
            f"{bootstrap.base_url}/api/re/health/live",
            headers=_auth_headers(bootstrap.launch_id, bootstrap.bearer_token),
        )
        live = urlopen(live_request, timeout=3)
        assert live.status == 200

        request = Request(
            f"{bootstrap.base_url}/api/re/health/session",
            headers=_auth_headers(bootstrap.launch_id, bootstrap.bearer_token),
        )
        protected = urlopen(request, timeout=3)
        assert protected.status == 200
    finally:
        runtime.shutdown()

    assert runtime.state is LocalServiceState.STOPPED
    with pytest.raises(RuntimeError):
        runtime.start()


def test_live_runtime_rejects_missing_credentials() -> None:
    runtime = LocalServiceRuntime()
    bootstrap = runtime.start()
    try:
        with pytest.raises(HTTPError) as captured:
            urlopen(f"{bootstrap.base_url}/api/re/health/session", timeout=3)
        assert captured.value.code == 401
    finally:
        runtime.shutdown()


def test_framework_imports_are_confined_to_adapter_layer() -> None:
    violations: list[str] = []
    for relative_root in ("domain", "application", "ports"):
        root = RE_ROOT / relative_root
        for path in sorted(root.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    modules = [node.module or ""]
                else:
                    continue
                if any(module == "flask" or module.startswith("flask.") for module in modules):
                    violations.append(str(path.relative_to(RE_ROOT)))
    assert not violations, f"Flask escaped adapter layer: {violations}"
