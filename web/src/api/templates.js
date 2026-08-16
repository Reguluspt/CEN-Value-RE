import client from './client';

export const getTemplates = () => {
  return client.get('/templates');
};

export const getTemplateDetail = (name, groupId) => {
  return client.get(`/templates/${encodeURIComponent(name)}`, { params: groupId ? { group_id: groupId } : {} });
};

export const uploadTemplateVersion = (name, formData, groupId) => {
  return client.put(`/templates/${encodeURIComponent(name)}`, formData, {
    params: groupId ? { group_id: groupId } : {},
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const getTemplateHistory = (name, groupId) => {
  return client.get(`/templates/${encodeURIComponent(name)}/history`, { params: groupId ? { group_id: groupId } : {} });
};

export const downloadTemplate = (name, groupId) => {
  return client.get(`/templates/${encodeURIComponent(name)}/download`, {
    params: groupId ? { group_id: groupId } : {},
    responseType: 'blob',
  });
};

export const getTemplateEditorConfig = (name, groupId) => {
  return client.get(`/templates/${encodeURIComponent(name)}/onlyoffice-config`, { params: groupId ? { group_id: groupId } : {} });
};

export const getTemplateAutofillPreviewConfig = (name, caseId, groupId) => {
  return client.post(
    `/templates/${encodeURIComponent(name)}/onlyoffice-preview-config`,
    { case_id: caseId },
    { params: groupId ? { group_id: groupId } : {} },
  );
};

export const getTemplateGroups = (customerType) =>
  client.get('/template-groups', { params: customerType ? { customer_type: customerType } : {} });

export const createTemplateGroup = (formData) =>
  client.post('/template-groups', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
