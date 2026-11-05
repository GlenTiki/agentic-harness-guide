import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const utcSeconds = (iso) => new Date(iso).toISOString().replace(/\.\d+Z$/, 'Z');

const git = (repoRoot, args) => {
  const env = { ...process.env };
  for (const key of ['GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE']) delete env[key];
  return execFileSync('git', args, { cwd: repoRoot, env, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim();
};

const historyRoot = (repoRoot) => {
  if (!fs.existsSync(path.join(repoRoot, '.git'))) return null;
  if (git(repoRoot, ['rev-parse', '--is-shallow-repository']) === 'true') {
    throw new Error('Page dates require complete history; shallow repositories are not supported.');
  }
  const roots = git(repoRoot, ['rev-list', '--max-parents=0', 'HEAD']).split('\n');
  if (roots.length !== 1 || !roots[0]) throw new Error('Page dates require a single reachable history root.');
  return roots[0];
};

const gitDate = (kind, file, repoRoot) => {
  if (!fs.existsSync(path.resolve(repoRoot, file))) return null;
  const relative = path.relative(repoRoot, path.resolve(repoRoot, file)).split(path.sep).join('/');
  const manifest = path.join(repoRoot, 'src/data/page-dates.json');
  const baseline = fs.existsSync(manifest) ? JSON.parse(fs.readFileSync(manifest, 'utf8'))[relative] : undefined;
  const root = historyRoot(repoRoot);
  if (!root) {
    if (baseline) return baseline[kind];
    throw new Error(`Source archive has no date baseline for ${relative}; build from complete Git history or refresh the baseline before export.`);
  }
  if (kind === 'first' && baseline) return baseline.first;
  const args = kind === 'first' ? ['--reverse'] : ['-1'];
  const record = git(repoRoot, ['log', '--format=%H%x09%cI', ...args, '--', relative]).split('\n')[0];
  if (!record) return null;
  const [commit, date] = record.split('\t');
  return kind === 'last' && baseline && commit === root ? baseline.last : utcSeconds(date);
};

export const lastCommitDate = (file, repoRoot = process.cwd()) => gitDate('last', file, path.resolve(repoRoot));
export const firstCommitDate = (file, repoRoot = process.cwd()) => gitDate('first', file, path.resolve(repoRoot));

const docsRoot = 'src/content/docs';
export const sourceFileFor = (id, repoRoot = process.cwd()) =>
  [`${id}.md`, `${id}.mdx`, `${id}/index.md`, `${id}/index.mdx`]
    .map((name) => path.join(docsRoot, name))
    .find((candidate) => fs.existsSync(path.join(repoRoot, candidate))) ?? null;
