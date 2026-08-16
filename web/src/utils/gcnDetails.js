const extractedValue = (value) => (
  typeof value === 'object' && value !== null ? value.value || '' : value || ''
);

const detailValue = (detail, ...fields) => {
  for (const field of fields) {
    const value = String(extractedValue(detail?.[field])).trim();
    if (value) return value;
  }
  return '';
};

const parseDetails = (value) => {
  if (Array.isArray(value)) return value;
  if (typeof value !== 'string' || !value.trim()) return [];
  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
};

export const normalizeGcnDetails = (value) => parseDetails(value)
  .filter((detail) => detail && typeof detail === 'object')
  .map((detail, index) => ({
    source_file_id: String(detail.source_file_id || ''),
    source_file_name: String(detail.source_file_name || ''),
    asset_index: Number(detail.asset_index ?? index),
    so_thua_dat: detailValue(detail, 'so_thua_dat', 'so_thua'),
    so_to_ban_do: detailValue(detail, 'so_to_ban_do', 'so_to'),
    dia_chi_thua_dat: detailValue(detail, 'dia_chi_thua_dat', 'land_address'),
    owner_name: detailValue(detail, 'ten_chu_so_huu_cuoi_cung', 'owner_name'),
    owner_address: detailValue(detail, 'dia_chi_chu_so_huu_cuoi_cung', 'owner_address'),
    owner_citizen_id: detailValue(detail, 'so_cccd_chu_so_huu_cuoi_cung', 'owner_citizen_id', 'so_cccd'),
    so_giay_chung_nhan: detailValue(detail, 'so_giay_chung_nhan'),
    so_vao_so_cap_giay_chung_nhan: detailValue(detail, 'so_vao_so_cap_giay_chung_nhan'),
    ngay_cap_giay_chung_nhan: detailValue(detail, 'ngay_cap_giay_chung_nhan'),
  }));

export const buildGcnDetailsNote = (value) => normalizeGcnDetails(value)
  .map((detail, index) => {
    const heading = `GCN ${index + 1}${detail.source_file_name ? ` - ${detail.source_file_name}` : ''}`;
    return [
      heading,
      `Thửa: ${detail.so_thua_dat || 'N/A'} | Tờ bản đồ: ${detail.so_to_ban_do || 'N/A'}`,
      `Địa chỉ thửa đất: ${detail.dia_chi_thua_dat || 'N/A'}`,
      `Số GCN: ${detail.so_giay_chung_nhan || 'N/A'} | Số vào sổ: ${detail.so_vao_so_cap_giay_chung_nhan || 'N/A'} | Ngày cấp: ${detail.ngay_cap_giay_chung_nhan || 'N/A'}`,
      `Chủ sử dụng: ${detail.owner_name || 'N/A'} | CCCD: ${detail.owner_citizen_id || 'N/A'}`,
      `Địa chỉ chủ sử dụng: ${detail.owner_address || 'N/A'}`,
    ].join('\n');
  })
  .join('\n\n');

export const buildAppraisalMailNotes = (record) => {
  const existingNote = String(record?.personal_note || record?.notes || '').trim();
  const gcnNote = buildGcnDetailsNote(record?.gcn_details);
  if (!gcnNote || existingNote.includes(gcnNote)) return existingNote || gcnNote;
  return [existingNote, gcnNote].filter(Boolean).join('\n\n');
};
