# Gate B.10 — Output Consumer Contract v1
**Status:** FROZEN FOR EXEMPLAR

## Finding
The workbook intentionally carries two total-value states:
- `Bangtinh!G181`: exact total after land + included CTXD, rounded to whole VND.
- `Bangtinh!G182`: final appraisal value rounded to nearest 1,000,000 VND.

They serve different downstream outputs:
- `Offical!E32` references **G181**.
- `Data!M261`, `Data!D281`, `Data!D301` also carry G181.
- `Sheet1!B275` references **G182** and feeds the amount-in-words chain.
- `Data!M262` and `Data!G309` carry G182.

## CenValue canonical decision
Both are canonical derived values with distinct meanings:
- `total_value_before_rounding_vnd`
- `final_appraised_value_vnd`

Do not overwrite one with the other.

Each output mapping chooses explicitly which value it needs. In the exemplar:
- structured `Offical.Total` remains mapped to pre-million-rounding total;
- report/amount-in-words final-result flow uses the million-rounded final appraisal value.

This is an output-consumer mapping rule, not a contradiction in the valuation domain.
