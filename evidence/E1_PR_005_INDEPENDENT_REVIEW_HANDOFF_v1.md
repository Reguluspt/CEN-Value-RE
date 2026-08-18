# E1-PR-005 — Corrective Independent Re-Review Handoff v1

**Date:** 2026-08-18
**Repository:** `Reguluspt/CEN-Value-RE`
**PR:** #15
**Branch:** `agent/e1-pr-005-workbook-output-generation`
**Accepted base:** `f14018b19afcdb1cf600f46524e18f8ea2d3f4de`
**Original reviewed HEAD:** `87069ec05a11d5bbc98656def46c16aaecba6f1f`
**Corrective runtime-tested HEAD:** `3455c2353fbe8d0ef6ffab5adad91c9f88a85a9d`
**Binding Windows run:** `32107305776`
**Binding result:** full `249 passed in 6.08s`; focused `25 passed in 1.56s`
**Gate:** `WorkbookGenerationGate`
**Decision requested:** `ACCEPTED` / `RETURN FINDINGS`

## Exact review-head rule

Resolve PR #15 HEAD directly from GitHub immediately before re-review and bind the verdict to that exact SHA.

After corrective runtime-tested HEAD `3455c2353fbe8d0ef6ffab5adad91c9f88a85a9d`, the final review HEAD may differ only by:

- updated binding runtime evidence;
- updated implementation report;
- this corrective re-review handoff;
- removal of `.github/workflows/e1-pr-005-corrective-verify.yml`;
- PR metadata/comments, which are not tree changes.

Any post-test source/test/dependency/profile/source-evidence/currentness/publication/runtime-bearing change invalidates run `32107305776`.

## Targeted corrective scope

Do not redo discovery/design. The original independent review accepted all other workbook-generation boundaries and returned two HIGH findings only:

- `E1PR005-IR-001` — canonical workbook payload could drift away from the final-valuation snapshot it claimed to bind;
- `E1PR005-IR-002` — final output publication could overwrite/delete a foreign destination and leak a partial temp under failure/race conditions.

The corrective implementation addresses these two findings. Independent re-review is required to decide whether they are CLOSED. Verify no regression to the previously accepted write/profile/formula/Gate B.10/qualification semantics.

## E1PR005-IR-001 corrective behavior to verify

`WorkbookOutputService.generate()` now follows:

1. authoritative current final-valuation resolve;
2. one `WorkbookOutputUnitOfWork.atomic()` payload-freeze transaction;
3. freeze case/profile, subject/parcel/land compatibility inputs, exactly TSSS01–03, current observations/characteristics, and all explicit CURRENT C1–C11 decisions;
4. release the payload transaction;
5. authoritative current final-valuation resolve again;
6. require the exact same final snapshot ID and semantic SHA;
7. invoke the writer only after successful revalidation.

The SQLCipher UoW uses `BEGIN IMMEDIATE`. The accepted E1-PR-004 resolver itself was not altered, so nested transactions are not introduced.

Acceptance proof to inspect:

`tests/re/test_workbook_output_service.py`

A deterministic test changes a C1 decision after the initial final resolve and before payload completion. Expected result:

- second authoritative final resolution fails;
- generation rejects;
- `WorkbookOutputWriter.generate()` is not called.

Normal path must still bind the exact final snapshot ID/SHA.

## E1PR005-IR-002 corrective behavior to verify

`OpenPyxlWorkbookOutputWriter` now:

- allocates a unique attempt-owned temp `.tmp.xlsx` in the output directory;
- covers `Workbook.save`, package normalization, reopen/verification and publication with owned-temp cleanup;
- publishes via `os.link(temp, output)` rather than `os.replace`, so an already-created destination is not replaced;
- never blindly unlinks an unproven destination;
- uses `os.path.samefile()` before any exceptional cleanup of a published output;
- cleans normalization staging and partial save temps.

Acceptance proof to inspect:

`tests/re/test_workbook_output_publication_corrective.py`

Required Windows-proven vectors:

