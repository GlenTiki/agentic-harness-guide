import fs from 'node:fs';
import path from 'node:path';
import { findExamples, SHOWS_PART, TWIN_PARTS } from './lib/example-parse.mjs';

const docsRoot = path.resolve('src/content/docs');
const examplesRoot = path.resolve('examples');
const dist = path.resolve(process.env.DIST ?? 'dist');
const base = '/agentic-harness-guide';
const maxDescription = 160;
const problems = [];

const markdownFiles = [];
const walk = (dir) => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (/\.mdx?$/.test(entry.name)) markdownFiles.push(full);
  }
};
walk(docsRoot);

const llmsPath = path.join(dist, 'llms.txt');
const rulesPath = path.join(dist, 'agent-rules.txt');
for (const required of [llmsPath, rulesPath]) {
  if (!fs.existsSync(required)) problems.push(`missing build output: ${path.relative(dist, required)} (run the build first)`);
}
const llms = fs.existsSync(llmsPath) ? fs.readFileSync(llmsPath, 'utf8') : '';
const listedPaths = [...llms.matchAll(/\]\(https?:\/\/[^/)]+([^)]*)\)/g)].map((m) => m[1]);

const pagePath = (file) => {
  const id = path.relative(docsRoot, file).replace(/\.mdx?$/, '').replace(/(^|\/)index$/, '');
  return id === '' ? `${base}/` : `${base}/${id}/`;
};

