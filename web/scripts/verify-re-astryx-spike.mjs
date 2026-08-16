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
const failures = [];
const assert = (condition, message) => {
  if (!condition) failures.push(message);
};
const require = createRequire(import.meta.url);

const pkg = JSON.parse(read('package.json'));
const app = read('src/App.jsx');
const shell = read('src/re/ReShell.jsx');
const css = read('src/re/astryx.css');
const viteConfig = read('vite.config.js');

assert(pkg.dependencies['@astryxdesign/core'] === '0.2.0', 'Astryx core must be pinned to 0.2.0');
assert(pkg.dependencies['@astryxdesign/theme-neutral'] === '0.2.0', 'Neutral theme must be pinned to 0.2.0');
assert(pkg.dependencies['@stylexjs/stylex'] === '0.19.0', 'StyleX peer must be pinned to 0.19.0');
assert(app.includes("lazy(() => import('./re/ReShell'))"), '/re shell must be lazy-loaded');

const reRouteIndex = app.indexOf('path="/re"');
const reRouteBlock = reRouteIndex >= 0 ? app.slice(reRouteIndex, reRouteIndex + 600) : '';
assert(reRouteIndex >= 0, 'App router must expose /re');
assert(reRouteBlock.includes('<ProtectedRoute adminOnly={true}>'), '/re must remain behind existing admin protection');
assert(reRouteBlock.includes('<Suspense'), '/re must lazy-load behind Suspense');
assert(!reRouteBlock.includes('<Layout>'), '/re must not reuse legacy Ant Design Layout');

assert(shell.includes("from '@astryxdesign/core/AppShell'"), 'RE shell must use Astryx AppShell');
assert(shell.includes("from '@astryxdesign/core/SideNav'"), 'RE shell must use Astryx SideNav');
assert(shell.includes("from '@astryxdesign/core/FormLayout'"), 'RE shell must use Astryx FormLayout');
assert(shell.includes("from '@astryxdesign/core/TextInput'"), 'RE shell must use Astryx TextInput');
assert(!shell.includes("from '@astryxdesign/core/theme'"), 'RE shell must not mount Astryx root Theme because it mutates documentElement');
assert(!shell.includes("from '@astryxdesign/theme-neutral/built'"), 'RE shell must not use a root Theme provider');
assert(shell.includes('data-astryx-theme="neutral"'), 'Neutral theme name must be scoped on the RE surface');
assert(shell.includes('data-theme={themeMode}'), 'Light/dark theme mode must be scoped on the RE surface');

const importSources = [...shell.matchAll(/(?:from\s+|import\s+)['"]([^'"]+)['"]/g)].map((match) => match[1]);
const disallowedImports = importSources.filter((source) =>
  source !== 'react' &&
  source !== './astryx.css' &&
  !source.startsWith('@astryxdesign/')
);
assert(disallowedImports.length === 0, `RE shell has non-Astryx/application imports: ${disallowedImports.join(', ')}`);

assert(!css.includes("@import '@astryxdesign/core/reset.css'"), 'Global Astryx reset must not be imported in isolated spike');
assert(css.includes('.cenvalue-re-surface'), 'Compatibility reset must be scoped to .cenvalue-re-surface');
assert(!css.includes(':root'), 'Local RE CSS must not override global :root');
assert(!/^body\s*\{/m.test(css), 'Local RE CSS must not override global body');
assert(viteConfig.includes('reAstryxCssContainmentPlugin'), 'Vite must install the RE Astryx CSS containment transform');
assert(viteConfig.includes('scopeReAstryxVendorCss'), 'Vite must transform resolved Astryx vendor CSS before emission');

const vendorExports = [
  '@astryxdesign/core/astryx.css',
  '@astryxdesign/theme-neutral/theme.css',
];

for (const specifier of vendorExports) {
  const resolved = require.resolve(specifier);
  const raw = fs.readFileSync(resolved, 'utf8');
  assert(
    raw.includes(':root') || /html\s*\[data-theme=/.test(raw),
    `${specifier} negative-control source must expose the known global-selector mutation`,
  );
  try {
    const transformed = scopeReAstryxVendorCss(raw, resolved);
    assertReAstryxCssContained(transformed, specifier);
  } catch (error) {
    failures.push(`${specifier} containment transform failed: ${error.message}`);
  }
}

if (failures.length) {
  console.error('E0-PR-002 static verification FAILED');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('E0-PR-002 static verification PASSED');
console.log('- exact Astryx dependency pins present');
console.log('- /re route is protected, lazy-loaded, and outside legacy Layout');
console.log('- AppShell + SideNav + FormLayout + TextInput present');
console.log('- RE shell has no root Astryx Theme provider/documentElement sync path');
console.log('- resolved Astryx vendor CSS globals are rewritten to .cenvalue-re-surface');
console.log('- known raw vendor :root/html[data-theme] mutation is retained as a negative control and eliminated by the transform');
