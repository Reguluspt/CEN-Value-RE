# Gate B.12 — Microsoft Excel Qualification Protocol v1
**Status:** DESIGN FROZEN / EXECUTION REQUIRES WINDOWS + MICROSOFT EXCEL

## Purpose
Verify that a generated approval workbook is genuinely compatible with Microsoft Excel and the declared template profile.

## Test environment
- Windows machine used for CenValue desktop qualification.
- Supported Microsoft Excel desktop version recorded in test evidence.
- Test is automated through an approved Windows Excel automation harness (COM/Office automation or equivalent controlled mechanism).

## Procedure
1. Copy the immutable source template to a temporary qualification path.
2. Verify `ExcelTemplateProfile` fingerprint/signature.
3. Fill only declared `INPUT`/approved compatibility-override cells.
4. Save the candidate workbook.
5. Open workbook in Microsoft Excel with links/update prompts controlled by the harness.
6. Force full calculation/rebuild.
7. Save and close.
8. Re-open read-only and capture all declared checkpoint values plus formula integrity hashes.
9. Compare against CenValue canonical expected values under per-checkpoint rounding rules.
10. Verify no unresolved external-link prompt/dependency remains for the stale self-reference.
11. Produce a machine-readable qualification report.

## Mandatory evidence
- source template hash;
- generated workbook hash before Excel recalc;
- generated workbook hash after Excel recalc;
- Excel version/build;
- profile ID/version;
- checkpoint expected/actual/pass-fail;
- formula-integrity result;
- external-link result;
- timestamp.

## Failure policy
Any mandatory checkpoint mismatch, unexpected formula mutation, unresolved mandatory external dependency, unsupported template signature or Excel open/recalc error = qualification FAIL.

## CI strategy
Normal cross-platform/unit CI runs the deterministic CenValue engine and adapter tests without Excel.
A Windows qualification job is a release/pilot gate, not a dependency for every developer edit.

## Golden exemplar
Initial qualification fixture: N08-0038. Expected checkpoint values are defined in `GOLDEN_CASE_CHECKPOINT_MANIFEST_v0.2.md`.
