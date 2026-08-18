# E1-PR-005 — Deterministic Package Metadata Hotfix Runtime Evidence v1

**Date:** 2026-08-18
**Repository:** `Reguluspt/CEN-Value-RE`
**PR:** #17
**Accepted base:** `be537e573d6692c6cbfaf5a6cb3710ad7c229177`
**Runtime-tested implementation HEAD:** `4bfc75e796295adb4aeb9fbfb3c5c1ce487fdc2f`
**Binding Windows run:** `32135261987`
**Tested PR merge-ref:** `47c0caf0f8732417faf6d891ad371a53aefcbddc`
**Binding runtime tree:** `48def79cbb35e56809cc4feb1588029cb0d1797c`

## Binding result

Run `32135261987` completed SUCCESS on Microsoft Windows Server 2025 with CPython `3.11.9`.

- dependency install: PASS;
- `git diff --check be537e573d6692c6cbfaf5a6cb3710ad7c229177..HEAD`: PASS;
- `python -m compileall -q src/re`: PASS;
- full `tests/re`: **250 passed in 7.07s**;
- focused writer/publication/package-determinism suite: **9 passed in 2.92s**.

The checked-out merge-ref `47c0caf0f8732417faf6d891ad371a53aefcbddc` has tree `48def79cbb35e56809cc4feb1588029cb0d1797c`, exactly equal to runtime-tested branch HEAD `4bfc75e796295adb4aeb9fbfb3c5c1ce487fdc2f` tree.

## Reproduction closed

The new regression proof performs two otherwise identical supported-profile generations with a deliberate `1.2s` delay between saves. This crosses the wall-clock boundary that previously allowed `openpyxl==3.1.5` to produce a different `docProps/core.xml` modified value and therefore a different package SHA.

The binding run proves byte-for-byte identical generated outputs and identical artifact SHA values across that boundary.

## Bounded change

The hotfix changes only deterministic package metadata normalization:

- source `docProps/core.xml` `dcterms:modified` value is captured from the supported source package;
- generated package normalization restores that stable source-derived value after openpyxl save;
- ZIP member ordering/timestamps remain canonicalized as before.

No change is made to workbook write allowlists, formula protection, E5 compatibility transformation, source SHA qualification, fingerprint authority, C1–C11 semantics, publication safety, canonical state binding, or Excel qualification state.

## Claim boundary

This evidence closes only the inherited deterministic generated-package SHA regression discovered while running E1-PR-006 regressions. It does not re-open or expand E1-PR-005 business scope and does not claim Microsoft Excel Desktop qualification PASS.

After runtime-tested HEAD `4bfc75e796295adb4aeb9fbfb3c5c1ce487fdc2f`, only evidence/report/handoff updates and removal of the one-time hotfix verifier are permitted before independent review. Any source/test/dependency/runtime-bearing change requires a new binding run.