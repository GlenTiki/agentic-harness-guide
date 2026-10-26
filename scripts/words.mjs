import fs from 'node:fs';
import path from 'node:path';
import { countWords } from './lib/prose.mjs';

const root = path.resolve('src/content/docs');
const caps = [
  [/^journey\/\d\d-/, 2000],
  [/^workflows\/(?!index)/, 1800],
];
const strict = process.argv.includes('--strict');

const files = [];
const walk = (dir) => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (/\.mdx?$/.test(entry.name)) files.push(full);
  }
};
walk(root);

let over = 0;
const rows = files
  .map((file) => {
    const rel = path.relative(root, file).replace(/\.mdx?$/, '');
    const cap = caps.find(([pattern]) => pattern.test(rel))?.[1];
    return { rel, words: countWords(fs.readFileSync(file, 'utf8')), cap };
  })
  .sort((a, b) => a.rel.localeCompare(b.rel));

for (const { rel, words, cap } of rows) {
  const flag = cap && words > cap ? `  OVER by ${words - cap}` : '';
  if (flag) over += 1;
  console.log(`${String(words).padStart(6)}  ${cap ? String(cap).padStart(5) : '    -'}  ${rel}${flag}`);
}
console.log(`${rows.length} pages, ${over} over their cap (informational${strict ? ', strict' : ''})`);
process.exit(strict && over ? 1 : 0);
