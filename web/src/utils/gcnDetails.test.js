import test from 'node:test';
import assert from 'node:assert/strict';
import { buildAppraisalMailNotes, normalizeGcnDetails } from './gcnDetails.js';


test('normalizes stored preliminary GCN extraction for the detail drawer', () => {
  const details = normalizeGcnDetails(JSON.stringify([{
    source_file_name: 'Thửa 1243, Tờ 212.pdf',
    so_thua_dat: { value: '1243' },
    so_to_ban_do: { value: '212' },
    dia_chi_thua_dat: { value: 'Xã Ea M’Droh, tỉnh Đắk Lắk' },
    so_giay_chung_nhan: { value: 'CS 123456' },
    so_vao_so_cap_giay_chung_nhan: { value: 'CH 00123' },
    ngay_cap_giay_chung_nhan: { value: '02/02/2025' },
    ten_chu_so_huu_cuoi_cung: { value: 'Nguyễn Văn A' },
    so_cccd_chu_so_huu_cuoi_cung: { value: '066000000001' },
    dia_chi_chu_so_huu_cuoi_cung: { value: 'Buôn Ma Thuột' },
  }]));

  assert.deepEqual(details[0], {
    source_file_id: '',
    source_file_name: 'Thửa 1243, Tờ 212.pdf',
    asset_index: 0,
    so_thua_dat: '1243',
    so_to_ban_do: '212',
    dia_chi_thua_dat: 'Xã Ea M’Droh, tỉnh Đắk Lắk',
    owner_name: 'Nguyễn Văn A',
    owner_address: 'Buôn Ma Thuột',
    owner_citizen_id: '066000000001',
    so_giay_chung_nhan: 'CS 123456',
    so_vao_so_cap_giay_chung_nhan: 'CH 00123',
    ngay_cap_giay_chung_nhan: '02/02/2025',
  });
});


test('fills appraisal mail notes from stored GCN details without duplicating existing content', () => {
  const gcnDetails = [{
    source_file_name: 'gcn.pdf',
    so_thua_dat: '1242',
    so_to_ban_do: '212',
    so_giay_chung_nhan: 'AA 001',
  }];
  const first = buildAppraisalMailNotes({
    personal_note: 'Ghi chú hồ sơ',
    gcn_details: gcnDetails,
  });

  assert.match(first, /Ghi chú hồ sơ/);
  assert.match(first, /GCN 1 - gcn\.pdf/);
  assert.match(first, /Số GCN: AA 001/);
  assert.equal(
    buildAppraisalMailNotes({ personal_note: first, gcn_details: gcnDetails }),
    first,
  );
});
