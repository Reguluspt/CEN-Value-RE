# E0-PR-002 Runtime Evidence v2

**Date:** 2026-08-16  
**Repository:** `Reguluspt/CEN-Value-RE`  
**Implementation baseline:** `94ff266a3686b5b5bfd98cb55459dbe7a6cf24d8`  
**Tested input head:** `cc0e3c5699d53d0704f19a0a4132563ba07e639f`  
**GitHub Actions run:** `31948848497`

## Result
- Node 22.13.0: PASS
- static verifier: PASS
- scoped E0-PR-002 lint: PASS
- full legacy lint non-regression: PASS (88 errors baseline; 88 after; 0 unchanged-file regressions)
- production build: PASS
- unauthenticated `/re` redirect to `/login`: PASS
- guest `/re` redirect to `/sobo`: PASS
- admin `/re` render: PASS
- two Astryx `TextInput` controls: PASS
- client-side CSS isolation for `/dashboard` and `/cases`: PASS
- new browser page errors after visiting `/re`: 0
- new browser console errors after visiting `/re`: 0
- inherited legacy console deprecation messages are baseline debt and did not regress through the `/re` visit
- `node_modules/`: not version-controlled

## Acceptance
Corrective implementation evidence only. E0-PR-002 remains pending independent acceptance.
