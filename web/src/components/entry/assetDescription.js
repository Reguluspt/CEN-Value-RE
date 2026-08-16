const LAND_REFERENCE_PATTERN = /(?:^|[\s,;])(thửa|thua)(?:\s|$)/iu;
const SHORT_REFERENCE_PATTERN = /^[\p{L}\p{N}_./-]+$/u;

const normalizeAssetLine = (line) => {
  let value = line.trim();
  // Strip old prefixes like [GCN 1], [GCN 2], etc.
  value = value.replace(/^\[GCN\s*\d+\]\s*/i, '').trim();
  // Strip existing bullet character if present
  value = value.replace(/^[•\-\*]\s*/, '').trim();
  if (!value) return '';

  if (!LAND_REFERENCE_PATTERN.test(value)) {
    const firstComma = value.indexOf(',');
    const secondComma = value.indexOf(',', firstComma + 1);
    if (firstComma >= 0 && secondComma >= 0) {
      const parcelNumber = value.slice(0, firstComma).trim();
      const mapSheetNumber = value.slice(firstComma + 1, secondComma).trim();
      const address = value.slice(secondComma + 1).trim();
      if (
        parcelNumber
        && mapSheetNumber
        && address
        && SHORT_REFERENCE_PATTERN.test(parcelNumber)
        && SHORT_REFERENCE_PATTERN.test(mapSheetNumber)
      ) {
        value = `Thửa đất số ${parcelNumber}, tờ bản đồ số ${mapSheetNumber}; tại địa chỉ ${address}`;
      }
    }
  }

  return `• ${value}`;
};

export const normalizeShortAssetDescription = (text) => {
  const lines = String(text || '')
    .split(/\r?\n/)
    .map(normalizeAssetLine)
    .filter(Boolean);

  return lines.join('\n');
};
