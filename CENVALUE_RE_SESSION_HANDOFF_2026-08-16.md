# CENVALUE RE — SESSION HANDOFF
## 2026-08-16
## Tiếp tục từ E0-PR-001

### 1. Trạng thái chính thức
- Project: CenValue RE / CenValue Manager
- Repository: `Reguluspt/New-project`
- Gate B: **FROZEN / CLOSED**
- Gate C Pre-Implementation Design Audit: **PASS WITH CORRECTIVE**
- Audit findings: **0 BLOCKER / 3 MAJOR / 2 MINOR**
- Epic 0: **READY TO IMPLEMENT**
- E0-PR-001: **ACCEPTED / CORRECTIVE v1 VERIFIED / 6 TESTS PASSED / NOT PUBLISHED**
- E0-PR-002: **AUTHORIZED TO IMPLEMENT — ASTRYX INTEGRATION SPIKE**
- Bước tiếp theo: **Implement E0-PR-002**, then independent review/acceptance before E0-PR-003.

### 2. Governance
- Implementation/verification hiện được thực hiện **trên server trước**.
- `H:\CEN Manage` **không còn là gate bắt buộc**.
- Không publish GitHub/VPS nếu Project Owner chưa chỉ đạo.
- Không tự merge/approve.
- PR Plan hiện hành là source of truth; numbering/mô tả trong Independent Audit không thay thế PR Plan.
- Không brainstorm lại các quyết định đã khóa.

### 3. Kiến trúc đã khóa
Hexagonal/Clean Architecture:
`UI/API → Application → Domain → Ports ← Adapters`

Domain không phụ thuộc Flask, React/Tauri, SQLAlchemy, openpyxl/Excel libraries, AI SDKs, database frameworks hoặc infrastructure.

Không mở rộng legacy flat `cases` table làm canonical model.

Canonical conceptual model:
`Case → SubjectProperty(Parcel, Construction[]) + Comparable[](Evidence[], AdjustmentFactor[]) + ValuationResult + AuditTrail`

Excel là compatibility adapter/contract, không phải canonical domain model.

### 4. Các quyết định nghiệp vụ quan trọng
**Appraisal date:** dùng `appraisal_date`, không dùng `YEAR(NOW())`; kết quả deterministic/reproducible.

**CTXD:**
- GCN không có thông tin CTXD không được vội kết luận không có CTXD.
- CTXD có thể tồn tại nhưng chưa hoàn công và vẫn cần định giá.
- CTXD có 2 hướng: `VALUE` hoặc `DESCRIBE_ONLY`.
- Một TSTĐ có thể có nhiều CTXD.
- Chế độ duy tu/bảo dưỡng: người dùng tự đánh % theo quan sát thực tế; tỷ trọng kết cấu cố định.

**Adjustment 0%:**
- Không học từ mọi ô 0%.
- 0% có thể là đánh giá hợp lệ, nhất là các sai khác kích thước nhỏ.
- Phân biệt explicit 0% với unfilled/null.

**Historical Learning:**
- Người dùng lọc file đầu vào một lượt trước.
- Learning chỉ học từ dataset đã được lọc/curated.

**Google Maps:**
- Người dùng dán goo.gl/maps link.
- Phần mềm tự chuyển thành latitude/longitude.
- Giữ raw URL để provenance.

**GCN/QR/VBDLIS:**
- QR có thể tra cứu tại `https://tracuuqr.vbdlis.vn/`.
- Nếu ảnh GCN không đủ chất lượng để quét QR: bỏ qua QR step, không block workflow.
- Không tập trung xử lý đăng ký/xóa đăng ký thế chấp.

**Hồ sơ:**
- Nhiều hồ sơ.
- Lưu hồ sơ dở dang.
- Chuyển qua hồ sơ khác.
- Quay lại hồ sơ cũ.
- Nhập lại kết quả sau khi nhận file phê duyệt.

**Rounding:**
- Có chức năng chọn mức làm tròn.
- Rounding Policy configurable.
- Giữ raw/unrounded và final rounded.

**Human approval:**
- AI không được APPROVE/phát hành chứng thư.
- Human-in-the-loop là boundary bất biến.

