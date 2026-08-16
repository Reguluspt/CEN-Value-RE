# CenValue RE — Gate B.8 Rounding & Tolerance Matrix v0.1

**Date:** 2026-08-15  
**Status:** SAMPLE PROFILE FROZEN / CROSS-TEMPLATE REVIEW OPEN

| Calculation | Workbook rule | Canonical comparison |
|---|---|---|
| TSSS price after market adjustment | `ROUND(asking × factor, -7)` | exact integer VND after nearest 10,000,000 rounding |
| Comparable land unit price before adjustment | `ROUND(..., -3)` | exact integer VND/m² after nearest 1,000 |
| CTXD age-method remaining quality | `ROUND(..., 2)` | Decimal scale 2 on fractional rate |
| CTXD expert remaining quality | `ROUND(..., 2)` | Decimal scale 2 on fractional rate |
| CTXD average remaining quality | `ROUND(..., 2)` | Decimal scale 2 on fractional rate |
| CTXD replacement cost | multiplication, no explicit ROUND in sample | compare exact integer/Decimal result |
| CTXD remaining value | multiplication, no explicit ROUND in sample | compare exact integer/Decimal result |
| Adjustment amount | rate × declared base, no explicit ROUND | Decimal calculation; compare Excel numeric result after domain precision policy |
| Running indicated price | additive, no explicit ROUND | Decimal calculation; output/checkpoint numeric tolerance ≤ 0.5 VND/m² unless profile states otherwise |
| Final indicated unit price | `ROUND(selected indication, -3)` | exact integer nearest 1,000 |
| Land component value | area × unit price | Decimal product; compare workbook numeric value |
| Property value before rounding | `ROUND(land + CTXD, 0)` | integer VND |
| Final appraised value | `ROUND(value_before_rounding, -6)` | exact integer nearest 1,000,000 |
| Deviation from average | division, no explicit ROUND | compare Decimal; UI percentage display rounding is presentation-only |

## Decimal policy

- Never use binary floating-point as canonical monetary/percentage state.
- Use decimal arithmetic.
- VND money and VND/m² results are persisted as integer VND when the business step has been rounded to an integer.
- Percentage inputs are Decimal percentage/fraction values with explicit scale.
- Areas/lengths remain Decimal.

## Checkpoint tolerance

For explicitly rounded workbook checkpoints: tolerance = 0 after applying the same rounding rule.

For unrounded Excel intermediate decimals:
- compare after converting both sides to the declared Decimal scale;
- default technical tolerance must be stricter than the smallest business-relevant unit and may not hide a different rounding algorithm.

Do not adopt one global tolerance for every checkpoint.

## Open
Validate this matrix against additional historical workbook variants before declaring it template-family universal.
