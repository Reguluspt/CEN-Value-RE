# E0-PR-008 — Independent Review Handoff v1

**Date:** 2026-08-17
**Repository:** `Reguluspt/CEN-Value-RE`
**Branch:** `agent/e0-pr-008-excel-qualification`
**Implementation baseline:** `560e6dee34ceeaceb492eb4576f6081dff3e61f1`
**Runtime-tested HEAD:** `27552f4f32b3f7806282aba9b94434c5b4d711fb`
**Binding GitHub Actions run:** `31983760941`
**Runner:** `windows-latest`
**Python:** `3.11.9`
**Result:** `142 passed in 2.42s`
**Decision requested:** `ACCEPTED` / `RETURN FINDINGS`

## Exact review-head rule

Before verdict, resolve the current PR HEAD directly from GitHub. If it differs from the exact review HEAD supplied with the review request, stop and report `HEAD MISMATCH` until the delta is reviewed.

The final runtime-tested implementation HEAD is:

`27552f4f32b3f7806282aba9b94434c5b4d711fb`

Any later delta may contain only:

- successful binding evidence/logs;
- removal of the one-time verification workflow;
- implementation report;
- independent-review handoff/documentation.

If implementation source, tests, dependency pin, or qualification contract changed after the tested HEAD without a new full Windows run, do not accept.

## Frozen authority

Review against:

- `epic-0/EPIC_0_PR_PLAN_v1.md` — E0-PR-008 scope/acceptance;
- `epic-0/EPIC_0_ACCEPTANCE_MATRIX_v1.md`;
- `epic-0/EPIC_0_ENGINEERING_FOUNDATION_PACKET_v1.md`;
- `Design Book/13_EXCEL_COMPATIBILITY.md`;
- `epic-0/E0_PR_008_EXCEL_QUALIFICATION_CONTRACT_v1.md`;
- E0-PR-004 template-profile/fingerprint contracts;
- E0-PR-005 Golden Fixture manifest/comparator contracts.

## Expected implementation surface

Implementation-bearing files are limited to:

- `requirements-re.txt`;
- `src/re/ports/excel_qualification.py`;
- `src/re/application/services/excel_qualification.py`;
- `src/re/adapters/excel_qualification/__init__.py`;
- `src/re/adapters/excel_qualification/com_runner.py`;
- `src/re/adapters/excel_qualification/qualification_cli.py`;
- `tests/re/test_excel_qualification_harness.py`;
- `epic-0/E0_PR_008_EXCEL_QUALIFICATION_CONTRACT_v1.md`;
- evidence/report files.

The one-time verification workflow must be absent from the final review tree.

## Required review

### 1. Scope / architecture

Confirm:

- runner abstractions are framework-independent under `src/re/ports/`;
- application qualification orchestration does not import pywin32/COM/concrete runner;
- existing `src/re/adapters/excel/` remains profile/fingerprint-only and workbook-runtime-free;
- COM runtime lives in separate `src/re/adapters/excel_qualification/` infrastructure;
- no workbook generation/fill, approval round-trip, valuation formula, persistence, API/UI feature, or Tauri wiring is introduced;
- no claim of GF-01/GF-02 end-to-end correctness is made.

### 2. Fail-closed qualification states

Confirm report states are exactly:

- PASS;
- FAILED;
- NOT_QUALIFIED.

`NOT_QUALIFIED` must never be treated as PASS.

A PASS must be impossible unless the report has:

- `actual_excel_evidence=true`;
- `full_recalculation_performed=true`;
- `opened_without_link_updates=true`;
- non-empty Excel version;
- non-empty required checkpoint results;
- every checkpoint `passed=true`.

Review both constructor invariants and orchestration paths.

### 3. Report schema / evidence binding

Confirm schema v1 records:

- profile id/version;
- exact workbook SHA-256;
- manifest id/version;
- checkpoint-set SHA-256;
- runner id/version;
- Excel version where available;
- actual-Excel/full-recalc/no-link-update flags;
- ordered checkpoint outcomes with expected/actual/pass/reason.

Serialization must be deterministic.

Workbook hash mismatch must produce `NOT_QUALIFIED`.

### 4. Checkpoint reuse

