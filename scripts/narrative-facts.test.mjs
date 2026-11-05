import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { spawnSync } from 'node:child_process';

const SCRIPT = path.resolve('scripts/narrative-facts.mjs');
const FIXTURES = path.resolve('scripts/fixtures/narrative');

const run = (root, ...extra) => {
  const result = spawnSync('node', [SCRIPT, '--root', root, '--config', path.join(FIXTURES, 'sidebar.txt'), ...extra], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  return { pages: result.stdout.split('\n').filter(Boolean).map((line) => JSON.parse(line)), stderr: result.stderr };
};

const bySlug = (pages) => Object.fromEntries(pages.map((p) => [p.slug, p]));

test('pages follow sidebar order and the rest follow path order', () => {
  const { pages } = run(FIXTURES);
  assert.deepEqual(pages.map((p) => [p.slug, p.order]), [['one/b', 1], ['one/a', 2], ['glossary', 3]]);
  assert.equal(pages[0].group, 'Start');
  assert.equal(pages[2].group, 'glossary');
});

test('code blocks are not counted as prose', () => {
  const a = bySlug(run(FIXTURES).pages)['one/a'];
  assert.equal(a.term_variants.actor.agent, 1);
  assert.equal(a.words, 28);
});

test('links in, links out and next resolve to slugs', () => {
  const pages = bySlug(run(FIXTURES).pages);
  assert.deepEqual(pages['one/a'].links_out, ['one/b']);
  assert.equal(pages['one/a'].next, 'one/b');
  assert.deepEqual(pages['one/b'].links_in, ['one/a']);
  assert.deepEqual(pages.glossary.links_in, []);
  assert.deepEqual(pages.glossary.links_out, []);
  assert.equal(pages['one/b'].next, null);
});

test('counts the voice, hedges, labels and phrases', () => {
  const pages = bySlug(run(FIXTURES).pages);
  assert.deepEqual(pages['one/a'].first_person, { I: 1, my: 0, we: 1, you: 1 });
  assert.equal(pages['one/a'].hedges.may, 1);
  assert.equal(pages['one/a'].hedges.usually, 1);
  assert.equal(pages['one/a'].principle_not_measured['Principle, not measured'], 1);
  assert.equal(pages['one/b'].principle_not_measured['My view, not measured'], 1);
  assert.equal(pages['one/b'].term_variants.helper['sub-agent'], 1);
  assert.equal(pages['one/b'].term_variants.actor.agent, 0);
  assert.deepEqual(pages['one/a'].example_labels, { Observed: 0, Computed: 0, Constructed: 0 });
});

test('glossary terms used use whole words and strip the bracketed note', () => {
  const pages = bySlug(run(FIXTURES).pages);
  assert.deepEqual(pages['one/a'].glossary_terms_used, ['Agent', 'Hook']);
  assert.deepEqual(pages['one/b'].glossary_terms_used, []);
  assert.deepEqual(pages.glossary.glossary_terms_used, []);
});

test('dirty is null without --previous and marks exactly one changed page with it', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'narrative-'));
  const previous = path.join(dir, 'old.jsonl');
  const first = run(FIXTURES, '--out', previous);
  assert.ok(first.stderr.includes('3 pages'));
  assert.ok(first.stderr.includes('dirty: n/a'));
  const copy = path.join(dir, 'docs');
  fs.cpSync(FIXTURES, copy, { recursive: true });
  fs.appendFileSync(path.join(copy, 'one/b.md'), '\nA new line.\n');
  const { pages, stderr } = run(copy, '--previous', previous);
  assert.deepEqual(pages.filter((p) => p.dirty).map((p) => p.slug), ['one/b']);
  assert.ok(stderr.includes('dirty: 1'));
  fs.rmSync(dir, { recursive: true });
});
