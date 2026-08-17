# E1-PR-001 — Independent Review Handoff v1

**Date:** 2026-08-17  
**Repository:** `Reguluspt/CEN-Value-RE`  
**Branch:** `agent/e1-pr-001-manual-data-backbone`  
**Implementation baseline:** `723409a3da60216e42cc9344afadc75c1f590d91`  
**Runtime-tested HEAD:** `ed929c05f8515da81c2ec23a126bf0b6c3ac1955`  
**Binding GitHub Actions run:** `31999801801`  
**Runner:** `windows-latest`  
**Result:** `150 passed in 3.09s`; focused `8 passed in 0.98s`  
**Decision requested:** `ACCEPTED` / `RETURN FINDINGS`

## Exact review-head rule

Before issuing a verdict, resolve the current PR HEAD directly from GitHub. The review request will provide the exact review HEAD after this handoff/report-only delta is complete.

If current PR HEAD differs from the supplied exact review HEAD, stop and report `HEAD MISMATCH` until the delta is reviewed.

No implementation-bearing change after runtime-tested HEAD `ed929c05f8515da81c2ec23a126bf0b6c3ac1955` may be accepted without a new full Windows run.

## Frozen authority

Review against:

- `epic-1/EPIC_1_IMPLEMENTATION_PACKET_v1.md`;
- `epic-1/EPIC_1_PR_PLAN_v1.md` — E1-PR-001 scope;
- `epic-1/EPIC_1_ACCEPTANCE_MATRIX_v1.md` — `ManualCaseDataGate`;
- `epic-1/E1_PR_001_MANUAL_DATA_CONTRACT_v1.md`;
- `Design Book/03_DOMAIN_MODEL.md`;
- accepted Epic 0 Decimal/local-service/encrypted-persistence boundaries.

Do not review E1-PR-002 calculation behavior as if it were implemented here.

## Expected implementation-bearing surface

Review the net implementation delta in:

- `epic-1/E1_PR_001_MANUAL_DATA_CONTRACT_v1.md`;
- `src/re/ports/persistence.py`;
- `src/re/adapters/persistence/migrations.py`;
- `src/re/adapters/persistence/repositories.py`;
- `src/re/adapters/persistence/store.py`;
- `src/re/application/commands/__init__.py`;
- `src/re/application/commands/manual_case.py`;
- `src/re/application/queries/__init__.py`;
- `src/re/application/queries/manual_case.py`;
- `src/re/application/services/__init__.py`;
- `src/re/application/services/manual_case.py`;
- `src/re/adapters/local_service/flask_app.py`;
- `src/re/adapters/local_service/manual_case_routes.py`;
- `tests/re/test_encrypted_persistence.py`;
- `tests/re/test_manual_case_data_backbone.py`.

The final review tree must contain no one-time E1-PR-001 verification/materialization workflows or staging payload files.

## Required review checklist

### 1. Scope / architecture

Confirm:

- E1-PR-001 is data-backbone only;
- Domain/Application do not import Flask, SQLCipher, SQLite, DPAPI, Excel/COM or concrete persistence adapters;
- Flask adapter does not execute SQL;
- no market normalization, C1–C11 calculation, quality, indicated price, land/final valuation, CTXD calculation, workbook generation, full workbench UI or OCR/provider feature appears.

### 2. Manual case contract

Confirm a case requires:

- canonical ISO appraisal date;
- explicit supported `template_profile_id` and version;
- stable case id/code/status.

Unsupported profiles must fail closed. Missing/invalid appraisal date must fail.

### 3. Subject / land data

Confirm subject persistence represents:

- legal/current addresses;
- location coordinates;
- legal review state;
- planning/environment notes;
- identified land parcels;
- land valuation components separate from legal parcel identity;
- typed property characteristics.

No land-value calculation belongs in this PR.

### 4. TSSS01–03

Confirm exactly slots 1, 2 and 3 are supported and independently addressable.

Each comparable must preserve:

- stable property identity and case lineage;
- slot/order;
- one market observation;
- asking/sale price;
- negotiated price;
- optional fractional negotiation rate;
- typed comparison characteristics;
- zero or more light evidence rows.

No adjustment percentage may be invented or stored in comparable source records.

