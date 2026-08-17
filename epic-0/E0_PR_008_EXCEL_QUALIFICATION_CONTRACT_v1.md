# E0-PR-008 — Excel Qualification Harness Contract v1

**Status:** IMPLEMENTATION CONTRACT — EPIC 0 SKELETON
**Baseline:** E0-PR-007 accepted/merged
**Scope:** Windows qualification command/report schema + Excel COM runner boundary

## 1. Purpose

This contract defines a fail-closed qualification harness for Microsoft Excel Desktop compatibility. It does **not** implement workbook generation/fill, approval workflow, or the canonical valuation engine.

The legacy workbook remains an output/compatibility artifact. CenValue RE calculation remains canonical.

## 2. Qualification states

The only report states are:

- `PASS`
- `FAILED`
- `NOT_QUALIFIED`

`NOT_QUALIFIED` is not PASS and must remain visible to callers.

A report may be `PASS` only when all of the following are evidenced:

1. an actual Microsoft Excel Desktop COM execution occurred;
2. the evidence is bound to the exact workbook SHA-256;
3. the workbook was opened with arbitrary external-link updates disabled;
4. Excel `CalculateFullRebuild` completed;
5. an Excel version is recorded;
6. every required checkpoint in the versioned manifest is present and passes the frozen per-checkpoint comparison policy.

Missing Excel, missing COM capability, runner failure, incomplete recalculation evidence, or missing link-update-policy evidence produces `NOT_QUALIFIED`, never PASS.

Actual Excel evidence with failed, missing, or unexpected required checkpoints produces `FAILED`.

## 3. Report schema v1

Every report records:

- `schema_version`;
- `status`;
- `reason_code` and bounded reason;
- `profile_id`;
- `profile_version`;
- exact `workbook_sha256`;
- `manifest_id`;
- `manifest_version`;
- `checkpoint_set_sha256`;
- runner id/version;
- Excel version when available;
- `actual_excel_evidence`;
- `full_recalculation_performed`;
- `opened_without_link_updates`;
- ordered per-checkpoint results including expected/actual/pass/reason.

The schema constructor itself rejects a `PASS` report that lacks actual Excel evidence, full recalculation evidence, no-link-update evidence, Excel version, or an all-pass checkpoint set.

## 4. Runner port

`src/re/ports/excel_qualification.py` owns the framework-independent runner contract.

The application service must not import `win32com`, COM types, Excel APIs, or adapter implementation.

## 5. Windows COM adapter

`WindowsExcelCOMRunner` is adapter infrastructure.

Target behavior:

1. lazily load pywin32;
2. create isolated `Excel.Application` through `DispatchEx`;
3. keep Excel hidden and disable alerts;
4. open workbook with `UpdateLinks=0` and read-only mode;
5. execute `CalculateFullRebuild`;
6. wait for Excel calculation state `xlDone`;
7. read only the requested `Sheet!A1` checkpoint values;
8. close workbook without saving;
9. quit Excel;
10. return evidence bound to the workbook SHA-256.

The runner must report unavailable rather than claiming PASS when:

- platform is not Windows;
- pywin32 COM support is unavailable;
- Microsoft Excel Desktop cannot be activated.

## 6. Qualification command

Command module:

`python -m src.re.adapters.excel.qualification_cli`

Required inputs:

- `--workbook`
- `--profile-id`
- `--profile-version`
- `--manifest`
- `--report`

Exit codes:

- `0` = PASS
- `1` = FAILED
- `2` = NOT_QUALIFIED

The command must write the JSON report for all normal qualification outcomes.

## 7. External links

The qualification runner opens with `UpdateLinks=0`.

This skeleton does not resolve or sanitize links itself. Template-profile validation and known-link handling remain the upstream responsibility defined by the Excel compatibility design. The runner must never silently update arbitrary historical links.

## 8. Checkpoint policy

Checkpoint comparison is delegated to the versioned Golden Fixture manifest and E0-PR-005 comparator. E0-PR-008 must not introduce a second global epsilon or duplicate valuation rules.

## 9. CI / no-Excel proof

A Windows environment with pywin32 installed but Microsoft Excel Desktop unavailable must produce `NOT_QUALIFIED`.

CI evidence must explicitly prove:

- status is not PASS;
- `actual_excel_evidence=false`;
- report still contains profile id/version, workbook SHA-256, manifest id/version/checkpoint-set hash, and ordered checkpoint IDs.

This proves unavailable/skip behavior is fail-closed; it is not Excel qualification PASS.

## 10. Deferred

Not implemented by this PR:

- workbook generation/fill;
- template input mapping execution;
- external-link rewrite implementation;
- workbook save/hash approval artifact pipeline;
- Excel installer/licensing;
- Tauri invocation wiring;
- approval round-trip;
- valuation formulas;
- GF-01/GF-02 end-to-end appraisal correctness.

Those require later vertical slices and/or real Excel qualification inputs.
