# Golden Case Checkpoint Manifest v0.1
**Case:** N08-0038 exemplar
**Purpose:** Walking Skeleton regression oracle

## Fixture inputs
The exemplar workbook plus an extracted canonical-case fixture will form the initial golden case. The canonical fixture must include:
- appraisal_date;
- TSTĐ land/location/comparison fields;
- TSSS01–03 market/property fields;
- adjustment decisions including explicit zero;
- CTXD input/condition fields;
- selected indicated price/final result inputs.

## Mandatory checkpoint groups
1. Market normalization / negotiated prices.
2. Normalized base unit price prior to property adjustments.
3. Each factor adjustment amount and running indicated unit price.
4. F108:H108 final comparable indications.
5. Gross/net/count/amplitude quality metrics.
6. Selected/recommended indication and H119 rounding.
7. CTXD remaining-quality age/expert/average.
8. Replacement cost and remaining CTXD value.
9. Final land + CTXD result checkpoints once final result region is fully traced.

## Comparison rule
Each checkpoint carries its own explicit rounding/scale rule.
No single global floating-point epsilon.
Decimal arithmetic is used in CenValue.

## Acceptance status
- Adjustment structure: READY FOR FIXTURE EXTRACTION.
- CTXD structure: READY FOR FIXTURE EXTRACTION.
- Final total valuation: READY FOR FIXTURE EXTRACTION; Bangtinh G171/G169/G178/G181/G182 identified.
- Template compatibility: PENDING complete profile fingerprint/signature.
