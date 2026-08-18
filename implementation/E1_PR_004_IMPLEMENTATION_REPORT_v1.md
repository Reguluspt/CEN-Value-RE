# E1-PR-004 — Implementation Report v1

**Date:** 2026-08-17
**Repository:** `Reguluspt/CEN-Value-RE`
**Accepted base:** `eef0a9111f1977a49bad11ace2089d9c73ca5772`
**Runtime-tested implementation HEAD:** `e66be8d3ea419eb736012b06c81f669b30c76a78`
**Binding Windows run:** `32043291836`
**Gate:** `FinalValuationCompositionGate`

## Outcome

E1-PR-004 implements the bounded Epic 1 land/final valuation composition slice and consumes the accepted E1-PR-003 current human indication as upstream authority.

It does not implement the CTXD calculation engine. Construction value is supplied only through a typed, append-only `SUPPLIED_PRECOMPUTED` boundary input with evidence, actor, timestamp, revision and semantic SHA.

## Land composition

The pure domain composes canonical included subject `LandValuationComponent` rows:

- `COMPLIANT + MARKET_INDICATED` uses the current **rounded** human indicated unit price;
- a conflicting manual price on that component fails closed;
- included `NON_COMPLIANT` components require explicit unit price plus provenance metadata;
- `UNKNOWN` planning status cannot contribute to final value;
- excluded/archived components do not contribute.

All arithmetic is Decimal-only and independent of ambient Decimal context precision.

## Construction boundary

`FinalValuationService.bind_supplied_construction_aggregate()` persists append-only supplied construction evidence. Exact amount/evidence repeat is idempotent; a material amount/evidence change creates the next case revision and makes an older final result non-current.

The service does not read or derive value from `construction_asset.replacement_cost_vnd`, `remaining_quality_pct`, `remaining_value_vnd`, age or expert observations.

## Final value / rounding

Canonical values remain separate:

- `recognized_land_value_vnd`;
- `construction_value_total_vnd`;
- `total_value_before_rounding_vnd` (G181 boundary);
- `final_appraised_value_vnd` (G182 boundary).

For a profiled case, `TEMPLATE_DEFAULT` TOTAL_VALUE policy is checked against the trusted `ExcelTemplateProfile` through the core Excel port. N08 requires `NEAREST / 1,000,000 VND`. Case override remains explicit and carries its required actor/time audit metadata.

## Immutable and current evidence

Migration v5 adds:

- append-only `construction_aggregate_input`;
- immutable/append-only `final_valuation_snapshot`;
- immutable/append-only `final_valuation_land_source` bindings;
- persistence-level case/subject/human/construction/land lineage guards.

A final snapshot binds case/appraisal date, subject, exact current human-indication ID/hash, rounded indication consumed, exact included land-component hashes/JSON, exact construction input ID/hash, all land/construction/G181/G182 totals, full effective TOTAL_VALUE policy, timestamp and semantic SHA.

`resolve_current()` fails closed if appraisal date, case profile/rounding default, subject, current human indication/upstream adjustment evidence, included land components, or supplied construction input changes. Historical final snapshots remain immutable and their semantic SHA remains reconstructable from persisted snapshot content.

## Golden result

The accepted N08 chain reproduces:

- compliant land `16279822440`;
- noncompliant/planning land `2148620000`;
- recognized land `18428442440`;
- supplied construction `1152970000`;
- G181/pre-rounded total `19581412440`;
- G182/final rounded appraisal `19581000000`.

Gate B.10 `Offical!E32` consumes the pre-rounded G181 value `19581412440`. Workbook generation is not performed in this PR.

## Verification

Binding Windows run `32043291836` on runtime-tested HEAD `e66be8d3ea419eb736012b06c81f669b30c76a78`:

- Microsoft Windows Server 2025 / Python 3.11.9;
- diff hygiene: PASS;
- compile: PASS;
- full `tests/re`: **229 passed in 4.11s**;
- focused E1-PR-004: **17 passed in 0.33s**;
- tested merge-ref `f51d7d3e4596d5e004c8919f9df61c01a99fa656` tree `21905f501b2385dce3c868bca5daa18eb3c260a9` exactly equals runtime HEAD tree.

## Explicit non-scope

No implementation is claimed for the Epic 2 CTXD calculation engine, workbook generation/Excel qualification, OCR/Maps, Historical Learning, approval return/revision, full Astryx workbench, or Epic 1 closure.

The implementer does not self-issue acceptance. E1-PR-005 must not begin until independent review accepts the exact final E1-PR-004 review HEAD and PR #14 is merged using expected-head protection.
