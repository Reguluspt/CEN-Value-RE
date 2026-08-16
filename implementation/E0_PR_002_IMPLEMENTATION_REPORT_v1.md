# E0-PR-002 — Astryx Integration Spike — Implementation Report v1

**Date:** 2026-08-16  
**Status:** SERVER PAYLOAD PREPARED; STATIC GUARD GREEN; RUNTIME BUILD/RENDER EVIDENCE PENDING  
**Repository baseline inspected:** `Reguluspt/New-project` `main` at `cc6ad5fcc15703ae31fd9f2e8ee78c972f06d2ff`  
**Publish status:** NOT PUBLISHED

## Scope
This payload implements only the Epic 0 Astryx integration spike:
- isolated `/re` frontend surface;
- exact Astryx v0.2.0 package pins + StyleX peer pin;
- Astryx `AppShell`, `SideNav`, `FormLayout`, `TextInput`, Neutral theme;
- CSS collision containment against the legacy Ant Design/global CSS surface;
- static architectural verifier for the spike.

No appraisal/domain formula, persistence, Excel runtime, API service, OCR/provider, or production business workflow is introduced.

## Changed files
- `web/package.json`
- `web/src/App.jsx`
- `web/src/re/ReShell.jsx` (new)
- `web/src/re/astryx.css` (new)
- `web/scripts/verify-re-astryx-spike.mjs` (new)

## Isolation strategy
- `/re` is protected by the existing `ProtectedRoute adminOnly` boundary.
- `/re` is lazy-loaded and intentionally not wrapped by the legacy Ant Design `Layout`.
- the RE shell imports only React, Astryx packages, and its local scoped stylesheet.
- `@astryxdesign/core/reset.css` is deliberately NOT imported because the Astryx reset is global and could alter legacy UI after the route chunk is loaded.
- a minimal compatibility reset is scoped to `.cenvalue-re-surface`.

## Dependency pins
- `@astryxdesign/core`: `0.2.0`
- `@astryxdesign/theme-neutral`: `0.2.0`
- `@stylexjs/stylex`: `0.19.0`

Pins are exact because Astryx is pre-1.0 and this spike must be reproducible.

## Static verification
Command:
`cd web && npm run verify:re-astryx`

Equivalent direct command used on the server payload:
`node scripts/verify-re-astryx-spike.mjs`

Observed result: **PASSED**.

The verifier checks:
- exact dependency pins;
- `/re` protected/lazy route;
- route is outside legacy `Layout`;
- required Astryx components are present;
- RE shell has no Ant Design/domain/API imports;
- no global Astryx reset, `:root`, or global `body` override enters the RE stylesheet.

## Server limitation / open acceptance evidence
The execution server cannot resolve `github.com` or the npm registry through its shell network. Therefore this session cannot honestly generate/update `web/package-lock.json`, install Astryx packages, run Vite build, or capture browser render evidence.

This is an evidence limitation, not a declared runtime PASS. Before independent acceptance, a networked worktree must:
1. apply this patch;
2. run `npm install --save-exact @astryxdesign/core@0.2.0 @astryxdesign/theme-neutral@0.2.0 @stylexjs/stylex@0.19.0` from `web/` to update the lockfile;
3. run `npm run verify:re-astryx`;
4. run `npm run build` and `npm run lint`;
5. render `/re` as an admin user;
6. verify legacy `/dashboard`, `/cases`, and other Ant Design routes remain visually/functionally unchanged before and after visiting `/re`.

## Acceptance status
**NOT SELF-ACCEPTED.** Submit runtime evidence to independent review against E0-PR-002 acceptance criteria.
