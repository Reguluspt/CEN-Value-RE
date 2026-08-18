# E1-PR-006 — Independent Review Handoff v1

**Review target:** E1-PR-006 — Local Service + Astryx Manual Workbench Integration  
**PR:** #16  
**Gate:** `ManualWorkbenchGate`  
**Status:** READY FOR INDEPENDENT REVIEW AFTER ONE-TIME VERIFIER REMOVAL — NOT SELF-ACCEPTED

## 1. Exact accepted base

Accepted base for this review:

`f68ce4c62280b2859b7db0e8f0fc75b52374bb67`

This is the protected merge of independently accepted PR #17, the E1-PR-005 deterministic package metadata hotfix.

The original E1-PR-006 implementation began from `be537e573d6692c6cbfaf5a6cb3710ad7c229177`, but the branch was subsequently merged forward onto accepted `main` `f68ce4c...` and final runtime evidence was rerun on that accepted base.

## 2. Binding runtime baseline

Runtime-tested implementation HEAD:

`96e6bba253f53242e00408fc3f5e21458ed21fd8`

Binding Windows run:

`32139803874`

Binding runtime tree:

`93ccb845db7ead34799d15d06a7aa48e3f4e093d`

Tested PR merge-ref:

`8b3529195ec64168bf5496edf8fb1907851be719`

The merge-ref has the same tree:

`93ccb845db7ead34799d15d06a7aa48e3f4e093d`

The independent reviewer must resolve PR #16 HEAD directly from GitHub before review and again immediately before verdict.

## 3. Binding evidence summary

GitHub Actions run `32139803874` on Windows Server 2025 / CPython 3.11.9 / Node 22.23.2 completed successfully.

Binding results:

- dependency install PASS;
- diff hygiene PASS against accepted base `f68ce4c...`;
- Python compile PASS;
- full `tests/re`: **254 passed in 7.57s**;
- focused E1-PR-006 backend/live-listener suite: **38 passed in 2.82s**;
- Astryx isolation verification PASS;
- workbench boundary verification PASS;
- real-browser vertical smoke PASS;
- frontend changed-source scope guard PASS;
- scoped E1 frontend lint PASS;
- production Vite build PASS.

The browser smoke mounts the actual Astryx `ReShell` in a real headless Chromium/Edge process and verifies create/subject/TSSS/adjustment/quality/indication/final/workbook request wiring, reload/resume, exact percentage conversion, explicit zero, structured error rendering, credential headers, and the `NOT_RUN` Excel qualification boundary.

Browser transport responses are deterministic mocks. The reviewer must treat them as UI/client integration evidence, not as a substitute for the separate Python application/currentness/live-listener evidence.

## 4. Review focus

The independent review should verify at least the following.

### A. Architecture authority

- React/Astryx is presentation only;
- Flask routes are transport only;
- no valuation formula is reimplemented in frontend or Flask;
- application/domain services remain calculation/currentness authority;
- no direct SQL/persistence or concrete Excel adapter dependency crosses into the frontend/transport logic.

### B. Local-service security

- all new HTTP capabilities remain under `/api/re`;
- existing loopback and launch-session authorization applies to every new route;
- no anonymous HTTP bootstrap or shutdown path was introduced;
- no credential persistence/fixed fallback exists in frontend code;
- error responses do not leak bearer credentials;
- live runtime dependency injection does not move service construction/persistence responsibility into the listener runtime.

### C. Human authority / exact adjustment semantics

- C1–C11 selection remains explicit human action;
- explicit `0` is distinct from missing across resume/UI/API;
- percentage display conversion uses exact decimal strings and does not introduce binary floating point;
- stale/incomplete decisions cannot be presented as a current calculation snapshot;
- system quality/guidance does not auto-confirm the human indication.

### D. Currentness / resume

- reload/resume is reconstructed from canonical persisted/application evidence;
- stale downstream evidence becomes unavailable rather than silently reused;
- current adjustment/final snapshots are exposed only when upstream bindings remain current;
- resume does not make browser-local state authoritative.

### E. Rounding authority

- template-default rounding increments are resolved server-side from the accepted profile;
- frontend does not hard-code trusted calculation increments;
- any case override remains explicit and typed under accepted upstream rules.

### F. Astryx isolation

- `/re` stays admin-protected, lazy-loaded, and outside legacy layout;
- scoped Astryx CSS does not mutate document-root tokens/global body/theme selectors;
- E0 isolation verification has not been weakened;
- E1 changed frontend source remains isolated under `web/src/re`.

### G. Workbook boundary

- UI only requests E1-PR-005 workbook generation;
- template/output paths remain explicit request inputs but workbook qualification/currentness is enforced by application/writer authority;
- generation response does not claim Microsoft Excel qualification PASS;
- `excel_qualification_status=NOT_RUN` remains visible/unchanged;
- E1-PR-007 remains the real Excel Desktop/reference-workbook qualification and Epic 1 closure gate.

### H. Browser evidence

- smoke driver actually launches a real browser rather than evaluating source statically;
- smoke mounts the real `ReShell` and drives DOM controls;
- request capture proves headers and exact request bodies;
- reload/resume and explicit-zero behavior are exercised after a real page navigation;
- structured 409 error and successful `NOT_RUN` response are rendered through the same production client/error path;
- smoke mocks transport only and does not falsely claim backend business calculation evidence.

## 5. Inherited observations requiring reviewer awareness

The binding run records two inherited repository observations:

1. full repository frontend lint: **96 problems (88 errors, 8 warnings)** in legacy frontend source outside E1's isolated change surface;
2. `npm ci`: **5 high severity vulnerabilities** in the inherited frontend dependency graph.

E1-PR-006 did not modify `package.json` or `package-lock.json`. Changed-source scope guard and scoped E1 lint pass. The implementation does not self-waive these observations; the reviewer should determine whether either creates an E1-PR-006 acceptance finding under the frozen scope.

## 6. Post-runtime delta rule

After runtime-tested HEAD `96e6bba253f53242e00408fc3f5e21458ed21fd8`, only the following changes are permitted before independent review:

1. `evidence/E1_PR_006_RUNTIME_EVIDENCE_v1.md`;
2. `implementation/E1_PR_006_IMPLEMENTATION_REPORT_v1.md`;
3. this independent-review handoff;
4. removal of `.github/workflows/e1-pr-006-verify.yml`.

Any later source, test, dependency, contract, browser-harness, CSS, route, runtime composition, or runtime-bearing configuration change invalidates run `32139803874` as binding acceptance evidence and requires a new run.

## 7. Independence / verdict

The implementer/Lead does not declare `ManualWorkbenchGate` PASS.

The independent reviewer should issue only the verdict required by the project review protocol and bind it to the exact resolved current PR #16 HEAD.

Acceptance of E1-PR-006 does **not** mean Microsoft Excel Desktop qualification PASS and does **not** close Epic 1.

If accepted, PR #16 should only be merged with expected-head protection on the independently accepted review HEAD. E1-PR-007 may begin only after that protected merge establishes the next accepted `main` base.
