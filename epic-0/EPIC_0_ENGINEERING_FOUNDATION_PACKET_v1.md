# CenValue RE — Epic 0 Engineering Foundation Packet v1
**Gate:** Post Gate-B
**Status:** READY FOR IMPLEMENTATION

## Objective
Create the minimum production-grade foundation on which the CenValue RE Walking Skeleton can be built without coupling domain logic to legacy Excel, Flask, Tauri, or Astryx APIs.

## Work packages

### E0-01 — Repository baseline & module boundaries
Create/confirm boundaries:
- desktop shell;
- frontend;
- local application/API service;
- `domain` package;
- persistence adapter;
- Excel adapter/profile package;
- tests/fixtures.

Rule: domain package imports no UI, Flask/Tauri, Excel or database framework.

### E0-02 — Astryx integration spike
Using official Astryx packages/documentation:
- integrate Astryx into one isolated React/Vite screen;
- establish theme and CSS cascade order;
- verify App Shell/Side Nav/Form primitives;
- document Ant Design/global CSS collision handling;
- do not globally migrate the legacy UI.

Acceptance: isolated CenValue RE shell renders without CSS collision and business components remain framework-independent.

### E0-03 — Local service boundary
- loopback only;
- Tauri-supervised service lifecycle;
- per-launch session/bootstrap credential;
- no production fixed default password;
- health/startup/shutdown behavior;
- structured error contract.

### E0-04 — Encrypted persistence foundation
- separate RE database;
- explicit migration versioning;
- encrypted SQLite-family implementation;
- Windows user-scoped protected key strategy;
- repository interfaces for Case/Subject/Comparable/Construction/Adjustment/Approval;
- soft-delete/archive baseline.

Exact crypto/database binding is implementation-selected but must satisfy Gate A.4.

### E0-05 — Decimal + RoundingPolicy primitives
Implement framework-independent:
- money/decimal value objects;
- percentage value handling;
- `RoundingPolicy`;
- NEAREST increment calculation;
- raw vs rounded value separation;
- template default + case override resolution.

Tests include 1k/10k/100k/1m/10m/custom and N08-0038 golden values.

### E0-06 — ExcelTemplateProfile infrastructure
Implement:
- profile identity/version;
- required sheets;
- formula signature normalization/hash;
- cell classes;
- compatibility transformations;
- unsupported-template fail-safe;
- external-link classification metadata.

Do not implement the full workbook adapter yet.

### E0-07 — Golden fixture harness
Load canonical fixture + expected checkpoint manifest.
Provide test interfaces so Epic 1 calculation modules can assert checkpoint compatibility without requiring Excel for ordinary unit tests.

### E0-08 — Windows Excel qualification harness skeleton
Define executable interface/report schema for a future Windows+Excel recalculation run.
The first foundation PR may mock/skip actual Excel COM execution when Excel is unavailable, but release qualification must not be marked PASS without real Excel evidence.

## Definition of Done
- boundaries documented and enforced by tests/import checks;
- frontend Astryx spike passes;
- local service loopback/session baseline passes;
- encrypted DB opens/migrates through repository abstraction;
- RoundingPolicy unit tests pass;
- template fingerprint detects exemplar and rejects a deliberately mutated signature;
- golden fixture loads;
- no secrets/plaintext key committed;
- CI green.

## Explicitly NOT in Epic 0
- complete TSTĐ UI;
- TSSS entry UI;
- Adjustment Grid;
- CTXD valuation UI;
- GCN OCR/QR/VBDLIS;
- Historical Learning runtime;
- approval workbook round-trip;
- AI providers.

Those start in later Epic/PR packets after the foundation is accepted.

## First implementation sequence
1. E0-01
2. E0-02
3. E0-05
4. E0-06
5. E0-07
6. E0-03
7. E0-04
8. E0-08

This sequence front-loads architecture/UI/calculation risks without prematurely building appraisal features.
