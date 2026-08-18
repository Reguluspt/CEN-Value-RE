import assert from 'node:assert/strict';

import {
  clearReBootstrap,
  installReBootstrap,
  ReLocalServiceError,
  reRequest,
} from '../src/re/localServiceClient.js';
import {
  displayPercentToFraction,
  fractionToDisplayPercent,
} from '../src/re/percent.js';

assert.equal(displayPercentToFraction(''), null);
assert.equal(displayPercentToFraction('0'), '0');
assert.equal(displayPercentToFraction('5'), '0.05');
assert.equal(displayPercentToFraction('-5'), '-0.05');
assert.equal(displayPercentToFraction('0.5'), '0.005');
assert.equal(displayPercentToFraction('12.3400'), '0.1234');
assert.equal(fractionToDisplayPercent(null), '');
assert.equal(fractionToDisplayPercent('0'), '0');
assert.equal(fractionToDisplayPercent('0.05'), '5');
assert.equal(fractionToDisplayPercent('-0.05'), '-5');
assert.equal(fractionToDisplayPercent('0.005'), '0.5');
assert.throws(() => displayPercentToFraction('5e-2'), /plain finite decimal/);
assert.throws(() => displayPercentToFraction('NaN'), /plain finite decimal/);

clearReBootstrap();
await assert.rejects(
  () => reRequest('/api/re/health/live'),
  (error) => error instanceof ReLocalServiceError && error.code === 'RE_BOOTSTRAP_REQUIRED',
);

assert.throws(
  () =>
    installReBootstrap({
      base_url: 'http://0.0.0.0:9999',
      launch_id: 'launch',
      bearer_token: 'secret',
    }),
  /loopback/,
);
assert.throws(
  () =>
    installReBootstrap({
      base_url: 'https://127.0.0.1:9999',
      launch_id: 'launch',
      bearer_token: 'secret',
    }),
  /loopback/,
);

installReBootstrap({
  base_url: 'http://127.0.0.1:43123',
  launch_id: 'launch-1',
  bearer_token: 'secret-1',
});

const calls = [];
globalThis.fetch = async (url, options) => {
  calls.push({ url, options });
  return {
    ok: true,
    status: 200,
    async json() {
      return { status: 'ok' };
    },
  };
};

const response = await reRequest('/api/re/health/live');
assert.deepEqual(response, { status: 'ok' });
assert.equal(calls.length, 1);
assert.equal(calls[0].url, 'http://127.0.0.1:43123/api/re/health/live');
assert.equal(calls[0].options.headers['X-CenValue-RE-Launch-ID'], 'launch-1');
assert.equal(calls[0].options.headers.Authorization, 'Bearer secret-1');
await assert.rejects(() => reRequest('/outside/re'), /inside \/api\/re/);

clearReBootstrap();
console.log('E1-PR-006 workbench boundary verification PASSED');
console.log('- explicit zero remains distinct from missing percentage input');
console.log('- display percentage conversion uses exact decimal strings');
console.log('- absent bootstrap fails closed');
console.log('- non-loopback/HTTPS bootstrap is rejected');
console.log('- current launch ID and bearer are attached in-memory to /api/re requests');
