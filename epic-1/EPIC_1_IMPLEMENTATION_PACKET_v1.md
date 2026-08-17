# Epic 1 — Manual Walking Skeleton Implementation Packet v1

**Status:** IMPLEMENTATION PACKET — DERIVED FROM FROZEN GATE B
**Repository baseline:** `df14f1c1ee845734dc58c0e63f42d12db3d54155`
**Epic:** 1 — Manual Walking Skeleton
**Scope:** `Create Case → Manual TSTĐ → Manual TSSS01/02/03 → Market Normalization → Adjustment C1–C11 → Comparable Quality → Human Indicated Price → Land/Valuation Result → Excel Output`

## 1. Purpose

Epic 1 is the first business-capable vertical slice of CenValue RE. It proves that the canonical model, deterministic calculation engine, persistence boundary, local-service/application orchestration, Astryx workbench and Excel compatibility adapter can cooperate without allowing the legacy workbook to become the canonical business model.

Epic 1 is not a rewrite of every legacy Excel cell. It implements the mandatory Walking Skeleton business chain frozen by Gate B.

## 2. Frozen authority and precedence

Implementation is governed by, in order:

1. current Project Owner decisions and `MASTER_PRODUCT_ROADMAP_v1.md`;
2. `gate-b/GATE_B_CLOSURE_REPORT_v1.md`;
3. current frozen Gate B contracts, especially:
   - `GATE_B8_ADJUSTMENT_FACTOR_REGISTRY_v1.md`;
   - `GATE_B10_OUTPUT_CONSUMER_CONTRACT_v1.md`;
   - `GATE_B13_ROUNDING_POLICY_v1.md`;
   - `GATE_B14_DEPENDENCY_CLASSIFICATION_BASELINE.md`;
   - `GOLDEN_CASE_CHECKPOINT_MANIFEST_v0.2.md` and versioned fixture manifest;
   - `EXCEL_TEMPLATE_PROFILE_v1.md` / `EXCEL_TEMPLATE_FINGERPRINT_v1.md`;
4. Design Book reviewed contracts;
5. historical v0.1 trace documents only where not superseded by later closure.

Historical sections that still say a later-closed item is “open” are provenance, not current blockers.

## 3. Architecture invariants

Existing Epic 0 boundaries remain binding:

`UI/API → Application → Domain → Ports ← Adapters`

- Domain must not import React/Tauri, Flask, SQLCipher/sqlite, Excel/COM/openpyxl, provider SDKs or concrete adapters.
- Application may depend on ports and domain, not concrete infrastructure.
- Excel remains a compatibility/output adapter, not canonical calculation truth.
- `src/re/adapters/excel/` remains template profile/fingerprint infrastructure; workbook runtime belongs in dedicated workbook/output/qualification adapter packages.
- Binary float is not allowed at canonical numeric boundaries.
- Human authority is mandatory for adjustment selection and final indicated-price decision.

Every Epic 1 PR reruns the accepted Epic 0 regressions.

## 4. Dependency classification rule

Do not convert the legacy workbook dependency graph one-for-one into domain fields.

Every needed datum is classified as:

- `CANONICAL_INPUT` — durable business/user data;
- `DERIVED` — deterministic CenValue calculation;
- `CONTROL` — template/profile/output policy;
- `LEGACY_ONLY` — workbook plumbing/layout not persisted as business meaning;
- `OUT_OF_SCOPE` — not required for the Walking Skeleton.

A newly discovered dependency blocks Epic 1 only if it affects a mandatory Walking Skeleton checkpoint/output and cannot be reproduced from classified canonical input + derived values + controls.

Unknown dependencies that can change a mandatory checkpoint must fail safe and become a design finding; they may not be silently ignored.

## 5. Canonical manual-input boundary

Epic 1 manual case data must support at least:

### Case
- case id/code;
- appraisal date — required and authoritative;
- supported template/profile selection;
- lifecycle state needed to create/resume the manual appraisal work.

### TSTĐ / subject property
- legal/location/address/parcel identity needed by the Walking Skeleton;
- land areas needed by final land valuation, including compliant and separately treated noncompliant/planning component;
- comparison characteristics used by active C1–C11 factors;
- optional canonical location values already frozen by the domain.

### TSSS01/02/03
- three comparable identities;
- evidence/provenance metadata required by the manual workflow;
- asking price;
- negotiated/market-normalized price inputs;
- land/comparison characteristics needed by active factors;
- explicit distinction between missing and entered zero-valued data.

Epic 1 does not require OCR, GCN parsing, Maps resolution or Historical Learning suggestions. Those are later epics.

## 6. Adjustment engine contract

The exemplar factor registry is frozen as:

1. C1 `legal_status`
2. C2 `location`
3. C3 `relative_distance_to_local_points`
4. C4 `scale_area`
5. C5 `frontage`
6. C6 `depth`
7. C7 `shape`
8. C8 `traffic_access`
9. C9 `business_environment`
10. C10 `infrastructure`
11. C11 `other_disadvantage`

Selected adjustment rate is a human decision. A rate of `0%` is an explicit valid decision and must not be converted to missing/null.

For the N08 exemplar, calculation stages must preserve the frozen workbook-derived base dependency. The engine must not replace the sample graph with a generic fully compounded chain.

Each adjustment run produces an immutable/reproducible calculation snapshot containing the selected rates, base values, adjustment amounts, running indicated values and provenance required to audit the human decisions.

## 7. Golden decision-fixture rule

