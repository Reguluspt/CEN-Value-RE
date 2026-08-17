# E1-PR-001 — Manual Case / TSTĐ / TSSS Data Backbone Contract v1

**Status:** IMPLEMENTATION CONTRACT — EPIC 1
**Baseline:** `723409a3da60216e42cc9344afadc75c1f590d91`
**Scope:** canonical manual case, subject property and TSSS01/02/03 data only

## 1. Purpose

E1-PR-001 establishes the first business-data vertical slice after Epic 0. A caller can create, update and resume one manual appraisal case containing:

- required appraisal date;
- explicit supported Excel template profile id/version;
- one active subject property (TSTĐ);
- subject legal/location/parcel/land-segmentation/comparison characteristics;
- three independently addressable comparable slots TSSS01–03;
- comparable market observation amounts and light evidence metadata;
- exact Decimal/string values without binary-float conversion.

This PR does not calculate adjustment, quality, indication, land value or final valuation.

## 2. Canonical numeric and missing-value rules

Canonical numeric request values are accepted only as:

- Decimal;
- integer;
- exact decimal string.

Binary `float`, non-finite Decimal, and `bool` at numeric boundaries fail closed.

Exact decimal scale is preserved as text in persistence. Therefore:

- `"6500000.00"` remains `"6500000.00"`;
- `"0.0000"` remains `"0.0000"`;
- `None` remains missing.

Explicit zero is not missing.

## 3. Profile selection

The application service receives an explicit supported-profile catalog at composition time.

A manual case stores:

- `template_profile_id`;
- `template_profile_version`.

The core application does not import the concrete Excel profile adapter. An unrecognized profile selection is rejected with a bounded application error.

For the N08 Walking Skeleton, the supported profile reference is:

`cenvalue-re-n08-0038-v1@1`.

## 4. Subject property

The active subject record preserves the canonical common Property fields required by the Walking Skeleton:

- legal/current address;
- latitude/longitude;
- planning/environment notes;
- legal review status;
- source certificate id when known.

Land data is not flattened into the Property row.

### LandParcel

A subject may carry versioned/identified parcel rows with:

- parcel number;
- map sheet;
- total area;
- legal/current address;
- notes.

### LandValuationComponent

Appraisal land segmentation is separate from legal parcel identity. Each component records:

- planning status: `COMPLIANT | NON_COMPLIANT | UNKNOWN`;
- exact area;
- valuation basis: `MARKET_INDICATED | OFFICIAL_LAND_PRICE | OTHER_MANUAL_BASIS`;
- optional unit price;
- inclusion flag;
- policy/note provenance metadata.

E1-PR-001 stores these inputs only. E1-PR-004 will calculate land values.

## 5. Property characteristics

Walking Skeleton comparison characteristics use typed rows keyed by stable `definition_key`.

Exactly one typed value is present per row:

- decimal;
- text;
- code;
- boolean;
- date.

An absent characteristic means missing/unentered. A decimal characteristic `"0.0000"` is an explicit zero value and remains present.

## 6. Comparable properties / TSSS

A manual case supports exactly slots 1, 2 and 3.

Each comparable stores:

- stable property identity;
- case lineage;
- slot/order;
- legal/current address and location metadata;
- completeness status;
- one current market observation;
- typed comparison characteristics;
- zero or more light evidence metadata rows.

Market observation stores:

- asking/sale price;
- negotiated price;
- optional canonical fractional negotiation rate;
- optional observation date/note.

E1-PR-001 does not normalize market price or calculate indicated price.

## 7. Persistence migration v2

Migration `2 — epic1_manual_case_data_backbone` is explicit, ordered and transactional.

It extends the accepted encrypted RE database with:

- case profile selection;
- property location/note columns;
- comparable case/slot uniqueness;
- `land_parcel`;
- `land_valuation_component`;
- `property_characteristic`;
- `market_observation`;
- `evidence`.

It does not open, migrate or reshape legacy `cases.db`.

## 8. Atomic application writes

`SQLCipherUnitOfWork.atomic()` owns bundle transaction boundaries.

Repository methods remain independently usable. When called inside `atomic()`, repositories do not commit intermediate records.

A failed nested subject/comparable write must roll back the whole application command.

Operational archive remains non-destructive.

## 9. Application capability

`ManualCaseService` exposes:

- `create_case`;
- `save_subject`;
- `save_comparable`;
- `resume_case`.

Resume returns a deterministic serialized snapshot containing case, subject bundle and comparable bundles in comparable-order order.

Identity reuse across another case/role/slot fails closed.

## 10. Local-service exercise

When a `ManualCaseService` is explicitly injected, the authenticated loopback RE blueprint exposes:

- `POST /api/re/manual-cases`;
- `GET /api/re/manual-cases/<case_id>`;
- `PUT /api/re/manual-cases/<case_id>/subject`;
- `PUT /api/re/manual-cases/<case_id>/comparables/<1|2|3>`.

Existing per-launch loopback/session authentication remains mandatory.

The Flask adapter only maps JSON/application errors. It does not own domain validation or SQL.

## 11. Explicit non-scope

Not implemented here:

- market normalization;
- C1–C11 decisions/calculation;
- comparable quality/readiness;
- human indicated-price decision;
- land/final valuation calculation;
- CTXD calculation;
- workbook generation;
- full Astryx workbench;
- OCR/provider integrations.

`ManualCaseDataGate = PASS` must not be interpreted as any calculation correctness claim.
