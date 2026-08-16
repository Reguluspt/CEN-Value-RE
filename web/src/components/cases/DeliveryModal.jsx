import { useState } from 'react';
import { Modal, Form, Input, Select, Space, Button, message, Divider, Typography } from 'antd';
import { CompassOutlined, PlusOutlined } from '@ant-design/icons';
import {
  createDeliveryContact,
  getDeliveryContacts,
  saveDelivery,
  sendPhathanhReply,
  updateDeliveryContact,
} from '../../api/documents';
import { deliveryMailFailureNotice } from './deliveryMailError';
import SwapAddressButton from '../entry/SwapAddressButton';

const DEFAULT_CONTACT_DETAILS = 'CÔNG TY CỔ PHẦN THẨM ĐỊNH GIÁ THẾ KỶ - VP TẠI GIA LAI\nĐịa chỉ: 90/60/3 Trường Chinh, TP. Pleiku, Gia Lai\nĐiện thoại: 0905226968';


export default function DeliveryModal({ open, onClose, caseId, contractNumber, onSuccess }) {
  const [form] = Form.useForm();
  const [contactForm] = Form.useForm();
  const [contacts, setContacts] = useState([]);
  const [loadingContacts, setLoadingContacts] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [contactModalOpen, setContactModalOpen] = useState(false);
  const [savingContact, setSavingContact] = useState(false);
  const [contactSearch, setContactSearch] = useState('');

  const selectedContactId = Form.useWatch('delivery_contact_id', form);

  const fetchContacts = async () => {
    setLoadingContacts(true);
    try {
      const res = await getDeliveryContacts();
      setContacts(res.data || []);
    } catch (err) {
      console.error(err);
      message.error('Không thể tải danh bạ chuyển phát');
    } finally {
      setLoadingContacts(false);
    }
  };

  const handleModalOpenChange = (isOpen) => {
    if (!isOpen) return;
    form.resetFields();
    form.setFieldsValue({
      delivery_contact_id: undefined,
      recipient_details: '',
    });
    setContactSearch('');
    fetchContacts();
  };

  const handleContactChange = (contactId) => {
    const details = contactId === 0
      ? DEFAULT_CONTACT_DETAILS
      : contacts.find((contact) => contact.id === contactId)?.full_details || '';
    form.setFieldValue('recipient_details', details);
  };

  const handleAddContact = async () => {
    try {
      const values = await contactForm.validateFields();
      setSavingContact(true);
      const res = await createDeliveryContact({
        short_name: values.short_name,
        full_details: values.full_details,
      });
      await fetchContacts();
      if (res.data?.id) {
        form.setFieldsValue({
          delivery_contact_id: res.data.id,
          recipient_details: values.full_details,
        });
      }
      setContactSearch('');
      setContactModalOpen(false);
      contactForm.resetFields();
      message.success('Đã thêm người nhận vào danh bạ chuyển phát');
    } catch (err) {
      if (err?.errorFields) return;
      console.error(err);
      message.error(err.response?.data?.error || 'Không thể thêm danh bạ chuyển phát');
    } finally {
      setSavingContact(false);
    }
  };

  const handleSubmit = async (values) => {
    setSubmitting(true);
    try {
      const certificateNumber = String(contractNumber || '').trim();
      if (!certificateNumber) {
        message.error('Hồ sơ chưa có số hợp đồng để dùng làm số chứng thư');
        return;
      }

      const recipientText = String(values.recipient_details || '').trim();
      const selectedContactIdForSave = values.delivery_contact_id;

      if (selectedContactIdForSave !== 0) {
        const selectedContact = contacts.find(
          (contact) => contact.id === selectedContactIdForSave,
        );
        if (!selectedContact) {
          message.error('Không tìm thấy người nhận đã chọn trong danh bạ chuyển phát');
          return;
        }

        if (recipientText !== String(selectedContact.full_details || '').trim()) {
          try {
            await updateDeliveryContact(selectedContact.id, {
              short_name: selectedContact.short_name,
              full_details: recipientText,
            });
            setContacts((currentContacts) =>
              currentContacts.map((contact) =>
                contact.id === selectedContact.id
                  ? { ...contact, full_details: recipientText }
                  : contact,
              ),
            );
          } catch (updateErr) {
            console.error(updateErr);
            message.error(
              updateErr.response?.data?.error
                || 'Không thể lưu thông tin đã sửa vào danh bạ chuyển phát',
            );
            return;
          }
        }
      }

      let deliverySaveWarning = '';
      try {
        await saveDelivery(caseId, {
          delivery_contact_id: selectedContactIdForSave,
        });
      } catch (saveErr) {
        console.error(saveErr);
        deliverySaveWarning = 'Không lưu được thông tin chuyển phát, nhưng hệ thống vẫn tiếp tục gửi mail phát hành.';
      }

      const replyRes = await sendPhathanhReply(caseId, {
        certificate_number: certificateNumber,
        recipient: recipientText,
      });

      const resultWarnings = [deliverySaveWarning, replyRes.data?.warning].filter(Boolean);
      Modal.success({
        title: 'Gửi mail phát hành chứng thư thành công',
        content: (
          <div>
            <p>
              Đã gửi mail phát hành chứng thư tới{' '}
              <strong>{replyRes.data?.to_email || 'người nhận'}</strong>.
            </p>
            {resultWarnings.map((warning) => (
              <p key={warning} style={{ marginBottom: 0, color: '#b45309' }}>
                {warning}
              </p>
            ))}
          </div>
        ),
        okText: 'Đóng',
        onOk: () => {
          if (onSuccess) onSuccess();
          onClose();
        },
      });
    } catch (err) {
      console.error(err);
      const failureNotice = deliveryMailFailureNotice(err);
      Modal[failureNotice.type]({
        title: failureNotice.title,
        content: failureNotice.content,
        okText: 'Đóng',
      });
    } finally {
      setSubmitting(false);
    }
  };

  const isDefaultContact = selectedContactId === 0;

  return (
    <>
      <Modal
        open={open}
        title={(
          <Space>
            <CompassOutlined style={{ color: '#007f7a' }} />
            <span>Phát hành chứng thư & Thông tin chuyển phát</span>
          </Space>
        )}
        okText="Xác nhận phát hành"
        cancelText="Hủy"
        confirmLoading={submitting}
        onCancel={onClose}
        onOk={() => form.submit()}
        afterOpenChange={handleModalOpenChange}
        width={600}
        destroyOnClose
        style={{ borderRadius: 10 }}
      >
        <Form form={form} layout="vertical" onFinish={handleSubmit} style={{ marginTop: 16 }}>
          <Form.Item label="Số chứng thư phát hành">
            <Input value={contractNumber || ''} disabled />
          </Form.Item>

          <Form.Item
            name="delivery_contact_id"
            label="Chọn người nhận chuyển phát"
            rules={[{ required: true, message: 'Vui lòng chọn người nhận chuyển phát' }]}
          >
            <Select
              placeholder="Chọn từ danh bạ..."
              loading={loadingContacts}
              showSearch
              searchValue={contactSearch}
              onSearch={setContactSearch}
              onChange={handleContactChange}
              onDropdownOpenChange={(visible) => {
                if (visible) setContactSearch('');
              }}
              optionFilterProp="label"
              filterOption={(input, option) =>
                String(option?.label || '').toLowerCase().includes(input.toLowerCase())
              }
              style={{ width: '100%' }}
              dropdownRender={(menu) => (
                <>
                  {menu}
                  <Divider style={{ margin: '8px 0' }} />
                  <Button
                    type="text"
                    icon={<PlusOutlined />}
                    block
                    onClick={() => setContactModalOpen(true)}
                  >
                    Thêm danh bạ chuyển phát
                  </Button>
                </>
              )}
              options={[
                { value: 0, label: 'VP Gia Lai (mặc định) - 90/60/3 Trường Chinh' },
                ...contacts.map((contact) => ({
                  value: contact.id,
                  label: `${contact.short_name} (${contact.full_details.split('\n')[0] || ''})`,
                })),
              ]}
            />
          </Form.Item>

          <Form.Item
            name="recipient_details"
            label={(
              <Space size={4}>
                <span>Thông tin chuyển phát</span>
                <Form.Item noStyle shouldUpdate={(prev, curr) => prev.recipient_details !== curr.recipient_details}>
                  {({ getFieldValue, setFieldValue }) => (
                    <SwapAddressButton
                      value={getFieldValue('recipient_details')}
                      mode="owner"
                      onSwap={(val) => setFieldValue('recipient_details', val)}
                    />
                  )}
                </Form.Item>
              </Space>
            )}
            rules={[{ required: true, message: 'Vui lòng nhập thông tin chuyển phát' }]}
            help={
              isDefaultContact
                ? 'Thông tin liên hệ mặc định được hệ thống bảo vệ.'
                : 'Nội dung chỉnh sửa sẽ được lưu vào liên hệ đã chọn khi xác nhận phát hành.'
            }
          >
            <Input.TextArea
              rows={4}
              disabled={selectedContactId === undefined}
              readOnly={isDefaultContact}
              placeholder="Chọn người nhận chuyển phát để xem và chỉnh sửa thông tin"
            />
          </Form.Item>

          <Typography.Text type="secondary">
            Số chứng thư sẽ lấy theo số hợp đồng của hồ sơ.
          </Typography.Text>
        </Form>
      </Modal>

      <Modal
        open={contactModalOpen}
        title="Thêm danh bạ chuyển phát"
        okText="Lưu danh bạ"
        cancelText="Hủy"
        confirmLoading={savingContact}
        onOk={handleAddContact}
        onCancel={() => {
          setContactModalOpen(false);
          contactForm.resetFields();
        }}
        destroyOnClose
      >
        <Form form={contactForm} layout="vertical">
          <Form.Item
            name="short_name"
            label="Tên gợi nhớ"
            rules={[{ required: true, message: 'Vui lòng nhập tên gợi nhớ' }]}
          >
            <Input placeholder="Ví dụ: BIDV Nam Gia Lai" />
          </Form.Item>

          <Form.Item
            name="full_details"
            label={(
              <Space size={4}>
                <span>Thông tin chuyển phát</span>
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
            rules={[{ required: true, message: 'Vui lòng nhập thông tin chuyển phát' }]}
          >
            <Input.TextArea
              rows={5}
              placeholder="Họ tên người nhận hoặc đơn vị&#10;Địa chỉ: ...&#10;Điện thoại: ..."
            />
          </Form.Item>

        </Form>
      </Modal>
    </>
  );
}
