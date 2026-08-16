# ExcelTemplateProfile v1 — N08-0038 Family
**Status:** DRAFT PROFILE / Walking Skeleton baseline

## Identity
- `profile_id`: `cenvalue-re-n08-0038-v1`
- Source exemplar: `N08-0038_Huedtl_MTN_TranNguyenVanDau_UNLOCKED.xlsx`
- Required sheets: Hồ sơ, Nhập liệu, Phieu TTTT, Bangtinh, Sheet1, Data, Offical, QH, PX
- Workbook contains protected/hidden helper sheets; unknown structure changes fail closed.

## Cell classes
- INPUT: approved mapped user/canonical inputs.
- FORMULA_PROTECTED: workbook formulas not overwritten.
- OUTPUT_CHECKPOINT: formulas/results verified.
- CONTROL: lookup/config/defined-name inputs.
- APPROVAL_RETURN: cells allowed in returned-workbook diff.
- VOLATILE_COMPAT_OVERRIDE: narrowly approved transformation.
- UNKNOWN: read-only/fail-safe.

## Approved compatibility transformations
1. Construction effective age uses `AppraisalCase.appraisal_date`, not `YEAR(NOW())`.
2. Stale external self-reference at `Phieu TTTT!E5` is localized to the canonical/template locality field and external dependency removed.

## Required checkpoint groups
### Adjustment/Comparables
- Bangtinh!F108:H108 indicated prices.
- Bangtinh!F112:H115 quality metrics region.
- Sheet1!A18:C24 helper metrics.
- Sheet1!G18 selected/recommended indication.
- Bangtinh!H119 rounded indication.

### Construction
- Bangtinh!H127 age-method remaining quality.
- Bangtinh!F140 expert remaining quality sample checkpoint.
- Bangtinh!H153 average remaining quality.
- Bangtinh!G156:G157 replacement-cost region.
- Bangtinh!H161:H163 remaining/total construction value.

## Formula policy
Mapped INPUT cells may be filled.
FORMULA_PROTECTED cells must retain formula text unless the profile explicitly declares an approved transformation.
Unknown cells remain untouched.

## Recalculation
Canonical CenValue calculation engine establishes truth.
Generated workbook is marked for full recalculation on open.
Qualification tests use Microsoft Excel automation when available to force actual recalculation and compare declared checkpoints.
openpyxl/formula preservation alone is not accepted as proof of recalculation.

## Profile compatibility
A workbook is accepted only if:
- required sheets exist;
- required checkpoint/formula signatures match the profile;
- known protected/helper regions are structurally compatible;
- no unknown external dependency affects required outputs.

Otherwise: `UNSUPPORTED_TEMPLATE` and no silent fill.
