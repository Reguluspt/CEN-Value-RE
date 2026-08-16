import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { assertReAstryxCssContained } from './scope-re-astryx-css.mjs';

const explicitPath = process.argv[2];
let cssPath = explicitPath;

if (!cssPath) {
  const assetsDir = path.join(process.cwd(), 'dist', 'assets');
  const matches = fs
    .readdirSync(assetsDir)
    .filter((name) => /^ReShell-.*\.css$/.test(name));

  if (matches.length !== 1) {
    console.error(`Expected exactly one built ReShell CSS asset, found ${matches.length}: ${matches.join(', ')}`);
    process.exit(1);
  }
  cssPath = path.join(assetsDir, matches[0]);
}

const css = fs.readFileSync(cssPath, 'utf8');

try {
  assertReAstryxCssContained(css, `Built RE CSS (${cssPath})`);
} catch (error) {
  console.error('E0-PR-002 built CSS verification FAILED');
  console.error(`- ${error.message}`);
  process.exit(1);
}

for (const requiredToken of ['--border-width', '--color-accent']) {
  if (!css.includes(requiredToken)) {
    console.error('E0-PR-002 built CSS verification FAILED');
    console.error(`- Built RE CSS is missing expected Astryx token ${requiredToken}`);
    process.exit(1);
  }
}

console.log('E0-PR-002 built CSS verification PASSED');
console.log(`- inspected ${cssPath}`);
console.log('- no :root/html[data-theme]/body global selectors remain in the RE CSS asset');
console.log('- Astryx token declarations remain present inside the scoped asset');
