import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve('src/content/docs');
const marker = 'TODO(writer)';
const hits = [];
const walk = (dir) => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (/\.mdx?$/.test(entry.name)) {
      const lines = fs.readFileSync(full, 'utf8').split('\n');
      lines.forEach((line, i) => line.includes(marker) && hits.push(`${path.relative(root, full)}:${i + 1}`));
    }
  }
};
walk(root);

const perFile = new Map();
for (const hit of hits) {
  const file = hit.split(':')[0];
  perFile.set(file, (perFile.get(file) ?? 0) + 1);
}
for (const [file, count] of perFile) console.log(`${file}: ${count} TODO(writer)`);
console.log(`${perFile.size} files with ${hits.length} markers remaining`);
process.exit(hits.length ? 1 : 0);