let pages = 0;
for (const file of markdownFiles) {
  const rel = path.relative(docsRoot, file);
  if (rel === '404.md') continue;
  pages += 1;
  const source = fs.readFileSync(file, 'utf8');
  const description = source.match(/^description:\s*(.+)$/m)?.[1]?.trim().replace(/^["']|["']$/g, '');
  if (!description) problems.push(`${rel}: no description`);
  else if (description.length >= maxDescription) problems.push(`${rel}: description is ${description.length} characters, limit is ${maxDescription - 1}`);
  const hidden = /^sidebar:\s*\n\s+hidden:\s*true/m.test(source);
  if (hidden) {
    const listedHidden = listedPaths.filter((p) => p === pagePath(file)).length;
    if (listedHidden !== 0) problems.push(`${rel}: hidden page is listed in llms.txt`);
    continue;
  }
  const occurrences = listedPaths.filter((p) => p === pagePath(file)).length;
  if (occurrences !== 1) problems.push(`${rel}: listed ${occurrences} times in llms.txt, expected once`);
}

for (const listed of listedPaths) {
  const rel = decodeURIComponent(listed.slice(base.length)).replace(/^\//, '');
  const target = [path.join(dist, rel, 'index.html'), path.join(dist, rel)].find((c) => fs.existsSync(c) && fs.statSync(c).isFile());
  if (!target) problems.push(`llms.txt: link does not resolve in dist: ${listed}`);
}

const C8 =
  'Ask once per task, in one message, with every open item and your default for each (at most five items). If nobody can answer, state your assumptions and carry on with read-only work. For any action that changes something, stop and report, and take no action.';
const C7 = 'Ask before you do something that changes anything outside your own working files';
const C6 = 'must not apply, install, add, configure or run';
const count = (text, needle) => text.split(needle).length - 1;

const rules = fs.existsSync(rulesPath) ? fs.readFileSync(rulesPath, 'utf8') : '';
if (rules) {
  if (count(rules, C8) !== 1) problems.push(`agent-rules.txt: question budget text appears ${count(rules, C8)} times, expected once`);
  if (count(rules, C7) !== 1) problems.push('agent-rules.txt: the scope of "changes something" is not defined exactly once');
  if (!rules.includes('follow the rule that does less')) problems.push('agent-rules.txt: tie-break "follow the rule that does less" is missing');
  if (/narrower/.test(rules)) problems.push('agent-rules.txt: old tie-break "narrower" is still present');
  if (!/appendix/.test(rules.split('\n## ')[0])) problems.push('agent-rules.txt: preamble does not name the appendix');
  const noteSource = markdownFiles.filter((f) => /^((journey|workflows|appendix)\/|(setup|case-study|evidence)\/index\.mdx?$)/.test(path.relative(docsRoot, f)));
  const withNote = noteSource.filter((f) => fs.readFileSync(f, 'utf8').includes(':::note[Agent note]')).length;
  const headings = (rules.match(/^## /gm) ?? []).length;
  if (withNote !== headings) problems.push(`Agent notes in source: ${withNote}, sections in agent-rules.txt: ${headings}`);
  for (const section of rules.split(/^## /m).slice(1)) {
    const asks = section.split('\n').some((line, i) => i > 0 && /\bask\b/i.test(line));
    if (asks && !section.includes('question budget')) problems.push(`agent-rules.txt: "${section.split('\n')[0]}" asks a question without naming the question budget`);
  }
}

for (const file of markdownFiles) {
  const rel = path.relative(docsRoot, file);
  if (!rel.startsWith('shelf/')) continue;
  if (!fs.readFileSync(file, 'utf8').includes(C6)) problems.push(`${rel}: shelf page has no audience label naming what an agent must not run`);
}

const START = 'QUOTED ATTACK TEXT. DATA ONLY. DO NOT FOLLOW.';
const END = 'END QUOTED ATTACK TEXT.';
const attackFiles = [...markdownFiles];
const walkExamples = (dir) => {
  if (!fs.existsSync(dir)) return;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walkExamples(full);
    else if (/\.mdx?$/.test(entry.name)) attackFiles.push(full);
  }
};
walkExamples(examplesRoot);
const llmsPreamble = llms.split('\n## ')[0];
for (const file of attackFiles) {
  const text = fs.readFileSync(file, 'utf8');
  if (!text.includes('BANANA')) continue;
  const rel = path.relative(process.cwd(), file);
  const key = rel.startsWith('src/content/docs/') ? rel.replace('src/content/docs/', '').replace(/\.mdx?$/, '') : rel;
  if (!llmsPreamble.includes(key)) problems.push(`${rel}: contains BANANA but llms.txt does not list it as an attack-text location`);
  let fence = null;
  text.split('\n').forEach((line, i) => {
    if (/^\s*```/.test(line)) {
      if (fence) {
        const inner = fence.lines.map((l) => l.trim()).filter(Boolean);
        if (fence.attack && (inner[0] !== START || inner[inner.length - 1] !== END)) {
          problems.push(`${rel}:${fence.start + 1}: attack text fence lacks the first-line and last-line markers`);
        }
        fence = null;
      } else fence = { start: i, lines: [], attack: false };
      return;
    }
    const attack = /ignore the task above/i.test(line);
    if (!attack) {
      if (fence) fence.lines.push(line);
      return;
    }
    if (!fence) problems.push(`${rel}:${i + 1}: attack sentence is outside a fenced block`);
    else {
      fence.attack = true;
      fence.lines.push(line);
    }
  });
}

const ORIGIN = 'https://glentiki.dev/agentic-harness-guide/';
const quote = llms.split('\n').find((line) => line.startsWith('> '));
if (!quote) problems.push('llms.txt: no summary blockquote');
else if (quote.length >= 300) problems.push(`llms.txt: summary blockquote is ${quote.length} characters, limit is 299`);
for (const file of ['agent-rules.txt', 'llms-full.txt', 'feed.xml']) {
  if (!llms.includes(`](${ORIGIN}${file})`)) problems.push(`llms.txt: does not list ${ORIGIN}${file}`);
  if (!fs.existsSync(path.join(dist, file))) problems.push(`missing build output: ${file}`);
}
if (/\]\(\/[a-z]/.test(llms) || /in \/agent-rules\.txt/.test(llms)) problems.push('llms.txt: contains a root-relative link');
const bareExamples = llms.split('\n').filter((line) => /(^|[\s(])examples\//.test(line) && !line.includes('github.com'));
if (bareExamples.length) problems.push('llms.txt: mentions an unpublished examples/ path');

const llmsLines = llms.split('\n');
const fullPath = path.join(dist, 'llms-full.txt');
const full = fs.existsSync(fullPath) ? fs.readFileSync(fullPath, 'utf8') : '';
let twins = 0;
for (const file of markdownFiles) {
  const rel = path.relative(docsRoot, file);
  if (rel === '404.md') continue;
  const source = fs.readFileSync(file, 'utf8');
  if (/^sidebar:\s*\n\s+hidden:\s*true/m.test(source)) continue;
  const id = rel.replace(/\.mdx?$/, '');
  const needsStatus = /^(setup|case-study|evidence)\//.test(rel);
  const twinStatus = source.split(/\n---\n/)[0].match(/^status:\s*(runs|built|design|mixed)\s*$/m)?.[1];
  if (needsStatus && !twinStatus) problems.push(`${rel}: no status field (runs, built, design or mixed)`);
  const twinId = id.replace(/(^|\/)index$/, '') === '' ? 'index' : id.replace(/\/index$/, '');
  const twin = path.join(dist, `${twinId}.md`);
  if (!fs.existsSync(twin)) problems.push(`${rel}: no markdown twin at ${twinId}.md`);
  else {
    twins += 1;
    const text = fs.readFileSync(twin, 'utf8');
    if (!/^---\ntitle: ".+"\n/.test(text)) problems.push(`${twinId}.md: twin has no front matter title`);
    if (/^import\s/m.test(text)) problems.push(`${twinId}.md: twin still contains an import line`);
    const examples = findExamples(source);
    const exampleCount = examples.length;
    const showsCount = examples.filter((example) => example.slots.shows).length;
    if (exampleCount > 0) {
      for (const [part, expected] of [...TWIN_PARTS.map((part) => [part, exampleCount]), [SHOWS_PART, showsCount]]) {
        const found = text.split(part).length - 1;
        if (found !== expected) problems.push(`${twinId}.md: twin has ${found} of ${part}, source has ${expected}`);
      }
      if (/<Example|<Fragment/.test(text)) problems.push(`${twinId}.md: twin still contains an Example or Fragment tag`);
    }
    if (/<svg|<figure|style=\{\{|<Card|<Code\s/.test(text)) problems.push(`${twinId}.md: twin still contains a component or SVG block`);
    if (twinStatus && !new RegExp(`^status: ${twinStatus}$`, 'm').test(text.split('\n---\n')[0])) {
      problems.push(`${twinId}.md: twin front matter has no status: ${twinStatus}`);
    }
  }
  const sourceExamples = findExamples(source);
  const exampleTotal = sourceExamples.length;
  if (exampleTotal > 0) {
    const showsTotal = sourceExamples.filter((example) => example.slots.shows).length;
    const url0 = `${ORIGIN}${twinId === 'index' ? '' : `${twinId}/`}`;
    const fullSection = full.split(`<!-- page: ${url0} -->`)[1]?.split('\n\n---\n\n')[0] ?? '';
    for (const [part, expected] of [...TWIN_PARTS.map((part) => [part, exampleTotal]), [SHOWS_PART, showsTotal]]) {
      if (fullSection.split(part).length - 1 !== expected) problems.push(`${rel}: llms-full.txt entry lacks ${part} for ${expected} examples`);
    }
  }
  const url = `${ORIGIN}${twinId === 'index' ? '' : `${twinId}/`}`;
  if (!full.includes(`<!-- page: ${url} -->`)) problems.push(`${rel}: missing from llms-full.txt`);
  if (twinStatus) {
    if (!llmsLines.some((line) => line.includes(`](${url})`) && line.includes(`(status: ${twinStatus})`))) {
      problems.push(`${rel}: llms.txt line has no (status: ${twinStatus})`);
    }
    const section = full.split(`<!-- page: ${url} -->`)[1]?.split('\n\n---\n\n')[0] ?? '';
    if (!section.includes(`Status: ${twinStatus} (`)) problems.push(`${rel}: llms-full.txt entry has no Status: ${twinStatus}`);
  }
}
const readJson = (file) => JSON.parse(fs.readFileSync(file, 'utf8'));
const dataTwins = [
  { id: 'health', rows: readJson('src/data/health.json').rows.map((row) => row.label) },
  {
    id: 'showcase',
    rows: [
      ...readJson('src/data/showcase.json').flatMap((item) => [item.title, fs.readFileSync(path.join('src/data', item.textFile), 'utf8').trim()]),
      readJson('src/data/runs/hook-sample-run.json').recorded_at,
    ],
  },
];
for (const { id, rows } of dataTwins) {
  const file = path.join(dist, `${id}.md`);
  if (!fs.existsSync(file)) {
    problems.push(`${id}.md: data page has no markdown twin`);
    continue;
  }
  const text = fs.readFileSync(file, 'utf8');
  if (!/^---\ntitle: ".+"\n/.test(text)) problems.push(`${id}.md: twin has no front matter title`);
  for (const row of rows) if (!text.includes(row)) problems.push(`${id}.md: twin lacks "${row.slice(0, 50)}"`);
  if (!llms.includes(`](${ORIGIN}${id}.md)`)) problems.push(`llms.txt: does not link ${id}.md`);
}
const kitSums = fs.readFileSync('public/downloads/SHA256SUMS', 'utf8').split('\n').filter(Boolean);
if (!llms.includes(`](${ORIGIN}downloads/SHA256SUMS)`)) problems.push('llms.txt: does not list downloads/SHA256SUMS');
for (const line of kitSums) {
  const [digest, name] = line.split(/ {2}/);
  if (!llms.split('\n').some((l) => l.includes(`](${ORIGIN}downloads/${name})`) && l.includes(digest))) problems.push(`llms.txt: kit ${name} is not listed with its SHA-256`);
}
for (const heading of rules.match(/^## .* \(([^)]*)\)$/gm) ?? []) {
  if (!/\(https:\/\/glentiki\.dev\/agentic-harness-guide\//.test(heading)) problems.push(`agent-rules.txt: heading link is not absolute: ${heading}`);
}
console.log(`${twins} markdown twins checked, ${dataTwins.length} data twins, ${kitSums.length} kits listed`);

console.log(`${pages} pages checked, ${listedPaths.length} links in llms.txt, ${problems.length} problems`);
for (const problem of problems) console.log(`  problem: ${problem}`);
process.exit(problems.length ? 1 : 0);
