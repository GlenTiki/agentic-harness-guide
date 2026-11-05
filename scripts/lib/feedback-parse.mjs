const LABELS = {
  kind: 'What kind of feedback is it?',
  page: 'Page',
  section: 'Section',
  quote: 'Text you selected',
  comment: 'What happened, and what did you expect?',
  device: 'Device',
};
const ORDER = ['kind', 'page', 'section', 'quote', 'comment', 'device'];
const NO_RESPONSE = '_No response_';
const CONTROL_CHARACTERS = /[\u0000-\u0008\u000b-\u001f\u007f-\u009f‪-‮⁦-⁩]/g;

export const stripControl = (text) => String(text ?? '').replace(CONTROL_CHARACTERS, '');

const headingPattern = (field) => new RegExp(`^### ${LABELS[field].replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[ \\t]*$`, 'gm');

const positions = (body, field) => [...body.matchAll(headingPattern(field))].map((m) => ({ start: m.index, end: m.index + m[0].length }));

export const parseFeedbackBody = (body) => {
  const text = String(body ?? '').replace(/\r\n/g, '\n');
  const found = {};
  let cursor = 0;
  for (const field of ORDER) {
    const all = positions(text, field).filter((p) => p.start >= cursor);
    const hit = field === 'device' ? all.at(-1) : all[0];
    if (!hit) continue;
    found[field] = hit;
    cursor = hit.end;
  }
  const present = ORDER.filter((field) => found[field]);
  const fields = Object.fromEntries(ORDER.map((field) => [field, '']));
  present.forEach((field, i) => {
    const next = found[present[i + 1]];
    const value = text.slice(found[field].end, next ? next.start : text.length).trim();
    fields[field] = value === NO_RESPONSE ? '' : stripControl(value);
  });
  return fields;
};

const pagePath = (page) => page.split('#')[0] || '(no page)';

export const toEntry = (issue) => ({
  number: issue.number,
  state: String(issue.state ?? '').toLowerCase(),
  createdAt: issue.createdAt,
  url: issue.url,
  ...parseFeedbackBody(issue.body),
});

export const buildDigest = (issues, { openOnly = false } = {}) => {
  const entries = issues
    .map(toEntry)
    .filter((entry) => !openOnly || entry.state === 'open')
    .sort((a, b) => String(b.createdAt).localeCompare(String(a.createdAt)));
  const byPage = new Map();
  for (const entry of entries) {
    const key = pagePath(entry.page);
    byPage.set(key, [...(byPage.get(key) ?? []), entry]);
  }
  const countBy = (list, pick) => list.reduce((acc, e) => ({ ...acc, [pick(e) || '(none)']: (acc[pick(e) || '(none)'] ?? 0) + 1 }), {});
  return {
    total: entries.length,
    open: entries.filter((e) => e.state === 'open').length,
    byKind: countBy(entries, (e) => e.kind),
    pages: [...byPage].map(([page, items]) => ({ page, count: items.length, byKind: countBy(items, (e) => e.kind), entries: items })),
  };
};

const shorten = (text, limit) => {
  const flat = text.replace(/\s+/g, ' ');
  return flat.length > limit ? `${flat.slice(0, limit - 1)}…` : flat;
};
const kinds = (counts) => Object.entries(counts).map(([kind, n]) => `${kind} ${n}`).join(', ');

export const formatDigest = (digest) => {
  if (digest.total === 0) return 'No feedback issues.\n';
  const lines = [`Feedback issues: ${digest.total} (${digest.open} open). ${kinds(digest.byKind)}.`];
  for (const page of digest.pages) {
    lines.push('', `${page.page} (${page.count}: ${kinds(page.byKind)})`);
    for (const e of page.entries) {
      lines.push(`  #${e.number} [${e.kind || 'no kind'}] ${e.state} ${e.createdAt}`);
      if (e.section) lines.push(`    section: ${shorten(e.section, 150)}`);
      if (e.quote) lines.push(`    quote: ${shorten(e.quote, 300)}`);
      lines.push(`    comment: ${shorten(e.comment, 600) || '(empty)'}`);
      if (e.device) lines.push(`    device: ${shorten(e.device, 120)}`);
      lines.push(`    ${e.url}`);
    }
  }
  return `${lines.join('\n')}\n`;
};
