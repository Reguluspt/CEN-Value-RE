# E1-PR-005 — Runtime Evidence v1

**Date:** 2026-08-18  
**Repository:** `Reguluspt/CEN-Value-RE`  
**PR:** #15  
**Accepted base:** `f14018b19afcdb1cf600f46524e18f8ea2d3f4de`  
**Runtime-tested implementation HEAD:** `0c3b693d272befde32da8f1521b4acf390fe592a`  
**Binding GitHub Actions run:** `32089429684`  
**Gate:** `WorkbookGenerationGate`

## 1. Binding environment and result

Run `32089429684` completed SUCCESS on Microsoft Windows Server 2025 with CPython `3.11.9`.

- dependency install: PASS;
- `openpyxl==3.1.5` installed from pinned `requirements-re.txt` only for the concrete workbook-output adapter/test runtime;
- `git diff --check f14018b19afcdb1cf600f46524e18f8ea2d3f4de..HEAD`: PASS;
- `python -m compileall -q src/re`: PASS;
- full `tests/re`: **245 passed in 4.77s**;
- focused E1-PR-005 suite: **21 passed in 1.02s**.

GitHub Actions checked out PR merge-ref `9dc3c3f130c4bf1e16a7293b9bf60e7cd69adcff`. Its tree SHA is `78d4a62e494875e954b604ef612f8edefe0eae6c`, exactly equal to runtime-tested branch HEAD `0c3b693d272befde32da8f1521b4acf390fe592a` tree SHA `78d4a62e494875e954b604ef612f8edefe0eae6c`.

## 2. Capability evidence

The binding run covers:

- explicit N08 workbook-output profile/write allowlist;
- no write permission inferred from historical mapping labels;
- copy-on-write generation with source/output path separation;
- refusal to overwrite an existing output path;
- exact supported source-exemplar SHA contract;
- pre-write structural/fingerprint/external-link qualification;
- every source formula cell dynamically read-only unless an accepted compatibility transformation explicitly targets it;
- `Phieu TTTT!E5` localization only through `localize-stale-phieu-tttt-e5`;
- fixed/formula-backed legacy source cells treated as read-only compatibility prerequisites;
- unexpected cell changes outside the explicit write/compatibility allowlist fail closed;
- formula preservation outside declared compatibility transformations;
- Gate B.10 consumer formulas preserved for G181/G182/`Offical!E32`;
- source bytes verified unchanged after generation;
- deterministic generated package SHA for identical tested source/payload;
- generated artifact records exact source/output SHA and current final-valuation snapshot ID/hash;
- `WorkbookGenerated=true` while Excel qualification remains `NOT_RUN`;
- application accepts only case/file paths and builds the writer payload from canonical persisted case/final/TSSS/C1-C11 evidence rather than arbitrary caller cell maps;
- complete CURRENT explicit C1-C11 decisions required for all three comparables;
- transaction-success factor derived as `1 - canonical fractional negotiation rate`, never reverse-solved from rounded negotiated-price output;
- architecture guard prevents `openpyxl`/adapter imports from domain/application/ports.

## 3. Direct N08 source evidence

The actual frozen N08 workbook remains external to Git. Its accepted SHA-256 is:

`d410cfcc2263d7d50a436a79e192461f04b6863e6c3676a28da7a2eed287389c`

Before final binding, the source XLSX package/XML was inspected directly from the project Library. The resulting non-binary evidence is committed as:

`fixtures/N08_0038_OUTPUT_SOURCE_EVIDENCE_v1.json`

The focused binding suite verifies the output profile against that evidence, including:

- direct writable subject/TSSS cells;
- formula-backed cells that must remain read-only;
- all 33 direct C1-C11 decision cells;
- the known stale `Phieu TTTT!E5` compatibility formula/transformation;
- Gate B.10 G181/G182/`Offical!E32` formulas;
- market-normalization direct factor inputs versus formula-backed negotiated-price outputs.

The hosted GitHub runner does **not** possess the external Library workbook bytes, so this run does not claim Microsoft Excel/reference-workbook qualification. Concrete writer behavior is exercised against structurally representative supported-profile test workbooks, while direct reference-source classifications are separately SHA-bound by the source-evidence fixture.

## 4. Gate B.10 output-consumer boundary

E1-PR-005 preserves the frozen consumer formulas and does not overwrite them:

```text
Bangtinh!G181 = ROUND(G169 + G178, 0)
Bangtinh!G182 = ROUND(G181, -6)
Offical!E32   = Bangtinh!G181
```

Therefore `total_value_before_rounding_vnd` and `final_appraised_value_vnd` remain distinct, and `Offical!E32` continues to consume G181 rather than G182.

## 5. Run history / supersession

- `32089177377`: non-binding. Dependency install, diff hygiene and compile passed; full suite reached **240 passed / 1 failed**. The single defect was temp output naming as `generated.xlsx.tmp`, which `openpyxl` correctly rejected because `.tmp` is not a supported workbook extension. The writer was corrected to use `generated.tmp.xlsx`.
- `32089275861`: successful intermediate run, **241 passed / 17 focused passed**, but superseded because direct N08 source-evidence fixture/tests were added afterward.
- Any other auto-triggered intermediate E1-PR-005 runs are superseded by the final implementation state.
- `32089429684`: **binding final implementation run**, **245/245 full** and **21/21 focused PASS**.

Only run `32089429684` binds the final E1-PR-005 implementation behavior.

## 6. Claim boundary

This evidence supports only E1-PR-005 / `WorkbookGenerationGate`.

It does **not** claim:

- Microsoft Excel Desktop recalculation or Excel qualification PASS;
- E1-PR-006 Astryx manual workbench integration;
- E1-PR-007 end-to-end/reference Excel qualification;
- approval return/revision import;
- generic external-link repair;
- generic template-family formula rewriting;
- Epic 2 CTXD calculation engine;
- OCR/Maps;
- Historical Learning;
- Epic 1 closure.

## 7. Post-test binding rule

After runtime-tested HEAD `0c3b693d272befde32da8f1521b4acf390fe592a`, only this runtime evidence, the implementation report, the independent-review handoff, and removal of `.github/workflows/e1-pr-005-verify.yml` may be present before independent review.

Any post-test change to source, tests, dependency pins, workbook-output contract/profile, source-evidence fixture, persistence/currentness behavior, formula/write semantics, or runtime-bearing configuration invalidates run `32089429684` and requires a new full Windows run.
