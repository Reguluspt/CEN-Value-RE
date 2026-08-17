# E1-PR-002 — Runtime Evidence v1

**Date:** 2026-08-17
**Repository:** `Reguluspt/CEN-Value-RE`
**Accepted base:** `c4e5753c328443e63ce474c03ecbbbf31a2370ed`
**Original review HEAD:** `e197ab72a65fe3c2308cad2d866eba704b7e3424`
**Corrective runtime-tested HEAD:** `74670edb9c5ece5cbd94706808272d6e08a2ee57`
**Binding corrective GitHub Actions run:** `32017538546`
**Runner:** Microsoft Windows Server 2025
**Python:** `3.11.9`

## 1. Binding result

Run `32017538546` completed SUCCESS against corrective implementation HEAD `74670edb9c5ece5cbd94706808272d6e08a2ee57`.

- dependency install: PASS;
- `git diff --check c4e5753...HEAD`: PASS;
- `python -m compileall -q src/re`: PASS;
- full `tests/re`: **184 passed in 3.35s**;
- focused E1-PR-002 corrective suite: **34 passed in 0.18s**.

Runtime dependency set:

- Flask `3.1.1`;
- sqlcipher3 `0.6.2`;
- pywin32 `312`;
- pytest `9.1.1`.

## 2. Corrective findings covered

This binding run includes tests for all three independent-review findings returned against `e197ab72a...`.

### E1PR002-IR-001 — authoritative source revision

- adjustment source state is persisted server-side;
- source revision is not caller-authoritative;
- accepted comparable/market-observation/characteristic writes advance source revision and stale prior CURRENT decisions transactionally;
- the normalized P0/base input is bound to the authoritative source revision and is invalidated when source data changes;
- replay of an old caller revision cannot authorize a calculation.

### E1PR002-IR-002 — concurrency-safe decision lifecycle

- selection, stale marking, validation and snapshot persistence use transaction/CAS protection;
- blind overwrite of a newer human reselection is rejected;
- run validation is rechecked before snapshot insert;
- a decision set that becomes stale/reselected cannot persist a snapshot as though the older state were current.

### E1PR002-IR-003 — immutable decision lineage

- `case_id`, `comparable_property_id`, and `factor_key` are immutable after decision insert;
- persistence rejects re-parenting/re-factoring of an existing decision identity;
- historical audit rows remain bound to the same immutable decision lineage.

## 3. Frozen behavior preserved

The corrective loop does not redesign the accepted E1-PR-002 calculation contract. It preserves:

- exact frozen C1–C11 order and canonical factor keys;
- deterministic Decimal-only calculation;
- explicit selected `0%` distinct from missing/unreviewed;
- C1 on `P0`, C2 on `P1`, C3–C11 adjustment amounts on frozen `P1`;
- human-selected rate authority;
- supplied/precomputed construction aggregate as an Epic-1 boundary input only;
- provenance-complete Golden decision fixture and exact workbook SHA/source cells;
- direct-source reproduction of `F108 = 196308350`, `G108 = 227083250`, `H108 = 212201640`.

## 4. Run history

- `32009701673`: superseded; 175 passed / 2 failed due stale schema-v2 assertions.
- `32009934815`: original pre-review binding run; 177/177 full and 27/27 focused PASS, later superseded by corrective implementation.
- `32017373547`: non-binding corrective attempt; stopped at diff hygiene because prior Markdown hard-break trailing spaces were present.
- `32017538546`: **binding corrective run**; 184/184 full and 34/34 focused PASS.

## 5. Claim boundary

This evidence supports only E1-PR-002 / `AdjustmentCalculationGate`.

It does not claim Comparable Quality / 15%, Human Indication, Final Valuation Composition, CTXD engine, workbook generation, Microsoft Excel qualification, or Epic 1 closure.

## 6. Binding rule

Any source, test, migration, fixture decision value, calculation contract, source-state contract, concurrency behavior, or persistence behavior change after corrective runtime-tested HEAD `74670edb9c5ece5cbd94706808272d6e08a2ee57` requires a new full Windows run before acceptance.

Evidence/report/handoff updates and removal of the one-time corrective workflow may form the post-test review delta only when they do not alter implementation-bearing behavior.
