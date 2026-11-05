import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { firstCommitDate, lastCommitDate } from './lib/git-dates.mjs';

const repoRoot = path.resolve(process.argv[2] ?? '.');
if (!fs.existsSync(path.join(repoRoot, '.git'))) throw new Error('Record the date baseline from a Git checkout, not a source archive.');
const env = { ...process.env };
for (const key of ['GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE']) delete env[key];
const git = (args) => execFileSync('git', args, { cwd: repoRoot, env, encoding: 'utf8' }).trim();
if (git(['status', '--porcelain', '--', 'src/content/docs'])) {
  throw new Error('Commit uncommitted Guide page changes before recording their date baseline.');
}
const files = git(['ls-files', '-z', '--', 'src/content/docs']).split('\0').filter((file) => /\.mdx?$/.test(file)).sort();
const baseline = Object.fromEntries(files.map((file) => {
  const first = firstCommitDate(file, repoRoot);
  const last = lastCommitDate(file, repoRoot);
  if (!first || !last) throw new Error(`No committed dates for ${file}.`);
  return [file, { first, last }];
}));
const destination = path.join(repoRoot, 'src/data/page-dates.json');
fs.mkdirSync(path.dirname(destination), { recursive: true });
fs.writeFileSync(destination, `${JSON.stringify(baseline, null, 2)}\n`);
console.log(`Recorded dates for ${files.length} Guide pages.`);
