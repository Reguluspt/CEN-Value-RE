# Gate B.8 — Adjustment Factor Registry v1
**Status:** FROZEN FOR EXEMPLAR / EXTENSIBLE BY PROFILE

## Registry order
| Key | Workbook label | Canonical factor key | Source characteristic |
|---|---|---|---|
| C1 | Pháp lý | `legal_status` | legal completeness/status |
| C2 | Vị trí | `location` | physical/location position |
| C3 | Khoảng cách tương đối từ tài sản đến các địa điểm trong khu vực | `relative_distance_to_local_points` | descriptive relative-distance factor |
| C4 | Quy mô, diện tích | `scale_area` | total/comparison land area |
| C5 | Mặt tiền | `frontage` | frontage length |
| C6 | Chiều dài | `depth` | parcel depth |
| C7 | Hình dáng | `shape` | parcel shape |
| C8 | Giao thông | `traffic_access` | traffic/access quality |
| C9 | Môi trường kinh doanh | `business_environment` | business environment |
| C10 | Hệ thống hạ tầng kỹ thuật | `infrastructure` | infrastructure quality |
| C11 | Yếu tố bất lợi khác | `other_disadvantage` | other adverse factors |

## Evidence
- Workbook `Bangtinh!C63 = Bangtinh!B14`, where `B14` is “Khoảng cách tương đối từ tài sản đến các địa điểm trong khu vực”.
- Workbook `Bangtinh!C98 = Bangtinh!B18`, where `B18` resolves from `Nhập liệu!F61` to “Hệ thống hạ tầng kỹ thuật”.

Thus C3 and C10 are no longer unresolved dynamic factors in the exemplar profile.

## Design rule
The engine uses stable canonical factor keys. Workbook labels remain profile/presentation metadata.

A future template may add/reorder factors through `AdjustmentFactorDefinition`, but it may not reuse an existing canonical key for a materially different business meaning.

## Adjustment rows in exemplar
C1 rate row 55
C2 60
C3 65
C4 70
C5 75
C6 80
C7 85
C8 90
C9 95
C10 100
C11 105
