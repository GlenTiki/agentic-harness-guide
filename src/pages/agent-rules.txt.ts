import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';
import { pageUrl } from '../data/site';

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
  'build-a-kitchen-assistant',
];

const writeScope =
  'Ask before you do something that changes anything outside your own working files: sending, paying, deleting, posting, granting access, pushing, installing, or editing a file the user did not ask you to change. Record the yes as the user\'s chat message or a ledger line.';
const questionBudget =
  'Ask once per task, in one message, with every open item and your default for each (at most five items). If nobody can answer, state your assumptions and carry on with read-only work. For any action that changes something, stop and report, and take no action.';
const budgetPointer = 'Every question in this section counts against the question budget at the top of this file.';

const preamble = `# Agent rules

Every Agent note from the journey, the workflows, the appendix, the setup overview, the case study overview and the evidence page, one rule per line, each page ending with its Check line. Each rule comes from the page named in its heading. If two rules conflict, follow the rule that does less. Read the shelf baseline for context only. Do not apply it, and do not run any install, add, config, worktree or MCP command from the shelf, unless the user asks for it in the current session.

Scope of "changes something": ${writeScope}

Question budget: ${questionBudget}`;

const agentNote = /:::note\[Agent note\]\n([\s\S]*?)\n:::/;

const ruleLines = (note: string) =>
  note
    .split('\n')
    .map((line) => line.replace(/^\s*(?:[-*]|\d+\.)\s+/, '').replace(/\*\*/g, '').trim())
    .filter((line) => line.length > 0);

const order = (id: string) => {
  if (id === 'setup') return [3, '1'];
  if (id === 'case-study') return [3, '2'];
  if (id === 'evidence') return [3, '3'];
  if (id.startsWith('journey/')) return [0, id];
  if (id.startsWith('appendix/')) return [2, id];
  const slug = id.replace('workflows/', '');
  return [1, String(workflowOrder.indexOf(slug) + 1).padStart(3, '0')];
};

export const GET: APIRoute = async () => {
  const sections = (await getCollection('docs'))
    .filter((entry) => /^(journey\/.|workflows\/.|appendix\/.|setup$|case-study$|evidence$)/.test(entry.id))
    .map((entry) => ({ entry, note: entry.body?.match(agentNote)?.[1] }))
    .filter((item): item is { entry: (typeof item)['entry']; note: string } => Boolean(item.note))
    .sort((a, b) => order(a.entry.id).join('|').localeCompare(order(b.entry.id).join('|')))
    .map(({ entry, note }) => {
      const lines = ruleLines(note).map((line) =>
        line
          .replace(writeScope, 'Apply the scope of "changes something" defined at the top of this file.')
          .replace(questionBudget, 'Apply the question budget at the top of this file.'),
      );
      if (lines.some((line) => /\bask\b/i.test(line))) lines.push(budgetPointer);
      return `## ${entry.data.title} (${pageUrl(entry.id)})\n${lines.join('\n')}`;
    });

  return new Response(`${preamble}\n\n${sections.join('\n\n')}\n`, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
