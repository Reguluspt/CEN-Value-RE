import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { createRequire } from 'node:module';
import {
  assertReAstryxCssContained,
  scopeReAstryxVendorCss,
} from './scope-re-astryx-css.mjs';

const webRoot = process.cwd();
const read = (relative) => fs.readFileSync(path.join(webRoot, relative), 'utf8');
const stripCssComments = (source) => source.replace(/\/\*[\s\S]*?\*\//g, '');
const failures = [];
const assert = (condition, message) => {
  if (!condition) failures.push(message);
};
const require = createRequire(import.meta.url);

const pkg = JSON.parse(read('package.json'));
const app = read('src/App.jsx');
const shell = read('src/re/ReShell.jsx');
const localServiceClient = read('src/re/localServiceClient.js');
const percentBoundary = read('src/re/percent.js');
const workbenchApi = read('src/re/workbenchApi.js');
const css = read('src/re/astryx.css');
const cssRulesOnly = stripCssComments(css);
const generatedCore = read('src/re/generated/astryx-core.scoped.css');
const generatedTheme = read('src/re/generated/neutral-theme.scoped.css');
const generator = read('scripts/generate-re-astryx-css.mjs');

assert(pkg.dependencies['@astryxdesign/core'] === '0.2.0', 'Astryx core must be pinned to 0.2.0');
assert(pkg.dependencies['@astryxdesign/theme-neutral'] === '0.2.0', 'Neutral theme must be pinned to 0.2.0');
assert(pkg.dependencies['@stylexjs/stylex'] === '0.19.0', 'StyleX peer must be pinned to 0.19.0');
assert(pkg.scripts.dev.includes('prepare:re-astryx-css'), 'dev must generate scoped Astryx CSS before Vite');
assert(pkg.scripts.build.includes('prepare:re-astryx-css'), 'build must generate scoped Astryx CSS before Vite');
assert(pkg.scripts['verify:re-astryx'].includes('prepare:re-astryx-css'), 'static verification must regenerate scoped Astryx CSS');
assert(app.includes("lazy(() => import('./re/ReShell'))"), '/re shell must be lazy-loaded');

const reRouteIndex = app.indexOf('path="/re"');
const reRouteBlock = reRouteIndex >= 0 ? app.slice(reRouteIndex, reRouteIndex + 600) : '';
assert(reRouteIndex >= 0, 'App router must expose /re');
assert(reRouteBlock.includes('<ProtectedRoute adminOnly={true}>'), '/re must remain behind existing admin protection');
assert(reRouteBlock.includes('<Suspense'), '/re must lazy-load behind Suspense');
assert(!reRouteBlock.includes('<Layout>'), '/re must not reuse legacy Ant Design Layout');

assert(shell.includes("from '@astryxdesign/core/AppShell'"), 'RE workbench must use Astryx AppShell');
assert(shell.includes("from '@astryxdesign/core/SideNav'"), 'RE workbench must use Astryx SideNav');
assert(shell.includes("from '@astryxdesign/core/Text'"), 'RE workbench must use Astryx Text');
assert(shell.includes('data-re-workbench="e1-pr-006"'), 'RE workbench must expose the E1-PR-006 marker');
assert(!shell.includes("from '@astryxdesign/core/theme'"), 'RE shell must not mount Astryx root Theme because it mutates documentElement');
assert(!shell.includes("from '@astryxdesign/theme-neutral/built'"), 'RE shell must not use a root Theme provider');
assert(shell.includes("import './generated/astryx-core.scoped.css'"), 'RE shell must import generated scoped Astryx core CSS');
assert(shell.includes("import './generated/neutral-theme.scoped.css'"), 'RE shell must import generated scoped Neutral theme CSS');
assert(shell.includes('data-astryx-theme="neutral"'), 'Neutral theme name must be scoped on the RE surface');
assert(shell.includes('data-theme={themeMode}'), 'Light/dark theme mode must be scoped on the RE surface');

const importSources = [...shell.matchAll(/(?:from\s+|import\s+)['"]([^'"]+)['"]/g)].map((match) => match[1]);
const allowedLocalImports = new Set([
  './astryx.css',
  './generated/astryx-core.scoped.css',
  './generated/neutral-theme.scoped.css',
  './localServiceClient',
  './percent',
  './workbenchApi',
]);
const disallowedImports = importSources.filter((source) =>
  source !== 'react' &&
  !allowedLocalImports.has(source) &&
  !source.startsWith('@astryxdesign/')
);
assert(disallowedImports.length === 0, `RE shell has disallowed infrastructure imports: ${disallowedImports.join(', ')}`);
assert(!shell.includes('src/re/adapters'), 'Frontend must not import Python adapters');
assert(!shell.includes('persistence'), 'Frontend must not import persistence internals');
assert(!shell.includes('openpyxl'), 'Frontend must not import workbook runtime internals');

assert(localServiceClient.includes("let bootstrapEnvelope = null"), 'Local-service bootstrap must be in-memory module state');
assert(!localServiceClient.includes('localStorage'), 'Bearer bootstrap must not use localStorage');
assert(!localServiceClient.includes('sessionStorage'), 'Bearer bootstrap must not use sessionStorage');
assert(!localServiceClient.includes('document.cookie'), 'Bearer bootstrap must not use cookies');
assert(localServiceClient.includes("path.startsWith('/api/re/')"), 'API client must constrain requests to /api/re');
assert(localServiceClient.includes('Authorization: `Bearer ${bootstrapEnvelope.bearerToken}`'), 'API client must attach the launch bearer token in memory');
assert(localServiceClient.includes('[LAUNCH_ID_HEADER]: bootstrapEnvelope.launchId'), 'API client must attach the current launch ID');

assert(!percentBoundary.includes('parseFloat'), 'Percentage boundary must not use parseFloat');
assert(!percentBoundary.includes('parseInt'), 'Percentage boundary must not use parseInt');
assert(!percentBoundary.includes('Number('), 'Percentage boundary must not convert canonical percentages through Number');
assert(!percentBoundary.includes('Math.'), 'Percentage boundary must not calculate percentages through binary Math helpers');
assert(percentBoundary.includes('shiftDecimal(value, -2)'), 'Display percent must convert to canonical fraction by exact decimal shift');
assert(percentBoundary.includes('shiftDecimal(String(value), 2)'), 'Canonical fraction must convert to display percent by exact decimal shift');

assert(workbenchApi.includes("import { reRequest } from './localServiceClient'"), 'Workbench API must use the bounded local-service client');
assert(!workbenchApi.includes('axios'), 'Workbench API must not create a second HTTP stack');
assert(!workbenchApi.includes('fetch('), 'Workbench API must not bypass the credentialed local-service client');

assert(!cssRulesOnly.includes('@import'), 'Local RE CSS must not import vendor/global styles directly');
assert(cssRulesOnly.includes('.cenvalue-re-surface'), 'Compatibility reset must be scoped to .cenvalue-re-surface');
assert(!cssRulesOnly.includes(':root'), 'Local RE CSS must not override global :root');
assert(!/html\s*\[data-theme=/m.test(cssRulesOnly), 'Local RE CSS must not target global html[data-theme]');
assert(!/(^|[{}])\s*body(?:\s|[.#:\[\]>+~])*\{/m.test(cssRulesOnly), 'Local RE CSS must not override global body');
assert(generator.includes("'@astryxdesign/core/astryx.css'"), 'Generator must resolve Astryx core CSS from the pinned package');
assert(generator.includes("'@astryxdesign/theme-neutral/theme.css'"), 'Generator must resolve Neutral theme CSS from the pinned package');

const vendorExports = [
  {
    specifier: '@astryxdesign/core/astryx.css',
    generated: generatedCore,
  },
  {
    specifier: '@astryxdesign/theme-neutral/theme.css',
    generated: generatedTheme,
  },
];

for (const entry of vendorExports) {
  const resolved = require.resolve(entry.specifier);
  const raw = fs.readFileSync(resolved, 'utf8');
  assert(
    raw.includes(':root') || /html\s*\[data-theme=/.test(raw),
    `${entry.specifier} negative-control source must expose the known global-selector mutation`,
  );
  try {
    const transformed = scopeReAstryxVendorCss(raw, resolved);
    assertReAstryxCssContained(transformed, entry.specifier);
    assertReAstryxCssContained(entry.generated, `generated ${entry.specifier}`);
    assert(
      entry.generated.includes(transformed),
      `Generated ${entry.specifier} must contain the exact deterministic scoped vendor output`,
    );
  } catch (error) {
    failures.push(`${entry.specifier} containment verification failed: ${error.message}`);
  }
}

if (failures.length) {
  console.error('E1-PR-006 Astryx/workbench verification FAILED');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('E1-PR-006 Astryx/workbench verification PASSED');
console.log('- accepted Astryx pins and /re isolation remain intact');
console.log('- /re remains admin-protected, lazy-loaded, and outside legacy Layout');
console.log('- manual workbench uses the bounded credentialed /api/re client');
console.log('- local-service bootstrap remains in memory only');
console.log('- percentage conversion avoids binary floating-point helpers');
console.log('- local RE CSS contains no vendor import or global :root/html[data-theme]/body rule');
console.log('- generated vendor CSS remains deterministically scoped to .cenvalue-re-surface');
