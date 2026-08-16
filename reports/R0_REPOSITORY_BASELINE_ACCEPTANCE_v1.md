# CenValue RE — R0 Repository Baseline Acceptance v1

**Date:** 2026-08-16  
**Gate:** R0 — Repository Baseline / Initial Import  
**Repository:** `Reguluspt/CEN-Value-RE`  
**Pull Request:** #1 — `agent/initial-project-import` → `main`  
**Verdict:** **CONTENT-INTEGRITY PASS / ACCEPTED FOR REVIEW**

## 1. Source snapshot

Canonical source at the start of the R0 acceptance run: ChatGPT Library workspace `/CEN Value RE`.

- Library files in snapshot: **103**
- Intentionally excluded by approved repository policy: **15**
  - 10 sample/reference PDF files
  - 1 sample Excel workbook (`*.xlsx`)
  - 3 packaged implementation archives (`*.zip`)
  - `BRAINSTORM Full.md` provenance-only archive
- Reviewable/version-controlled target: **88 files**

Excluded files remain in the project Library and are not missing GitHub deliverables.

## 2. Library integrity verification

All 88 reviewable files were materialized directly from their **current Library versions** before final Git tree creation.

Initial comparison against the older import staging copy found **9 stale files**:

1. `Design Book/00_DESIGN_BOOK_INDEX.md`
2. `Design Book/03_DOMAIN_MODEL.md`
3. `gate-a/GATE_A3_CANONICAL_SCHEMA_V1.md`
4. `epic-0/EPIC_0_DESIGN_FREEZE_v1.md`
5. `epic-0/EPIC_0_PR_PLAN_v1.md`
6. `gate-b/GATE_B1_CTXD_CALCULATION_CONTRACT_v0.1.md`
7. `gate-b/GATE_B2_ADJUSTMENT_MAPPING_AND_CALCULATION_v0.1.md`
8. `gate-b/GATE_B3_INDICATED_PRICE_SELECTION_v0.1.md`
9. `gate-b/GATE_B7_FINAL_VALUATION_CONTRACT_v0.1.md`

The stale staging copies were replaced from current Library bytes and the comparison was re-run.

**Final Library ↔ staging result: 88/88 SHA-256 matches; 0 mismatches.**

## 3. GitHub import verification

Final canonical import commit:
`6135e039bf918461cae386e9953af54bb1168619`

PR #1 changed-file inventory after the canonical import commit:
- expected reviewable files: **88**
- observed changed files: **88**
- forbidden `*.pdf`: **0**
- forbidden `*.xlsx`: **0**
- forbidden `*.zip`: **0**
- forbidden `BRAINSTORM Full.md`: **0**

The approved compact decision history `CENVALUE_RE_BRAINSTORM_HISTORY.md` is included.

## 4. Critical remote blob verification

The files most exposed to stale-version or transport risk were checked against Git blob SHA derived from current Library bytes.

| File | Expected / observed Git blob SHA | Result |
|---|---|---|
| `Design Book/00_DESIGN_BOOK_INDEX.md` | `66f504e21b5e94c9d10ebcfcd80c3a6c8dbbf634` | MATCH |
| `Design Book/03_DOMAIN_MODEL.md` | `e104ab384de2ef974371137b0bed872cb8a0ea92` | MATCH |
| `gate-a/GATE_A3_CANONICAL_SCHEMA_V1.md` | `5f7a12265e6bc114d34ccf97293b1cd7fc2baed6` | MATCH |
| `epic-0/EPIC_0_DESIGN_FREEZE_v1.md` | `bce97b4bb4882a5f903da98789d8542e3b1fd4ca` | MATCH |
| `epic-0/EPIC_0_PR_PLAN_v1.md` | `67bbe5798bf7cb123ff752ab9e157d5b9ad91a99` | MATCH |
| `gate-b/GATE_B1_CTXD_CALCULATION_CONTRACT_v0.1.md` | `da7205eb425f93536cf371186aa008c178a3a303` | MATCH |
| `gate-b/GATE_B2_ADJUSTMENT_MAPPING_AND_CALCULATION_v0.1.md` | `d25d190a19f20ef9d008a3eb638903bb872e23db` | MATCH |
| `gate-b/GATE_B3_INDICATED_PRICE_SELECTION_v0.1.md` | `bda50ae195db1d6289a71dafb8e2a6690756b4ef` | MATCH |
| `gate-b/GATE_B7_FINAL_VALUATION_CONTRACT_v0.1.md` | `87b8e1a071d406695b17269b5682d715133aae2d` | MATCH |
| `CENVALUE_RE_BRAINSTORM_HISTORY.md` | `00514839f7c23230b24a2b6db643ac3ed22feb87` | MATCH |
| `gate-b/CENVALUE_RE_WORKBOOK_MAPPING_MATRIX_v0.1.csv` | `397bd9f195b5fe05cfa0f2d8cec07b71cd35893f` | MATCH |

The critical corrected contracts preserve the current authority rules, including fractional Percentage (`Decimal("0.05") = 5%`), appraisal-date effective-age authority, governance supersession, and historical/superseded markers.

## 5. Baseline content gate verdict

**R0 repository baseline content is accepted for review.**

The import is complete for the approved GitHub scope and passes the content/integrity policy. PR #1 may be moved from Draft to **Ready for Review**.

This verdict does **not** merge the PR and does not claim R0 is merged into `main`. R0 becomes the repository baseline of record only after PR #1 receives the required review/owner decision and is merged.

## 6. Next gate

After PR #1 review/merge, resume the approved Master Product Roadmap at Epic 0, with E0-PR-002 runtime acceptance as the active engineering gate.
