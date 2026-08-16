# CENVALUE MANAGER REAL ESTATE

## Brainstorm History & Decision Log

**Phiên bản:** 3.0\
**Ngày khởi tạo:** 14/08/2026\
**Trạng thái:** Living Document

> Mục đích: lưu vết đầy đủ các phiên brainstorm, quyết định thiết kế,
> giả định, phạm vi và các quy tắc bắt buộc trước khi chuyển sang vòng
> brainstorm tiếp theo.

------------------------------------------------------------------------

# 1. Quy tắc quản trị tài liệu brainstorm

1.  Đây là **tài liệu sống (living document)** và là nguồn tham chiếu
    chính cho các quyết định brainstorm của CenValue Manager Real
    Estate.
2.  Trước khi bắt đầu bất kỳ vòng brainstorm mới nào, **phải cập nhật
    tài liệu này bằng kết quả của vòng vừa kết thúc**.
3.  Mỗi lần cập nhật phải ghi: ngày/giờ, mục tiêu vòng brainstorm, các
    phương án đã thảo luận, phản biện của từng vai, quyết định đã chốt,
    nội dung chưa chốt, tác động kiến trúc/UI/UX/nghiệp vụ và bước tiếp
    theo.
4.  Không được âm thầm thay đổi quyết định cũ. Nếu thay đổi, phải tạo
    mục **Decision Revision** nêu quyết định cũ, lý do thay đổi và quyết
    định mới.
5.  Các giả định chưa được xác minh phải đánh dấu **GIẢ ĐỊNH**; nội dung
    được người dùng chốt phải đánh dấu **ĐÃ CHỐT**.
6.  Mỗi vòng phải duy trì **Open Questions** để tránh biến suy đoán
    thành yêu cầu.
7.  Trước khi tạo coding packet/PR, các quyết định liên quan phải xuất
    hiện trong tài liệu brainstorm và được chuyển thành design/data
    contract phù hợp.
8.  Workbook mẫu, mã nguồn CenValue hiện tại và quy định nghiệp vụ là
    bằng chứng. Khi chúng mâu thuẫn, phải ghi nhận mâu thuẫn thay vì tự
    chọn một phía.
9.  AI/Historical Learning không phải nguồn phê duyệt giá. Quyết định hệ
    số và kết quả cuối vẫn cần human review theo phạm vi đã chốt.
10. **Update-before-next-brainstorm là gate bắt buộc: chưa cập nhật lịch
    sử thì chưa chuyển sang vòng brainstorm mới.**

------------------------------------------------------------------------

# 2. Thành phần team brainstorm

### Product / Architecture Lead

Chuyển workbook và mã nguồn CenValue thành kiến trúc sản phẩm, data
model, engine, integration và roadmap.

### Chuyên gia thẩm định giá BĐS --- phương pháp so sánh

Bảo vệ tính đúng đắn nghiệp vụ, logic TSTĐ/TSSS, bảng điều chỉnh, bằng
chứng và kết luận.

### Chuyên gia UI/UX

Thiết kế trải nghiệm thân thiện cho người dùng đã quen Excel; giữ muscle
memory hữu ích nhưng loại bỏ sự phụ thuộc vào ô, sheet và công thức ẩn.

**Nguyên tắc phản biện:** Không ép đồng thuận sớm. Khác biệt giữa nghiệp
vụ, UX và kiến trúc phải được ghi lại và giải quyết bằng quyết định có
lý do.

------------------------------------------------------------------------

# 3. Lịch sử brainstorm chi tiết

## Phiên 01 --- Định hình sản phẩm từ workbook Excel

-   Không bê nguyên Excel vào phần mềm theo mô hình `1 ô = 1 công thức`.
-   Reverse-engineer workbook thành **business rules**, calculation
    modules và data provenance.
-   CenValue RE được định hình theo các lớp: hồ sơ, tài sản, dữ liệu thị
    trường/TSSS, Valuation Engine, Document Engine, Audit/AI.
-   Đề xuất **Valuation Calculation Graph** để truy vết từ giá nguồn qua
    từng điều chỉnh tới giá trị kết luận.
-   Đề xuất **Excel Compatibility Mode**: engine mới chạy song song với
    workbook legacy để regression-check kết quả.
-   Excel được xem là **legacy valuation engine** và bằng chứng nghiệp
    vụ thực tế.

## Phiên 02 --- Team đa chuyên gia và nguyên tắc UI/UX

-   Thiết lập ba vai brainstorm: Architecture Lead, chuyên gia thẩm định
    BĐS, chuyên gia UI/UX.
-   **ĐÃ CHỐT:** UI/UX phải dựa trên giao diện nhập liệu hiện tại của
    workbook để người dùng quen Excel chuyển đổi với ít ma sát.
