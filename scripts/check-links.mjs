import fs from 'node:fs';
import path from 'node:path';

const dist = path.resolve('dist');
const base = '/agentic-harness-guide';
const htmlFiles = [];
const walk = (dir) => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (entry.name.endsWith('.html')) htmlFiles.push(full);
  }
};
walk(dist);

const idsByFile = new Map();
for (const file of htmlFiles) {
  const html = fs.readFileSync(file, 'utf8');
  idsByFile.set(file, new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1])));
}

const resolveTarget = (urlPath) => {
  const rel = decodeURIComponent(urlPath.slice(base.length)).replace(/^\//, '');
  const candidates = [path.join(dist, rel, 'index.html'), path.join(dist, rel)];
  return candidates.find((c) => fs.existsSync(c) && fs.statSync(c).isFile());
};

const problems = [];
for (const file of htmlFiles) {
  const html = fs.readFileSync(file, 'utf8');
  const pageUrl = base + '/' + path.relative(dist, file).replace(/index\.html$/, '');
  for (const match of html.matchAll(/\s(?:href|src)="([^"]+)"/g)) {
    const raw = match[1];
    if (/^(https?:|mailto:|data:|tel:)/.test(raw)) continue;
    const resolved = new URL(raw, 'http://x' + pageUrl);
    const target = resolveTarget(resolved.pathname.startsWith(base) ? resolved.pathname : base + resolved.pathname);
    const where = path.relative(dist, file);
    if (!resolved.pathname.startsWith(base)) {
      problems.push(`${where}: outside base: ${raw}`);
      continue;
    }
    if (!target) {
      problems.push(`${where}: missing target: ${raw}`);
      continue;
    }
    const hash = resolved.hash.slice(1);
    if (hash && target.endsWith('.html') && !idsByFile.get(target)?.has(decodeURIComponent(hash))) {
      problems.push(`${where}: missing anchor: ${raw}`);
    }
  }
}

console.log(`${htmlFiles.length} pages checked, ${problems.length} problems`);
for (const problem of problems) console.log(problem);
process.exit(problems.length ? 1 : 0);
