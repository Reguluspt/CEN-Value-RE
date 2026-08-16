# Gate B.1 — Workbook Mapping Discovery: Bangtinh rows 123–163

Workbook: `N08-0038_Huedtl_MTN_TranNguyenVanDau_UNLOCKED.xlsx`

This is a direct structural extraction from the workbook XML. Values shown are stored cell values and formulas; it does not recalculate formulas.

## Cells

### Row 123
- `B123` = `3. BẢNG TÍNH GIÁ TRỊ CÔNG TRÌNH XÂY DỰNG `

### Row 124
- `B124` = `A. TỶ LỆ CHẤT LƯỢNG CÒN LẠI (TLCLCL) `

### Row 125
- `B125` = `THEO PHƯƠNG PHÁP TUỔI ĐỜI`

### Row 126
- `B126` = `Stt`
- `C126` = `Hạn mục công trình`
- `D126` = `Năm  xây dựng`
- `E126` = `Tuổi đời  kinh tế (năm)`
- `F126` = `Tuổi đời  hiệu quả (năm)`
- `G126` = `Chế độ duy tu/bảo dưỡng`
- `H126` = `Tỷ lệ CLCL  (%)`

### Row 127
- `B127` = `1`
- `C127` = `Công trình xây dựng (CTXD)`
- `D127` value=`2008` formula=`'Nhập liệu'!F74`
- `E127` = `50`
- `F127` value=`18` formula=`IF(OR('Nhập liệu'!F74="",'Nhập liệu'!F74="-/-"),0,VALUE(YEAR(NOW())-D127))`
- `G127` = `0.05`
- `H127` value=`0.69` formula=`ROUND((E127-F127)/E127+G127,2)`

### Row 128
- `B128` = `Tỷ lệ CLCL công trình xây dựng = (Tuổi đời kinh tế - Tuổi đời hiệu quả) / Tuổi đời kinh tế + Chế độ duy tu/bảo dưỡng (*) Chế độ duy tu/bảo dưỡng: Duy tu/bảo dưỡng tốt ( + ); Duy...`

### Row 129

### Row 130
- `B130` = `PHƯƠNG PHÁP CHUYÊN GIA`

### Row 131
- `B131` = `Công trình `
- `D131` = `Kết cấu chính`
- `F131` = `Tỷ trọng`
- `G131` = `Tỷ lệ hao mòn`
- `H131` = `Mức đóng góp`

### Row 132
- `B132` = `Nhà từ 3 đến 5 tầng`
- `D132` = `Móng`
- `F132` value=`0.08` formula=`Sheet1!A26`
- `G132` = `0.25`
- `H132` value=`0.02` formula=`G132*Sheet1!A26`

### Row 133
- `D133` = `Khung cột `
- `F133` value=`0.1` formula=`Sheet1!A27`
- `G133` = `0.3`
- `H133` value=`0.03` formula=`G133*Sheet1!A27`

### Row 134
- `D134` = `Tường`
- `F134` value=`0.12` formula=`Sheet1!A28`
- `G134` = `0.3`
- `H134` value=`3.5999999999999997E-2` formula=`G134*Sheet1!A28`

### Row 135
- `D135` = `Nền, sàn`
- `F135` value=`0.16` formula=`Sheet1!A29`
- `G135` = `0.3`
- `H135` value=`4.8000000000000001E-2` formula=`G135*Sheet1!A29`

### Row 136
- `D136` = `Kết cấu đỡ mái`
- `F136` value=`0.12` formula=`Sheet1!A30`
- `G136` = `0.3`
- `H136` value=`3.5999999999999997E-2` formula=`G136*Sheet1!A30`

### Row 137
- `D137` = `Mái`
- `F137` value=`0.05` formula=`Sheet1!A31`
- `G137` = `0.3`
- `H137` value=`1.4999999999999999E-2` formula=`G137*Sheet1!A31`

### Row 138
- `D138` = `Tổng`
- `F138` value=`0.63` formula=`SUM(Sheet1!A26:A31)`
- `G138` = `--`
- `H138` value=`0.185` formula=`SUM(H132:H137)`

### Row 139
- `D139` = `Tỷ lệ hao mòn`
- `F139` value=`0.28999999999999998` formula=`ROUND(H138/F138,2)`

### Row 140
- `D140` = `Tỷ lệ chất lượng còn lại`
- `F140` value=`0.71` formula=`ROUND(100%-F139,2)`

### Row 141
- `B141` = `Công trình `
- `D141` = `Kết cấu chính`
- `F141` = `Tỷ trọng`
- `G141` = `Tỷ lệ hao mòn`
- `H141` = `Mức đóng góp`

