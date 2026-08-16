# 03 — Canonical Domain Model v1

**Status: REVIEWED — CORE CONTRACT FROZEN; workbook-specific registry remains extensible**

## 1. Storage conventions

- Primary IDs: UUID text.
- Timestamps: UTC ISO-8601.
- Money: decimal/integer VND, never binary float.
- Area: decimal m².
- Length: decimal m.
- Percentage adjustment: canonical fractional decimal (`Decimal("0.05")` = +5%; `Decimal("-0.05")` = -5%).
- All canonical `*_pct` values use fractional representation; input/display/Excel adapters are responsible for percentage-point formatting and conversion.
- Coordinates: decimal latitude/longitude.
- User-visible Vietnamese labels are presentation metadata; canonical keys are stable machine keys.
- Derived/calculated fields are not authoritative inputs unless explicitly marked as a human decision.

## 2. Aggregate root — AppraisalCase

```text
AppraisalCase
- id
- case_code
- status
- created_at / updated_at
- appraisal_date?
- client_name?
- valuation_purpose?
- include_in_historical_learning : bool
- active_subject_property_id
- current_approval_revision?
- version
```

Case status:
`DRAFT | IN_PROGRESS | READY_FOR_APPROVAL | EXPORTED_FOR_APPROVAL | APPROVAL_RETURNED | REVISION_REQUIRED | APPROVED | CLOSED`

The legacy CenValue Manager case record may be linked by `legacy_case_id`, but it is not the canonical aggregate.

## 3. Property model

### Property
Common identity used by TSTĐ and TSSS:

```text
Property
- id
- case_id
- role : SUBJECT | COMPARABLE
- display_name?
- legal_address
- current_address
- latitude?
- longitude?
- planning_note?
- environment_note?
- created_at / updated_at
- version
```

### SubjectProperty
```text
SubjectProperty
- property_id
- legal_review_status
- source_certificate_id?
```

### ComparableProperty
```text
ComparableProperty
- property_id
- comparable_order
- market_observation_id?
- completeness_status
```

Property data never contains case-specific adjustment rates.

## 4. Land legal/parcel model

### LandCertificate
```text
LandCertificate
- id
- property_id
- certificate_serial?
- certificate_number?
- issued_date?
- legal_holder_text?
- registered_attached_assets_text?
- qr_payload?
- source_document_id?
```

### LandParcel
```text
LandParcel
- id
- property_id
- parcel_number?
- map_sheet_number?
- total_area_m2?
- use_form?
- land_use_origin?
- legal_address?
- current_address?
- notes?
```

A certificate/property may contain multiple parcels.

### LandUseComponent
```text
LandUseComponent
- id
- parcel_id
- land_use_code?
- land_use_label
- area_m2?
- term_text?
- term_end_date?
```


## 4A. Land valuation segmentation

Workbook evidence shows that the same legal land-use type can be split into different appraisal treatments, e.g. residential land split into planning-compliant and planning-violating portions.

Therefore legal `LandUseComponent` is not enough for valuation.

### LandValuationComponent
```text
- id
- property_id
- parcel_id?
- land_use_component_id?
- planning_status
- area_m2
- valuation_basis
- unit_price_vnd_per_m2?
- include_in_final_value
- note?
- policy_version?
```

`planning_status`:
`COMPLIANT | NON_COMPLIANT | UNKNOWN`

`valuation_basis`:
`MARKET_INDICATED | OFFICIAL_LAND_PRICE | OTHER_MANUAL_BASIS`

This is an appraisal segmentation/treatment layer. It does not overwrite the legal land-use record.

## 5. Property characteristics for comparison

Stable legal/identity fields stay structured. Comparison factors use a typed extensible registry so workbook-specific factors can be added without changing the database schema.

### CharacteristicDefinition
```text
- key                 # stable: area, frontage, depth, road_width, shape...
- label_vi
- value_type          # DECIMAL | TEXT | CODE | BOOLEAN | DATE
- unit?               # m2, m, ...
- comparison_enabled
- adjustment_factor_key?
- version
```

### PropertyCharacteristic
```text
- id
- property_id
- definition_key
- decimal_value?
- text_value?
- code_value?
- bool_value?
- date_value?
- source_status
- provenance_id?
- verified_by_user : bool
- updated_at
```

Core definitions at v1 include at minimum:
`area`, `frontage`, `depth`, `shape`, `access_type`, `road_name`, `road_width`, `location_quality`, `business_environment`, `infrastructure_quality`.

Workbook Mapping may add definitions/factors, but may not create parallel property tables or duplicate source-of-truth fields.

## 6. ConstructionAsset

```text
ConstructionAsset
- id
- property_id
- name
- construction_type?
- use_function?
- floors?
- construction_area_m2?
- gross_floor_area_m2?
- year_built?
- structure_description?
- observed_condition_note?
- legal_registration_status
- valuation_treatment
- maintenance_condition_pct?
- replacement_cost_vnd?
- remaining_quality_pct?
- remaining_value_vnd?       # derived snapshot
- created_at / updated_at
- version
```

`legal_registration_status`:
`REGISTERED | NOT_REGISTERED | UNKNOWN`

`valuation_treatment`:
`VALUE | DESCRIBE_ONLY | EXCLUDE`

Rules:
- legal absence ≠ physical absence;
- `DESCRIBE_ONLY` is complete, not missing;
- only `VALUE` contributes to construction value.

Detailed component/weight rows are modeled separately:

