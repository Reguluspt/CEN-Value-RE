# CenValue RE — Brainstorm History & Decision Log

**Purpose:** compact decision history retained for provenance. This file is not the primary implementation authority; latest Gate/Design Freeze/PR packets take precedence.

## Core product direction
- Windows desktop/local-first appraisal workbench.
- React + Astryx target UI; Tauri 2 preferred shell.
- Local application service boundary; Flask transitional where useful.
- Canonical domain is framework-independent.
- Excel legacy workbook is compatibility/output contract, not canonical source of truth.
- Deterministic calculation and Excel compatibility precede AI sophistication.
- Human review/approval remains mandatory.

## Phase 1 closed loop
`Create/manage case → TSTĐ → TSSS → CTXD → Adjustment → Valuation Result → Excel approval export → returned approval import → close case`.

## Canonical boundaries
`Case → SubjectProperty(Parcel, Construction[]) + Comparable[](Evidence[], AdjustmentFactor[]) + ValuationResult + AuditTrail`

External/AI outputs adapt through provider/adapter boundaries into frozen canonical contracts; they do not redefine the domain.

## Key decisions
### Astryx
Current legacy CenValue Manager uses React/Vite + Ant Design. Astryx is the target design system for CenValue RE and is introduced gradually on isolated RE surfaces.

### Effective construction age
Legacy workbook behavior: `YEAR(NOW()) - construction_year`.
Canonical CenValue rule: `YEAR(appraisal_date) - construction_year` so closed cases remain reproducible.

### Percentage
Canonical percentages use fractional Decimal representation: `5% = Decimal("0.05")`.

### CTXD
- Legal absence on GCN is not proof of physical absence.
- Multiple CTXD supported.
- `VALUE | DESCRIBE_ONLY | EXCLUDE` treatment.
- TSTĐ and TSSS use the same Construction Engine.

### Adjustment
- C1–C11 factor registry is template/profile-aware.
- `suggested_rate` is separate from `selected_rate`.
- explicit `0%` is a valid selected decision and differs from null/unset.
- historical observations are separate from live AdjustmentDecision.

### Rounding
Keep raw/unrounded and rounded values separately. RoundingPolicy is configurable with template defaults and case-level overrides.

### Excel
- ExcelTemplateProfile identifies supported template family/version, mappings, formula signatures, compatibility transformations and checkpoints.
- Unknown templates fail safe.
- Microsoft Excel Desktop recalculation evidence is required for qualification PASS.
- Known stale external link is localized/internalized through profile rules.

### GCN / OCR / Maps / VBDLIS
- OCR pipeline: image/PDF → preprocess → OCR/Vision → semantic parser → staging/reconciliation → human review → canonical property.
- QR best-effort; failure never blocks workflow.
- Maps URL resolves to canonical lat/lng; raw URL retained for provenance.
- Manual entry remains available when online services fail.

### Historical Learning
User curates historical Excel input first. Pipeline is deterministic extractor → normalized cases → AdjustmentObservation → statistical patterns → optional AI semantic analysis. Deterministic before AI.

### Approval Round-trip
Each export creates immutable ApprovalSubmission snapshot. Returned workbook is profile-matched and diffed; human confirms approval/revision. Never infer adjustment changes from only a changed final value.

## Delivery model
Vertical slices, not isolated module-first delivery.

Walking Skeleton:
`Create Case → Manual TSTĐ → Manual TSSS → Adjustment → Result → Fill Excel`

Epic envelope:
0. Engineering Foundation
1. Manual Walking Skeleton
2. CTXD & rich property
3. GCN/location
4. Historical Learning
5. Lifecycle/Approval Round-trip
6. Productivity/MVP+ intelligence
7. Pilot hardening/Release Candidate

## Governance updates
- Server-first implementation/verification is permitted by latest Project Owner instruction.
- `H:\CEN Manage` is no longer a mandatory gate.
- GitHub/VPS publication still requires explicit Project Owner direction.
- Do not reopen frozen Gate A/B decisions without new evidence.

## Current stage — 2026-08-16
- Gate B: FROZEN/CLOSED.
- Gate C: PASS WITH CORRECTIVE.
- E0-PR-001: independently ACCEPTED after architecture-guard corrective; clean focused suite 6/6 green and mutation proofs reject absolute/relative adapter imports.
- E0-PR-002: Astryx Integration Spike payload/static verification prepared; runtime install/build/browser evidence pending.
- Master Product Roadmap v1 approved by Project Owner.
