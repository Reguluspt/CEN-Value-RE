# E1-PR-003 — Implementation Report v1

**Date:** 2026-08-17
**Repository:** `Reguluspt/CEN-Value-RE`
**Accepted base:** `7e60be157e6b0d5300ffaa8dabac1aadc73f96fb`
**Runtime-tested implementation HEAD:** `c8fd43df4b2f15be430ae2a5dcc9c4f151caba33`
**Binding Windows run:** `32037927058`
**Gate:** `HumanIndicationGate`

## Outcome

E1-PR-003 implements the bounded Epic 1 slice for comparable quality metrics, inclusive 15% readiness guidance, frozen minimum-gross recommendation behavior, and explicit human indicated-price confirmation.

The implementation consumes accepted E1-PR-002 adjustment snapshots as authoritative calculation evidence. It does not duplicate or alter the frozen C1–C11 adjustment graph.

## Domain behavior

For each current comparable adjustment run, E1-PR-003 derives deterministic Decimal-only:

- gross adjustment value = sum of absolute adjustment amounts;
- net adjustment value = sum of signed adjustment amounts;
- adjustment count = count of non-zero selected rates;
- amplitude = min/max absolute non-zero selected rates.

Explicitly selected `0%` remains a valid human decision but is not counted as a non-zero adjustment and does not fabricate a `0–0` amplitude.

The 15% readiness check uses the arithmetic average of exactly three current comparable indicated prices and applies the inclusive criterion `abs(deviation) <= 0.15`. `NEEDS_REVIEW` is advisory only and never changes rates, drops a comparable, or auto-selects a final price.

## Guidance / tie behavior

- unique minimum gross adjustment -> advisory comparable recommendation;
- two or three zero-gross minimum candidates -> frozen supported average indication;
- equal non-zero minimum gross candidates -> ambiguous guidance requiring human choice;
- no general mean/median or information-quality scoring formula is invented.

## Human authority

`ComparableQualityService.confirm_indication()` requires an explicit human actor, timestamp, and non-empty reason. A professional may confirm any of the three current comparables even when it is not the system recommendation.

The API has no arbitrary caller-supplied numeric final-price path. The only non-comparable selection is the frozen zero-gross average when current evidence proves eligibility.

## Freshness and E1-PR-002 binding

Quality/indication uses only E1-PR-002 adjustment snapshots whose:

- source revision matches authoritative current adjustment source state;
- complete C1–C11 decisions are explicit and CURRENT at that revision;
- decision-set SHA matches the current persisted decision set.

Rate reselection or source drift makes older adjustment evidence ineligible until E1-PR-002 is rerun.

Human confirmation is immutable historical evidence. `resolve_current_indication()` verifies the latest human snapshot against current comparable lineage, current source revisions, current decision-set SHA values, exact referenced adjustment snapshot IDs/hashes, and the human snapshot semantic SHA. After source drift/reselection and a new adjustment run, an older human confirmation remains reproducible history but is rejected as current until the human reconfirms.

## RoundingPolicy integration

E1-PR-003 reuses the accepted `RoundingPolicy` primitive rather than duplicating rounding logic.

The immutable confirmation snapshot preserves:

- target;
- mode;
- increment;
- source;
- profile ID/version where applicable;
- case-override selected-by/selected-at metadata;
- raw indicated unit price;
- rounded indicated unit price.

Template-default rounding must match the case profile. Application-default rounding is not accepted when a case already has a template binding. Case overrides retain their own professional-selection audit metadata.

## Persistence v4

Migration v4 adds:

- immutable `human_indication_snapshot` records;
- immutable `human_indication_source` records binding the exact three comparable adjustment snapshots and semantic hashes;
- case/comparable/adjustment lineage guards;
- append-only update/delete guards;
- rounding-policy constraints and case-override metadata constraints.

The service creates the parent and all three source bindings in one transaction. Current resolution additionally fails closed if a malformed/partial snapshot lacks exactly three source bindings.

## Golden result

The accepted Golden adjustment evidence reproduces:

- TSSS01: count `2`, gross `34642650`, net `-34642650`, amplitude `5–10`;
- TSSS02: count `4`, gross `83662250`, net `-11951750`, amplitude `5–15`;
- TSSS03: count `4`, gross `35366940`, net `15718640`, amplitude `3–5`;
- raw selected indication `196308350`;
- N08 default rounded indication `196308000`.

The Golden E1-PR-002 workbook provenance/decision fixture remains unchanged.

## Verification

Binding Windows run `32037927058` against implementation HEAD `c8fd43df4b2f15be430ae2a5dcc9c4f151caba33`:

- Windows Server 2025 / Python 3.11.9;
- diff hygiene: PASS;
- compile: PASS;
- full `tests/re`: **206 passed in 4.78s**;
- focused E1-PR-003: **20 passed in 0.26s**;
- tested merge-ref tree exactly equals runtime HEAD tree `8808d6d345aba43d994152fd7f55f19373c1ef51`.

## Explicit non-scope

No implementation is claimed for E1-PR-004 final valuation composition, CTXD engine, workbook generation/Excel qualification, OCR/Maps, Historical Learning, approval return/revision, full Astryx workbench, or Epic 1 closure.

The implementer does not self-issue acceptance. E1-PR-004 must not begin until independent review accepts the exact final E1-PR-003 review HEAD and the PR is merged by expected-head protection.
