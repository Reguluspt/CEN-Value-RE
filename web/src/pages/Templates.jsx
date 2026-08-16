import { useCallback, useEffect, useMemo, useState } from 'react';
import { Alert, Button, Card, Empty, Form, Input, Modal, Select, Space, Table, Tabs, Tag, Tooltip, Typography, Upload, message } from 'antd';
import { DownloadOutlined, EditOutlined, EyeOutlined, FileAddOutlined, FileSearchOutlined, FileWordOutlined, FolderAddOutlined, UploadOutlined } from '@ant-design/icons';
import { listCases } from '../api/cases';
import { createTemplateGroup, downloadTemplate, getTemplateGroups } from '../api/templates';
import TemplateEditor from '../components/templates/TemplateEditor';
import OnlyOfficeTemplateEditor from '../components/templates/OnlyOfficeTemplateEditor';

const { Title, Paragraph, Text } = Typography;

const ORGANIZATION_ROLES = [
  { key: 'hop_dong', label: 'Hợp đồng', required: true },
  { key: 'bien_ban_nghiem_thu', label: 'Biên bản nghiệm thu / Thanh lý', required: true },
  { key: 'de_nghi_thanh_toan', label: 'Đề nghị thanh toán', required: true },
  { key: 'thu_chao_phi', label: 'Thư chào phí', required: true },
  { key: 'hop_dong_tam_ung', label: 'Hợp đồng có tạm ứng', required: false },
];

