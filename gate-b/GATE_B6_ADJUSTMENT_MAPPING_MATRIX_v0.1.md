# CenValue RE — Gate B.6 Adjustment Mapping Matrix v0.1

**Workbook:** `N08-0038_Huedtl_MTN_TranNguyenVanDau_UNLOCKED.xlsx`  
**Status:** SAMPLE-TEMPLATE MAPPING — REVIEWED

## 1. Adjustment factor mapping

| Factor | Business meaning | Subject source in workbook | TSSS sources | Rate cells | Amount cells | Running result cells | Canonical definition |
|---|---|---|---|---|---|---|---|
| C1 | Pháp lý | `Bangtinh!E10` (hard-coded `Hoàn chỉnh` in this sample) | `F10:H10` | `F55:H55` | `F56:H56` | `F57:H57` | `legal_quality` / special transaction-legal stage |
| C2 | Vị trí | `Nhập liệu!F22` → `Bangtinh!E13` | `Phieu TTTT!B43/G43/L43` | `F60:H60` | `F61:H61` | `F62:H62` | `location_description` |
| C3 | Khoảng cách tương đối đến địa điểm trong khu vực | `Nhập liệu!F27` → `E14` | `Phieu TTTT!B49/G49/L49` | `F65:H65` | `F66:H66` | `F67:H67` | `relative_distance_context` |
| C4 | Quy mô, diện tích | `Nhập liệu!F36` → `E23` | aggregate `Phieu TTTT` area rows → `F23:H23` | `F70:H70` | `F71:H71` | `F72:H72` | `area` |
| C5 | Mặt tiền | `Nhập liệu!H46` → `E15` | `Phieu TTTT!D34/I34/N34` | `F75:H75` | `F76:H76` | `F77:H77` | `frontage` |
| C6 | Chiều dài | `Nhập liệu!H47` → `E16` | `Phieu TTTT!D35/I35/N35` | `F80:H80` | `F81:H81` | `F82:H82` | `depth` |
| C7 | Hình dáng | `Nhập liệu!H48` → `E12` | `Phieu TTTT!D38/I38/N38` | `F85:H85` | `F86:H86` | `F87:H87` | `shape` |
| C8 | Giao thông | `Nhập liệu!H60` → `E17` | `Phieu TTTT!E60/J60/O60` | `F90:H90` | `F91:H91` | `F92:H92` | `traffic_access` |
| C9 | Môi trường kinh doanh | `Nhập liệu!H62` → `E19` | `Phieu TTTT!E62/J62/O62` | `F95:H95` | `F96:H96` | `F97:H97` | `business_environment` |
| C10 | Hệ thống hạ tầng kỹ thuật (label originates from `Nhập liệu!F61`) | `Nhập liệu!H61` → `E18` | `Phieu TTTT!E61/J61/O61` | `F100:H100` | `F101:H101` | `F102:H102` | `technical_infrastructure` |
| C11 | Yếu tố bất lợi khác | `Nhập liệu!F68` → `E22` | `Phieu TTTT!B65/G65/L65` | `F105:H105` | `F106:H106` | `F107:H107` | `adverse_factors` |

## 2. Additional comparison characteristics present but not used as C1–C11 in this sample

The workbook also carries:
- mục đích sử dụng đất;
- môi trường sống, an ninh;
- yếu tố có lợi khác;
- road/position details and additional parcel/CTXD data.

Therefore the CenValue `CharacteristicDefinition` registry must remain broader than the factor list used by one template, and `AdjustmentFactorDefinition` must be versioned/template-aware.

## 3. Calculation base

`Bangtinh!F51:H51` = unit price after market/transaction normalization.

C1 legal:
```text
amount_C1 = rate_C1 × unit_price_after_market_normalization
result_C1 = base + amount_C1
```

C2:
```text
amount_C2 = rate_C2 × result_C1
result_C2 = result_C1 + amount_C2
```

From C3 onward in this sample:
```text
amount_Ci = rate_Ci × result_C1
result_Ci = prior_running_result + amount_Ci
```

Important: `result_C1` (`row 57`) acts as the normalized property-characteristic adjustment base.

This is more precise than treating all factors as either a simple additive percentage of the original price or a fully compounded chain.

## 4. Read-only vs editable UI mapping

Adjustment Workbench:
- characteristic/value rows are read-only references to canonical TSTĐ/TSSS data;
- rate rows are editable human decisions;
- comparison label (`Tương đồng/Kém hơn/Tốt hơn`) is derived from rate sign;
- adjustment amount and running prices are derived;
- quality metrics/final indication are derived/read-only;
- double-clicking a characteristic value navigates to the source canonical field.

## 5. Hard-coded legal row warning

In this sample `Bangtinh!E10:H10` are hard-coded as `Hoàn chỉnh`.

Do not freeze a product rule that every TSTĐ/TSSS is legally `Hoàn chỉnh`.

Gate B must inspect additional historical workbook variants before the final `legal_quality` factor contract is frozen.

## 6. Factor registry consequence

The sample proves:
- factor labels can originate from configurable input rows (`C10`);
- some stored characteristics are not necessarily adjustment factors in a given template;
- the factor order matters to calculation.

Therefore `AdjustmentFactorDefinition` requires at least:
- `key`
- `label_vi`
- `order_index`
- `base_policy`
- `input_characteristic_key`
- `enabled`
- `template_profile_version`
- `calculation_stage`