1. foreign sentinel appears after initial output validation and before publication: generation rejects and sentinel remains byte-for-byte;
2. two competing attempts target the same output: exactly one succeeds, the other rejects, winner remains intact, no temp leak;
3. injected `Workbook.save()` failure after owned temp creation: owned partial temp is removed and foreign destination is not deleted.

## Preserved accepted behavior

Verify corrective changes do not weaken:

- exact N08 source SHA/profile qualification;
- explicit write allowlist; historical mapping labels remain non-authoritative;
- all runtime formula cells read-only except frozen `Phieu TTTT!E5` transformation;
- 33 direct C1–C11 cells and explicit-zero semantics;
- canonical transaction factor `1 - negotiation_rate`, no reverse-solving;
- G181/G182/`Offical!E32` Gate B.10 formulas;
- source workbook never edited in place;
- deterministic package SHA for identical tested source/payload;
- artifact binding to exact final valuation snapshot ID/SHA;
- `WorkbookGenerated=true`, `excel_qualification_status=NOT_RUN`;
- architecture guard against `openpyxl`/adapter imports in domain/application/ports.

## Direct N08 source evidence

External workbook SHA remains:

`d410cfcc2263d7d50a436a79e192461f04b6863e6c3676a28da7a2eed287389c`

`fixtures/N08_0038_OUTPUT_SOURCE_EVIDENCE_v1.json` is unchanged by the corrective loop. Do not treat the fixture or hosted run as Microsoft Excel Desktop qualification.

## Binding runtime evidence

Inspect GitHub Actions run `32107305776` directly.

Expected:

- Microsoft Windows Server 2025;
- Python `3.11.9`;
- diff hygiene PASS;
- compile PASS;
- full `tests/re`: `249 passed`;
- focused corrective suite: `25 passed`;
- tested merge-ref `1386a3e34503b6f7a0f4c0c7afcebccd6e047955` tree `a1a2a03c9ac148b7f145261a500b8407b84b4a1e` equals corrective runtime HEAD `3455c2353fbe8d0ef6ffab5adad91c9f88a85a9d` tree exactly.

Superseded evidence:

- `32089429684`: original pre-corrective binding run;
- `32107120120`: non-binding corrective attempt that stopped at Markdown diff hygiene before compile/tests.

Only `32107305776` binds the corrective implementation.

## Authority

Review against at least:

- `epic-1/EPIC_1_IMPLEMENTATION_PACKET_v1.md`;
- `epic-1/EPIC_1_PR_PLAN_v1.md`;
- `epic-1/EPIC_1_ACCEPTANCE_MATRIX_v1.md`;
- `epic-1/E1_PR_005_WORKBOOK_OUTPUT_CONTRACT_v1.md`;
- `gate-b/GATE_B10_OUTPUT_CONSUMER_CONTRACT_v1.md`;
- `gate-b/GATE_B14_DEPENDENCY_CLASSIFICATION_BASELINE.md`;
- accepted Excel profile/fingerprint/compatibility-transformation contracts;
- accepted E1-PR-001..004 currentness contracts;
- `fixtures/N08_0038_OUTPUT_SOURCE_EVIDENCE_v1.json`.

Brainstorm History remains provenance/design intent only where later frozen authority does not supersede it.

## Explicit non-scope

Do not block this corrective re-review merely because it does not implement Microsoft Excel Desktop qualification PASS, E1-PR-006 workbench integration, E1-PR-007 E2E qualification, approval return/revision, CTXD engine, OCR/Maps, Historical Learning, or Epic 1 closure.

## Required verdict

Return only `ACCEPTED` or `RETURN FINDINGS`.

If accepted, bind acceptance to the exact resolved PR HEAD and `WorkbookGenerationGate`, explicitly close `E1PR005-IR-001` and `E1PR005-IR-002`, and confirm acceptance does not equal Excel qualification or Epic 1 closure.

If findings remain, do not modify code or merge. Report exact issue, violated invariant, concrete failure mode, reproduction/evidence, minimum corrective requirement and acceptance condition.