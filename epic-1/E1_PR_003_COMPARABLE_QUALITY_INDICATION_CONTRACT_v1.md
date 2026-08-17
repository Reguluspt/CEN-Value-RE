# E1-PR-003 — Comparable Quality + 15% Readiness + Human Indication Contract v1

**Status:** IMPLEMENTATION CONTRACT — EPIC 1
**Baseline:** `7e60be157e6b0d5300ffaa8dabac1aadc73f96fb`
**Gate:** `HumanIndicationGate`

## 1. Authority

This contract implements the accepted Epic 1 plan and the frozen Gate B Walking Skeleton decisions. Historical Gate B v0.1 documents and Brainstorm History are provenance only where later Gate B closure supersedes them.

E1-PR-003 consumes accepted E1-PR-002 adjustment calculation snapshots. It does not recompute C1–C11 with a different graph and does not implement E1-PR-004 final valuation composition.

## 2. Comparable quality metrics

For one current adjustment run with ordered steps `i=1..11`:

```text
gross_adjustment_value = SUM(ABS(adjustment_amount_i))
net_adjustment_value   = SUM(adjustment_amount_i)
adjustment_count       = COUNT(selected_rate_i != 0)
min_abs_nonzero_rate   = MIN(ABS(selected_rate_i) WHERE selected_rate_i != 0)
max_abs_nonzero_rate   = MAX(ABS(selected_rate_i) WHERE selected_rate_i != 0)
```

An explicitly selected `0%` remains a valid human decision but is excluded from `adjustment_count` and amplitude. When every selected rate is zero, the canonical min/max non-zero amplitude is absent rather than fabricated as zero.

All arithmetic is Decimal-only and deterministic.

## 3. 15% readiness

For the three current comparable indicated unit prices `I1`, `I2`, `I3`:

```text
Iavg = (I1 + I2 + I3) / 3
deviation_i = (Ii - Iavg) / Iavg
```

`Iavg` must be positive. The readiness criterion is inclusive:

```text
ABS(deviation_i) <= Decimal("0.15")
```

Exactly 15% is READY. A value outside the threshold produces `NEEDS_REVIEW` guidance only. It never changes an adjustment rate, removes a comparable, or selects a final price automatically.

## 4. Recommendation and tie behavior

System guidance is advisory.

- Normal case: the unique comparable with minimum gross adjustment is the recommended comparable.
- Frozen special tie: when two or three comparables have gross adjustment exactly zero, the arithmetic average of the zero-gross candidates may be proposed as a supported average indication.
- Equal non-zero minimum gross values do **not** authorize automatic averaging. The guidance remains ambiguous and the human must choose a comparable.
- No mean/median/general averaging rule may be introduced outside the frozen zero-gross tie behavior.

The information-quality scoring contract remains outside this implementation because Gate B did not freeze a canonical scoring formula. E1-PR-003 must not invent one.

## 5. Human indication authority

The final indicated unit price used downstream requires an explicit human confirmation.

Supported selections are:

1. any one of the three current comparables; or
2. the frozen zero-gross average only when current guidance proves that tie eligible.

A caller may not submit an arbitrary numeric final price and may not convert a recommendation into a decision without confirmation.

The immutable confirmation snapshot binds:

- case identity;
- exact three current adjustment snapshot IDs and semantic hashes;
- quality/readiness/guidance snapshot;
- selection kind and selected comparable when applicable;
- raw indicated unit price;
- exact applied `RoundingPolicy` metadata;
- rounded indicated unit price;
- human actor;
- confirmation timestamp;
- non-empty reason;
- canonical semantic SHA-256.

## 6. Freshness / stale evidence

A comparable adjustment snapshot is eligible only when:

- its case/comparable lineage is current;
- its source revision equals the authoritative current adjustment source revision;
- all C1–C11 decisions are CURRENT at that revision;
- the snapshot decision-set SHA equals the current persisted decision set.

If a human rate is reselected or source data changes after a snapshot, quality/indication must fail closed until a new E1-PR-002 adjustment snapshot exists.

## 7. Rounding

Human confirmation preserves raw and rounded values separately:

```text
raw_selected_indication -> UNIT_PRICE RoundingPolicy -> rounded_indication
```

For N08-0038 the frozen default is 1,000 VND/m². E1-PR-003 reuses the accepted `RoundingPolicy` domain primitive and does not duplicate rounding logic.

## 8. Golden acceptance

Using the provenance-complete Golden C1–C11 decision fixture, E1-PR-003 must reproduce:

- TSSS01 count `2`, gross `34642650`, net `-34642650`, amplitude `5–10`;
- TSSS02 count `4`, gross `83662250`, net `-11951750`, amplitude `5–15`;
- TSSS03 count `4`, gross `35366940`, net `15718640`, amplitude `3–5`;
- selected/raw indication `196308350` corresponding to `Sheet1!G18`;
- 1,000-VND rounded indication `196308000` corresponding to `Bangtinh!H119`.

15% tests must cover exactly-at, inside, and outside the inclusive threshold.

## 9. Explicit non-scope

Not implemented here:

- CTXD calculation engine;
- subject land/final valuation composition;
- workbook generation or Excel qualification;
- OCR/Maps;
- Historical Learning / suggested-rate engine;
- approval return/revision;
- full Astryx workbench;
- information-quality scoring formula.