-   Không clone Excel theo nghĩa đen.
-   Giữ các hành vi hữu ích: Tab/Enter, copy/paste vùng, grid editing,
    phím tắt, undo/redo.
-   Workbench + progressive disclosure là hướng dung hòa giữa ma trận
    nghiệp vụ dày đặc và trải nghiệm dễ dùng.

## Phiên 03 --- Hai nguồn hệ số điều chỉnh

-   **ĐÃ CHỐT:** Hệ số điều chỉnh phát triển theo hai hướng song song.
-   **Company Rule Engine:** bộ quy tắc điều chỉnh do công ty ban hành,
    có version/ngày hiệu lực; phát triển sau.
-   **Historical Adjustment Learning:** quét hàng loạt file Excel cũ để
    học pattern điều chỉnh thực tế.
-   Historical Learning trước tiên là **empirical evidence /
    recommendation**, không mặc nhiên biến quyết định lịch sử thành quy
    tắc đúng.
-   Mỗi adjustment phải lưu provenance: nguồn đề xuất, sample
    size/confidence, giá trị được chọn, override và lý do.

## Phiên 04 --- Roadmap hai giai đoạn

### Giai đoạn 1 --- Appraisal Production

**ĐÃ CHỐT:**

-   Bộ khung học hệ số từ Excel cũ.
-   Nhập thông tin TSTĐ.
-   Nhập thông tin TSSS.
-   Bảng điều chỉnh.
-   Calculation.
-   Fill dữ liệu trở lại workbook mẫu.
-   Xuất Excel trình cấp phê duyệt.

### Giai đoạn 2 --- Appraisal Intelligence

**ĐÃ CHỐT:**

-   Kho dữ liệu tài sản đã thẩm định.
-   Kho TSSS.
-   Property Identity.
-   Lịch sử giá.
-   Tìm kiếm TSSS.
-   Geospatial database / Map.
-   Property Knowledge.

**Nguyên tắc:** GĐ1 phải lưu dữ liệu đủ cấu trúc để GĐ2 hình thành tự
nhiên, không làm sản phẩm tạm rồi viết lại.

Tọa độ `Latitude + Longitude` trong workbook được nâng thành thuộc tính
lõi của Property Identity.

## Phiên 05 --- Thiết kế sâu GĐ1

Đề xuất 7 workspace:

1.  Khởi tạo hồ sơ.
2.  TSTĐ.
3.  TSSS.
4.  Bảng so sánh & điều chỉnh.
5.  Gợi ý hệ số lịch sử.
6.  Kiểm tra hồ sơ.
7.  Xuất Excel.

### GCN Scanner

Luồng:

`GCN → OCR/Vision → Semantic Parser → Staging → Human Review → PropertyDraft`

-   UI GCN theo kiểu đối chiếu: ảnh GCN bên trái, field trích xuất bên
    phải.
-   Có confidence và human confirmation.
-   Địa chỉ pháp lý trên GCN và địa chỉ hành chính hiện tại phải là hai
    trường riêng.
-   **Không overwrite địa chỉ pháp lý gốc.**

### Administrative Address Resolver

-   Hỗ trợ mapping đơn vị hành chính theo thời gian.
-   Không chỉ dùng dictionary đơn giản.
-   Trường hợp đơn vị cũ bị chia/nhập cần có khả năng sử dụng tọa độ +
    GIS polygon.
-   Giữ provenance/version của việc chuyển đổi.

### TSSS Workbench

Hai chế độ:

-   Card/Form.
-   Bảng so sánh kiểu Excel.

### Historical Learning

`Template Fingerprint → Deterministic Extractor → Normalized Case → Adjustment Observations → Statistical Patterns → AI Semantic Analysis`

Nguyên tắc: **deterministic trước, AI sau.**

### Excel

Excel trở thành **Output Adapter**.

`Property/Appraisal Data Model` là source of truth mới.

## Phiên 06 --- Desktop local-first

**ĐÃ CHỐT:** CenValue Manager Real Estate là **Windows Desktop-first,
local-first**.

-   Không phụ thuộc web để thực hiện nghiệp vụ cốt lõi.
-   Ưu tiên Tauri 2 + React/Astryx hiện có.
-   Tái sử dụng backend/domain logic CenValue thay vì viết lại toàn bộ.
-   Migration ban đầu có thể sử dụng embedded/local-only FastAPI.
-   Local data cần encrypted storage.
-   Historical Excel Learning chạy local.
-   Excel input/output chạy local.
-   Network access là capability có kiểm soát, không phải mặc định.

## Phiên 07 --- Online OCR & Google Maps có kiểm soát

**ĐÃ CHỐT:** GĐ1 sử dụng OCR online và Google Maps/Geocoding online để
giảm gánh nặng cấu hình.

