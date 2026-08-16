# CenValue RE — Gate B.1 CTXD Calculation Contract v0.1

**Evidence:** workbook `N08-0038_Huedtl_MTN_TranNguyenVanDau_UNLOCKED.xlsx`, sheet `Bangtinh`, rows 123–163.
**Status:** WORKBOOK-DERIVED / REVIEW REQUIRED BEFORE FROZEN


> **CURRENT AUTHORITY NOTE — 2026-08-16**  
> This is a historical workbook-derived v0.1 contract. Its observation that the legacy workbook uses `YEAR(NOW())` remains evidence only. CenValue RE's effective-age rule is superseded by `DECISION_REVISION_APPRAISAL_DATE_EFFECTIVE_AGE.md`: `effective_age_years = YEAR(appraisal_date) - construction_year`. Do not treat unresolved item 6 below as open.

## A. Remaining quality — age method
Workbook row 127:

- construction year ← `Nhập liệu!F74`
- economic life = 50 years in this sample
- effective age = `YEAR(NOW()) - construction_year`
- maintenance/condition adjustment = user-entered percentage
- remaining quality:
  `ROUND((economic_life - effective_age) / economic_life + maintenance_adjustment, 2)`

CenValue design revision already requires the maintenance/condition percentage to be entered by the appraiser from actual observation; it must not be converted into an automatic friendly-mode selector.

### Required domain inputs
- construction_year
- economic_life_years
- maintenance_condition_pct

### Derived
- effective_age_years
- remaining_quality_age_method_pct

## B. Remaining quality — expert/component method
Workbook rows 131–150 use fixed structural weights and observed deterioration by component.

For each component:
`contribution = deterioration_rate × fixed_weight`

Then:
`overall_deterioration = SUM(contribution) / SUM(fixed_weight)`

`remaining_quality_expert = 1 - overall_deterioration`

Sample fixed weights for the selected 3–5-storey house profile:
- foundation 8%
- frame/columns 10%
- walls 12%
- floor/slab 16%
- roof support 12%
- roof 5%

These weights total 63% in the workbook sample; therefore the formula normalizes deterioration by the sum of included weights rather than assuming weights sum to 100%.

### Required domain inputs
- construction_type/profile
- fixed component weight table
- appraiser-observed deterioration percentage per component

### Derived
- weighted deterioration contribution per component
- overall deterioration
- remaining_quality_expert_pct

## C. Average remaining quality
Workbook row 153:

`remaining_quality_average = ROUND((age_method + expert_method) / 2, 2)`

This is the workbook compatibility formula for the sample.

## D. Replacement cost
Workbook rows 154–157:

`replacement_cost = gross_floor_area × new_build_unit_cost × price_escalation_factor`

Sample:
`253.4 × 6,500,000 × 1 = 1,647,100,000 VND`

The workbook separates at least:
- CTXD compliant with planning
- CTXD violating planning

CenValue canonical model should not hard-code only two construction assets. Planning/compliance classification should be an attribute used by the workbook adapter to reproduce the legacy rows.

## E. Remaining construction value
Workbook rows 159–163:

`remaining_value = replacement_cost × remaining_quality_average × applicable_factor`

Sample:
`1,647,100,000 × 70% × 1 = 1,152,970,000 VND`

Total construction value is the sum of included CTXD values.

CenValue domain rule remains:
`TotalConstructionValue = Σ remaining_value WHERE valuation_treatment = VALUE`

`DESCRIBE_ONLY` does not run this calculation and contributes no value.

## F. Compatibility checkpoints for this region
Minimum Gate B checkpoint set:
- Bangtinh!H127 — age-method remaining quality.
- Bangtinh!F140 (and additional CTXD expert result blocks) — expert remaining quality.
- Bangtinh!H153 — average remaining quality.
- Bangtinh!G156/G157 — replacement cost by legacy planning class.
- Bangtinh!H161/H162 — remaining value by class.
- Bangtinh!H163 — total CTXD value.

## G. Important unresolved items
Before this contract is FROZEN across all workbook templates:
1. confirm whether economic life=50 is selected from a reference table or hard-coded for this construction type;
2. enumerate all construction profiles and fixed component-weight tables;
3. identify how multiple CTXD blocks are represented in other workbook variants;
4. identify the business meaning and source of the row-160/161 additional factor;
5. freeze rounding scale for every intermediate step;
6. confirm whether `YEAR(NOW())` must be replaced by appraisal date for deterministic/reproducible CenValue calculations;
7. map planning-compliance classification into canonical schema and output adapter.
