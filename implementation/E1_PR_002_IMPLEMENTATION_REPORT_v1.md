# E1-PR-002 — Implementation Report v1

**Date:** 2026-08-17
**Repository:** `Reguluspt/CEN-Value-RE`
**Accepted base:** `c4e5753c328443e63ce474c03ecbbbf31a2370ed`
**Original reviewed HEAD:** `e197ab72a65fe3c2308cad2d866eba704b7e3424`
**Corrective runtime-tested HEAD:** `74670edb9c5ece5cbd94706808272d6e08a2ee57`
**Binding corrective run:** `32017538546`

## Outcome

E1-PR-002 remains the bounded Epic 1 market-normalization and C1–C11 adjustment slice. The independent review of `e197ab72...` returned three HIGH findings. This corrective loop addresses only those findings and preserves the previously verified frozen calculation and Golden-source behavior.

## Corrective implementation

### Authoritative adjustment source state

The application no longer accepts a caller-supplied revision as authority for selection or calculation. A persisted `AdjustmentSourceState` is the server-side authority for each case/comparable.

Accepted comparable, market-observation and adjustment-relevant characteristic changes advance the authoritative source revision inside persistence and stale prior CURRENT adjustment decisions. A normalized P0/base value is explicitly bound to the current source revision with evidence metadata; source drift invalidates that binding.

### Transaction and concurrency safety

Human selection, source-drift state changes, calculation validation and snapshot persistence now use transaction/CAS protection. Decision state is revalidated before snapshot persistence. A stale operation cannot blind-overwrite a newer human reselection, and an older validated decision set cannot persist a snapshot after an intervening decision change.

### Immutable decision lineage

The persistence boundary freezes `case_id`, `comparable_property_id` and `factor_key` for an existing adjustment decision identity. Re-parenting or re-factoring an existing decision is rejected, so historical selection-audit lineage cannot become inconsistent with the current decision row.

## Frozen behavior preserved

The corrective work does not change:

- exact frozen N08 C1–C11 factor registry/order;
- deterministic Decimal-only calculation;
- explicit selected `0%` versus missing/unreviewed semantics;
- C1 on P0, C2 on P1, and C3–C11 adjustment amounts on frozen P1;
- human professional selection authority;
- supplied/precomputed construction aggregate as an Epic-1 boundary input only;
- Golden decision fixture source workbook SHA/cell provenance;
- exact Golden outputs `F108=196308350`, `G108=227083250`, `H108=212201640`.

## Persistence changes

The E1-PR-002 persistence extension now includes:

- adjustment source-state persistence;
- server-authoritative revision advancement and P0 invalidation on source change;
- transactional staling of CURRENT decisions on source change;
- CAS-capable decision updates;
- immutable decision lineage/factor guards;
- existing selection-audit and calculation-snapshot lineage protections.

No Epic 2/3/4/5 or E1-PR-003+ capability is pulled into this corrective loop.

## Verification

Binding corrective Windows run `32017538546` on exact runtime-tested HEAD `74670edb9c5ece5cbd94706808272d6e08a2ee57`:

- diff hygiene: PASS;
- compile: PASS;
- full `tests/re`: **184 passed in 3.35s**;
- focused corrective E1-PR-002: **34 passed in 0.18s**.

The focused suite includes the reviewer-requested negative/interleaving conditions for old-revision replay, human reselection versus drift write, stale/reselected decision before snapshot, and decision re-parent/re-factor rejection.

## Acceptance boundary

The requested gate remains E1-PR-002 `AdjustmentCalculationGate` only. The implementer does not self-issue `ACCEPTED` and E1-PR-003 must not begin until independent re-review accepts the corrective review HEAD.
