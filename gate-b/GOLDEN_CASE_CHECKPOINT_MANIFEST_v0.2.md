# Golden Case Checkpoint Manifest v0.2
**Fixture:** N08-0038 exemplar
**Status:** EXPECTED VALUES EXTRACTED FROM WORKBOOK CACHE

> These values are the legacy workbook's stored/calculated checkpoint values. They are the first regression oracle. CenValue's appraisal-date revision must be applied when regenerating the canonical fixture.

## Comparable indication
| Checkpoint | Expected |
|---|---:|
| Bangtinh!F108 | 196,308,350 |
| Bangtinh!G108 | 227,083,250 |
| Bangtinh!H108 | 212,201,640 |
| Sheet1!G18 | 196,308,350 |
| Bangtinh!H119 | 196,308,000 |

## Comparable quality
| Metric | TSSS01 | TSSS02 | TSSS03 |
|---|---:|---:|---:|
| Adjustment count | 2 | 4 | 4 |
| Gross adjustment value | 34,642,650 | 83,662,250 | 35,366,940 |
| Adjustment amplitude | 5–10 | 5–15 | 3–5 |
| Net adjustment value | -34,642,650 | -11,951,750 | 15,718,640 |

### Exact amplitude formula
For each TSSS the legacy workbook:
1. takes absolute adjustment-rate values;
2. ignores zero values;
3. returns `min - max` if min != max;
4. otherwise returns the single non-zero magnitude.

This confirms 0% is excluded from the amplitude range while remaining a valid explicit professional decision.

## CTXD
| Checkpoint | Expected |
|---|---:|
| Bangtinh!H127 age-method CLCL | 0.69 |
| Bangtinh!F140 expert CLCL | 0.71 |
| Bangtinh!H153 average CLCL | 0.70 |
| Bangtinh!G156 replacement cost | 1,647,100,000 |
| Bangtinh!G157 noncompliant replacement cost | 0 |
| Bangtinh!H161 remaining value | 1,152,970,000 |
| Bangtinh!H163 total CTXD | 1,152,970,000 |

## Final valuation
| Checkpoint | Expected |
|---|---:|
| Bangtinh!G171 compliant residential land value | 16,279,822,440 |
| Bangtinh!G175 noncompliant residential land value | 2,148,620,000 |
| Bangtinh!G169 recognized land aggregate | 18,428,442,440 |
| Bangtinh!G178 construction/on-land aggregate | 1,152,970,000 |
| Bangtinh!G181 total before million-rounding | 19,581,412,440 |
| Bangtinh!G182 final million-rounded value | 19,581,000,000 |
| Offical!E32 | 19,581,412,440 |

## Important output divergence
`Offical!E32` maps to `Bangtinh!G181`, while the workbook separately calculates final rounded appraisal value at `Bangtinh!G182`.

This difference is **not resolved by assumption**. ExcelTemplateProfile must classify which downstream consumer expects:
- pre-million-rounding `G181`, versus
- final rounded `G182`.

## Regression rule
- Exact rounded-money checkpoints: exact equality after declared ROUND rule.
- Decimal checkpoints: exact equality at declared scale.
- No generic floating-point epsilon.
- Microsoft Excel recalculation is required for template qualification; cached values alone are not final qualification evidence.
