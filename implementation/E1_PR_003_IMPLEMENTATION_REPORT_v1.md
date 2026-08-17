# E1-PR-003 — Implementation Report v1

**Date:** 2026-08-17
**Repository:** `Reguluspt/CEN-Value-RE`
**Accepted base:** `7e60be157e6b0d5300ffaa8dabac1aadc73f96fb`
**Original reviewed HEAD:** `a558ebd969de227b4433edb0a32333d5babf4667`
**Corrective runtime-tested HEAD:** `2a6361744a78e5ef573682f569bb093c626c2271`
**Binding corrective Windows run:** `32040251279`
**Gate:** `HumanIndicationGate`

## Outcome

E1-PR-003 continues to implement the bounded Epic 1 slice for comparable quality, inclusive 15% readiness, advisory comparable guidance, and explicit human indicated-price confirmation. The targeted corrective loop closes reviewer finding F-01 without redesigning the already-reviewed quality/readiness/freshness/persistence behavior.

## F-01 corrective — trusted template rounding authority

Before correction, `ComparableQualityService` verified that a `TEMPLATE_DEFAULT` policy carried the same profile ID/version as the case but did not verify that its target/mode/increment matched the frozen template profile. A caller could therefore label `10,000 VND` as the N08 template default.

The correction makes the template profile the authority:

1. `ExcelTemplateProfile` now declares immutable `TemplateRoundingDefault` entries.
2. `N08_0038_PROFILE` declares:
   - `UNIT_PRICE`: `NEAREST`, `1,000 VND`;
   - `TOTAL_VALUE`: `NEAREST`, `1,000,000 VND`.
3. `src/re/ports/excel.py` exposes a `TemplateRoundingDefaultResolver` protocol/data record without importing adapters.
4. `src/re/adapters/excel/rounding_defaults.py` resolves supported defaults only from frozen `ExcelTemplateProfile` objects.
5. `ComparableQualityService` receives that resolver through dependency injection and, for `TEMPLATE_DEFAULT`, validates exact profile ID/version, target, mode, and increment. Missing resolver/default or any mismatch fails closed.
6. `CASE_OVERRIDE` remains a separate professional selection path and keeps the required `selected_by` / `selected_at` audit metadata.

There is no hard-coded N08 increment inside the application service and no application-to-adapter dependency.

## Corrective acceptance behavior

- N08 `TEMPLATE_DEFAULT`, `UNIT_PRICE`, `NEAREST`, `1,000` is accepted and `196308350 -> 196308000`.
- N08 `TEMPLATE_DEFAULT` with `NONE` is rejected.
- N08 `TEMPLATE_DEFAULT` with `10,000` is rejected.
- N08 `CASE_OVERRIDE` with `10,000`, actor and timestamp is accepted, persists `CASE_OVERRIDE` provenance, and produces `196310000`.
- Unknown profile/target or missing trusted resolver fails closed.

## Preserved E1-PR-003 behavior

The corrective patch does not alter:

- Decimal comparable quality metrics;
- explicit selected `0%` semantics;
- inclusive 15% readiness;
- unique-minimum-gross advisory recommendation;
- frozen zero-gross average branch;
- equal non-zero tie ambiguity;
- human final-indication authority;
- current E1-PR-002 evidence freshness rules;
- immutable human indication/source evidence;
- semantic SHA reconstruction;
- reconfirmation requirement after source drift/reselection;
- migration v4 or Golden decision provenance.

## Verification

Binding Windows run `32040251279` against corrective runtime HEAD `2a6361744a78e5ef573682f569bb093c626c2271`:

- Windows Server 2025 / Python 3.11.9;
- diff hygiene: PASS;
- compile: PASS;
- full `tests/re`: **212 passed in 3.85s**;
- focused E1-PR-003 corrective: **26 passed in 0.34s**;
- Actions merge-ref `5daa5d6fb4596c2abd34f3a8c97616f7279e828a` tree `ad7af1357666efb189b28070f231ebbbd2e9e056` exactly equals the corrective runtime HEAD tree.

Run `32037927058` is superseded and non-binding because F-01 required implementation/test/profile changes after that run.

## Explicit non-scope

No implementation is claimed for E1-PR-004 final valuation composition, CTXD engine, workbook generation/Excel qualification, OCR/Maps, Historical Learning, approval return/revision, full Astryx workbench, or Epic 1 closure.

The implementer does not self-issue acceptance. PR #13 must be independently re-reviewed on the exact final review HEAD before merge, and E1-PR-004 may begin only from the accepted merge commit.
