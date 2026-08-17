# Epic 1 — Manual Walking Skeleton Acceptance Matrix v1

**Status:** ACCEPTANCE BASELINE — DERIVED FROM FROZEN GATE B
**Baseline:** `df14f1c1ee845734dc58c0e63f42d12db3d54155`

## 1. Gate philosophy

Epic 1 acceptance is evidence-driven and fail-closed.

- A unit test cannot substitute for an integration gate it does not exercise.
- Golden oracle self-comparison does not prove the valuation engine.
- A fake Excel/COM test does not prove Microsoft Excel qualification.
- `NOT_QUALIFIED` is not PASS.
- Missing C1–C11 source decisions may not be fabricated to make a Golden test green.
- Human adjustment/indication authority may not be replaced by system recommendation.

Every implementation PR must preserve all accepted Epic 0 boundaries and all earlier Epic 1 accepted behavior.

## 2. Cross-cutting mandatory controls

| Control | Acceptance rule |
|---|---|
| Architecture | Domain/Application remain free of concrete UI/DB/Excel/provider infrastructure imports. |
| Decimal safety | Money, unit prices, areas and percentages use canonical Decimal/string boundaries; binary float rejected where canonical precision matters. |
| Percentage | `5% = Decimal("0.05")`; display-percent conversion is adapter/UI responsibility. |
| Appraisal date | Required deterministic `appraisal_date`; no `NOW()`/system-date calculation authority. |
| Explicit zero | Selected `0%` is valid and distinguishable from missing/unreviewed. |
| Human authority | Adjustment selection and final indicated-price decision remain human-confirmed and auditable. |
| Persistence | Canonical RE store only; legacy `cases.db` remains unchanged. |
| Archive | No operational destructive delete in the baseline workflow. |
| Excel safety | Unknown/protected cells not silently overwritten; unsupported template/dependency fails closed. |
| Regression | All prior accepted tests/guards remain green. |
| Evidence binding | Runtime-tested HEAD and exact reviewed HEAD are recorded; implementation change after test requires rerun. |

## 3. E1-PR-001 acceptance — Manual Case / TSTĐ / TSSS Data Backbone

### Required proof
- create a canonical manual case with required appraisal date and supported profile selection;
- save and resume subject property data;
- save and resume TSSS01, TSSS02 and TSSS03 independently;
- preserve exact Decimal/string scale for numeric business inputs;
- preserve explicit `0` values separately from missing values;
- encrypted persistence migration is explicit, ordered and transactional;
- repository/application round-trips do not touch legacy DB;
- local-service exercise proves the use case without direct DB access.

### Negative proof
- missing required appraisal date rejected;
- binary float rejected at canonical numeric boundary where applicable;
- unsupported profile/template selection rejected or explicitly unresolved;
- canonical DB path equal to legacy DB path rejected;
- malformed comparable identity/case lineage rejected.

### Exit
`ManualCaseDataGate = PASS`

No calculation correctness claim is permitted yet.

## 4. E1-PR-002 acceptance — Market Normalization + C1–C11 Adjustment Run

### Required proof
- exact frozen C1–C11 canonical keys and order;
- selected-rate provenance includes case/comparable/factor and human selection metadata;
- explicit zero remains a decision;
- missing decision remains missing and cannot silently calculate as zero;
- calculation graph uses the frozen exemplar base dependencies rather than generic full compounding;
- deterministic adjustment amounts/running indicated prices;
- source-data change can mark a previously selected decision stale/needs review without overwriting it.

### Golden decision fixture gate
Before N08 end-to-end assertion:

- adjustment decisions must be extracted from source workbook/reference evidence;
- each extracted rate must bind to source workbook hash/identity and source cell/range;
- fixture version and semantic digest must be recorded;
- rates may not be solved backwards from expected output prices.

If any mandatory selected rate remains unproven:

`N08AdjustmentE2E = BLOCKED_INPUT_COVERAGE`

—not PASS and not FAIL-by-invention.

### Once fixture coverage is complete
Expected indicated-price checkpoints:

- `Bangtinh!F108 = 196308350` within ±0.5 VND/m²;
- `Bangtinh!G108 = 227083250` within ±0.5 VND/m²;
- `Bangtinh!H108 = 212201640` within ±0.5 VND/m².

### Exit
`AdjustmentCalculationGate = PASS`

## 5. E1-PR-003 acceptance — Quality / 15% / Human Indication

### Required quality checkpoints

| Checkpoint | Expected |
|---|---:|
| TSSS01 adjustment count | 2 |
| TSSS02 adjustment count | 4 |
| TSSS03 adjustment count | 4 |
| TSSS01 gross adjustment | 34642650 |
| TSSS02 gross adjustment | 83662250 |
| TSSS03 gross adjustment | 35366940 |
| TSSS01 amplitude | `5–10` |
| TSSS02 amplitude | `5–15` |
| TSSS03 amplitude | `3–5` |
| TSSS01 net adjustment | -34642650 |
| TSSS02 net adjustment | -11951750 |
| TSSS03 net adjustment | 15718640 |

Numeric checkpoint policies reuse the versioned Golden manifest; no second epsilon is introduced.

### 15% readiness proof
For `deviation = (indicated - average) / average`:

- exactly ±15% is within readiness;
- value just inside is ready;
- value just outside emits review warning;
- warning does not modify selected rates or exclude a comparable.

### Human indication proof
- system may recommend candidate(s);
- final selection requires explicit human action;
- selected value, actor, timestamp and reason/snapshot are persisted;
- raw selected indication remains separate from rounded indication;
- default N08 unit-price rounding produces:
  - `Sheet1!G18 = 196308350` within ±0.5;
  - `Bangtinh!H119 = 196308000` exact integer at 1,000-VND increment.

