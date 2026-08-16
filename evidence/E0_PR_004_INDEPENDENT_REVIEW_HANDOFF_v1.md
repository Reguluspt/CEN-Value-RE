# E0-PR-004 — Independent Review Handoff v1

**Date:** 2026-08-16
**Repository:** `Reguluspt/CEN-Value-RE`
**Branch:** `agent/e0-pr-004-excel-profile`
**Implementation baseline:** `eb8144b47576bf847c618bf13836aff7a9e7d37c`
**Runtime-tested HEAD:** `af37fde63c39c6cfd723edb20cf036e3dc276ca8`
**Successful runtime run:** `31954303962`
**Focused result:** `70 passed in 0.13s`
**Decision requested:** ACCEPTED / RETURN FINDINGS

## Exact review-head rule

Before issuing a verdict, resolve the current exact PR HEAD from GitHub.

Compare runtime-tested HEAD `af37fde63c39c6cfd723edb20cf036e3dc276ca8` to the current review HEAD. Any post-test delta must be limited to:

- successful-run evidence;
- removal of the one-time verification workflow;
- implementation report;
- independent-review handoff documentation.

If any implementation or test file changed after the runtime-tested HEAD without a corresponding rerun, do not accept.

## Frozen authority

Review against:

- `epic-0/EPIC_0_PR_PLAN_v1.md` — E0-PR-004 scope/acceptance;
- `gate-b/EXCEL_TEMPLATE_PROFILE_v1.md` — profile/cell classes/compatibility/fail-safe contract;
- `gate-b/EXCEL_TEMPLATE_FINGERPRINT_v1.md` — N08 sheet-state/formula signatures and match policy;
- Epic 0 corrective rule: structural-critical mismatch is blocking; metadata is lenient/warning.

Do not redesign or expand into E0-PR-005 Golden Fixture Harness or full Excel read/write/recalculation runtime.

## Expected implementation surface

Implementation:

- `src/re/adapters/excel/__init__.py`
- `src/re/adapters/excel/profile.py`
- `src/re/adapters/excel/fingerprint.py`
- `src/re/adapters/excel/n08_0038.py`

Tests:

- `tests/re/test_excel_template_profile.py`

Evidence/report files under `evidence/` and `implementation/` are expected.

## Required technical review

### 1. Scope and architecture

Confirm:

- implementation stays in Excel adapter infrastructure;
- Domain/Application/Ports boundaries are not weakened;
- no openpyxl, COM, xlwings or workbook runtime dependency is introduced;
- no workbook fill/write implementation exists;
- no Golden Fixture Harness, valuation formula, persistence, API/UI/provider or Epic 1 feature is added.

### 2. Profile schema

Confirm the profile can represent:

- profile identity/version/source exemplar;
- required sheet names/states;
- cell safety classes;
- formula signatures;
- compatibility transformations;
- exact alternate formulas for declared transformations;
- required named/control ranges;
- external-link policy;
- source fingerprint hashes as provenance.

Confirm unknown cells default to `UNKNOWN` and no write permission is inferred.

### 3. N08 frozen data

Confirm against Gate B:

- profile id `cenvalue-re-n08-0038-v1`;
- all 16 required sheet/state entries;
- all 24 formula signature cells/formulas;
- source sheet/state SHA `481997e9672fa4fa88a8b00cb677280e72916b5ce29fde0625f508409ab5e951`;
- source formula checkpoint SHA `05812836786218f2893feeb065e271b515b777aa8b3b5965dcc8c9819a4e2d7d`;
- effective-age/appraisal-date transformation metadata;
- stale `Phieu TTTT!E5` localization metadata.

Gate-B v1 does not enumerate concrete required named/control-range names. Confirm the implementation does not invent them and does fail closed once a profile declares them.

### 4. Formula normalization and signatures

Confirm normalization:

- canonicalizes optional leading `=`;
- ignores insignificant whitespace/case outside literals;
- preserves double-quoted string values exactly;
- preserves quoted sheet-name content;
- does not rewrite locale separators, `$` references or literal values;
- malformed quoted formulas produce fail-closed `FORMULA_INVALID` rather than an unhandled exception.

Review deterministic normalized signature digests and ensure a semantic mutation changes/rejects the signature.

### 5. Fail-closed matching

Confirm these are blocking:

- required sheet missing;
- required sheet-state mismatch;
- unknown extra sheet under N08 strict no-extra policy;
- required formula-signature missing;
- normalized formula mismatch;
- undeclared external-link state;
- declared required control missing.

Confirm filename mismatch is warning-only metadata and filename cannot identify a template.

Sheet order is intentionally not identity. Review that this is consistent with the frozen minimum match rule (required sheets exist/states match) and does not weaken structural safety because names/states and extra sheets remain strict.

### 6. Compatibility transformation safety

Confirm a compatibility transformation declaration alone does **not** allow arbitrary formula drift.

Only an exact alternate formula explicitly declared for that cell may pass as a transformation exception. A different arbitrary formula must remain `UNSUPPORTED_TEMPLATE`.

### 7. External-link policy

For N08 confirm:

- `NONE` is supported;
- `KNOWN_STALE_SELF_REFERENCE` is supported with warning because Gate B explicitly records the stale compatibility condition;
- unknown/undeclared states reject the candidate.

### 8. Frozen acceptance vectors

From runtime evidence:

- structurally declared N08 exemplar observation -> `MATCHED`;
- deliberate `Bangtinh!H119` mutation `ROUND(...,-3)` -> `ROUND(...,-4)` -> `UNSUPPORTED_TEMPLATE` / `FORMULA_SIGNATURE_MISMATCH`.

Primary logs:

- `evidence/E0_PR_004_RUNTIME_EVIDENCE_v1.md`;
- `evidence/E0-PR-004_tests_v1.log`;
- `evidence/E0-PR-004_fingerprint_vectors_v1.log`.

Run `31954303962` is expected to show Python 3.11.15 and **70 passed in 0.13s**.

### 9. Evidence binding

Verify no `src/` or `tests/` file changed after tested HEAD `af37fde63c39c6cfd723edb20cf036e3dc276ca8`.

## Finding format

If a finding exists, report:

- ID;
- severity: BLOCKER / HIGH / MEDIUM / LOW;
- file/path and exact issue;
- why it matters;
- required corrective action;
- acceptance test for closure.

Do not raise cosmetic/style preferences as blocking findings.

## Required output

Return:

```text
E0-PR-004 INDEPENDENT REVIEW

Repository:
PR:
Base:
Runtime-tested HEAD:
Reviewed HEAD:
Runtime run:

1. Scope / Architecture Review
...

2. Profile Schema Review
...

3. N08 Frozen Data Review
...

4. Formula Normalization / Fingerprint Review
...

5. Fail-Closed / Compatibility Review
...

6. Runtime / Evidence Review
...

7. Evidence Binding Review
...

FINDINGS
- NONE

VERDICT:
ACCEPTED

E0-PR-004 may proceed to merge and E0-PR-005 may begin after merge.
```

or `RETURN FINDINGS` with open findings.

E0-PR-004 remains **not self-accepted** until this independent verdict is supplied and bound to the exact reviewed PR head.
