import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Alert,
  Button,
  Form,
  Input,
  message,
  Modal,
  Popconfirm,
  Space,
  Table,
  Tag,
  Tooltip,
  Typography,
} from 'antd';
import {
  DeleteOutlined,
  EditOutlined,
  LockOutlined,
  PlusOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import {
  addFormOption,
  deleteFormOption,
  getCustomFormOptions,
  getFormOptions,
  updateFormOption,
} from '../../api/entry';

const { Text } = Typography;

export default function OptionDirectory({
  field,
  title,
  description,
  itemLabel,
}) {
  const [values, setValues] = useState([]);
  const [customValues, setCustomValues] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [search, setSearch] = useState('');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingValue, setEditingValue] = useState(null);
  const [form] = Form.useForm();

  const fetchValues = useCallback(async () => {
    setLoading(true);
    try {
      const [optionsResponse, customResponse] = await Promise.all([
        getFormOptions(),
        getCustomFormOptions(),
      ]);
      setValues(optionsResponse.data?.[field] || []);
      setCustomValues(customResponse.data?.[field] || []);
    } catch (error) {
      message.error(
        error.response?.data?.error || `Không thể tải ${title.toLowerCase()}`,
      );
    } finally {
      setLoading(false);
    }
  }, [field, title]);

  useEffect(() => {
    // Initial API synchronization for this directory tab.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchValues();
  }, [fetchValues]);

  const customValueSet = useMemo(
    () => new Set(customValues),
    [customValues],
  );

  const rows = useMemo(() => {
    const normalizedSearch = search.trim().toLocaleLowerCase('vi');
    return values
      .filter(
        (value) =>
          !normalizedSearch ||
          value.toLocaleLowerCase('vi').includes(normalizedSearch),
      )
      .map((value) => ({
        key: value,
        value,
        isCustom: customValueSet.has(value),
      }));
  }, [customValueSet, search, values]);

  const openAddModal = () => {
    setEditingValue(null);
    form.resetFields();
    setModalOpen(true);
  };

  const openEditModal = (value) => {
    setEditingValue(value);
    form.setFieldsValue({ value });
    setModalOpen(true);
  };

  const handleSave = async () => {
    const formValues = await form.validateFields();
    const nextValue = formValues.value.trim();
    setSaving(true);
    try {
      if (editingValue) {
        await updateFormOption(field, editingValue, nextValue);
        message.success(`Đã cập nhật ${itemLabel}`);
      } else {
        await addFormOption(field, nextValue);
        message.success(`Đã thêm ${itemLabel}`);
      }
      setModalOpen(false);
      form.resetFields();
      await fetchValues();
    } catch (error) {
      message.error(
        error.response?.data?.error || `Không thể lưu ${itemLabel}`,
      );
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (value) => {
    try {
      await deleteFormOption(field, value);
      message.success(`Đã xóa ${itemLabel}`);
      await fetchValues();
    } catch (error) {
      message.error(
        error.response?.data?.error || `Không thể xóa ${itemLabel}`,
      );
    }
  };

  const columns = [
    {
      title: itemLabel.charAt(0).toUpperCase() + itemLabel.slice(1),
      dataIndex: 'value',
      key: 'value',
      render: (value) => <Text strong>{value}</Text>,
    },
    {
      title: 'Nguồn dữ liệu',
      dataIndex: 'isCustom',
      key: 'source',
      width: 180,
      render: (isCustom) =>
        isCustom ? (
          <Tag color="cyan">Danh bạ hợp nhất</Tag>
        ) : (
          <Tag icon={<LockOutlined />}>Dữ liệu kế thừa</Tag>
        ),
    },
    {
      title: 'Thao tác',
      key: 'actions',
      width: 130,
      align: 'right',
      render: (_, record) =>
        record.isCustom ? (
          <Space size={4}>
            <Tooltip title="Chỉnh sửa">
              <Button
                type="text"
                icon={<EditOutlined />}
                onClick={() => openEditModal(record.value)}
                aria-label={`Chỉnh sửa ${record.value}`}
              />
            </Tooltip>
            <Popconfirm
              title={`Xóa ${itemLabel}?`}
              description="Giá trị sẽ bị xóa khỏi danh sách lựa chọn. Thông tin trong các hồ sơ đã sử dụng vẫn được giữ nguyên."
              okText="Xóa"
              cancelText="Hủy"
              okButtonProps={{ danger: true }}
              onConfirm={() => handleDelete(record.value)}
            >
              <Tooltip title="Xóa">
                <Button
                  type="text"
                  danger
                  icon={<DeleteOutlined />}
                  aria-label={`Xóa ${record.value}`}
                />
              </Tooltip>
            </Popconfirm>
          </Space>
        ) : (
          <Tooltip title="Giá trị mặc định được lấy từ file Excel cấu hình">
            <Text type="secondary">
              <LockOutlined /> Được bảo vệ
            </Text>
          </Tooltip>
        ),
    },
  ];

  return (
    <div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          gap: 16,
          marginBottom: 20,
          flexWrap: 'wrap',
        }}
      >
        <div>
          <Typography.Title level={4} style={{ margin: 0 }}>
            {title}
          </Typography.Title>
          <Text type="secondary">{description}</Text>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={openAddModal}>
          Thêm {itemLabel}
        </Button>
      </div>

      <Alert
        type="info"
        showIcon
        message={`${values.length} giá trị đã được đồng bộ và hợp nhất`}
        description="Nguồn chuẩn được lưu tại cases.db và dùng chung cho form nhập hồ sơ, bot Telegram, bộ lọc và trang Danh bạ."
        style={{ marginBottom: 16 }}
      />

      <Input
        allowClear
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        prefix={<SearchOutlined style={{ color: '#94a3b8' }} />}
        placeholder={`Tìm kiếm ${itemLabel}...`}
        style={{ marginBottom: 16, maxWidth: 480 }}
      />

      <Table
        columns={columns}
        dataSource={rows}
        loading={loading}
        pagination={{ pageSize: 10, showSizeChanger: false }}
        scroll={{ x: 640 }}
      />

      <Modal
        title={editingValue ? `Chỉnh sửa ${itemLabel}` : `Thêm ${itemLabel}`}
        open={modalOpen}
        onOk={handleSave}
        onCancel={() => setModalOpen(false)}
        okText={editingValue ? 'Lưu thay đổi' : 'Thêm vào danh bạ'}
        cancelText="Hủy"
        confirmLoading={saving}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" style={{ marginTop: 20 }}>
          <Form.Item
            name="value"
            label={itemLabel.charAt(0).toUpperCase() + itemLabel.slice(1)}
            rules={[
              {
                required: true,
                whitespace: true,
                message: 'Vui lòng nhập thông tin',
              },
              {
                validator: (_, value) => {
                  const normalizedValue = String(value || '').trim();
                  const duplicate = values.some(
                    (item) =>
                      item !== editingValue &&
                      item.toLocaleLowerCase('vi') ===
                        normalizedValue.toLocaleLowerCase('vi'),
                  );
                  return duplicate
                    ? Promise.reject(new Error('Giá trị này đã có trong danh bạ'))
                    : Promise.resolve();
                },
              },
            ]}
          >
            <Input autoFocus placeholder={`Nhập ${itemLabel}`} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
