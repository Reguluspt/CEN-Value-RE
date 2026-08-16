import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Row,
  Col,
  Card,
  Typography,
  Radio,
  Form,
  Input,
  Select,
  Button,
  Space,
  Modal,
  Tag,
  Divider,
  message,
  Spin,
  Alert
} from 'antd';
import {
  FilePdfOutlined,
  UploadOutlined,
  SendOutlined,
  EyeOutlined,
  PlusOutlined,
  DeleteOutlined,
  HomeOutlined,
  ToolOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import FileUploader from './FileUploader';
import PageViewer from './PageViewer';
import OcrActions from './OcrActions';
import { initialScanStatus } from './ocrQueue';
import { extractFields } from '../../api/entry';
import { getSoboEmailMapping, previewSoboEmail, createAndSendSobo } from '../../api/sobo';

import SwapAddressButton from './SwapAddressButton';

const { Title, Text } = Typography;

const { TextArea } = Input;
const DEFAULT_EMAIL_MAPPING = {
  'Sobo.taynguyen@gmail.com': ['gia lai', 'đắk lắk', 'đăk lăk', 'dak lak', 'kon tum', 'đắk nông', 'đăk nông', 'dak nong'],
  'Sobo.binhdinh@gmail.com': ['bình định', 'binh dinh', 'khánh hòa', 'khanh hoa', 'phú yên', 'phu yen'],
  'Sobo.danang@gmail.com': ['đà nẵng', 'da nang', 'quảng ngãi', 'quang ngai', 'quảng nam', 'quang nam', 'huế', 'hue', 'thừa thiên huế', 'quảng bình', 'quang binh', 'quảng trị', 'quang tri'],
  'Sobohcm.cenvalue@gmail.com': ['hồ chí minh', 'ho chi minh', 'tp.hcm', 'tphcm', 'tây ninh', 'tay ninh', 'long an', 'lâm đồng', 'lam dong'],
  'Sobo.dongnai@gmail.com': ['đồng nai', 'dong nai', 'bình thuận', 'binh thuan', 'ninh thuận', 'ninh thuan'],
  'Sobo.binhduong@gmail.com': ['bình dương', 'binh duong', 'bình phước', 'binh phuoc', 'bà rịa', 'vũng tàu', 'ba ria', 'vung tau'],
  'Sobo.cantho@gmail.com': ['cần thơ', 'can tho', 'tiền giang', 'tien giang', 'bến tre', 'ben tre', 'vĩnh long', 'vinh long', 'trà vinh', 'tra vinh', 'hậu giang', 'hau giang', 'sóc trăng', 'soc trang', 'đồng tháp', "dong thap", 'an giang', 'kiên giang', 'kien giang', 'bạc liêu', 'bac lieu', 'cà mau', 'ca mau']
};
const DEFAULT_EMAIL_OPTIONS = Object.keys(DEFAULT_EMAIL_MAPPING);

export default function SoboEntry() {
  const navigate = useNavigate();

  const processedFileIdsRef = useRef(new Set());

  // Mode & Asset Type States
  const [assetType, setAssetType] = useState('real_estate'); // 'real_estate' | 'machinery'
  const [assetSubType, setAssetSubType] = useState('single'); // 'single' | 'multi'

  // Upload States
  const [uploadId, setUploadId] = useState(null);
  const [files, setFiles] = useState([]);
  const [activeFileIndex, setActiveFileIndex] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [rotation, setRotation] = useState(0);

  // Email Mapping & Options State
  const [emailMapping, setEmailMapping] = useState(DEFAULT_EMAIL_MAPPING);
  const [emailOptions, setEmailOptions] = useState(DEFAULT_EMAIL_OPTIONS);
  const [suggestedEmail, setSuggestedEmail] = useState('');

  // Form State
  const [form] = Form.useForm();
  const [assetsList, setAssetsList] = useState([
    { id: 1, so_thua: '', so_to: '', dia_chi: '', link: '' }
  ]);
  const [submitting, setSubmitting] = useState(false);

  // HTML Preview State
  const [previewModalOpen, setPreviewModalOpen] = useState(false);
  const [previewData, setPreviewData] = useState({ subject: '', body: '', body_html: '' });
  const [loadingPreview, setLoadingPreview] = useState(false);

  // Load Email Mapping
  useEffect(() => {
    getSoboEmailMapping()
      .then((res) => {
        if (res.data?.mapping && Object.keys(res.data.mapping).length) {
          setEmailMapping(res.data.mapping);
        }
        if (Array.isArray(res.data?.options) && res.data.options.length) {
          setEmailOptions(res.data.options);
        }
      })
      .catch((err) => {
        console.error('Lỗi tải email mapping:', err);
      });
  }, []);


  // Helper to suggest email from address
  const suggestEmailFromAddress = useCallback(
    (addressStr) => {
      if (!addressStr || !emailMapping) return '';
      const addrLower = addressStr.toLowerCase();
      for (const [email, provinces] of Object.entries(emailMapping)) {
        for (const prov of provinces) {
          if (addrLower.includes(prov.toLowerCase())) {
            return email;
          }
        }
      }
      return '';
    },
    [emailMapping]
  );

  // Auto scan files using Gemini 2.5 Flash
  const autoScanFiles = async (targetUploadId, filesToScan) => {
    if (assetType !== 'real_estate') return;
    const pendingToScan = (filesToScan || []).filter((f) => f.scanStatus === 'pending');
    if (!pendingToScan.length) return;

    message.loading({
      content: `AI Gemini 2.5 Flash đang quét tự động ${pendingToScan.length} file GCN...`,
      key: 'soboAutoScanKey',
      duration: 0
    });

    let scannedCount = 0;
    for (const file of pendingToScan) {
      handleFileScanState(file.file_id, { scanStatus: 'processing', scanError: '' });
      try {
        const pageNumbers = Array.from({ length: file.pages || 0 }, (_, i) => i + 1);
        const res = await extractFields({
          upload_id: targetUploadId,
          file_id: file.file_id,
          pages: pageNumbers,
          provider: 'Gemini',
          model: 'gemini-2.5-flash',
          extract_all: false,
        });

        const extraction = res.data?.extraction || {};
        const multiExtraction = res.data?.multi_extraction || {};
        const assetCount = Array.isArray(multiExtraction.assets) ? multiExtraction.assets.length : 0;

        handleFileScanState(file.file_id, {
          scanStatus: 'applied',
          extraction,
          multiExtraction,
          assetCount,
          scanError: '',
        });

        handleFileScanned(file.file_id, extraction, multiExtraction, file.name);
        scannedCount += 1;

      } catch (err) {
        console.error(err);
        handleFileScanState(file.file_id, {
          scanStatus: 'error',
          scanError: err.response?.data?.error || 'Không thể trích xuất file này.',
        });
      }
    }

    if (scannedCount > 0) {
      message.success({
        content: `Đã hoàn tất quét AI Gemini 2.5 Flash cho ${scannedCount} file GCN và đưa vào Form!`,
        key: 'soboAutoScanKey'
      });
    } else {
      message.destroy('soboAutoScanKey');
    }
  };

  // File Upload Handlers
  const handleUploadSuccess = (newUploadId, uploadedFiles, isAppend = false) => {
    const nextFiles = (uploadedFiles || []).map((file) => ({
      ...file,
      scanStatus: initialScanStatus(file, uploadedFiles),
      extraction: null,
      multiExtraction: null,
      scanError: ''
    }));

    if (isAppend && uploadId) {
      setFiles((prevFiles) => {
        const existingIds = new Set(prevFiles.map((f) => f.file_id));
        const filteredNew = nextFiles.filter((f) => !existingIds.has(f.file_id));
        const updatedList = [...prevFiles, ...filteredNew];
        setTimeout(() => autoScanFiles(uploadId, filteredNew), 100);
        return updatedList;
      });
    } else {
      setUploadId(newUploadId);
      setFiles(nextFiles);
      setActiveFileIndex(0);
      setCurrentPage(1);
      setRotation(0);
      setTimeout(() => autoScanFiles(newUploadId, nextFiles), 100);
    }
  };

  const deduplicateAssets = (list) => {

    const unique = [];
    const seenKeys = new Set();
    for (const item of list) {
      const thuaStr = String(item.so_thua || '').trim();
      const toStr = String(item.so_to || '').trim();
      const addrStr = String(item.dia_chi || '').trim();
      if (!thuaStr && !addrStr) continue;
      const key = `${thuaStr}|${toStr}|${addrStr}`;
      if (!seenKeys.has(key)) {
        seenKeys.add(key);
        unique.push(item);
      }
    }
    return unique;
  };

  const handleResetFiles = () => {
    setUploadId(null);
    setFiles([]);
    setActiveFileIndex(0);
    setCurrentPage(1);
    setRotation(0);
    processedFileIdsRef.current.clear();
  };

  const handleFileScanState = (fileId, changes) => {
    setFiles((currentFiles) =>
      currentFiles.map((file) => (file.file_id === fileId ? { ...file, ...changes } : file))
    );
  };

  // OCR Scanned Handler - Auto Fill Form
  const handleFileScanned = (fileId, extraction, multiExtraction) => {
    if (!extraction) return;
    if (fileId && processedFileIdsRef.current.has(fileId)) return;
    if (fileId) processedFileIdsRef.current.add(fileId);

    if (assetType === 'real_estate') {
      const getVal = (field) => {
        const val = extraction[field];
        return typeof val === 'object' ? val?.value || '' : val || '';
      };

      const thua = getVal('so_thua_dat') || getVal('so_thua');
      const to = getVal('so_to_ban_do') || getVal('so_to');
      const diaChi = getVal('dia_chi_thua_dat') || getVal('land_address');

      const extractedAssets = Array.isArray(multiExtraction?.assets) && multiExtraction.assets.length
        ? multiExtraction.assets
        : [extraction];

      const newAssetItems = extractedAssets.map((a, idx) => {
        const aThua = (typeof a.so_thua_dat === 'object' ? a.so_thua_dat?.value : a.so_thua_dat) || getVal('so_thua') || '';
        const aTo = (typeof a.so_to_ban_do === 'object' ? a.so_to_ban_do?.value : a.so_to_ban_do) || getVal('so_to') || '';
        const aAddr = (typeof a.dia_chi_thua_dat === 'object' ? a.dia_chi_thua_dat?.value : a.dia_chi_thua_dat) || getVal('dia_chi_thua_dat') || '';
        return {
          id: Date.now() + idx,
          file_id: fileId,
          so_thua: aThua,
          so_to: aTo,
          dia_chi: aAddr,
          link: ''
        };
      }).filter(item => item.so_thua || item.dia_chi);

      setAssetsList((prev) => {
        const existing = prev.filter(item => item.so_thua || item.dia_chi);
        const combined = existing.length ? [...existing, ...newAssetItems] : newAssetItems;
        return deduplicateAssets(combined);
      });

      const primaryAddr = newAssetItems[0]?.dia_chi || diaChi;
      if (primaryAddr && !form.getFieldValue('email_recipient')) {
        const matchedEmail = suggestEmailFromAddress(primaryAddr);
        if (matchedEmail) {
          form.setFieldValue('email_recipient', matchedEmail);
          setSuggestedEmail(matchedEmail);
        }
      }
    }
  };




  // Address blur handler for single asset
  const handleAddressBlur = (e) => {
    const val = e.target.value;
    const currentEmail = form.getFieldValue('email_recipient');
    if (!currentEmail && val) {
      const suggested = suggestEmailFromAddress(val);
      if (suggested) {
        form.setFieldValue('email_recipient', suggested);
        setSuggestedEmail(suggested);
        message.info(`Đã gợi ý email phòng ban: ${suggested}`);
      }
    }
  };

  // Multi asset helpers
  const handleAddAssetRow = () => {
    setAssetsList((prev) => [
      ...prev,
      { id: Date.now(), so_thua: '', so_to: '', dia_chi: '', link: '' }
    ]);
  };

  const handleRemoveAssetRow = (id) => {
    if (assetsList.length <= 1) {
      message.warning('Danh sách phải có ít nhất 1 tài sản');
      return;
    }
    setAssetsList((prev) => prev.filter((item) => item.id !== id));
  };

  const handleAssetCellChange = (id, field, value) => {
    setAssetsList((prev) =>
      prev.map((item) => {
        if (item.id === id) {
          const updated = { ...item, [field]: value };
          if (field === 'dia_chi' && item.id === prev[0]?.id) {
            const suggested = suggestEmailFromAddress(value);
            if (suggested && !form.getFieldValue('email_recipient')) {
              form.setFieldValue('email_recipient', suggested);
              setSuggestedEmail(suggested);
            }
          }
          return updated;
        }
        return item;
      })
    );
  };

  // Build current payload for preview or submit
  const buildPayload = () => {
    const values = form.getFieldsValue();
    const effectiveSubType = assetsList.length > 1 ? 'multi' : 'single';
    const gcnDetails = files.flatMap((file) => {
      const extractedAssets = Array.isArray(file.multiExtraction?.assets) && file.multiExtraction.assets.length
        ? file.multiExtraction.assets
        : file.extraction
          ? [file.extraction]
          : [];
      return extractedAssets.map((asset, index) => ({
        ...asset,
        source_file_id: file.file_id,
        source_file_name: file.name || '',
        asset_index: index,
      }));
    });
    const payload = {
      asset_type: assetType,
      asset_sub_type: effectiveSubType,
      upload_id: uploadId,
      source: values.source || '',
      email_recipient: values.email_recipient || '',
      note: values.note || '',
      equipment_name: values.equipment_name || '',
      gcn_details: gcnDetails,
    };

    if (assetType === 'real_estate') {
      payload.assets_list = assetsList;
      payload.so_thua = assetsList.map((a) => a.so_thua).filter(Boolean).join(', ');
      payload.so_to = assetsList.map((a) => a.so_to).filter(Boolean).join(', ');
      payload.dia_chi = assetsList[0]?.dia_chi || '';
    }

    return payload;
  };


  // Fetch HTML Email Preview
  const handleOpenPreview = async () => {
    try {
      await form.validateFields();
    } catch (err) {
      message.error('Vui lòng điền đủ các thông tin bắt buộc trước khi xem bản trước!');
      return;
    }

    setLoadingPreview(true);
    setPreviewModalOpen(true);
    try {
      const payload = buildPayload();
      const res = await previewSoboEmail(payload);
      setPreviewData(res.data);
    } catch (err) {
      console.error(err);
      message.error('Lỗi khi tải bản xem trước email');
    } finally {
      setLoadingPreview(false);
    }
  };

  // Submit Handler -> Create & Send -> Redirect to /sobo
  const handleSubmit = async () => {
    try {
      await form.validateFields();
    } catch (err) {
      message.error('Vui lòng nhập đầy đủ các thông tin bắt buộc');
      return;
    }

    const payload = buildPayload();
    if (!payload.email_recipient) {
      message.error('Vui lòng chọn Email phòng ban nhận sơ bộ');
      return;
    }

    setSubmitting(true);
    const hideMessage = message.loading('Đang khởi tạo yêu cầu và gửi email sơ bộ...', 0);
    try {
      const res = await createAndSendSobo(payload);
      hideMessage();
      if (res.data.success) {
        message.success(`Đã gửi sơ bộ thành công! Mã hồ sơ #${res.data.id}. Đang chuyển hướng...`);
        // Auto redirect to /sobo as requested
        setTimeout(() => {
          navigate('/sobo');
        }, 1200);
      } else {
        message.error(res.data.user_message || 'Gửi yêu cầu sơ bộ thất bại');
      }
    } catch (err) {
      hideMessage();
      console.error(err);
      message.error(err.response?.data?.error || 'Lỗi khi gửi sơ bộ');
    } finally {
      setSubmitting(false);
    }
  };

  const activeFile = files[activeFileIndex];

  return (
    <div className="sobo-entry-container" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Selection Control Card */}
      <Card style={{ borderRadius: 12, border: '1px solid #d8e7e5' }} bodyStyle={{ padding: '16px 24px' }}>
        <Row gutter={[16, 16]} align="middle" justify="space-between">
          <Col xs={24} md={14}>
            <Space direction="vertical" size={4}>
              <Text strong style={{ fontSize: '15px', color: '#0f172a' }}>
                📌 Chọn loại tài sản cần gửi Sơ bộ:
              </Text>
              <Radio.Group
                value={assetType}
                onChange={(e) => {
                  setAssetType(e.target.value);
                  form.resetFields();
                }}
                buttonStyle="solid"
                size="middle"
              >
                <Radio.Button value="real_estate">
                  <HomeOutlined style={{ marginRight: 6 }} />
                  Bất động sản (GCN)
                </Radio.Button>
                <Radio.Button value="machinery">
                  <ToolOutlined style={{ marginRight: 6 }} />
                  Máy móc thiết bị
                </Radio.Button>
              </Radio.Group>
            </Space>
          </Col>

        </Row>
      </Card>


      {/* Main Workspace Row */}
      <Row gutter={[16, 16]}>
        {/* Left Column: File Uploader & Viewer */}
        <Col xs={24} lg={12}>
          {!uploadId ? (
            <Card
              style={{
                borderRadius: 12,
                border: '1px solid #d8e7e5',
                minHeight: '450px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center'
              }}
              styles={{ body: { padding: '24px' } }}
            >
              <div style={{ textAlign: 'center', marginBottom: 24 }}>
                <FilePdfOutlined style={{ fontSize: 48, color: '#007f7a' }} />
                <Title level={4} style={{ marginTop: 12, marginBottom: 8 }}>
                  Tải lên tài liệu đính kèm
                </Title>
                <Text type="secondary" style={{ fontSize: '13px' }}>
                  {assetType === 'real_estate'
                    ? 'AI sẽ tự động nhận diện và đưa Số thửa, Số tờ, Địa chỉ vào Form'
                    : 'Tài liệu hồ sơ hoặc hình ảnh thiết bị sẽ được đính kèm vào Email'}
                </Text>
              </div>
              <FileUploader 
                onUploadSuccess={handleUploadSuccess} 
                placeholderText={assetType === 'real_estate' ? 'Kéo thả hoặc Click để tải lên GCN' : 'Kéo thả hoặc Click để tải lên pháp lý tài sản'}
                hintText={assetType === 'real_estate' ? 'Tự động tải lên & quét AI bằng Gemini 2.5 Flash ngay sau khi chọn file' : 'Tài liệu pháp lý hoặc hình ảnh thiết bị sẽ được đính kèm vào Email'}
              />
            </Card>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <FileUploader
                uploadId={uploadId}
                compact={false}
                placeholderText={assetType === 'real_estate' ? 'Kéo thả hoặc Click để tải lên GCN thứ 2, thứ 3...' : 'Kéo thả hoặc Click để tải lên bổ sung pháp lý tài sản'}
                hintText={assetType === 'real_estate' ? 'Tự động tải lên & quét AI bằng Gemini 2.5 Flash ngay sau khi chọn file' : 'Tài liệu pháp lý hoặc hình ảnh thiết bị sẽ được đính kèm vào Email'}
                onUploadSuccess={handleUploadSuccess}
              />

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Space wrap>
                  {files.length > 1 && (
                    <Select
                      value={activeFileIndex}
                      onChange={(idx) => {
                        setActiveFileIndex(idx);
                        setCurrentPage(1);
                      }}
                      style={{ minWidth: 200 }}
                      options={files.map((f, i) => ({
                        value: i,
                        label: `${i + 1}. ${f.name}`
                      }))}
                    />
                  )}
                  {assetType === 'real_estate' && (
                    <OcrActions
                      uploadId={uploadId}
                      activeFile={activeFile}
                      files={files}
                      onFileScanState={handleFileScanState}
                      onFileScanned={handleFileScanned}
                    />
                  )}
                </Space>
                <Button icon={<UploadOutlined />} onClick={handleResetFiles} size="small">
                  Đổi file khác
                </Button>
              </div>

              <PageViewer
                uploadId={uploadId}
                activeFile={activeFile}
                currentPage={currentPage}
                onPageChange={setCurrentPage}
                rotation={rotation}
                onRotationChange={setRotation}
              />
            </div>
          )}


        </Col>

        {/* Right Column: Input Form & Actions */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Text strong style={{ color: '#007f7a', fontSize: '16px' }}>
                  {assetType === 'real_estate' ? '📋 Thông tin tài sản Sơ bộ' : '⚙️ Thông tin Máy móc thiết bị'}
                </Text>
                {suggestedEmail && (
                  <Tag color="cyan" style={{ borderRadius: 12 }}>
                    Auto-suggest: {suggestedEmail}
                  </Tag>
                )}
              </div>
            }
            style={{ borderRadius: 12, border: '1px solid #d8e7e5' }}
            bodyStyle={{ padding: '20px 24px' }}
          >
            <Form form={form} layout="vertical">
              {/* Email Recipient */}
              <Form.Item
                name="email_recipient"
                label="📧 Email phòng ban nhận Sơ bộ"
                rules={[{ required: true, message: 'Vui lòng chọn email phòng ban nhận' }]}
              >
                <Select
                  placeholder="Chọn email phòng ban nghiệp vụ..."
                  allowClear
                  options={emailOptions.map((opt) => ({
                    value: opt,
                    label: `${opt} ${opt === suggestedEmail ? ' (Gợi ý theo địa chỉ)' : ''}`
                  }))}
                />
              </Form.Item>

              {/* Real Estate Assets Form */}
              {assetType === 'real_estate' && (
                <div style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                    <Text strong style={{ color: '#334155' }}>
                      Danh sách tài sản ({assetsList.length})
                    </Text>
                    <Button type="dashed" icon={<PlusOutlined />} onClick={handleAddAssetRow} size="small">
                      Thêm tài sản
                    </Button>
                  </div>


                  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {assetsList.map((item, idx) => (
                      <Card
                        key={item.id}
                        size="small"
                        style={{ background: '#f8fafc', borderRadius: 8 }}
                        title={<Text type="secondary">Tài sản #{idx + 1}</Text>}
                        extra={
                          assetsList.length > 1 && (
                            <Button
                              type="text"
                              danger
                              icon={<DeleteOutlined />}
                              onClick={() => handleRemoveAssetRow(item.id)}
                              size="small"
                            />
                          )
                        }
                      >
                        <Row gutter={8}>
                          <Col span={12}>
                            <Input
                              placeholder="Số thửa"
                              value={item.so_thua}
                              onChange={(e) => handleAssetCellChange(item.id, 'so_thua', e.target.value)}
                              size="small"
                            />
                          </Col>
                          <Col span={12}>
                            <Input
                              placeholder="Số tờ"
                              value={item.so_to}
                              onChange={(e) => handleAssetCellChange(item.id, 'so_to', e.target.value)}
                              size="small"
                            />
                          </Col>
                        </Row>
                        <Input
                          placeholder="Địa chỉ..."
                          value={item.dia_chi}
                          onChange={(e) => handleAssetCellChange(item.id, 'dia_chi', e.target.value)}
                          size="small"
                          suffix={
                            <SwapAddressButton
                              value={item.dia_chi}
                              onSwap={(val) => handleAssetCellChange(item.id, 'dia_chi', val)}
                            />
                          }
                          style={{ marginTop: 8 }}
                        />

                        <Input
                          placeholder="Link Maps..."
                          value={item.link}
                          onChange={(e) => handleAssetCellChange(item.id, 'link', e.target.value)}
                          size="small"
                          style={{ marginTop: 8 }}
                        />
                      </Card>
                    ))}
                  </div>
                </div>
              )}

              {/* Machinery Form */}
              {assetType === 'machinery' && (
                <Form.Item
                  name="equipment_name"
                  label="⚙️ Tên máy móc thiết bị"
                  rules={[{ required: true, message: 'Vui lòng nhập tên thiết bị' }]}
                >
                  <Input placeholder="Ví dụ: Máy xúc Komatsu PC200, Dây chuyền sản xuất..." />
                </Form.Item>
              )}

              {/* Common Fields */}
              <Form.Item
                name="source"
                label="👤 Nguồn khách hàng / Đơn vị yêu cầu"
                rules={[{ required: true, message: 'Vui lòng nhập nguồn khách hàng' }]}
              >
                <Input placeholder="Ví dụ: VCB Tây Nguyên, KH Cá nhân A..." />
              </Form.Item>

              <Form.Item name="note" label="📝 Ghi chú bổ sung">
                <TextArea rows={3} placeholder="Nhập ghi chú gửi kèm email sơ bộ (nếu có)..." />
              </Form.Item>

              <Divider style={{ margin: '16px 0' }} />

              {/* Action Buttons */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12 }}>
                <Button icon={<EyeOutlined />} onClick={handleOpenPreview}>
                  Xem trước Email
                </Button>
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handleSubmit}
                  loading={submitting}
                  style={{ background: '#007f7a', borderColor: '#007f7a' }}
                >
                  Gửi yêu cầu Sơ bộ ngay
                </Button>
              </div>
            </Form>
          </Card>
        </Col>
      </Row>

      {/* HTML Email Preview Modal */}
      <Modal
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <EyeOutlined style={{ color: '#007f7a' }} />
            <span>Bản xem trước HTML Email thực tế sẽ gửi</span>
          </div>
        }
        open={previewModalOpen}
        onCancel={() => setPreviewModalOpen(false)}
        width={760}
        footer={[
          <Button key="close" onClick={() => setPreviewModalOpen(false)}>
            Đóng
          </Button>,
          <Button
            key="submit"
            type="primary"
            icon={<SendOutlined />}
            loading={submitting}
            onClick={() => {
              setPreviewModalOpen(false);
              handleSubmit();
            }}
            style={{ background: '#007f7a', borderColor: '#007f7a' }}
          >
            Xác nhận Gửi Email này
          </Button>
        ]}
      >
        {loadingPreview ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" tip="Đang dựng giao diện HTML Email..." />
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <Alert
              message={`Tiêu đề Email: ${previewData.subject}`}
              type="info"
              showIcon
              style={{ fontWeight: 600 }}
            />

            <div
              style={{
                border: '1px solid #cbd5e1',
                borderRadius: 8,
                maxHeight: '520px',
                overflowY: 'auto',
                background: '#ffffff'
              }}
            >
              <iframe
                title="Email HTML Preview"
                srcDoc={previewData.body_html}
                style={{ width: '100%', height: '480px', border: 'none' }}
              />
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
