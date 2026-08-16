# E0-PR-006 — Independent Review Handoff v1

**Date:** 2026-08-16
**Repository:** `Reguluspt/CEN-Value-RE`
**Branch:** `agent/e0-pr-006-local-service`
**Implementation baseline:** `f53d2f2b500e8a70a2e1a4b76bc7a699c7820c88`
**Runtime-tested HEAD:** `0e8cd17c74017780e6ba82ec3ec46791f8130a8c`
**Binding GitHub Actions run:** `31958002783`
**Runtime:** Python `3.11.15`, Flask `3.1.1`
**Result:** `119 passed in 1.39s`
**Decision requested:** `ACCEPTED` / `RETURN FINDINGS`

## Exact review-head rule

Before issuing a verdict, resolve the current PR HEAD directly from GitHub. If it differs from the review HEAD supplied with the PR/review request, stop and report `HEAD MISMATCH` until the delta is reviewed.

The final runtime-tested implementation HEAD is:

`0e8cd17c74017780e6ba82ec3ec46791f8130a8c`

Any delta after this commit must be limited to:

- successful final-run evidence/logs;
- removal of the one-time verification workflow;
- implementation report;
- independent-review handoff/documentation.

If source, tests, dependency pin or lifecycle contract changed after the tested HEAD without another full run, do not accept.

## Frozen authority

Review against:

- `epic-0/EPIC_0_PR_PLAN_v1.md` — E0-PR-006 scope and acceptance;
- `epic-0/EPIC_0_ACCEPTANCE_MATRIX_v1.md`;
- `epic-0/EPIC_0_ENGINEERING_FOUNDATION_PACKET_v1.md`;
- `gate-a/GATE_A2_RUNTIME_BOUNDARY.md`;
- `gate-a/GATE_A1_REPOSITORY_REUSE_AUDIT.md`;
- `Design Book/15_SECURITY_AND_PRIVACY.md`;
- `epic-0/E0_PR_006_TAURI_LIFECYCLE_CONTRACT_v1.md`.

`Reguluspt/New-project@cc6ad5fcc15703ae31fd9f2e8ee78c972f06d2ff` is a read-only compatibility reference only. The implementation repository is `CEN-Value-RE`.

## Expected implementation surface

- `src/re/adapters/local_service/__init__.py`
- `src/re/adapters/local_service/bootstrap.py`
- `src/re/adapters/local_service/flask_app.py`
- `src/re/adapters/local_service/runtime.py`
- `requirements-re.txt`
- `epic-0/E0_PR_006_TAURI_LIFECYCLE_CONTRACT_v1.md`
- `tests/re/test_local_service_boundary.py`
- evidence/report files.

## Required technical review

### 1. Scope / architecture

Confirm:

- Flask/Werkzeug are confined to adapter infrastructure;
- Domain/Application/Ports do not import Flask or `re.adapters.local_service`;
- no persistence or encrypted database implementation is included;
- no appraisal/business API or valuation formula is included;
- no Excel runtime/fill/recalculation is included;
- no UI feature or public-web deployment is included;
- no Tauri package/sidecar/IPC implementation is falsely claimed complete.

The Tauri integration in E0-PR-006 is a documented/testable lifecycle contract only. Concrete IPC/sidecar transport is intentionally deferred.

### 2. Loopback-only listener

Confirm `LocalServiceConfig`:

- defaults to `127.0.0.1`;
- defaults to port `0` for OS-assigned ephemeral binding;
- accepts numeric loopback addresses only;
- rejects wildcard, LAN/public and hostname bind targets.

At minimum independently probe rejection of:

- `0.0.0.0`;
- `::`;
- `192.168.1.10`;
- `10.0.0.5`;
- `8.8.8.8`;
- `localhost`.

Confirm the live runtime actually binds `127.0.0.1` on a non-zero ephemeral port and that the listener is closed after shutdown.

### 3. Per-launch bootstrap credential

Confirm every new launch generates fresh:

- `launch_id`;
- bearer token from `secrets.token_urlsafe(32)` or equivalent high-entropy mechanism.

Confirm:

- no fixed/default production password;
- bearer is excluded from `repr`;
- `public_metadata()` excludes bearer;
- no `/api/re/bootstrap` HTTP endpoint exists;
- bootstrap secret is not returned by health/error endpoints;
- `LocalServiceRuntime` does not retain an unnecessary second `LaunchCredential` copy after startup.

