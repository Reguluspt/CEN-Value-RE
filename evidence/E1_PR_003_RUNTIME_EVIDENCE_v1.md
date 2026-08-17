# E1-PR-003 — Runtime Evidence v1

**Date:** 2026-08-17
**Repository:** `Reguluspt/CEN-Value-RE`
**Accepted base:** `7e60be157e6b0d5300ffaa8dabac1aadc73f96fb`
**Runtime-tested implementation HEAD:** `c8fd43df4b2f15be430ae2a5dcc9c4f151caba33`
**Binding GitHub Actions run:** `32037927058`
**Gate:** `HumanIndicationGate`

## 1. Binding environment and result

Run `32037927058` completed SUCCESS on Microsoft Windows Server 2025 with CPython `3.11.9`.

- dependency install: PASS;
- `git diff --check 7e60be157e6b0d5300ffaa8dabac1aadc73f96fb..HEAD`: PASS;
- `python -m compileall -q src/re`: PASS;
- full `tests/re`: **206 passed in 4.78s**;
- focused E1-PR-003 suite: **20 passed in 0.26s**.

Runtime dependency set included Flask `3.1.1`, sqlcipher3 `0.6.2`, pywin32 `312`, and pytest `9.1.1`.

GitHub Actions checked out PR merge commit `cab6bcb7e55ad670a1c231747af7a1d192c6b3b6`. Its tree SHA is `8808d6d345aba43d994152fd7f55f19373c1ef51`, exactly equal to runtime-tested branch HEAD `c8fd43df4b2f15be430ae2a5dcc9c4f151caba33` tree SHA `8808d6d345aba43d994152fd7f55f19373c1ef51`. The tested tree therefore contains exactly the implementation under review plus the accepted base, with no merge-only content difference.

## 2. Capability evidence

The binding run covers:

- Golden comparable quality metrics from accepted E1-PR-002 adjustment snapshots;
- explicit selected `0%` retained as a decision while excluded from adjustment count/amplitude;
- Decimal-only gross/net/count/amplitude calculation;
- inclusive `<= 15%` readiness tests for exact-boundary, inside, and outside cases;
- advisory unique-minimum-gross recommendation;
- frozen zero-gross tie-average branch;
- equal non-zero minimum-gross tie remaining ambiguous rather than inventing a general averaging rule;
- human selection of any current comparable without arbitrary caller-supplied final numeric price;
- explicit human actor/reason/time authority;
- raw and rounded indicated unit price kept separately;
- N08-0038 template-default 1,000 VND/m² rounding;
- case-level UNIT_PRICE rounding override including selected-by/selected-at audit metadata;
- exact case/profile binding for template-default rounding;
- migration v4 immutable human-indication snapshot and immutable three-source adjustment evidence bindings;
- semantic SHA reconstruction from immutable human-indication content;
- stale adjustment evidence rejection after rate reselection;
- historical human snapshot reproducibility after source drift while `resolve_current_indication()` fails closed until a new human confirmation binds current adjustment evidence.

## 3. Golden proof

Using the provenance-complete Golden C1–C11 fixture accepted in E1-PR-002, the focused suite reproduces:

- TSSS01: count `2`, gross `34642650`, net `-34642650`, amplitude `5–10`, indicated `196308350`;
- TSSS02: count `4`, gross `83662250`, net `-11951750`, amplitude `5–15`, indicated `227083250`;
- TSSS03: count `4`, gross `35366940`, net `15718640`, amplitude `3–5`, indicated `212201640`;
- Golden human selected/raw indication: `196308350`;
- N08 template-default rounded indication: `196308000`.

The accepted E1-PR-002 Golden source workbook SHA and direct decision-cell provenance are consumed unchanged; E1-PR-003 does not introduce or reverse-solve any adjustment rate.

## 4. Run history / supersession

- `32036909796`: non-binding; stopped at diff hygiene because the initial contract Markdown contained trailing whitespace.
- `32036989649`: non-binding; full suite reached `200 passed / 2 failed`, exposing one precision-sensitive test literal and one forward-compatibility schema assertion; both were corrected.
- `32037384853`: successful intermediate run (`204/204` full, `18/18` focused) but **superseded** by later hardening of complete `RoundingPolicy` snapshot metadata and current-human-indication freshness.
- `32037927058`: **binding final implementation run**, `206/206` full and `20/20` focused PASS.

Any other workflow run from an intermediate E1-PR-003 commit is non-binding. Only run `32037927058` binds the final implementation behavior.

## 5. Claim boundary

This evidence supports only E1-PR-003 / `HumanIndicationGate`.

It does not claim E1-PR-004 final valuation composition, CTXD engine, workbook generation, Microsoft Excel qualification, OCR/Maps, Historical Learning, approval round-trip, full Astryx workbench, or Epic 1 closure.

## 6. Post-test binding rule

After runtime-tested HEAD `c8fd43df4b2f15be430ae2a5dcc9c4f151caba33`, only evidence/report/handoff updates and removal of the one-time E1-PR-003 verifier may be present before independent review.

Any post-test change to source, tests, migration, domain contract, persistence behavior, rounding behavior, freshness semantics, Golden values, dependencies, or runtime-bearing configuration invalidates run `32037927058` and requires a new full Windows run.
