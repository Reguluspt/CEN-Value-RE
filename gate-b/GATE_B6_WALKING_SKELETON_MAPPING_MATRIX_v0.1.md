# Gate B.6 — Walking Skeleton Mapping Matrix v0.1
**Workbook:** N08-0038_Huedtl_MTN_TranNguyenVanDau_UNLOCKED.xlsx
**Scope:** Epic 1 Walking Skeleton
**Status:** BASELINE — expand during golden-fixture construction

## Mapping rule
Every required datum follows:
`Business meaning → UI field → canonical field → ExcelTemplateProfile mapping → formula/checkpoint`

Unknown workbook cells are read-only by default.

## Case-level
| Business meaning | Canonical | Workbook | Direction | Rule |
|---|---|---|---|---|
| Appraisal date | `AppraisalCase.appraisal_date` | legacy case/Ho-so input region; CTXD formulas previously used `NOW()` | UI→canonical→Excel | canonical date is authoritative; volatile current-date behavior is neutralized |
| Case code | `AppraisalCase.case_code` | Ho-so / document-output regions | bidirectional profile mapping | profile-specific |

## Subject Property / TSTĐ
| Business meaning | Canonical | Workbook evidence | Direction |
|---|---|---|---|
| Current locality/province | property current address/locality | `Nhập liệu!F9`; stale external reference at `Phieu TTTT!E5` | canonical→both cells |
| CTXD type/profile | `ConstructionAsset.construction_type` | `Nhập liệu!F73` → `Sheet1!A4` | canonical→Excel |
| Construction year | `ConstructionAsset.year_built` | `Nhập liệu!F74` → `Bangtinh!B127` | canonical→Excel |
| Structure description | `ConstructionAsset.structure_description` | `Nhập liệu!F75` → `Sheet1!A6` | canonical→Excel |

Property characteristics such as area/frontage/depth/road width remain in the typed `PropertyCharacteristic` registry. Exact source cells are added to the profile as the corresponding adjustment factor is frozen.

## TSSS
Legacy comparable blocks are column-oriented in `Phieu TTTT` and `Bangtinh`; sampled comparable columns in adjustment calculations are F:G:H.

TSSS property/source data maps to `ComparableProperty` + `MarketObservation`; adjustment percentages never live in those source records.

## Adjustment Grid — mandatory profile mapping
| Factor | Rate row | Amount row | Running result row | Canonical |
|---|---:|---:|---:|---|
| C1 Pháp lý | 55 | 56 | 57 | `AdjustmentDecision(C1)` |
| C2 Vị trí | 60 | 61 | 62 | `AdjustmentDecision(C2)` |
| C3 dynamic | 65 | 66 | 67 | `AdjustmentDecision(C3)` |
| C4 Quy mô/diện tích | 70 | 71 | 72 | `AdjustmentDecision(C4)` |
| C5 Mặt tiền | 75 | 76 | 77 | `AdjustmentDecision(C5)` |
| C6 Chiều dài | 80 | 81 | 82 | `AdjustmentDecision(C6)` |
| C7 Hình dáng | 85 | 86 | 87 | `AdjustmentDecision(C7)` |
| C8 Giao thông | 90 | 91 | 92 | `AdjustmentDecision(C8)` |
| C9 Môi trường kinh doanh | 95 | 96 | 97 | `AdjustmentDecision(C9)` |
| C10 dynamic | 100 | 101 | 102 | `AdjustmentDecision(C10)` |
| C11 Bất lợi khác | 105 | 106 | 107 | `AdjustmentDecision(C11)` |

Comparable columns: `Bangtinh!F:H`.

Final comparable indicated unit prices: `Bangtinh!F108:H108`.

## Comparable quality
| Metric | Workbook | Canonical |
|---|---|---|
| Gross adjustment | `Bangtinh!F112:H112` / `Sheet1!A22:C22` | `ComparableCalculation.gross_adjustment` |
| Adjustment count | `Bangtinh!F113:H113` / `Sheet1!A20:C20` | `ComparableCalculation.adjustment_count` |
| Adjustment amplitude | `Bangtinh!F114:H114` / `Sheet1!A18:C18` | `ComparableCalculation.adjustment_amplitude` |
| Net adjustment | `Bangtinh!F115:H115` / `Sheet1!A24:C24` | `ComparableCalculation.net_adjustment` |
| Final indicated price | `Bangtinh!H119` ← `Sheet1!G18` | `ValuationResult.indicated_unit_price` |

## CTXD checkpoints
| Meaning | Workbook | Canonical |
|---|---|---|
| Age-method remaining quality | `Bangtinh!H127` | CTXD calculation snapshot |
| Expert remaining quality | `Bangtinh!F140` (+ corresponding blocks) | CTXD component assessment result |
| Average remaining quality | `Bangtinh!H153` | `remaining_quality_pct` |
| Replacement cost | `Bangtinh!G156:G157` | `replacement_cost_vnd` |
| Remaining value | `Bangtinh!H161:H162` | `remaining_value_vnd` |
| Total CTXD | `Bangtinh!H163` | `ValuationResult.construction_value_vnd` |

## Output-profile special transformation
`Phieu TTTT!E5` stale external self-reference is replaced with the same canonical locality value mapped to `Nhập liệu!F9`.

## Profile cell classes
- INPUT
- FORMULA_PROTECTED
- OUTPUT_CHECKPOINT
- CONTROL
- APPROVAL_RETURN
- VOLATILE_COMPAT_OVERRIDE

## Blocking items before profile freeze
1. resolve C3/C10 labels and upstream source fields;
2. map all TSTĐ/TSSS source cells used by C1–C11;
3. trace final land-value/total-value output cells;
4. map workbook approval-return cells;
5. build golden fixture values after real Excel recalculation.
