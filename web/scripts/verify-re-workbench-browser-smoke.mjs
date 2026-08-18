import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdtemp, rm } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';

const WEB_ROOT = path.resolve(import.meta.dirname, '..');
const VITE_PORT = 4174;
const CDP_PORT = 9333;
const PAGE_URL = `http://127.0.0.1:${VITE_PORT}/re-workbench-smoke.html`;
const CASE_ID = 'case-smoke-1';

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function waitFor(label, probe, { timeoutMs = 20000, intervalMs = 100 } = {}) {
  const deadline = Date.now() + timeoutMs;
  let lastError = null;
  while (Date.now() < deadline) {
    try {
      const result = await probe();
      if (result) return result;
    } catch (error) {
      lastError = error;
    }
    await delay(intervalMs);
  }
  const suffix = lastError ? ` Last error: ${lastError.message}` : '';
  throw new Error(`Timed out waiting for ${label}.${suffix}`);
}

function browserCandidates() {
  const candidates = [
    process.env.RE_BROWSER_PATH,
    process.env.CHROME_PATH,
    process.env.EDGE_PATH,
  ].filter(Boolean);

  if (process.platform === 'win32') {
    candidates.push(
      'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
      'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    );
  } else if (process.platform === 'darwin') {
    candidates.push(
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
    );
  } else {
    candidates.push(
      '/usr/bin/google-chrome',
      '/usr/bin/google-chrome-stable',
      '/usr/bin/chromium',
      '/usr/bin/chromium-browser',
      '/usr/bin/microsoft-edge',
    );
  }
  return [...new Set(candidates)];
}

function findBrowser() {
  const browser = browserCandidates().find((candidate) => existsSync(candidate));
  if (!browser) {
    throw new Error('No supported Chrome/Edge executable was found for browser smoke verification.');
  }
  return browser;
}

function killProcessTree(child) {
  if (!child || child.exitCode !== null || child.killed) return Promise.resolve();
  if (process.platform === 'win32') {
    return new Promise((resolve) => {
      const killer = spawn('taskkill', ['/PID', String(child.pid), '/T', '/F'], {
        stdio: 'ignore',
      });
      killer.on('error', () => resolve());
      killer.on('exit', () => resolve());
    });
  }
  try {
    process.kill(-child.pid, 'SIGTERM');
  } catch {
    try {
      child.kill('SIGTERM');
    } catch {
      // Best-effort cleanup only.
    }
  }
  return Promise.resolve();
}

class CdpClient {
  constructor(url) {
    this.url = url;
    this.socket = null;
    this.nextId = 1;
    this.pending = new Map();
  }

  async connect() {
    this.socket = new WebSocket(this.url);
    await new Promise((resolve, reject) => {
      const onOpen = () => {
        cleanup();
        resolve();
      };
      const onError = () => {
        cleanup();
        reject(new Error('CDP WebSocket connection failed.'));
      };
      const cleanup = () => {
        this.socket.removeEventListener('open', onOpen);
        this.socket.removeEventListener('error', onError);
      };
      this.socket.addEventListener('open', onOpen);
      this.socket.addEventListener('error', onError);
    });
    this.socket.addEventListener('message', (event) => {
      let payload;
      try {
        payload = JSON.parse(typeof event.data === 'string' ? event.data : Buffer.from(event.data).toString('utf8'));
      } catch {
        return;
      }
      if (!payload.id) return;
      const entry = this.pending.get(payload.id);
      if (!entry) return;
      this.pending.delete(payload.id);
      if (payload.error) {
        entry.reject(new Error(`CDP ${payload.error.code}: ${payload.error.message}`));
      } else {
        entry.resolve(payload.result);
      }
    });
  }

  command(method, params = {}) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      return Promise.reject(new Error('CDP socket is not open.'));
    }
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.socket.send(JSON.stringify({ id, method, params }));
    });
  }

  async evaluate(expression) {
    const result = await this.command('Runtime.evaluate', {
      expression,
      awaitPromise: true,
      returnByValue: true,
      userGesture: true,
    });
    if (result.exceptionDetails) {
      const description = result.exceptionDetails.exception?.description || result.exceptionDetails.text;
      throw new Error(`Browser evaluation failed: ${description}`);
    }
    return result.result?.value;
  }

  close() {
    try {
      this.socket?.close();
    } catch {
      // Best-effort cleanup only.
    }
  }
}

async function waitForVite() {
  await waitFor('Vite smoke page', async () => {
    const response = await fetch(PAGE_URL).catch(() => null);
    return response?.ok;
  }, { timeoutMs: 30000, intervalMs: 200 });
}

async function findPageTarget() {
  return waitFor('browser DevTools page target', async () => {
    const response = await fetch(`http://127.0.0.1:${CDP_PORT}/json/list`).catch(() => null);
    if (!response?.ok) return null;
    const targets = await response.json();
    return targets.find((target) => target.type === 'page' && target.webSocketDebuggerUrl) || null;
  }, { timeoutMs: 30000, intervalMs: 200 });
}

