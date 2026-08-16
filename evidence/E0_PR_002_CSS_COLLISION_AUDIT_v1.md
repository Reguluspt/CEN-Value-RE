# E0-PR-002 — Astryx / Legacy CSS Collision Audit v1

**Date:** 2026-08-16  
**Status:** SOURCE-LEVEL MITIGATION IMPLEMENTED; BROWSER CONFIRMATION PENDING

## Legacy baseline observed
The existing frontend uses Ant Design and a global `web/src/index.css` that applies:
- `:root` typography, colors and `color-scheme`;
- global `body` / `#root` layout;
- global `h1`, `h2`, `p`, `code` rules;
- an Ant Design table-header override.

## Astryx risk
Astryx v0.2.0's standard quick-start imports `reset.css`, `astryx.css`, then Neutral theme CSS. The official reset is intentionally global and resets box model, typography, lists, form controls, buttons, tables and other HTML primitives.

Loading that reset into the existing application would create avoidable risk that legacy Ant Design screens change after the `/re` bundle is visited.

## Mitigation selected for the spike
1. `/re` is a lazy route.
2. RE is not wrapped by legacy `Layout`.
3. Load Astryx component CSS and Neutral theme CSS only in the RE route chunk.
4. Do not import Astryx global `reset.css`.
5. Recreate only the minimum reset required by the spike under `.cenvalue-re-surface`.
6. Do not define global `:root`, `body`, Ant Design selectors, or legacy component selectors in RE CSS.
7. Use Astryx `Text` instead of relying on legacy global heading rules.

## Static proof
`web/scripts/verify-re-astryx-spike.mjs` rejects:
- a global Astryx reset import;
- `:root` or global `body` rules in RE CSS;
- legacy `Layout` around `/re`;
- Ant Design/domain/API imports in the RE shell.

Server result: static verification PASSED.

## Browser acceptance checklist
Browser evidence is still required:
- open legacy `/dashboard`; capture baseline;
- open `/re`; confirm AppShell, SideNav and both TextInputs render/use Neutral theme;
- navigate back to `/dashboard` and `/cases`; confirm no typography/layout/form/table regression;
- repeat light/dark/system color-scheme where supported;
- verify browser console has no Astryx/theme errors;
- verify keyboard focus and inputs operate normally.

No browser PASS is claimed by this document.
