# Gate B — Design Closure Status v0.2

## Closed for exemplar
- CTXD calculation structure.
- Appraisal-date effective-age revision.
- Adjustment Factor Registry C1–C11.
- Adjustment base/additive-running behavior.
- Explicit-zero semantics.
- Comparable quality metrics.
- Exact adjustment-amplitude formula.
- Indicated-price helper/selection behavior.
- Final land + CTXD + total value chain.
- Distinction between pre-final-rounding total and final million-rounded appraisal value.
- Output consumer mapping for G181 vs G182.
- H119 and G182 rounding checkpoints.
- Stale external-link classification.
- ExcelTemplateProfile baseline.
- Structural/formula fingerprint baseline.
- Canonical golden-case fixture v0.1.
- Golden checkpoint expected-value manifest v0.2.
- Microsoft Excel qualification protocol v1.
- Mapping matrix currently contains 195 approved field/control/checkpoint rows.

## Remaining before Gate B can be declared fully FROZEN
1. Classify the remaining direct workbook dependencies needed by the Walking Skeleton as:
   `CANONICAL_INPUT | DERIVED | CONTROL | LEGACY_ONLY | OUT_OF_SCOPE`.
2. Add any missing canonical mappings that materially affect:
   - subject property,
   - TSSS01–03,
   - adjustment base,
   - final valuation,
   - approval workbook.
3. Freeze bank/profile-specific branches as output/profile policy, keeping them out of core domain.
4. Run the first real Microsoft Excel qualification on Windows when the implementation harness exists.

## Design readiness
The core calculation/output model is sufficiently understood to proceed with dependency classification.
Feature coding should still wait until item 1–3 are closed into the Epic 1 mapping/profile contract.