Review the lifecycle contract requirement that eventual Tauri integration passes the bootstrap envelope through supervisor-owned out-of-band transport, not HTTP bootstrap, persisted file, fixed environment default, or normal logs.

Do not fail E0-PR-006 merely because the concrete Tauri IPC implementation is deferred; do fail it if source/report claims that integration already exists.

### 4. Health authentication

All `/api/re/health/*` endpoints must require both:

- `X-CenValue-RE-Launch-ID`;
- `Authorization: Bearer <current bearer>`.

Loopback must not be treated as authentication.

Expected behavior:

- anonymous `/api/re/health/live` -> `401`, `RE_SESSION_REQUIRED`;
- anonymous `/api/re/health/session` -> `401`, `RE_SESSION_REQUIRED`;
- stale prior-launch ID -> `401`, `RE_SESSION_STALE`;
- current launch ID + wrong bearer -> `401`, `RE_SESSION_INVALID`;
- revoked session -> `401`, `RE_SESSION_REVOKED`;
- non-loopback remote -> `403`, `RE_LOOPBACK_REQUIRED`;
- valid current credential -> `200` for both health endpoints.

Confirm credential comparison is timing-safe (`hmac.compare_digest` or equivalent).

### 5. Lifecycle / shutdown

Confirm:

- state is effectively `NEW -> RUNNING -> STOPPED`;
- a runtime starts only once;
- shutdown revokes current session before server stop/close;
- listener is closed after shutdown;
- stopped runtime cannot restart;
- no `/api/re/shutdown` HTTP endpoint exists;
- Tauri remains intended process supervisor.

### 6. Structured errors and secret hygiene

Expected envelope:

```json
{
  "error": {
    "code": "RE_SESSION_REQUIRED",
    "message": "..."
  }
}
```

Confirm security error payloads do not contain bearer credentials and error codes distinguish required/stale/invalid/revoked/loopback failures.

### 7. Runtime / regressions

Binding run:

`31958002783`

Expected checked-out/tested HEAD:

`0e8cd17c74017780e6ba82ec3ec46791f8130a8c`

Expected runtime:

- Python `3.11.15`;
- Flask `3.1.1`;
- `119 passed in 1.39s`.

The run must include:

- architecture/import regressions;
- E0-PR-003 Decimal/RoundingPolicy regressions;
- E0-PR-004 ExcelTemplateProfile/Fingerprint regressions;
- E0-PR-005 Golden Fixture regressions;
- E0-PR-006 local-service tests;
- live listener/security vectors.

Binding vector log must establish:

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

### 8. Verification-history interpretation

Earlier workflow runs are not binding acceptance evidence:

- `31957616821`: CI shell quoting failure before substantive verification;
- `31957687997`: `git diff --check` correctly rejected lifecycle-document trailing whitespace before pytest;
- `31957763104`: successful but deliberately superseded by pre-review security tightening that removed anonymous liveness.

Only `31958002783` is binding for the final tested implementation.

### 9. Evidence binding

Compare the final runtime-tested HEAD to the exact current PR review HEAD. The post-test delta may contain only evidence/logs, one-time workflow removal, report and review handoff. There must be no untested change to:

- `src/re/adapters/local_service/*`;
- `requirements-re.txt`;
- `epic-0/E0_PR_006_TAURI_LIFECYCLE_CONTRACT_v1.md`;
- `tests/re/test_local_service_boundary.py`.

## Finding format

For each finding report:

- ID;
- severity: BLOCKER / HIGH / MEDIUM / LOW;
- exact file/path;
- exact issue;
- why it matters;
- required corrective action;
- acceptance test for closure.

Do not create blocking findings for cosmetic/style preference.

## Required verdict

If clean:

```text
FINDINGS
- NONE

VERDICT:
ACCEPTED

E0-PR-006 may proceed to merge and E0-PR-007 may begin after merge.
```

If findings exist:

```text
VERDICT:
RETURN FINDINGS

OPEN FINDINGS:
- ...

E0-PR-006 must not merge and E0-PR-007 must not begin until findings are closed.
```

E0-PR-006 is not self-accepted by the implementer.
