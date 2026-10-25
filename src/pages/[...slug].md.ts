import type { APIRoute, GetStaticPaths } from 'astro';
import { dateModified, publishedDocs, rawBody, statusOf, type Doc } from '../data/pages';
import { pageUrl } from '../data/site';

const statusLine = (doc: Doc) => (statusOf(doc) ? `status: ${statusOf(doc)}\n` : '');

const markdownTwin = (doc: Doc) =>
  `---\ntitle: ${JSON.stringify(doc.data.title)}\ndescription: ${JSON.stringify(doc.data.description ?? '')}\nurl: ${pageUrl(doc.id)}\n${statusLine(doc)}last_modified: ${dateModified(doc)}\n---\n\n${rawBody(doc)}\n`;

export const getStaticPaths: GetStaticPaths = async () =>
  (await publishedDocs()).map((doc) => ({ params: { slug: doc.id }, props: { doc } }));

export const GET: APIRoute = ({ props }) =>
  new Response(markdownTwin(props.doc as Doc), { headers: { 'Content-Type': 'text/markdown; charset=utf-8' } });
