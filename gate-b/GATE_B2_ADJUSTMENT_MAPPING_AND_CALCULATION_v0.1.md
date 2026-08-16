# Gate B.2 — Adjustment Mapping & Calculation Contract v0.1
**Workbook:** N08-0038...
**Sheet:** Bangtinh rows 47–120
**Status:** WORKBOOK-DERIVED / PARTIALLY FROZEN


> **SUPERSEDED STATUS NOTE — 2026-08-16**  
> This v0.1 file is retained as historical workbook evidence. Later Gate B contracts/closure resolve the factor registry, 15% readiness control, and final selection dependencies. Use `GATE_B8_ADJUSTMENT_FACTOR_REGISTRY_v1.md`, the later mapping/selection contracts, and `GATE_B_CLOSURE_REPORT_v1.md` as current authority. Statements below that say a later-traced item “remains to be frozen” are historical, not current blockers.

## Factor sequence observed
C1 Pháp lý
C2 Vị trí
C3 dynamic factor from Bangtinh!B14
C4 Quy mô, diện tích
C5 Mặt tiền
C6 Chiều dài
C7 Hình dáng
C8 Giao thông
C9 Môi trường kinh doanh
C10 dynamic factor from Bangtinh!B18
C11 Yếu tố bất lợi khác

The two dynamic labels must be resolved from their upstream workbook cells before the Factor Registry is frozen.

## Adjustment-rate rows
C1 55; C2 60; C3 65; C4 70; C5 75; C6 80; C7 85; C8 90; C9 95; C10 100; C11 105.
Comparable columns are F:H in this sample.

## Comparison semantics
Workbook derives:
- rate = 0 → `Tương đồng`
- rate > 0 → comparable `Kém hơn`
- rate < 0 → comparable `Tốt hơn`

This is presentation derived from the human-selected adjustment rate, not an independent source field.

## Critical calculation behavior
The workbook is not a purely chained multiplicative adjustment.

It establishes a post-transaction unit-price base at row 57 and many later adjustment amounts are calculated against that same base:
`adjustment_amount_i = selected_rate_i × row57_base_unit_price`

The running adjusted price is then accumulated across factors.

Observed examples:
- C2 amount = rate × row57; result = row57 + amount.
- C3 amount = rate × row57; result = previous result + amount.
- C4...C11 follow the same base-row pattern in this sample.

Therefore the new engine must explicitly model:
1. transaction/legal stage;
2. normalized adjustment base;
3. additive factor adjustment amounts based on that normalized base;
4. running indicated unit price.

Do not implement each factor as `previous_price × (1 + rate)` unless another workbook profile proves that behavior.

## Explicit 0%
The workbook contains many legitimate 0% rates. This supports the frozen design rule that zero is a valid explicit decision, not missing data.

## Indicated prices
Row 108 = final running adjusted price for each comparable.
Row 109 = average indicated price.
Row 110 = each comparable's deviation from the average.

## Quality metrics
Rows 112–115 expose:
- gross adjustment value;
- adjustment count;
- adjustment amplitude;
- net adjustment value.

These feed the comparable-quality/indicated-price decision and must be canonical derived metrics, not Excel-only fields.

## Workbook narrative constraints
Row 116 states transaction/legal-related adjustment is performed before property-characteristic adjustments.
Row 117 states the difference around the average indicated unit prices is controlled at no more than 15% in this workbook narrative.

The exact machine validation for the 15% rule remains to be frozen after tracing the corresponding Sheet1 formulas.

## Final indication
Row 119 uses `ROUND(Sheet1!G18,-3)`.
The upstream Sheet1 selection logic must be traced before the final indicated-price selection contract is frozen.

## Next trace
Trace Sheet1 cells feeding:
- A18:C18
- A20:C20
- A22:C22
- A24:C24
- F23
- G18
and their dependencies, then reconcile them with the user-approved rule for selecting the comparable with the smallest gross adjustment subject to information quality and other criteria.
