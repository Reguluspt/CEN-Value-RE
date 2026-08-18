# E1-PR-005 — Supported-Profile Workbook Output Generation Contract v1

**Status:** IMPLEMENTATION CONTRACT — EPIC 1
**Baseline:** `f14018b19afcdb1cf600f46524e18f8ea2d3f4de`
**Gate:** `WorkbookGenerationGate`

## 1. Purpose and authority

E1-PR-005 generates a **new** workbook artifact from the accepted Epic 1 canonical Walking Skeleton state. Excel remains a compatibility/output surface; CenValue domain/application state remains calculation authority.

This PR consumes the accepted E1-PR-004 current final valuation and preserves all Epic 0/E1-PR-001..004 guards. Historical workbook mapping documents are provenance only where later profile/fingerprint/Gate B closure gives a stronger contract.

Supported output profile in this slice:

`cenvalue-re-n08-0038-v1@1`

The external N08 exemplar is identified by exact SHA-256:

`d410cfcc2263d7d50a436a79e192461f04b6863e6c3676a28da7a2eed287389c`

The source workbook remains external to Git and is never edited in place.

## 2. Writer architecture

Workbook runtime I/O lives in a dedicated adapter package separate from the existing pure profile/fingerprint package.

Application code depends only on `WorkbookOutputWriter` / `WorkbookOutputUnitOfWork` ports. It does not import `openpyxl` or the concrete Excel adapter.

The concrete writer is allowed to depend on the pinned workbook runtime dependency only inside the adapter boundary.

## 3. Fail-closed source qualification

Before writing anything, generation must verify:

- source path exists and is `.xlsx`;
- output path is distinct and does not already exist;
- source SHA-256 equals the profile exemplar SHA;
- structural fingerprint matches the accepted `ExcelTemplateProfile`;
- required sheet names/states are intact;
- accepted formula signatures are intact;
- external-link state is allowed by the profile;
- Gate B.10 output-consumer formulas are intact.

Unsupported profile, source-hash mismatch, structural drift, formula drift or unknown external dependency fails closed.

## 4. Explicit write allowlist

No write permission is inferred from the historical mapping matrix, from a non-empty cell, or from a cell that merely looks editable.

`WorkbookOutputProfile` declares the exact writable cells. All other cells are read-only by default.

Every source cell that contains a formula at runtime is read-only unless it is the target of an explicitly declared `CompatibilityTransformation`.

E1-PR-005 writes only:

- supported canonical subject input cells that are direct values in the frozen exemplar;
- supported canonical TSSS input cells that are direct values in the frozen exemplar;
- the 33 direct C1–C11 human-selected rate cells at `Bangtinh!F/G/H` rows `55,60,...,105`;
- `Phieu TTTT!E5` only through the already frozen `localize-stale-phieu-tttt-e5` compatibility transformation.

Formula-backed legacy cells are never silently converted to literals.

## 5. Fixed source compatibility bindings

Direct inspection of the frozen exemplar proves that some historically mapped fields are formula-backed or hard-coded formula state. Gate B did not authorize rewriting those formulas.

For the Walking Skeleton these fields are therefore **read-only compatibility prerequisites**. Current canonical values must match the source workbook cached value within a narrow numeric tolerance, otherwise generation fails closed.

This includes the N08 exemplar's fixed/formula-backed total/depth/control and comparable detail cells needed by the Walking Skeleton.

This bounded behavior is intentional: E1-PR-005 proves safe output generation for the supported exemplar; it does not generalize or redesign the workbook formula graph.

## 6. Market normalization input semantics

The workbook stores transaction-success factor (for example `0.85`) while the accepted E1-PR-001 model stores the canonical fractional negotiation rate (for example `0.15`).

Generation uses:

```text
transaction_success_factor = 1 - canonical_negotiation_rate
```

It must **not** reverse-solve the factor from rounded negotiated-price output.

A missing canonical negotiation rate therefore fails closed for E1-PR-005.

## 7. Canonical freshness

Application generation requires:

- current non-archived case with supported profile binding;
- current E1-PR-004 final valuation resolved through the accepted freshness gate;
- current subject/parcel/land state compatible with the supported output profile;
- exactly current TSSS01/02/03;
- current market observation data;
- required typed comparison characteristics;
- complete explicit CURRENT C1–C11 decisions for each comparable.

Caller supplies only case identity and file paths. Caller does **not** supply arbitrary workbook cell/value pairs.

The generated artifact binds the exact current final-valuation snapshot ID and semantic SHA.

## 8. Copy-on-write and structural non-regression

Generation writes to a temporary/new output path and never mutates source bytes.

After save, the adapter reopens the generated workbook and verifies:

- structural fingerprint remains supported;
- output-consumer formulas remain intact;
- source formulas have not disappeared outside declared transformations;
- changed cell values are a subset of the explicit write/compatibility allowlist;
- source workbook SHA is unchanged.

Any unexpected cell change fails closed and removes the failed output artifact.

## 9. Artifact evidence

A successful generation returns at least:

- profile ID/version;
- source and output paths;
- source SHA-256;
- generated artifact SHA-256;
- exact final-valuation snapshot ID/hash binding;
- generation timestamp;
- changed-cell allowlist evidence;
- applied compatibility transformations;
- `WorkbookGenerated = true`;
- Excel qualification status `NOT_RUN`.

Generation may never self-claim Excel qualification `PASS`.

## 10. Gate B.10 consumer boundary

The writer does **not** overwrite frozen output-consumer formulas.

The N08 contract explicitly preserves:

```text
Bangtinh!G181 = ROUND(G169 + G178, 0)
Bangtinh!G182 = ROUND(G181, -6)
Offical!E32   = Bangtinh!G181
```

Thus `total_value_before_rounding_vnd` and `final_appraised_value_vnd` remain distinct. `Offical!E32` consumes the pre-million-rounding G181 value, not G182.

## 11. Determinism boundary

Given identical supported source bytes and identical canonical write payload, package serialization is normalized so the generated artifact SHA is deterministic for the tested runtime.

This is generation determinism only. It is not a claim that Microsoft Excel has recalculated the workbook or that qualification checkpoints pass.

## 12. Explicit non-scope

Not implemented or claimed here:

- Microsoft Excel Desktop recalculation/qualification PASS;
- E1-PR-006 Astryx manual workbench integration;
- E1-PR-007 end-to-end Excel qualification;
- approval-return import/revision workflow;
- arbitrary external-link repair;
- generic template-family formula rewriting;
- CTXD calculation engine;
- OCR/Maps;
- Historical Learning;
- Epic 1 closure.
