# E1-PR-004 — Land + Final Valuation Composition Contract v1

**Status:** IMPLEMENTATION CONTRACT — EPIC 1
**Baseline:** `eef0a9111f1977a49bad11ace2089d9c73ca5772`
**Gate:** `FinalValuationCompositionGate`

## 1. Authority and boundary

E1-PR-004 consumes the accepted E1-PR-003 current human indicated-price confirmation and composes the Walking Skeleton land/final result. It follows Gate B.7 provenance as superseded by Gate B.10/Gate B.13 closure.

Epic 1 does **not** calculate CTXD age, expert deterioration, component deterioration, replacement cost, or remaining-value chains. Construction value enters this PR only through a typed `SUPPLIED_PRECOMPUTED` aggregate with evidence, actor, timestamp, revision and semantic SHA. Epic 2 replaces/feeds this boundary with the canonical Construction Engine.

## 2. Land composition

Included subject `LandValuationComponent` rows are authoritative canonical inputs.

### Compliant residential component

For `planning_status=COMPLIANT` and `valuation_basis=MARKET_INDICATED`:

```text
component_value = current_human_indication.rounded_unit_price × area_m2
```

The current human-indication **rounded** value is used. A conflicting stored/manual unit price fails closed.

### Noncompliant/planning component

For an included `NON_COMPLIANT` component using `OFFICIAL_LAND_PRICE` or `OTHER_MANUAL_BASIS`:

- explicit unit price is mandatory;
- source/profile/control provenance is mandatory through `policy_version` and/or note;
- no unit price is invented or inferred from expected output.

`UNKNOWN` planning status may not contribute to the final value.

Recognized land value is the sum of all included composed land components. Excluded/archived components do not contribute.

## 3. Construction aggregate boundary

`construction_aggregate_input` is append-only evidence. A materially new supplied amount/evidence creates a new case revision. Rebinding the exact current amount/evidence is idempotent.

The application must not derive this value from `ConstructionAsset.replacement_cost_vnd`, `remaining_quality_pct`, `remaining_value_vnd`, age or expert observations in Epic 1.

For the N08 exemplar:

```text
construction_value_total_vnd = 1,152,970,000
```

with explicit source/evidence provenance.

## 4. Final composition and rounding

Canonical values remain distinct:

```text
recognized_land_value_vnd
construction_value_total_vnd
total_value_before_rounding_vnd
final_appraised_value_vnd
```

The pre-final total follows the frozen whole-VND checkpoint:

```text
total_value_before_rounding_vnd = ROUND(recognized_land_value_vnd + construction_value_total_vnd, 0 VND)
```

The final value applies the effective `TOTAL_VALUE` `RoundingPolicy` to `total_value_before_rounding_vnd`.

For a profiled case, `TEMPLATE_DEFAULT` must resolve from the trusted `ExcelTemplateProfile`; caller profile/target/mode/increment labels are not authority. N08 declares `TOTAL_VALUE = NEAREST / 1,000,000 VND`.

A `CASE_OVERRIDE` remains allowed only with its required actor/time audit metadata.

`total_value_before_rounding_vnd` (G181) and `final_appraised_value_vnd` (G182) must never collapse into one field.

## 5. Immutable/current evidence

A final valuation snapshot binds:

- case and appraisal date;
- current subject identity;
- exact current human-indication snapshot ID + semantic SHA;
- rounded indicated unit price consumed;
- exact included land-component semantic bindings and composed JSON/digest;
- exact supplied construction input ID + semantic SHA;
- recognized land and construction totals;
- G181-equivalent pre-rounded total;
- G182-equivalent final rounded value;
- complete effective `TOTAL_VALUE` rounding metadata;
- composition timestamp;
- canonical semantic SHA-256.

Snapshot and source bindings are append-only/immutable.

`resolve_current()` fails closed when the current human indication, included land component state, subject identity, or supplied construction input no longer matches the latest final snapshot. Historical snapshots remain immutable evidence.

## 6. Golden acceptance

With N08 current human indication and explicit land/control inputs, reproduce:

- compliant area: `82.93 m²`;
- rounded indicated unit price: `196308000 VND/m²`;
- `Bangtinh!G171 = 16279822440`;
- noncompliant area: `20.27 m²`;
- explicit noncompliant unit price: `106000000 VND/m²`, sourced from the frozen N08 control/reference evidence (`Nhập liệu!I31` provenance);
- noncompliant component value: `2148620000`;
- `Bangtinh!G169 = 18428442440`;
- supplied `Bangtinh!G178 = 1152970000`;
- `Bangtinh!G181 = 19581412440`;
- `Bangtinh!G182 = 19581000000` under N08 TOTAL_VALUE template default;
- `Offical!E32 = 19581412440` as the Gate B.10 pre-rounded consumer contract.

Golden output values are acceptance comparators, not sources for missing land/control/construction inputs.

## 7. Explicit non-scope

Not implemented here:

- CTXD calculation engine;
- workbook generation or output-cell writing;
- Excel Desktop qualification;
- OCR/Maps;
- Historical Learning;
- approval return/revision;
- full Astryx workbench;
- Epic 1 closure.
