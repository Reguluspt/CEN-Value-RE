# CenValue RE — Master Product Roadmap v1

**Status:** APPROVED  
**Approved by:** Project Owner  
**Approval date:** 2026-08-16  
**Scope:** CenValue RE Phase 1 / Release 1.0  

## 1. Product completion definition

CenValue RE 1.0 is complete when a Windows Desktop user can execute the full appraisal loop:

`Create/manage case → TSTĐ → TSSS → CTXD → Adjustment → Valuation Result → Excel approval export → returned approval import → revision/approval → close case`.

The product remains local-first. Excel is a compatibility/output contract, not the canonical domain model. Human approval remains mandatory; AI may assist but may not approve or issue appraisal results.

## 2. Delivery model

Delivery follows vertical slices, not isolated module-first implementation.

Primary dependency chain:

`R0 Repository Baseline → Epic 0 Engineering Foundation → Epic 1 Manual Walking Skeleton → Epic 2 CTXD & Rich Property → Epic 3 GCN/Location → Epic 4 Historical Learning → Epic 5 Lifecycle/Approval Round-trip → Epic 6 Productivity/MVP+ → Epic 7 Pilot Hardening/RC → Excel Qualification PASS → CenValue RE 1.0`

## 3. R0 — Repository Baseline

Objective: establish GitHub as the reviewable engineering source of truth while the Library remains the canonical project workspace/reference corpus.

Exit gate:
- reviewable Design Book, Gate A/B, Epic 0, corrective, fixtures, patches, evidence and reports are present in PR #1;
- sample/reference `*.pdf`, `*.xlsx`, `*.zip` remain Library-only by approved policy;
- `BRAINSTORM Full.md` remains provenance-only in Library;
- integrity is checked against current Library content;
- PR #1 is reviewed and merged before `main` becomes the baseline of record.

## 4. Epic 0 — Engineering Foundation

Objective: create production-grade boundaries without prematurely building appraisal features.

Work sequence:
1. E0-PR-001 — RE Domain Skeleton + Import Boundaries — **ACCEPTED**.
2. E0-PR-002 — Astryx Integration Spike — implementation/static evidence prepared; runtime acceptance pending.
3. E0-PR-003 — Decimal + RoundingPolicy.
4. E0-PR-004 — ExcelTemplateProfile + Fingerprint.
5. E0-PR-005 — Golden Fixture Harness.
6. E0-PR-006 — Local Service Bootstrap Boundary.
7. E0-PR-007 — Encrypted RE Persistence Foundation.
8. E0-PR-008 — Windows Excel Qualification Harness Skeleton.

Epic 0 exit gate:
- architecture boundaries enforced;
- Astryx surface runtime accepted without legacy CSS regression;
- deterministic Decimal/Rounding primitives accepted;
- template fingerprint/fail-safe accepted;
- golden fixture harness operational;
- loopback/session boundary accepted;
- encrypted RE DB/migrations/repository abstraction accepted;
- Excel qualification harness cannot falsely report PASS;
- CI/focused evidence green.

## 5. Epic 1 — Manual Walking Skeleton

Vertical slice:

`Create Case → Manual TSTĐ → Manual TSSS01/02/03 → Market Normalization → Adjustment C1–C11 → Comparable Quality → Human Indicated Price → Land/Valuation Result → Excel Output`

Goals:
- prove canonical case/property/comparable contracts;
- implement deterministic adjustment/calculation engine;
- preserve explicit 0% versus missing;
- calculate comparable quality and 15% readiness control;
- retain human final selection;
- generate workbook through ExcelTemplateProfile.

Golden checkpoints include indicated prices, H119, land total, CTXD total, total before rounding and final rounded value.

Exit gate: canonical engine and required Excel checkpoints agree under declared rounding/tolerance; no hidden workbook behavior becomes canonical by accident.

## 6. Epic 2 — CTXD & Rich Property

Goals:
- zero/one/multiple `ConstructionAsset`;
- legal registration status separate from physical existence;
- `VALUE | DESCRIBE_ONLY | EXCLUDE` treatment;
- appraisal-date effective age;
- age and expert/component remaining-quality methods;
- replacement cost and remaining value;
- same Construction Engine for TSTĐ and TSSS.

Exit gate: representative CTXD scenarios calculate, persist, audit and export correctly.

## 7. Epic 3 — GCN & Location Intelligence

Pipeline:

`Image/PDF → preprocessing → OCR/Vision → semantic parser → staging/reconciliation → human review → canonical property`

