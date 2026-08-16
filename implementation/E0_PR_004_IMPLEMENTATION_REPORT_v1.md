# E0-PR-004 — ExcelTemplateProfile + Fingerprint — Implementation Report v1

**Date:** 2026-08-16
**Status:** IMPLEMENTED; RUNTIME EVIDENCE GREEN; INDEPENDENT ACCEPTANCE PENDING
**Repository:** `Reguluspt/CEN-Value-RE`
**Implementation baseline:** `eb8144b47576bf847c618bf13836aff7a9e7d37c`
**Runtime-tested HEAD:** `af37fde63c39c6cfd723edb20cf036e3dc276ca8`
**Successful GitHub Actions run:** `31954303962`
**Focused suite:** `70 passed in 0.13s`
**Publish status:** FEATURE BRANCH ONLY; NOT MERGED / NOT DEPLOYED

## Frozen scope implemented

E0-PR-004 implements Excel compatibility infrastructure only:

- immutable `ExcelTemplateProfile` schema;
- required sheet/state requirements;
- cell safety classes;
- normalized formula signatures;
- deterministic sheet-state and formula-signature digests;
- compatibility-transformation metadata;
- external-link classification policy;
- required named/control-range schema;
- workbook fingerprint observation/result contract;
- `UNSUPPORTED_TEMPLATE` fail-closed behavior;
- frozen N08-0038 profile data from the Gate-B fingerprint.

No workbook fill/write implementation, Excel calculation runtime, Golden Fixture Harness, valuation formula, persistence, API, UI, OCR/provider or Epic 1 feature is introduced.

## Implementation files

- `src/re/adapters/excel/profile.py`
- `src/re/adapters/excel/fingerprint.py`
- `src/re/adapters/excel/n08_0038.py`
- `src/re/adapters/excel/__init__.py`

Tests:

- `tests/re/test_excel_template_profile.py`

Evidence:

- `evidence/E0_PR_004_RUNTIME_EVIDENCE_v1.md`
- `evidence/E0-PR-004_tests_v1.log`
- `evidence/E0-PR-004_fingerprint_vectors_v1.log`

## Profile schema

The schema models:

- profile identity/version/source exemplar;
- exact required sheet names and visible/hidden state;
- formula signature cells;
- explicit `CellClass` values (`INPUT`, `FORMULA_PROTECTED`, `OUTPUT_CHECKPOINT`, `CONTROL`, `APPROVAL_RETURN`, `VOLATILE_COMPAT_OVERRIDE`, `UNKNOWN`);
- declared compatibility transformations and their affected cells;
- optional exact alternate formula signatures for approved transformations;
- required named/control ranges when a profile freezes them;
- allowed/warning external-link states;
- source Gate-B SHA-256 values as provenance.

Unknown cells default to `UNKNOWN`; no write permission is inferred from absence of a rule.

## N08-0038 profile data

The implementation carries the frozen Gate-B fingerprint data:

- `profile_id = cenvalue-re-n08-0038-v1`;
- 16 required sheet/state entries;
- 24 required formula signatures;
- source sheet/state SHA-256 `481997e9672fa4fa88a8b00cb677280e72916b5ce29fde0625f508409ab5e951`;
- source formula-checkpoint SHA-256 `05812836786218f2893feeb065e271b515b777aa8b3b5965dcc8c9819a4e2d7d`;
- effective-age/appraisal-date compatibility metadata;
- stale `Phieu TTTT!E5` localization compatibility metadata.

The historical Gate-B SHA values are retained as provenance. E0-PR-004 does not guess the unpublished historical hashing serialization; runtime matching checks the declared structural/formula contract directly and computes deterministic normalized digests using the implementation's documented algorithm.

Gate-B v1 does not enumerate concrete names for required named/control ranges. The schema supports them and matching fails closed whenever a profile declares one; N08 v1 does not invent unnamed controls.

## Formula normalization

`normalize_formula()`:

- canonicalizes a leading `=`;
- removes insignificant whitespace outside quoted literals;
- normalizes case outside quoted literals;
- preserves double-quoted Excel string content exactly;
- preserves quoted sheet-name content exactly;
- preserves locale separators, `$` absolute-reference markers and literal values.

This permits harmless spelling differences while rejecting semantic literal/reference mutations.

Malformed quoted formulas fail closed as `FORMULA_INVALID`; they do not crash the matcher.

## Structural vs metadata policy

Blocking structural checks include:

- missing required sheet;
- required sheet-state mismatch;
- unknown extra sheet when the profile disallows extras;
- missing required formula-signature cell;
- normalized formula mismatch;
- undeclared external-link state;
- missing required named/control range.

Filename is metadata only. Renaming an otherwise compatible workbook produces a warning and cannot establish or defeat template identity.

Sheet order is not used as identity: the frozen minimum contract requires sheet existence/state, and the implementation digest is order-independent. Names/states and the no-extra-sheet rule remain strict.

## Compatibility transformations

A transformation declaration alone does not bypass fingerprint verification.

For a transformed formula to pass with a non-baseline signature, the profile must declare that exact alternate formula for that affected cell. An arbitrary formula in a transformable cell remains `UNSUPPORTED_TEMPLATE`.

This keeps the effective-age transformation metadata extensible without permitting silent formula drift before a concrete transformed signature is frozen.

## External links

For N08-0038:

- `NONE` is supported;
- `KNOWN_STALE_SELF_REFERENCE` is supported with a warning because Gate B explicitly identifies the stale compatibility condition;
- undeclared/unknown external-link states are blocking.

## Runtime evidence

GitHub Actions run `31954303962` checked out exact HEAD `af37fde63c39c6cfd723edb20cf036e3dc276ca8` on Python 3.11.15.

Results:

- compile: PASS;
- bounded scope: PASS;
- `git diff --check`: PASS;
- architecture/import regressions: PASS;
- E0-PR-003 Decimal/RoundingPolicy regressions: PASS;
- E0-PR-004 tests: PASS;
- total: **70 passed in 0.13s**.

Runtime fingerprint vector:

- exemplar status: `MATCHED`;
- exemplar warning: `EXTERNAL_LINK_STATE_WARNING`;
- normalized sheet digest: `5ee6ba3c64b9d29a5d064a051324cc5075dd7515a234d2daae90e8953964a4cc`;
- normalized formula digest: `0ad19b1d66dad2f874b2a1312a1eadaeed9520872aebbf20105e9b8fe190564f`;
- deliberate `Bangtinh!H119` mutation from `-3` to `-4`: `UNSUPPORTED_TEMPLATE` / `FORMULA_SIGNATURE_MISMATCH`.

## Acceptance status

**NOT SELF-ACCEPTED.** E0-PR-004 requires independent review against the exact final PR head. E0-PR-005 must not begin until E0-PR-004 is independently accepted and merged.