Mở hướng chuyển OCR sang server nội bộ công ty về sau.

### Provider abstraction

``` text
OcrProvider
├── CloudOcrProvider
└── InternalOcrProvider
```

``` text
MapProvider
├── GoogleMapsProvider
└── FutureInternalMapProvider
```

-   UI không gọi trực tiếp provider.
-   External traffic đi qua **External Service Gateway**.
-   OCR chỉ nhận dữ liệu tối thiểu cần thiết; không gửi toàn bộ hồ sơ,
    bảng giá hay TSSS.
-   OCR chia hai tầng:
    -   Provider: image → text/layout.
    -   CenValue: GCN semantic parser → PropertyDraft.
-   Khi mất Internet, các chức năng local vẫn hoạt động: nhập TSTĐ/TSSS,
    Historical Learning, bảng điều chỉnh, calculation và Excel export.

------------------------------------------------------------------------

# 4. Kiến trúc GĐ1 hiện đang được chốt

-   **Platform:** Windows Desktop.
-   **UI:** React + Astryx, thiết kế theo muscle memory của workbook
    Excel.
-   **Desktop shell:** ưu tiên Tauri 2.
-   **Core:** local-first; có thể tái sử dụng FastAPI
    embedded/local-only trong migration.
-   **Storage:** local encrypted database + document/evidence vault.
-   **Input:** GCN, manual input, historical Excel batch scanner.
-   **OCR:** online trong GĐ1, thông qua provider abstraction.
-   **Maps:** Google Maps/Geocoding online qua gateway.
-   **Historical Learning:** local deterministic extraction +
    statistical pattern memory; AI hỗ trợ semantic
    analysis/recommendation.
-   **Output:** fill dữ liệu vào workbook Excel legacy ban đầu để trình
    cấp phê duyệt.
-   **Future:** OCR có thể chuyển sang server nội bộ mà không thay đổi
    workflow/data model.

Core model:

``` text
AppraisalCase
│
├── SubjectProperty
│   ├── Legal
│   ├── AddressHistory
│   ├── Location
│   ├── LandParcel
│   ├── Planning
│   ├── Building
│   └── Environment
│
├── ComparableProperty[]
│   ├── Transaction
│   ├── Evidence
│   ├── Location
│   ├── LandParcel
│   └── Building
│
├── AdjustmentMatrix
│   └── Adjustment[]
│
├── ValuationResult
└── Evidence[]
```

------------------------------------------------------------------------

# 5. Quy tắc nghiệp vụ và thiết kế bắt buộc

-   Excel legacy là compatibility/output contract trong GĐ1, không phải
    source of truth mới.
-   Không được bỏ sót field hoặc business dependency của workbook khi
    chuyển sang UI/data model.
-   Phải truy vết được:

`UI field ↔ Database field ↔ Excel cell/range`

-   UI phải thân thiện với người dùng đã quen workbook hiện tại.
-   GCN extraction luôn có staging/human review trước khi apply.
-   Giữ đồng thời địa chỉ trên GCN và địa chỉ hành chính hiện hành, kèm
    provenance/version.
-   Historical Adjustment Suggestion phải hiển thị căn cứ: sample size,
    distribution/range, confidence và hồ sơ nguồn khi có.
-   Human quyết định hệ số cuối cùng và kết quả thẩm định.
-   External service traffic phải qua gateway và có audit.
-   Core phải usable khi offline.
-   GĐ1 phải tạo dữ liệu sẵn sàng cho Property/TSSS Knowledge Base của
    GĐ2.

------------------------------------------------------------------------

# 6. Open Questions

-   Chọn OCR cloud provider cụ thể cho GĐ1 và chính sách lưu/xóa dữ liệu
    của provider.
-   Cơ chế mã hóa database/document vault và quản lý khóa trên Windows.
-   Data contract chi tiết của `SubjectProperty`, `ComparableProperty`,
    `AdjustmentObservation`.
-   Mapping đầy đủ từng vùng/ô workbook sang UI/DB/Excel Output Adapter.
-   Phương pháp phân nhóm workbook legacy theo template family và xử lý
    workbook biến thể.
-   Nguồn dữ liệu hành chính/GIS chính thức và chiến lược cập nhật
    registry.
-   Quy tắc thống kê/ML xác định "trường hợp tương tự" khi gợi ý hệ số.
-   Phạm vi Google Maps trong GĐ1: mở vị trí/geocoding hay embedded map
    trong Workbench.

------------------------------------------------------------------------

# 7. UPDATE-BEFORE-NEXT-BRAINSTORM GATE

## Quy tắc bắt buộc

> **Không được bắt đầu vòng brainstorm N+1 trước khi kết quả của vòng N
> được cập nhật đầy đủ vào tài liệu này.**

