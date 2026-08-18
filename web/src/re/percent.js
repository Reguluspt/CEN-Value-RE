const DECIMAL_TEXT = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/;

function normalizeDecimalText(value) {
  if (typeof value !== 'string') {
    throw new TypeError('percentage value must be text');
  }
  const trimmed = value.trim();
  if (!trimmed || !DECIMAL_TEXT.test(trimmed)) {
    throw new TypeError('percentage value must be a plain finite decimal');
  }

  const negative = trimmed.startsWith('-');
  const unsigned = trimmed.replace(/^[+-]/, '');
  const [whole = '0', fractional = ''] = unsigned.split('.');
  const normalizedWhole = (whole || '0').replace(/^0+(?=\d)/, '') || '0';
  const normalizedFraction = fractional.replace(/0+$/, '');
  const isZero = /^0*$/.test(normalizedWhole) && /^0*$/.test(normalizedFraction);
  return {
    negative: negative && !isZero,
    whole: normalizedWhole,
    fractional: normalizedFraction,
  };
}

function shiftDecimal(value, places) {
  const parsed = normalizeDecimalText(value);
  const digits = `${parsed.whole}${parsed.fractional}`.replace(/^0+(?=\d)/, '') || '0';
  const currentPoint = parsed.whole.length;
  const nextPoint = currentPoint + places;

  let whole;
  let fractional;
  if (nextPoint <= 0) {
    whole = '0';
    fractional = `${'0'.repeat(-nextPoint)}${digits}`;
  } else if (nextPoint >= digits.length) {
    whole = `${digits}${'0'.repeat(nextPoint - digits.length)}`;
    fractional = '';
  } else {
    whole = digits.slice(0, nextPoint);
    fractional = digits.slice(nextPoint);
  }

  whole = whole.replace(/^0+(?=\d)/, '') || '0';
  fractional = fractional.replace(/0+$/, '');
  const zero = /^0+$/.test(whole) && !fractional;
  const sign = parsed.negative && !zero ? '-' : '';
  return `${sign}${whole}${fractional ? `.${fractional}` : ''}`;
}

export function displayPercentToFraction(value) {
  if (typeof value !== 'string') {
    throw new TypeError('display percentage must be text');
  }
  if (!value.trim()) {
    return null;
  }
  return shiftDecimal(value, -2);
}

export function fractionToDisplayPercent(value) {
  if (value === null || value === undefined || value === '') {
    return '';
  }
  return shiftDecimal(String(value), 2);
}
