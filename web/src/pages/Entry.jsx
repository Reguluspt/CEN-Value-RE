import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Row, Col, Card, Typography, Button, message, Select, Tag, Tabs } from 'antd';
import { FilePdfOutlined, UploadOutlined, FileSearchOutlined, FileTextOutlined } from '@ant-design/icons';
import FileUploader from '../components/entry/FileUploader';
import PageViewer from '../components/entry/PageViewer';
import OcrActions from '../components/entry/OcrActions';
import EntryForm from '../components/entry/EntryForm';
import SoboEntry from '../components/entry/SoboEntry';
import { initialScanStatus } from '../components/entry/ocrQueue';
import { extractFields } from '../api/entry';

const { Title, Text } = Typography;

const extractedValue = (asset, field) => {
  const value = asset?.[field];
  return typeof value === 'object' ? value?.value || '' : value || '';
};

const assetDescriptionFromExtraction = (asset) => {
  const assetDescription = String(asset?.asset_description || '').trim();
  if (assetDescription) return assetDescription;

  const landParcel = extractedValue(asset, 'so_thua_dat') || extractedValue(asset, 'so_thua');
  const mapSheet = extractedValue(asset, 'so_to_ban_do') || extractedValue(asset, 'so_to');
  const address = extractedValue(asset, 'dia_chi_thua_dat') || extractedValue(asset, 'land_address');

  if (!landParcel && !address) return '';

  if (landParcel && mapSheet && address) {
    return `Thửa đất số ${landParcel}, tờ bản đồ số ${mapSheet}; tại địa chỉ ${address}`;
  } else if (landParcel && address) {
    return `Thửa đất số ${landParcel}; tại địa chỉ ${address}`;
  } else if (address) {
    return `Tại địa chỉ ${address}`;
  }
  return '';
};