### Row 142
- `B142` = `Nhà ở riêng lẻ 2`
- `D142` = `Móng `
- `F142` = `0.08`
- `G142` = `0.6`
- `H142` value=`4.8000000000000001E-2` formula=`G142*F142`

### Row 143
- `B143` = `Nhà từ 3 đến 5 tầng`
- `D143` = `Khung cột `
- `F143` = `0.1`
- `G143` = `0.15`
- `H143` = `1.4999999999999999E-2`

### Row 144
- `D144` = `Tường`
- `F144` = `0.12`
- `G144` = `0.15`
- `H144` = `1.7999999999999999E-2`

### Row 145
- `D145` = `Nền, sàn`
- `F145` = `0.16`
- `G145` = `0.2`
- `H145` = `3.2000000000000001E-2`

### Row 146
- `D146` = `Kết cấu đỡ mái`
- `F146` = `0.12`
- `G146` = `7.0000000000000007E-2`
- `H146` = `8.4000000000000012E-3`

### Row 147
- `D147` = `Mái`
- `F147` = `0.05`
- `G147` = `0.1`
- `H147` = `5.000000000000001E-3`

### Row 148
- `D148` = `Tổng`
- `F148` value=`0.63` formula=`SUM(F142:F147)`
- `G148` = `--`
- `H148` value=`0.12640000000000001` formula=`SUM(H142:H147)`

### Row 149
- `D149` = `Tỷ lệ hao mòn`
- `F149` value=`0.20063492063492067` formula=`H148/F148`

### Row 150
- `D150` = `Tỷ lệ chất lượng còn lại`
- `F150` value=`0.79936507936507928` formula=`100%-F149`

### Row 151
- `B151` = `TỶ LỆ CHẤT LƯỢNG CÒN LẠI BÌNH QUÂN `

### Row 152
- `B152` = `Tỷ lệ chất lượng còn lại bình quân = (TLCLCL theo phương pháp tuổi đời + TLCLCL theo phương pháp chuyên gia)/2`

### Row 153
- `B153` = `TLCLCLBQ công trình xây dựng = (`
- `D153` value=`0.69` formula=`$H$127`
- `E153` = `+`
- `F153` value=`0.71` formula=`F140`
- `G153` = `)/2                 =`
- `H153` value=`0.7` formula=`ROUND(($H127+$F140)/2,2)`

### Row 154
- `B154` = `B. CHI PHÍ THAY THẾ `

### Row 155
- `B155` = `Stt`
- `C155` = `Hạng mục công trình `
- `D155` = `Hệ số  trượt giá`
- `E155` = `Tổng diện  tích sàn (m2)`
- `F155` = `Đơn giá  xây mới (*)`
- `G155` = `Chi phí thay thế (đ)`

### Row 156
- `B156` = `+`
- `C156` = `CTXD phù hợp quy hoạch`
- `D156` = `1`
- `E156` value=`253.4` formula=`'Nhập liệu'!I79`
- `F156` = `6500000`
- `G156` value=`1647100000` formula=`F156*E156*D156`

### Row 157
- `B157` = `+`
- `C157` = `CTXD vi phạm quy hoạch`
- `D157` = `1`
- `E157` = `0`
- `F157` = `0`
- `G157` value=`0` formula=`F157*E157*D157`

### Row 158

### Row 159
- `B159` = `C. GIÁ TRỊ CÒN LẠI CỦA CÔNG TRÌNH XÂY DỰNG TRÊN ĐẤT`

### Row 160
- `B160` = `Stt`
- `C160` = `Tên công trình `
- `D160` = `Chi phí thay thế (đ)`
- `F160` = `TLCLCL  bình quân`
- `G160` value=`Hệ số` formula=`IF('Hồ sơ'!G14="VIB",CONCATENATE("Hệ số ",'Hồ sơ'!G14),"Hệ số")`
- `H160` = `Giá trị (đ)`

### Row 161
- `B161` = `+`
- `C161` value=`Giá trị CTXD phù hợp quy hoạch` formula=`CONCATENATE("Giá trị ",C156)`
- `D161` value=`1647100000` formula=`G156`
- `F161` value=`0.7` formula=`H153`
- `G161` = `1`
- `H161` value=`1152970000` formula=`F161*D161*G161`

### Row 162
- `B162` = `+`
- `C162` value=`Giá trị CTXD vi phạm quy hoạch` formula=`CONCATENATE("Giá trị ",C157)`
- `D162` value=`0` formula=`G157`
- `F162` = `0`
- `G162` = `0`
- `H162` value=`0` formula=`F162*D162*G162`

### Row 163
- `C163` = `Công trình xây dựng`
- `H163` value=`1152970000` formula=`SUM(H162+H161)`