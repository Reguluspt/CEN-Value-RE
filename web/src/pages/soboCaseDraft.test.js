import test from 'node:test';
import assert from 'node:assert/strict';
import { buildCaseDraftFromSobo } from './soboCaseDraft.js';


test('fills customer fields from Sơ bộ OCR fields', () => {
  const draft = buildCaseDraftFromSobo({
    asset_type: 'real_estate',
    asset_sub_type: 'single',
    owner_name: 'Nguyễn Văn A',
    owner_address: 'phường Đông Hà, tỉnh Quảng Trị',
    owner_citizen_id: '012345678901',
    note: 'Ghi chú nội bộ',
    response_content: '<table>Phản hồi sơ bộ</table>',
  });

  assert.equal(draft.customer_info, 'Nguyễn Văn A');
  assert.equal(draft.customer_address, 'phường Đông Hà, tỉnh Quảng Trị');
  assert.equal(draft.citizen_id, '012345678901');
  assert.equal(draft.asset_type, 'BĐS đặc thù khác');
  assert.equal(draft.personal_note, 'Ghi chú sơ bộ: Ghi chú nội bộ');
});


test('uses legacy customer field names as fallbacks', () => {
  const draft = buildCaseDraftFromSobo({
    asset_type: 'real_estate',
    customer_info: 'Trần Thị B',
    customer_address: 'Gia Lai',
    citizen_id: '123456789012',
  });

  assert.equal(draft.customer_info, 'Trần Thị B');
  assert.equal(draft.customer_address, 'Gia Lai');
  assert.equal(draft.citizen_id, '123456789012');
});


test('carries full GCN details and builds the appraisal mail note', () => {
  const draft = buildCaseDraftFromSobo({
    asset_type: 'real_estate',
    note: 'Khách hàng cần xử lý sớm',
    gcn_details: [
      {
        source_file_id: 'file-1',
        source_file_name: 'gcn-1.pdf',
        asset_index: 0,
        so_thua_dat: { value: '1242' },
        so_to_ban_do: { value: '212' },
        dia_chi_thua_dat: { value: 'Đắk Lắk' },
        ten_chu_so_huu_cuoi_cung: { value: 'Nguyễn Văn A' },
        so_cccd_chu_so_huu_cuoi_cung: { value: '012345678901' },
        so_giay_chung_nhan: { value: 'AA 001' },
        so_vao_so_cap_giay_chung_nhan: { value: 'CS 001' },
        ngay_cap_giay_chung_nhan: { value: '01/01/2026' },
      },
    ],
  });

  assert.equal(draft.gcn_details.length, 1);
  assert.equal(draft.gcn_details[0].so_giay_chung_nhan, 'AA 001');
  assert.match(draft.personal_note, /GCN 1 - gcn-1\.pdf/);
  assert.match(draft.personal_note, /Thửa: 1242 \| Tờ bản đồ: 212/);
  assert.match(draft.personal_note, /Số GCN: AA 001 \| Số vào sổ: CS 001 \| Ngày cấp: 01\/01\/2026/);
  assert.match(draft.personal_note, /Khách hàng cần xử lý sớm/);
});
