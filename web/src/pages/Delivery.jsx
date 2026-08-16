import React, { useState, useEffect, useRef, useCallback, useContext } from 'react';
import {
  Card,
  Typography,
  Table,
  Button,
  Input,
  Form,
  Popconfirm,
  Row,
  Col,
  Statistic,
  message,
  Divider,
  Modal,
  Space
} from 'antd';
import {
  SearchOutlined,
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  ContactsOutlined
} from '@ant-design/icons';
import {
  getDeliveryContacts,
  createDeliveryContact,
  updateDeliveryContact,
  deleteDeliveryContact
} from '../api/delivery';
import SwapAddressButton from '../components/entry/SwapAddressButton';

const { Title, Paragraph } = Typography;

const EditableContext = React.createContext(null);

const EditableRow = (rowPropsWithIndex) => {
  const { index, ...props } = rowPropsWithIndex;
  void index;
  const [form] = Form.useForm();
  return (
    <Form form={form} component={false}>
      <EditableContext.Provider value={form}>
        <tr {...props} />
      </EditableContext.Provider>
    </Form>
  );
};

const EditableCell = ({
  title,
  editable,
  children,
  dataIndex,
  record,
  handleSave,
  ...restProps
}) => {
  const [editing, setEditing] = useState(false);
  const inputRef = useRef(null);
  const form = useContext(EditableContext);

  useEffect(() => {
    if (editing) {
      inputRef.current.focus();
    }
  }, [editing]);

  const toggleEdit = () => {
    setEditing(!editing);
    form.setFieldsValue({
      [dataIndex]: record[dataIndex],
    });
  };

  const save = async () => {
    try {
      const values = await form.validateFields();
      toggleEdit();
      handleSave({ ...record, ...values });
    } catch (errInfo) {
      console.log('Save failed:', errInfo);
    }
  };

  let childNode = children;

  if (editable) {
    childNode = editing ? (
      <Form.Item
        name={dataIndex}
        style={{ margin: 0 }}
        rules={[
          {
            required: true,
            message: `${title} là bắt buộc.`,
          },
        ]}
      >
        {dataIndex === 'full_details' ? (
          <Input.TextArea
            ref={inputRef}
            onBlur={save}
            autoSize={{ minRows: 2, maxRows: 6 }}
            style={{ width: '100%' }}
          />
        ) : (
          <Input
            ref={inputRef}
            onPressEnter={save}
            onBlur={save}
          />
        )}
      </Form.Item>
    ) : (
      <div
        className="editable-cell-value-wrap"
        style={{
          padding: '4px 12px',
          minHeight: '32px',
          border: '1px solid transparent',
          borderRadius: '4px',
          cursor: 'pointer',
          transition: 'all 0.2s'
        }}
        onClick={toggleEdit}
        onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#d9d9d9'; }}
        onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'transparent'; }}
      >
        <span style={{ whiteSpace: 'pre-wrap' }}>{children}</span>
      </div>
    );
  }

  return <td {...restProps}>{childNode}</td>;
};