Checklist trước khi chuyển vòng:

-   [ ] Cập nhật `Lịch sử brainstorm chi tiết`.
-   [ ] Ghi ngày/giờ và mục tiêu của phiên.
-   [ ] Ghi các phương án đã thảo luận.
-   [ ] Ghi phản biện quan trọng của Architecture / Appraisal / UI-UX.
-   [ ] Ghi rõ các quyết định **ĐÃ CHỐT**.
-   [ ] Chuyển vấn đề chưa quyết định vào `Open Questions`.
-   [ ] Nếu thay đổi quyết định cũ, tạo `Decision Revision`.
-   [ ] Cập nhật `Kiến trúc hiện đang được chốt`.
-   [ ] Cập nhật `Quy tắc nghiệp vụ và thiết kế bắt buộc` nếu cần.
-   [ ] Xác định đầu vào và phạm vi của vòng brainstorm tiếp theo.
-   [ ] Tăng version tài liệu khi có thay đổi đáng kể.
-   [ ] Chỉ sau khi toàn bộ gate hoàn tất mới bắt đầu vòng tiếp theo.

------------------------------------------------------------------------

# 8. Quy tắc Decision Revision

Khi một quyết định đã chốt bị thay đổi, thêm mục theo mẫu:

``` markdown
### DR-XXX — Tên quyết định

**Ngày:** YYYY-MM-DD  
**Trạng thái:** ĐÃ CHỐT

**Quyết định cũ:**  
...

**Bằng chứng/vấn đề mới:**  
...

**Quyết định mới:**  
...

**Lý do:**  
...

**Tác động:**
- Architecture:
- Data:
- UI/UX:
- Appraisal:
- Migration:
```

Không xóa quyết định cũ khỏi lịch sử.

------------------------------------------------------------------------

# 9. Template cho mỗi vòng brainstorm mới

``` markdown
## Phiên XX — [Tên phiên]

**Ngày/giờ:**  
**Mục tiêu:**  
**Đầu vào:**  

### Vấn đề cần giải quyết
...

### Góc nhìn chuyên gia thẩm định
...

### Góc nhìn UI/UX
...

### Góc nhìn Architecture
...

### Phương án đã thảo luận
1. ...
2. ...

### Phản biện / Trade-offs
...

### Quyết định đã chốt
- [ĐÃ CHỐT] ...

### Giả định
- [GIẢ ĐỊNH] ...

### Open Questions
- ...

### Tác động
**Architecture:**  
**Data Model:**  
**UI/UX:**  
**Valuation Engine:**  
**Excel Compatibility:**  
**Security:**  

### Đầu vào vòng tiếp theo
...
```

------------------------------------------------------------------------

# 10. Vòng brainstorm kế tiếp dự kiến

Thiết kế **Information Architecture + Wireframe + Data Contract** cho
bốn màn hình lõi GĐ1:

1.  Khởi tạo hồ sơ & Quét GCN.
2.  TSTĐ Workbench.
3.  TSSS Workbench.
4.  Adjustment Workbench.

Đầu ra bắt buộc:

-   `UI field ↔ Database field ↔ Excel cell/range`.
-   GCN Field Mapping.
-   Historical Adjustment Observation Schema.
-   Validation rules.
-   Human-review gates.

**Lưu ý:** Trước khi bắt đầu vòng này phải thực hiện
`UPDATE-BEFORE-NEXT-BRAINSTORM GATE`.

---

## Quyết định đã chốt — Subject/TSSS Data Entry Interaction v0.1
**Thời điểm khóa:** 15/08/2026  
**Trạng thái:** **ĐÃ CHỐT**

- GCN/VBDLIS/manual cùng đi vào một canonical TSTĐ form; OCR/VBDLIS là nguồn pre-fill, không tạo workflow riêng.
- Extraction đi qua staging/reconciliation/human confirmation; provenance chi tiết nằm trong Context Drawer.
- Dữ liệu nhiều loại đất dùng `land_use_components[]`; đặc điểm phục vụ so sánh được bố trí gần nhau.
- Google Maps URL/tọa độ/pin normalize về canonical `lat/lng`.
- TSSS có Quick Entry + Expanded Entry; GĐ1 ưu tiên giá bán/chào bán, tỷ lệ thương lượng và giá sau thương lượng.
- Duplicate TSSS chỉ copy property/source data; không copy AdjustmentDecision, suggested/selected rate, indicated price hoặc quality metrics.
- Comparison View dùng kiểm tra dữ liệu, không đồng nhất Adjustment Grid.
- Property source data chỉ sửa tại canonical TSTĐ/TSSS form; Adjustment Grid reference dữ liệu và source-value cells là read-only.
- Source data thay đổi làm recompute suggestion/calculation nhưng **không overwrite human-selected adjustment**; giữ selected rate và đánh dấu cần review.
- Dependency invalidation + Case Readiness chỉ surface quyết định cần kiểm tra lại.
- Keyboard-first, autosave, inline calculation, numeric normalization theo locale Việt Nam.
- Validation: tolerant khi edit, validate khi blur, strict tại readiness/export.
- TSTĐ và TSSS có readiness policy khác nhau.

