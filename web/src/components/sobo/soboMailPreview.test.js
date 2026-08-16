import test from 'node:test';
import assert from 'node:assert/strict';
import { toMailPreviewText } from './soboMailPreview.js';


test('converts formatted email HTML to a compact plain-text preview', () => {
  const content = `
    <style>table { width: 1200px; }</style>
    <p>Kính gửi anh Trường,</p>
    <table><tr><td>Thửa 143</td><td>751.718.000&nbsp;đ</td></tr></table>
    <script>alert('ignored')</script>
  `;

  const preview = toMailPreviewText(content);

  assert.match(preview, /Kính gửi anh Trường,/);
  assert.match(preview, /Thửa 143 751\.718\.000 đ/);
  assert.doesNotMatch(preview, /width: 1200px|alert|<table>/);
});

test('keeps plain-text email content readable', () => {
  assert.equal(toMailPreviewText(' Dòng 1\nDòng 2 '), 'Dòng 1\nDòng 2');
});