### 5. Audit Correctives đã khóa
**FIND-E0-01 — Percentage (MAJOR)**
- Domain lưu fraction: `5% = Decimal("0.05")`.
- Display/input adapter mới chuyển sang percent representation.

**FIND-E0-02 — Valuation naming (MAJOR)**
Canonical:
- `total_value_before_rounding_vnd`
- `final_appraised_value_vnd`
Không tạo duplicate `raw_*`/`rounded_*` serialized fields.

**FIND-E0-03 — Excel fingerprint (MAJOR)**
- Structural-critical: strict/blocking.
- Metadata: lenient/warning.

**FIND-E0-04 — Astryx CSS (MINOR)**
- Scoped RE surface/layer.
- Không phá legacy Ant Design.
- Không giả định API Astryx khi chưa xác minh package thực tế.

**FIND-E0-05 — GeoLocation (MINOR)**
- `latitude: Decimal | None`
- `longitude: Decimal | None`
- `raw_maps_url: str | None`
- WGS84 validation latitude [-90,90], longitude [-180,180].

### 6. E0-PR-001 implementation + corrective v1
Đã tạo additive bounded context:

`src/re/`
- `domain/cases`
- `domain/property`
- `domain/construction`
- `domain/adjustment`
- `domain/valuation`
- `domain/approval`
- `domain/common`
- `application/commands`
- `application/queries`
- `application/services`
- `ports/persistence.py`
- `ports/excel.py`
- `ports/providers.py`
- `adapters/persistence`
- `adapters/excel`
- `adapters/providers`

Tests:
- `tests/re/test_architecture_boundaries.py`
- `tests/re/test_package_imports.py`

Baseline server result before corrective:
**4 passed**

Corrective v1 result:
**6 passed in 0.03s**

Architecture tests hiện kiểm soát:
1. Domain không import forbidden frameworks/infrastructure/provider/database/adapters.
2. Core không import ngược adapters.
3. `src.re.*` được normalize về canonical `re.*` trước khi guard kiểm tra.
4. Relative/alias import forms như `from ...adapters ...` và `from src.re import adapters` không được bypass guard.
5. Required RE packages tồn tại.
6. RE core packages import được.

Mutation evidence:
- `from src.re.adapters import persistence` trong Domain → test FAIL đúng yêu cầu.
- `from ...adapters import persistence` trong Domain → test FAIL đúng yêu cầu.
- Sau khi restore mutation → final focused suite 6/6 green.

Corrective evidence chỉ chuẩn bị cho Review/Acceptance; implementer không tự kết luận ACCEPTED/PASS.

Chưa làm trong PR-001:
- Percentage/Money/RoundingPolicy.
- Astryx.
- ExcelTemplateProfile.
- concrete persistence.
- API/Flask wiring.
- valuation formulas/business entities hoàn chỉnh.

### 7. E0-PR-001 artifacts
Đã tạo:
- `E0-PR-001_SERVER_IMPLEMENTATION.zip`
- `E0-PR-001_SERVER_IMPLEMENTATION.patch`
- `E0_PR_001_IMPLEMENTATION_REPORT.md`
- `implementation/E0-PR-001_CORRECTIVE_v1.patch`
- `implementation/E0-PR-001_CORRECTED_IMPLEMENTATION_v1.zip`
- `implementation/E0_PR_001_CORRECTIVE_REPORT_v1.md`
- `evidence/E0_PR_001_ACCEPTANCE_EVIDENCE_v1.md`
- mutation/test logs dưới `evidence/`

Chưa push/commit GitHub.

Lưu ý: server/container không clone GitHub trực tiếp được do outbound DNS/network restriction. Repository đã được inspect qua connected GitHub source; implementation được tạo dưới dạng surgical additive patch/worktree payload.

### 8. Design/Audit documents quan trọng
Epic 0:
- `EPIC_0_DESIGN_FREEZE_v1.md`
- `EPIC_0_ENGINEERING_FOUNDATION_PACKET_v1.md`
- `EPIC_0_PR_PLAN_v1.md`
- `EPIC_0_ACCEPTANCE_MATRIX_v1.md`

Audit:
- `EPIC_0_PRE_IMPLEMENTATION_DESIGN_AUDIT.md`
- `EPIC_0_PRE_IMPLEMENTATION_CORRECTIVE_REGISTER_v1.md`
- `GATE_C_PRE_IMPLEMENTATION_AUDIT_STATUS_v1.md`

