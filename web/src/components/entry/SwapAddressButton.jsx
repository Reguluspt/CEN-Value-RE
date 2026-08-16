import React, { useState } from 'react';
import { Button, Tooltip, message } from 'antd';
import { SwapOutlined } from '@ant-design/icons';
import { convertAddress } from '../../api/entry';

export default function SwapAddressButton({ value, onSwap, mode = 'annotate', size = 'small', style = {} }) {
  const [loading, setLoading] = useState(false);

  const handleSwap = async (e) => {
    if (e) e.preventDefault();
    const currentVal = String(value || '').trim();
    if (!currentVal) {
      message.warning('Vui lòng nhập hoặc chọn địa chỉ trước khi hoán đổi.');
      return;
    }

    // Instant local toggle if already annotated anywhere
    if (currentVal.includes('(Nay là ') || currentVal.includes('(nay là ')) {
      const reverted = currentVal
        .split('\n')
        .map((line) => line.replace(/\s*\((?:Nay|nay) là [^)]+\)/, '').trim())
        .join('\n');
      onSwap(reverted);
      message.success('Đã hoán đổi về địa chỉ cũ gốc!');
      return;
    }

    setLoading(true);
    try {
      const res = await convertAddress(currentVal, mode);
      if (res.data && res.data.converted) {
        onSwap(res.data.converted);
        if (res.data.is_annotated) {
          message.success('Đã hoán đổi sang địa chỉ mới (Nay là...)!');
        } else if (res.data.matched) {
          message.success('Đã hoán đổi địa chỉ thành công!');
        } else {
          message.info('Địa chỉ giữ nguyên (chưa có tên Phường/Xã hoặc không thuộc diện đổi tên ĐVHC).');
        }
      } else {
        message.info('Không có dữ liệu thay đổi cho địa chỉ này.');
      }
    } catch (err) {
      console.error('Lỗi quy đổi địa chỉ:', err);
      message.warning('Chưa thể kết nối dịch vụ quy đổi địa chỉ (Vui lòng khởi động lại dịch vụ backend VPS).');
    } finally {
      setLoading(false);
    }

  };

  return (
    <Tooltip title="Hoán đổi địa chỉ mới / cũ (Theo cú pháp: Nay là...)">
      <Button
        type="text"
        size={size}
        icon={<SwapOutlined style={{ color: '#007f7a', fontSize: '15px' }} />}
        loading={loading}
        onClick={handleSwap}
        style={{
          borderRadius: 4,
          padding: '0 4px',
          ...style
        }}
      />
    </Tooltip>
  );
}
