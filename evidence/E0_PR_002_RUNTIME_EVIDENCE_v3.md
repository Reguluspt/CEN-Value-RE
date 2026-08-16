# E0-PR-002 Runtime Evidence v3 — Independent Review Findings Corrective

**Date:** 2026-08-16  
**Repository:** `Reguluspt/CEN-Value-RE`  
**Implementation baseline:** `94ff266a3686b5b5bfd98cb55459dbe7a6cf24d8`  
**Corrective tested input head:** `bbc7b3dea0bed562124a320149722623e3d72ca4`  
**GitHub Actions run:** `31951150586` (attempt 2)

## Findings targeted
- `E0-PR-002-F001` HIGH — Astryx vendor CSS mutated document `:root` / `html[data-theme]`.
- `E0-PR-002-F002` MEDIUM — verifier/browser harness did not detect resolved/built root mutation.

## Corrective design
- `scripts/generate-re-astryx-css.mjs` resolves the exact pinned Astryx CSS exports before `dev`, `build`, and static verification.
- `scripts/scope-re-astryx-css.mjs` deterministically rewrites the known vendor global token selectors onto `.cenvalue-re-surface` and fails closed if the pinned vendor selector contract drifts.
- Generated scoped vendor CSS is ignored by Git and imported by `ReShell`; raw Astryx vendor CSS is no longer directly imported into application CSS.
- Astryx root `Theme` provider is not mounted because Astryx v0.2.0 root Theme synchronizes attributes to `document.documentElement`; `data-theme` and `data-astryx-theme` are instead applied only to `.cenvalue-re-surface`.

## Corrective result
- Node 22.13.0: PASS
- resolved raw vendor CSS exposes the expected global-selector negative control before rewrite: PASS
- deterministic pre-build generator rewrites Astryx token globals to `.cenvalue-re-surface`: PASS
- Astryx root `Theme` provider/documentElement sync path removed from RE shell: PASS
- scoped E0-PR-002 lint: PASS
- full legacy lint non-regression: PASS (88 errors baseline; 88 after; 0 unchanged-file regressions)
- production build: PASS
- emitted ReShell CSS contains no `:root`, `html[data-theme]`, or global `body` selector: PASS
- emitted ReShell CSS still contains expected Astryx token declarations including `--border-width` and `--color-accent`: PASS
- static negative control with the known `:root { --border-width; --color-accent }` mutation: REJECTED as expected
- browser negative control with the same root custom-property mutation: REJECTED as expected
- unauthenticated `/re` -> `/login`: PASS
- guest `/re` -> `/sobo`: PASS
- admin `/re` render: PASS in light and dark environments
- two Astryx `TextInput` controls: PASS in light and dark environments
- `documentElement` attributes + every computed root CSS custom property unchanged after client-side `/re` visit: PASS in light and dark environments
- representative `/dashboard` and `/cases` computed styles unchanged after `/re`: PASS in light and dark environments
- new browser page errors after `/re`: 0
- new browser console errors after `/re`: 0
- `node_modules/`: not version-controlled
- generated scoped CSS under `web/src/re/generated/`: not version-controlled and reproducible from exact pinned packages

## Primary evidence files
- `evidence/E0-PR-002_static_verification_runtime_v3.log`
- `evidence/E0-PR-002_build_v3.log`
- `evidence/E0-PR-002_built_css_verification_v3.log`
- `evidence/E0-PR-002_static_negative_control_v3.log`
- `evidence/E0-PR-002_browser_negative_control_v3.log`
- `evidence/E0-PR-002_browser_smoke_v3.log`
- `evidence/E0-PR-002_lint_nonregression_v3.json`

## Gate
Corrective implementation evidence only. `E0-PR-002-F001` and `E0-PR-002-F002` require independent reviewer closure; E0-PR-002 remains **NOT SELF-ACCEPTED** and must not merge until re-review returns an acceptance verdict bound to the final review head.
