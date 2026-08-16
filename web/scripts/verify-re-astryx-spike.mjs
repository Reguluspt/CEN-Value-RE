import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const webRoot = process.cwd();
const read = (relative) => fs.readFileSync(path.join(webRoot, relative), 'utf8');
const failures = [];
const assert = (condition, message) => {
  if (!condition) failures.push(message);
};

const pkg = JSON.parse(read('package.json'));
const app = read('src/App.jsx');
const shell = read('src/re/ReShell.jsx');
const css = read('src/re/astryx.css');

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
assert(shell.includes("from '@astryxdesign/core/theme'"), 'RE shell must use Astryx Theme provider');
assert(shell.includes("from '@astryxdesign/theme-neutral/built'"), 'RE shell must use prebuilt Neutral theme');

const importSources = [...shell.matchAll(/(?:from\s+|import\s+)['"]([^'"]+)['"]/g)].map((match) => match[1]);
const disallowedImports = importSources.filter((source) =>
  source !== 'react' &&
  source !== './astryx.css' &&
  !source.startsWith('@astryxdesign/')
);
assert(disallowedImports.length === 0, `RE shell has non-Astryx/application imports: ${disallowedImports.join(', ')}`);

assert(!css.includes("@import '@astryxdesign/core/reset.css'"), 'Global Astryx reset must not be imported in isolated spike');
assert(css.includes('.cenvalue-re-surface'), 'Compatibility reset must be scoped to .cenvalue-re-surface');
assert(!css.includes(':root'), 'RE CSS must not override global :root');
assert(!/^body\s*\{/m.test(css), 'RE CSS must not override global body');

if (failures.length) {
  console.error('E0-PR-002 static verification FAILED');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('E0-PR-002 static verification PASSED');
console.log('- exact Astryx dependency pins present');
console.log('- /re route is protected, lazy-loaded, and outside legacy Layout');
console.log('- AppShell + SideNav + FormLayout + TextInput present');
console.log('- RE shell imports only React, Astryx, and its scoped stylesheet');
console.log('- global Astryx reset/:root/body overrides excluded');
