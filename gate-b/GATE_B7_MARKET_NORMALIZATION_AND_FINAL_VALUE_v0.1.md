# CenValue RE — Gate B.7 Market Normalization & Final Property Value v0.1

**Date:** 2026-08-15  
**Workbook:** `N08-0038_Huedtl_MTN_TranNguyenVanDau_UNLOCKED.xlsx`  
**Status:** WORKBOOK-DERIVED / SAMPLE PROFILE REVIEWED

## 1. Comparable market normalization

For each TSSS the workbook carries:
- market asking/listing price;
- a field labelled `Tỷ lệ ước tính giao dịch thành công`;
- price after adjustment.

Sample formula:
```text
price_after_market_adjustment
= ROUND(asking_price × successful_transaction_factor, -7)
```

Sample factor = 0.85 for all three TSSS.

Cached results:
- 21,500,000,000 × 0.85 → 18,280,000,000
- 88,000,000,000 × 0.85 → 74,800,000,000
- 38,000,000,000 × 0.85 → 32,300,000,000

### Canonical decision
GĐ1 primary stored price fields remain:
- source/asking or market price;
- price after negotiation/market normalization.

The factor may be stored/derived for provenance and workbook compatibility, but the two price values are the primary business facts.

Do not rename the historical workbook field silently; retain its raw source label in provenance.

## 2. Comparable construction deduction

Comparable land unit price is derived after removing the estimated CTXD value from the normalized property price.

Sample CTXD value:
```text
comparable_construction_value
= new_build_unit_cost
  × construction_area
  × remaining_quality
```

## 3. Comparable land unit price

Workbook `Sheet1!F12:H12`:

If `converted_land_area > 0`:
```text
land_unit_price
= ROUND(
    (price_after_market_adjustment - comparable_construction_value)
    / converted_land_area,
    -3
  )
```

Otherwise:
```text
land_unit_price
= ROUND(
    (
      price_after_market_adjustment
      - comparable_construction_value
      + land_use_conversion_cost
    )
    / total_land_area,
    -3
  )
```

Sample:
- TSSS 01: 230,951,000 đ/m²
- TSSS 02: 239,035,000 đ/m²
- TSSS 03: 196,483,000 đ/m²

This value becomes the pre-adjustment base `P0` for the Adjustment Engine.

## 4. Land segmentation on TSTĐ

The sample TSTĐ splits land by **planning treatment**, even when the legal land-use type is the same:

```text
Total land area: 103.20 m²
├── planning-compliant land: 82.93 m²
│   └── residential land: 82.93 m²
└── planning-violating land: 20.27 m²
    └── residential land: 20.27 m²
```

This proves that `LandUseComponent` alone is insufficient for valuation.

### Required domain addition

Introduce a valuation segmentation layer, e.g. `LandValuationComponent`:

```text
LandValuationComponent
- id
- property_id / parcel_id
- land_use_component_id?
- planning_status
- area_m2
- valuation_basis
- unit_price_vnd_per_m2?
- include_in_final_value
- note?
```

Possible `planning_status`:
`COMPLIANT | NON_COMPLIANT | UNKNOWN`

Possible `valuation_basis`:
`MARKET_INDICATED | OFFICIAL_LAND_PRICE | OTHER_MANUAL_BASIS`

This layer is appraisal treatment, not a replacement for legal `LandUseComponent`.

## 5. Subject land value in sample

Planning-compliant residential land:
```text
82.93 × 196,308,000
= 16,279,822,440
```

Planning-violating residential land:
```text
20.27 × 106,000,000
= 2,148,620,000
```

Total recognized land value:
```text
18,428,442,440
```

Thus the sample applies the market-indicated unit price to compliant land and the official land-price input to the planning-violating portion.

This is a TemplateProfile/business-policy behavior; it must not be generalized to all cases until corroborated by additional workbook variants/company rules.

## 6. Subject construction value

Sample:
```text
CTXD compliant planning value = 1,152,970,000
CTXD non-compliant planning value = 0
```

The sample output labels CTXD value as `(tham khảo)` in the final table.

CenValue's domain remains broader:
- VALUE
- DESCRIBE_ONLY
- EXCLUDE

The workbook adapter maps the user's treatment/policy into the legacy rows.

## 7. Final property value

Sample workbook:

```text
property_value_before_rounding
= recognized_land_value
  + included_construction_value
```

```text
18,428,442,440
+ 1,152,970,000
= 19,581,412,440
```

Final rounded value:
```text
ROUND(19,581,412,440, -6)
= 19,581,000,000
```

## 8. Client/lender-specific branches

The workbook contains branches based on `Hồ sơ!G14` (examples include Shinhan/VIB) that change labels or which planning-violating components are included.

These are **not universal domain formulas**.

CenValue must model them as a versioned valuation/output policy extension, not `if bank == ...` logic embedded in the core calculation engine.

## 9. Design impact

- add `LandValuationComponent` / equivalent segmentation;
- separate legal land-use facts from valuation treatment;
- add policy/TemplateProfile extension point for lender/company-specific inclusion;
- keep market-normalized comparable price separate from raw listing price;
- final result remains human-confirmed and snapshot-versioned.
