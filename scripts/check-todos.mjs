import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.argv[2] ?? 'src/content/docs');
const marker = 'TODO(writer)';
const banned = ['Verified against'];
const hits = [];
const unlabelled = [];
const wrongReply = /of a WRONG reply/;
const provenanceLabel = /^(Observed|Computed|Constructed)\b/;
const walk = (dir) => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (/\.mdx?$/.test(entry.name)) {
      const lines = fs.readFileSync(full, 'utf8').split('\n');
      lines.forEach((line, i) => {
        if (wrongReply.test(line) && !provenanceLabel.test(line)) unlabelled.push(`${path.relative(root, full)}:${i + 1}`);
        if (line.includes(marker) || banned.some((phrase) => line.includes(phrase))) hits.push(`${path.relative(root, full)}:${i + 1}`);
      });
    }
  }
};
walk(root);

const perFile = new Map();
for (const hit of hits) {
  const file = hit.split(':')[0];
  perFile.set(file, (perFile.get(file) ?? 0) + 1);
}
for (const [file, count] of perFile) console.log(`${file}: ${count} TODO(writer) or banned phrase`);
console.log(`${perFile.size} files with ${hits.length} markers or banned phrases remaining`);
for (const where of unlabelled) console.log(`${where}: wrong reply without an Observed, Computed or Constructed label`);
const slipFile = 'src/components/SlipCompare.astro';
const slipUnlabelled = process.argv[2] === undefined && !fs.readFileSync(slipFile, 'utf8').includes('Observed');
if (slipUnlabelled) console.log(`${slipFile}: wrong reply card without an Observed tag`);
process.exit(hits.length || unlabelled.length || slipUnlabelled ? 1 : 0);