### 5. Exact numeric / missing semantics

Confirm binary `float`, bool and non-finite numeric values fail at canonical precision boundaries.

Persistence must retain exact string scale. Explicit `0.0000` must remain distinct from missing `None`.

### 6. Persistence migration v2

Confirm migration v2 is:

- explicit;
- ordered;
- transactional;
- limited to canonical RE database;
- not a migration of legacy `cases.db`.

Review schema constraints for profile fields, comparable lineage/slots and canonical child tables.

### 7. Deterministic child ordering corrective

The earlier substantive run `31999430320` returned `149 passed / 1 failed` because land components with equal timestamps fell back to UUID order.

Review the correction carefully:

- `land_parcel.parcel_order` is persisted and positive;
- `land_valuation_component.component_order` is persisted and positive;
- `evidence.evidence_order` is persisted and positive;
- repositories read using those ordinals rather than timestamp/UUID as primary logical ordering;
- service assigns ordinals from the submitted tuple sequence;
- multiple parcel/component/evidence tests prove deterministic resume ordering.

Treat this as a correctness issue, not cosmetic ordering, because positional update matching depends on deterministic child sequence.

### 8. Atomicity / identity fail-closed

Confirm:

- outer UoW transaction controls nested bundle commit/rollback;
- partial nested writes do not survive a failing command;
- property identity cannot silently move across cases/roles/slots;
- DB trigger independently rejects comparable case-lineage mismatch and invalid slots.

### 9. Local-service path

When `ManualCaseService` is injected, confirm authenticated loopback routes exercise application services for:

- create case;
- resume case;
- save subject;
- save comparable slots 1–3.

Existing per-launch authentication must remain enforced. No direct DB access in the HTTP adapter.

### 10. Legacy safety

Confirm canonical operations do not open/migrate/reshape legacy `cases.db` and existing same-path protection remains intact.

Binding tests must prove a legacy sentinel hash remains unchanged.

## Binding runtime evidence

Only run `31999801801` is binding.

Expected tested HEAD:

`ed929c05f8515da81c2ec23a126bf0b6c3ac1955`

Expected target/runtime:

- `windows-latest` / Windows Server 2025;
- Python `3.11.9`;
- Flask `3.1.1`;
- sqlcipher3 `0.6.2`;
- pywin32 `312`.

Expected test results:

- complete `tests/re`: `150 passed in 3.09s`;
- focused `tests/re/test_manual_case_data_backbone.py`: `8 passed in 0.98s`.

Expected vector includes:

```text
manual_case_data_gate=PASS
schema_version=2
required_appraisal_date=true
supported_profile_binding=true
subject_roundtrip=true
comparable_slots=1,2,3
deterministic_parcel_order=true
deterministic_component_order=true
deterministic_evidence_order=true
exact_decimal_scale=true
explicit_zero_distinct_from_missing=true
binary_float_rejected=true
unsupported_profile_rejected=true
atomic_bundle_rollback=true
comparable_lineage_guard=true
local_service_roundtrip=true
local_service_direct_db_access=false
legacy_hash_unchanged=true
calculation_correctness_claim=false
```

## Verification history

Do not use earlier runs as acceptance evidence:

- `31999274874`: stopped before pytest on one-time workflow whitespace hygiene;
- `31999358889`: stopped before pytest because cumulative diff still included the superseded workflow;
- `31999430320`: substantive run, `149 passed / 1 failed`; exposed nondeterministic land-component ordering;
- `31999801801`: corrected implementation, `150 passed`; **FINAL / BINDING**.

## Claim boundary

An ACCEPTED verdict for this PR establishes only `ManualCaseDataGate = PASS`.

It must not be interpreted as:

- AdjustmentCalculationGate PASS;
- Golden N08 adjustment E2E PASS;
- comparable-quality/15% PASS;
- human indication PASS;
- final valuation PASS;
- workbook-generation PASS;
- Microsoft Excel qualification PASS;
- Epic 1 closure.

## Verdict rule

Return `ACCEPTED` only if all E1-PR-001 acceptance requirements are independently supported and there is no untested implementation-bearing post-test delta.

Otherwise return `RETURN FINDINGS` with actionable finding id, severity, file/path, exact issue, corrective action and closure test.
