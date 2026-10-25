import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve('src/content/docs');
const scope = process.argv.slice(2);
const problems = [];
let links = 0;

const files = [];
const walk = (dir) => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (/\.mdx?$/.test(entry.name)) files.push(full);
  }
};
walk(root);

const titleOf = (file) => fs.readFileSync(file, 'utf8').match(/^title:\s*(.+)$/m)?.[1].trim().replace(/^(["'])(.*)\1$/, '$2');

const resolveTarget = (from, href) => {
  const base = /^index\.mdx?$/.test(path.basename(from)) ? path.dirname(from) : from.replace(/\.mdx?$/, '');
  const target = path.normalize(path.join(base, href.split('#')[0])).replace(/\/$/, '');
  return [`${target}.mdx`, `${target}.md`, path.join(target, 'index.mdx'), path.join(target, 'index.md')].find((c) => fs.existsSync(c));
};

for (const file of files) {
  const rel = path.relative(root, file);
  if (scope.length && !scope.some((prefix) => rel.startsWith(prefix))) continue;
  for (const [, text, href] of fs.readFileSync(file, 'utf8').matchAll(/\*\*Next:\*\*\s*\[([^\]]+)\]\(([^)]+)\)/g)) {
    links += 1;
    const target = resolveTarget(file, href);
    if (!target) problems.push(`${rel}: Next link does not resolve: ${href}`);
    else if (titleOf(target) !== text) problems.push(`${rel}: Next text "${text}" differs from the page title "${titleOf(target)}"`);
  }
}
console.log(`${links} Next links checked, ${problems.length} problems`);
for (const problem of problems) console.log(`  problem: ${problem}`);
process.exit(problems.length ? 1 : 0);
