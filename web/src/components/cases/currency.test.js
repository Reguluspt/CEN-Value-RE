import test from 'node:test';
import assert from 'node:assert/strict';
import { formatCurrency, formatMillions } from './currency.js';

test('formats VND amounts without a suffix', () => {
  assert.equal(formatCurrency(1470000000), '1.470.000.000');
  assert.equal(formatCurrency('937000000'), '937.000.000');
  assert.equal(formatCurrency(0), '0');
});

test('keeps the Tr suffix for summary amounts', () => {
  assert.equal(formatMillions(1470000000), '1.470 Tr');
  assert.equal(formatMillions('937000000'), '937 Tr');
});
