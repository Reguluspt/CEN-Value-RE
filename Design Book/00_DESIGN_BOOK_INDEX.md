# CENVALUE MANAGER REAL ESTATE — DESIGN BOOK v0.1
**Status:** DRAFT / DESIGN-CLOSURE
**Source:** Brainstorm History & Decision Log

## Status
FROZEN = đủ khóa cho planning; REVIEWED = hướng đã thống nhất, còn chi tiết; DRAFT = còn design gap; OPEN = chưa được coding tự quyết.

## Chapters
01 Product Scope — FROZEN
02 System Architecture — REVIEWED
03 Domain Model — DRAFT
04 Case Lifecycle — FROZEN
05 Workbench UX — REVIEWED
06 Property & TSSS — REVIEWED
07 GCN Intelligence — REVIEWED
08 Location & Maps — REVIEWED
09 Construction Valuation — REVIEWED
10 Adjustment Engine — DRAFT
11 Historical Learning — DRAFT
12 Valuation Result — DRAFT
13 Excel Compatibility — DRAFT / RELEASE CRITICAL
14 Approval Round-trip — REVIEWED
15 Security & Privacy — DRAFT
16 Provenance & Audit — REVIEWED
17 Engineering Roadmap — REVIEWED
18 Design Gap Audit — OPEN ACTION LIST

## Global non-negotiables
- Windows Desktop-first, local-first; React + Astryx; Tauri 2 preferred.
- Excel legacy is compatibility/output contract, not the new source of truth.
- Core remains usable without online OCR/Maps/VBDLIS.
- Human controls final adjustment and valuation result.
- Preserve useful Excel muscle memory without cloning hidden spreadsheet logic.
- Trace important data UI ↔ canonical data ↔ Excel.
- GĐ1 data must be structurally ready for GĐ2.
- External/AI output adapts into canonical contracts; it does not define them.
- Delivery uses vertical slices; first skeleton: Manual Case → Adjustment → Result → Excel.
