import { Card, Col, Row, Typography } from 'antd';

const { Title } = Typography;

const formatMillion = (value) => {
  const million = Math.round(Number(value || 0) / 1_000_000);
  return million.toLocaleString('vi-VN');
};

export default function CollectionStatusDonut({
  paid = 0,
  unpaid = 0,
  periodLabel = '',
}) {
  const total = Number(paid || 0) + Number(unpaid || 0);
  const paidPercent = total > 0 ? (Number(paid || 0) / total) * 100 : 0;
  const data = [
    { label: 'Đã thu', value: Number(paid || 0), color: '#047857' },
    { label: 'Công nợ', value: Number(unpaid || 0), color: '#c2413d' },
  ];
  const gradient = total > 0
    ? `conic-gradient(#047857 0% ${paidPercent.toFixed(2)}%, #c2413d ${paidPercent.toFixed(2)}% 100%)`
    : 'conic-gradient(#e2e8f0 0% 100%)';

  return (
    <Card
      style={{ borderRadius: 12, border: '1px solid #d8e7e5', height: '100%' }}
      bodyStyle={{ padding: '20px 22px' }}
    >
      <Title level={4} style={{ fontSize: 16, fontWeight: 700, marginBottom: 4 }}>
        Cơ cấu thu tiền
      </Title>
      <div style={{ fontSize: 12, color: '#64748b', marginBottom: 20 }}>
        Tỷ lệ đã thu và công nợ {periodLabel || 'theo bộ lọc hiện tại'}.
      </div>

      <Row gutter={[16, 16]} align="middle" style={{ minHeight: 220 }}>
        <Col xs={24} sm={10} style={{ display: 'flex', justifyContent: 'center' }}>
          <div
            style={{
              position: 'relative',
              width: 170,
              height: 170,
              borderRadius: '50%',
              background: gradient,
            }}
          >
            <div
              style={{
                position: 'absolute',
                inset: 42,
                borderRadius: '50%',
                background: '#ffffff',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.05)',
              }}
            >
              <b style={{ fontSize: 22, fontWeight: 850, color: '#0f172a', lineHeight: 1.1 }}>
                {Math.round(paidPercent)}%
              </b>
              <span style={{ fontSize: 11, color: '#64748b', fontWeight: 600, marginTop: 4 }}>
                Đã thu
              </span>
            </div>
          </div>
        </Col>

        <Col xs={24} sm={14}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {data.map((item) => {
              const percent = total > 0 ? (item.value / total) * 100 : 0;
              return (
                <div
                  key={item.label}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: 12,
                    fontSize: 12,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span
                      style={{
                        width: 10,
                        height: 10,
                        borderRadius: 3,
                        background: item.color,
                      }}
                    />
                    <span style={{ color: '#475569', fontWeight: 600 }}>{item.label}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                    <span style={{ color: '#64748b', fontWeight: 600 }}>
                      {formatMillion(item.value)} Tr
                    </span>
                    <span style={{ color: '#0f172a', fontWeight: 700, width: 45, textAlign: 'right' }}>
                      {percent.toFixed(1)}%
                    </span>
                  </div>
                </div>
              );
            })}
            <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: 12, color: '#64748b', fontSize: 12 }}>
              Tổng giá trị theo dõi: <b style={{ color: '#0f172a' }}>{formatMillion(total)} Tr</b>
            </div>
          </div>
        </Col>
      </Row>
    </Card>
  );
}