async function pageWait(cdp, label, expression, timeoutMs = 10000) {
  return waitFor(label, async () => Boolean(await cdp.evaluate(expression)), {
    timeoutMs,
    intervalMs: 75,
  });
}

async function dom(cdp, method, args) {
  const encoded = args.map((value) => JSON.stringify(value)).join(',');
  return cdp.evaluate(`globalThis.__RE_SMOKE_DOM.${method}(${encoded})`);
}

async function fill(cdp, section, label, value, article = null) {
  await dom(cdp, 'fill', [section, label, value, article]);
  await delay(50);
}

async function click(cdp, section, text, article = null) {
  await dom(cdp, 'click', [section, text, article]);
}

async function requestCount(cdp) {
  return Number(await cdp.evaluate('globalThis.__RE_SMOKE_REQUESTS.length'));
}

async function waitForRequest(cdp, previousCount, predicateExpression) {
  await pageWait(
    cdp,
    'expected /api/re request',
    `globalThis.__RE_SMOKE_REQUESTS.length > ${previousCount} && globalThis.__RE_SMOKE_REQUESTS.some((request) => (${predicateExpression}))`,
  );
}

async function assertPage(cdp, condition, message) {
  const ok = await cdp.evaluate(condition);
  if (!ok) throw new Error(message);
}

