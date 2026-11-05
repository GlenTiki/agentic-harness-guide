import type { APIRoute } from 'astro';
import { orderedSections, rawBody, STATUS_LABELS, statusOf, type Doc } from '../data/pages';
import { preamble } from '../data/llms-text';
import { pageUrl } from '../data/site';

const statusBlock = (doc: Doc) => {
  const status = statusOf(doc);
  return status ? `Status: ${status} (${STATUS_LABELS[status]})\n\n` : '';
};

export const GET: APIRoute = async () => {
  const parts = (await orderedSections()).flatMap(([, docs]) =>
    docs.map((doc) => `<!-- page: ${pageUrl(doc.id)} -->\n\n# ${doc.data.title}\n\n> ${doc.data.description ?? ''}\n\n${statusBlock(doc)}${rawBody(doc)}`),
  );
  return new Response(`${preamble}\n\n${parts.join('\n\n---\n\n')}\n`, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
