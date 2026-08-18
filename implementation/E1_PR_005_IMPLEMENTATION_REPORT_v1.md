# E1-PR-005 — Implementation Report v1

**Date:** 2026-08-18
**Repository:** `Reguluspt/CEN-Value-RE`
**Accepted base:** `f14018b19afcdb1cf600f46524e18f8ea2d3f4de`
**Original reviewed HEAD:** `87069ec05a11d5bbc98656def46c16aaecba6f1f`
**Corrective runtime-tested HEAD:** `3455c2353fbe8d0ef6ffab5adad91c9f88a85a9d`
**Binding Windows run:** `32107305776`
**Gate:** `WorkbookGenerationGate`

## Outcome

E1-PR-005 implements the bounded supported-profile workbook generation slice for `cenvalue-re-n08-0038-v1@1`. The targeted corrective loop addresses the two independent-review findings without redesigning the already accepted profile, formula, Gate B.10 or qualification boundaries.

Excel remains an output/compatibility surface. CenValue canonical state remains calculation authority. No Microsoft Excel Desktop qualification or Epic 1 closure is claimed.

## Corrective response — IR-001 coherent payload provenance

The original application flow could resolve a current final valuation and then build the workbook payload after that resolver transaction ended. A concurrent canonical change could therefore make the final snapshot stale while later reads supplied newer payload values.

The corrected `WorkbookOutputService.generate()` now:

1. resolves the authoritative current final valuation;
2. freezes all workbook payload inputs under one `WorkbookOutputUnitOfWork.atomic()` transaction;
3. freezes the case profile and final snapshot source binding with that payload;
4. releases the database transaction before slow workbook I/O;
5. resolves the authoritative current final valuation again;
6. requires the exact same final snapshot ID and semantic SHA;
7. calls the writer only after that revalidation succeeds.

The SQLCipher implementation uses `BEGIN IMMEDIATE` for the payload-freeze transaction. The accepted E1-PR-004 resolver remains unchanged, avoiding nested persistence transactions.

A deterministic regression mutates a C1 decision after the initial resolve and before payload completion. The authoritative second resolve rejects the stale final evidence and the writer receives no call.

## Corrective response — IR-002 race-safe publication ownership

The original writer used an early `output.exists()` check followed by deterministic temp naming and final `os.replace()`. That could overwrite a destination created after the pre-check, and generic exception cleanup could remove a foreign destination.

The corrected writer:

- creates a unique attempt-owned `.tmp.xlsx` using `tempfile.mkstemp()` in the destination directory;
- places save, normalization, reopen, structural verification and publication in a cleanup scope covering the owned temp;
- publishes with `os.link(temporary, output)`, giving create-if-absent semantics instead of replacement semantics;
- treats an occupied destination at publication time as a fail-closed conflict;
- never blindly deletes `output_path` on failure;
- only removes an output during exceptional post-publication cleanup when `os.path.samefile()` proves it is the same attempt-owned file;
- removes normalization staging and partial save temp files.

Windows regression tests prove:

- a destination sentinel created after initial validation is not overwritten or deleted;
- two competing attempts for one output produce at most one success;
- an injected `Workbook.save()` failure cleans the owned partial temp without deleting a foreign destination.

## Preserved workbook contract

The corrective loop preserves the original E1-PR-005 contract:

- explicit `WorkbookOutputProfile` write allowlist;
- no write authority inferred from historical mapping labels;
- exact N08 source-exemplar SHA;
- all runtime formula cells protected except the accepted `Phieu TTTT!E5` compatibility transformation;
- all 33 direct C1–C11 human decision cells writable with explicit-zero semantics;
- canonical market factor `1 - negotiation_rate`, never reverse-solved from rounded negotiated output;
- protected G181/G182/`Offical!E32` consumer formulas;
- source workbook never edited in place;
- deterministic generated package bytes for identical tested source/payload;
- generated artifact binds exact final-valuation snapshot ID/SHA;
- `WorkbookGenerated=true` and `excel_qualification_status=NOT_RUN`;
- `openpyxl==3.1.5` remains confined to the concrete adapter/runtime boundary.

## Direct N08 source evidence

The external reference workbook remains outside Git and is identified by:

`d410cfcc2263d7d50a436a79e192461f04b6863e6c3676a28da7a2eed287389c`

`fixtures/N08_0038_OUTPUT_SOURCE_EVIDENCE_v1.json` is unchanged by the corrective loop.

## Verification

Binding Windows run `32107305776` on corrective runtime-tested HEAD `3455c2353fbe8d0ef6ffab5adad91c9f88a85a9d`:

- Microsoft Windows Server 2025 / Python 3.11.9;
- dependency install: PASS;
- diff hygiene: PASS;
- compile: PASS;
- full `tests/re`: **249 passed in 6.08s**;
- focused E1-PR-005 corrective suite: **25 passed in 1.56s**;
- tested merge-ref `1386a3e34503b6f7a0f4c0c7afcebccd6e047955` tree `a1a2a03c9ac148b7f145261a500b8407b84b4a1e` exactly equals the corrective runtime-tested HEAD tree.

Run `32089429684` is superseded by corrective source/test changes. Corrective attempt `32107120120` stopped at diff hygiene before compile/tests because historical Markdown evidence contained trailing whitespace and is non-binding.

## Explicit non-scope

No claim is made for Microsoft Excel Desktop recalculation/qualification, E1-PR-006 workbench integration, E1-PR-007 end-to-end qualification, approval return/revision, CTXD engine, OCR/Maps, Historical Learning or Epic 1 closure.

The implementer does not self-issue acceptance. PR #15 must not merge and E1-PR-006 must not begin until independent re-review accepts the exact corrective review HEAD.