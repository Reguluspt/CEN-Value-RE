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

`R0 Repository Baseline → Epic 0 Foundation → Epic 1 Walking Skeleton → Epic 2 CTXD/Rich Property → Epic 3 GCN/Location → Epic 4 Historical Learning → Epic 5 Approval Round-trip → Epic 6 Productivity/MVP+ → Epic 7 Pilot Hardening/RC → Excel Qualification PASS → Release 1.0`.

Every Epic must produce reviewable acceptance evidence. No Epic may silently redefine frozen canonical contracts.

## 3. R0 — Repository Baseline

### Objective
Create a stable GitHub engineering baseline before further implementation expands.

### Deliverables
- Complete PR #1 with reviewable engineering artifacts.
- Keep sample/reference binaries (`*.pdf`, `*.xlsx`, `*.zip`) in the project Library only.
- Version Design Book, Gate A/B, Epic 0 packets, corrective records, fixtures, mappings, patches, logs and reports.
- Merge the approved initial import into `main`.

### Exit gate
- Intended version-controlled project baseline is present in PR #1.
- No unintended PDF/XLSX/ZIP assets are committed.
- PR reviewed and merged.
- `main` becomes the GitHub engineering source-of-truth baseline.

## 4. Epic 0 — Engineering Foundation

### Objective
Build the minimum production-grade foundation without coupling domain logic to legacy Excel, Flask, Tauri, Astryx, database frameworks or provider SDKs.

### Work packages
1. **E0-PR-001 — Architecture Boundary Guard** — ACCEPTED.
2. **E0-PR-002 — Astryx Integration Spike** — implementation/static evidence prepared; runtime acceptance pending.
3. **E0-PR-003 — Decimal + RoundingPolicy**.
4. **E0-PR-004 — ExcelTemplateProfile infrastructure**.
5. **E0-PR-005 — Golden Fixture Harness**.
6. **E0-PR-006 — Local Service Boundary**.
7. **E0-PR-007 — Encrypted Persistence Foundation**.
8. **E0-PR-008 — Windows Excel Qualification Harness**.

### Foundation rules
- `5% = Decimal("0.05")` in the canonical domain.
- Effective construction age uses `appraisal_date`, never `YEAR(NOW())`.
- Preserve raw and rounded valuation results separately.
- Domain imports no React/Astryx, Flask/Tauri, Excel libraries, DB frameworks or provider SDKs.
- Local service is loopback-only with per-launch session/bootstrap credentials.
- RE persistence is separate and encrypted at rest.

### Exit gate
- Architecture guards green.
- Astryx runtime integration accepted.
- Decimal/RoundingPolicy tests green.
- Excel template fingerprinting works and rejects deliberate mutations.
- Golden fixture loads and is testable without requiring Excel for normal unit tests.
- Local service and encrypted persistence baseline accepted.
- CI green.

## 5. Epic 1 — Walking Skeleton: Manual Case → Excel

### Objective
Prove the canonical data model, calculation engine and Excel adapter through one manual end-to-end appraisal flow.

### Flow
`Case Portfolio → Create Case → Manual TSTĐ → Manual TSSS → Market Normalization → Adjustment C1–C11 → Comparable Quality → Valuation Result → Rounding → Excel Output`.

### Required capabilities
- Case creation, autosave, resume and archive.
- Structured TSTĐ entry.
- TSSS Quick/Expanded Entry.
- Market normalization distinct from comparison adjustments.
- Adjustment Engine with explicit-zero semantics.
- Comparable quality metrics and human selection.
- Final valuation with separate before-rounding and final-rounded values.
- Excel output through `ExcelTemplateProfile`.

### Golden acceptance targets
Golden case must reproduce intermediate and final checkpoints, not only the final total, including:
- indicated comparable prices;
- `H119 = 196,308,000`;
- land value `18,428,442,440`;
- raw total `19,581,412,440`;
- rounded total `19,581,000,000`.

### Exit gate
Manual closed calculation loop passes against frozen golden checkpoints and tolerance rules.

## 6. Epic 2 — CTXD & Rich Property

### Objective
Complete physical-property modeling and construction valuation.

### Required capabilities
- Zero, one or multiple `ConstructionAsset` records per property.
- CTXD may be present physically even when absent from GCN.
- Support `VALUE` and `DESCRIBE_ONLY` treatment.
- TSTĐ and TSSS use the same Construction Engine.
- Replacement cost, age method, expert/component method, remaining quality and remaining value.

### Exit gate
Representative CTXD cases persist, calculate and export correctly and match Excel checkpoints.

## 7. Epic 3 — GCN / Document Intelligence & Location

### Objective
Reduce manual input while preserving deterministic canonical contracts and human confirmation.

### GCN pipeline
`Image/PDF → Preprocess → OCR/Vision → Semantic Parser → Staging/Reconciliation → Human Review → Canonical Property`.

### Rules
- OCR output never writes directly to canonical data.
- QR is best-effort and never blocks workflow.
- VBDLIS is a provider/source, not an unquestioned source-of-truth.
- Conflicts require reconciliation and human review.
- Manual entry must remain available when OCR/provider/network fails.

### Location
`Google Maps URL → resolver → latitude/longitude`, preserving raw URL for provenance.

### Exit gate
Manual and GCN-assisted intake converge to the same canonical property contract after confirmation.

## 8. Epic 4 — Historical Learning

