import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const folder = path.resolve(process.argv[2] ?? 'public/downloads');
const expectedKits = 13;
const problems = [];

const sumsFile = path.join(folder, 'SHA256SUMS');
if (!fs.existsSync(sumsFile)) {
  console.log(`missing ${path.relative(process.cwd(), sumsFile)}`);
  process.exit(1);
}

const listed = new Map();
for (const line of fs.readFileSync(sumsFile, 'utf8').split('\n').filter(Boolean)) {
  const match = line.match(/^([0-9a-f]{64}) {2}(\S+)$/);
  if (!match) problems.push(`bad SHA256SUMS line: ${line}`);
  else listed.set(match[2], match[1]);
}

if (listed.size !== expectedKits) problems.push(`SHA256SUMS lists ${listed.size} kits; expected ${expectedKits}`);

for (const [name, digest] of listed) {
  const file = path.join(folder, name);
  if (!fs.existsSync(file)) {
    problems.push(`missing download: ${name}`);
    continue;
  }
  const actual = crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
  if (actual !== digest) problems.push(`checksum mismatch: ${name}`);
}

for (const name of fs.readdirSync(folder)) {
  if (name.endsWith('.zip') && !listed.has(name)) problems.push(`download not in SHA256SUMS: ${name}`);
}

const pagesText = fs.readFileSync(path.resolve('src/content/docs/case-study/index.mdx'), 'utf8');
for (const [name, digest] of listed) {
  if (!pagesText.includes(digest)) problems.push(`index page does not show the checksum for ${name}`);
}

console.log(`${listed.size} downloads checked, ${problems.length} problems`);
for (const problem of problems) console.log(problem);
process.exit(problems.length ? 1 : 0);
