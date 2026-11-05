import test from 'node:test';
import assert from 'node:assert/strict';
import { z } from 'astro/zod';
import { notesSchema, publishedNotes, notesFeed, noteMarkdown, notesMarkdown, notesJsonLd, buildClock } from './lib/notes.mjs';

const now = '2026-11-05T00:00:00Z';
const site = { url: 'https://example.org/nested/base/', name: 'Judgement First', author: 'Glen Keane', authorUrl: 'https://example.org/', image: 'https://example.org/nested/base/og.png' };
const note = (id, data = {}) => ({ id, body: 'A useful note.', data: { title: id, description: 'A short description.', publishedAt: '2026-11-01T00:00:00Z', draft: false, ...data } });

test('clock samples once and accepts a fixed instant', () => {
  let calls = 0;
  assert.equal(buildClock(undefined, () => { calls++; return new Date(now); }), now);
  assert.equal(calls, 1);
  assert.equal(buildClock(now, () => { throw Error('must not sample'); }), now);
  assert.throws(() => buildClock('2026-02-30T00:00:00Z'), /UTC/);
});

test('schema defaults to draft and rejects impossible or non-UTC-second dates', () => {
  const schema = notesSchema(z, now);
  const { draft, ...data } = note('a').data;
  assert.equal(schema.parse(data).draft, true);
  for (const publishedAt of ['2026-02-30T00:00:00Z', '2026-11-01', '2026-11-01T00:00:00+00:00', '2026-11-01T00:00:00.000Z']) {
    assert.equal(schema.safeParse({ ...data, publishedAt }).success, false, publishedAt);
  }
  assert.equal(schema.safeParse({ ...data, updatedAt: '2026-10-30T00:00:00Z' }).success, false);
  assert.equal(schema.safeParse({ ...data, updatedAt: '2026-11-06T00:00:00Z' }).success, false);
  assert.equal(schema.safeParse({ ...data, publishedAt: '2026-12-01T00:00:00Z' }).success, true);
});

test('publication is opt-in, includes boundary and sorts by publication then stable id', () => {
  const input = [note('z'), note('a'), note('old', { publishedAt: '2026-10-01T00:00:00Z', updatedAt: now }), note('future', { publishedAt: '2026-11-05T00:00:01Z' }), note('draft', { draft: true }), note('boundary', { publishedAt: now })];
  const missing = note('missing'); delete missing.data.draft; input.push(missing);
  assert.deepEqual(publishedNotes(input, now).map(n => n.id), ['boundary', 'a', 'z', 'old']);
  assert.equal(input[0].id, 'z');
  assert.throws(() => publishedNotes([note('bad', { updatedAt: '2026-11-06T00:00:00Z' })], now), /updatedAt/);
});

test('feed is valid when empty, escapes content, keeps absolute IDs and separates dates', () => {
  assert.match(notesFeed([], now, site), new RegExp(`<updated>${now}</updated>`));
  const initial = note('a', { title: 'A & <B> "C"' });
  const edited = note('a', { ...initial.data, updatedAt: now });
  const feed = notesFeed([edited], now, site);
  assert.match(feed, /<title>A &amp; &lt;B&gt; &quot;C&quot;<\/title>/);
  assert.match(feed, /<id>https:\/\/example.org\/nested\/base\/field-notes\/a\/<\/id>/);
  assert.match(feed, /<published>2026-11-01T00:00:00Z<\/published>/);
  assert.match(feed, new RegExp(`<updated>${now}</updated>`));
  assert.deepEqual([...notesFeed([initial], now, site).matchAll(/<id>(.*?)<\/id>/g)].map(x=>x[1]), [...feed.matchAll(/<id>(.*?)<\/id>/g)].map(x=>x[1]));
});

test('all public lists omit drafts and future notes and markdown keeps author and dates', () => {
  const input = [note('visible'), note('draft-canary', { draft: true }), note('future-canary', { publishedAt: '2026-12-01T00:00:00Z' })];
  for (const output of [notesFeed(input, now, site), notesMarkdown(input, now, site)]) {
    assert.match(output, /visible/);
    assert.doesNotMatch(output, /draft-canary|future-canary/);
  }
  const md = noteMarkdown(input[0], site);
  assert.match(md, /author: "Glen Keane"/);
  assert.match(md, /publishedAt: 2026-11-01T00:00:00Z/);
  assert.match(md, /https:\/\/example.org\/nested\/base\/field-notes\/visible\//);
});

test('note schema uses BlogPosting, preserves dates, escapes scripts, archive uses CollectionPage', () => {
  const data = notesJsonLd(note('a', { title: '</script>' }), site);
  assert.doesNotMatch(data, /<\/script>/);
  const graph = JSON.parse(data)['@graph'];
  assert.equal(graph[0]['@type'], 'BlogPosting');
  assert.equal(graph[0].datePublished, graph[0].dateModified);
  assert.equal(graph[1].itemListElement[1].item, 'https://example.org/nested/base/field-notes/');
  assert.equal(JSON.parse(notesJsonLd(null, site))['@graph'][0]['@type'], 'CollectionPage');
});
