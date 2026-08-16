# E0-PR-002 — Runtime Acceptance Checklist v1

**Gate:** Independent Review / Acceptance  
**Current status:** PENDING RUNTIME EVIDENCE

## Dependency and build
- [ ] Apply `E0-PR-002_ASTRYX_SPIKE_v1.patch` to the target worktree.
- [ ] From `web/`, install exact dependencies and commit the resulting `package-lock.json` update.
- [ ] `npm run verify:re-astryx` passes.
- [ ] `npm run lint` passes (or only pre-existing unrelated findings are separately evidenced).
- [ ] `npm run build` passes.

## Astryx surface
- [ ] Authenticate as an admin and open `/re`.
- [ ] Astryx AppShell renders.
- [ ] SideNav renders with the RE and legacy-dashboard entries.
- [ ] Neutral theme is visibly applied.
- [ ] Basic FormLayout renders two controlled TextInput fields.
- [ ] Inputs accept/edit text with no console errors.

## Legacy safety / CSS collision
- [ ] `/dashboard` renders identically before and after visiting `/re`.
- [ ] `/cases` renders identically before and after visiting `/re`.
- [ ] Existing Ant Design table header behavior remains intact.
- [ ] No global Astryx reset appears in the legacy document styles.
- [ ] No unexpected root/body typography or color-scheme regression.

## Architecture/scope
- [ ] `/re` does not use legacy `Layout`.
- [ ] RE component has no appraisal/domain calculation logic.
- [ ] RE component has no direct database/Excel/provider/API implementation access.
- [ ] No persistence/backend/Excel feature code is introduced by this PR.

## Verdict
Only an independent reviewer may change the gate to ACCEPTED after the checked evidence is attached.
