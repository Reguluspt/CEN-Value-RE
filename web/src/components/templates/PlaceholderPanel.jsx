import { useMemo, useState } from 'react';
import { Alert, Button, Collapse, Empty, Input, Spin, Tag, Tooltip, Typography, message } from 'antd';
import { CheckCircleOutlined, CopyOutlined, ReloadOutlined, SearchOutlined, TagsOutlined, WarningOutlined } from '@ant-design/icons';
import placeholderCatalog from './placeholderCatalog';

const { Text } = Typography;

function tokens(values) {
  return (values || []).map((value) => `{{${value}}}`).join(', ');
}

export default function PlaceholderPanel({ detail, loading, onRefresh }) {
  const [query, setQuery] = useState('');
  const normalizedQuery = query.trim().toLocaleLowerCase('vi');
  const groups = useMemo(() => {
    const result = new Map();
    placeholderCatalog.forEach((item) => {
      const haystack = `${item.key} ${item.label} ${item.source}`.toLocaleLowerCase('vi');
      if (normalizedQuery && !haystack.includes(normalizedQuery)) return;
      if (!result.has(item.group)) result.set(item.group, []);
      result.get(item.group).push(item);
    });
    return [...result.entries()];
  }, [normalizedQuery]);

  const warningCount = (detail?.unknown_placeholders?.length || 0)
    + (detail?.invalid_placeholders?.length || 0)
    + (detail?.missing_placeholders?.length || 0);

  const copyPlaceholder = async (key) => {
    const value = `{{${key}}}`;
    try {
      await navigator.clipboard.writeText(value);
      message.success(`Đã sao chép ${value}`);
    } catch {
      message.error('Không thể sao chép thẻ vào clipboard');
    }
  };

  const items = groups.map(([group, entries]) => ({
    key: group,
    label: `${group} (${entries.length})`,
    children: (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {entries.map((item) => (
          <div key={item.key} style={{ padding: '8px 0', borderBottom: '1px solid #f0f0f0' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Text code style={{ flex: 1, fontSize: 12 }}>{`{{${item.key}}}`}</Text>
              <Tooltip title="Sao chép thẻ">
                <Button size="small" icon={<CopyOutlined />} onClick={() => copyPlaceholder(item.key)} />
              </Tooltip>
            </div>
            <div style={{ marginTop: 5, fontSize: 12, fontWeight: 600, color: '#334155' }}>{item.label}</div>
            <div style={{ marginTop: 2, fontSize: 12, lineHeight: 1.4, color: '#64748b' }}>{item.source}</div>
          </div>
        ))}
      </div>
    ),
  }));

  return (
    <aside style={{ width: 360, minWidth: 360, height: '100%', borderLeft: '1px solid #d9d9d9', background: '#fff', overflowY: 'auto' }}>
      <div style={{ position: 'sticky', top: 0, zIndex: 1, padding: 16, background: '#fff', borderBottom: '1px solid #f0f0f0' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 700 }}>
          <TagsOutlined style={{ color: '#007f7a' }} />
          <span style={{ flex: 1 }}>Thẻ tự điền</span>
          <Tooltip title="Đọc lại file Word đã lưu">
            <Button size="small" icon={<ReloadOutlined />} loading={loading} onClick={onRefresh}>Kiểm tra lại</Button>
          </Tooltip>
        </div>
        <div style={{ marginTop: 6, fontSize: 12, color: '#64748b' }}>
          Sao chép thẻ rồi dán vào vị trí cần điền trong Word.
        </div>
        <Input
          allowClear
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          prefix={<SearchOutlined />}
          placeholder="Tìm tên thẻ hoặc nguồn dữ liệu..."
          style={{ marginTop: 12 }}
        />
      </div>

      <div style={{ padding: 12 }}>
        {loading && !detail ? (
          <div style={{ padding: 32, textAlign: 'center' }}><Spin /></div>
        ) : warningCount > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 12 }}>
            {(detail?.invalid_placeholders?.length || 0) > 0 && (
              <Alert type="error" showIcon icon={<WarningOutlined />} message="Thẻ sai cú pháp" description={detail.invalid_placeholders.join(', ')} />
            )}
            {(detail?.unknown_placeholders?.length || 0) > 0 && (
              <Alert type="warning" showIcon message="Thẻ chưa được hỗ trợ" description={tokens(detail.unknown_placeholders)} />
            )}
            {(detail?.missing_placeholders?.length || 0) > 0 && (
              <Alert type="warning" showIcon message="Mẫu đang thiếu thẻ bắt buộc" description={tokens(detail.missing_placeholders)} />
            )}
          </div>
        ) : detail ? (
          <Alert
            type="success"
            showIcon
            icon={<CheckCircleOutlined />}
            message={`Đã kiểm tra ${detail.placeholders?.length || 0} thẻ trong mẫu`}
            style={{ marginBottom: 12 }}
          />
        ) : null}

        {items.length > 0 ? (
          <Collapse size="small" items={items} defaultActiveKey={items.slice(0, 2).map((item) => item.key)} />
        ) : (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="Không tìm thấy thẻ phù hợp" />
        )}
        <div style={{ marginTop: 12 }}>
          <Tag color="blue">{placeholderCatalog.length} thẻ được hỗ trợ</Tag>
        </div>
      </div>
    </aside>
  );
}
