# CenValue RE — Workspace Baseline Manifest

**Baseline date:** 2026-08-16  
**Library workspace:** `/CEN Value RE`  
**Pre-corrective unique file count:** 75  
**Duplicate policy:** byte-identical duplicates removed; one canonical copy retained.

## Workspace areas
Existing source areas:
- `/CEN Value RE/Design Book`
- `/CEN Value RE/gate-a`
- `/CEN Value RE/gate-b`
- `/CEN Value RE/epic-0`
- `/CEN Value RE/audits`

Controlled working/output areas created on 2026-08-16:
- `/CEN Value RE/corrective`
- `/CEN Value RE/implementation`
- `/CEN Value RE/evidence`
- `/CEN Value RE/fixtures`
- `/CEN Value RE/reports`

## Authority chain
1. Latest explicit Project Owner decision.
2. Latest Gate closure / Design Freeze / Decision Revision.
3. Current Design Book.
4. Specialized Gate-B contracts.
5. Brainstorm History only for provenance/conflict investigation.
6. Legacy workbook as compatibility evidence, not application architecture.

## Critical baseline SHA-256
| Artifact | SHA-256 |
|---|---|
| N08 exemplar workbook | `d410cfcc2263d7d50a436a79e192461f04b6863e6c3676a28da7a2eed287389c` |
| `CENVALUE_RE_SESSION_HANDOFF_2026-08-16.md` | `dc980a3c88e1b445ee013e79ca93b0fce5bdd112baf611c43f53e78dceb56d9e` |
| `GATE_B_CLOSURE_REPORT_v1.md` | `5325b1f84ba880c501408eae12d992ab3528a004c795fed357c0dccf991c8b60` |
| `EPIC_0_PR_PLAN_v1.md` | `c1cb3c499c18552379fee425c28b717c922fc20ca5510c668925b3e5b653dc74` |
| `EPIC_0_ACCEPTANCE_MATRIX_v1.md` | `3c119fbade81a1a92a25e83d4db127417f5c7f4d99d2e93792df074632690880` |
| Original `E0-PR-001_SERVER_IMPLEMENTATION.zip` | `502f377fd96df6db6a4c10bc749adf59549691bd5fdd3d247200337c2c74660b` |

## Baseline rule
All subsequent corrective/implementation artifacts must be stored inside `/CEN Value RE` and reference this baseline or a later explicitly versioned baseline. Original evidence artifacts are retained unless a canonical document is intentionally corrected in place with a recorded corrective report.
