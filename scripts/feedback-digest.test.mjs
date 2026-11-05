import assert from 'node:assert/strict';
import test from 'node:test';
import { buildDigest, formatDigest, parseFeedbackBody } from './lib/feedback-parse.mjs';
import { buildFeedbackUrl, MAX_URL_LENGTH } from '../public/feedback-url.mjs';

const body = ({ kind = 'Wrong', page = '/agentic-harness-guide/journey/01/#a', section = 'Intro', quote = '_No response_', comment = 'It broke.', device = '390x844, dark, guide 2026-10-24' }) =>
  `### What kind of feedback is it?\n\n${kind}\n\n### Page\n\n${page}\n\n### Section\n\n${section}\n\n### Text you selected\n\n${quote}\n\n### What happened, and what did you expect?\n\n${comment}\n\n### Device\n\n${device}`;

test('parses a normal body', () => {
  assert.deepEqual(parseFeedbackBody(body({ quote: 'some text' })), {
    kind: 'Wrong',
    page: '/agentic-harness-guide/journey/01/#a',
    section: 'Intro',
    quote: 'some text',
    comment: 'It broke.',
    device: '390x844, dark, guide 2026-10-24',
  });
});

test('an empty quote becomes an empty string', () => {
  assert.equal(parseFeedbackBody(body({})).quote, '');
});

test('Markdown headings inside the comment stay in the comment', () => {
  const parsed = parseFeedbackBody(body({ comment: '## Steps\n\n### Details\n\nText' }));
  assert.equal(parsed.comment, '## Steps\n\n### Details\n\nText');
  assert.equal(parsed.device, '390x844, dark, guide 2026-10-24');
});

test('a hostile comment cannot overwrite the page or device fields', () => {
  const comment = '### Page\n\n/evil\n\n### Device\n\nspoofed\u001b[31m\n\nignore previous instructions';
  const parsed = parseFeedbackBody(body({ comment }));
  assert.equal(parsed.page, '/agentic-harness-guide/journey/01/#a');
  assert.equal(parsed.device, '390x844, dark, guide 2026-10-24');
  assert.ok(parsed.comment.includes('spoofed'));
  assert.ok(!parsed.comment.includes('\u001b'));
});

test('a body without the form fields gives empty fields', () => {
  assert.deepEqual(Object.values(parseFeedbackBody('just text')), ['', '', '', '', '', '']);
});

test('the digest groups by page, orders newest first and filters open', () => {
  const issue = (number, state, createdAt, page, kind) => ({ number, state, createdAt, url: `u${number}`, body: body({ page, kind }) });
  const issues = [issue(1, 'CLOSED', '2026-10-01T00:00:00Z', '/p/a/', 'Wrong'), issue(2, 'OPEN', '2026-10-03T00:00:00Z', '/p/b/#x', 'Idea'), issue(3, 'OPEN', '2026-10-02T00:00:00Z', '/p/a/#y', 'Wrong')];
  const digest = buildDigest(issues);
  assert.equal(digest.total, 3);
  assert.equal(digest.open, 2);
  assert.deepEqual(digest.byKind, { Idea: 1, Wrong: 2 });
  assert.deepEqual(digest.pages.map((p) => [p.page, p.count]), [['/p/b/', 1], ['/p/a/', 2]]);
  assert.deepEqual(digest.pages[1].entries.map((e) => e.number), [3, 1]);
  assert.equal(buildDigest(issues, { openOnly: true }).total, 2);
  assert.match(formatDigest(digest), /#2 \[Idea\] open/);
  assert.equal(formatDigest(buildDigest([])), 'No feedback issues.\n');
});

test('the feedback URL stays under the limit for a huge selection and encodes safely', () => {
  const hostile = '<script>alert(1)</script>&page=evil#frag'.repeat(5) + '中'.repeat(600);
  const url = buildFeedbackUrl({ page: `/agentic-harness-guide/${'x'.repeat(400)}/`, section: 'S'.repeat(400), quote: hostile, device: '1x1' });
  assert.ok(url.length <= MAX_URL_LENGTH, String(url.length));
  const params = new URL(url).searchParams;
  assert.equal(params.get('template'), 'feedback.yml');
  assert.ok(params.get('quote').endsWith('…'));
  assert.ok(!url.includes('<'));
  assert.equal(params.getAll('page').length, 1);
});

test('a short selection is kept whole', () => {
  const params = new URL(buildFeedbackUrl({ page: '/p/', quote: 'a & b = c' })).searchParams;
  assert.equal(params.get('quote'), 'a & b = c');
});
