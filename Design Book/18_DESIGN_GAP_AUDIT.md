# 18 — Design Gap Audit v0.1
**Status: OPEN ACTION LIST**

## Gate A — close before Epic 0 contract freeze
1. Repository/reuse audit of existing CenValue Manager source.
2. Runtime boundary: Tauri/Rust vs embedded/local FastAPI + IPC/API.
3. Persistence/security: DB, encryption, keys, vault, migrations.
4. Canonical schema v1 field-level contracts.
5. Units/decimal/currency/percentage precision.

## Gate B — close before Epic 1 acceptance
6. Full workbook mapping matrix.
7. Exact calculation sequence/formulas/rounding/tolerance.
8. Excel recalculation/verification strategy.
9. Template fingerprint/family contract.
10. Walking Skeleton real-case acceptance fixtures/checkpoints.

## Gate C — close before relevant intelligence epics
11. GCN schema/OCR provider/retention/reconciliation.
12. VBDLIS provider/manual-assisted boundary.
13. Maps/embed/admin-address source.
14. Historical similarity/quality/statistics/confidence/dataset versioning.
15. Approval returned-workbook mapping/change classification.

## Inconsistencies to normalize
- Older model used singular `Building`; current contract requires `ConstructionAsset[]`.
- Older comparable model had generic Evidence; GĐ1 later narrows price workflow and avoids heavy evidence subsystem.
- Earlier brainstorm mentioned adjustment override reason; current desired UX needs explicit freeze decision before schema finalization.
- Brainstorm History header/version metadata is stale relative to appended decisions; normalize metadata without deleting history.

## Closure order
`Repository/Runtime → Canonical Schema → Workbook Mapping → Calculation/Excel → Security → GCN/Maps → Historical Learning → Approval`

**Assessment:** product/high-level architecture is mature enough for Design Book v0.1. Do not start coding until Gate A closes; do not declare Epic 1 ready until Gate B closes.