### 8 nguyên tắc khóa
1. GCN/VBDLIS/manual cùng đi vào canonical form.
2. TSTĐ nhập chi tiết; TSSS có Quick Entry + Expanded Entry.
3. Dữ liệu chỉ nhập một lần rồi reference sang Comparison/Adjustment/Excel.
4. Adjustment Grid không sửa source property data.
5. Duplicate TSSS tuyệt đối không copy adjustment decision.
6. Source data thay đổi recompute nhưng không overwrite quyết định hệ số của chuyên viên.
7. Dependency invalidation + Readiness surface các quyết định cần review.
8. Keyboard-first + autosave + inline calculation là behavior mặc định.

## DR — ConstructionAsset: Legal absence ≠ physical absence
**Trạng thái:** **ĐÃ CHỐT**

**Vấn đề:** GCN/VBDLIS không ghi nhận tài sản gắn liền với đất không chứng minh thực tế không có CTXD.

**Quyết định mới:**
- **Legal absence ≠ physical absence.**
- Tách `PropertyLegal.registered_attached_assets[]` và `PropertyPhysical.construction_assets[]`.
- CTXD thực tế có thể xác định từ khảo sát, ảnh, hồ sơ khác hoặc người dùng nhập.
- `legal_registration_status` là thuộc tính riêng của từng ConstructionAsset.
- CTXD không ghi nhận trên GCN vẫn có thể được định giá.
- UI phải ghi “GCN/VBDLIS không ghi nhận CTXD”, không tự kết luận “Không có CTXD”.
- Người dùng luôn có thể xác nhận không có CTXD thực tế hoặc thêm một/nhiều CTXD.

## DR — ConstructionAsset Valuation Treatment
**Trạng thái:** **ĐÃ CHỐT**

Mỗi `ConstructionAsset` có `valuation_treatment` độc lập với trạng thái pháp lý:

- `VALUE`: mô tả + chạy Construction Valuation Engine + tính giá trị.
- `DESCRIBE_ONLY`: mô tả CTXD nhưng không chạy Construction Valuation Engine và không cộng giá trị.
- `EXCLUDE`: CTXD không thuộc phạm vi xử lý hiện tại/chủ động loại khỏi nghiệp vụ.

`TotalConstructionValue = Σ value(ConstructionAsset) WHERE valuation_treatment = VALUE`

- `DESCRIBE_ONLY` là trạng thái nghiệp vụ hoàn chỉnh, không phải missing data.
- `DESCRIBE_ONLY` vẫn xuất hiện trong mô tả/Excel output khi template yêu cầu.
- `legal_registration_status` và `valuation_treatment` độc lập; `not_registered + VALUE` và `registered + DESCRIBE_ONLY` đều hợp lệ.
- UI cho chọn tối thiểu `Định giá CTXD` hoặc `Chỉ mô tả, không định giá`; khi chỉ mô tả thì ẩn/disable vùng TLCLCL, đơn giá xây mới, chi phí thay thế và giá trị còn lại.

> Có CTXD thực tế không đồng nghĩa phải định giá CTXD; không định giá CTXD cũng không đồng nghĩa được bỏ qua CTXD.

---

## Vòng tiếp theo — Implementation Boundary & MVP Cut
**Trạng thái:** **BẮT ĐẦU**

Mục tiêu: chia GĐ1 thành `MVP bắt buộc`, `MVP+ / Convenience`, và `Deferred`, nhưng không làm đứt closed appraisal loop.

Nguyên tắc:
- Không cắt thành phần làm đứt closed appraisal loop.
- Không cắt provenance/human-review/audit ở quyết định nghiệp vụ quan trọng.
- Deterministic calculation + Excel compatibility ưu tiên trước AI sophistication.
- Historical Learning phải có data contract từ đầu; intelligence có thể tăng dần.
- OCR/Maps/VBDLIS online là capability bổ trợ; core workflow phải tiếp tục khi offline.
- GĐ1 chưa xây kho BĐS/TSSS quy mô GĐ2 nhưng canonical data phải đủ cấu trúc để GĐ2 không cần migration phá vỡ.

---

## Quyết định đã chốt — Implementation Boundary & MVP Cut v0.1

**Thời điểm khóa:** 15/08/2026  
**Trạng thái:** **ĐÃ CHỐT**

### Định nghĩa MVP GĐ1

