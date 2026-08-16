# 12 — Valuation Result
**Status: REVIEWED — GUIDANCE/QUALITY CONTRACT DERIVED; FINAL PROPERTY-VALUE TRACE STILL OPEN**

## Comparable indication
Each comparable produces a final indicated unit price.

Sample workbook:
- final indicated prices: `Bangtinh!F108:H108`;
- arithmetic average: `Bangtinh!G109`;
- deviation from average: `Bangtinh!F110:H110`.

## Quality metrics shown to appraiser
- gross adjustment;
- adjustment count;
- min/max absolute non-zero adjustment amplitude;
- net adjustment;
- 15% deviation readiness validation;
- information quality.

## Recommendation
Normal workbook behavior selects the comparable with minimum gross adjustment. A special average branch exists only when two or three gross-adjustment values are zero.

CenValue does not encode workbook narrative concatenation as business logic. It creates a structured `GuidanceCandidate` with metrics and recommendation reason.

The appraiser confirms final indicated price.

## Final property result
May combine:
- land value;
- Σ CTXD values with `valuation_treatment = VALUE`.

`DESCRIBE_ONLY` CTXD never contributes value.

## Determinism
All result/calculation snapshots include `appraisal_date`; closed results must not change because the computer date changes.

## OPEN
- full downstream trace from indicated unit price to final property value;
- final rounding steps;
- exceptional/tie decision contract beyond workbook-supported zero-gross branch;
- final approval/checkpoint matrix.