### Exit
`HumanIndicationGate = PASS`

## 6. E1-PR-004 acceptance — Land + Final Valuation Composition

### Required N08 vectors

| Checkpoint | Expected |
|---|---:|
| `Bangtinh!G171` compliant land value | 16279822440 |
| `Bangtinh!G175` noncompliant land value | 2148620000 |
| `Bangtinh!G169` recognized land aggregate | 18428442440 |
| `Bangtinh!G178` supplied construction aggregate | 1152970000 |
| `Bangtinh!G181` total before final rounding | 19581412440 |
| `Bangtinh!G182` final rounded appraisal | 19581000000 |
| `Offical!E32` pre-million-rounding total | 19581412440 |

### Invariants
- compliant and noncompliant/planning land components remain separately traceable;
- construction aggregate source is explicitly marked as supplied/precomputed Epic-1 boundary input;
- no CTXD age/expert/replacement-cost engine is introduced;
- `total_value_before_rounding_vnd` and `final_appraised_value_vnd` are distinct canonical values;
- rounding uses existing configurable `RoundingPolicy`;
- no bank/template name is hard-coded into domain calculation.

### Negative proof
- missing required component/control fails closed;
- invalid/non-finite Decimal rejected;
- output consumer requesting pre-rounded value cannot accidentally receive final-rounded value and vice versa.

### Exit
`FinalValuationCompositionGate = PASS`

## 7. E1-PR-005 acceptance — Supported-Profile Workbook Output

### Required proof
- source workbook/template path is external input; sample XLSX remains outside Git repository;
- source artifact hash/fingerprint checked before write;
- unsupported template -> fail closed;
- reference workbook is never edited in place;
- writer creates a new artifact;
- only declared profile writable/compatibility cells are modified;
- formula-protected and unknown cells are not overwritten;
- known stale locality compatibility override is explicit and limited to declared mapping;
- no arbitrary historical external-link update;
- output consumers map `G181`/pre-rounded versus `G182`/final-rounded intentionally;
- output artifact SHA-256 and generation report recorded.

### Structural non-regression
Before/after workbook inspection must show:

- required sheet set/states preserved;
- protected formula signatures preserved except explicitly declared compatibility transformations;
- no unexpected new external links;
- no unexpected changed cells outside writer allowlist.

### Qualification state
Generation alone yields:

`WorkbookGenerated = true`

It does not yield `ExcelQualification = PASS`.

### Exit
`WorkbookGenerationGate = PASS`

## 8. E1-PR-006 acceptance — Local Service + Astryx Manual Workbench

### Browser/use-case path

`Create Case → TSTĐ → TSSS01/02/03 → Adjustment C1–C11 → Quality → Human Indication → Result → Export`

### Required proof
- all business calculations are obtained through application contracts;
- UI has no duplicated valuation formula;
- percent display/input conversion preserves canonical fraction semantics;
- explicit zero versus missing is visibly distinguishable;
- manual human decisions require explicit interaction;
- reload/resume returns the persisted case state;
- error responses are structured and do not leak secrets;
- local-service launch/session rules from E0-PR-006 remain enforced;
- `/re` CSS isolation remains green against legacy routes;
- core manual flow does not require OCR, Maps or AI network access.

### Negative proof
- unauthenticated/guest access cannot reach protected RE workbench actions;
- invalid/stale local-service credential rejected;
- UI cannot submit incomplete mandatory decision set as ready result;
- export disabled/fails closed when calculation/readiness prerequisites are incomplete.

### Exit
`ManualWorkbenchGate = PASS`

## 9. E1-PR-007 acceptance — End-to-End + Real Excel

This is the Epic 1 closure gate.

### Required environment
A controlled Windows workstation/runner with actual supported Microsoft Excel Desktop.

Hosted Windows with no Excel may only prove `NOT_QUALIFIED` fail-safe behavior and cannot close this gate.

### Required artifact chain
- exact accepted application commit;
- canonical manual-input package;
- provenance-complete adjustment-decision fixture;
- supported source template hash/fingerprint;
- generated output workbook SHA-256;
- qualification report bound to that exact generated workbook;
- Excel version and runner identity.

### Required execution
1. build canonical case through the same application contracts used by the workbench;
2. run normalization/adjustment/quality/human-selection/final composition;
3. generate workbook through supported profile;
4. open generated workbook with arbitrary link updates disabled;
5. call Microsoft Excel Desktop full recalculation;
6. read all mandatory checkpoint values;
7. evaluate with the versioned checkpoint comparator;
8. require qualification status `PASS`.

### Mandatory checkpoint rule
All Walking Skeleton-required checkpoints must be present and pass the frozen comparison policy. Missing/unexpected required checkpoint is not PASS.

### Epic 1 closure
Epic 1 is `ACCEPTED/CLOSED` only if:

- E1-PR-001 through E1-PR-006 are independently accepted;
- E1-PR-007 end-to-end application path passes;
- actual Microsoft Excel qualification returns PASS;
- no open BLOCKER/HIGH/MEDIUM acceptance finding remains;
- the reviewed/qualified workbook is bound to exact code and input provenance.

If Microsoft Excel is unavailable:

`Epic1Status = IMPLEMENTATION_COMPLETE / QUALIFICATION_PENDING`

not `CLOSED`.

## 10. Independent-review evidence rule

Each implementation PR handoff must contain:

- exact base SHA;
- runtime-tested HEAD;
- exact review HEAD;
- binding workflow/run id and runner/runtime;
- test result/count;
- changed-file scope;
- explicit superseded-run history when applicable;
- post-test-delta review;
- open finding list;
- verdict request `ACCEPTED | RETURN FINDINGS`.

The implementer must not self-declare acceptance.
