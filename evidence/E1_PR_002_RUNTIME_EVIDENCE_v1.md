# E1-PR-002 — Runtime Evidence v1

**Date:** 2026-08-17
**Repository:** `Reguluspt/CEN-Value-RE`
**Accepted base:** `c4e5753c328443e63ce474c03ecbbbf31a2370ed`
**Original review HEAD:** `e197ab72a65fe3c2308cad2d866eba704b7e3424`
**Corrective-1 review HEAD:** `78cd4c08ba1d6e4d52d8809655deb8316125f55c`
**Corrective-2 runtime-tested HEAD:** `0bfa7fef058541d93d5e546ea874325012cef140`
**Binding corrective-2 GitHub Actions run:** `32030676413`
**Runner:** Microsoft Windows Server 2025
**Python:** `3.11.9`

## 1. Binding result

Run `32030676413` completed successfully with branch head `0bfa7fef058541d93d5e546ea874325012cef140`.

- dependency install: PASS;
- diff hygiene: PASS;
- source compile: PASS;
- full `tests/re`: **186 passed in 3.13s**;
- focused E1-PR-002 corrective-2 suite: **36 passed in 0.20s**.

Runtime dependencies remained Flask `3.1.1`, sqlcipher3 `0.6.2`, pywin32 `312`, and pytest `9.1.1`.

## 2. Corrective-2 finding coverage

### E1PR002-IR-001 — material P0 rebind

A first P0/evidence binding attaches to the current authoritative source revision. Repeating the identical binding is idempotent. A materially different P0/evidence binding atomically advances source revision, preserves selected rates, marks CURRENT C1–C11 decisions `SOURCE_DATA_CHANGED`, appends drift audit evidence, and blocks calculation until human reselection on the new revision.

### E1PR002-IR-004 — immutable source-drift audit

Canonical comparable/market-observation/characteristic drift now appends `SOURCE_DATA_CHANGED` audit evidence with `SYSTEM_SOURCE_DRIFT`, timestamp and the authoritative revision at the stale transition, in the same transaction that advances source state and stales CURRENT decisions. Direct single-source mutation proof verifies the audit revision equals the new authoritative revision. A composite `save_comparable()` may contain several canonical low-level mutations; its immutable audit records retain the exact revision at which the decision first became stale while later source mutations may further advance the current revision.

### E1PR002-IR-005 — reproducible snapshot semantic SHA

`normalized_base_evidence_ref` is persisted as immutable calculation-snapshot content. The canonical semantic payload can be reconstructed from persisted snapshot fields alone, and its SHA-256 reproduces the stored `semantic_sha256` both before and after current source state is advanced/rebound.

## 3. Previously closed behavior preserved

Corrective-2 does not weaken IR-002 concurrency/CAS protection or IR-003 immutable decision lineage. Frozen C1–C11 ordering, Decimal-only arithmetic, explicit-zero semantics, human authority, P0/P1 dependency graph, CTXD boundary and Golden workbook provenance/output reproduction remain unchanged.

## 4. Corrective-2 run history

- `32030234190`: superseded/non-binding; 167 passed / 19 failed because the migration-result helper incorrectly indexed a dict row with `row[0]`.
- `32030440283`: superseded/non-binding; 185 passed / 1 failed because the composite-save integration test incorrectly required the stale-transition audit revision to equal the final revision after multiple low-level mutations.
- `32030676413`: **binding corrective-2 run**; 186/186 full and 36/36 focused PASS.

Earlier pre-corrective runs remain superseded.

## 5. Claim boundary

This evidence supports only E1-PR-002 / `AdjustmentCalculationGate`. It does not claim Comparable Quality / 15%, Human Indication, Final Valuation Composition, CTXD engine, workbook generation, Microsoft Excel qualification, or Epic 1 closure.

## 6. Binding rule

Any source, test, migration, fixture decision value, calculation contract, source-state contract, audit behavior, snapshot semantics, concurrency behavior, or persistence behavior change after corrective-2 runtime-tested HEAD `0bfa7fef058541d93d5e546ea874325012cef140` requires a new full Windows run before acceptance.

Evidence/report/handoff updates and removal of the one-time corrective-2 verifier may form the post-test review delta only when they do not alter implementation-bearing behavior.