### Objective
Generate reproducible adjustment suggestions from curated historical appraisal workbooks.

### Pipeline
`Curated Historical Excel → Template Fingerprint → Deterministic Extractor → Normalized Cases → AdjustmentObservation → Quality Gate → Statistics/Similarity → Suggested Rate`.

### Rules
- Deterministic before AI.
- Preserve workbook/case provenance.
- Distinguish explicit `0%` from missing/unfilled values.
- `suggested_rate` and appraiser `selected_rate` are distinct.
- Later approval lineage preserves suggested → appraiser → approved values where supported.

### Minimum suggestion evidence
- suggested rate;
- sample size;
- median;
- P25/P75;
- confidence/quality metadata;
- dataset snapshot/version;
- source provenance.

### Exit gate
At least one curated historical corpus produces reproducible suggestions traceable to source workbooks/cases.

## 9. Epic 5 — Case Lifecycle & Approval Round-trip

### Objective
Close the real operational appraisal workflow.

### Lifecycle
`DRAFT → IN_PROGRESS → READY_FOR_APPROVAL → EXPORTED_FOR_APPROVAL → APPROVAL_RETURNED → REVISION_REQUIRED | APPROVED → CLOSED`.

### Approval flow
`Export R01 → immutable ApprovalSubmission → returned workbook → matching TemplateProfile read → diff → human confirmation → approve or revise`.

### Rules
- Every export keeps immutable revision, timestamp, workbook/template identity and submitted snapshots.
- Returned workbooks never blindly overwrite canonical data.
- Appraiser and approval decisions remain separate.
- If only final result changes, do not invent an adjustment change.
- Revision chain R01 → Returned → R02... remains auditable.

### Exit gate
A real case can complete export, returned approval, revision and final close without losing provenance or revision history.

## 10. Epic 6 — Productivity & MVP+ Intelligence

### Objective
Improve expert productivity after the core closed loop is stable.

### Candidate capabilities
- Advanced Context Drawer.
- Copy comparable feature groups.
- Historical comparable picker.
- Keyboard/grid productivity.
- Advanced GCN reconciliation.
- Parcel/location assistance.
- Advanced VBDLIS integration.
- AI semantic similarity and explanations.
- Approval analytics.

### Rule
This Epic must not delay the core MVP closed loop.

## 11. Epic 7 — Pilot Hardening & Release Candidate

### Objective
Turn the feature-complete MVP into a releasable Windows product without major feature expansion.

### Security / operations
- Final SQLCipher-class binding and packaging.
- Document/evidence encryption implementation.
- Windows user-scoped protected key handling.
- Provider secret/retention policy.
- Encrypted backup and recovery design.
- Installer/update signing.

### Reliability
- Autosave and crash recovery.
- Database migration/rollback discipline.
- Corrupt DB/workbook handling.
- Source artifact hashing and provenance consistency.
- Structured error handling and log redaction.

### Performance
Validate representative loads for many cases, TSSS, CTXD, historical corpora, workbook generation and document batches.

### Pilot UX
Run real-user workflows from create case through approval/close with appraisal staff.

### Exit gate
Pilot acceptance criteria pass; no release-critical defects remain.

## 12. Excel Qualification — Mandatory Release Gate

### Role
Excel remains the Phase 1 approval/output compatibility contract and migration oracle; CenValue canonical calculation is the source of truth.

### Qualification pipeline
`Canonical Case Snapshot → TemplateProfile validation → fill mapped inputs → sanitize known external-link exceptions → preserve formulas/layout → Microsoft Excel Desktop full recalculation → read checkpoints → compare with CenValue Engine → PASS/BLOCK`.

### PASS requires
- matching fingerprint;
- complete required mappings;
- no unknown external dependency;
- successful canonical calculation;
- real Excel Desktop recalculation/verification when required;
- all required checkpoints within frozen tolerance.

No Excel Desktop recalculation evidence means qualification may be pending, but must not be reported as PASS.

## 13. Release 1.0 Definition of Done

A Windows user can:

`Launch → Create/Resume Case → Manual or GCN-assisted TSTĐ → Location → Multiple CTXD → TSSS → Market Normalization → Historical Suggestion → Human Adjustment → Comparable Quality → Valuation Result → Rounding → Excel Export → Approval Return → Diff/Human Confirmation → Revision if required → APPROVED → CLOSED`.

Release 1.0 additionally requires:
- encrypted local persistence;
- auditable provenance;
- human approval boundary;
- stable autosave/resume;
- Excel compatibility qualification PASS;
- pilot hardening and installer readiness.

## 14. Explicitly deferred beyond Release 1.0

The following are not release blockers for Phase 1:
- enterprise property/TSSS warehouse;
- advanced GIS intelligence;
- autonomous workflow automation;
- CRM/revenue dashboards;
- mobile/web clients;
- multi-user collaboration;
- internal OCR server;
- full Company Adjustment Rule Engine runtime.

Phase 1 must preserve forward-compatible structured data so these capabilities can be added later without destructive redesign.

## 15. Governance

- One Epic/PR scope at a time.
- Evidence before acceptance.
- Independent review where required.
- No self-declared PASS for gated work.
- Corrective loops address specific findings without reopening frozen discovery/design unless a blocker proves the frozen contract invalid.
- GitHub stores reviewable engineering source-of-truth; Library retains reference/sample binary corpus and working artifacts that are intentionally excluded from Git.