MVP phải cho phép một chuyên viên thực hiện closed appraisal loop:

`Tạo/quản lý hồ sơ -> nhập TSTĐ -> nhập TSSS -> CTXD -> Adjustment -> Valuation Result -> xuất workbook trình phê duyệt -> nhập lại workbook phê duyệt -> đóng hồ sơ`

mà không phải quay lại Excel để thực hiện nghiệp vụ chính.

### MVP bắt buộc

- Case Portfolio + lifecycle + autosave/resume.
- TSTĐ canonical form.
- GCN intake có staging/human review; QR optional.
- Location/Google Maps với canonical `lat/lng`.
- Multiple `ConstructionAssets[]` với `VALUE | DESCRIBE_ONLY | EXCLUDE`.
- TSSS Quick/Expanded Entry, duplicate an toàn, market normalization.
- Adjustment Factor Registry, sequential calculation, explicit zero, dependency invalidation.
- Historical Learning data contract + deterministic historical extraction/statistical suggestion ở mức tối thiểu đủ dùng.
- Comparable quality metrics + mức giá chỉ dẫn + human final decision.
- ExcelTemplateProfile, formula protection, checkpoint verification, workbook output.
- Approval Round-trip với immutable submission, diff, revision và human confirmation.

### MVP+ / Convenience

- VBDLIS integration sâu/tự động hơn.
- AI semantic matching nâng cao cho Historical Learning.
- Copy nhóm đặc điểm giữa TSSS.
- Advanced GCN conflict reconciliation/parcel geometry.
- TSSS historical picker nâng cao.
- Rich Context Drawer / advanced keyboard multi-cell operations.
- Approval analytics và prediction-error analytics.

### Deferred

- Kho dữ liệu BĐS/TSSS doanh nghiệp hoàn chỉnh của GĐ2.
- GIS intelligence nâng cao.
- Workflow Pattern Memory / AI tự thực hiện workflow.
- Dashboard doanh thu, CRM, mobile/web app, multi-user collaboration.
- Internal OCR server.
- Company Adjustment Rule Engine full runtime (chỉ giữ extension point trong GĐ1).

### Release Gate

Excel Compatibility là release gate: cùng một case phải đối chiếu CenValue Engine với workbook legacy theo các calculation checkpoints và rounding/tolerance đã khai báo. Sai vượt tolerance thì không coi slice/domain tương ứng là hoàn thành.

### Quyết định triển khai trung tâm — Vertical Slice

**ĐÃ CHỐT:** Không xây tuần tự theo module cô lập kiểu “xong OCR -> xong Maps -> xong AI”.

Walking skeleton đầu tiên:

`Create Case -> Manual TSTĐ -> Manual TSSS -> Adjustment -> Result -> Fill Excel`

Mục tiêu là chứng minh sớm ba rủi ro kiến trúc lớn nhất:

1. Canonical data model.
2. Valuation/calculation engine.
3. Excel compatibility/output adapter.

Sau walking skeleton mới cắm dần:

- GCN/VBDLIS -> TSTĐ.
- Google Maps -> Location.
- Historical Excel -> Suggested Adjustment.
- Returned Approval Workbook -> Approval Round-trip.

### Nguyên tắc

- Không cắt thành phần làm đứt closed appraisal loop.
- Deterministic calculation/Excel compatibility ưu tiên trước AI sophistication.
- Provenance/human review/audit ở các quyết định chính không được cắt.
- Online capability không được trở thành dependency bắt buộc của core.
- GĐ1 phải lưu canonical data đủ cấu trúc để GĐ2 không cần migration phá vỡ.

### Đầu vào vòng tiếp theo

Thiết kế `Engineering Roadmap & Epic Decomposition` theo vertical slices, bắt đầu từ Walking Skeleton và lần lượt mở rộng tới GCN/Maps, CTXD, Historical Learning, Approval Round-trip và pilot hardening.

---

## Design Closure — Gate A & Gate B workbook reverse-engineering

**Ngày:** 15/08/2026  
**Trạng thái:** **ĐANG THỰC HIỆN DESIGN CLOSURE**

### DR — Astryx reference trong CenValue Manager hiện tại

**Quyết định cũ:**  
Một số đoạn brainstorm trước mô tả `React/Astryx hiện có` trong CenValue Manager.

**Bằng chứng/vấn đề mới:**  
Audit repo `Reguluspt/New-project` xác nhận frontend hiện tại dùng React/Vite + Ant Design. Astryx chưa được tích hợp trong codebase hiện hành.

**Quyết định mới — ĐÃ CHỐT:**  
Astryx là **target design system của CenValue RE**, không phải UI component library được reuse trực tiếp từ CenValue Manager hiện tại. Reuse React/Vite + business UX knowledge; migrate visual/component layer từ Ant Design/custom CSS sang Astryx theo từng surface.

