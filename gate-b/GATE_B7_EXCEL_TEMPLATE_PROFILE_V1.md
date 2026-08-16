# Gate B.7 — ExcelTemplateProfile v1 Contract
**Status:** CONTRACT FROZEN; concrete profile instance still being completed

## Identity
```text
ExcelTemplateProfile
- id
- profile_version
- template_family
- workbook_fingerprint
- supported_sheet_manifest
- required_named_regions/cell signatures
- mapping_entries[]
- checkpoint_entries[]
- compatibility_transformations[]
- external_link_policy
```

## Fingerprint
A workbook is accepted only when the profile can establish its identity from a combination of:
- expected sheet names/order/signature;
- stable formula/cell signatures in critical regions;
- workbook structural metadata;
- optional content hash for an exact golden template.

A raw file hash alone is insufficient because approved copies may contain legitimate input/result changes.

## MappingEntry
```text
- canonical_field_key
- sheet
- cell_or_range
- direction: TO_WORKBOOK | FROM_RETURNED_WORKBOOK | BOTH
- cell_class
- data_type
- unit
- required
- transform_key?
```

## CheckpointEntry
```text
- checkpoint_key
- sheet
- cell
- canonical_result_key
- rounding_rule
- comparison_rule
- mandatory
```

## CompatibilityTransformation
Only narrowly approved, versioned transformations are allowed.
Initial transformations:
1. CTXD effective age uses canonical `appraisal_date` rather than volatile `NOW()`.
2. stale external self-reference `Phieu TTTT!E5` is localized to canonical/current workbook locality input.

## Unknown-template behavior
If fingerprint/signature does not match:
- do not write to workbook;
- show `Unsupported/Unknown template`;
- allow read-only diagnostic scan;
- require a new/updated profile before production export.

## Formula integrity
Before and after filling:
- hash/signature critical protected formulas;
- reject unexpected mutation in protected regions;
- record approved compatibility transformations separately.

## Output artifact
Every export records:
- template profile/version;
- source template fingerprint;
- generated workbook hash;
- case/calculation version;
- applied transformations;
- checkpoint verification result.

## Approval return
Returned workbook must match the originating submission/profile family before mapped values are diffed. Unknown structural changes are surfaced for human review and are not blindly imported.
