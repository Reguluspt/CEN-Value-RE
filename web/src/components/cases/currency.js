export const formatCurrency = (value) => {
  const amount = Number(value || 0);
  return Number.isFinite(amount)
    ? Math.round(amount).toLocaleString('vi-VN')
    : '0';
};

export const formatMillions = (value) => {
  const amount = Number(value || 0);
  const millions = Number.isFinite(amount) ? Math.round(amount / 1_000_000) : 0;
  return `${millions.toLocaleString('vi-VN')} Tr`;
};
