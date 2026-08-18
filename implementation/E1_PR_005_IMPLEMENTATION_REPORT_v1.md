# E1-PR-005 — Implementation Report v1

**Date:** 2026-08-18  
**Repository:** `Reguluspt/CEN-Value-RE`  
**Accepted base:** `f14018b19afcdb1cf600f46524e18f8ea2d3f4de`  
**Runtime-tested implementation HEAD:** `0c3b693d272befde32da8f1521b4acf390fe592a`  
**Binding Windows run:** `32089429684`  
**Gate:** `WorkbookGenerationGate`

## Outcome

E1-PR-005 implements the bounded Epic 1 supported-profile workbook generation slice for `cenvalue-re-n08-0038-v1@1`.

Excel remains an output/compatibility surface. CenValue canonical application/domain state remains authority. The implementation does not claim Excel Desktop qualification or Epic 1 closure.

## Output architecture

A new framework-independent boundary in `src/re/ports/workbook_output.py` exposes generation without leaking workbook runtime dependencies into the core layers.

The concrete writer lives in `src/re/adapters/excel_output/` and uses pinned `openpyxl==3.1.5`. Architecture tests explicitly prevent `openpyxl` or concrete adapter imports from domain/application/ports.

The existing `src/re/adapters/excel/` profile/fingerprint package remains the pure structural contract and is reused rather than redesigned.

## Supported-profile write contract

`WorkbookOutputProfile` adds a second, explicit layer above `ExcelTemplateProfile`:

- exact source exemplar SHA;
- exact writable cells;
- read-only fixed source bindings;
- accepted compatibility transformations;
- frozen output-consumer formulas.

No write permission is inferred from the historical mapping matrix.

The N08 profile writes only direct canonical subject/TSSS inputs, all 33 direct C1-C11 human decision cells, and `Phieu TTTT!E5` through its already accepted locality compatibility transformation.

Direct source inspection exposed several historical `input_or_derived` cells that are formulas in the actual exemplar. These are explicitly not writable. Every runtime formula cell is dynamically protected even when it is not one of the smaller frozen fingerprint-signature set.

## Canonical application payload

`WorkbookOutputService` accepts only:

- case ID;
- source/template path;
- new output path.

It obtains current evidence from persistence and the accepted upstream gates:

- active case/profile;
- current E1-PR-004 final valuation;
- current subject and parcel;
- supported land components;
- exactly TSSS01/TSSS02/TSSS03;
- current market observations;
- required typed characteristics;
- complete explicit CURRENT C1-C11 decisions.

The writer therefore never receives an arbitrary caller-controlled cell/value map from the application API.

The artifact binds the exact current final-valuation snapshot ID and semantic SHA.

## Market normalization export

The frozen workbook stores transaction-success factor (`0.85`) while the accepted canonical model stores fractional negotiation rate (`0.15`). E1-PR-005 uses:

```text
transaction_success_factor = 1 - canonical_negotiation_rate
```

The implementation deliberately rejects a missing canonical rate rather than reverse-solving from the rounded negotiated-price workbook result.

## Copy-on-write / fail-closed behavior

The writer:

1. requires source/output `.xlsx` paths;
2. refuses in-place editing;
3. refuses an already existing output;
4. verifies source SHA;
5. verifies accepted profile/fingerprint and external-link state;
6. validates read-only fixed source compatibility values;
7. verifies frozen G181/G182/`Offical!E32` consumer formulas;
8. scans all actual source formula cells and blocks normal writes to them;
9. applies only declared writes/transformation;
10. saves to a valid temporary `.xlsx`;
11. normalizes XLSX package entry ordering/timestamps for deterministic bytes;
12. reopens and re-verifies the generated workbook;
13. confirms original formulas remain except declared transformation targets;
14. confirms changed cells are a subset of the explicit allowlist;
15. rechecks source SHA unchanged;
16. atomically moves the completed artifact into the requested new output path.

Failures clean up the incomplete output.

## Artifact evidence

Successful generation returns:

- profile ID/version;
- source/output paths;
- source SHA;
- output SHA;
- exact final-valuation source binding;
- generation timestamp;
- changed cells;
- applied compatibility transformations;
- `WorkbookGenerated=true`;
- `excel_qualification_status=NOT_RUN`.

The artifact type explicitly refuses a `PASS` Excel qualification claim from this generation boundary.

## Direct source evidence

The real N08 workbook remains external to Git and is bound by SHA:

`d410cfcc2263d7d50a436a79e192461f04b6863e6c3676a28da7a2eed287389c`

Direct XLSX package/XML inspection of the Library source is recorded without workbook bytes in:

`fixtures/N08_0038_OUTPUT_SOURCE_EVIDENCE_v1.json`

Tests bind the N08 output profile to this evidence: direct writable cells, formula-backed read-only cells, 33 rate decisions, stale E5 transformation, market-factor semantics, and Gate B.10 consumers.

## Gate B.10 preservation

E1-PR-005 does not write output consumer cells. It preserves:

```text
G181 = ROUND(G169 + G178, 0)
G182 = ROUND(G181, -6)
Offical!E32 = Bangtinh!G181
```

The pre-rounded and final-rounded values therefore remain separate.

## Verification

Binding Windows run `32089429684` on implementation HEAD `0c3b693d272befde32da8f1521b4acf390fe592a`:

- Microsoft Windows Server 2025 / Python 3.11.9;
- diff hygiene: PASS;
- compile: PASS;
- full `tests/re`: **245 passed in 4.77s**;
- focused E1-PR-005: **21 passed in 1.02s**;
- tested merge-ref `9dc3c3f130c4bf1e16a7293b9bf60e7cd69adcff` tree `78d4a62e494875e954b604ef612f8edefe0eae6c` exactly equals the runtime-tested branch HEAD tree.

## Explicit non-scope

No claim is made for Microsoft Excel Desktop recalculation/qualification, E1-PR-006 workbench integration, E1-PR-007 end-to-end qualification, approval return/revision, generic template rewriting, CTXD engine, OCR/Maps, Historical Learning, or Epic 1 closure.

The implementer does not self-issue acceptance. E1-PR-006 must not begin until an independent reviewer accepts the exact final E1-PR-005 review HEAD and PR #15 is merged using expected-head protection.
