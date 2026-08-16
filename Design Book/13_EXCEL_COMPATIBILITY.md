# 13 — Excel Compatibility & Output Adapter
**Status: REVIEWED — RELEASE CRITICAL; TEMPLATE FAMILY/TOLERANCE MATRIX OPEN**

## Role
Legacy workbook is:
- GĐ1 approval/output artifact;
- regression/compatibility oracle during migration.

Canonical CenValue domain/calculation is source of truth.

## Workbook evidence
Current sample:
- 16 sheets;
- 13,689 formula cells;
- calculation chain;
- defined names/protected sheets;
- one external workbook link.

## ExcelTemplateProfile
Must declare:
- workbook/template fingerprint;
- supported template family/version;
- canonical ↔ cell/range input mapping;
- formula/protected regions;
- approved volatile-formula replacements;
- known external-link handling;
- required checkpoints;
- rounding/tolerance rules.

## Output pipeline
```text
Canonical Case Snapshot
→ TemplateProfile validation
→ fill mapped input cells
→ resolve/sanitize known external-link exceptions
→ preserve formulas/layout
→ Excel Desktop full recalculation when available
→ read checkpoints
→ compare with CenValue Engine
→ PASS/BLOCK
→ save/hash approval workbook
```

## Recalculation
Preferred Windows compatibility runner: Microsoft Excel Desktop automation when installed.

Open without updating arbitrary external links, force full recalculation/dependency rebuild, then save and read checkpoints.

If Excel Desktop is unavailable:
- core appraisal remains usable;
- workbook can be generated as `RECALC_PENDING_EXCEL`;
- checkpoint verification must not be reported as PASS.

## External links
Sample has a stale/redundant link at `Phieu TTTT!E5`.

Policy:
- unknown external link → TemplateProfile validation fails/requires review;
- known redundant link → explicitly replace/internalize via profile;
- never silently update arbitrary historical file paths.

## Volatile formulas
Legacy `YEAR(NOW())` for CTXD effective age is not canonical.
Adapter must reproduce calculation using `AppraisalCase.appraisal_date` and prevent future reopen from changing closed-case output.

## Required checkpoint classes
Adjustment:
- `Bangtinh!F108:H115`
- `Bangtinh!H119`

CTXD:
- Gate B.1 checkpoints including rows 127, 140, 153, 156–163.

Additional upstream/downstream checkpoints will be added as mapping closes.

## Release gate
PASS requires:
- matching fingerprint;
- complete required mappings;
- no unknown external dependency;
- canonical calculation success;
- required Excel recalculation/verification when runner available;
- all required checkpoints within frozen tolerance.
