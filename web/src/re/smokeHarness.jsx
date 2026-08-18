import { createRoot } from 'react-dom/client';
import ReShell from './ReShell';
import { installReBootstrap } from './localServiceClient';

const FACTORS = Array.from({ length: 11 }, (_, index) => `C${index + 1}`);
const CASE_ID = 'case-smoke-1';

const characteristic = (definitionKey, field, value) => ({
  definition_key: definitionKey,
  [field]: value,
});

const comparable = (order) => ({
  property: {
    id: `comparable-${order}`,
    comparable_order: order,
    legal_address: `TSSS${order} legal`,
    current_address: `TSSS${order} current`,
  },
  market_observation: {
    asking_or_sale_price_vnd: String(10_000_000_000 + order),
    negotiated_price_vnd: String(9_500_000_000 + order),
    negotiation_rate_pct: '0.05',
  },
  characteristics: [
    characteristic('area_m2', 'decimal_value', '100'),
    characteristic('frontage', 'decimal_value', '5'),
    characteristic('depth', 'decimal_value', '20'),
    characteristic('shape', 'text_value', 'RECTANGLE'),
    characteristic('building_area_m2', 'decimal_value', '80'),
    characteristic('building_remaining_quality', 'decimal_value', '0.8'),
  ],
});

const persistedSnapshot = {
  case: {
    id: CASE_ID,
    case_code: 'SMOKE-001',
    appraisal_date: '2026-08-18',
    profile_id: 'cenvalue-re-n08-0038-v1',
    profile_version: '1',
    client_name: 'Smoke Client',
    valuation_purpose: 'Browser proof',
  },
  subject: {
    property: {
      id: 'subject-smoke',
      legal_address: '1 Test Street',
      current_address: '1 Test Street',
      latitude: null,
      longitude: null,
    },
    parcels: [
      {
        parcel_number: 'P-1',
        map_sheet_number: 'M-1',
        total_area_m2: '200',
      },
    ],
    land_valuation_components: [
      {
        planning_status: 'COMPLIANT',
        valuation_basis: 'MARKET_INDICATED',
        area_m2: '150',
      },
      {
        planning_status: 'NON_COMPLIANT',
        valuation_basis: 'OFFICIAL_LAND_PRICE',
        area_m2: '50',
        unit_price_vnd_per_m2: '5000000',
      },
    ],
    characteristics: [
      characteristic('address.current.province', 'text_value', 'Tp. HCM'),
      characteristic('frontage', 'decimal_value', '10'),
      characteristic('depth', 'decimal_value', '20'),
      characteristic('shape', 'text_value', 'RECTANGLE'),
    ],
  },
  comparables: [1, 2, 3].map(comparable),
};

const adjustmentState = (order) => ({
  comparable_order: order,
  source_state: {
    normalized_base_price_vnd_per_m2: String(100_000_000 + order),
    normalized_base_evidence_ref: `P0-EVIDENCE-${order}`,
    source_revision: 7,
  },
  decisions: FACTORS.map((factorKey, index) => ({
    factor_key: factorKey,
    selected_rate_pct: order === 1 && index === 0 ? '0' : '0.01',
    selected_explicitly: true,
    review_status: 'CURRENT',
  })),
  current_run: {
    snapshot_id: `adjustment-${order}`,
    semantic_sha256: String(order).repeat(64),
  },
});

const qualityPayload = {
  status: 'READY',
  threshold_pct: '0.15',
  comparable_orders: [1, 2, 3],
};

const indicationPayload = {
  snapshot_id: 'indication-smoke',
  selection_kind: 'COMPARABLE',
  selected_comparable_order: 1,
  confirmed_by: 'Smoke Reviewer',
};

const finalPayload = {
  snapshot_id: 'final-smoke',
  semantic_sha256: 'f'.repeat(64),
  final_value_vnd: '12300000000',
};

const requests = [];

globalThis.__RE_SMOKE_REQUESTS = requests;

