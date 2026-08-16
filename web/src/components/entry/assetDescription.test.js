import test from 'node:test';
import assert from 'node:assert/strict';
import { normalizeShortAssetDescription } from './assetDescription.js';

test('expands a shortened land asset description', () => {
  assert.equal(
    normalizeShortAssetDescription('43,12, Tổ 2 An Tân, phường An Khê, tỉnh Gia Lai'),
    'Thửa đất số 43, tờ bản đồ số 12; tại địa chỉ Tổ 2 An Tân, phường An Khê, tỉnh Gia Lai',
  );
});

test('expands every shortened asset on separate lines', () => {
  assert.equal(
    normalizeShortAssetDescription([
      '43,12, Tổ 2 An Tân, phường An Khê, tỉnh Gia Lai',
      '89,26, Tổ 5, phường Phù Đổng, tỉnh Gia Lai',
    ].join('\n')),
    [
      'Thửa đất số 43, tờ bản đồ số 12; tại địa chỉ Tổ 2 An Tân, phường An Khê, tỉnh Gia Lai',
      'Thửa đất số 89, tờ bản đồ số 26; tại địa chỉ Tổ 5, phường Phù Đổng, tỉnh Gia Lai',
    ].join('\n'),
  );
});

test('keeps full descriptions and free text unchanged', () => {
  const value = [
    'Thửa đất số 43, tờ bản đồ số 12; tại địa chỉ Tổ 2 An Tân',
    'Nhà xưởng, máy móc thiết bị tại Gia Lai',
  ].join('\n');

  assert.equal(normalizeShortAssetDescription(value), value);
});