Confirm E0-PR-008 delegates checkpoint evaluation to the E0-PR-005 versioned Golden Fixture manifest/comparator rather than creating a second global epsilon or duplicate valuation rules.

Actual Excel evidence with failed/missing/unexpected required checkpoints must produce `FAILED`.

### 5. Windows COM runner interface

Review `WindowsExcelCOMRunner` and confirm:

- pywin32 import is lazy;
- `DispatchEx("Excel.Application")` is used for an isolated instance;
- Excel is hidden and alerts disabled;
- workbook is opened with `UpdateLinks=0` and read-only mode;
- `CalculateFullRebuild` is called;
- runner waits until calculation state is `xlDone` (`0`) or times out;
- only requested `Sheet!A1` checkpoints are read using `Value2`;
- workbook is closed without saving;
- Excel is quit in cleanup paths;
- evidence is bound to exact workbook SHA-256;
- non-Windows, missing pywin32, or Excel activation failure reports unavailable rather than PASS.

A fake COM unit test proves call/interface semantics. Treat it as interface proof only, not real Excel qualification.

### 6. Qualification CLI

Expected module:

`python -m src.re.adapters.excel_qualification.qualification_cli`

Required inputs:

- `--workbook`;
- `--profile-id`;
- `--profile-version`;
- `--manifest`;
- `--report`.

Exit codes:

- 0 = PASS;
- 1 = FAILED;
- 2 = NOT_QUALIFIED.

### 7. Binding no-Excel runtime proof

Only run `31983760941` is binding.

Expected checked-out/tested HEAD:

`27552f4f32b3f7806282aba9b94434c5b4d711fb`

Expected runner/runtime:

- `windows-latest`;
- Python `3.11.9`;
- pywin32 `312` installed/importable;
- result `142 passed in 2.42s`.

The hosted Windows runner does not provide Microsoft Excel Desktop. The actual CLI/probe must therefore prove fail-closed behavior:

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

This vector is **not Excel qualification PASS**. It proves only that no-Excel/skip behavior cannot accidentally pass.

### 8. Verification history

Do not bind to earlier failed runs:

- `31983476082`: stopped before tests on contract whitespace/encoding hygiene;
- `31983589182`: `1 failed, 141 passed`; correctly exposed E0-PR-004 architecture regression because COM runtime was initially placed under profile/fingerprint adapter package;
- `31983760941`: `142 passed`; architecture corrected and no-Excel proof passed; FINAL/BINDING.

### 9. Evidence binding

Compare runtime-tested HEAD to exact current review HEAD.

Allowed post-test delta only:

- binding evidence/logs;
- removal of one-time workflow;
- implementation report;
- independent-review handoff/documentation.

There must be no untested post-run changes to:

- `requirements-re.txt`;
- `src/re/ports/excel_qualification.py`;
- `src/re/application/services/excel_qualification.py`;
- `src/re/adapters/excel_qualification/*`;
- `tests/re/test_excel_qualification_harness.py`;
- `epic-0/E0_PR_008_EXCEL_QUALIFICATION_CONTRACT_v1.md`.

## Primary evidence

- `evidence/E0_PR_008_RUNTIME_EVIDENCE_v1.md`;
- `evidence/E0-PR-008_tests_v1.log`;
- `evidence/E0-PR-008_no_excel_vectors_v1.log`;
- `implementation/E0_PR_008_IMPLEMENTATION_REPORT_v1.md`;
- this handoff.

## Finding format

For each finding report:

- ID;
- severity: BLOCKER / HIGH / MEDIUM / LOW;
- exact file/path;
- exact issue;
- why it matters;
- required corrective action;
- acceptance test for closure.

Do not create blocking findings for cosmetic/style preference.

## Required verdict

If clean:

```text
FINDINGS
- NONE

VERDICT:
ACCEPTED

E0-PR-008 may proceed to merge. Epic 0 foundation may close and the next roadmap slice may begin after merge.
```

If findings exist:

```text
VERDICT:
RETURN FINDINGS

OPEN FINDINGS:
- ...

E0-PR-008 must not merge until findings are closed.
```

E0-PR-008 is not self-accepted by the implementer.
