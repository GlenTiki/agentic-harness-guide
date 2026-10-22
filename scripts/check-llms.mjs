import fs from 'node:fs';
import path from 'node:path';

const docsRoot = path.resolve('src/content/docs');
const dist = path.resolve('dist');
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
  const occurrences = listedPaths.filter((p) => p === pagePath(file)).length;
  if (occurrences !== 1) problems.push(`${rel}: listed ${occurrences} times in llms.txt, expected once`);
}

for (const listed of listedPaths) {
  const rel = decodeURIComponent(listed.slice(base.length)).replace(/^\//, '');
  const target = [path.join(dist, rel, 'index.html'), path.join(dist, rel)].find((c) => fs.existsSync(c) && fs.statSync(c).isFile());
  if (!target) problems.push(`llms.txt: link does not resolve in dist: ${listed}`);
}

console.log(`${pages} pages checked, ${listedPaths.length} links in llms.txt, ${problems.length} problems`);
for (const problem of problems) console.log(`  problem: ${problem}`);
process.exit(problems.length ? 1 : 0);
