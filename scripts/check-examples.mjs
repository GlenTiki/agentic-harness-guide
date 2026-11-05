import fs from 'node:fs';
import path from 'node:path';
import { findExamples, LABELS, REPO_BLOB, REQUIRED_SLOTS, SLOTS } from './lib/example-parse.mjs';

const root = path.resolve(process.argv[2] ?? 'src/content/docs');
const repoRoot = path.resolve(process.argv[3] ?? '.');
const REPO_TREE = REPO_BLOB.replace('/blob/', '/tree/');
const KNOWN_ATTRS = ['label', 'task', 'evidence', 'env'];
const problems = [];
let total = 0;

const evidenceResolves = (item) => {
  const target = /^https?:\/\//.test(item)
    ? [REPO_BLOB, REPO_TREE].map((prefix) => (item.startsWith(prefix) ? item.slice(prefix.length) : null)).find((rel) => rel !== null)
    : item;
  if (target === undefined) return false;
  return fs.existsSync(path.join(repoRoot, decodeURIComponent(target.split('#')[0])));
};

const walk = (dir) => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (/\.mdx$/.test(entry.name)) checkFile(full);
  }
};

function checkFile(file) {
  const source = fs.readFileSync(file, 'utf8');
  const rel = path.relative(root, file);
  const found = findExamples(source);
  const tags = [...source.matchAll(/<Example\b/g)].length;
  const lineOf = (index) => source.slice(0, index).split('\n').length;
  if (tags !== found.length) {
    const unparsed = [...source.matchAll(/<Example\b/g)].find((m) => !found.some((f) => f.start === m.index));
    problems.push(`${rel}:${lineOf(unparsed.index)}: <Example> tag is malformed (use double-quoted string attributes only)`);
  }
  for (const example of found) {
    total += 1;
    const at = `${rel}:${example.line}`;
    const { attrs, slots } = example;
    if (!example.closed) problems.push(`${at}: <Example> has no closing tag`);
    for (const name of Object.keys(attrs)) if (!KNOWN_ATTRS.includes(name)) problems.push(`${at}: unknown attribute ${name}`);
    for (const name of Object.keys(slots)) if (!SLOTS.includes(name)) problems.push(`${at}: unknown slot ${name}`);
    if (!LABELS.includes(attrs.label)) problems.push(`${at}: label "${attrs.label ?? ''}" is not one of ${LABELS.join(', ')}`);
    if (!attrs.task?.trim()) problems.push(`${at}: task is empty`);
    for (const slot of REQUIRED_SLOTS) if (!slots[slot]) problems.push(`${at}: slot "${slot}" is missing or empty`);
    if (slots.shows === '') problems.push(`${at}: slot "shows" is empty (leave the Fragment out when there is nothing to say)`);
    for (const slot of ['input', 'output']) {
      if (slots[slot] && !/^```/m.test(slots[slot])) problems.push(`${at}: slot "${slot}" has no fenced block (show it verbatim)`);
    }
    if (attrs.label === 'Observed') {
      const items = (attrs.evidence ?? '').split(/\s+/).filter(Boolean);
      if (items.length === 0) problems.push(`${at}: Observed example has no evidence`);
      for (const item of items) {
        if (!evidenceResolves(item)) problems.push(`${at}: evidence does not resolve to a file in this repository: ${item}`);
      }
    }
    if (attrs.label === 'Computed' && !attrs.evidence?.trim()) problems.push(`${at}: Computed example has no script or sum in evidence`);
  }
}

walk(root);
console.log(`${total} examples checked, ${problems.length} problems`);
for (const problem of problems) console.log(`  problem: ${problem}`);
process.exit(problems.length ? 1 : 0);
