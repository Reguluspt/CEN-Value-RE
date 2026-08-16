# CenValue RE — Epic 0 PR Plan v1
**Status:** DESIGN PACKET

## Proposed sequence

### E0-PR-001 — RE Domain Skeleton + Import Boundaries
Scope:
- create `src/re` bounded packages;
- define dependency/import guard;
- add domain common primitives;
- no business feature UI.

Acceptance:
- domain imports no Flask/Tauri/Excel/database framework;
- tests enforce import boundary.

### E0-PR-002 — Astryx Integration Spike
Scope:
- isolated `/re` frontend shell;
- official Astryx packages/theme;
- App Shell/Side Nav/basic Form;
- CSS collision audit with Ant Design/global styles.

Acceptance:
- legacy UI unaffected;
- RE shell renders with Astryx;
- no domain logic in components.

### E0-PR-003 — Decimal + RoundingPolicy
Scope:
- Money/Percentage/UnitPrice value objects;
- `RoundingPolicy`;
- profile default + case override resolver.

Acceptance:
- exact tests for NONE/1k/10k/100k/1m/10m/custom;
- N08-0038 default values reproduce 196,308,000 and 19,581,000,000.

### E0-PR-004 — ExcelTemplateProfile + Fingerprint
Scope:
- profile schema;
- required sheets;
- normalized formula signatures;
- compatibility-transform metadata;
- unsupported-template fail-safe.

Acceptance:
- exemplar matches;
- deliberate formula mutation is rejected.

### E0-PR-005 — Golden Fixture Harness
Scope:
- load canonical fixture/checkpoint manifest;
- per-checkpoint rounding/tolerance;
- report pass/fail without needing Excel desktop.

Acceptance:
- fixture loads deterministically;
- expected checkpoint set versioned.

### E0-PR-006 — Local Service Bootstrap Boundary
Scope:
- loopback-only local Flask RE blueprint/health;
- per-launch bootstrap/session contract;
- structured errors.

Acceptance:
- no LAN bind;
- unauthenticated/stale session rejected;
- Tauri lifecycle contract documented/testable.

### E0-PR-007 — Encrypted RE Persistence Foundation
Scope:
- separate RE DB;
- migrations;
- repository interfaces;
- encrypted-at-rest implementation;
- Windows key protection adapter baseline.

Acceptance:
- create/migrate/open through repositories;
- no plaintext key;
- legacy `cases` unchanged.

### E0-PR-008 — Excel Qualification Harness Skeleton
Scope:
- Windows qualification command/report schema;
- Excel COM runner interface;
- skip/not-qualified behavior when Excel unavailable.

Acceptance:
- cannot report PASS without actual Excel evidence;
- report includes profile/hash/checkpoints/version.

## Merge gate
No PR advances to appraisal feature work until all Epic 0 acceptance rows are satisfied.

## Deployment restriction
> **Governance supersession — 2026-08-16:** the latest Project Owner/session-handoff decision supersedes the earlier mandatory-local-worktree gate. Implementation/verification may be performed server-first; `H:\CEN Manage` is no longer a mandatory gate. The restriction on publishing to GitHub/VPS without explicit Project Owner instruction remains in force.

Historical repository rule recorded by this v1 packet: implementation was originally expected to be applied/verified in `H:\CEN Manage` first.
