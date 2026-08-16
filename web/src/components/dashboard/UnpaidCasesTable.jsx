import { Card, Table, Typography } from 'antd';

const { Title } = Typography;

const formatNumber = (value) => {
  if (value === undefined || value === null) return "0";
  return Math.round(value).toLocaleString('vi-VN');
};

const wrappedText = (text) => (
  <div style={{ whiteSpace: 'normal', overflowWrap: 'anywhere', lineHeight: 1.45 }}>
    {text || 'N/A'}
  </div>
);

export default function UnpaidCasesTable({ 
  data = [], 
  unpaidTotal = 0, 
  unpaidCount = 0, 
  periodLabel = ''
}) {
  const columns = [
    {
      title: 'Số HS',
      dataIndex: 'contract_number',
      key: 'contract_number',
      width: 210,
      render: (text) => (
        <div style={{ fontWeight: 700 }}>
          {wrappedText(text)}
        </div>
      ),
    },
    {
      title: 'Khách hàng',
      dataIndex: 'customer_info',
      key: 'customer_info',
      width: 500,
      render: wrappedText,
    },
    {
      title: 'Ngân hàng',
      dataIndex: 'source',
      key: 'source',
      width: 300,
      render: wrappedText,
    },
    {
      title: 'Còn lại',
      dataIndex: 'valuation_fee_number',
      key: 'valuation_fee_number',
      align: 'right',
      width: 150,
      render: (val) => <span>{formatNumber(val)}</span>,
    },
  ];

  return (
    <Card 
      style={{ borderRadius: 12, border: '1px solid #d8e7e5', height: '100%' }}
      bodyStyle={{ padding: '20px 22px' }}
    >
      <Title level={4} style={{ fontSize: 16, fontWeight: 700, marginBottom: 4 }}>
        Báo cáo công nợ chi tiết ({periodLabel})
      </Title>
      <div style={{ fontSize: 12, color: '#64748b', marginBottom: 16 }}>
        Số hồ sơ chưa thanh toán: {unpaidCount} | Tổng công nợ: {formatNumber(unpaidTotal)}
      </div>
      <Table
        size="small"
        columns={columns}
        dataSource={data}
        rowKey="case_id"
        pagination={{
          defaultPageSize: 10,
          showSizeChanger: true,
          pageSizeOptions: ['10', '20', '50'],
          showTotal: (total) => `${total} hồ sơ`,
        }}
        scroll={{ x: 1160 }}
        tableLayout="fixed"
        style={{ border: '1px solid #f1f5f9', borderRadius: 8, overflow: 'hidden' }}
      />
    </Card>
  );
}
