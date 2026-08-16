# E0-PR-002 — Astryx Integration Spike — Implementation Report v1

**Date:** 2026-08-16  
**Status:** IMPLEMENTED; CORRECTIVE STATIC/RUNTIME EVIDENCE GREEN; INDEPENDENT ACCEPTANCE PENDING  
**Repository of record:** `Reguluspt/CEN-Value-RE`  
**Implementation baseline:** `94ff266a3686b5b5bfd98cb55459dbe7a6cf24d8`  
**Corrective tested input head:** `cc0e3c5699d53d0704f19a0a4132563ba07e639f`  
**Successful corrective run:** `31948848497`  
**Legacy frontend provenance:** `Reguluspt/New-project@cc6ad5fcc15703ae31fd9f2e8ee78c972f06d2ff` (read-only reference imported by R1)  
**Publish status:** FEATURE BRANCH ONLY; NOT MERGED / NOT DEPLOYED

## Scope
This implementation covers only the Epic 0 Astryx integration spike:
- isolated `/re` frontend surface;
- exact Astryx v0.2.0 package pins + StyleX peer pin;
- Astryx `AppShell`, `SideNav`, `FormLayout`, `TextInput`, Neutral theme;
- CSS collision containment against the legacy Ant Design/global CSS surface;
- static architectural verifier;
- reusable browser authorization/CSS-isolation harness;
- version-controlled `package-lock.json`.

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

## Isolation and authorization strategy
- `/re` is protected by the existing `ProtectedRoute adminOnly` boundary.
- `/re` is lazy-loaded and intentionally not wrapped by the legacy Ant Design `Layout`.
- the RE shell imports only React, Astryx packages, and its local scoped stylesheet.
- `@astryxdesign/core/reset.css` is deliberately NOT imported because the reset is global and could alter legacy UI after the `/re` chunk is loaded.
- a minimal compatibility reset is scoped to `.cenvalue-re-surface`.
- browser non-regression testing navigates client-side from legacy routes to `/re` and back, keeping the lazy-loaded Astryx stylesheet present while legacy computed styles are compared.
- browser authorization testing independently verifies unauthenticated `/re` redirects to `/login` and guest `/re` redirects to `/sobo`; neither may render the Astryx marker.

## Dependency pins
- `@astryxdesign/core`: `0.2.0`
- `@astryxdesign/theme-neutral`: `0.2.0`
- `@stylexjs/stylex`: `0.19.0`

Pins are exact because Astryx is pre-1.0 and this spike must be reproducible.

`node_modules/` is runtime-only and is not version-controlled. `web/package-lock.json` is version-controlled.

## Corrective runtime verification v2
Executed on GitHub Actions using Node `22.13.0`. The successful run is `31948848497`, tested against exact input head `cc0e3c5699d53d0704f19a0a4132563ba07e639f`.

Results:
- `npm run verify:re-astryx`: **PASS**;
- scoped ESLint for E0-PR-002 JavaScript: **PASS**;
- full legacy lint non-regression: **PASS** (`88` inherited errors baseline, `88` after, `0` unchanged-file regressions);
- `npm run build`: **PASS**;
- unauthenticated `/re` redirect to `/login`: **PASS**;
- guest `/re` redirect to `/sobo`: **PASS**;
- `/re` browser render as mocked admin: **PASS**;
- two Astryx `TextInput` controls rendered: **PASS**;
- `/dashboard` computed styles unchanged after client-side visit to `/re`: **PASS**;
- `/cases` computed styles unchanged after client-side visit to `/re`: **PASS**;
- new browser page errors after `/re`: **0**;
- new browser console errors after `/re`: **0**.

The legacy routes emit five unique Ant Design deprecation messages before `/re` is visited. The browser gate records these as inherited baseline debt and fails only if a new console-error message appears after the `/re` visit. It does not whitelist warning text.

Primary evidence: `evidence/E0_PR_002_RUNTIME_EVIDENCE_v2.md`.  
Independent review handoff: `evidence/E0_PR_002_INDEPENDENT_REVIEW_HANDOFF_v2.md`.

## Corrective harness history
Three harness issues were isolated and corrected without weakening product acceptance:
1. Playwright package resolution when the script ran outside its installation root.
2. broad `**/api/**` interception catching frontend modules under `/src/api/`.
3. absolute zero-console-error gating treating inherited legacy Ant Design deprecations as E0-PR-002 regressions.

The v2 gate uses isolated Playwright installation, backend-only API interception, explicit negative authorization checks, client-side CSS-isolation checks, and console-error non-regression.

## Inherited baseline debt / non-scope observations
The exact imported legacy frontend has existing ESLint debt. This PR uses a non-regression gate rather than expanding scope to repair unrelated legacy files.

Dependency installation also reports inherited npm audit findings. No automatic `npm audit fix` is performed in E0-PR-002 because that can modify dependency versions outside the bounded spike. Dependency-security remediation should be tracked as a separate hardening/corrective item if required by the release gate.

## Acceptance status
**NOT SELF-ACCEPTED.** Runtime implementation evidence is complete and must be independently reviewed. Do not merge or start E0-PR-003 until E0-PR-002 receives the required independent acceptance verdict bound to the exact reviewed PR head.
