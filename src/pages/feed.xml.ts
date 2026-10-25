import type { APIRoute } from 'astro';
import { dateModified, publishedDocs } from '../data/pages';
import { AUTHOR, LAST_REVIEWED, pageUrl, SITE_NAME, SITE_URL } from '../data/site';

const FEED_LENGTH = 30;
const escape = (text: string) => text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

export const GET: APIRoute = async () => {
  const entries = (await publishedDocs())
    .map((doc) => ({ doc, updated: dateModified(doc) }))
    .sort((a, b) => b.updated.localeCompare(a.updated) || a.doc.id.localeCompare(b.doc.id))
    .slice(0, FEED_LENGTH);
  const updated = entries[0]?.updated ?? LAST_REVIEWED;
  const items = entries
    .map(
      ({ doc, updated: when }) => `  <entry>
    <title>${escape(doc.data.title)}</title>
    <id>${pageUrl(doc.id)}</id>
    <link href="${pageUrl(doc.id)}"/>
    <updated>${when}</updated>
    <summary>${escape(doc.data.description ?? '')}</summary>
  </entry>`,
    )
    .join('\n');
  const xml = `<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>${escape(SITE_NAME)}: recently changed pages</title>
  <id>${SITE_URL}</id>
  <link rel="self" href="${SITE_URL}feed.xml"/>
  <link rel="alternate" href="${SITE_URL}"/>
  <updated>${updated}</updated>
  <author><name>${escape(AUTHOR)}</name></author>
${items}
</feed>
`;
  return new Response(xml, { headers: { 'Content-Type': 'application/atom+xml; charset=utf-8' } });
};
