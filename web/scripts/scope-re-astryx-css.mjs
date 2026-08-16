const RE_SCOPE = '.cenvalue-re-surface';
const CORE_SUFFIX = '/@astryxdesign/core/dist/astryx.css';
const THEME_SUFFIX = '/@astryxdesign/theme-neutral/dist/theme.css';

const normalizeId = (id) => id.split('?')[0].replaceAll('\\', '/');
const stripCssComments = (css) => css.replace(/\/\*[\s\S]*?\*\//g, '');

export function isReAstryxVendorCss(id) {
  const normalized = normalizeId(id);
  return normalized.endsWith(CORE_SUFFIX) || normalized.endsWith(THEME_SUFFIX);
}

function assertNoForbiddenGlobalSelectors(css, label) {
  const rulesOnly = stripCssComments(css);
  const failures = [];
  if (rulesOnly.includes(':root')) failures.push(':root');
  if (/html\s*\[data-theme=(?:"|')(?:light|dark)(?:"|')\]/.test(rulesOnly)) {
    failures.push('html[data-theme]');
  }
  if (/(^|[{}])\s*body(?:\s|[.#:\[\]>+~])*\{/m.test(rulesOnly)) failures.push('body');
  if (failures.length) {
    throw new Error(`${label} still contains forbidden global selector(s): ${failures.join(', ')}`);
  }
}

export function scopeReAstryxVendorCss(css, id) {
  const normalized = normalizeId(id);

  if (normalized.endsWith(CORE_SUFFIX)) {
    let rootPairCount = 0;
    const transformed = css.replace(
      /:root\s*,\s*(\.[A-Za-z0-9_-]+)/g,
      (_match, classSelector) => {
        rootPairCount += 1;
        return `${RE_SCOPE}, ${RE_SCOPE} ${classSelector}`;
      },
    );

    if (rootPairCount !== 13) {
      throw new Error(
        `Astryx core CSS global-selector contract drift: expected 13 :root/class token rules, found ${rootPairCount}`,
      );
    }
    assertNoForbiddenGlobalSelectors(transformed, 'Astryx core CSS');
    return transformed;
  }

  if (normalized.endsWith(THEME_SUFFIX)) {
    let rootCount = 0;
    let htmlThemeCount = 0;

    let transformed = css.replace(/:root(?=\s*\{)/g, () => {
      rootCount += 1;
      return RE_SCOPE;
    });
    transformed = transformed.replace(
      /html(\s*\[data-theme=(?:"|')(?:light|dark)(?:"|')\])(?=\s*\{)/g,
      (_match, themeAttribute) => {
        htmlThemeCount += 1;
        return `${RE_SCOPE}${themeAttribute}`;
      },
    );

    if (rootCount !== 1 || htmlThemeCount !== 2) {
      throw new Error(
        `Astryx Neutral theme CSS global-selector contract drift: expected 1 :root and 2 html[data-theme] rules, found ${rootCount} and ${htmlThemeCount}`,
      );
    }
    assertNoForbiddenGlobalSelectors(transformed, 'Astryx Neutral theme CSS');
    return transformed;
  }

  return css;
}

export function assertReAstryxCssContained(css, label = 'Astryx CSS') {
  assertNoForbiddenGlobalSelectors(css, label);
  if (!stripCssComments(css).includes(RE_SCOPE)) {
    throw new Error(`${label} does not contain the required ${RE_SCOPE} containment selector`);
  }
}

export { RE_SCOPE };
