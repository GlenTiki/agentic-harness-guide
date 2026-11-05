import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawnSync } from 'node:child_process';

const root = path.resolve(import.meta.dirname, '..');
const archive = 'field-notes/index.html';
const note = 'field-notes/why-this-guide-exists/index.html';
const guide = 'journey/00-hello-robot/index.html';

test('SEO checks require each route type and retain Guide sitemap date checks', () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'field-notes-seo-'));
  try {
    for (const file of ['index.html', archive, note, guide, 'og.png', 'feed.xml', 'sitemap-0.xml']) {
      const target = path.join(directory, file);
      fs.mkdirSync(path.dirname(target), { recursive: true });
      fs.copyFileSync(path.join(root, 'dist', file), target);
    }
    const check = () => spawnSync(process.execPath, ['scripts/check-seo.mjs', directory], { cwd: root, encoding: 'utf8' });
    const baseline = check();
    assert.equal(baseline.status, 0, baseline.stdout + baseline.stderr);
    const cases = [
      [note, '"@type":"BlogPosting"', '"@type":"TechArticle"', /Field note has no BlogPosting/],
      [guide, '"@type":"TechArticle"', '"@type":"BlogPosting"', /no TechArticle/],
      [archive, '"@type":"CollectionPage"', '"@type":"WebSite"', /archive has no CollectionPage/],
      [guide, /"datePublished":"[^"]+"/, '"datePublished":"2026-11-05"', /datePublished is not UTC seconds/],
      ['sitemap-0.xml', /<lastmod>[^<]+<\/lastmod>/, '', /a URL has no lastmod/],
    ];
    for (const [file, original, replacement, expected] of cases) {
      const target = path.join(directory, file);
      const content = fs.readFileSync(target, 'utf8');
      const changed = content.replace(original, replacement);
      assert.notEqual(changed, content, `fixture replacement in ${file}`);
      fs.writeFileSync(target, changed);
      const result = check();
      assert.equal(result.status, 1, result.stdout + result.stderr);
      assert.match(result.stdout, expected);
      fs.writeFileSync(target, content);
    }
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});
