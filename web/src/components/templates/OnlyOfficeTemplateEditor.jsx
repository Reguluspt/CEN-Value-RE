import { useCallback, useEffect, useRef, useState } from 'react';
import { Alert, Button, Drawer, Spin } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';
import { getTemplateAutofillPreviewConfig, getTemplateDetail, getTemplateEditorConfig } from '../../api/templates';
import PlaceholderPanel from './PlaceholderPanel';

const SCRIPT_ID = 'onlyoffice-document-editor-api';
const EDITOR_ID = 'onlyoffice-template-editor';

function loadOnlyOfficeApi(documentServerUrl) {
  if (window.DocsAPI?.DocEditor) return Promise.resolve();

  return new Promise((resolve, reject) => {
    const scriptUrl = `${documentServerUrl}/web-apps/apps/api/documents/api.js`;
    let script = document.getElementById(SCRIPT_ID);

    if (script) {
      script.remove();
      script = null;
    }

    script = document.createElement('script');
    script.id = SCRIPT_ID;
    script.dataset.src = scriptUrl;
    script.src = scriptUrl;

    const handleLoad = () => {
      cleanup();
      if (window.DocsAPI?.DocEditor) resolve();
      else reject(new Error('ONLYOFFICE API không khởi tạo được'));
    };
    const handleError = () => {
      cleanup();
      reject(new Error('Không thể kết nối ONLYOFFICE Document Server'));
    };
    const cleanup = () => {
      script.removeEventListener('load', handleLoad);
      script.removeEventListener('error', handleError);
    };

    script.addEventListener('load', handleLoad);
    script.addEventListener('error', handleError);
    document.head.appendChild(script);
  });
}

export default function OnlyOfficeTemplateEditor({
  open,
  templateName,
  groupId,
  displayName,
  onClose,
  previewCaseId,
  previewCaseLabel,
}) {
  const editorRef = useRef(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [reloadKey, setReloadKey] = useState(0);
  const [placeholderDetail, setPlaceholderDetail] = useState(null);
  const [placeholderLoading, setPlaceholderLoading] = useState(false);
  const [previewWarnings, setPreviewWarnings] = useState(null);
  const previewMode = Boolean(previewCaseId);

  const refreshPlaceholderStatus = useCallback(async () => {
    if (!templateName || previewMode) return;
    setPlaceholderLoading(true);
    try {
      const response = await getTemplateDetail(templateName, groupId);
      setPlaceholderDetail(response.data);
    } catch {
      setPlaceholderDetail(null);
    } finally {
      setPlaceholderLoading(false);
    }
  }, [templateName, groupId, previewMode]);

  useEffect(() => {
    if (!open || !templateName) return undefined;

    let cancelled = false;

    const initialize = async () => {
      if (cancelled) return;
      setLoading(true);
      setError('');
      try {
        const response = previewMode
          ? await getTemplateAutofillPreviewConfig(templateName, previewCaseId, groupId)
          : await getTemplateEditorConfig(templateName, groupId);
        const { document_server_url: documentServerUrl, config } = response.data;
        setPreviewWarnings(previewMode ? {
          missingData: response.data.missing_data_placeholders || [],
          unresolved: response.data.unresolved_placeholders || [],
          invalid: response.data.invalid_placeholders || [],
        } : null);
        await loadOnlyOfficeApi(documentServerUrl);
        if (cancelled) return;

        editorRef.current = new window.DocsAPI.DocEditor(EDITOR_ID, {
          ...config,
          events: {
            onAppReady: () => setLoading(false),
            onDocumentReady: () => setLoading(false),
            onError: (event) => {
              setLoading(false);
              setError(`ONLYOFFICE gặp lỗi (${event?.data?.errorCode ?? 'không xác định'}).`);
            },
            onRequestClose: onClose,
          },
        });
      } catch (err) {
        if (cancelled) return;
        setLoading(false);
        setPreviewWarnings(null);
        setError(err.response?.data?.error || err.message || 'Không thể mở trình soạn thảo Word');
      }
    };

    queueMicrotask(() => {
      if (!previewMode) refreshPlaceholderStatus();
      initialize();
    });
    return () => {
      cancelled = true;
      if (editorRef.current?.destroyEditor) {
        editorRef.current.destroyEditor();
      }
      editorRef.current = null;
    };
  }, [open, templateName, groupId, onClose, previewCaseId, previewMode, reloadKey, refreshPlaceholderStatus]);

  const missingData = previewWarnings?.missingData || [];
  const unresolved = previewWarnings?.unresolved || [];
  const invalid = previewWarnings?.invalid || [];
  const hasPreviewWarnings = missingData.length + unresolved.length + invalid.length > 0;

  return (
    <Drawer
      title={`${previewMode ? 'Xem thử tự điền' : 'Soạn thảo Word'}: ${displayName || templateName || ''}`}
      placement="right"
      width="100%"
      open={open}
      onClose={onClose}
      destroyOnClose
      styles={{ body: { padding: 0, overflow: 'hidden', position: 'relative' } }}
    >
      <div style={{ display: 'flex', width: '100%', height: 'calc(100vh - 56px)' }}>
        <div style={{ position: 'relative', flex: 1, minWidth: 0, height: '100%' }}>
          <div id={EDITOR_ID} style={{ width: '100%', height: '100%' }} />

          {loading && (
            <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', background: '#fff' }}>
              <Spin size="large" tip="Đang mở trình soạn thảo Word..." />
            </div>
          )}

          {error && (
            <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', padding: 32, background: '#f8fafc' }}>
              <Alert
                type="error"
                showIcon
                message="Không thể mở trình soạn thảo"
                description={error}
                action={(
                  <Button icon={<ReloadOutlined />} onClick={() => setReloadKey((value) => value + 1)}>
                    Thử lại
                  </Button>
                )}
              />
            </div>
          )}
        </div>
        {previewMode ? (
          <aside style={{ width: 320, padding: 16, overflowY: 'auto', borderLeft: '1px solid #e5e7eb', background: '#fff' }}>
            <div style={{ fontWeight: 700, marginBottom: 4 }}>Dữ liệu xem thử</div>
            <div style={{ color: '#64748b', fontSize: 12, marginBottom: 14 }}>{previewCaseLabel || `Hồ sơ #${previewCaseId}`}</div>
            <Alert
              type={hasPreviewWarnings ? 'warning' : 'success'}
              showIcon
              message={hasPreviewWarnings ? 'Cần kiểm tra dữ liệu' : 'Đã tự điền đầy đủ các thẻ'}
              description={hasPreviewWarnings ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {missingData.length > 0 && <div><strong>Chưa có dữ liệu:</strong><br />{missingData.map((key) => `{{${key}}}`).join(', ')}</div>}
                  {unresolved.length > 0 && <div><strong>Thẻ chưa hỗ trợ:</strong><br />{unresolved.map((key) => `{{${key}}}`).join(', ')}</div>}
                  {invalid.length > 0 && <div><strong>Thẻ sai cú pháp:</strong><br />{invalid.join(', ')}</div>}
                </div>
              ) : 'Bản xem thử được tạo từ dữ liệu hồ sơ đã chọn.'}
            />
            <div style={{ color: '#64748b', fontSize: 12, marginTop: 14 }}>
              Đây là bản tạm chỉ xem, không làm thay đổi file mẫu và không tạo văn bản chính thức.
            </div>
          </aside>
        ) : (
          <PlaceholderPanel
            detail={placeholderDetail}
            loading={placeholderLoading}
            onRefresh={refreshPlaceholderStatus}
          />
        )}
      </div>
    </Drawer>
  );
}
