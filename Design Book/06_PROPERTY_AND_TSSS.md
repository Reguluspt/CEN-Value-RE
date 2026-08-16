# 06 — Subject Property & TSSS
**Status: REVIEWED — SAMPLE WORKBOOK MARKET-NORMALIZATION CONTRACT ADDED**

## TSTĐ
GCN/VBDLIS/manual converge into one canonical TSTĐ form. Extracted values are pre-fill until human confirmation.

Legal land use and appraisal treatment are separate:
- `LandUseComponent` stores legal land-use facts;
- `LandValuationComponent` may split land by planning/valuation treatment even when the legal land-use type is identical.

## TSSS
- Quick Entry + Expanded Entry.
- Primary GĐ1 price facts: source/asking price and price after negotiation/market normalization.
- Historical workbook may contain an intermediate factor such as `Tỷ lệ ước tính giao dịch thành công`; preserve it in provenance/compatibility data rather than silently renaming it.
- One TSSS may have multiple Evidence; GĐ1 avoids a heavy evidence subsystem.
- Duplicate TSSS copies property/source data only; never adjustment decisions or derived quality/indicated-price state.
- Comparison View is for data inspection; it is not Adjustment Grid.

## Comparable price normalization
Sample workbook derives price after market adjustment, deducts estimated CTXD value, applies optional land-use conversion adjustment, and derives an equivalent land unit price used as the Adjustment Engine base.

These formulas are versioned calculation/profile contracts rather than UI-entered duplicate fields.

## Single source of truth
Source property fields are edited only in canonical TSTĐ/TSSS forms. Adjustment Grid references those values read-only and may navigate back to the source field.
