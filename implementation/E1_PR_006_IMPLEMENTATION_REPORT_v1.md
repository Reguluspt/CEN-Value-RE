# E1-PR-006 — Implementation Report v1

**Status:** IMPLEMENTATION COMPLETE — AWAITING INDEPENDENT REVIEW  
**Gate:** `ManualWorkbenchGate`  
**Accepted base:** `f68ce4c62280b2859b7db0e8f0fc75b52374bb67`  
**Runtime-tested implementation HEAD:** `96e6bba253f53242e00408fc3f5e21458ed21fd8`  
**Binding Windows run:** `32139803874`

## 1. Purpose

E1-PR-006 exposes the accepted Epic 1 manual Walking Skeleton through the protected local loopback service and the isolated Astryx `/re` workbench.

The implemented sequence is:

`Create Case → TSTĐ → TSSS01/02/03 → C1–C11 → Quality → Human Indication → Final Valuation → Workbook Export`

This PR integrates accepted E1-PR-001 through E1-PR-005 application behavior. It does not move valuation authority into Flask or React and does not claim Microsoft Excel Desktop qualification.

## 2. Application workbench facade

`src/re/application/services/manual_workbench.py` provides the bounded orchestration/read boundary required by the manual UI.

It:

- resumes the canonical manual-case snapshot;
- reconstructs current per-comparable adjustment state from persisted source state and explicit decisions;
- preserves explicit `0` as an entered human decision distinct from missing;
- exposes a current adjustment snapshot only when source revision, decision-set binding, calculation inputs, and semantic hash still match;
- delegates adjustment calculation to the accepted E1-PR-002 service;
- delegates quality/readiness and human indication to accepted E1-PR-003 services;
- delegates construction binding/final composition/current resolution to accepted E1-PR-004 services;
- delegates workbook generation to accepted E1-PR-005;
- resolves trusted template-default rounding policy server-side rather than accepting frontend calculation authority.

No valuation formula is duplicated in the workbench facade.

## 3. Local-service adapter

`src/re/adapters/local_service/workbench_routes.py` adds thin `/api/re` transport endpoints for the workbench capabilities.

The routes remain behind the existing E0 loopback/session `before_request` guard. They translate JSON/request data into application calls and structured response/error envelopes; they do not query SQL or calculate appraisal results.

`flask_app.py` composes the optional workbench routes without weakening existing health/manual-case behavior.

`runtime.py` now accepts application-service dependencies through constructor injection and supplies them to the real loopback listener at start. The runtime still owns only listener/session lifecycle; it does not construct persistence or business services internally.

A real ephemeral-loopback test verifies that workbench routes are available through `LocalServiceRuntime`, not only Flask `test_client` composition.

## 4. Astryx manual workbench

The previous `/re` integration spike has been replaced with an eight-stage manual workbench in `web/src/re/ReShell.jsx`.

The UI:

- creates/resumes manual cases;
- captures TSTĐ and exactly TSSS01/02/03;
- allows explicit human C1–C11 selections;
- visually distinguishes explicit `0%` from missing;
- invokes adjustment calculation only through the local-service API;
- reads quality/readiness returned by application authority;
- requires an explicit human indication action;
- binds the supplied/precomputed construction aggregate and requests final composition;
- requests supported-profile workbook generation and renders the returned artifact metadata;
- explicitly states that generated workbook success leaves Excel qualification `NOT_RUN`.

Results shown by the UI are local-service/application responses rather than frontend recomputations.

## 5. Credential and transport boundary

`web/src/re/localServiceClient.js` accepts one supervisor-provided bootstrap envelope in memory:

- `base_url`;
- `launch_id`;
- `bearer_token`.

The client:

- rejects absent bootstrap;
- accepts only HTTP numeric loopback origins;
- does not use localStorage/sessionStorage/cookies/files for credentials;
- rejects paths outside `/api/re/`;
- attaches the current launch ID and bearer on every request;
- converts structured local-service failures to bounded `ReLocalServiceError` values.

No HTTP bootstrap endpoint was added. Concrete production Tauri IPC/sidecar delivery remains outside E1-PR-006, as frozen in the contract.

