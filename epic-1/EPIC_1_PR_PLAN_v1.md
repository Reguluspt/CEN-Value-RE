# Epic 1 — Manual Walking Skeleton PR Plan v1

**Status:** PROPOSED IMPLEMENTATION SEQUENCE — DERIVED FROM FROZEN GATE B
**Baseline:** `df14f1c1ee845734dc58c0e63f42d12db3d54155`
**Epic:** 1 — Manual Walking Skeleton

## Sequencing principles

- Deliver vertical business capabilities, not one technical layer at a time.
- Every PR is independently reviewable and must preserve all accepted Epic 0 regressions.
- Each implementation PR gets runtime evidence and independent acceptance before the next dependent PR starts.
- Unknown Excel dependencies that can alter a mandatory checkpoint fail safe and become findings.
- No PR may fabricate missing Golden Fixture inputs.
- Human-selected adjustment and final indication remain authoritative human decisions.
- Real Microsoft Excel Desktop qualification is the final Epic 1 exit gate.

---

## E1-PR-001 — Manual Case / TSTĐ / TSSS Data Backbone

### User-visible capability
A user/application client can create and resume a manual RE appraisal case containing a TSTĐ and three comparable properties without relying on the legacy flat `cases` model.

### Scope
- expand canonical `AppraisalCase`, subject-property and comparable contracts only as needed for the Walking Skeleton;
- required `appraisal_date` and supported profile selection;
- manual subject legal/location/parcel/land/comparison characteristics;
- TSSS01/02/03 identities, evidence metadata, asking/negotiated values and comparison characteristics;
- application commands/queries for create, update and resume;
- persistence migration/repository expansion using the accepted encrypted RE store;
- local-service/application integration needed to exercise the capability programmatically;
- deterministic serialization/round-trip tests.

### Explicit non-scope
- adjustment calculations;
- comparable quality;
- final valuation;
- workbook writing;
- full UI workbench;
- CTXD calculation engine;
- OCR/providers.

### Acceptance
- create/resume round-trip preserves Decimal strings and appraisal date exactly;
- three comparable slots/records are independently addressable;
- missing and explicit zero are distinguishable where business meaning requires it;
- legacy `cases.db` remains untouched;
- archive behavior remains non-destructive;
- architecture guards and all Epic 0 regressions remain green.

---

## E1-PR-002 — Market Normalization + C1–C11 Adjustment Run

### User-visible capability
A manual comparable can receive a complete human-selected C1–C11 adjustment run and produce a deterministic indicated unit price.

### Scope
- exemplar factor registry C1–C11 using stable canonical keys;
- explicit selected-rate decision model and provenance;
- explicit `0%` valid decision versus missing/unreviewed decision;
- source-data-change / needs-review staleness behavior where applicable;
- market/transaction normalized base required by the frozen exemplar calculation graph;
- adjustment amount and running indicated price calculation;
- immutable calculation snapshot per comparable;
- application/persistence integration for adjustment decisions and results;
- Golden decision-fixture extraction contract.

### Golden-fixture precondition
Before claiming N08 end-to-end calculation agreement, create a versioned adjustment-decision fixture by extracting selected rates from the source workbook/reference corpus. Every rate must retain source-cell/workbook provenance.

Forbidden:
- inferring rates backwards from F108/H119;
- inventing missing C1–C11 decisions;
- replacing the frozen exemplar dependency graph with a generic fully compounded formula.

### Acceptance
- all 11 factor keys present in frozen order;
- explicit zero contributes zero amount but remains an entered decision;
- missing decision is not silently treated as zero;
- Decimal-only calculations;
- snapshot determinism under changed ambient Decimal context;
- extracted Golden decision fixture is provenance-complete or the affected N08 assertions remain blocked;
- when the source decisions are complete, F108/G108/H108 agree with frozen checkpoint tolerance.

---

## E1-PR-003 — Comparable Quality + 15% Readiness + Human Indication

### User-visible capability
The appraiser can see comparable quality metrics/readiness guidance and explicitly confirm the indicated unit price used for valuation.

### Scope
- gross adjustment value;
- net adjustment value;
- adjustment count from non-zero selected rates;
- min/max absolute non-zero rate amplitude;
- arithmetic average of comparable indicated prices;
- 15% deviation readiness validation;
- guidance candidates / minimum-gross recommendation semantics;
- frozen supported tie behavior only;
- human final indicated-price decision, actor/time/reason and persisted snapshot;
- unit-price `RoundingPolicy` application after human selection.

### Rules
- readiness warning never changes rates automatically;
- recommendation is advisory;
- final decision requires human confirmation;
- no arbitrary averaging outside frozen tie behavior.

### Acceptance
- quality checkpoints reproduce the manifest values when driven by the Golden decision fixture;
- 15% boundary tests include exactly-at, inside and outside threshold;
- zero-rate decisions are excluded from adjustment count/amplitude as frozen, while remaining valid decisions;
- `Sheet1!G18` selected indication and `Bangtinh!H119` rounded indication match checkpoint policy;
- raw selected indication and rounded indication remain separate.

---

## E1-PR-004 — Land + Final Valuation Composition

### User-visible capability
A confirmed indicated unit price can produce the Walking Skeleton land value and final appraisal result with explicit rounding states.

### Scope
- compliant residential land value;
- separately treated noncompliant/planning land component using an explicit profile/control input;
- recognized land aggregate;
- construction/on-land aggregate input boundary;
- total before final rounding;
- final appraisal rounding using existing `RoundingPolicy`;
- immutable valuation result snapshot and persistence/application integration.