`fixtures/GOLDEN_CASE_CANONICAL_FIXTURE_v1.json` is intentionally `PARTIAL INPUT COVERAGE` and does not contain explicit C1–C11 decisions per comparable.

Therefore:

- Epic 1 must not invent adjustment decisions;
- Epic 1 must not solve rates backwards from F108/H119 or other expected outputs;
- before N08 is used as a calculation-engine end-to-end oracle, a versioned adjustment-decision fixture must be extracted from the source workbook/reference corpus;
- every extracted selected rate must retain comparable id, factor key, source workbook identity, source cell/range evidence and extraction provenance;
- if source evidence is ambiguous, the datum remains open and the affected end-to-end assertion stays blocked.

The existing Golden Fixture expected outputs remain comparator/checkpoint oracle values, not proof of the missing decisions.

## 8. Comparable quality and human indication

For each comparable the canonical calculation exposes:

- final indicated unit price;
- gross adjustment value;
- net adjustment value;
- adjustment count using non-zero selected rates;
- minimum/maximum absolute non-zero adjustment amplitude;
- 15% deviation readiness result;
- information-quality input/status when available;
- guidance/recommendation reason.

15% readiness is advisory validation. It never silently changes a rate or removes a comparable.

System selection is guidance only. The human appraiser confirms the final indicated-price decision and an auditable decision snapshot is persisted.

Explicit tie/equality behavior is allowed only where a frozen rule supports it; no arbitrary averaging rule may be introduced.

## 9. Land and final valuation boundary

Epic 1 implements the frozen final-composition chain without pulling the full Construction Engine forward from Epic 2.

Required canonical states include:

- rounded selected indicated unit price;
- compliant residential land value;
- separately treated noncompliant/planning land component under profile/output policy;
- recognized land aggregate;
- construction/on-land aggregate supplied through an explicit derived-value boundary;
- `total_value_before_rounding_vnd`;
- `final_appraised_value_vnd`.

For N08:

- unit-price rounding default: nearest 1,000 VND/m²;
- final total rounding default: nearest 1,000,000 VND.

Both total states remain canonical because downstream consumers intentionally use different values:

- `Bangtinh!G181` / `Offical!E32` use pre-million-rounding total;
- `Bangtinh!G182` is the final million-rounded appraisal value.

Epic 1 may compose a supplied construction aggregate for the exemplar, but it must not implement CTXD age/expert/replacement-cost calculation logic. That belongs to Epic 2.

## 10. Excel output boundary

Epic 1 must generate an output workbook through a supported `ExcelTemplateProfile`.

Rules:

- input/output writes are profile-controlled;
- unknown cells are read-only by default;
- formula-protected cells are not overwritten by application values;
- known compatibility overrides are explicit and versioned;
- stale external-link localization uses the frozen profile rule and may not silently update arbitrary links;
- output is generated as a new artifact/copy; the reference workbook is not edited in place;
- generated workbook hash is recorded;
- workbook generation itself does not claim Excel qualification PASS.

The sample/reference XLSX remains Library-only under repository policy.

## 11. Epic 1 checkpoint boundary

Mandatory exemplar checkpoints include at least:

- `Bangtinh!F108:H108` comparable indicated prices;
- `Sheet1!G18` selected/recommended indication;
- `Bangtinh!H119` rounded final indicated unit price;
- comparable quality count/gross/amplitude/net checkpoints;
- `Bangtinh!G171` compliant land value;
- `Bangtinh!G169` recognized land aggregate;
- `Bangtinh!G178` construction/on-land aggregate;
- `Bangtinh!G181` total before final million-rounding;
- `Bangtinh!G182` final rounded appraisal value;
- `Offical!E32` pre-million-rounding output mapping.

CTXD internal quality/replacement-cost checkpoints remain Epic 2 calculation responsibility even though the versioned Golden manifest already preserves them as workbook oracle data.

## 12. Real Excel exit gate

Epic 0 proved that missing Microsoft Excel cannot falsely report PASS.

Epic 1 is stricter: it does not close until a workbook generated by the Epic 1 vertical slice is qualified with actual Microsoft Excel Desktop evidence under the frozen qualification protocol.

Required final gate:

`Canonical manual case → CenValue calculation → generated supported-profile workbook → Microsoft Excel Desktop full recalculation → checkpoint readback → tolerance comparison → PASS`

If the available runner has no Excel Desktop, the result remains `NOT_QUALIFIED`; Epic 1 may be implementation-complete but is not accepted/closed.

## 13. Deferred from Epic 1

Not part of this epic:

- CTXD age/expert/component/replacement-cost calculation engine;
- OCR/GCN/QR/VBDLIS;
- Maps resolution;
- Historical Learning/statistical suggestions;
- approval-return import/revision lifecycle;
- advanced productivity features;
- installer/update hardening.

## 14. Definition of done

Epic 1 is complete only when:

1. a manual case can be created/resumed;
2. TSTĐ and exactly three exemplar TSSS can be entered and persisted;
3. market normalization and C1–C11 human adjustment decisions calculate deterministically;
4. explicit 0% remains distinct from missing;
5. comparable quality and 15% readiness are calculated;
6. a human indicated-price decision is recorded;
7. land/final result calculation produces separate raw/pre-final and final-rounded values;
8. a supported-profile workbook is generated without unsafe writes;
9. mandatory checkpoints agree with frozen oracle/tolerance rules;
10. actual Microsoft Excel Desktop qualification returns PASS for the generated artifact;
11. all prior foundation regressions remain green;
12. no hidden workbook behavior becomes canonical by accident.
