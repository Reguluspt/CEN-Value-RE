# E0-PR-006 — Tauri / Local-Service Lifecycle Contract v1

**Status:** IMPLEMENTATION CONTRACT
**Baseline:** `f53d2f2b500e8a70a2e1a4b76bc7a699c7820c88`

## Boundary

Tauri owns the desktop/process lifecycle. The Python service is transitional Flask
infrastructure and is not part of the RE Domain/Application core.

The service:

- binds only to a numeric loopback address (`127.0.0.0/8` or `::1`);
- defaults to `127.0.0.1` and port `0` (OS-assigned ephemeral port);
- refuses wildcard, LAN and public bind addresses;
- creates a fresh launch ID and high-entropy bearer token for every runtime;
- keeps the bearer token in process memory only;
- exposes no HTTP route that issues or returns the bearer token;
- revokes the launch session before listener shutdown.

## Supervisor bootstrap

`LocalServiceRuntime.start()` returns an in-memory bootstrap envelope containing:

- `base_url`;
- `launch_id`;
- `bearer_token`.

The concrete Tauri sidecar/IPC transport is intentionally deferred. Integration
must deliver this envelope through a supervisor-owned out-of-band channel that is
not an HTTP bootstrap endpoint, persisted file, fixed environment default, or
ordinary application log.

Only `public_metadata()` is log-safe; it excludes the bearer token.

## Request contract

Protected RE routes require both:

- `X-CenValue-RE-Launch-ID: <current launch id>`
- `Authorization: Bearer <current launch bearer token>`

A launch ID from a previous process launch is stale even if paired with its old
token. Missing, stale, invalid and revoked credentials are rejected.

## Health

- `GET /api/re/health/live` is credential-protected liveness and returns no
  credential/session data.
- `GET /api/re/health/session` is credential-protected and confirms the current
  launch ID.
- No RE HTTP route is anonymously accessible; loopback binding is not treated as
  an authentication mechanism.

There is no HTTP shutdown route. Tauri supervises process shutdown; the runtime
revokes its launch session before closing the listener.

## Structured error envelope

Errors use:

```json
{
  "error": {
    "code": "RE_SESSION_REQUIRED",
    "message": "..."
  }
}
```

Security-relevant codes include:

- `RE_LOOPBACK_REQUIRED`
- `RE_SESSION_REQUIRED`
- `RE_SESSION_STALE`
- `RE_SESSION_INVALID`
- `RE_SESSION_REVOKED`

The error payload never includes the bearer token.

## Testable lifecycle

1. `NEW -> RUNNING` occurs once.
2. Start binds a validated loopback IP and returns an ephemeral endpoint/credential.
3. Correct current credentials reach protected health.
4. Missing credentials reject.
5. Previous-launch ID rejects as stale.
6. Wrong bearer rejects.
7. Non-loopback remote addresses reject even inside the Flask request layer.
8. `shutdown()` revokes the session and closes the listener.
9. A stopped runtime cannot restart; the next launch requires a new runtime and credential.
