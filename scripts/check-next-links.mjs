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
    const route = rel.replace(/(^|\/)index\.mdx?$/, '$1').replace(/\.mdx?$/, '/');
    const built = path.join('dist', route, 'index.html');
    if (!fs.existsSync(built)) {
      problems.push(`${rel}: built page missing; run the build first`);
      continue;
    }
    const html = fs.readFileSync(built, 'utf8');
    const inlineLinks = [...html.matchAll(/<p><strong>Next:<\/strong>\s*<a href="([^"]+)"/g)];
    const cards = [...html.matchAll(/<a\b(?=[^>]*\brel="next")(?=[^>]*\bhref="([^"]+)")[^>]*>/g)];
    const [inline] = inlineLinks;
    const [card] = cards;
    const base = `https://guide.invalid/agentic-harness-guide/${route}`;
    if (inlineLinks.length !== 1 || cards.length > 1) problems.push(`${rel}: built Next links missing or ambiguous`);
    if (!card && rel !== 'shelf/reference/anti-patterns.md') problems.push(`${rel}: navigation card missing`);
    if (!inline) continue;
    if (new URL(inline[1], base).href !== new URL(href, base).href) problems.push(`${rel}: built Next differs from source; rebuild`);
    if (card && new URL(inline[1], base).href !== new URL(card[1], base).href) {
      problems.push(`${rel}: inline Next and navigation card have different destinations`);
    }
  }
}
console.log(`${links} Next links checked, ${problems.length} problems`);
for (const problem of problems) console.log(`  problem: ${problem}`);
process.exit(problems.length ? 1 : 0);