### Gate A — các baseline đã khóa

- Source code base/reference: `Reguluspt/New-project`.
- Runtime logical boundary: `Tauri Desktop -> React UI -> loopback-only local application service -> framework-independent RE domain -> adapters`.
- Flask được phép giữ làm transitional local application-service layer; không chuyển FastAPI chỉ vì preference công nghệ.
- New RE canonical persistence tách khỏi flat legacy `cases` table.
- Canonical Schema v1 khóa các boundary: AppraisalCase, Property, LandParcel/LandUseComponent, ConstructionAsset, ComparableProperty, AdjustmentDecision/Observation, ValuationResult, Approval, Provenance và CaseWorkspaceState.
- Local persistence thuộc SQLite family nhưng RE DB phải encrypted-at-rest; document vault encrypted; secret/key management theo Windows protection baseline; local API không bind public/LAN.

### DR — Reference date tính tuổi đời hiệu quả CTXD

**Quyết định cũ / Workbook behavior:**  
Workbook sample dùng `YEAR(NOW()) - construction_year`.

**Quyết định mới — ĐÃ CHỐT:**  
CenValue dùng năm của `AppraisalCase.appraisal_date`:

`effective_age_years = YEAR(appraisal_date) - construction_year`

**Lý do:**  
Kết quả phải deterministic và tái lập được khi mở lại hồ sơ sau nhiều năm.

**Tác động:**  
`appraisal_date` là calculation input bắt buộc trong calculation snapshot/approval snapshot. Excel adapter phải ngăn công thức volatile `NOW()` làm thay đổi hồ sơ đã đóng.

### Gate B — phát hiện workbook đã xác minh

#### CTXD
Đã reverse-engineer `Bangtinh` dòng 123–163:
- age-method remaining quality;
- expert/component remaining quality với fixed structural weights;
- average remaining quality;
- replacement cost;
- remaining construction value;
- CTXD total checkpoints.

#### Adjustment Engine
Đã reverse-engineer `Bangtinh` dòng 47–120.

**ĐÃ XÁC MINH:**
- C1–C11 của sample gồm: Pháp lý, Vị trí, Khoảng cách tương đối, Quy mô/diện tích, Mặt tiền, Chiều dài, Hình dáng, Giao thông, Môi trường kinh doanh, Hạ tầng kỹ thuật, Yếu tố bất lợi khác.
- `0%` là quyết định hợp lệ.
- Comparison label `Tương đồng/Kém hơn/Tốt hơn` được derive từ dấu của selected rate.
- Calculation không phải fully-compounded chain:
  - C1 tính trên unit price sau market/transaction normalization;
  - C2 tính trên kết quả sau C1;
  - C3–C11 trong sample tính adjustment amount trên **cùng base sau C1**, sau đó cộng dồn vào running result.
- Property source cells trong Adjustment Grid phải read-only; rate cells editable.

#### Comparable Quality Metrics
Đã khóa cách biểu diễn:
- `gross_adjustment_value = SUM(ABS(adjustment_amount_i))`
- `adjustment_count = COUNT(rate_i != 0)`
- `net_adjustment_value = SUM(adjustment_amount_i)`
- `adjustment_amplitude` lưu canonical min/max của **absolute non-zero rates**, không lưu chuỗi hiển thị `"5 - 10"` làm source of truth.

Workbook chọn TSSS có gross adjustment nhỏ nhất trong trường hợp bình thường. Nhánh average đặc biệt của sample chỉ kích hoạt khi 2 hoặc 3 gross-adjustment values bằng 0; không suy rộng thành rule average cho mọi equal non-zero minimum.

Human vẫn xác nhận mức giá chỉ dẫn cuối.

#### 15% control
Workbook tính:
`deviation_i = (indicated_price_i - average_indicated_price) / average_indicated_price`

Narrative yêu cầu mức chênh lệch không quá 15%, nhưng không có bằng chứng workbook tự sửa rate hay tự loại TSSS.

**ĐÃ CHỐT:** CenValue triển khai đây là Readiness/Quality validation:
`abs(deviation_i) <= 15%`.
Nếu vượt: `NEEDS_REVIEW`; không tự thay đổi adjustment.

#### External workbook link
Sample có một external link tại `Phieu TTTT!E5`, trỏ tới một workbook lịch sử và có cached value trùng `Nhập liệu!F9`.

**ĐÃ CHỐT baseline:** unknown external link không được trở thành runtime dependency. TemplateProfile phải inventory/sanitize known redundant links và fail-safe với unknown links.

### Excel recalculation baseline

