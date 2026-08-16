# Gate B.7 — Final Valuation Contract v0.1
**Status:** WORKBOOK-DERIVED / CORE FORMULA FROZEN FOR EXEMPLAR


> **SUPERSEDED STATUS NOTE — 2026-08-16**  
> This v0.1 file is retained for provenance. The `G181`/`G182` output-consumer question was resolved by `GATE_B10_OUTPUT_CONSUMER_CONTRACT_v1.md` and Gate B closure. Keep both canonical values (`total_value_before_rounding_vnd` and `final_appraised_value_vnd`); do not treat section 8 below as an open blocker.

## 1. Land value
For the compliant residential land component:
`land_value_compliant = indicated_unit_price_rounded × compliant_residential_area`

Workbook exemplar:
- `Bangtinh!E171 = Nhập liệu!F38`
- `Bangtinh!F171 = Bangtinh!H119`
- `Bangtinh!G171 = F171 × E171`

Non-compliant/planning-violation land is valued separately using the applicable published/reference land price in this exemplar:
- `Bangtinh!E175 = Nhập liệu!F42`
- `Bangtinh!F175 = Nhập liệu!I31`
- `Bangtinh!G175 = F175 × E175`

The exact inclusion/exclusion treatment can vary by bank/template condition; therefore canonical components remain separate and the template/output policy decides presentation/inclusion.

## 2. Construction value in final result
`Bangtinh!G178` aggregates the remaining values of CTXD rows represented by `Bangtinh!H161:H162`.

CenValue canonical rule remains:
`construction_value_total = Σ remaining_value WHERE valuation_treatment = VALUE`

A `DESCRIBE_ONLY` CTXD is not included.

## 3. Total value before final rounding
`Bangtinh!G181 = ROUND(G169 + G178, 0)`

Canonical:
`total_value_before_rounding_vnd = round(land_value_total + construction_value_total, 0 VND)`

## 4. Final rounded appraisal value
`Bangtinh!G182 = ROUND(G181, -6)`

Canonical exemplar rule:
`final_appraised_value_vnd = round(total_value_before_rounding_vnd, nearest 1,000,000 VND)`

This is an explicit calculation checkpoint, not UI-only formatting.

## 5. Official output
The hidden `Offical` sheet exposes a structured interface-like mapping:
- appraisal date/address/GPS/planning;
- land result row area/unit price/amount;
- CTXD row area/unit price/amount;
- total.

This sheet is valuable as an existing export contract and should be treated as a secondary output mapping source, not the canonical domain.

## 6. Bank/template branches
Rows 169–182 contain bank-specific branches (e.g. Shinhan). CenValue RE should model these as `ExcelTemplateProfile`/output policy conditions, not embed bank names inside the core valuation engine.

## 7. Final-value checkpoints
Mandatory:
- Bangtinh!G171 — compliant land value.
- Bangtinh!G169 — total recognized land value.
- Bangtinh!G178 — construction/on-land value aggregate.
- Bangtinh!G181 — total before final million-rounding.
- Bangtinh!G182 — final rounded appraisal value.
- Offical!E32 — official exported total mapping.

## 8. Open issue
Determine whether `Offical!E32` intentionally represents G181 (pre-million-rounding) while other approval/report outputs use G182. This must be classified per output consumer before profile freeze; do not silently force all outputs to one value.
