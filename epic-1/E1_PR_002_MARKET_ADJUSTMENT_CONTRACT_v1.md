# E1-PR-002 — Market Normalization + C1–C11 Adjustment Contract v1

**Status:** IMPLEMENTATION CONTRACT — EPIC 1
**Baseline:** `c4e5753c328443e63ce474c03ecbbbf31a2370ed`
**Scope:** manual comparable market normalization and human-selected C1–C11 adjustment calculation

## 1. Authority

This implementation derives from the accepted Epic 1 plan, frozen Gate B closure, Gate B.8 factor registry, the reviewed Adjustment Engine design and the product Brainstorm History.

Historical v0.1 workbook-discovery documents are provenance where later closure supersedes them. They may supply workbook evidence only when consistent with the later frozen contracts.

## 2. Factor registry

The exemplar registry is ordered and exact:

1. `C1` — `legal_status`
2. `C2` — `location`
3. `C3` — `relative_distance_to_local_points`
4. `C4` — `scale_area`
5. `C5` — `frontage`
6. `C6` — `depth`
7. `C7` — `shape`
8. `C8` — `traffic_access`
9. `C9` — `business_environment`
10. `C10` — `infrastructure`
11. `C11` — `other_disadvantage`

Workbook labels remain presentation/profile metadata. Canonical calculation uses stable keys.

## 3. Human authority and missing-value semantics

A selected adjustment rate is a human decision.

- canonical percentage is fractional Decimal: `5% = Decimal("0.05")`;
- an explicitly selected `0%` is a valid decision;
- `None`/missing is not zero and blocks a complete adjustment run;
- recommendation/suggestion may never overwrite a selected rate;
- source-data drift marks the decision `SOURCE_DATA_CHANGED / NEEDS_REVIEW` rather than silently changing the selected rate.

## 4. Market normalization

For the frozen N08 exemplar, source workbook evidence supports:

`normalized_property_price = ROUND(asking_price × transaction_success_factor, 10,000,000 VND)`.

The normalized/negotiated price remains a primary business fact and may be persisted directly. The transaction factor is provenance/compatibility metadata and must not replace the stored normalized value.

Comparable land-unit base `P0` is derived after subtracting a **supplied/precomputed construction aggregate boundary input**. E1-PR-002 does not implement the CTXD age/expert/replacement-cost engine.

When converted land area is positive:

`P0 = ROUND((normalized_property_price - supplied_construction_value) / converted_land_area, 1,000 VND/m²)`.

Otherwise:

`P0 = ROUND((normalized_property_price - supplied_construction_value + land_use_conversion_cost) / total_land_area, 1,000 VND/m²)`.

A missing/invalid denominator fails closed.

## 5. Frozen adjustment graph

The N08 exemplar is not a generic fully-compounded chain.

Let `P0` be the normalized land-unit price.

- `C1`: `A1 = r1 × P0`; `P1 = P0 + A1`.
- `C2`: `A2 = r2 × P1`; `P2 = P1 + A2`.
- `C3..C11`: `Ai = ri × P1`; `Pi = P(i-1) + Ai`.

Therefore `P1`, not each immediately previous running price, is the adjustment-amount base for C3–C11.

A profile may define a different graph in the future, but E1-PR-002 may not generalize one without evidence and a versioned contract.

## 6. Determinism

All calculation is Decimal-only and independent of ambient Decimal precision. Binary float, bool, non-finite Decimal and malformed decimal strings fail closed at canonical numeric boundaries.

The calculation result is an immutable snapshot containing:

- normalized base `P0`;
- the C1-derived property adjustment base `P1`;
- ordered factor key/rate/base/amount/running-price steps;
- final indicated unit price.

## 7. Golden Fixture input gate

The current canonical Golden Fixture lacks explicit C1–C11 selected decisions.

Before N08 F108/G108/H108 can be claimed as end-to-end calculation evidence, a versioned decision fixture must be extracted from source workbook/reference evidence. Each rate must retain source workbook identity/SHA and source cell/range provenance.

Forbidden:

- inventing a missing rate;
- reverse-solving a rate from F108/G108/H108/H119 or any expected output;
- treating an expected checkpoint as the source decision.

If mandatory source decisions remain unproven, the N08 adjustment E2E state is `BLOCKED_INPUT_COVERAGE`, not PASS.

## 8. Explicit non-scope

Not implemented by this PR:

- comparable quality/15% readiness;
- final indicated-price human selection;
- subject land/final valuation composition;
- CTXD calculation engine;
- workbook generation;
- OCR/Maps/Historical Learning/approval round-trip;
- full Astryx workbench.

## 9. Acceptance

E1-PR-002 is acceptable only when:

- registry order and canonical keys are exact;
- explicit zero is retained as an entered decision;
- missing decisions fail closed;
- C3–C11 use frozen `P1` amount base;
- calculation is Decimal-only and deterministic under changed ambient Decimal precision;
- persistence/application snapshots preserve decision provenance and staleness state;
- Golden decision fixture is provenance-complete, or N08 E2E assertions remain explicitly blocked;
- all previous Epic 0/E1 guards remain green.
