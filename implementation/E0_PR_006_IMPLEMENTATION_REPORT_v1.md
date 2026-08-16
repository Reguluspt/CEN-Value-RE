# E0-PR-006 — Local Service Bootstrap Boundary Implementation Report v1

**Date:** 2026-08-16
**Repository:** `Reguluspt/CEN-Value-RE`
**Branch:** `agent/e0-pr-006-local-service`
**Implementation baseline:** `f53d2f2b500e8a70a2e1a4b76bc7a699c7820c88`
**Final runtime-tested HEAD:** `0e8cd17c74017780e6ba82ec3ec46791f8130a8c`
**Binding GitHub Actions run:** `31958002783`
**Runtime:** Python `3.11.15`, Flask `3.1.1`
**Focused + foundation result:** `119 passed in 1.39s`

## 1. Scope implemented

E0-PR-006 adds only the Epic 0 local application-service/bootstrap boundary:

- loopback-only Flask adapter under `src/re/adapters/local_service/`;
- per-launch in-memory `launch_id` + bearer credential;
- structured security/session errors;
- protected health endpoints;
- testable local listener lifecycle and shutdown;
- a Tauri/local-service lifecycle contract;
- focused dependency pin `Flask==3.1.1` in `requirements-re.txt`;
- focused tests and runtime evidence.

No persistence, appraisal/business API, valuation formula, Excel runtime, UI feature, public-web deployment, or Tauri packaging/IPC implementation is included.

## 2. Architecture boundary

Flask/Werkzeug stay inside the RE adapter layer. Domain, Application and Ports do not import Flask or the local-service adapter. Existing architecture/import regression tests are part of the binding run.

`Reguluspt/New-project@cc6ad5fcc15703ae31fd9f2e8ee78c972f06d2ff` was used read-only as a compatibility reference for the legacy Flask pattern and dependency version. No code was written to that repository and its legacy `0.0.0.0` default bind behavior was deliberately not reused.

## 3. Loopback fail-closed boundary

`LocalServiceConfig` defaults to:

- host `127.0.0.1`;
- port `0`, letting the OS assign an ephemeral port.

The runtime accepts numeric loopback IPs only. Wildcard, LAN/public addresses and hostname-based bind targets are rejected. Runtime evidence independently exercised rejection of:

- `0.0.0.0`;
- `::`;
- `192.168.1.10`;
- `10.0.0.5`;
- `8.8.8.8`;
- `localhost`.

The live runtime probe confirmed an actual non-zero ephemeral port on `127.0.0.1` and confirmed that the listener was closed after shutdown.

## 4. Per-launch bootstrap/session contract

Every new `LaunchSession.issue()` creates:

- a new UUID-derived launch identifier;
- a high-entropy `secrets.token_urlsafe(32)` bearer token.

There is no fixed production password/default secret. The bearer token is excluded from `repr`, omitted from `public_metadata()`, and is not exposed by an HTTP bootstrap route. `LocalServiceRuntime` retains only the active `LaunchSession`; it does not keep a second `LaunchCredential` copy after constructing the bootstrap envelope.

The concrete Tauri sidecar/IPC transport is intentionally outside E0-PR-006. The frozen lifecycle contract requires the bootstrap envelope to travel through a supervisor-owned out-of-band mechanism, not an HTTP bootstrap endpoint, persisted file, fixed environment default, or ordinary log.

## 5. Authentication and stale-session behavior

Every `/api/re/health/*` route requires both:

- `X-CenValue-RE-Launch-ID`;
- `Authorization: Bearer <current-token>`.

Loopback presence is not treated as authentication.

Expected structured decisions:

- missing credentials → `401 / RE_SESSION_REQUIRED`;
- previous launch ID → `401 / RE_SESSION_STALE`;
- incorrect bearer token → `401 / RE_SESSION_INVALID`;
- revoked launch → `401 / RE_SESSION_REVOKED`;
- non-loopback remote address → `403 / RE_LOOPBACK_REQUIRED`.

Current valid credentials return `200` for both live and session health. Secret comparison uses `hmac.compare_digest`.

## 6. Lifecycle

`LocalServiceRuntime` implements a one-launch lifecycle:

`NEW -> RUNNING -> STOPPED`

A runtime can start only once. Shutdown revokes the active launch session before stopping and closing the listener. A stopped runtime cannot restart; a subsequent desktop launch must create a new runtime and therefore new credentials.

There is no HTTP shutdown route. Tauri remains the intended process supervisor.

## 7. Structured error contract

Security/application errors use the shape:

```json
{
  "error": {
    "code": "RE_SESSION_REQUIRED",
    "message": "..."
  }
}
```

Bearer credentials are never returned in the structured error envelope.

## 8. Verification history

Four workflow executions occurred during implementation. Only the final run is binding evidence.

### Run 1 — `31957616821`

Non-binding failure in the one-time CI harness while capturing Flask runtime version because of shell quoting. Compile/tests were not reached. Source acceptance was not inferred from this run.

### Run 2 — `31957687997`

Non-binding failure at the bounded-scope `git diff --check` gate due to trailing whitespace in the lifecycle Markdown. The hygiene failure was corrected without relaxing the gate. Pytest was not reached.

### Run 3 — `31957763104`

Successful run with `119 passed in 1.34s`, but it was deliberately superseded before review. A pre-review security check found that anonymous `/health/live` was an unnecessary exception to the frozen “unauthenticated session rejected” requirement. That evidence was deleted before the security tightening.

### Run 4 — `31958002783` — BINDING

Tested HEAD: `0e8cd17c74017780e6ba82ec3ec46791f8130a8c`

Result: `119 passed in 1.39s`.

The run established:

- compile PASS;
- bounded-scope / `git diff --check` PASS;
- architecture/import regressions PASS;
- E0-PR-003 Decimal/RoundingPolicy regressions PASS;
- E0-PR-004 ExcelTemplateProfile/Fingerprint regressions PASS;
- E0-PR-005 Golden Fixture regressions PASS;
- E0-PR-006 local-service tests PASS;
- all RE health endpoints reject anonymous requests;
- stale and invalid sessions reject;
- LAN remote access rejects;
- authenticated health succeeds;
- loopback/ephemeral listener succeeds;
- shutdown closes listener.

## 9. Binding runtime vectors

The final vector log records:

```text
bind_host=127.0.0.1
configured_port=0
actual_port_ephemeral=true
non_loopback_bind_rejected=true
launch_credentials_unique=true
secret_repr_redacted=true
http_bootstrap_route_present=false
http_shutdown_route_present=false
anonymous_live_status=401
anonymous_session_status=401
missing_session_code=RE_SESSION_REQUIRED
stale_session_code=RE_SESSION_STALE
invalid_session_code=RE_SESSION_INVALID
lan_remote_code=RE_LOOPBACK_REQUIRED
live_health_status=200
protected_health_status=200
shutdown_state=STOPPED
listener_closed=true
```

## 10. Evidence files

- `evidence/E0_PR_006_RUNTIME_EVIDENCE_v1.md`
- `evidence/E0-PR-006_tests_v1.log`
- `evidence/E0-PR-006_local_service_vectors_v1.log`
- `evidence/E0_PR_006_INDEPENDENT_REVIEW_HANDOFF_v1.md`
- this implementation report.

## 11. Gate

This report is implementation evidence, not self-acceptance. E0-PR-006 must remain unmerged and E0-PR-007 must not begin until an independent reviewer returns `ACCEPTED` against the exact review HEAD and the post-tested delta is verified as evidence/documentation-only.