Gate B:
- `GATE_B_CLOSURE_REPORT_v1.md`
- `GATE_B_STATUS_v0.3.md`
- `GATE_B13_ROUNDING_POLICY_v1.md`
- `GATE_B14_DEPENDENCY_CLASSIFICATION_BASELINE.md`
- `GATE_B1_BANGTINH_123_163_DISCOVERY.md`
- `GATE_B1_CTXD_CALCULATION_CONTRACT_v0.1.md`
- `GATE_B2_ADJUSTMENT_MAPPING_AND_CALCULATION_v0.1.md`
- `GATE_B3_INDICATED_PRICE_SELECTION_v0.1.md`
- `GATE_B4_QUALITY_METRICS_AND_15_PERCENT_RULE.md`
- `GATE_B4_ROUNDING_RECALCULATION_STRATEGY_v0.1.md`
- `GATE_B5_EXTERNAL_LINK_CLASSIFICATION.md`
- `GATE_B6_WALKING_SKELETON_MAPPING_MATRIX_v0.1.md`
- `GATE_B7_FINAL_VALUATION_CONTRACT_v0.1.md`
- `GATE_B8_ADJUSTMENT_FACTOR_REGISTRY_v1.md`
- `GATE_B10_OUTPUT_CONSUMER_CONTRACT_v1.md`
- `GATE_B11_UNMAPPED_REQUIRED_INPUTS.md`
- `GATE_B12_EXCEL_QUALIFICATION_PROTOCOL_v1.md`
- `EXCEL_TEMPLATE_PROFILE_v1.md`
- `EXCEL_TEMPLATE_FINGERPRINT_v1.md`
- `GOLDEN_CASE_CANONICAL_FIXTURE_v0.1.json`
- `GOLDEN_CASE_CHECKPOINT_MANIFEST_v0.2.md`
- `DECISION_REVISION_APPRAISAL_DATE_EFFECTIVE_AGE.md`

### 9. Next workflow
E0-PR-001 đã **ACCEPTED** bởi independent review.

**CURRENT = E0-PR-002 Astryx Integration Spike**

Server payload v1 đã được chuẩn bị trên frontend baseline `cc6ad5fcc15703ae31fd9f2e8ee78c972f06d2ff` với:
- isolated/protected/lazy `/re` route;
- Astryx `AppShell`, `SideNav`, `FormLayout`, `TextInput`;
- Neutral theme;
- exact pins `@astryxdesign/core@0.2.0`, `@astryxdesign/theme-neutral@0.2.0`, `@stylexjs/stylex@0.19.0`;
- scoped CSS compatibility baseline, không import global Astryx reset;
- static verifier green;
- patch apply-check clean trên baseline frontend.

Runtime acceptance vẫn **PENDING** vì server shell không resolve GitHub/npm DNS. Chưa được tuyên bố PASS/ACCEPTED cho PR-002. Networked worktree phải cập nhật `package-lock.json`, chạy `npm run verify:re-astryx`, `npm run lint`, `npm run build`, sau đó browser-smoke `/re` và legacy `/dashboard` + `/cases`.

Nếu runtime evidence đạt và independent reviewer ACCEPT → mới chuyển E0-PR-003 Decimal + RoundingPolicy.

### 10. Quy tắc token/workflow
Không đọc lại hàng chục tài liệu nếu không cần.
Ưu tiên:
1. Handoff này.
2. PR đang xử lý.
3. Acceptance Matrix.
4. PR Plan.
5. Finding/corrective liên quan.
6. Gate-B contract chỉ khi PR cần.

### 11. One-line status
**CenValue RE = Gate B FROZEN → Gate C PASS WITH CORRECTIVE → E0-PR-001 ACCEPTED → E0-PR-002 server payload/static guard GREEN → runtime build/browser evidence PENDING.**


### E0-PR-001 Acceptance Verdict — 2026-08-16
Independent review accepted DOC-01..DOC-05, FIX-01 and E0-PR-001-C01. The architecture guard mutation proofs were accepted and the clean focused suite was 6/6 green. Stage gate verdict: **E0-PR-001 ACCEPTED**. E0-PR-002 is now authorized.
