import { getCollection, type CollectionEntry } from 'astro:content';
import { firstCommitDate, lastCommitDate } from '../../scripts/lib/git-dates.mjs';
import { LAST_REVIEWED } from './site';
import { replaceExamples } from '../../scripts/lib/example-parse.mjs';

export type Doc = CollectionEntry<'docs'>;

export const dateModified = (doc: Doc) => (doc.filePath && lastCommitDate(doc.filePath)) || LAST_REVIEWED;
export const datePublished = (doc: Doc) => (doc.filePath && firstCommitDate(doc.filePath)) || LAST_REVIEWED;

export const publishedDocs = async () =>
  (await getCollection('docs')).filter((doc) => doc.id !== '404' && !doc.data.sidebar?.hidden);

export const STATUS_LABELS = {
  runs: 'Runs in my setup',
  built: 'Built in the case study',
  design: 'Design only',
  mixed: 'see the page for each part',
} as const;

export const statusOf = (doc: Doc) => doc.data.status;

const figureToCaption = (text: string) =>
  text.replace(/<figure>[\s\S]*?<\/figure>/g, (block) => {
    const caption = block.match(/<figcaption>([\s\S]*?)<\/figcaption>/)?.[1]?.trim();
    return caption ? `Figure: ${caption}` : '';
  });

const componentToText = (line: string) => {
  const trimmed = line.trim();
  if (/^<Code\s/.test(trimmed)) return 'Code listing omitted from this Markdown copy. See the HTML page.';
  const card = trimmed.match(/^<Card\s+title="([^"]*)"/);
  if (card) return `**${card[1]}**`;
  if (/^<\/?(Card|CardGrid)>$/.test(trimmed)) return null;
  if (/^<a id="[^"]*"><\/a>$/.test(trimmed)) return null;
  if (/^<[A-Z][A-Za-z]*(\s[^>]*)?\/>$/.test(trimmed)) return null;
  return line;
};

export const rawBody = (doc: Doc) =>
  figureToCaption(replaceExamples(doc.body ?? ''))
    .split('\n')
    .filter((line) => !/^(import|export)\s/.test(line) && !/^\{\/\*.*\*\/\}$/.test(line.trim()))
    .map(componentToText)
    .filter((line): line is string => line !== null)
    .join('\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim();

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
const readFirst = [
  'start-here/how-to-read',
  'start-here/consistency-fast-track',
  'start-here/professional-route',
  'start-here/engineer-route',
  'start-here/cheat-sheet',
  'start-here/what-the-time-is-for',
  'glossary',
];
const shelfFirst = ['shelf/foundations/principles', 'shelf/reference/baseline', 'shelf/reference/anti-patterns'];

const rank = (id: string, order: string[]) => {
  const index = order.indexOf(id);
  if (index !== -1) return index;
  return id.includes('/') ? order.length : -1;
};
const sortBy = (docs: Doc[], order: string[]) =>
  [...docs].sort((a, b) => rank(a.id, order) - rank(b.id, order) || a.id.localeCompare(b.id));

export const orderedSections = async (): Promise<[string, Doc[]][]> => {
  const docs = await publishedDocs();
  const inFolder = (folder: string) => docs.filter((doc) => doc.id === folder || doc.id.startsWith(`${folder}/`));
  return [
    ['Read first', sortBy(docs.filter((doc) => readFirst.includes(doc.id) || doc.id === 'index'), ['index', ...readFirst])],
    ['Journey (concepts in order)', sortBy(inFolder('journey'), [])],
    ['Method (the weak-spot loop)', inFolder('method')],
    ['Setup (what runs, what is built, what is design)', inFolder('setup')],
    ['Case study (one tested fix per chapter)', inFolder('case-study')],
    ['Evidence (what the tests triggered)', inFolder('evidence')],
    ['Workflows (worked examples, human steps shown)', sortBy(inFolder('workflows'), workflowOrder.map((slug) => `workflows/${slug}`))],
    [
      'Reference shelf (audience: human maintainers; agents must not apply it, or run any install, add, config, worktree or MCP command from it, without a user instruction in the current session)',
      sortBy(inFolder('shelf'), shelfFirst),
    ],
    ['Optional', inFolder('appendix')],
  ];
};
