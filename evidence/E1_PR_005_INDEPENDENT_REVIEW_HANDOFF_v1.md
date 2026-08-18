# E1-PR-005 — Independent Review Handoff v1

**Date:** 2026-08-18
**Repository:** `Reguluspt/CEN-Value-RE`
**PR:** #15
**Branch:** `agent/e1-pr-005-workbook-output-generation`
**Accepted base:** `f14018b19afcdb1cf600f46524e18f8ea2d3f4de`
**Runtime-tested implementation HEAD:** `0c3b693d272befde32da8f1521b4acf390fe592a`
**Binding Windows run:** `32089429684`
**Binding result:** full `245 passed in 4.77s`; focused `21 passed in 1.02s`
**Gate:** `WorkbookGenerationGate`
**Decision requested:** `ACCEPTED` / `RETURN FINDINGS`

## Exact review-head rule

Resolve PR #15 HEAD directly from GitHub immediately before review and bind the verdict to that exact SHA.

After runtime-tested HEAD `0c3b693d272befde32da8f1521b4acf390fe592a`, the final review HEAD may differ only by:

- binding runtime evidence;
- implementation report;
- this independent-review handoff;
- removal of `.github/workflows/e1-pr-005-verify.yml`;
- PR metadata/comments, which are not tree changes.

Any post-test source/test/dependency/profile/source-evidence/runtime-bearing change invalidates run `32089429684`.

## Review target

Review E1-PR-005 / `WorkbookGenerationGate` against the accepted Epic 1 plan and frozen Gate B/profile/fingerprint contracts.

### Source qualification / fail-closed behavior

Verify:

- source exemplar SHA is exact and profile-controlled;
- source and output paths are distinct `.xlsx` paths;
- source is never modified in place;
- an existing output is not silently overwritten;
- unsupported profile/source SHA/fingerprint/formula/external dependency fails closed;
- generated failure artifacts are cleaned up.

### Write authority

Verify:

- the historical mapping matrix is not itself write authority;
- the output profile contains an explicit allowlist;
- unknown cells are read-only by default;
- every runtime formula cell is protected, not only the smaller fingerprint-signature set;
- formula-backed legacy cells discovered in the actual N08 source are fixed/read-only compatibility prerequisites;
- only `Phieu TTTT!E5` may replace a formula, and only through the frozen `localize-stale-phieu-tttt-e5` transformation;
- all 33 direct C1-C11 rate cells remain writable and preserve explicit-zero semantics.

### Canonical application authority

Verify the application does not accept arbitrary caller cell/value pairs. Generation must consume current canonical evidence:

- active case and supported template profile;
- current E1-PR-004 final valuation;
- current subject/parcel/land compatibility data;
- exactly current TSSS01/02/03;
- current market observations and required typed characteristics;
- complete explicit CURRENT C1-C11 decisions.

The generated artifact must bind exact final-valuation snapshot ID + semantic SHA.

### Market factor semantics

Verify workbook transaction-success factor is derived from accepted canonical fractional negotiation rate:

```text
factor = 1 - negotiation_rate
```

Do not allow reverse-solving from negotiated-price output because the workbook rounds negotiated price.

Missing canonical negotiation rate must fail closed.

### Structural preservation

Verify post-save checks detect:

- formulas removed outside declared transformation;
- changed cells outside the write/compatibility allowlist;
- Gate B.10 consumer formula drift;
- source-byte mutation.

The generated package should produce deterministic SHA for identical tested source/payload.

### Gate B.10 boundary

Verify these formulas remain protected and distinct:

```text
Bangtinh!G181 = ROUND(G169 + G178, 0)
Bangtinh!G182 = ROUND(G181, -6)
Offical!E32   = Bangtinh!G181
```

E1-PR-005 must not collapse G181/G182 or rewrite `Offical!E32` to G182.

### Qualification boundary

Verify generation returns artifact SHA/report metadata but never claims Excel qualification PASS.

Expected generation state is:

```text
WorkbookGenerated = true
excel_qualification_status = NOT_RUN
```

Excel Desktop recalculation/qualification remains later scope.

## Direct N08 source evidence

The actual frozen workbook remains external to Git. Review:

`fixtures/N08_0038_OUTPUT_SOURCE_EVIDENCE_v1.json`

Expected source SHA:

`d410cfcc2263d7d50a436a79e192461f04b6863e6c3676a28da7a2eed287389c`

The fixture is a non-binary record of direct XLSX package/XML inspection of the Library exemplar and binds:

- direct writable cells;
- formula-backed read-only cells;
- all 33 direct C1-C11 cells;
- stale E5 transformation;
- market-normalization factor/formula distinction;
- Gate B.10 formulas.

Do not treat this fixture as Excel Desktop qualification evidence. The hosted binding run does not possess the external Library workbook bytes.

## Binding runtime evidence

Inspect GitHub Actions run `32089429684` directly.

Expected:

- Microsoft Windows Server 2025;
- Python `3.11.9`;
- pinned `openpyxl==3.1.5` in the concrete adapter runtime;
- diff hygiene PASS;
- compile PASS;
- full `tests/re`: `245 passed`;
- focused E1-PR-005: `21 passed`;
- checked-out merge-ref `9dc3c3f130c4bf1e16a7293b9bf60e7cd69adcff` tree `78d4a62e494875e954b604ef612f8edefe0eae6c` equals runtime HEAD `0c3b693d272befde32da8f1521b4acf390fe592a` tree exactly.

Earlier runs are superseded. In particular:

- `32089177377`: non-binding; one temp-file extension plumbing defect after 240 tests passed;
- `32089275861`: successful intermediate run but superseded by direct-source evidence/tests;
- `32089429684`: final binding run.

## Authority

Review against at least:

- `epic-1/EPIC_1_IMPLEMENTATION_PACKET_v1.md`;
- `epic-1/EPIC_1_PR_PLAN_v1.md`;
- `epic-1/EPIC_1_ACCEPTANCE_MATRIX_v1.md`;
- `epic-1/E1_PR_005_WORKBOOK_OUTPUT_CONTRACT_v1.md`;
- `gate-b/GATE_B10_OUTPUT_CONSUMER_CONTRACT_v1.md`;
- `gate-b/GATE_B14_DEPENDENCY_CLASSIFICATION_BASELINE.md`;
- accepted `ExcelTemplateProfile` / fingerprint / compatibility-transformation contracts;
- accepted E1-PR-001..004 contracts and currentness gates;
- Golden fixture/checkpoint manifest and direct adjustment-decision fixture;
- `fixtures/N08_0038_OUTPUT_SOURCE_EVIDENCE_v1.json`.

Brainstorm History remains provenance/design intent and does not override later frozen closure.

## Explicit non-scope

Do not block E1-PR-005 merely because it does not implement:

- Microsoft Excel Desktop qualification PASS;
- E1-PR-006 Astryx manual workbench integration;
- E1-PR-007 end-to-end/reference Excel qualification;
- approval return/revision;
- CTXD calculation engine;
- OCR/Maps;
- Historical Learning;
- Epic 1 closure.

## Required verdict

Return only `ACCEPTED` or `RETURN FINDINGS`.

If accepted, bind acceptance to the exact resolved PR HEAD and `WorkbookGenerationGate`. Acceptance does not close Epic 1. E1-PR-006 may begin only from the accepted merge commit after expected-head protected merge.

If findings remain, do not fix code or merge. Report precise issue, violated invariant, concrete failure mode, evidence/reproduction, minimum corrective requirement, and acceptance condition.