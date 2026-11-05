export const isUtcSecond = (value) => typeof value === 'string' && /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(value) && Number.isFinite(Date.parse(value)) && new Date(value).toISOString() === value.replace('Z', '.000Z');

export const buildClock = (override, clock = () => new Date()) => {
  const now = override ?? clock().toISOString().replace(/\.\d{3}Z$/, 'Z');
  if (!isUtcSecond(now)) throw new Error('Build clock must be a valid UTC timestamp with seconds and Z');
  return now;
};

export const validateNoteDates = (data, now) => {
  if (!isUtcSecond(data.publishedAt)) throw new Error('publishedAt must be a valid UTC timestamp with seconds and Z');
  if (data.updatedAt === undefined) return;
  if (!isUtcSecond(data.updatedAt)) throw new Error('updatedAt must be a valid UTC timestamp with seconds and Z');
  if (data.updatedAt < data.publishedAt) throw new Error('updatedAt must not precede publishedAt');
  if (data.updatedAt > now) throw new Error('updatedAt must not be in the future');
};

export const notesSchema = (z, now) => z.object({
  title: z.string().trim().min(1),
  description: z.string().trim().min(1).max(160),
  publishedAt: z.string(),
  updatedAt: z.string().optional(),
  draft: z.boolean().default(true),
}).strict().superRefine((data, context) => {
  try { validateNoteDates(data, now); }
  catch (error) { context.addIssue({ code: 'custom', message: error.message }); }
});

export const publishedNotes = (notes, now) => {
  buildClock(now);
  for (const note of notes) validateNoteDates(note.data, now);
  return notes.filter(note => note.data.draft === false && note.data.publishedAt <= now)
    .sort((a, b) => b.data.publishedAt.localeCompare(a.data.publishedAt) || a.id.localeCompare(b.id));
};

export const notesUrl = (site, id = '') => new URL(`field-notes/${id ? `${id}/` : ''}`, site.url).href;
export const noteModified = (note) => note.data.updatedAt ?? note.data.publishedAt;
const xmlEscape = (text) => text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');

export const notesFeed = (notes, now, site) => {
  const visible = publishedNotes(notes, now);
  const updated = visible.map(noteModified).sort().at(-1) ?? now;
  const items = visible.map(note => `  <entry>
    <title>${xmlEscape(note.data.title)}</title>
    <id>${xmlEscape(notesUrl(site, note.id))}</id>
    <link href="${xmlEscape(notesUrl(site, note.id))}"/>
    <published>${note.data.publishedAt}</published>
    <updated>${noteModified(note)}</updated>
    <summary>${xmlEscape(note.data.description)}</summary>
  </entry>`).join('\n');
  return `<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>${xmlEscape(site.name)}: Field notes</title>
  <id>${xmlEscape(notesUrl(site))}</id>
  <link rel="self" href="${xmlEscape(new URL('feed.xml', notesUrl(site)).href)}"/>
  <link rel="alternate" href="${xmlEscape(notesUrl(site))}"/>
  <updated>${updated}</updated>
  <author><name>${xmlEscape(site.author)}</name></author>
${items}
</feed>
`;
};

export const noteMarkdown = (note, site) => `---
title: ${JSON.stringify(note.data.title)}
description: ${JSON.stringify(note.data.description)}
author: ${JSON.stringify(site.author)}
url: ${notesUrl(site, note.id)}
publishedAt: ${note.data.publishedAt}
${note.data.updatedAt ? `updatedAt: ${note.data.updatedAt}\n` : ''}---

${note.body ?? ''}
`;

export const notesMarkdown = (notes, now, site) => {
  const visible = publishedNotes(notes, now);
  return `---\ntitle: "Field notes"\ndescription: "Notes on judgement, experiments and corrections as the guide develops."\nurl: ${notesUrl(site)}\n---\n\n# Field notes\n\nNotes on judgement, experiments and corrections as the guide develops.\n\n[Atom feed](${notesUrl(site)}feed.xml)\n\n${visible.map(note => `- [${note.data.title.replace(/[\[\]\\]/g, '\\$&')}](${notesUrl(site, note.id)}) (${note.data.publishedAt})\n  ${note.data.description}`).join('\n') || 'No notes published yet.'}\n`;
};

export const notesJsonLd = (note, site) => {
  const url = notesUrl(site, note?.id);
  const main = note ? {
    '@type': 'BlogPosting', headline: note.data.title, description: note.data.description,
    datePublished: note.data.publishedAt, dateModified: noteModified(note),
    author: { '@type': 'Person', name: site.author, url: site.authorUrl },
    image: site.image, mainEntityOfPage: url,
  } : { '@type': 'CollectionPage', name: 'Field notes', description: 'Notes on judgement, experiments and corrections as the guide develops.' };
  const trail = [{ name: 'Home', item: site.url }, { name: 'Field notes', item: notesUrl(site) }];
  if (note) trail.push({ name: note.data.title, item: url });
  return JSON.stringify({ '@context': 'https://schema.org', '@graph': [
    { ...main, url, inLanguage: 'en', isPartOf: { '@id': `${site.url}#website` } },
    { '@type': 'BreadcrumbList', itemListElement: trail.map((item, index) => ({ '@type': 'ListItem', position: index + 1, ...item })) },
  ] }).replace(/</g, '\\u003c');
};
