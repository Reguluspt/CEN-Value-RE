# E1-PR-004 — Runtime Evidence v1

**Date:** 2026-08-17
**Repository:** `Reguluspt/CEN-Value-RE`
**PR:** #14
**Accepted base:** `eef0a9111f1977a49bad11ace2089d9c73ca5772`
**Runtime-tested implementation HEAD:** `e66be8d3ea419eb736012b06c81f669b30c76a78`
**Binding GitHub Actions run:** `32043291836`
**Gate:** `FinalValuationCompositionGate`

## 1. Binding environment and result

Run `32043291836` completed SUCCESS on Microsoft Windows Server 2025 with CPython `3.11.9`.

- dependency install: PASS;
- `git diff --check eef0a9111f1977a49bad11ace2089d9c73ca5772..HEAD`: PASS;
- `python -m compileall -q src/re`: PASS;
- full `tests/re`: **229 passed in 4.11s**;
- focused E1-PR-004 suite: **17 passed in 0.33s**.

Runtime dependencies included Flask `3.1.1`, sqlcipher3 `0.6.2`, pywin32 `312`, and pytest `9.1.1`.

GitHub Actions checked out PR merge-ref `f51d7d3e4596d5e004c8919f9df61c01a99fa656`. Its tree SHA is `21905f501b2385dce3c868bca5daa18eb3c260a9`, exactly equal to runtime-tested branch HEAD `e66be8d3ea419eb736012b06c81f669b30c76a78` tree SHA `21905f501b2385dce3c868bca5daa18eb3c260a9`.

## 2. Capability evidence

The binding run covers:

- Decimal-only deterministic land/final composition independent of ambient Decimal precision;
- compliant `MARKET_INDICATED` land component using the current **rounded** human indicated unit price;
- conflicting caller/manual price on a market-indicated component failing closed;
- explicit separately-valued noncompliant/planning component requiring unit price and provenance;
- typed append-only `SUPPLIED_PRECOMPUTED` construction aggregate with evidence, actor, revision and semantic SHA;
- no CTXD age/expert/replacement-cost/remaining-value calculation path;
- distinct `total_value_before_rounding_vnd` and `final_appraised_value_vnd`;
- trusted-profile `TOTAL_VALUE` template-default rounding and audited case override;
- migration v5 immutable final valuation snapshot, construction input and land-source bindings;
- current-result rejection after land-component drift, construction rebind, appraisal-date drift, template-profile drift or upstream human-indication/adjustment drift;
- final snapshot semantic SHA reconstruction from immutable persisted snapshot content.

## 3. Golden acceptance proof

The focused suite reproduces the frozen N08 values:

- compliant area `82.93 m²` × rounded human indication `196308000` = `16279822440` (`Bangtinh!G171`);
- noncompliant area `20.27 m²` × explicit `106000000` = `2148620000`;
- recognized land = `18428442440` (`Bangtinh!G169`);
- supplied construction aggregate = `1152970000` (`Bangtinh!G178` boundary input);
- `total_value_before_rounding_vnd = 19581412440` (`Bangtinh!G181`);
- N08 trusted TOTAL_VALUE rounding produces `final_appraised_value_vnd = 19581000000` (`Bangtinh!G182`).

Gate B.10 `Offical!E32` consumes the pre-rounded G181-equivalent `19581412440`. E1-PR-004 does not write workbook cells.

## 4. Run history / supersession

- `32042474374`: non-binding; diff hygiene failed on contract Markdown trailing whitespace before compile/tests.
- `32042578931`: non-binding; full suite reached `223 passed / 2 failed`, exposing one forward-compatibility schema assertion and one real ambient-Decimal accumulation defect; both were corrected.
- later successful intermediate run on `1a461dcb65e5453037b35acbf911dec7d030ee80`: superseded by currentness hardening for appraisal-date/template-profile drift.
- `32043143295`: non-binding; `225 passed / 4 failed`, all four failures from a new test-harness helper omission.
- `32043209950`: non-binding; `228 passed / 1 failed`, where product correctly rejected stale upstream evidence but the test asserted an over-specific error message.
- `32043291836`: **binding final implementation run**, `229/229` full and `17/17` focused PASS.

Only run `32043291836` binds the final E1-PR-004 implementation behavior.

## 5. Claim boundary

This evidence supports only E1-PR-004 / `FinalValuationCompositionGate`.

It does not claim the Epic 2 CTXD calculation engine, E1-PR-005 workbook generation, Microsoft Excel qualification, OCR/Maps, Historical Learning, approval return/revision, full Astryx workbench, or Epic 1 closure.

## 6. Post-test binding rule

After runtime-tested HEAD `e66be8d3ea419eb736012b06c81f669b30c76a78`, only this runtime evidence, the implementation report, the independent-review handoff, and removal of `.github/workflows/e1-pr-004-verify.yml` may be present before independent review.

Any post-test change to source, tests, migration, contract, persistence behavior, rounding behavior, currentness semantics, Golden values, dependencies, or runtime-bearing configuration invalidates run `32043291836` and requires a new full Windows run.
