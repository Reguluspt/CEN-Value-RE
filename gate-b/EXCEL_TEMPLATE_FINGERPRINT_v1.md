# Excel Template Fingerprint v1
**Profile:** `cenvalue-re-n08-0038-v1`
**Source exemplar:** `N08-0038_Huedtl_MTN_TranNguyenVanDau_UNLOCKED.xlsx`

## Structural signature
- Required sheet count in exemplar: 16
- Sheet/state SHA-256: `481997e9672fa4fa88a8b00cb677280e72916b5ce29fde0625f508409ab5e951`
- Formula checkpoint SHA-256: `05812836786218f2893feeb065e271b515b777aa8b3b5965dcc8c9819a4e2d7d`

## Required sheet/state list
- `Hồ sơ` — visible
- `Nhập liệu` — visible
- `Phieu TTTT` — visible
- `Bangtinh` — visible
- `Kehoach` — visible
- `Data` — visible
- `BC-TSTĐG` — hidden
- `BC-TSSS` — hidden
- `Sheet1` — hidden
- `List` — hidden
- `Offical` — visible
- `BGD` — hidden
- `TL` — hidden
- `TTp` — hidden
- `QH` — hidden
- `PX` — hidden

## Formula signature cells
- `Bangtinh!F108=F107`
- `Bangtinh!G108=G107`
- `Bangtinh!H108=H107`
- `Bangtinh!F112=Sheet1!A22`
- `Bangtinh!G112=Sheet1!B22`
- `Bangtinh!H112=Sheet1!C22`
- `Bangtinh!H119=ROUND(Sheet1!G18,-3)`
- `Bangtinh!H127=ROUND((E127-F127)/E127+G127,2)`
- `Bangtinh!F140=ROUND(100%-F139,2)`
- `Bangtinh!H153=ROUND(($H127+$F140)/2,2)`
- `Bangtinh!G156=F156*E156*D156`
- `Bangtinh!H161=F161*D161*G161`
- `Bangtinh!H163=SUM(H162+H161)`
- `Bangtinh!G171=F171*E171`
- `Bangtinh!G169=IF('Hồ sơ'!G14="Shinhan",SUBTOTAL(9,G170:G173),SUBTOTAL(9,Bangtinh!G170:G178))`
- `Bangtinh!G178=IF('Hồ sơ'!G14="Shinhan",SUBTOTAL(9,G179),SUBTOTAL(9,Bangtinh!G179:G180))`
- `Bangtinh!G181=ROUND(G169+G178,0)`
- `Bangtinh!G182=ROUND(G181,-6)`
- `Sheet1!A18=IF(MIN(IF(A7:A17>0,A7:A17))<>MAX(IF(A7:A17>0,A7:A17)),CONCATENATE(MIN(IF(A7:A17>0,A7:A17))," - ",MAX(IF(A7:A17>0,A7:A17))),MIN(IF(A7:A17>0,A7:A17)))`
- `Sheet1!A20=(COUNTIF(Bangtinh!F53:F107,"<>0")-33)/2`
- `Sheet1!A22=ABS(Bangtinh!F56)+ABS(Bangtinh!F61)+ABS(Bangtinh!F71)+ABS(Bangtinh!F76)+ABS(Bangtinh!F81)+ABS(Bangtinh!F86)+ABS(Bangtinh!F91)+ABS(Bangtinh!F66)+ABS(Bangtinh!F96)+ABS(Bangtinh!F101)+ABS(Bangtinh!F106)`
- `Sheet1!A24=SUMIF(Bangtinh!$C$53:$C$107,"Mức điều chỉnh",Bangtinh!F$53:F$107)`
- `Sheet1!G18=IF(COUNTIF(Bangtinh!$F$112:$H$112,"0")<2,$G$14,$C$35)`
- `Offical!E32=Bangtinh!G181`

## Match policy
A candidate template is not identified by filename alone.

Minimum profile match:
1. required sheets exist;
2. required formula-signature cells exist;
3. normalized formulas at required signature cells match the profile, except declared compatibility transformations;
4. external-link classification matches allowed profile state;
5. required named/control ranges used by the Walking Skeleton exist.

Mismatch → `UNSUPPORTED_TEMPLATE`; do not silently fill.

## Compatibility transformation exception
The effective-age formula at `Bangtinh!F127/H127` may be transformed from volatile `YEAR(NOW())` semantics to canonical `appraisal_date`; fingerprint verification must understand this declared profile transformation rather than rejecting the generated output.
