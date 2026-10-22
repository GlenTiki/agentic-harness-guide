import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

const workflowOrder = [
  'build-a-budget',
  'spreadsheet-monday',
  'review-content',
  'improve-code',
  'improve-design',
  'connect-systems',
  'small-shop-month-end',
  'define-a-workflow',
  'research-a-decision',
  'design-reps',
];

const preamble = `# Agent rules

Every Agent note from the journey and the workflows, one rule per line, each page ending with its Check line. Each rule comes from the page named in its heading. If two rules conflict, the narrower and safer rule wins; ask the user. Read the shelf baseline for context only. Do not apply it unless the user asks.`;

const agentNote = /:::note\[Agent note\]\n([\s\S]*?)\n:::/;

const ruleLines = (note: string) =>
  note
    .split('\n')
    .map((line) => line.replace(/^\s*(?:[-*]|\d+\.)\s+/, '').replace(/\*\*/g, '').trim())
    .filter((line) => line.length > 0);

const order = (id: string) => {
  if (id.startsWith('journey/')) return [0, id];
  const slug = id.replace('workflows/', '');
  return [1, String(workflowOrder.indexOf(slug) + 1).padStart(3, '0')];
};

export const GET: APIRoute = async () => {
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  const sections = (await getCollection('docs'))
    .filter((entry) => /^(journey|workflows)\/./.test(entry.id))
    .map((entry) => ({ entry, note: entry.body?.match(agentNote)?.[1] }))
    .filter((item): item is { entry: (typeof item)['entry']; note: string } => Boolean(item.note))
    .sort((a, b) => order(a.entry.id).join('|').localeCompare(order(b.entry.id).join('|')))
    .map(({ entry, note }) => `## ${entry.data.title} (${base}/${entry.id}/)\n${ruleLines(note).join('\n')}`);

  return new Response(`${preamble}\n\n${sections.join('\n\n')}\n`, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