globalThis.fetch = async (input, init = {}) => {
  const url = new URL(typeof input === 'string' ? input : input.url);
  const method = String(init.method || 'GET').toUpperCase();
  const headers = Object.fromEntries(new Headers(init.headers || {}).entries());
  let body = null;
  if (typeof init.body === 'string' && init.body) {
    body = JSON.parse(init.body);
  }
  requests.push({ path: url.pathname, method, headers, body });

  let status = 200;
  let payload = null;

  if (url.pathname === '/api/re/manual-cases' && method === 'POST') {
    payload = persistedSnapshot;
  } else if (url.pathname === `/api/re/manual-cases/${CASE_ID}` && method === 'GET') {
    payload = persistedSnapshot;
  } else if (
    url.pathname === `/api/re/manual-cases/${CASE_ID}/subject` &&
    method === 'PUT'
  ) {
    payload = persistedSnapshot;
  } else if (
    /^\/api\/re\/manual-cases\/case-smoke-1\/comparables\/[123]$/.test(url.pathname) &&
    method === 'PUT'
  ) {
    payload = persistedSnapshot;
  } else {
    const adjustmentMatch = url.pathname.match(
      /^\/api\/re\/manual-cases\/case-smoke-1\/comparables\/([123])\/adjustment$/,
    );
    const baseMatch = url.pathname.match(
      /^\/api\/re\/manual-cases\/case-smoke-1\/comparables\/([123])\/adjustment\/base$/,
    );
    const decisionMatch = url.pathname.match(
      /^\/api\/re\/manual-cases\/case-smoke-1\/comparables\/([123])\/adjustments\/(C(?:[1-9]|10|11))$/,
    );
    const runMatch = url.pathname.match(
      /^\/api\/re\/manual-cases\/case-smoke-1\/comparables\/([123])\/adjustment\/run$/,
    );

    if (adjustmentMatch && method === 'GET') {
      payload = adjustmentState(Number(adjustmentMatch[1]));
    } else if (baseMatch && method === 'PUT') {
      payload = { source_revision: 7, comparable_order: Number(baseMatch[1]) };
    } else if (decisionMatch && method === 'PUT') {
      payload = {
        comparable_order: Number(decisionMatch[1]),
        factor_key: decisionMatch[2],
        selected_rate_pct: body?.selected_rate ?? null,
        selected_explicitly: true,
      };
    } else if (runMatch && method === 'POST') {
      payload = {
        snapshot_id: `adjustment-${runMatch[1]}`,
        semantic_sha256: runMatch[1].repeat(64),
      };
    } else if (
      url.pathname === `/api/re/manual-cases/${CASE_ID}/quality` &&
      method === 'GET'
    ) {
      payload = qualityPayload;
    } else if (
      url.pathname === `/api/re/manual-cases/${CASE_ID}/indication` &&
      method === 'GET'
    ) {
      payload = indicationPayload;
    } else if (
      url.pathname === `/api/re/manual-cases/${CASE_ID}/indication` &&
      method === 'POST'
    ) {
      payload = { ...indicationPayload, ...body };
    } else if (
      url.pathname === `/api/re/manual-cases/${CASE_ID}/construction-aggregate` &&
      method === 'PUT'
    ) {
      payload = { status: 'BOUND', ...body };
    } else if (
      url.pathname === `/api/re/manual-cases/${CASE_ID}/final-valuation` &&
      method === 'GET'
    ) {
      payload = finalPayload;
    } else if (
      url.pathname === `/api/re/manual-cases/${CASE_ID}/final-valuation` &&
      method === 'POST'
    ) {
      payload = finalPayload;
    } else if (
      url.pathname === `/api/re/manual-cases/${CASE_ID}/workbook-output` &&
      method === 'POST'
    ) {
      if (String(body?.output_path || '').includes('blocked')) {
        status = 409;
        payload = {
          error: {
            code: 'RE_WORKBOOK_BLOCKED',
            message: 'Workbook prerequisites are stale.',
          },
        };
      } else {
        payload = {
          workbook_generated: true,
          excel_qualification_status: 'NOT_RUN',
          output_sha256: 'a'.repeat(64),
          output_path: body?.output_path,
          source_binding: {
            case_id: CASE_ID,
            final_valuation_snapshot_id: finalPayload.snapshot_id,
            final_valuation_semantic_sha256: finalPayload.semantic_sha256,
          },
        };
      }
    } else {
      status = 404;
      payload = {
        error: {
          code: 'RE_SMOKE_ROUTE_MISSING',
          message: `${method} ${url.pathname} is not implemented by the smoke harness.`,
        },
      };
    }
  }

  return new Response(JSON.stringify(payload), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
};

function sectionScope(sectionId, articlePrefix = null) {
  const section = document.querySelector(`[aria-labelledby="${sectionId}"]`);
  if (!section) throw new Error(`section not found: ${sectionId}`);
  if (!articlePrefix) return section;
  const article = [...section.querySelectorAll('article')].find((candidate) =>
    candidate.querySelector('h3')?.textContent?.trim().startsWith(articlePrefix),
  );
  if (!article) throw new Error(`article not found: ${articlePrefix}`);
  return article;
}

function setControlValue(control, value) {
  const prototype =
    control.tagName === 'SELECT' ? HTMLSelectElement.prototype : HTMLInputElement.prototype;
  const setter = Object.getOwnPropertyDescriptor(prototype, 'value')?.set;
  if (!setter) throw new Error('native value setter unavailable');
  setter.call(control, value);
  control.dispatchEvent(new Event(control.tagName === 'SELECT' ? 'change' : 'input', { bubbles: true }));
  if (control.tagName !== 'SELECT') {
    control.dispatchEvent(new Event('change', { bubbles: true }));
  }
}

globalThis.__RE_SMOKE_DOM = {
  fill(sectionId, labelText, value, articlePrefix = null) {
    const scope = sectionScope(sectionId, articlePrefix);
    const label = [...scope.querySelectorAll('label')].find(
      (candidate) => candidate.querySelector('span')?.textContent?.trim() === labelText,
    );
    if (!label) throw new Error(`field not found: ${labelText}`);
    const control = label.querySelector('input, select');
    if (!control) throw new Error(`control not found: ${labelText}`);
    setControlValue(control, value);
    return true;
  },
  click(sectionId, buttonText, articlePrefix = null) {
    const scope = sectionScope(sectionId, articlePrefix);
    const button = [...scope.querySelectorAll('button')].find(
      (candidate) => candidate.textContent?.trim() === buttonText,
    );
    if (!button) throw new Error(`button not found: ${buttonText}`);
    if (button.disabled) throw new Error(`button disabled: ${buttonText}`);
    button.click();
    return true;
  },
  value(sectionId, labelText, articlePrefix = null) {
    const scope = sectionScope(sectionId, articlePrefix);
    const label = [...scope.querySelectorAll('label')].find(
      (candidate) => candidate.querySelector('span')?.textContent?.trim() === labelText,
    );
    return label?.querySelector('input, select')?.value ?? null;
  },
  text(sectionId, articlePrefix = null) {
    return sectionScope(sectionId, articlePrefix).innerText;
  },
  alertText() {
    return document.querySelector('[role="alert"]')?.textContent?.trim() || '';
  },
};

installReBootstrap({
  base_url: 'http://127.0.0.1:65500',
  launch_id: 'launch-smoke',
  bearer_token: 'smoke-secret-token',
});

createRoot(document.getElementById('root')).render(<ReShell />);
requestAnimationFrame(() => {
  globalThis.__RE_SMOKE_READY = true;
});