export default function Delivery({ embedded = false }) {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');

  // Modal Popup state for Add/Edit
  const [modalOpen, setModalOpen] = useState(false);
  const [editingContact, setEditingContact] = useState(null);
  const [submittingModal, setSubmittingModal] = useState(false);
  const [modalForm] = Form.useForm();

  // Fetch delivery contacts
  const fetchContacts = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getDeliveryContacts({ search: search.trim() });
      setContacts(res.data || []);
    } catch (err) {
      console.error(err);
      message.error('Không thể tải danh sách liên hệ chuyển phát');
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    const timer = window.setTimeout(fetchContacts, 200);
    return () => {
      window.clearTimeout(timer);
    };
  }, [fetchContacts]);

  // Inline cell save
  const handleCellSave = async (row) => {
    const hide = message.loading('Đang cập nhật...', 0);
    try {
      await updateDeliveryContact(row.id, {
        short_name: row.short_name,
        full_details: row.full_details
      });
      message.success('Đã cập nhật liên hệ chuyển phát');
      fetchContacts();
    } catch (err) {
      message.error('Lỗi cập nhật: ' + (err.response?.data?.error || err.message));
    } finally {
      hide();
    }
  };

  // Open Modal for Add
  const handleAddClick = () => {
    setEditingContact(null);
    modalForm.resetFields();
    setModalOpen(true);
  };

  // Open Modal for Edit
  const handleEditClick = (record) => {
    setEditingContact(record);
    modalForm.setFieldsValue({
      short_name: record.short_name,
      full_details: record.full_details,
    });
    setModalOpen(true);
  };

  // Handle Save in Modal Popup
  const handleModalSave = async () => {
    try {
      const values = await modalForm.validateFields();
      setSubmittingModal(true);
      if (editingContact) {
        await updateDeliveryContact(editingContact.id, values);
        message.success('Cập nhật liên hệ chuyển phát thành công');
      } else {
        await createDeliveryContact(values);
        message.success('Thêm mới liên hệ chuyển phát thành công');
      }
      setModalOpen(false);
      modalForm.resetFields();
      fetchContacts();
    } catch (err) {
      if (err.name !== 'ValidationError') {
        message.error('Lỗi lưu liên hệ chuyển phát: ' + (err.response?.data?.error || err.message));
      }
    } finally {
      setSubmittingModal(false);
    }
  };

  // Delete contact
  const handleDelete = async (id) => {
    try {
      await deleteDeliveryContact(id);
      message.success('Đã xóa liên hệ thành công');
      fetchContacts();
    } catch (err) {
      message.error('Lỗi xóa liên hệ: ' + (err.response?.data?.error || err.message));
    }
  };

  const defaultColumns = [
    {
      title: 'Tên viết tắt / Tên gợi nhớ',
      dataIndex: 'short_name',
      width: '25%',
      editable: true,
      sorter: (a, b) => a.short_name.localeCompare(b.short_name),
      render: (text) => <strong>{text}</strong>
    },
    {
      title: 'Thông tin chi tiết người nhận (Tên, Địa chỉ, Số điện thoại)',
      dataIndex: 'full_details',
      width: '55%',
      editable: true,
    },
    {
      title: 'Thao tác',
      key: 'actions',
      width: '20%',
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined style={{ color: '#007f7a' }} />}
            onClick={() => handleEditClick(record)}
          >
            Sửa
          </Button>
          <Popconfirm
            title="Xóa liên hệ"
            description="Bạn chắc chắn muốn xóa liên hệ này khỏi danh bạ?"
            onConfirm={() => handleDelete(record.id)}
            okText="Xóa"
            cancelText="Hủy"
            okButtonProps={{ danger: true }}
          >
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
            >
              Xóa
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const columns = defaultColumns.map((col) => {
    if (!col.editable) {
      return col;
    }
    return {
      ...col,
      onCell: (record) => ({
        record,
        editable: col.editable,
        dataIndex: col.dataIndex,
        title: col.title,
        handleSave: handleCellSave,
      }),
    };
  });

  const components = {
    body: {
      row: EditableRow,
      cell: EditableCell,
    },
  };

  const totalContacts = contacts.length;
  const completeContacts = contacts.filter(
    (c) => c.short_name && c.full_details && c.full_details.split('\n').length >= 2
  ).length;
  const incompleteContacts = Math.max(totalContacts - completeContacts, 0);

  return (
    <div>
      {/* Title Header */}
      <div style={{ marginBottom: 24, display: embedded ? 'none' : undefined }}>
        <Title level={3} style={{ margin: 0, fontWeight: 700 }}>
          📦 Danh bạ chuyển phát
        </Title>
        <Paragraph style={{ color: '#64748b', margin: '4px 0 0 0' }}>
          Quản lý người nhận hồ sơ phát hành chứng thư, địa chỉ, điện thoại và nội dung dùng khi gửi mail chuyển phát.
        </Paragraph>
      </div>

      {/* KPI Stats cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card bordered style={{ borderLeft: '5px solid #007f7a' }} hoverable>
            <Statistic title="Tổng liên hệ" value={totalContacts} prefix={<ContactsOutlined />} />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card bordered style={{ borderLeft: '5px solid #047857' }} hoverable>
            <Statistic title="Liên hệ đầy đủ thông tin" value={completeContacts} suffix={`/ ${totalContacts}`} />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card bordered style={{ borderLeft: '5px solid #c2413d' }} hoverable>
            <Statistic title="Cần bổ sung thông tin" value={incompleteContacts} />
          </Card>
        </Col>
      </Row>

      {/* Main Table Card */}
      <Card
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
            <span>Bảng chỉnh sửa danh bạ chuyển phát</span>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAddClick}
            >
              Tạo danh bạ mới
            </Button>
          </div>
        }
      >
        <Input
          placeholder="🔍 Tìm nhanh người nhận, tên gợi nhớ, địa chỉ..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ marginBottom: 16 }}
          allowClear
          prefix={<SearchOutlined style={{ color: '#94a3b8' }} />}
        />
        
        <Table
          components={components}
          rowClassName={() => 'editable-row'}
          bordered
          dataSource={contacts}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
          size="middle"
        />

        <Divider />
        <Paragraph style={{ color: '#64748b', fontSize: '13px' }}>
          💡 <strong>Hướng dẫn quản lý:</strong>
          <ol style={{ marginTop: 4, paddingLeft: 20 }}>
            <li>Bấm nút <strong>Tạo danh bạ mới</strong> hoặc nút <strong>Sửa</strong> để mở bảng popup nhập thông tin.</li>
            <li>Tại bảng Popup, bấm nút <strong>Icon Hoán đổi ⇄</strong> cạnh nhãn Thông tin chi tiết để đổi sang tên đơn vị hành chính mới (Nay là...).</li>
            <li>Hoặc rê chuột và click trực tiếp vào từng ô trong bảng để chỉnh sửa nhanh.</li>
          </ol>
        </Paragraph>
      </Card>

      {/* Add / Edit Contact Modal Popup */}
      <Modal
        open={modalOpen}
        title={editingContact ? `Cập nhật danh bạ chuyển phát #${editingContact.id}` : 'Thêm mới danh bạ chuyển phát'}
        okText="Lưu lại"
        cancelText="Hủy"
        confirmLoading={submittingModal}
        onOk={handleModalSave}
        onCancel={() => setModalOpen(false)}
        destroyOnClose
      >
        <Form form={modalForm} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item
            name="short_name"
            label="Tên viết tắt / Tên gợi nhớ"
            rules={[{ required: true, message: 'Vui lòng nhập tên gợi nhớ' }]}
          >
            <Input placeholder="Ví dụ: BIDV Nam Gia Lai - A Sửu" />
          </Form.Item>

          <Form.Item
            name="full_details"
            label={(
              <Space size={4}>
                <span>Thông tin chi tiết người nhận (Tên, Địa chỉ, Số điện thoại)</span>
                <Form.Item noStyle shouldUpdate={(prev, curr) => prev.full_details !== curr.full_details}>
                  {({ getFieldValue, setFieldValue }) => (
                    <SwapAddressButton
                      value={getFieldValue('full_details')}
                      mode="owner"
                      onSwap={(val) => setFieldValue('full_details', val)}
                    />
                  )}
                </Form.Item>
              </Space>
            )}
            rules={[{ required: true, message: 'Vui lòng nhập thông tin chi tiết người nhận' }]}
          >
            <Input.TextArea
              rows={5}
              placeholder={"Họ tên người nhận hoặc đơn vị\nĐịa chỉ: ...\nĐiện thoại: ..."}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
