# CenValue RE — Gate B Closure Report v1

**Date:** 2026-08-15  
**Status:** FROZEN FOR WALKING SKELETON

## Gate objective
Turn the legacy workbook into reproducible calculation/output contracts before application feature coding.

## Closed contracts
- CTXD calculation chain and appraisal-date reference.
- Adjustment Factor Registry C1–C11.
- Adjustment calculation structure and explicit-zero behavior.
- Comparable-quality metrics, amplitude and 15% readiness rule.
- Indicated-price recommendation + human decision boundary.
- Land + CTXD + final valuation chain.
- Raw vs rounded result separation and configurable `RoundingPolicy`.
- Output-consumer distinction between pre-final-rounding and final-rounded totals.
- ExcelTemplateProfile/fingerprint/fail-safe policy.
- Known stale external link localization.
- Golden fixture/checkpoint baseline.
- Microsoft Excel qualification protocol.
- Dependency classification boundary.

## Canonical rounding
`raw_value -> RoundingPolicy -> rounded_value`

N08-0038 defaults:
- UNIT_PRICE: 1,000 VND/m².
- TOTAL_VALUE: 1,000,000 VND.

Case-level override is allowed and auditable.

## Dependency closure
Legacy direct cell references are classified by responsibility:
`CANONICAL_INPUT | DERIVED | CONTROL | LEGACY_ONLY | OUT_OF_SCOPE`.

The new domain does not reproduce Excel's cell graph one-for-one.

## Release philosophy
CenValue calculation engine is canonical truth.
Excel is compatibility/output oracle.
A profile cannot be release-qualified without real Microsoft Excel recalculation evidence for mandatory checkpoints.

## Gate result
Gate B is sufficiently closed to start Epic 0 Engineering Foundation.

Unknown legacy dependencies discovered later remain fail-safe findings and cannot silently alter a mandatory checkpoint.
