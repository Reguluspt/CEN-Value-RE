# E0-PR-002 — Apply and Verify v1

Baseline frontend inspected from `Reguluspt/New-project` main at:
`cc6ad5fcc15703ae31fd9f2e8ee78c972f06d2ff`

The PR-002 patch is frontend-only and does not overlap the accepted PR-001 backend skeleton.

## Apply
```bash
git apply --check E0-PR-002_ASTRYX_SPIKE_v1.patch
git apply E0-PR-002_ASTRYX_SPIKE_v1.patch
cd web
npm install --save-exact @astryxdesign/core@0.2.0 @astryxdesign/theme-neutral@0.2.0 @stylexjs/stylex@0.19.0
```

The install step must update `package-lock.json`; include that lockfile diff in the final implementation review payload.

## Verify
```bash
npm run verify:re-astryx
npm run lint
npm run build
```

Then start the app and execute `E0_PR_002_RUNTIME_ACCEPTANCE_CHECKLIST_v1.md`.

## Restrictions
Do not publish/push/merge/deploy unless the Project Owner explicitly authorizes it.