### Epic boundary
Epic 1 does **not** calculate CTXD age/expert/component/replacement-cost chains. For the N08 exemplar, the construction aggregate may be supplied through a clearly typed precomputed/derived boundary solely to prove final composition. Epic 2 replaces/feeds this boundary with the canonical Construction Engine.

### Acceptance vectors
At minimum N08 must reproduce:

- `Bangtinh!G171 = 16279822440`;
- `Bangtinh!G169 = 18428442440`;
- `Bangtinh!G178 = 1152970000` as supplied construction aggregate;
- `Bangtinh!G181 = 19581412440`;
- `Bangtinh!G182 = 19581000000`;
- `Offical!E32 = 19581412440`.

`G181` and `G182` must never collapse into one field.

---

## E1-PR-005 — Supported-Profile Workbook Output Generation

### User-visible capability
CenValue can create a new approval/output workbook from a canonical Walking Skeleton case using a supported `ExcelTemplateProfile` without editing the reference workbook in place.

### Scope
- workbook-output port/application orchestration;
- profile-driven writer adapter separate from profile/fingerprint package;
- copy/open supported exemplar template from an explicit input path;
- write only declared writable/input/compatibility cells;
- preserve formula-protected cells and unknown cells;
- apply frozen known compatibility localization such as stale locality reference only through declared profile transformation;
- save to a new output path;
- bind artifact SHA-256 and generation report;
- synthetic workbook tests plus reference-workbook integration where the Library sample is available.

### Non-scope
- approval return import;
- arbitrary external-link repair;
- Excel Desktop recalculation inside the writer;
- final qualification PASS declaration.

### Acceptance
- reference workbook bytes are unchanged;
- unsupported/fingerprint-mismatched template fails closed;
- formula-protected and unknown cells are not overwritten;
- output artifact has deterministic generation metadata and hash;
- output mappings explicitly choose pre-rounded versus final-rounded total according to Gate B.10;
- generated artifact is eligible for the existing qualification harness.

---

## E1-PR-006 — Local Service + Astryx Manual Workbench Integration

### User-visible capability
A user can execute the complete manual Walking Skeleton in the CenValue RE workbench without direct database or workbook editing.

### Scope
- local-service application endpoints/commands for the accepted Epic 1 use cases;
- Astryx `/re` workbench flow for:
  - create/resume case;
  - manual TSTĐ;
  - manual TSSS01/02/03;
  - selected C1–C11 rates;
  - comparable quality/readiness;
  - human indicated-price confirmation;
  - valuation result;
  - workbook export;
- validation/error presentation from canonical application errors;
- persistence/resume behavior;
- UI must consume application contracts, not duplicate formulas.

### Rules
- UI never owns business formulas;
- browser inputs convert display percentages to canonical fractional Decimal representation at the boundary;
- explicit zero versus missing remains visible;
- human decisions cannot be auto-submitted by guidance;
- offline/manual core flow remains functional without OCR/Maps/AI providers.

### Acceptance
- browser-level vertical smoke from create case through generated workbook request;
- reload/resume preserves entered and selected values;
- no Astryx CSS regression to legacy routes;
- no direct frontend imports of persistence or Excel adapter internals;
- all domain results shown by UI are obtained from application responses.

---

## E1-PR-007 — Walking Skeleton End-to-End Acceptance + Real Excel Qualification

### Purpose
Close Epic 1 against a fully bound manual-input package, generated workbook and actual Microsoft Excel Desktop.

### Required input package
- canonical N08 fixture v1;
- provenance-complete C1–C11 decision fixture extracted from source evidence;
- explicit control/profile values required by mandatory checkpoints;
- construction aggregate clearly marked as supplied Epic-1 boundary input, not CTXD-engine output;
- supported source workbook/template provided from approved external/Library corpus, not committed if repository policy forbids it.

### End-to-end path

`Create/restore manual case → TSTĐ/TSSS → normalization → C1–C11 → quality/readiness → human indication → final composition → workbook generation → Microsoft Excel Desktop full recalculation → checkpoint readback`

### Binding acceptance
- application-calculated required checkpoints match the versioned Golden manifest under declared policies;
- generated workbook is fingerprint-supported;
- real Excel Desktop opens without arbitrary link updates;
- `CalculateFullRebuild` completes;
- qualification report is bound to generated workbook SHA-256;
- every mandatory checkpoint passes;
- qualification status is `PASS`, not `NOT_QUALIFIED`;
- no hidden workbook behavior changes a canonical result silently.

If no Excel-capable runner/workstation is available, E1-PR-007 remains blocked and Epic 1 is not closed.

---

## Cross-PR regression rule

Every E1 implementation PR must run:

- architecture/import guards;
- Decimal/RoundingPolicy tests;
- ExcelTemplateProfile/fingerprint tests;
- Golden Fixture harness tests;
- local-service tests;
- encrypted persistence tests appropriate to the runner;
- Excel qualification harness fail-closed tests;
- all earlier accepted E1 tests.

A later PR may not weaken an earlier guard to make new code pass. Architecture findings must be corrected by moving behavior to the proper boundary, as established during Epic 0.

## Review / merge rule

For every E1 implementation PR:

1. exact base and runtime-tested HEAD are recorded;
2. binding CI evidence is produced;
3. post-test delta is limited to evidence/report/handoff unless rerun;
4. independent reviewer returns `ACCEPTED` or `RETURN FINDINGS` against exact review HEAD;
5. merge uses expected-head protection;
6. next dependent PR starts from the accepted merge commit.
