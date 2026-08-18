# E1-PR-006 — Runtime Evidence v1

**Status:** BINDING IMPLEMENTATION EVIDENCE — NOT AN ACCEPTANCE VERDICT  
**Gate:** `ManualWorkbenchGate`  
**Accepted base:** `f68ce4c62280b2859b7db0e8f0fc75b52374bb67`  
**Runtime-tested implementation HEAD:** `96e6bba253f53242e00408fc3f5e21458ed21fd8`  
**Runtime tree:** `93ccb845db7ead34799d15d06a7aa48e3f4e093d`  
**Binding Windows run:** `32139803874`  
**Tested PR merge-ref:** `8b3529195ec64168bf5496edf8fb1907851be719`  
**Merge-ref tree:** `93ccb845db7ead34799d15d06a7aa48e3f4e093d`

## 1. Baseline binding

The binding run checked out GitHub PR #16 merge-ref `8b3529195ec64168bf5496edf8fb1907851be719`, whose parents are:

1. accepted `main` base `f68ce4c62280b2859b7db0e8f0fc75b52374bb67`;
2. runtime-tested branch HEAD `96e6bba253f53242e00408fc3f5e21458ed21fd8`.

The branch HEAD and tested merge-ref both resolve to tree:

`93ccb845db7ead34799d15d06a7aa48e3f4e093d`

Therefore the merge-ref did not introduce an untested conflict-resolution tree delta.

## 2. Runtime environment

GitHub Actions run `32139803874` completed successfully on:

- Microsoft Windows Server 2025 (`10.0.26100`);
- CPython `3.11.9`;
- Node.js `22.23.2`;
- pinned RE dependencies from `requirements-re.txt`, including `openpyxl==3.1.5`.

Dependency installation, `git diff --check`, and Python compilation all passed.

## 3. Python regression evidence

Full accepted RE regression:

`python -m pytest -q tests/re`

Result:

**254 passed in 7.57s**

Focused E1-PR-006 backend/live-listener proof:

`python -m pytest -q tests/re/test_manual_workbench_integration.py tests/re/test_manual_workbench_live_runtime.py tests/re/test_manual_case_data_backbone.py tests/re/test_local_service_boundary.py tests/re/test_architecture_boundaries.py`

Result:

**38 passed in 2.82s**

The focused proof covers the application workbench facade, protected local-service routes, exact percentage/explicit-zero semantics, current/stale resume behavior, trusted server-side rounding policy resolution, real ephemeral loopback listener dependency injection, E0 launch-session security vectors, and architecture import boundaries.

## 4. Astryx / frontend boundary evidence

The accepted Astryx isolation verifier and E1-PR-006 workbench boundary verifier both passed.

The run confirms:

- accepted Astryx package pins and `/re` isolation remain intact;
- `/re` remains admin-protected, lazy-loaded, and outside the legacy Ant Design `Layout`;
- RE CSS does not introduce global `:root`, `html[data-theme]`, or `body` mutations;
- generated Astryx vendor CSS remains scoped to `.cenvalue-re-surface`;
- the workbench uses the bounded credentialed `/api/re` client;
- bootstrap data remains in memory only;
- absent or non-loopback bootstrap fails closed;
- display percentage conversion uses exact decimal-string arithmetic;
- explicit zero remains distinct from missing.

The frontend changed-source scope guard also passed: E1-PR-006 did not modify legacy frontend source outside `web/src/re`.

Scoped lint over the E1-PR-006 frontend source and smoke harness passed.

## 5. Browser-level vertical smoke

A real headless Chromium/Edge page was launched on the Windows runner through the Chrome DevTools Protocol. The browser mounted the actual Astryx `ReShell` workbench.

The browser smoke exercised the visible manual sequence through request boundaries:

`Create Case → TSTĐ → TSSS01/02/03 → Adjustment → Quality → Human Indication → Final Valuation → Workbook Request`

The browser proof verifies:

- the in-memory launch ID and bearer are attached to every `/api/re` request;
- browser calls remain bounded under `/api/re`;
- `0.5%` display input becomes canonical fraction string `0.005` without binary-float conversion;
- reload/resume restores persisted subject/comparable presentation state;
- an explicit persisted C1 `0%` decision remains visibly entered rather than missing;
- submitting that decision sends canonical selected rate `"0"`;
- a canonical structured `409` workbook error renders its code/message without bearer leakage;
- a successful workbook response renders `workbook_generated=true` while preserving `excel_qualification_status=NOT_RUN`.

The browser harness mocks the transport responses only. It does **not** replace the independent backend/application proof above: valuation calculations, currentness, persistence behavior, local-service authorization, and live listener behavior are covered by the Python suites. The browser smoke proves presentation/client wiring and vertical request semantics.

## 6. Frontend build / inherited observations

Production Vite build passed.

Repository-wide `npm run lint` was retained as an explicit non-gating inherited-baseline observation. It reports:

**96 problems (88 errors, 8 warnings)**

in legacy frontend source outside the isolated E1-PR-006 RE change surface. E1-PR-006 changed-source scope enforcement and scoped lint both passed. This evidence does not declare the inherited repository-wide lint debt resolved.

`npm ci` also reported **5 high severity vulnerabilities** in the inherited frontend dependency graph. This run records the observation; E1-PR-006 does not claim to remediate or waive those dependencies, and the independent reviewer may assess scope/materiality.

## 7. Qualification boundary

No part of this GitHub-hosted run is Microsoft Excel Desktop qualification evidence.

Workbook-generation success remains:

- `WorkbookGenerated = true` when generation succeeds;
- `excel_qualification_status = NOT_RUN`.

E1-PR-007 remains the real Microsoft Excel Desktop/reference-workbook qualification and Epic 1 closure gate.

## 8. Superseded runs

Earlier E1-PR-006 runs are non-binding for final review because later implementation/proof changes were made.

In particular:

- run `32138548919` passed before browser-level acceptance proof was added;
- run `32139495550` proved the browser vertical smoke but failed scoped lint on a smoke-harness-only useless assignment;
- the one-line lint correction changed the implementation tree and therefore required run `32139803874`.

Only run `32139803874` is the binding runtime evidence for runtime-tested HEAD `96e6bba253f53242e00408fc3f5e21458ed21fd8`.
