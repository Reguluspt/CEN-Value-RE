import { reRequest } from './localServiceClient';

const casePath = (caseId) => `/api/re/manual-cases/${encodeURIComponent(caseId)}`;
const comparablePath = (caseId, order) => `${casePath(caseId)}/comparables/${order}`;

export const workbenchApi = {
  createCase(body) {
    return reRequest('/api/re/manual-cases', { method: 'POST', body });
  },
  resumeCase(caseId) {
    return reRequest(casePath(caseId));
  },
  saveSubject(caseId, body) {
    return reRequest(`${casePath(caseId)}/subject`, { method: 'PUT', body });
  },
  saveComparable(caseId, order, body) {
    return reRequest(comparablePath(caseId, order), { method: 'PUT', body });
  },
  adjustmentState(caseId, order) {
    return reRequest(`${comparablePath(caseId, order)}/adjustment`);
  },
  bindAdjustmentBase(caseId, order, body) {
    return reRequest(`${comparablePath(caseId, order)}/adjustment/base`, {
      method: 'PUT',
      body,
    });
  },
  selectAdjustmentRate(caseId, order, factorKey, body) {
    return reRequest(
      `${comparablePath(caseId, order)}/adjustments/${encodeURIComponent(factorKey)}`,
      { method: 'PUT', body },
    );
  },
  runAdjustment(caseId, order, body = {}) {
    return reRequest(`${comparablePath(caseId, order)}/adjustment/run`, {
      method: 'POST',
      body,
    });
  },
  quality(caseId) {
    return reRequest(`${casePath(caseId)}/quality`);
  },
  confirmIndication(caseId, body) {
    return reRequest(`${casePath(caseId)}/indication`, { method: 'POST', body });
  },
  currentIndication(caseId) {
    return reRequest(`${casePath(caseId)}/indication`);
  },
  bindConstruction(caseId, body) {
    return reRequest(`${casePath(caseId)}/construction-aggregate`, {
      method: 'PUT',
      body,
    });
  },
  composeFinal(caseId) {
    return reRequest(`${casePath(caseId)}/final-valuation`, {
      method: 'POST',
      body: {},
    });
  },
  currentFinal(caseId) {
    return reRequest(`${casePath(caseId)}/final-valuation`);
  },
  generateWorkbook(caseId, body) {
    return reRequest(`${casePath(caseId)}/workbook-output`, {
      method: 'POST',
      body,
    });
  },
};
