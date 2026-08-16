# Gate B.8 — Golden Fixture & Epic 1 Acceptance Matrix v0.1
**Status:** CONTRACT BASELINE

## Golden fixture principle
The original legacy workbook plus a fixed canonical case-input snapshot and recalculated expected checkpoint values form a golden fixture.

A fixture is immutable once qualified; changes create a new fixture version.

## Minimum fixture set for Epic 1
### GF-01 — Baseline subject + 3 comparables
Purpose: prove Manual TSTĐ → 3 TSSS → Adjustment → indicated price → Excel.

Must cover:
- non-zero positive adjustment;
- non-zero negative adjustment;
- explicit 0%;
- all mandatory quality metrics;
- final indicated-price selection.

### GF-02 — CTXD VALUE
Purpose: prove construction calculation using appraisal date, age method, expert method, replacement cost and remaining value.

### GF-03 — CTXD DESCRIBE_ONLY
Purpose: prove CTXD is present/described but does not run/contribute construction valuation and readiness still passes.

### GF-04 — Tie/equal-minimum comparable case
Purpose: prove tie/average recommendation behavior and human final confirmation.

### GF-05 — Unknown/modified template
Purpose: prove fail-safe fingerprinting; adapter must refuse production write.

## Mandatory checkpoints
Adjustment:
- rate/amount/running result for each enabled factor and TSSS;
- `Bangtinh!F108:H108`;
- `Bangtinh!F112:H115`;
- `Sheet1` quality metrics feeding selection;
- `Bangtinh!H119`.

CTXD:
- `Bangtinh!H127`;
- expert-method result;
- `Bangtinh!H153`;
- `Bangtinh!G156:G157`;
- `Bangtinh!H161:H163`.

Compatibility:
- localized `Phieu TTTT!E5`;
- no unresolved stale external dependency;
- protected-formula signatures unchanged except approved transformations.

## Acceptance assertions
1. Canonical engine result is deterministic across repeated runs.
2. Reopening a case later does not change effective age because calculation uses `appraisal_date`.
3. Explicit 0% remains distinguishable from unset.
4. Source-data changes invalidate dependent selected decisions without overwriting them.
5. Decimal/rounding rules match checkpoint contracts.
6. Generated workbook passes real Microsoft Excel recalculation in qualification environment.
7. Required workbook checkpoints equal expected values under declared rules.
8. Unknown template cannot be written.
9. Excel is never the source of canonical truth for the newly created case.
10. Final valuation requires human confirmation.

## Epic 1 release gate
Epic 1 is not accepted until GF-01 and the required subset of GF-02 pass end-to-end. Remaining fixtures may gate subsequent CTXD/approval hardening depending on final epic cut.