## 6. Exact percentage semantics

`web/src/re/percent.js` converts percentage display strings to canonical fractional decimal strings without `parseFloat`, `Number`, or other binary floating-point calculation.

Required examples are preserved:

- blank → missing;
- `0` → `"0"`;
- `5` → `"0.05"`;
- `0.5` → `"0.005"`;
- `-5` → `"-0.05"`.

Resume conversion maps canonical fractions back to display percentages while preserving explicit zero.

Both static boundary verification and real-browser vertical smoke exercise this behavior.

## 7. Resume/currentness behavior

The workbench reconstructs presentation state from persisted/application evidence instead of browser-local calculation state.

Earlier manual inputs remain resumable even when downstream evidence becomes stale. Current result snapshots are exposed only when the accepted upstream currentness/binding conditions still hold; stale calculation output is represented as unavailable rather than silently reused.

Tests explicitly cover current versus stale adjustment resume state and explicit-zero restoration.

## 8. Astryx isolation

The accepted E0 Astryx CSS isolation remains intact:

- `/re` stays lazy-loaded/admin-protected and outside the legacy `Layout`;
- generated Astryx vendor CSS remains scoped under `.cenvalue-re-surface`;
- RE-authored CSS does not introduce `:root`, document-theme, or global-body mutations;
- existing isolation verification was extended for the Manual Workbench rather than weakened.

No E1-PR-006 frontend source change occurs outside `web/src/re`.

## 9. Browser vertical proof

E1-PR-006 adds a browser smoke harness and a no-new-dependency Chrome DevTools Protocol driver.

The Windows verifier starts Vite and a real installed Chromium/Edge browser, mounts the actual workbench, and exercises the UI request path through workbook generation.

The browser harness mocks transport responses so that the UI/client wiring can be proven deterministically without replacing backend evidence. Backend calculations/currentness/security remain covered by Python application/live-listener tests.

The browser proof covers:

- create, subject, three comparables;
- exact `0.5% → 0.005` request conversion;
- reload/resume;
- explicit persisted `0%` rendering/submission;
- adjustment/quality/human-indication/final requests;
- structured error rendering without token leakage;
- successful workbook response with `excel_qualification_status=NOT_RUN`;
- `/api/re` and credential headers for all browser requests.

## 10. Runtime evidence

Binding Windows run: `32139803874`

- Windows Server 2025;
- CPython 3.11.9;
- Node 22.23.2;
- dependency install PASS;
- `git diff --check` PASS;
- Python compile PASS;
- full `tests/re`: **254 passed in 7.57s**;
- focused backend/live listener: **38 passed in 2.82s**;
- Astryx/workbench static boundary verification PASS;
- real-browser vertical smoke PASS;
- changed-frontend scope guard PASS;
- scoped E1 frontend lint PASS;
- production Vite build PASS.

Runtime-tested HEAD `96e6bba253f53242e00408fc3f5e21458ed21fd8` and tested merge-ref `8b3529195ec64168bf5496edf8fb1907851be719` share tree `93ccb845db7ead34799d15d06a7aa48e3f4e093d`.

## 11. Inherited observations

Repository-wide legacy frontend lint still reports **96 problems (88 errors, 8 warnings)** outside the isolated E1 change surface. The verifier retains this as a non-gating observation while separately enforcing changed-source scope and scoped E1 lint.

`npm ci` reports **5 high severity vulnerabilities** in the inherited frontend dependency graph. No dependency pin was changed by E1-PR-006. This report records the observation and does not self-waive independent review of its materiality.

## 12. Explicit non-scope / qualification boundary

E1-PR-006 does not implement or claim:

- Microsoft Excel Desktop/reference-workbook qualification;
- E1-PR-007 or Epic 1 closure;
- production Tauri IPC/sidecar credential transport beyond the accepted in-memory boundary;
- approval return/revision import;
- CTXD engine;
- OCR/Maps;
- Historical Learning/AI;
- generic workbook-family rewriting or generic external-link repair.

`ManualWorkbenchGate` is **not self-accepted** by this implementation report.
