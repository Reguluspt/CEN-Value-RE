# 10 — Adjustment Engine
**Status: REVIEWED — SAMPLE CALCULATION GRAPH DERIVED; FULL FACTOR REGISTRY STILL OPEN**

## Factor Registry
Adjustment factors are versioned definitions, not hard-coded UI columns.

Sample template C1–C11:
1. Pháp lý
2. Vị trí
3. Khoảng cách tương đối đến địa điểm trong khu vực
4. Quy mô/diện tích
5. Mặt tiền
6. Chiều dài
7. Hình dáng
8. Giao thông
9. Môi trường kinh doanh
10. Hệ thống hạ tầng kỹ thuật
11. Yếu tố bất lợi khác

The workbook contains other characteristics not necessarily active as factors in this template; therefore registry is template/version aware.

## Human decision
- `suggested_rate_pct` is separate from `selected_rate_pct`.
- explicit 0% is valid.
- source data changes recompute suggestions/calculations but never overwrite a selected rate.
- stale decisions become `SOURCE_DATA_CHANGED / NEEDS_REVIEW`.

## Comparison label
Derived from selected rate:
- 0 → Tương đồng
- >0 → comparable Kém hơn
- <0 → comparable Tốt hơn

## Sample calculation graph
The sample is not a fully compounded chain.

Let:
`P0 = unit price after market/transaction normalization`.

C1:
```text
A1 = r1 × P0
P1 = P0 + A1
```

C2:
```text
A2 = r2 × P1
P2 = P1 + A2
```

C3–C11 in the sample:
```text
Ai = ri × P1
Pi = P(i-1) + Ai
```

Thus `P1` is the normalized base for subsequent property-characteristic adjustment amounts.

Do not replace this with `previous_price × (1 + rate)` without evidence from another TemplateProfile.

## Quality metrics
```text
gross_adjustment_value = SUM(ABS(Ai))
net_adjustment_value   = SUM(Ai)
adjustment_count       = COUNT(ri != 0)
```

Amplitude canonical form:
```text
min_abs_nonzero_rate
max_abs_nonzero_rate
```
Display may be `5% – 10%`.

## 15% readiness control
For indicated prices `Ii`:

```text
Iavg = AVERAGE(Ii)
deviation_i = (Ii - Iavg) / Iavg
```

Readiness expects:
`ABS(deviation_i) <= 15%`.

Exceeding 15% creates review warning only; no automatic rate correction or comparable removal.

## Guidance
System may recommend based on gross/net/count/amplitude/information quality, prioritizing smallest gross adjustment where appropriate. Appraiser confirms final indicated price.

## OPEN
- legal factor semantics across historical template variants;
- full factor registry;
- all base policies/calculation stages across template families;
- rounding/tolerance for every intermediate;
- information-quality scoring contract.