export default function Templates() {
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [editorOpen, setEditorOpen] = useState(false);
  const [wordTemplate, setWordTemplate] = useState(null);
  const [wordEditorOpen, setWordEditorOpen] = useState(false);
  const [previewTemplate, setPreviewTemplate] = useState(null);
  const [previewPickerOpen, setPreviewPickerOpen] = useState(false);
  const [previewEditorOpen, setPreviewEditorOpen] = useState(false);
  const [previewCaseId, setPreviewCaseId] = useState(null);
  const [previewCaseLabel, setPreviewCaseLabel] = useState('');
  const [previewCaseOptions, setPreviewCaseOptions] = useState([]);
  const [previewCasesLoading, setPreviewCasesLoading] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [creating, setCreating] = useState(false);
  const [roleFiles, setRoleFiles] = useState({});
  const [form] = Form.useForm();

  const fetchGroups = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getTemplateGroups();
      setGroups(response.data || []);
    } catch (error) {
      console.error(error);
      message.error('Không thể tải danh sách bộ mẫu');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    queueMicrotask(fetchGroups);
  }, [fetchGroups]);

  const groupsByType = useMemo(() => ({
    individual: groups.filter((group) => group.customer_type === 'individual'),
    organization: groups.filter((group) => group.customer_type === 'organization'),
  }), [groups]);

  const formatDate = (value) => value ? new Date(value).toLocaleString('vi-VN') : '-';

  const handleDownload = async (record) => {
    try {
      const response = await downloadTemplate(record.name, record.group_id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.download = record.name;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error(error);
      message.error('Không thể tải văn bản mẫu');
    }
  };

  const openDetail = (record) => {
    setSelectedTemplate(record);
    setEditorOpen(true);
  };

  const openWordEditor = (record) => {
    setWordTemplate(record);
    setWordEditorOpen(true);
  };

  const loadPreviewCases = useCallback(async (customerType, search = '') => {
    if (!customerType) return;
    setPreviewCasesLoading(true);
    try {
      const response = await listCases({ page: 1, size: 50, sort: 'id', order: 'desc', search });
      const options = (response.data?.items || [])
        .filter((item) => item.customer_type === customerType)
        .map((item) => ({
          value: item.id,
          label: `#${item.id} · ${item.contract_number || 'Chưa có số HĐ'} · ${item.customer_info || 'Chưa có tên khách hàng'}`,
        }));
      setPreviewCaseOptions(options);
    } catch (error) {
      console.error(error);
      message.error('Không thể tải danh sách hồ sơ xem thử');
    } finally {
      setPreviewCasesLoading(false);
    }
  }, []);

  const openAutofillPreview = (record) => {
    setPreviewTemplate(record);
    setPreviewCaseId(null);
    setPreviewCaseLabel('');
    setPreviewCaseOptions([]);
    setPreviewPickerOpen(true);
    loadPreviewCases(record.customer_type);
  };

  const startAutofillPreview = () => {
    if (!previewCaseId) {
      message.warning('Vui lòng chọn hồ sơ để xem thử');
      return;
    }
    setPreviewPickerOpen(false);
    setPreviewEditorOpen(true);
  };

  const closeCreateModal = () => {
    setCreateOpen(false);
    setRoleFiles({});
    form.resetFields();
  };

  const handleCreateGroup = async () => {
    try {
      const values = await form.validateFields();
      const missing = ORGANIZATION_ROLES.filter((role) => role.required && !roleFiles[role.key]);
      if (missing.length) {
        message.error(`Vui lòng tải lên: ${missing.map((role) => role.label).join(', ')}`);
        return;
      }
      setCreating(true);
      const payload = new FormData();
      payload.append('name', values.name);
      payload.append('description', values.description || '');
      Object.entries(roleFiles).forEach(([role, file]) => payload.append(role, file));
      await createTemplateGroup(payload);
      message.success('Đã tạo bộ mẫu tổ chức mới');
      closeCreateModal();
      fetchGroups();
    } catch (error) {
      if (!error?.errorFields) {
        message.error(error.response?.data?.error || 'Không thể tạo bộ mẫu');
      }
    } finally {
      setCreating(false);
    }
  };

  const columns = [
    {
      title: 'Tên văn bản',
      dataIndex: 'display_name',
      key: 'display_name',
      render: (value, record) => (
        <Space>
          <FileWordOutlined style={{ color: '#007f7a', fontSize: 18 }} />
          <div>
            <div style={{ fontWeight: 650 }}>{value}</div>
            <Text type="secondary" style={{ fontSize: 11 }}>{record.name}</Text>
          </div>
        </Space>
      ),
    },
    {
      title: 'Dung lượng',
      dataIndex: 'size',
      width: 120,
      render: (size) => `${(size / 1024).toFixed(1)} KB`,
    },
    {
      title: 'Cập nhật lần cuối',
      dataIndex: 'last_modified',
      width: 180,
      render: formatDate,
    },
    {
      title: 'Thao tác',
      width: 220,
      align: 'center',
      render: (_, record) => (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }} onClick={(event) => event.stopPropagation()}>
          <Tooltip title="Soạn thảo">
            <Button
              type="text"
              aria-label="Soạn thảo"
              icon={<EditOutlined style={{ color: '#007f7a', fontSize: '18px' }} />}
              onClick={() => openWordEditor(record)}
              style={{ width: '36px', height: '36px', minWidth: '36px', display: 'flex', justifyContent: 'center', alignItems: 'center', borderRadius: '6px', backgroundColor: '#f1f5f9', border: 'none', padding: 0 }}
            />
          </Tooltip>
          <Tooltip title="Xem thử tự điền">
            <Button
              type="text"
              aria-label="Xem thử tự điền"
              icon={<FileSearchOutlined style={{ color: '#0284c7', fontSize: '18px' }} />}
              onClick={() => openAutofillPreview(record)}
              style={{ width: '36px', height: '36px', minWidth: '36px', display: 'flex', justifyContent: 'center', alignItems: 'center', borderRadius: '6px', backgroundColor: '#f1f5f9', border: 'none', padding: 0 }}
            />
          </Tooltip>
          <Tooltip title="Chi tiết">
            <Button
              type="text"
              aria-label="Chi tiết"
              icon={<EyeOutlined style={{ color: '#0891b2', fontSize: '18px' }} />}
              onClick={() => openDetail(record)}
              style={{ width: '36px', height: '36px', minWidth: '36px', display: 'flex', justifyContent: 'center', alignItems: 'center', borderRadius: '6px', backgroundColor: '#f1f5f9', border: 'none', padding: 0 }}
            />
          </Tooltip>
          <Tooltip title="Tải xuống">
            <Button
              type="text"
              aria-label="Tải xuống"
              icon={<DownloadOutlined style={{ color: '#007f7a', fontSize: '18px' }} />}
              onClick={() => handleDownload(record)}
              style={{ width: '36px', height: '36px', minWidth: '36px', display: 'flex', justifyContent: 'center', alignItems: 'center', borderRadius: '6px', backgroundColor: '#f1f5f9', border: 'none', padding: 0 }}
            />
          </Tooltip>
        </div>
      ),
    },
  ];

  const renderGroups = (items) => items.length ? (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {items.map((group) => (
        <Card
          key={group.id}
          title={(
            <Space wrap>
              <FolderAddOutlined style={{ color: '#007f7a' }} />
              <span>{group.name}</span>
              <Tag color={group.system ? 'default' : 'cyan'}>{group.system ? 'Bộ hệ thống' : 'Bộ tùy chỉnh'}</Tag>
              <Tag color={group.status === 'complete' ? 'success' : 'warning'}>
                {group.status === 'complete' ? 'Sẵn sàng xuất' : 'Chưa hoàn chỉnh'}
              </Tag>
            </Space>
          )}
          extra={<Text type="secondary">{group.templates.length} văn bản</Text>}
          styles={{ body: { padding: 0 } }}
        >
          {group.description && <div style={{ padding: '12px 16px 0', color: '#64748b' }}>{group.description}</div>}
          {group.missing_documents?.length > 0 && (
            <Alert
              type="warning"
              showIcon
              message={`Thiếu: ${group.missing_documents.join(', ')}`}
              style={{ margin: 16 }}
            />
          )}
          <Table
            rowKey={(record) => `${record.group_id}:${record.role}`}
            dataSource={group.templates.map((template) => ({
              ...template,
              customer_type: group.customer_type,
              group_name: group.name,
            }))}
            columns={columns}
            pagination={false}
            loading={loading}
            size="middle"
          />
        </Card>
      ))}
    </div>
  ) : <Empty description="Chưa có bộ mẫu" />;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 16, marginBottom: 20 }}>
        <div>
          <Title level={3} style={{ margin: 0 }}>Quản lý bộ mẫu văn bản</Title>
          <Paragraph style={{ color: '#64748b', margin: '4px 0 0' }}>
            Mỗi bộ mẫu gồm các văn bản dùng cùng nhau khi xuất hồ sơ Word.
          </Paragraph>
        </div>
        <Button type="primary" icon={<FileAddOutlined />} onClick={() => setCreateOpen(true)}>
          Tạo bộ mẫu tổ chức
        </Button>
      </div>

      <Tabs
        defaultActiveKey="organization"
        items={[
          { key: 'organization', label: `Tổ chức (${groupsByType.organization.length} bộ)`, children: renderGroups(groupsByType.organization) },
          { key: 'individual', label: `Cá nhân (${groupsByType.individual.length} bộ)`, children: renderGroups(groupsByType.individual) },
        ]}
      />

      <Modal
        open={createOpen}
        title="Tạo bộ mẫu hồ sơ tổ chức"
        okText="Tạo bộ mẫu"
        cancelText="Hủy"
        confirmLoading={creating}
        onOk={handleCreateGroup}
        onCancel={closeCreateModal}
        width={680}
        destroyOnClose
      >
        <Alert
          type="info"
          showIcon
          message="Tải file theo từng loại văn bản"
          description="Tên file gốc có thể tùy ý; hệ thống sẽ tự lưu theo vai trò để bộ mẫu xuất được ngay."
          style={{ marginBottom: 16 }}
        />
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="Tên bộ mẫu" rules={[{ required: true, message: 'Vui lòng nhập tên bộ mẫu' }]}>
            <Input placeholder="Ví dụ: BIDV Gia Lai – Bộ hồ sơ 2026" maxLength={120} />
          </Form.Item>
          <Form.Item name="description" label="Mô tả">
            <Input.TextArea rows={2} placeholder="Phạm vi hoặc đơn vị áp dụng bộ mẫu này" maxLength={300} />
          </Form.Item>
          {ORGANIZATION_ROLES.map((role) => (
            <Form.Item key={role.key} label={`${role.label}${role.required ? ' *' : ' (tùy chọn)'}`}>
              <Upload
                accept=".docx"
                maxCount={1}
                fileList={roleFiles[role.key] ? [roleFiles[role.key]] : []}
                beforeUpload={(file) => {
                  setRoleFiles((current) => ({ ...current, [role.key]: file }));
                  return false;
                }}
                onRemove={() => setRoleFiles((current) => {
                  const next = { ...current };
                  delete next[role.key];
                  return next;
                })}
              >
                <Button icon={<UploadOutlined />}>Chọn file Word</Button>
              </Upload>
            </Form.Item>
          ))}
        </Form>
      </Modal>

      <Modal
        open={previewPickerOpen}
        title={`Xem thử tự điền: ${previewTemplate?.display_name || ''}`}
        okText="Mở bản xem thử"
        cancelText="Hủy"
        onOk={startAutofillPreview}
        onCancel={() => setPreviewPickerOpen(false)}
        destroyOnClose
      >
        <Alert
          type="info"
          showIcon
          message="Chọn một hồ sơ làm dữ liệu mẫu"
          description="Hệ thống tạo một file Word tạm ở chế độ chỉ xem; file mẫu và hồ sơ không bị thay đổi."
          style={{ marginBottom: 16 }}
        />
        <Select
          showSearch
          allowClear
          value={previewCaseId}
          loading={previewCasesLoading}
          placeholder="Tìm theo số hợp đồng hoặc tên khách hàng"
          filterOption={false}
          onSearch={(value) => loadPreviewCases(previewTemplate?.customer_type, value)}
          onChange={(value, option) => {
            setPreviewCaseId(value || null);
            setPreviewCaseLabel(option?.label || '');
          }}
          options={previewCaseOptions}
          style={{ width: '100%' }}
          notFoundContent={previewCasesLoading ? 'Đang tìm hồ sơ...' : 'Không tìm thấy hồ sơ phù hợp'}
        />
      </Modal>

      <TemplateEditor
        open={editorOpen}
        templateName={selectedTemplate?.name}
        groupId={selectedTemplate?.group_id}
        displayName={selectedTemplate?.display_name}
        onClose={() => { setEditorOpen(false); setSelectedTemplate(null); }}
        onSuccess={fetchGroups}
      />

      <OnlyOfficeTemplateEditor
        open={wordEditorOpen}
        templateName={wordTemplate?.name}
        groupId={wordTemplate?.group_id}
        displayName={wordTemplate?.display_name}
        onClose={() => { setWordEditorOpen(false); setWordTemplate(null); fetchGroups(); }}
      />

      <OnlyOfficeTemplateEditor
        open={previewEditorOpen}
        templateName={previewTemplate?.name}
        groupId={previewTemplate?.group_id}
        displayName={previewTemplate?.display_name}
        previewCaseId={previewCaseId}
        previewCaseLabel={previewCaseLabel}
        onClose={() => {
          setPreviewEditorOpen(false);
          setPreviewTemplate(null);
          setPreviewCaseId(null);
          setPreviewCaseLabel('');
        }}
      />
    </div>
  );
}
