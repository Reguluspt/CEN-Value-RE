# E1-PR-003 — Runtime Evidence v1

**Date:** 2026-08-17
**Repository:** `Reguluspt/CEN-Value-RE`
**Accepted base:** `7e60be157e6b0d5300ffaa8dabac1aadc73f96fb`
**Original reviewed HEAD:** `a558ebd969de227b4433edb0a32333d5babf4667`
**Corrective runtime-tested implementation HEAD:** `2a6361744a78e5ef573682f569bb093c626c2271`
**Binding corrective GitHub Actions run:** `32040251279`
**Gate:** `HumanIndicationGate`

## 1. Binding environment and result

Run `32040251279` completed SUCCESS on Microsoft Windows Server 2025 with CPython `3.11.9`.

- dependency install: PASS;
- `git diff --check 7e60be157e6b0d5300ffaa8dabac1aadc73f96fb..HEAD`: PASS;
- `python -m compileall -q src/re`: PASS;
- full `tests/re`: **212 passed in 3.85s**;
- focused E1-PR-003 corrective suite: **26 passed in 0.34s**.

Runtime dependencies included Flask `3.1.1`, sqlcipher3 `0.6.2`, pywin32 `312`, and pytest `9.1.1`.

GitHub Actions checked out PR merge-ref `5daa5d6fb4596c2abd34f3a8c97616f7279e828a`. Its tree SHA is `ad7af1357666efb189b28070f231ebbbd2e9e056`, exactly equal to corrective runtime-tested branch HEAD `2a6361744a78e5ef573682f569bb093c626c2271` tree SHA `ad7af1357666efb189b28070f231ebbbd2e9e056`.

## 2. Corrective finding F-01 evidence

Independent review returned one HIGH finding: caller-supplied `TEMPLATE_DEFAULT` provenance could previously carry an N08 profile ID/version while supplying a non-profile increment such as `10,000`, producing `196310000` instead of the frozen N08 default `196308000`.

The corrective implementation now:

- declares rounding defaults inside the trusted `ExcelTemplateProfile` definition;
- declares N08-0038 `UNIT_PRICE = NEAREST / 1,000 VND` and `TOTAL_VALUE = NEAREST / 1,000,000 VND` in `N08_0038_PROFILE`;
- exposes trusted profile defaults to the application through `TemplateRoundingDefaultResolver` in the Excel port, preserving the core-to-adapter boundary;
- requires `ComparableQualityService` to resolve `TEMPLATE_DEFAULT` against the trusted case profile;
- validates exact profile ID/version, target, mode, and increment;
- fails closed if no trusted resolver/default exists or any field differs;
- preserves `CASE_OVERRIDE` behavior with actor/time audit metadata.

Regression proof includes:

- N08 + `TEMPLATE_DEFAULT` + `1,000` accepted and Golden `196308350 -> 196308000` preserved;
- N08 + `TEMPLATE_DEFAULT` + `NONE` rejected;
- N08 + `TEMPLATE_DEFAULT` + `10,000` rejected;
- N08 + `CASE_OVERRIDE` + `10,000` with actor/time accepted and persisted as `196310000` with `CASE_OVERRIDE` provenance;
- resolver absence/unknown profile/unknown target fails closed;
- architecture guard remains green, so application/ports do not import Excel adapters.

## 3. Previously accepted behavior preserved

The binding run continues to cover comparable quality, inclusive 15% readiness, advisory recommendation, frozen zero-gross average behavior, human authority, current-adjustment freshness, immutable human-indication evidence, semantic SHA reconstruction, source-drift/reselection reconfirmation, and Golden E1-PR-002 provenance without change.

Golden outputs remain:

- TSSS01 indicated `196308350`;
- TSSS02 indicated `227083250`;
- TSSS03 indicated `212201640`;
- selected/raw human indication `196308350`;
- N08 trusted template-default rounded indication `196308000`.

## 4. Superseded evidence

Run `32037927058` and runtime HEAD `c8fd43df4b2f15be430ae2a5dcc9c4f151caba33` are superseded by the F-01 corrective changes and are no longer binding for acceptance.

Only run `32040251279` binds the corrective implementation.

## 5. Claim boundary

This evidence supports only E1-PR-003 / `HumanIndicationGate`. It does not claim E1-PR-004 final valuation composition, CTXD engine, workbook generation, Microsoft Excel qualification, OCR/Maps, Historical Learning, approval round-trip, full Astryx workbench, or Epic 1 closure.

## 6. Post-test binding rule

After corrective runtime-tested HEAD `2a6361744a78e5ef573682f569bb093c626c2271`, only evidence/report/handoff updates and removal of `.github/workflows/e1-pr-003-corrective-verify.yml` may be present before independent re-review.

Any post-test change to source, tests, profile definition, ports, domain/application contract, persistence behavior, Golden values, dependencies, or runtime-bearing configuration invalidates run `32040251279` and requires a new full Windows run.
