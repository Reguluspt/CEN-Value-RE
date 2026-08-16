# CenValue RE — Workbook Engineering Baseline Status

**Date:** 2026-08-16  
**Canonical workbook:** `/CEN Value RE/(Trunghd_HTG) N08-0038-Huedtl-MTNguyenVanDau-P5-PhuNhuan-htg.xlsx`  
**SHA-256:** `d410cfcc2263d7d50a436a79e192461f04b6863e6c3676a28da7a2eed287389c`

## Baseline already established
Prior structural inspection established:
- 16 worksheets;
- 13,689 formula cells;
- protected and hidden helper sheets;
- one stale external workbook reference;
- legacy `YEAR(NOW())` CTXD volatility;
- cached `#REF!`/other legacy errors outside the proven golden valuation path;
- G181/G182 divergence as separate output contracts;
- workbook percentage values stored on fraction scale such as `0.05 = 5%`.

## Current engineering-copy state
No modified/unlocked workbook has been issued in this step.

The approved spreadsheet engine (`artifact_tool`) fails with an RPC transport error while importing this workbook. Because preservation of formulas, defined names, validations, cached values and package structure is more important than merely removing sheet-protection XML, the workspace does **not** use an alternate library or raw OOXML mutation as a workaround.

## Safe next action
When tool-safe workbook import/export is available:
1. import the canonical workbook;
2. create one engineering copy under `/CEN Value RE/fixtures`;
3. remove sheet protection only on the engineering copy;
4. preserve the root canonical workbook byte-for-byte;
5. compare sheet names, formula count/signatures, defined names, external links, validations and critical checkpoints before/after export;
6. record both hashes and a structural diff report.

Until then, all workbook-derived analysis remains read-only evidence and the original root workbook remains the only workbook artifact.
