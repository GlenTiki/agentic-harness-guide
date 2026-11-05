import fs from 'node:fs';
import path from 'node:path';

const skillPath = path.resolve(process.argv[2] ?? 'examples/prompt-refiner/SKILL.md');
const pagePath = path.resolve(process.argv[3] ?? 'src/content/docs/appendix/prompt-refiner-line-by-line.mdx');

const skillLines = fs.readFileSync(skillPath, 'utf8').split('\n');
if (skillLines.at(-1) === '') skillLines.pop();
const nonBlank = skillLines.flatMap((text, i) => (text.trim() ? [i + 1] : []));

const seen = new Map();
const problems = [];
for (const [, from, to] of fs.readFileSync(pagePath, 'utf8').matchAll(/\bshow\((\d+),\s*(\d+)\)/g)) {
  const [a, b] = [Number(from), Number(to)];
  if (a > b || b > skillLines.length) problems.push(`range ${a}-${b} is outside the ${skillLines.length}-line file`);
  for (let n = a; n <= b; n++) seen.set(n, (seen.get(n) ?? 0) + 1);
}

for (const n of nonBlank) {
  if (!seen.has(n)) problems.push(`line ${n} has no annotation: ${skillLines[n - 1].slice(0, 60)}`);
}
for (const [n, count] of seen) {
  if (count > 1) problems.push(`line ${n} is annotated ${count} times`);
}

const annotated = nonBlank.filter((n) => seen.has(n)).length;
console.log(`${annotated} of ${nonBlank.length} non-blank lines annotated (${skillLines.length} lines in the file)`);
for (const problem of problems) console.log(`  problem: ${problem}`);
process.exit(problems.length ? 1 : 0);
