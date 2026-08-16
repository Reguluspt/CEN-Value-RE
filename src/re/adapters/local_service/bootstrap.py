"""Per-launch in-memory bootstrap credential for the local RE service."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hmac
import secrets
import uuid


class SessionDecision(str, Enum):
    """Authorization outcome for one local-service request."""

    VALID = "VALID"
    REQUIRED = "REQUIRED"
    STALE = "STALE"
    INVALID = "INVALID"
    REVOKED = "REVOKED"


@dataclass(frozen=True, slots=True)
class LaunchCredential:
    """Credential handed once to the supervising desktop host.

    The bearer token is intentionally excluded from repr. It is never a
    production default and must remain process-memory-only.
    """

    launch_id: str
    bearer_token: str = field(repr=False)


class LaunchSession:
    """Single-process, single-launch authorization state."""

    __slots__ = ("_launch_id", "_bearer_token", "_revoked")

    def __init__(self, launch_id: str, bearer_token: str) -> None:
        if not launch_id:
            raise ValueError("launch_id must be non-empty")
        if not bearer_token:
            raise ValueError("bearer_token must be non-empty")
        self._launch_id = launch_id
        self._bearer_token = bearer_token
        self._revoked = False

    @classmethod
    def issue(cls) -> tuple["LaunchSession", LaunchCredential]:
        """Create a fresh per-launch ID and a high-entropy bearer token."""
        launch_id = uuid.uuid4().hex
        bearer_token = secrets.token_urlsafe(32)
        session = cls(launch_id, bearer_token)
        return session, LaunchCredential(launch_id=launch_id, bearer_token=bearer_token)

    @property
    def launch_id(self) -> str:
        return self._launch_id

    @property
    def revoked(self) -> bool:
        return self._revoked

    def revoke(self) -> None:
        """Invalidate the current launch before the listener is shut down."""
        self._revoked = True

    def authorize(
        self,
        *,
        launch_id: str | None,
        bearer_token: str | None,
    ) -> SessionDecision:
        """Fail closed for missing, stale, invalid, or revoked credentials."""
        if self._revoked:
            return SessionDecision.REVOKED
        if not launch_id or not bearer_token:
            return SessionDecision.REQUIRED
        if not hmac.compare_digest(launch_id, self._launch_id):
            return SessionDecision.STALE
        if not hmac.compare_digest(bearer_token, self._bearer_token):
            return SessionDecision.INVALID
        return SessionDecision.VALID
