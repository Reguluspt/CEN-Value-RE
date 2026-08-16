# E0-PR-002 — Astryx Integration Spike — Implementation Report v1

**Date:** 2026-08-16  
**Status:** IMPLEMENTED; STATIC/RUNTIME EVIDENCE GREEN; INDEPENDENT ACCEPTANCE PENDING  
**Repository of record:** `Reguluspt/CEN-Value-RE`  
**Implementation baseline:** `94ff266a3686b5b5bfd98cb55459dbe7a6cf24d8`  
**Legacy frontend provenance:** `Reguluspt/New-project@cc6ad5fcc15703ae31fd9f2e8ee78c972f06d2ff` (read-only reference imported by R1)  
**Publish status:** FEATURE BRANCH ONLY; NOT MERGED / NOT DEPLOYED

## Scope
This implementation covers only the Epic 0 Astryx integration spike:
- isolated `/re` frontend surface;
- exact Astryx v0.2.0 package pins + StyleX peer pin;
- Astryx `AppShell`, `SideNav`, `FormLayout`, `TextInput`, Neutral theme;
- CSS collision containment against the legacy Ant Design/global CSS surface;
- static architectural verifier;
- reusable browser smoke/CSS-isolation harness;
- version-controlled `package-lock.json` updated by npm on a GitHub-hosted runner.

No appraisal/domain formula, persistence, Excel runtime, API service, OCR/provider, or production business workflow is introduced.

## Changed implementation files
- `web/package.json`
- `web/package-lock.json`
- `web/src/App.jsx`
- `web/src/re/ReShell.jsx` (new)
- `web/src/re/astryx.css` (new)
- `web/scripts/verify-re-astryx-spike.mjs` (new)
- `web/scripts/e0-pr-002-browser-smoke.mjs` (new)

Evidence files are stored under `evidence/`.

## Isolation strategy
- `/re` is protected by the existing `ProtectedRoute adminOnly` boundary.
- `/re` is lazy-loaded and intentionally not wrapped by the legacy Ant Design `Layout`.
- the RE shell imports only React, Astryx packages, and its local scoped stylesheet.
- `@astryxdesign/core/reset.css` is deliberately NOT imported because the Astryx reset is global and could alter legacy UI after the route chunk is loaded.
- a minimal compatibility reset is scoped to `.cenvalue-re-surface`.
- browser non-regression testing navigates client-side from legacy routes to `/re` and back, ensuring the lazy-loaded Astryx stylesheet remains present while legacy computed styles are compared.

## Dependency pins
- `@astryxdesign/core`: `0.2.0`
- `@astryxdesign/theme-neutral`: `0.2.0`
- `@stylexjs/stylex`: `0.19.0`

Pins are exact because Astryx is pre-1.0 and this spike must be reproducible.

`node_modules/` is runtime-only and is not version-controlled. `web/package-lock.json` is version-controlled.

## Runtime verification
Executed on GitHub Actions using Node `22.13.0` against the CEN-Value-RE implementation baseline.

Results:
- exact Astryx dependency install / lockfile update: **PASS**;
- `npm run verify:re-astryx`: **PASS**;
- scoped ESLint for E0-PR-002 JavaScript: **PASS**;
- full legacy lint non-regression: **PASS** (`88` inherited errors before, `88` after, `0` unchanged-file regressions);
- `npm run build`: **PASS**;
- `/re` browser smoke as mocked admin: **PASS**;
- two Astryx `TextInput` controls rendered: **PASS**;
- `/dashboard` computed styles unchanged after client-side visit to `/re`: **PASS**;
- `/cases` computed styles unchanged after client-side visit to `/re`: **PASS**;
- browser page errors: **0**.

Primary evidence: `evidence/E0_PR_002_RUNTIME_EVIDENCE_v1.md`.

## Inherited baseline debt / non-scope observations
The exact imported legacy frontend has existing ESLint debt. This PR uses a non-regression gate rather than expanding scope to repair unrelated legacy files.

The dependency installation also reports inherited npm audit findings. No automatic `npm audit fix` is performed in E0-PR-002 because that can modify dependency versions outside the bounded spike. Dependency-security remediation should be tracked as a separate hardening/corrective item if required by the release gate.

## Acceptance status
**NOT SELF-ACCEPTED.** Runtime implementation evidence is complete and should be submitted to independent review against the E0-PR-002 acceptance criteria. Do not start E0-PR-003 until E0-PR-002 receives the required acceptance verdict.
