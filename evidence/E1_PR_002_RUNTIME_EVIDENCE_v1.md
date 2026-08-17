# E1-PR-002 — Runtime Evidence v1

**Date:** 2026-08-17  
**Repository:** `Reguluspt/CEN-Value-RE`  
**Accepted base:** `c4e5753c328443e63ce474c03ecbbbf31a2370ed`  
**Runtime-tested HEAD:** `83f742baf42b9f56c887b80c38b15972f22650a4`  
**Binding GitHub Actions run:** `32009934815`  
**Runner:** `windows-latest` / Microsoft Windows Server 2025  
**Python:** `3.11.9`

## 1. Result

Binding run `32009934815` completed SUCCESS on exact implementation HEAD `83f742baf42b9f56c887b80c38b15972f22650a4`.

- dependency install: PASS;
- `git diff --check c4e5753...HEAD`: PASS;
- `python -m compileall -q src/re`: PASS;
- full accepted `tests/re`: **177 passed in 3.21s**;
- focused E1-PR-002 suite: **27 passed in 0.13s**.

Runtime dependency set:

- Flask `3.1.1`;
- sqlcipher3 `0.6.2`;
- pywin32 `312`;
- pytest `9.1.1`.

## 2. Scope proof

The tested implementation proves:

- exact frozen C1–C11 order and canonical factor keys;
- market normalization using deterministic Decimal arithmetic;
- supplied/precomputed construction aggregate remains an Epic-1 boundary input rather than a CTXD engine;
- explicit selected `0%` remains a valid decision;
- missing/unreviewed decision blocks a complete adjustment run;
- C1 uses `P0`, C2 uses `P1`, and C3–C11 use frozen `P1` as adjustment-amount base;
- binary floats fail at canonical numeric boundaries;
- calculation remains deterministic under changed ambient Decimal precision;
- human rate selection writes current decision state plus append-only selection audit metadata;
- source-data drift marks a decision `SOURCE_DATA_CHANGED` without overwriting its selected rate;
- stale or source-revision-mismatched decisions block calculation;
- complete decision sets produce SHA-bound immutable calculation snapshot records;
- migration v3 installs case/comparable/decision/audit/snapshot lineage guards;
- accepted E1-PR-001 manual-data behavior remains green on schema v3.

## 3. Golden decision source proof

The Library reference workbook used for source extraction is:

`(Trunghd_HTG) N08-0038-Huedtl-MTNguyenVanDau-P5-PhuNhuan-htg.xlsx`

Verified workbook SHA-256:

`d410cfcc2263d7d50a436a79e192461f04b6863e6c3676a28da7a2eed287389c`

This exactly matches the workbook SHA already recorded by the canonical Golden Fixture.

The direct stored adjustment decision cells were read from `Bangtinh` columns F/G/H at rows:

`55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105`.

That yields 33 direct selected-rate source cells for TSSS01/02/03. The versioned fixture is:

`fixtures/GOLDEN_CASE_ADJUSTMENT_DECISIONS_v1.json`

Fixture controls:

- each decision carries exact source cell provenance;
- each rate is stored as canonical fractional Decimal text;
- explicit zero is represented as a selected decision;
- workbook actor metadata is explicitly `NOT_AVAILABLE_IN_SOURCE_WORKBOOK` rather than fabricated;
- fixture semantic SHA-256 is checked by tests.

Using those direct source rates with the frozen adjustment graph reproduces exactly:

- TSSS01 / `Bangtinh!F108 = 196308350`;
- TSSS02 / `Bangtinh!G108 = 227083250`;
- TSSS03 / `Bangtinh!H108 = 212201640`.

No rate was invented, reverse-solved from F108/G108/H108/H119, or inferred from an expected output.

## 4. Superseded run history

Run `32009701673` on HEAD `7d3a527f01c1a9893c11f15edab4dd7dee46d3af` is non-binding.

It established:

- dependency install PASS;
- diff hygiene PASS;
- compile PASS;
- **175 passed / 2 failed** in the full suite.

Both failures were stale E1-PR-001 test assertions that hard-coded `LATEST_SCHEMA_VERSION == 2` and exact migration list `[1,2]`. They did not expose a product calculation failure. The E1-PR-001 guards were corrected narrowly so they continue to verify migration v2 exactly while allowing later strictly ordered migrations. The corrected exact head then produced the binding 177/177 and 27/27 result above.

## 5. Claim boundary

This evidence supports only `AdjustmentCalculationGate` / E1-PR-002 behavior.

It does **not** claim:

- comparable-quality / 15% readiness PASS;
- human final indicated-price selection PASS;
- final subject valuation PASS;
- CTXD calculation-engine PASS;
- workbook generation PASS;
- Microsoft Excel qualification PASS;
- Epic 1 closure.

## 6. Binding rule

Any source, test, migration, calculation contract, fixture decision value, or persistence behavior change after runtime-tested HEAD `83f742baf42b9f56c887b80c38b15972f22650a4` requires a new full Windows run before acceptance.

Evidence/report/handoff additions and removal of the one-time verification workflow may form the post-test review delta only if they do not alter implementation-bearing behavior.
