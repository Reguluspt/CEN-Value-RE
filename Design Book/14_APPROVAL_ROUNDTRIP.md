# 14 — Approval Round-trip
**Status: REVIEWED**

Each export creates immutable `ApprovalSubmission` with revision, timestamp, workbook/template identity, submitted case/adjustment/result snapshot and artifact.

Returned workbook is read through matching template profile and diffed against submitted snapshot; never blindly overwrite. Human confirmation gates canonical approval. Keep appraiser and approval decisions separately. Revisions R01→Returned→R02... are immutable. If only final result changes, do not invent an adjustment change.
