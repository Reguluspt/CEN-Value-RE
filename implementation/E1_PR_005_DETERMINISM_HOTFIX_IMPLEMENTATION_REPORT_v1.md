# E1-PR-005 — Deterministic Package Metadata Hotfix Implementation Report v1

**Accepted base:** `be537e573d6692c6cbfaf5a6cb3710ad7c229177`
**Runtime-tested HEAD:** `4bfc75e796295adb4aeb9fbfb3c5c1ce487fdc2f`
**Binding run:** `32135261987`

## Problem

During E1-PR-006 full regression, the accepted E1-PR-005 deterministic package test failed once because two otherwise identical generated workbooks produced different SHA-256 values. Re-running the same E1-PR-006 code state passed, indicating a wall-clock-dependent package difference rather than E1-PR-006 business behavior.

The volatile package field is `docProps/core.xml` `dcterms:modified`. The writer already canonicalized ZIP entry order and ZIP timestamps, but `openpyxl==3.1.5` updates the core modified property during every save.

## Correction

`src/re/adapters/excel_output/openpyxl_writer.py` now:

1. reads the stable `dcterms:modified` value from the exact source XLSX package;
2. performs the existing openpyxl write/save flow unchanged;
3. during deterministic package normalization, restores only the generated package's `dcterms:modified` text value to the source-derived value;
4. keeps the existing canonical ZIP member order/timestamps and all post-save structural/formula/source guards.

A fallback constant is used only if a package lacks the core modified property; it is package metadata only and is not exposed as appraisal evidence.

## Regression proof

`tests/re/test_workbook_output_package_determinism_hotfix.py` deliberately sleeps `1.2s` between two generations from the same source and identical payload, then requires:

- each artifact SHA equals its output file SHA;
- both artifact SHAs are equal;
- both generated files are byte-for-byte equal.

The binding Windows run passed this proof together with all existing writer/publication tests and the full RE regression suite.

## Preserved invariants

Unchanged:

- exact supported source SHA/fingerprint qualification;
- `.xlsx` and copy-on-write restrictions;
- explicit write allowlist and runtime formula protection;
- `localize-stale-phieu-tttt-e5` as the only declared E5 transformation;
- 33 C1–C11 write cells and explicit-zero semantics;
- Gate B.10 formula/consumer boundary;
- canonical final-snapshot binding/currentness behavior;
- create-if-absent publication and owned-temp cleanup;
- `WorkbookGenerated=true` with Excel qualification remaining `NOT_RUN`.

## Review status

Implementation is not self-accepted. Independent review must bind to the exact final review HEAD after evidence/handoff-only commits and removal of the one-time hotfix workflow.