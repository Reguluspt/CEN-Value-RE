# Golden Fixture Normalization Report v1

**Date:** 2026-08-16  
**Source raw fixture:** `gate-b/GOLDEN_CASE_CANONICAL_FIXTURE_v0.1.json`  
**Output:** `corrective/GOLDEN_CASE_CANONICAL_FIXTURE_v1.json`

## Purpose
Separate canonical typed values from legacy Excel-cache representation without deleting the original extraction evidence.

## Applied normalization
- Excel serial `46239` → `appraisal_date = 2026-08-05`.
- Percentage convention explicitly uses fraction scale: `0.05 = 5%`.
- Profile selector preserves raw `"BIDV "` and exposes canonical trimmed `"BIDV"`.
- Known binary-float cache artefacts were normalized:
  - `19.350000000000001` → `19.35`;
  - `327.58999999999997` → `327.59`.
- CTXD exemplar inputs documented by the Gate-B contract/workbook review were added for the golden case:
  - economic life `50` years;
  - maintenance adjustment `0.05`.
- Money/area/percentage decimals remain JSON strings so a loader can construct `Decimal` exactly rather than passing through binary float.

## Deliberately not invented
The normalized fixture is marked **PARTIAL INPUT COVERAGE**. It does not fabricate missing C1-C11 adjustment decisions, construction component deterioration observations, or profile-specific source lineage that are absent from the source fixture. Those must be extracted/versioned before the Golden Fixture Harness can claim full walking-skeleton input coverage.

## Raw evidence policy
The existing `gate-b/GOLDEN_CASE_CANONICAL_FIXTURE_v0.1.json` is retained as raw legacy extraction evidence; it is not duplicated byte-for-byte under `fixtures/`.
