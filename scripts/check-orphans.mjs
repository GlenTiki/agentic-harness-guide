import fs from 'node:fs';
import path from 'node:path';

const dist = path.resolve(process.env.DIST ?? 'dist');
const ROOT = 'https://glentiki.dev/agentic-harness-guide/';
const files = [];
const walk = (dir) => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory() && !['pagefind', '_astro'].includes(entry.name)) walk(full);
    else if (entry.name === 'index.html' || entry.name === '404.html') files.push(full);
  }
};
walk(dist);

const idOf = (file) => {
  const rel = path.relative(dist, file).replace(/\\/g, '/');
  if (rel === '404.html') return '404';
  return rel.replace(/(^|\/)index\.html$/, '');
};
const urlOf = (id) => `${ROOT}${id === '' ? '' : `${id}/`}`;

const pages = new Map(files.map((file) => [idOf(file), file]));
const inbound = new Map([...pages.keys()].map((id) => [id, new Set()]));
const redirects = new Set();
for (const [id, file] of pages) {
  const html = fs.readFileSync(file, 'utf8');
  if (id === '404') continue;
  if (/http-equiv="refresh"/.test(html)) {
    redirects.add(id);
    continue;
  }
  for (const [, href] of html.matchAll(/<a [^>]*href="([^"#?]*)/g)) {
    if (!href || /^(mailto:|https?:\/\/(?!glentiki\.dev))/.test(href)) continue;
    const target = new URL(href, urlOf(id)).href;
    if (!target.startsWith(ROOT)) continue;
    const targetId = target.slice(ROOT.length).replace(/\/$/, '');
    if (targetId !== id && inbound.has(targetId)) inbound.get(targetId).add(id);
  }
}

const problems = [...inbound]
  .filter(([id, from]) => from.size === 0 && !redirects.has(id) && id !== '404')
  .map(([id]) => `${id || 'home'}: no other page links to it`);
console.log(`${pages.size} pages, ${redirects.size} redirect, ${problems.length} orphans`);
for (const problem of problems) console.log(`  problem: ${problem}`);
process.exit(problems.length ? 1 : 0);
