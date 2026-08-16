import { buildGcnDetailsNote, normalizeGcnDetails } from '../utils/gcnDetails.js';

export const buildCaseDraftFromSobo = (record) => {
  let gcnDetails = normalizeGcnDetails(record.gcn_details);
  if (!gcnDetails.length && (
    record.so_thua || record.so_to || record.dia_chi || record.so_giay_chung_nhan
  )) {
    gcnDetails = normalizeGcnDetails([{
      so_thua_dat: record.so_thua || '',
      so_to_ban_do: record.so_to || '',
      dia_chi_thua_dat: record.dia_chi || '',
      owner_name: record.owner_name || '',
      owner_address: record.owner_address || '',
      owner_citizen_id: record.owner_citizen_id || '',
      so_giay_chung_nhan: record.so_giay_chung_nhan || '',
      so_vao_so_cap_giay_chung_nhan: record.so_vao_so_cap_giay_chung_nhan || '',
      ngay_cap_giay_chung_nhan: record.ngay_cap_giay_chung_nhan || '',
    }]);
  }

  const primaryGcn = gcnDetails[0] || {};
  const ownerName = record.owner_name || primaryGcn.owner_name || record.customer_info || record.chu_so_huu || '';
  const ownerAddress = record.owner_address || primaryGcn.owner_address || record.customer_address || '';
  const ownerCitizenId = record.owner_citizen_id || primaryGcn.owner_citizen_id || record.citizen_id || '';
  const assetDescription = record.asset_type === 'machinery'
    ? (record.equipment_name || record.note || '')
    : [
        (record.so_thua || primaryGcn.so_thua_dat) ? `Thửa đất số ${record.so_thua || primaryGcn.so_thua_dat}` : '',
        (record.so_to || primaryGcn.so_to_ban_do) ? `tờ bản đồ số ${record.so_to || primaryGcn.so_to_ban_do}` : '',
        (record.dia_chi || primaryGcn.dia_chi_thua_dat) ? `tại ${record.dia_chi || primaryGcn.dia_chi_thua_dat}` : '',
      ].filter(Boolean).join(', ');

  return {
    customer_type: 'individual',
    customer_info: ownerName,
    customer_address: ownerAddress,
    citizen_id: ownerCitizenId,
    owner_name: ownerName,
    owner_address: ownerAddress,
    owner_citizen_id: ownerCitizenId,
    source: record.source || '',
    asset_type: record.asset_type === 'machinery' ? 'Máy móc thiết bị' : 'BĐS đặc thù khác',
    asset_description: assetDescription,
    so_thua_dat: record.so_thua || primaryGcn.so_thua_dat || '',
    so_to_ban_do: record.so_to || primaryGcn.so_to_ban_do || '',
    dia_chi_thua_dat: record.dia_chi || primaryGcn.dia_chi_thua_dat || '',
    gcn_details: gcnDetails,
    personal_note: [
      buildGcnDetailsNote(gcnDetails),
      record.note ? `Ghi chú sơ bộ: ${record.note}` : '',
    ].filter(Boolean).join('\n\n'),
    original_file_path: record.attachment_paths || '',
    case_status: 'Đang xử lý',
    payment_status: 'Chưa thanh toán',
    execution_month: `${String(new Date().getMonth() + 1).padStart(2, '0')}/${new Date().getFullYear()}`,
  };
};
