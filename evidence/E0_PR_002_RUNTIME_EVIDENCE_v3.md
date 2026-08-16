# E0-PR-002 Runtime Evidence v3 — Independent Review Findings Corrective

**Date:** 2026-08-16  
**Repository:** `Reguluspt/CEN-Value-RE`  
**Implementation baseline:** `94ff266a3686b5b5bfd98cb55459dbe7a6cf24d8`  
**Corrective tested input head:** `bbc7b3dea0bed562124a320149722623e3d72ca4`  
**GitHub Actions run:** `31951150586`

## Findings targeted
- `E0-PR-002-F001` HIGH — Astryx vendor CSS mutated document `:root` / `html[data-theme]`.
- `E0-PR-002-F002` MEDIUM — verifier/browser harness did not detect resolved/built root mutation.

## Corrective result
- Node 22.13.0: PASS
- resolved vendor CSS negative-control globals detected before transform: PASS
- Vite pre-transform rewrites Astryx token globals to `.cenvalue-re-surface`: PASS
- Astryx root `Theme` provider/documentElement sync path removed from RE shell: PASS
- scoped E0-PR-002 lint: PASS
- full legacy lint non-regression: PASS (88 errors baseline; 88 after; 0 unchanged-file regressions)
- production build: PASS
- emitted ReShell CSS contains no `:root`, `html[data-theme]`, or global `body` selector: PASS
- static negative control with the known `:root { --border-width; --color-accent }` mutation: REJECTED as expected
- browser negative control with the same root custom-property mutation: REJECTED as expected
- unauthenticated `/re` -> `/login`: PASS
- guest `/re` -> `/sobo`: PASS
- admin `/re` render: PASS in light and dark environments
- two Astryx `TextInput` controls: PASS in light and dark environments
- documentElement attributes + all computed root CSS custom properties unchanged after client-side `/re` visit: PASS in light and dark environments
- representative `/dashboard` and `/cases` computed styles unchanged after `/re`: PASS in light and dark environments
- new browser page errors after `/re`: 0
- new browser console errors after `/re`: 0
- `node_modules/`: not version-controlled

## Gate
Corrective implementation evidence only. Findings require independent reviewer closure; E0-PR-002 remains not self-accepted.
