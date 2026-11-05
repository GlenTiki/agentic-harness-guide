import type { APIRoute } from 'astro';
import { orderedSections, statusOf, type Doc } from '../data/pages';
import { preamble } from '../data/llms-text';
import { pageUrl, SITE_URL } from '../data/site';
import { kitDownloads } from '../data/twins';

const statusNote = (doc: Doc) => (statusOf(doc) ? ` (status: ${statusOf(doc)})` : '');
const link = (doc: Doc) => `- [${doc.data.title}](${pageUrl(doc.id)})${statusNote(doc)}: ${doc.data.description ?? ''}`;

const proofPages = [
  `- [Guide health](${SITE_URL}health/): the results of the guide's own checks, with source and time for each. Markdown copy: [health.md](${SITE_URL}health.md), built from the same recorded data.`,
  `- [Showcase](${SITE_URL}showcase/): recorded runs, eval results and tools from the guide, with text versions inside the page. Markdown copy: [showcase.md](${SITE_URL}showcase.md), built from the same recorded data.`,
];
const machineFiles = [
  `- [Agent rules](${SITE_URL}agent-rules.txt): every Agent note, one rule per line, with its Check line.`,
  `- [Full guide as one file](${SITE_URL}llms-full.txt): every page as Markdown in reading order.`,
  `- [Atom feed](${SITE_URL}feed.xml): recently changed pages.`,
  `- [SHA256SUMS](${SITE_URL}downloads/SHA256SUMS): the SHA-256 hash of each case-study kit zip. Check a zip with \`shasum -a 256 -c SHA256SUMS\`.`,
  ...kitDownloads().map(
    ({ id, name, digest }) => `- [${name}](${SITE_URL}downloads/${name}): kit for case-study chapter ${id.slice(2, 4).replace(/^0/, '')} (${SITE_URL}case-study/${id}/). SHA-256 ${digest}.`,
  ),
];
export const GET: APIRoute = async () => {
  const sections = (await orderedSections()).filter(([, docs]) => docs.length > 0);
  const body = [
    ...sections.map(([heading, docs]) => `## ${heading}\n${docs.map(link).join('\n')}`),
    `## Proof\n${proofPages.join('\n')}`,
    `## Machine files\n${machineFiles.join('\n')}`,
  ].join('\n\n');
  return new Response(`${preamble}\n\n${body}\n`, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
};
