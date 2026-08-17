# E1-PR-001 — Manual Case / TSTĐ / TSSS Data Backbone — Implementation Report v1

**Date:** 2026-08-17  
**Status:** IMPLEMENTED; WINDOWS RUNTIME EVIDENCE GREEN; INDEPENDENT ACCEPTANCE PENDING  
**Repository:** `Reguluspt/CEN-Value-RE`  
**Implementation baseline:** `723409a3da60216e42cc9344afadc75c1f590d91`  
**Runtime-tested HEAD:** `ed929c05f8515da81c2ec23a126bf0b6c3ac1955`  
**Binding GitHub Actions run:** `31999801801`  
**Runner:** `windows-latest` (`windows-2025-vs2026`)  
**Python:** `3.11.9`  
**Result:** `150 passed in 3.09s`; focused `8 passed in 0.98s`  
**Publish status:** FEATURE BRANCH ONLY; NOT MERGED / NOT DEPLOYED

## 1. Scope delivered

E1-PR-001 implements only the first Epic 1 business-data vertical slice:

- create a canonical manual appraisal case;
- require deterministic `appraisal_date`;
- bind each case to an explicit supported Excel template profile id/version;
- save/resume one subject property (TSTĐ);
- persist subject addresses, coordinates, legal-review status, planning/environment notes and optional source-certificate id;
- persist identified/ordered land parcels;
- persist ordered land-valuation components as input data only;
- persist typed property characteristics;
- save/resume TSSS01, TSSS02 and TSSS03 independently;
- persist one market observation per comparable plus ordered light evidence metadata;
- expose create/save/resume through application services and an authenticated local-service adapter;
- extend the encrypted SQLCipher store through explicit migration v2.

This PR does **not** calculate market normalization, C1–C11 adjustments, comparable quality, indicated price, land value, CTXD, final valuation, workbook output, or Excel qualification.

## 2. Canonical numeric / missing-value behavior

Numeric request values use the existing canonical Decimal boundary. Binary `float`, `bool`, and non-finite numeric values fail closed where canonical precision applies.

Persistence keeps exact decimal strings rather than converting through binary float. Examples covered by tests include:

- `6500000.00`;
- `82.9300`;
- `20.2700`;
- `0.0000`.

An explicit string zero such as `0.0000` remains present and distinguishable from `None` / missing.

## 3. Persistence schema v2

Migration `2 — epic1_manual_case_data_backbone` is explicit, ordered and transactional. It extends only the canonical encrypted RE database.

Added/extended persistence includes:

- case template-profile id/version;
- subject/comparable common location and note fields;
- comparable case lineage + slot uniqueness;
- `land_parcel`;
- `land_valuation_component`;
- `property_characteristic`;
- `market_observation`;
- `evidence`.

### Deterministic child ordering

The first substantive Windows regression run exposed that rows sharing the same timestamp could be returned in UUID order. This was not accepted as a presentation-only issue because positional child matching during later saves could update the wrong logical child.

The correction persists explicit 1-based ordinals:

- `land_parcel.parcel_order`;
- `land_valuation_component.component_order`;
- `evidence.evidence_order`.

Repository reads now order by those canonical ordinals. Tests cover multiple parcels, multiple land components and multiple evidence records across persistence/resume.

## 4. Atomic application writes

`SQLCipherUnitOfWork.atomic()` owns bundle transaction boundaries. Repository methods remain independently usable but do not commit intermediate records while an outer application transaction is active.

A failing nested subject write rolls back the entire command. The test suite deliberately exercises this behavior.

## 5. Case / property lineage

The application service preserves stable identities and rejects reuse across another case/role/slot.

Migration v2 also adds database triggers that fail closed when a comparable row has:

- no case lineage;
- a slot outside `1..3`;
- a case id different from the canonical `property.case_id`.

This prevents direct persistence writes from bypassing the application lineage rule.

## 6. Application and local-service boundary

`ManualCaseService` owns business validation/orchestration for:

- `create_case`;
- `save_subject`;
- `save_comparable`;
- `resume_case`.

The Flask adapter exposes, when the service is explicitly injected:

- `POST /api/re/manual-cases`;
- `GET /api/re/manual-cases/<case_id>`;
- `PUT /api/re/manual-cases/<case_id>/subject`;
- `PUT /api/re/manual-cases/<case_id>/comparables/<1|2|3>`.

Existing loopback/per-launch authentication remains mandatory. The route adapter does not execute SQL or own canonical validation.

## 7. Legacy safety

The canonical database remains separate from legacy `cases.db`. Existing Epic 0 same-path protection remains green. E1 tests also keep a legacy sentinel file and verify its SHA-256 is unchanged across canonical case creation, migration and resume.

## 8. Binding runtime evidence

Binding run: `31999801801`.

The run directly established:

- Windows target dependencies install successfully;
- compile: PASS;
- bounded-scope guard: PASS;
- full accepted `tests/re` regression suite: `150 passed in 3.09s`;
- focused E1-PR-001 suite: `8 passed in 0.98s`;
- schema v2: PASS;
- subject + TSSS01/02/03 persistence/resume: PASS;
- deterministic parcel/component/evidence ordering: PASS;
- exact decimal-string scale: PASS;
- explicit zero vs missing: PASS;
- atomic rollback: PASS;
- comparable lineage guard: PASS;
- authenticated local-service round-trip: PASS;
- legacy database unchanged: PASS.

Primary runtime evidence: `evidence/E1_PR_001_RUNTIME_EVIDENCE_v1.md`.

## 9. Verification history

The following earlier runs are **non-binding**:

- `31999274874`: stopped before pytest because `git diff --check` caught trailing whitespace in the one-time workflow evidence heredoc;
- `31999358889`: stopped before pytest because the cumulative branch diff still contained that superseded workflow;
- `31999430320`: reached the full product suite and returned `149 passed / 1 failed`; this correctly exposed nondeterministic land-component ordering.

The ordering defect was corrected in product persistence/service/tests before final binding run `31999801801`.

## 10. Claim boundary

`ManualCaseDataGate = PASS` means only that the manual case/TSTĐ/TSSS data backbone is implementation-ready according to E1-PR-001 acceptance.

It does **not** mean:

- adjustment-calculation correctness;
- Golden N08 C1–C11 end-to-end correctness;
- comparable-quality correctness;
- final valuation correctness;
- workbook generation correctness;
- Microsoft Excel qualification PASS;
- Epic 1 closure.

## 11. Acceptance status

**NOT SELF-ACCEPTED.**

An independent reviewer must inspect source, migration, tests, runtime evidence and post-test delta before E1-PR-001 may merge. E1-PR-002 must not begin from this branch; it begins only from the independently accepted merge commit.
