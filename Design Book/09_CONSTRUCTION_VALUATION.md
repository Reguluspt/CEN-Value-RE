# 09 — Construction Valuation
**Status: REVIEWED — SAMPLE WORKBOOK CONTRACT DERIVED; PROFILE TABLES STILL OPEN**

## Core domain
A Property may have zero or many `ConstructionAsset`.

Separate:
- legal registration of attached assets;
- physical existence of CTXD.

`legal_registration_status` is independent of:
`valuation_treatment = VALUE | DESCRIBE_ONLY | EXCLUDE`.

Only `VALUE` contributes to `TotalConstructionValue`.

## Deterministic reference date
Effective age uses `AppraisalCase.appraisal_date`, not current workstation date.

```text
effective_age_years
= YEAR(appraisal_date) - construction_year
```

## Remaining quality — age method
For the sample workbook profile:

```text
remaining_quality_age
= ROUND(
    (economic_life_years - effective_age_years)
    / economic_life_years
    + maintenance_condition_pct,
    2
  )
```

`maintenance_condition_pct` is appraiser-entered from actual observation.

## Remaining quality — expert/component method

For each component:

```text
weighted_deterioration_i
= observed_deterioration_i × fixed_component_weight_i
```

```text
overall_deterioration
= SUM(weighted_deterioration_i) / SUM(fixed_component_weight_i)
```

```text
remaining_quality_expert = 1 - overall_deterioration
```

Structural weights are fixed reference data for a construction profile; observation percentage is user input.

## Average remaining quality

Sample workbook:

```text
remaining_quality_average
= ROUND((age_method + expert_method) / 2, 2)
```

## Replacement/remaining value

```text
replacement_cost
= gross_floor_area
  × new_build_unit_cost
  × price_escalation_factor
```

```text
remaining_value
= replacement_cost
  × remaining_quality_average
  × applicable_factor
```

```text
TotalConstructionValue
= Σ remaining_value
  WHERE valuation_treatment = VALUE
```

## Sample compatibility checkpoints
- `Bangtinh!H127`
- expert/component result blocks around `Bangtinh!F140`
- `Bangtinh!H153`
- `Bangtinh!G156:G157`
- `Bangtinh!H161:H163`

## OPEN
- construction profiles and economic-life tables;
- full fixed-weight tables;
- semantics/source of additional applicable factor;
- exact intermediate rounding scales across template families;
- mapping of compliant/non-compliant planning classes to canonical CTXD attributes.
