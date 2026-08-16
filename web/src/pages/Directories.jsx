import { useEffect } from 'react';
import { Tabs, Typography } from 'antd';
import {
  ApartmentOutlined,
  BankOutlined,
  SendOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import OptionDirectory from '../components/directories/OptionDirectory';
import Delivery from './Delivery';
import Organizations from './Organizations';

const VALID_TABS = new Set([
  'organizations',
  'delivery',
  'staff',
  'sources',
]);

export default function Directories() {
  const { tab } = useParams();
  const navigate = useNavigate();
  const activeTab = VALID_TABS.has(tab) ? tab : 'organizations';

  useEffect(() => {
    if (tab !== activeTab) {
      navigate(`/directories/${activeTab}`, { replace: true });
    }
  }, [activeTab, navigate, tab]);

  const items = [
    {
      key: 'organizations',
      label: (
        <span>
          <BankOutlined /> Tổ chức
        </span>
      ),
      children: <Organizations embedded />,
    },
    {
      key: 'delivery',
      label: (
        <span>
          <SendOutlined /> Chuyển phát
        </span>
      ),
      children: <Delivery embedded />,
    },
    {
      key: 'staff',
      label: (
        <span>
          <TeamOutlined /> Chuyên viên nghiệp vụ
        </span>
      ),
      children: (
        <OptionDirectory
          field="valuation_staff"
          title="Danh bạ chuyên viên nghiệp vụ"
          description="Quản lý danh sách chuyên viên được lựa chọn khi nhập và xử lý hồ sơ."
          itemLabel="chuyên viên"
        />
      ),
    },
    {
      key: 'sources',
      label: (
        <span>
          <ApartmentOutlined /> Nguồn đối tác
        </span>
      ),
      children: (
        <OptionDirectory
          field="source"
          title="Danh bạ nguồn đối tác"
          description="Quản lý ngân hàng, chi nhánh và các nguồn giới thiệu hồ sơ."
          itemLabel="nguồn đối tác"
        />
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <Typography.Title level={2} style={{ margin: 0 }}>
          Danh bạ
        </Typography.Title>
        <Typography.Paragraph
          type="secondary"
          style={{ margin: '6px 0 0', maxWidth: 760 }}
        >
          Một khu vực thống nhất để quản lý các thông tin dùng chung trong toàn
          bộ quy trình nhập hồ sơ, phát hành và chuyển phát.
        </Typography.Paragraph>
      </div>

      <div
        style={{
          background: '#fff',
          border: '1px solid #dce8e6',
          borderRadius: 14,
          padding: '4px 24px 24px',
        }}
      >
        <Tabs
          activeKey={activeTab}
          items={items}
          onChange={(key) => navigate(`/directories/${key}`)}
          size="large"
          tabBarStyle={{ marginBottom: 24 }}
        />
      </div>
    </div>
  );
}