async function runSmoke(cdp) {
  await cdp.command('Page.enable');
  await cdp.command('Runtime.enable');
  await cdp.command('Page.navigate', { url: PAGE_URL });
  await pageWait(cdp, 'React workbench mount', 'globalThis.__RE_SMOKE_READY === true', 20000);

  await assertPage(
    cdp,
    `document.body.innerText.includes('Local-service session: ready')`,
    'Workbench did not recognize the in-memory local-service bootstrap.',
  );

  await fill(cdp, 'stage-case', 'Mã hồ sơ', 'SMOKE-001');
  await fill(cdp, 'stage-case', 'Ngày thẩm định', '2026-08-18');
  await fill(cdp, 'stage-case', 'Khách hàng', 'Smoke Client');
  await fill(cdp, 'stage-case', 'Mục đích', 'Browser proof');
  let count = await requestCount(cdp);
  await click(cdp, 'stage-case', 'Tạo hồ sơ');
  await waitForRequest(
    cdp,
    count,
    `request.path === '/api/re/manual-cases' && request.method === 'POST'`,
  );
  await assertPage(
    cdp,
    `globalThis.__RE_SMOKE_REQUESTS.some((request) => request.path === '/api/re/manual-cases' && request.headers['x-cenvalue-re-launch-id'] === 'launch-smoke' && request.headers.authorization === 'Bearer smoke-secret-token')`,
    'Launch ID/bearer headers were not attached to the browser workbench request.',
  );

  await fill(cdp, 'stage-subject', 'Địa chỉ pháp lý', '1 Test Street');
  await fill(cdp, 'stage-subject', 'Địa chỉ hiện tại', '1 Test Street');
  await fill(cdp, 'stage-subject', 'Tỉnh/TP', 'Tp. HCM');
  await fill(cdp, 'stage-subject', 'Số thửa', 'P-1');
  await fill(cdp, 'stage-subject', 'Tờ bản đồ', 'M-1');
  await fill(cdp, 'stage-subject', 'Tổng diện tích m²', '200');
  await fill(cdp, 'stage-subject', 'Diện tích phù hợp m²', '150');
  await fill(cdp, 'stage-subject', 'Diện tích không phù hợp m²', '50');
  await fill(cdp, 'stage-subject', 'Đơn giá đất không phù hợp', '5000000');
  await fill(cdp, 'stage-subject', 'Mặt tiền', '10');
  await fill(cdp, 'stage-subject', 'Chiều sâu', '20');
  await fill(cdp, 'stage-subject', 'Hình dạng', 'RECTANGLE');
  count = await requestCount(cdp);
  await click(cdp, 'stage-subject', 'Lưu TSTĐ');
  await waitForRequest(
    cdp,
    count,
    `request.path === '/api/re/manual-cases/${CASE_ID}/subject' && request.method === 'PUT'`,
  );

  for (const order of [1, 2, 3]) {
    const article = `TSSS0${order}`;
    await fill(cdp, 'stage-comparables', 'Địa chỉ pháp lý', `${article} legal`, article);
    await fill(cdp, 'stage-comparables', 'Địa chỉ hiện tại', `${article} current`, article);
    await fill(cdp, 'stage-comparables', 'Giá chào/bán', String(10000000000 + order), article);
    await fill(cdp, 'stage-comparables', 'Giá thương lượng', String(9500000000 + order), article);
    await fill(cdp, 'stage-comparables', 'Tỷ lệ thương lượng (%)', order === 1 ? '0.5' : '5', article);
    await fill(cdp, 'stage-comparables', 'Diện tích m²', '100', article);
    await fill(cdp, 'stage-comparables', 'Mặt tiền', '5', article);
    await fill(cdp, 'stage-comparables', 'Chiều sâu', '20', article);
    await fill(cdp, 'stage-comparables', 'Hình dạng', 'RECTANGLE', article);
    await fill(cdp, 'stage-comparables', 'Diện tích xây dựng', '80', article);
    await fill(cdp, 'stage-comparables', 'Chất lượng còn lại (fraction)', '0.8', article);
    count = await requestCount(cdp);
    await click(cdp, 'stage-comparables', `Lưu TSSS0${order}`, article);
    await waitForRequest(
      cdp,
      count,
      `request.path === '/api/re/manual-cases/${CASE_ID}/comparables/${order}' && request.method === 'PUT'`,
    );
  }
  await assertPage(
    cdp,
    `globalThis.__RE_SMOKE_REQUESTS.some((request) => request.path.endsWith('/comparables/1') && request.body?.negotiation_rate_pct === '0.005')`,
    '0.5% display input was not converted to canonical fraction 0.005.',
  );

  await cdp.command('Page.navigate', { url: PAGE_URL });
  await pageWait(cdp, 'workbench remount after reload', 'globalThis.__RE_SMOKE_READY === true', 20000);
  await fill(cdp, 'stage-case', 'Case ID để resume', CASE_ID);
  count = await requestCount(cdp);
  await click(cdp, 'stage-case', 'Resume');
  await waitForRequest(
    cdp,
    count,
    `request.path === '/api/re/manual-cases/${CASE_ID}' && request.method === 'GET'`,
  );
  await pageWait(
    cdp,
    'resume downstream reads',
    `globalThis.__RE_SMOKE_REQUESTS.some((request) => request.path.endsWith('/comparables/3/adjustment'))`,
  );
  await assertPage(
    cdp,
    `globalThis.__RE_SMOKE_DOM.value('stage-subject', 'Số thửa') === 'P-1' && globalThis.__RE_SMOKE_DOM.value('stage-comparables', 'Giá chào/bán', 'TSSS01') === '10000000001'`,
    'Reload/resume did not restore persisted subject/comparable inputs.',
  );
  await assertPage(
    cdp,
    `globalThis.__RE_SMOKE_DOM.text('stage-adjustments', 'TSSS01').includes('C1 (%) · đã nhập 0%')`,
    'Explicit zero C1 decision was not visibly distinct from missing after resume.',
  );

  await fill(cdp, 'stage-adjustments', 'Người chọn adjustment', 'Smoke Reviewer');
  count = await requestCount(cdp);
  await click(cdp, 'stage-adjustments', 'Lưu C1', 'TSSS01');
  await waitForRequest(
    cdp,
    count,
    `request.path.endsWith('/comparables/1/adjustments/C1') && request.body?.selected_rate === '0'`,
  );
  count = await requestCount(cdp);
  await click(cdp, 'stage-adjustments', 'Chạy adjustment', 'TSSS01');
  await waitForRequest(
    cdp,
    count,
    `request.path.endsWith('/comparables/1/adjustment/run') && request.method === 'POST'`,
  );

  count = await requestCount(cdp);
  await click(cdp, 'stage-quality', 'Đọc quality/readiness');
  await waitForRequest(cdp, count, `request.path.endsWith('/quality') && request.method === 'GET'`);

  await fill(cdp, 'stage-indication', 'Người xác nhận', 'Smoke Reviewer');
  await fill(cdp, 'stage-indication', 'Lý do', 'Browser vertical smoke');
  count = await requestCount(cdp);
  await click(cdp, 'stage-indication', 'Xác nhận human indication');
  await waitForRequest(cdp, count, `request.path.endsWith('/indication') && request.method === 'POST'`);

  await fill(cdp, 'stage-final', 'Construction aggregate (VND)', '500000000');
  await fill(cdp, 'stage-final', 'Evidence ref', 'CONSTRUCTION-SMOKE');
  await fill(cdp, 'stage-final', 'Người cung cấp', 'Smoke Reviewer');
  count = await requestCount(cdp);
  await click(cdp, 'stage-final', 'Bind construction aggregate');
  await waitForRequest(cdp, count, `request.path.endsWith('/construction-aggregate') && request.method === 'PUT'`);
  count = await requestCount(cdp);
  await click(cdp, 'stage-final', 'Compose final valuation');
  await waitForRequest(cdp, count, `request.path.endsWith('/final-valuation') && request.method === 'POST'`);

  await fill(cdp, 'stage-export', 'Supported source template path', 'C:\\fixtures\\N08_0038.xlsx');
  await fill(cdp, 'stage-export', 'New output path', 'C:\\outputs\\blocked.xlsx');
  count = await requestCount(cdp);
  await click(cdp, 'stage-export', 'Tạo workbook');
  await waitForRequest(cdp, count, `request.path.endsWith('/workbook-output') && request.method === 'POST'`);
  await pageWait(
    cdp,
    'structured workbook error rendering',
    `globalThis.__RE_SMOKE_DOM.alertText().includes('RE_WORKBOOK_BLOCKED: Workbook prerequisites are stale.')`,
  );
  await assertPage(
    cdp,
    `!globalThis.__RE_SMOKE_DOM.alertText().includes('smoke-secret-token')`,
    'Structured error rendering leaked the bearer token.',
  );

  await fill(cdp, 'stage-export', 'New output path', 'C:\\outputs\\generated.xlsx');
  count = await requestCount(cdp);
  await click(cdp, 'stage-export', 'Tạo workbook');
  await waitForRequest(cdp, count, `request.path.endsWith('/workbook-output') && request.body?.output_path?.endsWith('generated.xlsx')`);
  await pageWait(
    cdp,
    'successful workbook artifact rendering',
    `globalThis.__RE_SMOKE_DOM.text('stage-export').includes('"workbook_generated": true') && globalThis.__RE_SMOKE_DOM.text('stage-export').includes('"excel_qualification_status": "NOT_RUN"')`,
  );

  await assertPage(
    cdp,
    `globalThis.__RE_SMOKE_REQUESTS.every((request) => request.path.startsWith('/api/re/') && request.headers['x-cenvalue-re-launch-id'] === 'launch-smoke' && request.headers.authorization === 'Bearer smoke-secret-token')`,
    'One or more browser workbench calls escaped /api/re or missed current launch credentials.',
  );

  console.log('E1-PR-006 browser vertical smoke PASSED');
  console.log('- real Chromium/Edge page mounted the Astryx manual workbench');
  console.log('- create/subject/TSSS/adjustment/quality/indication/final/workbook request path exercised');
  console.log('- 0.5% became exact canonical fraction 0.005 without binary-float conversion');
  console.log('- reload/resume restored persisted inputs and explicit 0% remained visibly entered');
  console.log('- canonical structured 409 error rendered without bearer leakage');
  console.log('- successful workbook response remained excel_qualification_status=NOT_RUN');
  console.log('- every browser request stayed under /api/re and carried the in-memory launch credentials');
}

