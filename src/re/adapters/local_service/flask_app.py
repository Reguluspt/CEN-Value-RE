"""Flask adapter for the loopback-only CenValue RE local service."""

from __future__ import annotations

from ipaddress import ip_address
from typing import Final

from flask import Blueprint, Flask, jsonify, request

from .bootstrap import LaunchSession, SessionDecision

AUTHORIZATION_HEADER: Final = "Authorization"
LAUNCH_ID_HEADER: Final = "X-CenValue-RE-Launch-ID"
_BEARER_PREFIX: Final = "Bearer "


def _error(code: str, message: str, status: int):
    return jsonify({"error": {"code": code, "message": message}}), status


def _is_loopback_remote(remote_addr: str | None) -> bool:
    if not remote_addr:
        return False
    try:
        return ip_address(remote_addr).is_loopback
    except ValueError:
        return False


def _bearer_token() -> str | None:
    value = request.headers.get(AUTHORIZATION_HEADER)
    if not value or not value.startswith(_BEARER_PREFIX):
        return None
    token = value[len(_BEARER_PREFIX) :].strip()
    return token or None


def create_re_blueprint(
    session: LaunchSession,
    manual_cases=None,
    manual_workbench=None,
) -> Blueprint:
    """Create the bounded RE HTTP surface for one process launch."""
    blueprint = Blueprint("cenvalue_re_local", __name__, url_prefix="/api/re")

    @blueprint.before_request
    def enforce_local_boundary():
        if not _is_loopback_remote(request.remote_addr):
            return _error(
                "RE_LOOPBACK_REQUIRED",
                "CenValue RE local service accepts loopback requests only.",
                403,
            )

        decision = session.authorize(
            launch_id=request.headers.get(LAUNCH_ID_HEADER),
            bearer_token=_bearer_token(),
        )
        if decision is SessionDecision.VALID:
            return None

        errors = {
            SessionDecision.REQUIRED: (
                "RE_SESSION_REQUIRED",
                "A current launch session credential is required.",
            ),
            SessionDecision.STALE: (
                "RE_SESSION_STALE",
                "The supplied launch session is stale.",
            ),
            SessionDecision.INVALID: (
                "RE_SESSION_INVALID",
                "The supplied launch session credential is invalid.",
            ),
            SessionDecision.REVOKED: (
                "RE_SESSION_REVOKED",
                "The launch session is no longer active.",
            ),
        }
        code, message = errors[decision]
        return _error(code, message, 401)

    @blueprint.get("/health/live")
    def live_health():
        return jsonify({"service": "cenvalue-re", "status": "ok"})

    @blueprint.get("/health/session")
    def session_health():
        return jsonify(
            {
                "service": "cenvalue-re",
                "status": "ok",
                "launch_id": session.launch_id,
            }
        )

    if manual_cases is not None:
        from .manual_case_routes import register_manual_case_routes

        register_manual_case_routes(blueprint, manual_cases)

    if manual_workbench is not None:
        from .workbench_routes import register_workbench_routes

        register_workbench_routes(blueprint, manual_workbench)

    return blueprint


def create_local_service_app(
    session: LaunchSession,
    manual_cases=None,
    manual_workbench=None,
) -> Flask:
    """Create the standalone local Flask application-service boundary."""
    app = Flask("cenvalue_re_local_service")
    app.register_blueprint(
        create_re_blueprint(
            session,
            manual_cases=manual_cases,
            manual_workbench=manual_workbench,
        )
    )

    @app.errorhandler(404)
    def not_found(_error_value):
        return _error("RE_NOT_FOUND", "The requested local-service route was not found.", 404)

    @app.errorhandler(405)
    def method_not_allowed(_error_value):
        return _error("RE_METHOD_NOT_ALLOWED", "The HTTP method is not allowed.", 405)

    @app.errorhandler(500)
    def internal_error(_error_value):
        return _error("RE_INTERNAL_ERROR", "The local service could not complete the request.", 500)

    return app
