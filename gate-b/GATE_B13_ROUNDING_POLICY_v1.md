# Gate B.13 — RoundingPolicy v1
**Status:** FROZEN DESIGN

## 1. Principle
CenValue stores the unrounded calculated value separately from the presented/final rounded value.

`raw_value -> rounding_policy -> rounded_value`

Rounding never destroys or overwrites `raw_value`.

## 2. Scope
At minimum two independent policies are supported:
- `UNIT_PRICE` — indicated/appraised unit price.
- `TOTAL_VALUE` — total appraised asset value.

A future template may declare additional rounding targets without changing the calculation core.

## 3. Supported increments
- NONE
- 1,000 VND
- 10,000 VND
- 100,000 VND
- 1,000,000 VND
- 10,000,000 VND
- CUSTOM_INCREMENT

`CUSTOM_INCREMENT` must be a positive whole-VND increment.

## 4. Resolution priority
Effective policy is resolved in this order:
1. explicit case-level professional selection;
2. template/profile default;
3. application default only when the template declares no requirement.

AI may recommend/explain but may not silently change the effective rounding policy.

## 5. Canonical model
`RoundingPolicy`
- target
- mode = NEAREST
- increment_vnd
- source = TEMPLATE_DEFAULT | CASE_OVERRIDE | APPLICATION_DEFAULT
- profile_id/profile_version when applicable
- selected_by / selected_at for case override
- raw_value
- rounded_value

The selected policy is included in calculation and approval snapshots.

## 6. Workbook exemplar defaults
N08-0038 profile:
- indicated unit price: 1,000 VND/m² (`Bangtinh!H119 = ROUND(...,-3)`).
- final total appraisal value: 1,000,000 VND (`Bangtinh!G182 = ROUND(G181,-6)`).

These become profile defaults, not hard-coded global rules.

## 7. UI
In `Kết quả thẩm định`:
- show raw calculated value;
- show `Mức làm tròn` selector;
- show rounded result immediately;
- indicate when current selection differs from template default;
- changing it recalculates only affected derived/final outputs.

No reason field is required for changing the case-level rounding selection, but the change is auditable.

## 8. Excel compatibility
The adapter maps the effective policy to the appropriate output formula/value contract.
If a legacy template cannot represent a selected custom increment safely, the generated workbook must use an approved profile override/output value and record it in audit metadata rather than corrupting protected formulas.

## 9. Golden-case baseline
For N08-0038:
- raw indicated unit price: 196,308,350
- default rounded indicated unit price: 196,308,000
- total before final rounding: 19,581,412,440
- default final rounded value: 19,581,000,000

Golden tests must additionally cover at least one case override for UNIT_PRICE and one for TOTAL_VALUE.