export default function Entry() {
  const [searchParams, setSearchParams] = useSearchParams();
  const currentTabParam = searchParams.get('tab') === 'sobo' ? 'sobo' : 'appraisal';
  const [activeTab, setActiveTab] = useState(currentTabParam);

  useEffect(() => {
    const tabFromUrl = searchParams.get('tab') === 'sobo' ? 'sobo' : 'appraisal';
    if (tabFromUrl !== activeTab) {
      setActiveTab(tabFromUrl);
    }
  }, [searchParams]);

  const handleTabChange = (key) => {
    setActiveTab(key);
    if (key === 'sobo') {
      setSearchParams({ tab: 'sobo' });
    } else {
      setSearchParams({});
    }
  };

  const [uploadId, setUploadId] = useState(null);
  const [files, setFiles] = useState([]);
  const [activeFileIndex, setActiveFileIndex] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [ocrData, setOcrData] = useState(null);
  const [, setScannedResults] = useState({});

  // Auto scan files using Gemini 2.5 Flash
  const autoScanFiles = async (targetUploadId, filesToScan) => {
    const pendingToScan = (filesToScan || []).filter((f) => f.scanStatus === 'pending');
    if (!pendingToScan.length) return;

    message.loading({
      content: `AI Gemini 2.5 Flash đang quét tự động ${pendingToScan.length} file GCN...`,
      key: 'autoScanKey',
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
        key: 'autoScanKey'
      });
    } else {
      message.destroy('autoScanKey');
    }
  };

  const handleUploadSuccess = (newUploadId, uploadedFiles, isAppend = false) => {
    const nextFiles = (uploadedFiles || []).map((file) => ({
      ...file,
      scanStatus: initialScanStatus(file, uploadedFiles),
      extraction: null,
      multiExtraction: null,
      scanError: '',
    }));

    if (isAppend && uploadId) {
      setFiles((prevFiles) => {
        const existingIds = new Set(prevFiles.map((f) => f.file_id));
        const filteredNew = nextFiles.filter((f) => !existingIds.has(f.file_id));
        const updatedList = [...prevFiles, ...filteredNew];

        const mainNewIndex = updatedList.findIndex(
          (f) => !existingIds.has(f.file_id) && f.scanStatus === 'pending'
        );
        if (mainNewIndex !== -1) {
          setActiveFileIndex(mainNewIndex);
          setCurrentPage(1);
        }

        setTimeout(() => autoScanFiles(uploadId, filteredNew), 100);
        return updatedList;
      });
    } else {
      setUploadId(newUploadId);
      setFiles(nextFiles);
      setActiveFileIndex(0);
      setCurrentPage(1);
      setRotation(0);
      setOcrData(null);
      setScannedResults({});
      setTimeout(() => autoScanFiles(newUploadId, nextFiles), 100);
    }
  };

  const handleReset = () => {
    setUploadId(null);
    setFiles([]);
    setActiveFileIndex(0);
    setCurrentPage(1);
    setRotation(0);
    setOcrData(null);
    setScannedResults({});
  };

  const handlePageChange = (pageNum) => {
    setCurrentPage(pageNum);
  };

  const handleFileChange = (fileIndex) => {
    setActiveFileIndex(fileIndex);
    setCurrentPage(1);
    setRotation(0);
    setOcrData(null);
  };

  const handleFileScanned = (fileId, extraction, multiExtraction, fileNameOverride = '') => {
    setScannedResults((currentResults) => {
      const scannedFile = files.find((file) => file.file_id === fileId);
      const sourceFileName = fileNameOverride || scannedFile?.name || '';
      const nextResults = {
        ...currentResults,
        [fileId]: {
          extraction,
          multiExtraction,
          sourceFileName,
        },
      };
      const extractedFiles = Object.values(nextResults);
      // Use latest scanned extraction for primary form values (or fall back to first)
      const primaryExtraction = extraction || extractedFiles[extractedFiles.length - 1]?.extraction || extractedFiles[0]?.extraction;

      const assetDescriptions = extractedFiles.flatMap(({ extraction: fileExtraction, multiExtraction: fileMultiExtraction }, fileIdx) => {
        const assets = Array.isArray(fileMultiExtraction?.assets) && fileMultiExtraction.assets.length
          ? fileMultiExtraction.assets
          : [fileExtraction];
        return assets.map((asset) => {
          const desc = assetDescriptionFromExtraction(asset);
          if (!desc) return '';
          return desc.startsWith('• ') ? desc : `• ${desc}`;
        }).filter(Boolean);

      });

      const gcnDetails = extractedFiles.flatMap(({ extraction: fileExtraction, multiExtraction: fileMultiExtraction, sourceFileName: sName }, fileIndex) => {
        const assets = Array.isArray(fileMultiExtraction?.assets) && fileMultiExtraction.assets.length
          ? fileMultiExtraction.assets
          : [fileExtraction];
        return assets.map((asset, assetIndex) => ({
          ...asset,
          source_file_id: Object.keys(nextResults)[fileIndex],
          source_file_name: sName,
          asset_index: assetIndex,
        }));
      });

      setOcrData({
        ...primaryExtraction,
        asset_description: assetDescriptions.join('\n'),
        gcn_details: gcnDetails,
      });
      return nextResults;
    });
  };


  const handleFileScanState = (fileId, changes) => {
    setFiles((currentFiles) => currentFiles.map((file) => (
      file.file_id === fileId ? { ...file, ...changes } : file
    )));
  };

  const scanStatusLabel = (status) => ({
    pending: 'Chờ quét',
    processing: 'Đang quét',
    applied: 'Đã đưa vào form',
    error: 'Lỗi quét',
    skipped: 'Đã ghép vào PDF',
  }[status] || 'Chờ quét');

  const scanStatusColor = (status) => ({
    pending: 'default',
    processing: 'processing',
    applied: 'success',
    error: 'error',
    skipped: 'default',
  }[status] || 'default');

  const handleSaveSuccess = (caseId) => {
    message.success(`Hồ sơ đã được lưu trữ với ID: ${caseId}`);
    handleReset();
  };

  const activeFile = files[activeFileIndex];

  return (
    <div className="entry-page" style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <style>{`
        .entry-workspace-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 16px;
        }
        .entry-workspace-title {
          min-width: 0;
        }
        .entry-workspace-actions {
          display: flex;
          align-items: center;
          justify-content: flex-end;
          flex-wrap: wrap;
          gap: 8px;
        }
        .entry-file-select {
          min-width: 240px;
        }
        .entry-tabs .ant-tabs-nav {
          margin-bottom: 16px;
        }
        .entry-tabs .ant-tabs-tab {
          font-weight: 600;
          font-size: 15px;
          padding: 8px 16px;
        }
        @media (max-width: 767px) {
          .entry-workspace-header {
            flex-direction: column;
            align-items: stretch;
          }
          .entry-workspace-title .ant-typography {
            overflow-wrap: normal;
            word-break: normal;
          }
          .entry-workspace-title > .ant-typography:last-child {
            display: block;
            margin-top: 4px;
          }
          .entry-workspace-actions {
            width: 100%;
            justify-content: flex-start;
          }
          .entry-file-select {
            flex: 1 0 100%;
            width: 100% !important;
            min-width: 0 !important;
          }
          .entry-file-status {
            margin-inline-end: 0;
          }
          .entry-workspace-actions > .ant-btn {
            min-height: 44px;
            flex: 1 1 140px;
          }
        }
      `}</style>

      <Tabs
        className="entry-tabs"
        activeKey={activeTab}
        onChange={handleTabChange}
        items={[
          {
            key: 'appraisal',
            label: (
              <span>
                <FileSearchOutlined style={{ marginRight: 6 }} />
                Nhập hồ sơ Thẩm định
              </span>
            ),
            children: (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                {/* Header and Workspace Controls */}
                <div className="entry-workspace-header">
                  <div className="entry-workspace-title">
                    <Title level={3} style={{ margin: 0 }}>Nhập hồ sơ thẩm định mới</Title>
                    <Text type="secondary">Tải lên tài liệu GCN, trích xuất dữ liệu tự động bằng AI và lưu thông tin vào cơ sở dữ liệu.</Text>
                  </div>

                  {uploadId && (
                    <div className="entry-workspace-actions">
                      {files.length > 1 && (
                        <Select
                          className="entry-file-select"
                          value={activeFileIndex}
                          onChange={handleFileChange}
                          style={{ minWidth: 240 }}
                          options={files.map((file, index) => ({
                            value: index,
                            label: `${index + 1}. ${file.name} (${scanStatusLabel(file.scanStatus)})`,
                          }))}
                        />
                      )}
                      {activeFile && (
                        <Tag className="entry-file-status" color={scanStatusColor(activeFile.scanStatus)}>
                          {scanStatusLabel(activeFile.scanStatus)}
                        </Tag>
                      )}
                      <OcrActions 
                        uploadId={uploadId} 
                        activeFile={activeFile} 
                        files={files}
                        onFileScanState={handleFileScanState}
                        onFileScanned={handleFileScanned}
                      />
                      <Button 
                        icon={<UploadOutlined />} 
                        onClick={handleReset}
                        style={{ borderRadius: 6 }}
                      >
                        Chọn tài liệu khác
                      </Button>
                    </div>
                  )}
                </div>

                {/* Main Workspace Layout */}
                <Row gutter={[16, 16]}>
                  {/* Left Panel: PDF/Image Document Viewer or File Uploader */}
                  <Col xs={24} lg={12}>
                    {!uploadId ? (
                      <Card 
                        style={{ borderRadius: 12, border: '1px solid #d8e7e5', minHeight: '400px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}
                        styles={{ body: { padding: '24px' } }}
                      >
                        <div style={{ textAlign: 'center', marginBottom: 24 }}>
                          <FilePdfOutlined style={{ fontSize: 44, color: '#007f7a' }} />
                          <Title level={4} style={{ marginTop: 12, marginBottom: 8 }}>Bắt đầu bằng cách tải lên hồ sơ GCN</Title>
                          <Text type="secondary" style={{ fontSize: '13px' }}>AI sẽ tự động nhận diện và trích xuất thông tin.</Text>
                        </div>
                        <FileUploader onUploadSuccess={handleUploadSuccess} />
                      </Card>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                        <FileUploader
                          uploadId={uploadId}
                          compact={false}
                          placeholderText="Kéo thả hoặc Click để tải lên GCN thứ 2, thứ 3..."
                          onUploadSuccess={handleUploadSuccess}
                        />
                        <PageViewer 
                          uploadId={uploadId}
                          activeFile={activeFile}
                          currentPage={currentPage}
                          onPageChange={handlePageChange}
                          rotation={rotation}
                          onRotationChange={setRotation}
                        />
                      </div>

                    )}
                  </Col>

                  {/* Right Panel: Entry Form */}
                  <Col xs={24} lg={12}>
                    <EntryForm 
                      uploadId={uploadId}
                      formValues={ocrData}
                      onSaveSuccess={handleSaveSuccess}
                    />
                  </Col>
                </Row>
              </div>
            )
          },
          {
            key: 'sobo',
            label: (
              <span>
                <FileTextOutlined style={{ marginRight: 6 }} />
                Nhập hồ sơ Sơ bộ
              </span>
            ),
            children: <SoboEntry />
          }
        ]}
      />
    </div>
  );
}