let vite = null;
let browser = null;
let cdp = null;
let profileDir = null;
let viteOutput = '';
let browserOutput = '';

try {
  const viteEntry = path.join(WEB_ROOT, 'node_modules', 'vite', 'bin', 'vite.js');
  vite = spawn(
    process.execPath,
    [viteEntry, '--host', '127.0.0.1', '--port', String(VITE_PORT), '--strictPort'],
    {
      cwd: WEB_ROOT,
      detached: process.platform !== 'win32',
      stdio: ['ignore', 'pipe', 'pipe'],
    },
  );
  vite.stdout.on('data', (chunk) => {
    viteOutput += chunk.toString();
  });
  vite.stderr.on('data', (chunk) => {
    viteOutput += chunk.toString();
  });
  await waitForVite();

  const browserPath = findBrowser();
  profileDir = await mkdtemp(path.join(os.tmpdir(), 'cenvalue-re-smoke-'));
  browser = spawn(
    browserPath,
    [
      '--headless=new',
      '--disable-gpu',
      '--no-first-run',
      '--no-default-browser-check',
      '--remote-allow-origins=*',
      '--remote-debugging-address=127.0.0.1',
      `--remote-debugging-port=${CDP_PORT}`,
      `--user-data-dir=${profileDir}`,
      'about:blank',
    ],
    {
      detached: process.platform !== 'win32',
      stdio: ['ignore', 'pipe', 'pipe'],
    },
  );
  browser.stdout.on('data', (chunk) => {
    browserOutput += chunk.toString();
  });
  browser.stderr.on('data', (chunk) => {
    browserOutput += chunk.toString();
  });

  const target = await findPageTarget();
  cdp = new CdpClient(target.webSocketDebuggerUrl);
  await cdp.connect();
  await runSmoke(cdp);
} catch (error) {
  console.error(error.stack || error.message || String(error));
  if (viteOutput.trim()) console.error(`--- Vite output ---\n${viteOutput.trim()}`);
  if (browserOutput.trim()) console.error(`--- Browser output ---\n${browserOutput.trim()}`);
  process.exitCode = 1;
} finally {
  cdp?.close();
  await killProcessTree(browser);
  await killProcessTree(vite);
  if (profileDir) {
    await rm(profileDir, { recursive: true, force: true }).catch(() => {});
  }
}
