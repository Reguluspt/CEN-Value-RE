# Gate B.14 — Remaining Dependency Classification Baseline
**Status:** WALKING-SKELETON BOUNDARY FROZEN; implementation inventory remains generated evidence

## Decision
The dependency audit found many direct references from legacy sheets. A direct Excel dependency does **not** automatically become a CenValue canonical field.

Each dependency is classified by business responsibility:

### CANONICAL_INPUT
User/business data that must survive independently of Excel.
Examples:
- case/appraisal metadata;
- subject legal/location/land/CTXD characteristics;
- TSSS evidence, sale/asking price and negotiated price;
- comparable characteristics;
- professional adjustment rates;
- rounding policy selection.

### DERIVED
Values CenValue calculates from canonical inputs.
Examples:
- normalized comparable base price;
- adjustment amount/running indicated price;
- comparable quality metrics;
- CTXD remaining quality/replacement/remaining value;
- land value, total value, rounded value.

### CONTROL
Template/profile configuration or lookup selection needed to reproduce a workbook.
Examples:
- bank/template selector;
- fixed construction structural weights;
- lookup-table keys;
- template output conditions.

### LEGACY_ONLY
Helper text/layout/calculation plumbing needed only by the legacy workbook and reproducible from canonical/derived data. It is not persisted as a business field.

### OUT_OF_SCOPE
Legacy cells not required for the Walking Skeleton appraisal/approval loop. They remain untouched and do not block the first implementation unless a mandatory output consumes them.

## Closure rule
A dependency blocks Epic 1 only when it affects a mandatory Walking Skeleton checkpoint/output and cannot be reproduced from CANONICAL_INPUT + DERIVED + CONTROL.

Therefore the previously identified hundreds of direct legacy references are not converted one-for-one into the new schema.

## Walking Skeleton mandatory boundary
Must be reproducible:
1. case metadata and appraisal date;
2. TSTĐ land/legal/location/comparison characteristics;
3. CTXD where present, including VALUE / DESCRIBE_ONLY;
4. TSSS01–03 core evidence and comparison characteristics;
5. adjustment C1–C11;
6. quality metrics and indicated-price recommendation;
7. land + included CTXD final valuation;
8. configurable RoundingPolicy;
9. approval workbook generation and returned-result import;
10. required structured/report output fields.

Legacy presentation helpers outside this chain are LEGACY_ONLY/OUT_OF_SCOPE unless dependency testing proves otherwise.

## Fail-safe rule
During adapter implementation, any newly discovered unknown dependency that changes a mandatory checkpoint is promoted to a design finding and must be classified before release. It may not be silently ignored.
