# E1-PR-005 — Deterministic Package Metadata Hotfix Independent Review Handoff v1

**Repository:** `Reguluspt/CEN-Value-RE`
**PR:** #17
**Accepted base:** `be537e573d6692c6cbfaf5a6cb3710ad7c229177`
**Runtime-tested implementation HEAD:** `4bfc75e796295adb4aeb9fbfb3c5c1ce487fdc2f`
**Binding Windows run:** `32135261987`
**Binding runtime tree:** `48def79cbb35e56809cc4feb1588029cb0d1797c`
**Tested merge-ref:** `47c0caf0f8732417faf6d891ad371a53aefcbddc`

## Review question

Does this bounded corrective change restore the already-accepted E1-PR-005 invariant that identical supported source bytes plus identical canonical payload produce an identical generated XLSX package SHA, without weakening any E1-PR-005 write/formula/currentness/publication/qualification boundary?

## Exact implementation scope

Source change:

- `src/re/adapters/excel_output/openpyxl_writer.py`

Proof change:

- `tests/re/test_workbook_output_package_determinism_hotfix.py`

One-time verifier:

- `.github/workflows/e1-pr-005-determinism-hotfix-verify.yml` (removed before final review HEAD)

Evidence/report files are non-runtime.

## Root cause to verify

The prior deterministic normalization fixed ZIP entry ordering and ZIP member timestamps but did not stabilize `docProps/core.xml` `dcterms:modified`. `openpyxl==3.1.5` mutates this metadata on each save, making package SHA depend on wall-clock timing.

The corrective implementation reads the source package's `dcterms:modified` value and restores only that value in the generated package during normalization.

## Required checks

Reviewer should verify:

- no source workbook mutation;
- no change to cell write allowlist;
- no change to formula protection or Gate B.10 consumers;
- no change to E5 compatibility transformation authority;
- no change to canonical payload/final snapshot binding;
- no change to create-if-absent output publication and owned cleanup;
- normalization is deterministic and source-derived;
- core metadata normalization does not claim or fabricate appraisal/business evidence;
- the delayed regression test proves identical bytes/SHA across a real wall-clock boundary;
- binding run `32135261987` is valid for runtime-tested HEAD/tree and merge-ref tree;
- post-runtime delta contains only evidence/report/handoff and verifier removal.

## Binding run

Windows Server 2025 / CPython 3.11.9:

- dependency install PASS;
- diff hygiene PASS;
- compile PASS;
- full RE suite: **250 passed in 7.07s**;
- focused writer/publication/determinism: **9 passed in 2.92s**.

## Verdict boundary

Return `ACCEPTED` or `RETURN FINDINGS` for this hotfix only. Acceptance does not constitute Microsoft Excel Desktop qualification and does not close Epic 1.

PR #16 / E1-PR-006 remains draft until this hotfix is independently accepted, merged with expected-head protection, and PR #16 is rebased/updated onto that new accepted main.