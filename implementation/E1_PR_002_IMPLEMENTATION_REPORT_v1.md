# E1-PR-002 — Implementation Report v1

**Date:** 2026-08-17  
**Repository:** `Reguluspt/CEN-Value-RE`  
**Accepted base:** `c4e5753c328443e63ce474c03ecbbbf31a2370ed`  
**Runtime-tested HEAD:** `83f742baf42b9f56c887b80c38b15972f22650a4`

## Outcome

E1-PR-002 implements the bounded Epic 1 market-normalization and C1–C11 adjustment slice without pulling forward comparable-quality, final-indication, final-valuation, CTXD-engine, workbook-generation, OCR/Maps, Historical Learning, approval-round-trip, or workbench scope.

## Implemented capability

- exact frozen N08 C1–C11 factor registry and order;
- Decimal-only market normalization and comparable land-unit base calculation;
- supplied/precomputed construction value accepted only as an upstream boundary input;
- frozen adjustment dependency graph with C3–C11 adjustment amounts based on `P1`;
- explicit selected zero distinct from missing/unreviewed;
- human-selected rate application service with actor/time/source-revision audit metadata;
- source-data drift safety that marks decisions stale without overwriting professional selections;
- complete/current/source-revision decision gate before calculation;
- deterministic SHA-bound calculation snapshots;
- encrypted-persistence migration v3 for selection audit and calculation snapshots;
- case/comparable/decision lineage guards;
- provenance-complete Golden C1–C11 decision fixture extracted from the exact N08 source workbook.

## Golden fixture closure

The previous canonical Golden Fixture gap for missing explicit C1–C11 decisions is closed for the N08 exemplar by `fixtures/GOLDEN_CASE_ADJUSTMENT_DECISIONS_v1.json`.

The fixture uses 33 direct stored cells from `Bangtinh!F/G/H` rows `55..105` according to the frozen factor-row registry. Source workbook SHA-256 is `d410cfcc2263d7d50a436a79e192461f04b6863e6c3676a28da7a2eed287389c`.

The extracted decisions reproduce the three frozen indicated-price checkpoints exactly:

- `F108 = 196308350`;
- `G108 = 227083250`;
- `H108 = 212201640`.

No expected output was used as decision authority.

## Architecture

Domain calculation remains framework-independent and imports no Flask, SQLCipher, Excel, Astryx, Tauri, or provider SDK.

Application orchestration depends on framework-independent persistence ports. Concrete SQLCipher repositories remain in the adapter layer. Human-selection audit is kept separately from the current-state decision row so historical selection evidence is not collapsed into mutable current state.

## Persistence

Migration v3 adds:

- adjustment-decision case/comparable lineage triggers;
- append-only-by-repository `adjustment_selection_audit` records;
- immutable-by-repository `adjustment_calculation_snapshot` records;
- audit/snapshot lineage triggers and indexes.

The existing E1-PR-001 manual-data schema and behavior remain forward-compatible; its migration-v2 regression test continues to inspect v2 exactly while allowing later strictly ordered migrations.

## Verification

Binding Windows run `32009934815` on exact runtime-tested HEAD `83f742baf42b9f56c887b80c38b15972f22650a4`:

- diff hygiene PASS;
- compile PASS;
- full `tests/re`: **177 passed in 3.21s**;
- focused E1-PR-002: **27 passed in 0.13s**.

Run `32009701673` is explicitly superseded; it exposed two stale schema-version assertions and is not acceptance evidence.

## Acceptance boundary

The requested gate is E1-PR-002 `AdjustmentCalculationGate` only. The implementer does not self-issue `ACCEPTED`.
