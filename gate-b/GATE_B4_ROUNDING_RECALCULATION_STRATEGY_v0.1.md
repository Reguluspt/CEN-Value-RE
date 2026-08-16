# Gate B.4 — Rounding, Tolerance & Excel Recalculation Strategy v0.1
**Status:** DESIGN BASELINE / PILOT VALIDATION REQUIRED

## 1. Source-of-truth rule
CenValue's deterministic calculation engine is the canonical calculation source. The legacy workbook is a compatibility/output oracle and approval artifact.

The application must never depend on an open workbook session to know the canonical appraisal result.

## 2. Rounding policy
Rounding must be explicit per calculation checkpoint, never implicit through UI formatting.

Observed workbook rules include:
- CTXD age-method remaining quality: `ROUND(..., 2)`.
- CTXD average remaining quality: `ROUND(..., 2)`.
- final indicated unit price at `Bangtinh!H119`: `ROUND(..., -3)` (nearest thousand VND/m²).

Other intermediate adjustment calculations in the sampled `Bangtinh` region are not wrapped in `ROUND`; therefore CenValue must preserve higher precision internally and round only at declared checkpoints.

### Canonical numeric rule
- Use decimal arithmetic, not binary floating point.
- Persist selected human percentages exactly at the input precision.
- Derived values retain sufficient decimal precision until an explicit checkpoint.
- UI formatting is presentation only.

## 3. Compatibility tolerance
Checkpoint comparison uses two categories:

### Exact checkpoints
For explicitly rounded whole-money/unit-price outputs:
- expected equality after applying the workbook's declared rounding.

### Decimal checkpoints
For percentages/intermediate decimal results:
- compare after applying the exact checkpoint scale/rule.
- do not introduce a generic global epsilon in place of the workbook formula.

Until every workbook checkpoint is mapped, tolerance remains profile-specific rather than one global number.

## 4. Recalculation strategy

### Production export
The adapter:
1. fingerprints the workbook/template;
2. fills only declared input cells/ranges;
3. preserves protected/formula cells unless an approved compatibility transformation exists;
4. writes deterministic CenValue outputs only to explicitly mapped output/override cells;
5. marks workbook calculation properties for full recalculation on open where supported;
6. saves a generated approval artifact and its hash.

### Canonical result
CenValue does not read its own final answer back from Excel to establish truth. It calculates the canonical result in the domain engine and compares it to declared workbook checkpoints during validation.

### Excel-engine verification
For workbook-compatibility qualification/pilot regression, use a Windows verification environment with Microsoft Excel automation when available to force a real Excel recalculation and capture checkpoint values.

Do not require Microsoft Excel merely to operate core CenValue workflows.

### Non-Excel fallback
A library such as openpyxl can preserve/write formulas but does not calculate them. Therefore openpyxl alone is not accepted as proof that legacy formulas recalculate correctly.

LibreOffice/headless calculation may be used for diagnostic testing but must not silently become the compatibility oracle if results differ from Microsoft Excel.

## 5. Volatile formula policy
Volatile formulas that make historical results change after time passes must be neutralized through a declared template-profile transformation.

First frozen example:
`YEAR(NOW())` for construction effective age is replaced logically by the case `appraisal_date`.

Any such transformation must be:
- profile-versioned;
- documented;
- covered by a checkpoint test;
- visible in audit metadata.

## 6. Formula protection
Cell classes in `ExcelTemplateProfile`:
- `INPUT` — adapter may write.
- `FORMULA_PROTECTED` — adapter must not overwrite.
- `OUTPUT_CHECKPOINT` — formula/result monitored.
- `CONTROL` — lookup/reference/configuration.
- `APPROVAL_RETURN` — mapped for returned-file diff.
- `VOLATILE_COMPAT_OVERRIDE` — narrowly approved transformation.

Unknown cells are read-only by default.

## 7. Release gate
A template profile is release-qualified only when:
- fingerprint matches;
- all required mapped inputs are filled;
- formula integrity check passes;
- every mandatory checkpoint matches expected values under its declared rounding/tolerance rule;
- generated workbook opens/recalculates successfully in the qualification environment;
- no unknown external link silently changes a required checkpoint.

## 8. Known external-link risk
The workbook dependency analysis found one external workbook reference. Before Epic 1 acceptance, that dependency must be classified as:
- irrelevant to required checkpoints,
- replaced/localized,
- or explicitly required and packaged.
Unknown external dependency = release blocker.

## 9. Next work
- Build the complete Mapping Matrix for all required workflow regions.
- Trace the one external dependency to affected checkpoints.
- Freeze the remaining Adjustment amplitude and final-result formulas.
- Create golden case fixtures using the original workbook plus expected checkpoint values.
