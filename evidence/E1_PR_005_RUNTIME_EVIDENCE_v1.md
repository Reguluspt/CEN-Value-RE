# E1-PR-005 — Runtime Evidence v1

**Date:** 2026-08-18
**Repository:** `Reguluspt/CEN-Value-RE`
**PR:** #15
**Accepted base:** `f14018b19afcdb1cf600f46524e18f8ea2d3f4de`
**Original reviewed HEAD:** `87069ec05a11d5bbc98656def46c16aaecba6f1f`
**Corrective runtime-tested HEAD:** `3455c2353fbe8d0ef6ffab5adad91c9f88a85a9d`
**Binding GitHub Actions run:** `32107305776`
**Gate:** `WorkbookGenerationGate`

## 1. Binding environment and result

Run `32107305776` completed SUCCESS on Microsoft Windows Server 2025 with CPython `3.11.9`.

- dependency install: PASS;
- `openpyxl==3.1.5` installed from pinned `requirements-re.txt`;
- `git diff --check f14018b19afcdb1cf600f46524e18f8ea2d3f4de..HEAD`: PASS;
- `python -m compileall -q src/re`: PASS;
- full `tests/re`: **249 passed in 6.08s**;
- focused E1-PR-005 corrective suite: **25 passed in 1.56s**.

GitHub Actions checked out PR merge-ref `1386a3e34503b6f7a0f4c0c7afcebccd6e047955`. Its tree SHA is `a1a2a03c9ac148b7f145261a500b8407b84b4a1e`, exactly equal to corrective runtime-tested HEAD `3455c2353fbe8d0ef6ffab5adad91c9f88a85a9d` tree SHA `a1a2a03c9ac148b7f145261a500b8407b84b4a1e`.

## 2. Corrective finding evidence

### E1PR005-IR-001 — coherent canonical payload binding

Corrective orchestration now uses three phases:

1. resolve the authoritative current final-valuation snapshot;
2. freeze all canonical workbook payload reads under one `WorkbookOutputUnitOfWork.atomic()` boundary (`BEGIN IMMEDIATE` in SQLCipher);
3. after releasing the payload-freeze transaction, authoritatively resolve the current final valuation again and require the exact same snapshot ID and semantic SHA before any writer I/O begins.

The frozen payload includes case/profile, current subject/parcel/land compatibility data, exactly TSSS01–03, current observations/typed characteristics, and complete explicit CURRENT C1–C11 decisions.

A deterministic regression test mutates a C1 decision after initial final resolution and before payload freeze completes. The second authoritative resolution rejects the drift and the writer is not called.

### E1PR005-IR-002 — race-safe artifact publication

Corrective writer publication now:

- creates a unique attempt-owned temporary `.tmp.xlsx` in the destination directory;
- covers save, package normalization, reopening, verification and publication with owned-temp cleanup;
- publishes with `os.link(temporary, output)`, which creates the destination only if absent and does not replace an existing destination;
- never blindly unlinks `output_path` on failure;
- only removes a published destination during exceptional cleanup when `os.path.samefile()` proves it is the same attempt-owned file;
- cleans package-normalization staging files and partial save temp files.

Windows focused tests prove the three reviewer-requested vectors:

1. a foreign destination sentinel created after initial validation but before publication remains byte-for-byte unchanged and generation rejects;
2. two attempts racing for the same output yield exactly one success and one rejection, with the winner artifact intact and no temp leakage;
3. an injected `Workbook.save()` failure after temp creation removes the owned partial temp while preserving a foreign destination.

## 3. Preserved accepted behavior

The corrective loop does not change the previously accepted workbook semantics:

- explicit N08 profile/write allowlist;
- no write authority inferred from historical mapping labels;
- exact external source SHA binding;
- all runtime source formulas read-only except declared `Phieu TTTT!E5` compatibility transformation;
- 33 direct C1–C11 decision cells with explicit-zero semantics;
- transaction-success factor derived as `1 - canonical negotiation_rate`;
- G181/G182/`Offical!E32` consumer formulas preserved;
- source workbook not edited in place;
- deterministic generated package bytes for identical tested source/payload;
- artifact binds exact final-valuation snapshot ID/SHA;
- `WorkbookGenerated=true` with `excel_qualification_status=NOT_RUN`;
- architecture guard keeps `openpyxl` and concrete Excel-output adapter out of domain/application/ports.

## 4. Direct N08 source evidence

The frozen N08 workbook remains external to Git and is identified by SHA-256:

`d410cfcc2263d7d50a436a79e192461f04b6863e6c3676a28da7a2eed287389c`

`fixtures/N08_0038_OUTPUT_SOURCE_EVIDENCE_v1.json` remains unchanged and binds the direct writable/formula-backed classifications, all 33 C1–C11 source cells, E5 transformation, market-normalization distinction and Gate B.10 formulas.

This hosted run does not claim Microsoft Excel Desktop/reference-workbook qualification.

## 5. Run history / supersession

- `32089429684`: original pre-review binding run, **245/245 full** and **21/21 focused**, superseded by corrective source/test changes.
- `32107120120`: corrective attempt, non-binding; stopped at diff hygiene because historical Markdown evidence contained trailing whitespace, before compile/tests.
- `32107305776`: **binding corrective run**, **249/249 full** and **25/25 focused PASS**.

Only run `32107305776` binds the corrective implementation behavior.

## 6. Claim boundary

This evidence supports only E1-PR-005 / `WorkbookGenerationGate`. It does not claim Microsoft Excel Desktop qualification, E1-PR-006 integration, E1-PR-007 E2E qualification, approval return/revision, CTXD engine, OCR/Maps, Historical Learning, or Epic 1 closure.

## 7. Post-test binding rule

After corrective runtime-tested HEAD `3455c2353fbe8d0ef6ffab5adad91c9f88a85a9d`, only this runtime-evidence update, the implementation-report update, the independent-review-handoff update, and removal of `.github/workflows/e1-pr-005-corrective-verify.yml` may occur before independent re-review.

Any post-test source, test, dependency, profile, source-evidence, persistence/currentness, formula/write, publication or runtime-bearing change invalidates run `32107305776` and requires a new full Windows run.