### ConstructionComponentAssessment
```text
- id
- construction_asset_id
- component_key
- fixed_weight_pct
- observed_remaining_pct?
- derived_weighted_pct?
```

## 7. Comparable market observation

```text
MarketObservation
- id
- comparable_property_id
- asking_or_sale_price_vnd
- negotiation_rate_pct?
- negotiated_price_vnd
- observation_date?
- note?
```

Evidence is light in GĐ1:

```text
Evidence
- id
- property_id?
- market_observation_id?
- document_id?
- evidence_type?
- source_url?
- note?
```

One TSSS may have multiple Evidence.

## 8. Adjustment model

### AdjustmentFactorDefinition
```text
- key
- label_vi
- order_index
- input_characteristic_key?
- enabled
- rule_engine_extension_key?
- version
```

### AdjustmentDecision
Case-specific, one row per comparable/factor:

```text
- id
- case_id
- comparable_property_id
- factor_key
- suggested_rate_pct?
- selected_rate_pct?
- selected_explicitly : bool
- selected_at?
- source_data_revision
- review_status
- stale_reason?
- suggestion_snapshot_id?
- approved_rate_pct?
- approval_submission_id?
- version
```

`review_status`:
`UNSET | CURRENT | SOURCE_DATA_CHANGED | NEEDS_REVIEW`

Explicit 0% is represented as:
`selected_rate_pct = 0` + `selected_explicitly = true`.

### AdjustmentSuggestionSnapshot
```text
- id
- factor_key
- comparable_property_id
- suggested_rate_pct
- sample_size
- median_rate_pct?
- p25_rate_pct?
- p75_rate_pct?
- confidence?
- dataset_snapshot_id?
- created_at
```

Historical suggestion never overwrites `selected_rate_pct`.

## 9. Historical learning

### AdjustmentObservation
```text
- id
- source_case_id?
- source_workbook_id?
- factor_key
- subject_feature_snapshot
- comparable_feature_snapshot
- appraiser_rate_pct?
- approved_rate_pct?
- final_training_rate_pct?
- explicit_zero : bool
- eligible_for_learning : bool
- dataset_version
- provenance_id
```

No reason is required when a case is excluded from learning.

## 10. Calculation / ValuationResult

### ComparableCalculation
```text
- id
- case_id
- comparable_property_id
- base_unit_price_vnd_per_m2?
- sequential_steps_snapshot
- indicated_unit_price_vnd_per_m2?
- gross_adjustment_pct?
- net_adjustment_pct?
- adjustment_count?
- adjustment_amplitude_pct?
- quality_grade?
- calculation_version
```

### ValuationResult
```text
- id
- case_id
- selected_comparable_property_id?
- indicated_unit_price_vnd_per_m2?
- land_value_vnd?
- construction_value_vnd?
- total_value_before_rounding_vnd?
- final_appraised_value_vnd?
- final_decision_confirmed_at?
- calculation_version
- version
```

Human confirmation is required for the final valuation decision.

## 11. Documents, extraction and provenance

### SourceDocument
```text
- id
- case_id
- document_type
- file_name
- content_hash
- local_vault_path
- created_at
```

### ExtractionDraft
```text
- id
- document_id
- extractor_type
- status
- created_at
```

### ExtractionCandidate
```text
- id
- extraction_draft_id
- target_field_key
- candidate_value
- confidence?
- source_page?
- source_region?
- provider?
- review_status
```

No candidate becomes canonical until reconciliation/human review applies it.

### ProvenanceRecord
```text
- id
- entity_type
- entity_id
- field_key
- source_type
- source_id?
- source_revision?
- actor_type
- actor_id?
- action
- timestamp
```

Source types include:
`MANUAL | GCN_OCR | VBDLIS | MAPS | HISTORICAL | EXCEL_IMPORT | APPROVAL_RETURN`.

## 12. Approval

### ApprovalSubmission
```text
- id
- case_id
- revision_no
- exported_at
- template_profile_id
- workbook_hash
- submitted_case_snapshot
- submitted_result_snapshot
- output_document_id
- status
```

### ApprovalFieldDecision
```text
- id
- approval_submission_id
- field_key
- submitted_value
- returned_value
- change_type
- confirmed_by_user
```

Never infer an adjustment change from only a changed final result.

## 13. Workspace state

```text
CaseWorkspaceState
- case_id
- last_section
- active_comparable_property_id?
- active_construction_asset_id?
- focused_field_key?
- grid_row_key?
- grid_column_key?
- scroll_state?
- drawer_state?
- updated_at
```

This table is disposable UI state and does not affect valuation audit history.

## 14. Legacy coexistence

Existing `src/sqlite_store.py` tables remain legacy CenValue Manager storage.

CenValue RE creates new bounded persistence. It may retain `legacy_case_id` and import/adapt selected values, but:
- no new RE valuation fields are added to the legacy wide `cases` table;
- new RE domain code does not query legacy tables directly;
- migration is performed through explicit adapters/application services.

## 15. Freeze boundary

FROZEN at v1:
- aggregate/entity separation;
- legal vs physical split;
- multiple parcels and land-use components;
- typed extensible property characteristic registry;
- multiple CTXD and treatment semantics;
- TSSS property vs adjustment separation;
- explicit-zero adjustment semantics;
- suggestion/appraiser/approval lineage;
- staging/provenance/approval/workspace boundaries;
- decimal/units policy.

OPEN until Workbook/Calculation closure:
- final complete `CharacteristicDefinition` and `AdjustmentFactorDefinition` registry;
- precise calculation snapshots and rounding scale;
- fields required solely by the legacy workbook.
