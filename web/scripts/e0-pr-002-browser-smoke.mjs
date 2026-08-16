import { chromium } from 'playwright';
import assert from 'node:assert/strict';

const baseURL = process.env.E0_PR_002_BASE_URL || 'http://127.0.0.1:5173';
const browser = await chromium.launch({ headless: true });

async function createTestPage(user) {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const page = await context.newPage();
  const pageErrors = [];
  const consoleErrors = [];

  page.on('pageerror', error => pageErrors.push(String(error)));
  page.on('console', message => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });

  await page.route(`${baseURL}/api/**`, async route => {
    const path = new URL(route.request().url()).pathname;
    let body = {};

    if (path === '/api/auth/me') {
      body = { user };
    } else if (path === '/api/dashboard/stats') {
      body = {
        selected_month: '', available_months: [], monthly_revenue: [], daily_revenue: [],
        bank_revenue: [], unpaid_cases: [], year_paid: 0, year_unpaid: 0,
        unpaid_total: 0, unpaid_count: 0, total_cases: 0, total_revenue: 0,
        total_paid: 0, total_unpaid: 0
      };
    } else if (path === '/api/dashboard/recent-cases') {
      body = [];
    } else if (path === '/api/dashboard/filters') {
      body = { years: ['2026'], branches: [], staff_names: [], statuses: [], customer_types: [] };
    } else if (path === '/api/cases/filters') {
      body = { statuses: [], branches: [], staff_names: [], customer_types: [] };
    } else if (path === '/api/cases') {
      body = { items: [], total: 0 };
    } else if (path === '/api/sobo/stats') {
      body = { pending_count: 0, responded_count: 0, avg_duration_secs: 0, has_overdue: false };
    } else if (path === '/api/sobo') {
      body = { items: [], total: 0 };
    }

    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) });
  });

  return { context, page, pageErrors, consoleErrors };
}

async function assertRedirectForUser(user, expectedPath, label) {
  const test = await createTestPage(user);
  try {
    await test.page.goto(`${baseURL}/re`, { waitUntil: 'domcontentloaded' });
    await test.page.waitForURL(
      url => url.pathname === expectedPath,
      { timeout: 15000 }
    );
    assert.equal(
      await test.page.locator('[data-re-astryx-spike="v1"]').count(),
      0,
      `${label} must not render the /re Astryx surface`
    );
  } finally {
    await test.context.close();
  }
}

await assertRedirectForUser(null, '/login', 'Unauthenticated user');
await assertRedirectForUser(
  { id: 2, username: 'guest', role: 'guest' },
  '/sobo',
  'Guest user'
);

const admin = await createTestPage({ id: 1, username: 'admin', role: 'admin' });
const { context, page, pageErrors, consoleErrors } = admin;

async function diagnostics(label) {
  const bodyText = await page.locator('body').innerText().catch(() => '<body unavailable>');
  console.error(`DIAGNOSTIC ${label}`);
  console.error(`url=${page.url()}`);
  console.error(`body=${bodyText.slice(0, 5000)}`);
  console.error(`pageErrors=${JSON.stringify(pageErrors)}`);
  console.error(`consoleErrors=${JSON.stringify(consoleErrors)}`);
}

async function waitForText(text, label) {
  try {
    await page.getByText(text, { exact: false }).first().waitFor({ state: 'visible', timeout: 15000 });
    await page.waitForTimeout(250);
  } catch (error) {
    await diagnostics(label);
    throw error;
  }
}

async function firstGoto(path, text) {
  await page.goto(`${baseURL}${path}`, { waitUntil: 'networkidle' });
  await waitForText(text, `firstGoto:${path}`);
}

async function spaGoto(path, text) {
  await page.evaluate((nextPath) => {
    window.history.pushState({}, '', nextPath);
    window.dispatchEvent(new PopStateEvent('popstate'));
  }, path);
  await waitForText(text, `spaGoto:${path}`);
}

async function currentStyleSnapshot(selector) {
  return page.evaluate((sel) => {
    const body = getComputedStyle(document.body);
    const el = document.querySelector(sel);
    const target = el ? getComputedStyle(el) : null;
    return {
      bodyFontFamily: body.fontFamily,
      bodyFontSize: body.fontSize,
      bodyMargin: body.margin,
      bodyBackground: body.backgroundColor,
      targetFontFamily: target?.fontFamily ?? null,
      targetFontSize: target?.fontSize ?? null,
      targetColor: target?.color ?? null,
      targetBorderRadius: target?.borderRadius ?? null,
    };
  }, selector);
}

try {
  await firstGoto('/dashboard', 'Dashboard');
  const dashboardBefore = await currentStyleSnapshot('h1');

  await spaGoto('/cases', 'Quản lý hồ sơ');
  const casesBefore = await currentStyleSnapshot('.ant-card');

  await spaGoto('/re', 'CenValue RE — Astryx integration spike');
  await page.locator('[data-re-astryx-spike="v1"]').waitFor({ state: 'visible', timeout: 15000 });
  assert.equal(await page.locator('[data-re-astryx-spike="v1"] input').count(), 2);

  await spaGoto('/dashboard', 'Dashboard');
  const dashboardAfter = await currentStyleSnapshot('h1');
  await spaGoto('/cases', 'Quản lý hồ sơ');
  const casesAfter = await currentStyleSnapshot('.ant-card');

  assert.deepEqual(dashboardAfter, dashboardBefore, 'Dashboard computed styles changed after client-side visit to /re');
  assert.deepEqual(casesAfter, casesBefore, 'Cases computed styles changed after client-side visit to /re');
  assert.deepEqual(pageErrors, [], 'Browser page errors: ' + pageErrors.join(' | '));
  assert.deepEqual(consoleErrors, [], 'Browser console errors: ' + consoleErrors.join(' | '));

  console.log('E0-PR-002 browser smoke PASSED');
  console.log('- unauthenticated /re redirected to /login');
  console.log('- guest /re redirected to /sobo');
  console.log('- /re rendered as mocked admin');
  console.log('- two Astryx TextInput controls rendered');
  console.log('- /dashboard computed styles unchanged after client-side /re visit');
  console.log('- /cases computed styles unchanged after client-side /re visit');
  console.log('- browser page errors: 0');
  console.log('- browser console errors: 0');
} catch (error) {
  await diagnostics('fatal');
  throw error;
} finally {
  await context.close();
  await browser.close();
}
