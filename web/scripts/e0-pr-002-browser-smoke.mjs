import { chromium } from 'playwright';
import assert from 'node:assert/strict';

const baseURL = process.env.E0_PR_002_BASE_URL || 'http://127.0.0.1:5173';
const injectRootLeak = process.env.E0_PR_002_INJECT_ROOT_LEAK === '1';
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

async function rootAndLegacySnapshot(page, selector) {
  return page.evaluate((sel) => {
    const root = document.documentElement;
    const rootStyle = getComputedStyle(root);
    const bodyStyle = getComputedStyle(document.body);
    const target = document.querySelector(sel);
    const targetStyle = target ? getComputedStyle(target) : null;
    const customProperties = {};

    for (let index = 0; index < rootStyle.length; index += 1) {
      const property = rootStyle.item(index);
      if (property.startsWith('--')) {
        customProperties[property] = rootStyle.getPropertyValue(property).trim();
      }
    }

    return {
      rootAttributes: {
        dataTheme: root.getAttribute('data-theme'),
        dataAstryxTheme: root.getAttribute('data-astryx-theme'),
      },
      rootCustomProperties: Object.fromEntries(
        Object.entries(customProperties).sort(([a], [b]) => a.localeCompare(b)),
      ),
      rootComputed: {
        colorScheme: rootStyle.colorScheme,
        fontFamily: rootStyle.fontFamily,
        fontSize: rootStyle.fontSize,
      },
      bodyComputed: {
        fontFamily: bodyStyle.fontFamily,
        fontSize: bodyStyle.fontSize,
        margin: bodyStyle.margin,
        background: bodyStyle.backgroundColor,
      },
      targetComputed: {
        fontFamily: targetStyle?.fontFamily ?? null,
        fontSize: targetStyle?.fontSize ?? null,
        color: targetStyle?.color ?? null,
        borderRadius: targetStyle?.borderRadius ?? null,
        background: targetStyle?.backgroundColor ?? null,
      },
    };
  }, selector);
}

async function runAdminIsolationScenario(themeMode) {
  const admin = await createTestPage({ id: 1, username: 'admin', role: 'admin' });
  const { context, page, pageErrors, consoleErrors } = admin;

  async function diagnostics(label) {
    const bodyText = await page.locator('body').innerText().catch(() => '<body unavailable>');
    console.error(`DIAGNOSTIC ${themeMode}:${label}`);
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

  try {
    await firstGoto('/dashboard', 'Dashboard');
    await page.evaluate((mode) => {
      document.documentElement.setAttribute('data-theme', mode);
    }, themeMode);
    await page.waitForTimeout(50);

    const dashboardBefore = await rootAndLegacySnapshot(page, 'h1');

    await spaGoto('/cases', 'Quản lý hồ sơ');
    const casesBefore = await rootAndLegacySnapshot(page, '.ant-card');

    const baselinePageErrors = new Set(pageErrors);
    const baselineConsoleErrors = new Set(consoleErrors);

    if (injectRootLeak) {
      await page.addStyleTag({
        content: ':root { --border-width: 999px; --color-accent: rgb(1, 2, 3); }',
      });
    }

    await spaGoto('/re', 'CenValue RE — Astryx integration spike');
    const reSurface = page.locator('[data-re-astryx-spike="v1"]');
    await reSurface.waitFor({ state: 'visible', timeout: 15000 });
    assert.equal(await reSurface.locator('input').count(), 2);
    assert.equal(await reSurface.getAttribute('data-theme'), themeMode, `RE surface must keep ${themeMode} theme local`);
    assert.equal(await reSurface.getAttribute('data-astryx-theme'), 'neutral');

    await spaGoto('/dashboard', 'Dashboard');
    const dashboardAfter = await rootAndLegacySnapshot(page, 'h1');
    await spaGoto('/cases', 'Quản lý hồ sơ');
    const casesAfter = await rootAndLegacySnapshot(page, '.ant-card');

    const newPageErrors = [...new Set(pageErrors)].filter(message => !baselinePageErrors.has(message));
    const newConsoleErrors = [...new Set(consoleErrors)].filter(message => !baselineConsoleErrors.has(message));

    assert.deepEqual(
      dashboardAfter,
      dashboardBefore,
      `${themeMode}: document root/body/dashboard styles or custom properties changed after client-side /re visit`,
    );
    assert.deepEqual(
      casesAfter,
      casesBefore,
      `${themeMode}: document root/body/cases styles or custom properties changed after client-side /re visit`,
    );
    assert.deepEqual(newPageErrors, [], `${themeMode}: new browser page errors after /re: ${newPageErrors.join(' | ')}`);
    assert.deepEqual(newConsoleErrors, [], `${themeMode}: new browser console errors after /re: ${newConsoleErrors.join(' | ')}`);

    return baselineConsoleErrors.size;
  } catch (error) {
    await diagnostics('fatal');
    throw error;
  } finally {
    await context.close();
  }
}

try {
  await assertRedirectForUser(null, '/login', 'Unauthenticated user');
  await assertRedirectForUser(
    { id: 2, username: 'guest', role: 'guest' },
    '/sobo',
    'Guest user'
  );

  const lightConsoleBaseline = await runAdminIsolationScenario('light');
  const darkConsoleBaseline = await runAdminIsolationScenario('dark');

  console.log('E0-PR-002 browser smoke PASSED');
  console.log('- unauthenticated /re redirected to /login');
  console.log('- guest /re redirected to /sobo');
  console.log('- /re rendered as mocked admin in light and dark environments');
  console.log('- two Astryx TextInput controls rendered in both environments');
  console.log('- documentElement attributes and every computed root custom property unchanged after client-side /re visit');
  console.log('- /dashboard and /cases representative computed styles unchanged in light and dark environments');
  console.log(`- legacy console error baselines: light=${lightConsoleBaseline}, dark=${darkConsoleBaseline} unique message(s)`);
  console.log('- new browser page errors after /re: 0');
  console.log('- new browser console errors after /re: 0');
} finally {
  await browser.close();
}