Goals:
- OCR/provider abstraction;
- QR best-effort, never workflow-blocking;
- VBDLIS/manual-assisted registry path;
- Google Maps URL → canonical lat/lng with raw URL provenance;
- manual fallback when online services are unavailable.

Exit gate: manual and GCN-assisted creation converge to the same canonical contract after human confirmation.

## 8. Epic 4 — Historical Learning

Pipeline:

`Curated Historical Excel → Template Fingerprint → Deterministic Extraction → Normalized Cases → AdjustmentObservation → Quality Gate → Statistical Similarity → Suggested Rate`

Rules:
- deterministic before AI;
- provenance preserved;
- explicit 0% distinguished from missing;
- suggested rate never overwrites appraiser selection;
- approved/appraiser/suggested lineage retained.

Exit gate: a qualified historical corpus produces reproducible suggestions traceable to source workbooks/cases.

## 9. Epic 5 — Lifecycle & Approval Round-trip

Lifecycle:

`DRAFT → IN_PROGRESS → READY_FOR_APPROVAL → EXPORTED_FOR_APPROVAL → APPROVAL_RETURNED → REVISION_REQUIRED | APPROVED → CLOSED`

Approval flow:

`Export R01 → immutable ApprovalSubmission → returned workbook → profile-matched read → diff → human confirmation → approval/revision → R02...`

Rules:
- returned workbook never blindly overwrites canonical data;
- appraiser and approval decisions remain distinct;
- revision history is immutable;
- changing only final value must not fabricate an adjustment change.

Exit gate: a case completes R01 → returned → revision → R02 → approval → CLOSED with full audit/provenance.

## 10. Epic 6 — Productivity & MVP+ Intelligence

Only after the closed loop is stable:
- advanced Context Drawer;
- copy feature groups between TSSS;
- historical comparable picker;
- advanced keyboard/grid operations;
- advanced GCN reconciliation;
- parcel/location suggestions;
- deeper VBDLIS support;
- AI semantic similarity/explanation;
- approval/prediction analytics where useful.

This epic must not delay the core MVP loop.

## 11. Epic 7 — Pilot Hardening / Release Candidate

No major feature expansion.

Focus:
- SQLCipher-class production binding/distribution;
- document-vault crypto implementation;
- protected secrets/provider retention policy;
- backup/recovery;
- installer/update signing;
- crash/autosave/migration recovery;
- corrupted DB/workbook handling;
- performance with realistic case/TSSS/CTXD/history volumes;
- real-user pilot acceptance;
- production installer/update behavior.

## 12. Mandatory Excel Qualification Gate

Pipeline:

`Canonical Case → CenValue Engine → ExcelTemplateProfile → Generated Workbook → Microsoft Excel Desktop full recalculation → checkpoint readback → tolerance comparison → PASS/BLOCK`

PASS requires:
- matching supported template fingerprint;
- complete required mappings;
- no unknown external dependency;
- canonical calculation success;
- real Excel Desktop recalculation evidence where qualification is required;
- all mandatory checkpoints within frozen tolerance.

No real Excel evidence means qualification must not be reported PASS.

## 13. Release 1.0 Definition of Done

A user can:
- launch the Windows desktop product;
- create/resume multiple cases;
- enter TSTĐ manually or through GCN-assisted staging/review;
- resolve location;
- manage multiple CTXD;
- enter TSSS in practical quick/expanded workflows;
- use historical suggestions while retaining human adjustment authority;
- calculate comparable quality and valuation deterministically;
- choose rounding policy;
- export compatible approval Excel;
- import returned approval workbook;
- handle revisions;
- approve/close the case with full provenance;
- retain structured data ready for later knowledge-base/GĐ2 work.

## 14. Deferred beyond Release 1.0

Not blockers for GĐ1:
- enterprise property/TSSS warehouse;
- advanced GIS intelligence;
- workflow automation/pattern memory;
- CRM/revenue dashboard;
- mobile/web product;
- multi-user collaboration;
- internal OCR server;
- full Company Adjustment Rule Engine runtime.

GĐ1 must remain forward-compatible with these directions without implementing them prematurely.

## 15. Governing principles

- Current Project Owner decision overrides older historical notes.
- Do not reopen frozen Gate A/B decisions without new evidence.
- Every implementation slice requires explicit acceptance evidence.
- Domain logic remains independent of UI/framework/database/Excel/provider APIs.
- External intelligence adapts into canonical contracts; it never defines them.
- Deterministic calculation and Excel compatibility precede AI sophistication.
- Human-in-the-loop remains mandatory for adjustment/final appraisal/approval decisions.
- Core appraisal must remain usable when online providers fail.
- GitHub/VPS publication/deployment remains subject to explicit Project Owner direction.
