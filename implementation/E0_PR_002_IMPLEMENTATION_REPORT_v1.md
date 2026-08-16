# E0-PR-002 — Astryx Integration Spike — Implementation Report v1

**Date:** 2026-08-16  
**Status:** IMPLEMENTED; INDEPENDENT REVIEW FINDINGS F001/F002 CORRECTED; RE-REVIEW PENDING  
**Repository of record:** `Reguluspt/CEN-Value-RE`  
**Implementation baseline:** `94ff266a3686b5b5bfd98cb55459dbe7a6cf24d8`  
**External review that returned findings:** reviewed HEAD `96feb62572f6668c91b453f2a501569fbe9ed4f4`  
**Corrective tested input head:** `bbc7b3dea0bed562124a320149722623e3d72ca4`  
**Successful corrective run:** `31951150586` attempt 2  
**Legacy frontend provenance:** `Reguluspt/New-project@cc6ad5fcc15703ae31fd9f2e8ee78c972f06d2ff` (read-only reference imported by R1)  
**Publish status:** FEATURE BRANCH ONLY; NOT MERGED / NOT DEPLOYED

## Scope
This implementation remains limited to the Epic 0 Astryx integration spike:
- isolated `/re` frontend surface;
- exact Astryx v0.2.0 package pins + StyleX peer pin;
- Astryx `AppShell`, `SideNav`, `FormLayout`, `TextInput`, Neutral-theme tokens;
- strict CSS containment against the legacy Ant Design/global CSS surface;
- static + built-CSS architectural verification;
- reusable browser authorization/root-isolation harness;
- version-controlled `package-lock.json`.

No appraisal/domain formula, persistence, Excel runtime, API service, OCR/provider, or production business workflow is introduced.

## Implementation surface after findings corrective
- `.gitignore`
- `web/package.json`
- `web/package-lock.json`
- `web/src/App.jsx`
- `web/src/re/ReShell.jsx`
- `web/src/re/astryx.css`
- `web/scripts/generate-re-astryx-css.mjs`
- `web/scripts/scope-re-astryx-css.mjs`
- `web/scripts/verify-re-astryx-spike.mjs`
- `web/scripts/verify-re-astryx-built-css.mjs`
- `web/scripts/e0-pr-002-browser-smoke.mjs`
- implementation/evidence files.

Generated scoped vendor CSS under `web/src/re/generated/` is reproducible and intentionally ignored by Git.

## External independent review findings
The external reviewer returned:

### E0-PR-002-F001 — HIGH
Astryx core/theme CSS emitted global `:root` and `html[data-theme]` token selectors, mutating persistent `documentElement` custom properties after `/re` was lazy-loaded.

### E0-PR-002-F002 — MEDIUM
The prior static verifier inspected only locally authored CSS and the browser harness omitted document-root custom properties, so both missed F001.

Neither finding is self-closed here; this report records corrective implementation/evidence for independent re-review.

## Corrective containment design
1. **Raw vendor CSS is no longer imported directly by authored RE CSS.**
2. `scripts/generate-re-astryx-css.mjs` resolves the exact CSS exports from the exact pinned npm packages before `dev`, `build`, and static verification.
3. `scripts/scope-re-astryx-css.mjs` deterministically rewrites:
   - the 13 known Astryx core `:root, .x...` token rules to `.cenvalue-re-surface`-bounded selectors;
   - Neutral theme `:root` to `.cenvalue-re-surface`;
   - Neutral theme `html[data-theme="light|dark"]` to `.cenvalue-re-surface[data-theme="light|dark"]`.
4. The transformer **fails closed on vendor-selector contract drift** instead of silently passing an unknown Astryx CSS shape.
5. ReShell imports only the generated scoped CSS plus locally authored scoped CSS.
6. Astryx's root `Theme` provider is not mounted because Astryx v0.2.0 root Theme synchronizes `data-theme` and `data-astryx-theme` to `document.documentElement`. Theme attributes are instead placed only on `.cenvalue-re-surface`.
7. `@astryxdesign/core/reset.css` remains excluded.

## Dependency pins
- `@astryxdesign/core`: `0.2.0`
- `@astryxdesign/theme-neutral`: `0.2.0`
- `@stylexjs/stylex`: `0.19.0`

`node_modules/` is runtime-only and is not version-controlled. `web/package-lock.json` remains version-controlled.

## Corrective verification v3
GitHub Actions run `31951150586` attempt 2 tested exact corrective input head `bbc7b3dea0bed562124a320149722623e3d72ca4` using Node `22.13.0`.

Results:
- deterministic scoped-CSS generation from exact pinned packages: **PASS**;
- static Astryx verifier: **PASS**;
- no root Astryx `Theme` provider/documentElement sync path: **PASS**;
- scoped ESLint: **PASS**;
- full legacy lint non-regression: **PASS** (`88` baseline / `88` after / `0` unchanged-file regressions);
- production build: **PASS**;
- emitted `ReShell` CSS has no `:root`, `html[data-theme]`, or global `body` selector: **PASS**;
- expected Astryx token declarations remain in emitted scoped CSS: **PASS**;
- static negative control reproducing `:root { --border-width; --color-accent }`: **REJECTED as expected**;
- browser negative control reproducing the same root custom-property mutation: **REJECTED as expected**;
- unauthenticated `/re` -> `/login`: **PASS**;
- guest `/re` -> `/sobo`: **PASS**;
- admin `/re` render + two Astryx `TextInput` controls: **PASS in light and dark**;
- documentElement attributes + every computed root CSS custom property unchanged after client-side `/re` visit: **PASS in light and dark**;
- representative `/dashboard` and `/cases` styles unchanged after `/re`: **PASS in light and dark**;
- new browser page errors after `/re`: **0**;
- new browser console errors after `/re`: **0**.

Primary evidence: `evidence/E0_PR_002_RUNTIME_EVIDENCE_v3.md`.

## Negative-control evidence
`evidence/E0-PR-002_static_negative_control_v3.log` shows the static built-CSS gate explicitly rejects a CSS file containing the reviewer-observed root mutation.

`evidence/E0-PR-002_browser_negative_control_v3.log` shows the browser harness fails when `--border-width` and `--color-accent` are introduced on `:root`, including the before/after root custom-property diff.

The normal `evidence/E0-PR-002_browser_smoke_v3.log` then passes with the corrected implementation in both light and dark environments.

## Inherited baseline debt / non-scope observations
The imported legacy frontend still has existing ESLint debt and npm audit findings. E0-PR-002 preserves non-regression and does not auto-remediate unrelated dependency/application behavior.

## Acceptance status
**NOT SELF-ACCEPTED.** `E0-PR-002-F001` and `E0-PR-002-F002` require closure by the independent reviewer against the final corrective PR HEAD. Do not merge PR #3 and do not start E0-PR-003 until an independent `ACCEPTED` verdict is returned.
