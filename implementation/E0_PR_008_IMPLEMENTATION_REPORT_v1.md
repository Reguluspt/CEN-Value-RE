# E0-PR-008 — Excel Qualification Harness Skeleton — Implementation Report v1

**Date:** 2026-08-17
**Repository:** `Reguluspt/CEN-Value-RE`
**Branch:** `agent/e0-pr-008-excel-qualification`
**Implementation baseline:** `560e6dee34ceeaceb492eb4576f6081dff3e61f1`
**Final runtime-tested HEAD:** `27552f4f32b3f7806282aba9b94434c5b4d711fb`
**Binding GitHub Actions run:** `31983760941`
**Runner:** `windows-latest`
**Python:** `3.11.9`
**Result:** `142 passed in 2.42s`

## 1. Scope implemented

E0-PR-008 implements only the Epic 0 qualification skeleton:

- framework-independent Excel qualification runner port;
- deterministic qualification report schema and orchestration;
- isolated Windows Excel Desktop COM adapter;
- qualification CLI;
- Windows-only `pywin32==312` dependency pin;
- no-Excel fail-closed runtime proof;
- focused tests and contract documentation.

It does not implement workbook generation/fill, input mapping execution, external-link rewrite, approval artifact save/hash pipeline, Excel installer/licensing, Tauri invocation, approval round-trip, valuation formulas, or GF-01/GF-02 end-to-end correctness.

## 2. Architecture boundary

`src/re/ports/excel_qualification.py` owns the runner protocol and evidence DTOs.

`src/re/application/services/excel_qualification.py` consumes only the port plus the E0-PR-005 Golden Fixture comparator. It does not import pywin32, COM, or concrete Excel adapters.

Workbook-runtime infrastructure is isolated in `src/re/adapters/excel_qualification/`. The E0-PR-004 `src/re/adapters/excel/` package remains profile/fingerprint-only with no workbook runtime dependency.

## 3. Qualification states and fail-closed PASS invariant

Reports use exactly:

- `PASS`;
- `FAILED`;
- `NOT_QUALIFIED`.

`PASS` can only be constructed when all are true:

- actual Excel evidence exists;
- full recalculation is evidenced;
- the workbook was opened without arbitrary link updates;
- Excel version is recorded;
- a non-empty required checkpoint set exists;
- every required checkpoint passes.

The service also rejects workbook-hash mismatch, incomplete execution evidence, runner failure, or missing Excel as `NOT_QUALIFIED` rather than PASS.

When actual Excel evidence exists but required checkpoint comparison fails, status is `FAILED`.

## 4. Report binding

Schema v1 records:

- profile id/version;
- exact workbook SHA-256;
- manifest id/version;
- checkpoint-set SHA-256;
- runner id/version;
- Excel version when available;
- actual-Excel/full-recalc/no-link-update evidence flags;
- ordered per-checkpoint expected/actual/pass/reason results.

JSON serialization is deterministic.

## 5. Windows COM runner

`WindowsExcelCOMRunner`:

- lazily imports pywin32;
- uses isolated `DispatchEx("Excel.Application")`;
- keeps Excel hidden and disables alerts;
- opens with `UpdateLinks=0`, `ReadOnly=True`;
- calls `CalculateFullRebuild`;
- waits for Excel calculation state `xlDone`;
- reads only requested `Sheet!A1` checkpoints through `Value2`;
- closes without saving;
- quits Excel;
- returns evidence bound to the input workbook SHA-256.

If Windows/pywin32/Excel Desktop is unavailable, the runner reports unavailable rather than manufacturing PASS evidence.

## 6. Checkpoint comparison

E0-PR-008 reuses the versioned Golden Fixture manifest and `evaluate_checkpoint_results()` from E0-PR-005. It does not introduce another global epsilon or duplicate valuation rules.

## 7. CLI

Command:

`python -m src.re.adapters.excel_qualification.qualification_cli`

Exit codes:

- `0` = PASS;
- `1` = FAILED;
- `2` = NOT_QUALIFIED.

Normal qualification outcomes write the JSON report.

## 8. Verification history

### Run 1 — `31983476082` — NON-BINDING

Stopped before tests because `git diff --check` correctly found trailing whitespace in the contract Markdown. The contract was also repaired to clean UTF-8 before any review handoff. No acceptance evidence was produced.

### Run 2 — `31983589182` — NON-BINDING

Compile and bounded-scope checks passed. The full suite found one architecture regression: the COM runner had initially been placed under `src/re/adapters/excel/`, violating the E0-PR-004 guard that keeps profile/fingerprint infrastructure free of workbook-runtime dependencies. Result: `1 failed, 141 passed`.

Corrective action moved COM/CLI runtime to `src/re/adapters/excel_qualification/`; the old profile package remained runtime-free.

### Run 3 — `31983760941` — FINAL / BINDING

Tested HEAD:

`27552f4f32b3f7806282aba9b94434c5b4d711fb`

Runner:

`windows-latest`

Result:

`142 passed in 2.42s`.

The E0-PR-004 architecture guard passed after the boundary correction.

## 9. Hosted Windows no-Excel evidence

The binding runner successfully installed/imported pywin32, but Microsoft Excel Desktop could not be activated.

The actual CLI/probe therefore produced:

```text
runner_platform=windows
pywin32_available=true
excel_desktop_available=false
probe_reason_code=EXCEL_APPLICATION_UNAVAILABLE
qualification_status=NOT_QUALIFIED
actual_excel_evidence=false
pass_without_excel=false
profile_id=cenvalue-re-n08-0038-v1
profile_version=1
manifest_id=N08-0038-checkpoints-v1
manifest_version=1
checkpoint_count=31
checkpoint_set_sha256=48e991b8897498da192f0964ba6c198b0f26e9cc0f8f2b750b81ed1e8b4de2fb
workbook_sha256=c8975687aba624268d9be1b9b5fa302db39ff13babf2b43c325ae97cf96c51ea
```

This is the required fail-closed unavailable proof. It is **not Microsoft Excel qualification PASS**.

## 10. Evidence

- `evidence/E0_PR_008_RUNTIME_EVIDENCE_v1.md`
- `evidence/E0-PR-008_tests_v1.log`
- `evidence/E0-PR-008_no_excel_vectors_v1.log`
- `epic-0/E0_PR_008_EXCEL_QUALIFICATION_CONTRACT_v1.md`
- this implementation report.

## 11. Gate

This report is implementation evidence, not self-acceptance. E0-PR-008 must remain unmerged until an independent reviewer returns `ACCEPTED` against the exact review HEAD and confirms there is no untested implementation delta after the runtime-tested HEAD.
