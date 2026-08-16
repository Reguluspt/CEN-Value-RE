# CenValue RE — Corrective Register 2026-08-16

**Mode:** targeted corrective; no Gate A/B rediscovery or redesign.

## DOC-01 — Percentage canonical representation
**Status:** CORRECTED IN CANONICAL DOCUMENTATION  
**Authority:** Session Handoff audit corrective FIND-E0-01 + verified workbook storage.

Canonical rule:
- `5% = Decimal("0.05")`
- `-5% = Decimal("-0.05")`
- canonical `*_pct` values are fractions; presentation/Excel adapters convert display representation.

Updated in place:
- `gate-a/GATE_A3_CANONICAL_SCHEMA_V1.md`
- `Design Book/03_DOMAIN_MODEL.md`

## DOC-02 — Effective age reference date
**Status:** AUTHORITY CLARIFIED  
**Authority:** `gate-b/DECISION_REVISION_APPRAISAL_DATE_EFFECTIVE_AGE.md`.

Canonical rule:
`effective_age_years = YEAR(appraisal_date) - construction_year`

The legacy `YEAR(NOW())` formula is retained only as workbook evidence. `GATE_B1_CTXD_CALCULATION_CONTRACT_v0.1.md` now explicitly marks its old unresolved item as historical.

## DOC-03 — Historical Gate-B open/blocker wording
**Status:** AUTHORITY MARKERS ADDED

Historical v0.1 contracts were not rewritten. A superseded/current-authority marker was added to:
- `GATE_B1_CTXD_CALCULATION_CONTRACT_v0.1.md`
- `GATE_B2_ADJUSTMENT_MAPPING_AND_CALCULATION_v0.1.md`
- `GATE_B3_INDICATED_PRICE_SELECTION_v0.1.md`
- `GATE_B7_FINAL_VALUATION_CONTRACT_v0.1.md`

This prevents resolved items from being treated as current blockers while preserving provenance.

## DOC-04 — Design Book entry point
**Status:** CORRECTED

`Design Book/00_DESIGN_BOOK_INDEX.md` now identifies Gate B as frozen/closed and Epic 0 as ready, while preserving the historical chapter labels and stating the source-of-truth order.

## E0-PR-001-C01 — Architecture import guard false negative
**Status:** CLOSED — INDEPENDENTLY ACCEPTED

Finding: original guard could miss `src.re.adapters` and relative adapter imports.

Corrective:
- canonicalize `src.re.*` to `re.*`;
- resolve relative imports;
- include imported aliases in dependency targets;
- add guard self-tests and false-positive control.

Evidence:
- baseline focused suite: 4 passed;
- corrected focused suite: 6 passed;
- `from src.re.adapters import persistence` mutation fails the architecture test;
- `from ...adapters import persistence` mutation fails the architecture test;
- tree restored and final suite returns 6 passed.

Independent reviewer verdict on 2026-08-16: **ACCEPTED**. The implementer evidence remains non-self-approving; closure authority comes from the independent review verdict.

## Security report correction
The earlier operational concern about the sample PDF/workbook archive being unencrypted is **withdrawn for this review**, based on the Project Owner's clarification that the supplied files are test/sample data and do not create an information-security exposure in this context. The product security baseline itself is unchanged.

## FIX-01 — Golden fixture canonical normalization
**Status:** NORMALIZED v1 CREATED; INPUT COVERAGE STILL PARTIAL

Created `fixtures/GOLDEN_CASE_CANONICAL_FIXTURE_v1.json` from the legacy extracted fixture without deleting raw evidence. Normalizations include ISO appraisal date, fractional Percentage semantics, profile-selector raw/canonical separation, and cleanup of known binary-float cache artefacts. Missing C1-C11 decisions and construction-component observations remain explicitly open rather than being invented.

## WB-01 — Engineering unlocked copy
**Status:** PENDING TOOL-SAFE EXPORT

The canonical workbook remains unchanged at project root. The required spreadsheet engine (`artifact_tool`) currently fails transport while importing this 13,689-formula workbook. No OOXML patch or alternate-library rewrite was used, and no file has been falsely labeled “unlocked”. Resume only when the workbook can be imported/exported through the approved spreadsheet tool with post-export verification.

## DOC-05 — Governance source-of-truth alignment
**Status:** CORRECTED

The latest Project Owner/session handoff permits server-first implementation/verification and states that `H:\CEN Manage` is no longer a mandatory gate. Historical Epic 0 documents still recorded the older local-first requirement. Supersession markers were added to:
- `epic-0/EPIC_0_PR_PLAN_v1.md`;
- `epic-0/EPIC_0_DESIGN_FREEZE_v1.md`.

The no-publish/no-GitHub-or-VPS-without-explicit-owner-direction rule remains unchanged.

`CENVALUE_RE_SESSION_HANDOFF_2026-08-16.md` was also advanced to the current E0-PR-001 corrective state: 6/6 focused tests + mutation proof, Review/Acceptance still pending.


## E0-PR-001 Stage Gate Closure
**Status:** ACCEPTED / CLOSED  
**Date:** 2026-08-16

Independent review accepted DOC-01 through DOC-05, FIX-01 and the E0-PR-001 architecture-boundary corrective. E0-PR-002 — Astryx Integration Spike is authorized to begin. No GitHub/VPS publication is authorized by this closure.
