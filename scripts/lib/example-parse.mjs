export const LABELS = ['Observed', 'Computed', 'Constructed'];
export const SLOTS = ['input', 'output', 'notice', 'shows'];
export const REPO_BLOB = 'https://github.com/GlenTiki/agentic-harness-guide/blob/main/';

const OPEN = /<Example((?:\s+[A-Za-z]+="[^"]*")*)\s*>/g;
const SLOT = /<Fragment\s+slot="([a-z]+)"\s*>([\s\S]*?)<\/Fragment>/g;
const ATTR = /([A-Za-z]+)="([^"]*)"/g;

export const findExamples = (source) =>
  [...source.matchAll(OPEN)].map((open) => {
    const bodyStart = open.index + open[0].length;
    const close = source.indexOf('</Example>', bodyStart);
    const body = close === -1 ? source.slice(bodyStart) : source.slice(bodyStart, close);
    const attrs = Object.fromEntries([...open[1].matchAll(ATTR)].map((m) => [m[1], m[2]]));
    const slots = Object.fromEntries([...body.matchAll(SLOT)].map((m) => [m[1], m[2].trim()]));
    const end = close === -1 ? source.length : close + '</Example>'.length;
    return { start: open.index, end, line: source.slice(0, open.index).split('\n').length, attrs, slots, closed: close !== -1 };
  });

const evidenceItems = (evidence) => (evidence ?? '').split(/\s+/).filter(Boolean);

export const evidenceHref = (item) => (/^https?:\/\//.test(item) ? item : `${REPO_BLOB}${item}`);

export const exampleToMarkdown = ({ attrs, slots }) => {
  const evidence = attrs.label === 'Observed' ? evidenceItems(attrs.evidence).map(evidenceHref).join(' ') : attrs.evidence;
  const meta = [attrs.env && `Environment: ${attrs.env}`, evidence && `Evidence: ${evidence}`].filter(Boolean).join('. ');
  return [
    `**Example (${attrs.label}).**`,
    `**Task.** ${attrs.task}`,
    `**Input**\n\n${slots.input}`,
    `**Output**\n\n${slots.output}`,
    `**What to notice.** ${slots.notice}`,
    `**What it shows.** ${slots.shows}`,
    meta && `*${meta}.*`,
  ]
    .filter(Boolean)
    .join('\n\n');
};

export const replaceExamples = (source) =>
  findExamples(source)
    .reverse()
    .reduce((text, example) => `${text.slice(0, example.start)}${exampleToMarkdown(example)}${text.slice(example.end)}`, source);

export const TWIN_PARTS = ['**Task.**', '**Input**', '**Output**', '**What to notice.**', '**What it shows.**'];
