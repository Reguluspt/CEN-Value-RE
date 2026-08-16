import React, { useState, useRef } from 'react';
import { Upload, message, Progress, Card } from 'antd';
import { InboxOutlined, PlusCircleOutlined } from '@ant-design/icons';
import { uploadFiles } from '../../api/entry';

const { Dragger } = Upload;

export default function FileUploader({
  onUploadSuccess,
  uploadId = null,
  compact = false,
  placeholderText = null,
  hintText = null,
}) {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const uploadingRef = useRef(false);

  const startBatchUpload = async (filesToUpload) => {
    if (!filesToUpload || !filesToUpload.length || uploadingRef.current) return;

    uploadingRef.current = true;
    setUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    if (uploadId) {
      formData.append('upload_id', uploadId);
    }
    filesToUpload.forEach((file) => {
      formData.append('files', file.originFileObj || file);
    });

    try {
      const res = await uploadFiles(formData, (percent) => {
        setUploadProgress(percent);
      });

      message.success(`Đã tải lên ${filesToUpload.length} file tài liệu thành công!`);
      if (onUploadSuccess && res.data) {
        onUploadSuccess(res.data.upload_id, res.data.files, !!uploadId);
      }
    } catch (err) {
      console.error(err);
      message.error(err.response?.data?.error || 'Tải file thất bại.');
    } finally {
      uploadingRef.current = false;
      setUploading(false);
    }
  };

  const pendingBatchRef = useRef([]);
  const timerRef = useRef(null);

  const handleBeforeUpload = (file) => {
    pendingBatchRef.current.push(file);

    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }

    timerRef.current = setTimeout(() => {
      const batch = [...pendingBatchRef.current];
      pendingBatchRef.current = [];
      startBatchUpload(batch);
    }, 150);

    return false; // Prevent default upload action of Ant Design Dragger
  };

  if (compact) {
    return (
      <div style={{ marginTop: 8 }}>
        <Dragger
          name="files"
          multiple
          accept=".pdf,.png,.jpg,.jpeg,.webp"
          beforeUpload={handleBeforeUpload}
          showUploadList={false}
          disabled={uploading}
          style={{
            background: '#f8fafc',
            border: '1px dashed #007f7a',
            borderRadius: 8,
            padding: '8px 12px'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
            <PlusCircleOutlined style={{ fontSize: 18, color: '#007f7a' }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: '#0f172a' }}>
              {placeholderText || '➕ Kéo thả hoặc Click để tải lên file bổ sung...'}
            </span>
          </div>
        </Dragger>
        {uploading && (
          <div style={{ marginTop: 6, textAlign: 'center' }}>
            <span style={{ fontSize: 12, color: '#007f7a', fontWeight: 500 }}>
              Đang tải lên file bổ sung...
            </span>
            <Progress percent={uploadProgress} size="small" status="active" style={{ marginTop: 2 }} />
          </div>
        )}
      </div>
    );
  }

  return (
    <Card
      style={{ borderRadius: 10, border: '1px dashed #d8e7e5', padding: 4 }}
      bodyStyle={{ padding: 12 }}
    >
      <Dragger
        name="files"
        multiple
        accept=".pdf,.png,.jpg,.jpeg,.webp"
        beforeUpload={handleBeforeUpload}
        showUploadList={false}
        disabled={uploading}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined style={{ color: '#007f7a' }} />
        </p>
        <p className="ant-upload-text" style={{ fontSize: 15, fontWeight: 500 }}>
          {placeholderText || 'Kéo thả hoặc Click để tải lên GCN'}
        </p>
        <p className="ant-upload-hint" style={{ fontSize: 12, color: '#8c8c8c' }}>
          {hintText || 'Tự động tải lên & quét AI bằng Gemini 2.5 Flash ngay sau khi chọn file'}
        </p>
      </Dragger>


      {uploading && (
        <div style={{ marginTop: 12, textAlign: 'center' }}>
          <span style={{ fontSize: 13, color: '#007f7a', fontWeight: 500 }}>
            Đang tải lên và xử lý các trang file GCN...
          </span>
          <Progress percent={uploadProgress} size="small" status="active" style={{ marginTop: 4 }} />
        </div>
      )}
    </Card>
  );
}