- CenValue deterministic engine là source of truth.
- Preferred compatibility runner trên Windows: Microsoft Excel Desktop automation khi cài đặt sẵn.
- Mở workbook với update external links disabled trừ link được TemplateProfile cho phép.
- Full dependency rebuild/recalculation trước checkpoint comparison.
- Nếu Excel Desktop không khả dụng, core workflow vẫn chạy và có thể tạo workbook `RECALC_PENDING_EXCEL`, nhưng không được tuyên bố checkpoint verification PASS.
- Epic 1 release gate yêu cầu template fingerprint + mapping + canonical calculation + required checkpoint verification.

### Open Questions còn lại của Gate B

1. Freeze toàn bộ Workbook Mapping Matrix ngoài vùng Adjustment/CTXD.
2. Xác định đầy đủ template families và biến thể.
3. Freeze exact rounding/tolerance cho từng calculation checkpoint.
4. Xác định toàn bộ construction profiles/economic-life/reference-weight tables.
5. Xác định semantics của legal factor C1 trên các historical workbook khác vì sample này hard-code `Hoàn chỉnh`.
6. Trace market/transaction normalization upstream rows và final property value downstream.
7. Chốt Approval Returned Workbook mapping.

### Bước tiếp theo

Tiếp tục Gate B theo dependency-first:
`Market/Transaction normalization -> full Adjustment graph -> final land/property result -> Workbook Mapping Matrix -> Template fingerprint/family -> rounding/tolerance fixtures -> Walking Skeleton Acceptance Matrix`.

---

## Design Closure — Gate B Freeze + RoundingPolicy

**Ngày:** 15/08/2026  
**Trạng thái:** **GATE B ĐÃ KHÓA CHO WALKING SKELETON**

### RoundingPolicy — ĐÃ CHỐT

Người dùng yêu cầu CenValue cho phép chọn mức làm tròn thay vì cố định hoàn toàn theo workbook.

Canonical rule:

`raw_value -> RoundingPolicy -> rounded_value`

- Không được overwrite `raw_value`.
- Tách policy ít nhất cho `UNIT_PRICE` và `TOTAL_VALUE`.
- Mức hỗ trợ baseline:
  - NONE
  - 1.000 VND
  - 10.000 VND
  - 100.000 VND
  - 1.000.000 VND
  - 10.000.000 VND
  - CUSTOM_INCREMENT
- Thứ tự resolution:
  1. Case override do chuyên viên chọn.
  2. ExcelTemplateProfile default.
  3. Application default nếu template không quy định.
- Không yêu cầu nhập lý do khi đổi mức làm tròn, nhưng phải có audit trail.
- AI không được tự thay đổi rounding policy.
- N08-0038 default:
  - Unit price: 1.000 VND/m².
  - Final total value: 1.000.000 VND.

### Gate B — các contract đã khóa

- Appraisal-date effective-age thay cho volatile `YEAR(NOW())`.
- CTXD age/expert/average/replacement/remaning-value calculation chain.
- Adjustment Factor Registry C1–C11.
- Explicit 0% semantics.
- Adjustment calculation base/additive-running behavior.
- Comparable quality metrics.
- Exact adjustment-amplitude formula.
- 15% deviation là Readiness/Quality validation, không tự sửa adjustment.
- Indicated-price recommendation/selection model.
- Land + CTXD + final valuation chain.
- Phân biệt `total_value_before_rounding_vnd` và `final_appraised_value_vnd`.
- RoundingPolicy configurable theo hồ sơ.
- G181/G182 output-consumer contract.
- Stale external-link handling.
- ExcelTemplateProfile + formula fingerprint.
- Golden-case fixture/checkpoints.
- Microsoft Excel qualification protocol.
- Dependency classification boundary:
  `CANONICAL_INPUT | DERIVED | CONTROL | LEGACY_ONLY | OUT_OF_SCOPE`.

### Quyết định dependency

Không chuyển toàn bộ direct Excel references thành canonical fields.

Một dependency chỉ block Epic 1 khi nó ảnh hưởng mandatory Walking Skeleton checkpoint/output và không thể tái tạo từ:
`CANONICAL_INPUT + DERIVED + CONTROL`.

Unknown dependency phát hiện trong implementation phải fail-safe và được nâng thành design finding nếu làm thay đổi mandatory checkpoint.

### Gate B conclusion

**DESIGN READY / FROZEN FOR WALKING SKELETON.**

Exhaustive legacy-cell inventory tiếp tục là implementation evidence, không còn là blocker cho Engineering Foundation.

### Bước tiếp theo

Chuyển sang `Epic 0 — Engineering Foundation Design Freeze`, sau đó mới coding.

Lưu ý governance từ repo `Reguluspt/New-project`:
- Mọi source-code change phải được áp dụng/verify tại local Windows beta app `H:\CEN Manage` trước.
- Không tự publish/deploy GitHub/VPS nếu người dùng chưa chỉ đạo.

