import assert from 'node:assert/strict';
import { test } from 'node:test';
import { supportUrl } from './lib/support-url.mjs';

test('support stays absent until a public account URL is supplied', () => {
  assert.equal(supportUrl(undefined), null);
  assert.equal(supportUrl(''), null);
});

test('support accepts an HTTPS Ko-fi profile', () => {
  assert.equal(supportUrl('https://ko-fi.com/example'), 'https://ko-fi.com/example');
});

test('support refuses unsafe or misleading destinations', () => {
  for (const value of ['http://ko-fi.com/example', 'https://ko-fi.com.evil.test/example', 'https://evil.test/ko-fi.com', 'https://user@ko-fi.com/example', 'javascript:alert(1)', 'https://ko-fi.com/', 'not a URL']) {
    assert.throws(() => supportUrl(value));
  }
});
