import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { firstCommitDate, lastCommitDate, sourceFileFor } from './lib/git-dates.mjs';

const page = 'src/content/docs/example.mdx';
const first = '2026-01-01T01:02:03Z';
const last = '2026-02-02T02:03:04Z';
const baselineFile = 'src/data/page-dates.json';
const gitEnv = () => {
  const env = { ...process.env };
  for (const key of ['GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE']) delete env[key];
  return env;
};
const git = (root, ...args) => execFileSync('git', args, { cwd: root, env: gitEnv(), encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
const write = (root, file, body) => {
  fs.mkdirSync(path.dirname(path.join(root, file)), { recursive: true });
  fs.writeFileSync(path.join(root, file), body);
};
const commit = (root, date) => {
  git(root, 'add', '.');
  execFileSync('git', ['commit', '-qm', 'fixture'], {
    cwd: root, env: { ...gitEnv(), GIT_AUTHOR_DATE: date, GIT_COMMITTER_DATE: date },
  });
};
const fixture = (t) => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'guide-dates-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  git(root, 'init', '-q');
  git(root, 'config', 'commit.gpgsign', 'false');
  git(root, 'config', 'core.hooksPath', path.join(root, '.fixture-hooks'));
  git(root, 'config', 'user.name', 'Fixture');
  git(root, 'config', 'user.email', 'fixture@example.invalid');
  write(root, page, 'original');
  commit(root, first);
  write(root, page, 'revised');
  commit(root, last);
  return root;
};
const addBaseline = (root) => {
  write(root, baselineFile, `${JSON.stringify({ [page]: { first, last } }, null, 2)}\n`);
  commit(root, '2026-03-03T03:04:05Z');
};
const squash = (root) => {
  const tree = git(root, 'rev-parse', 'HEAD^{tree}');
  const rootCommit = git(root, 'commit-tree', tree, '-m', 'New public root');
  git(root, 'checkout', '-q', '--detach', rootCommit);
  assert.equal(git(root, 'rev-parse', 'HEAD^{tree}'), tree);
};

test('full history, exact-tree root squash, edits, reverts, new pages and unrelated commits', (t) => {
  const root = fixture(t);
  assert.equal(firstCommitDate(page, root), first);
  assert.equal(lastCommitDate(page, root), last);
  assert.equal(sourceFileFor('example', root), page);
  addBaseline(root);
  assert.equal(firstCommitDate(page, root), first);
  assert.equal(lastCommitDate(page, root), last);
  squash(root);
  assert.equal(firstCommitDate(page, root), first);
  assert.equal(lastCommitDate(page, root), last);
  write(root, page, 'later edit');
  commit(root, '2026-04-04T04:05:06Z');
  assert.equal(lastCommitDate(page, root), '2026-04-04T04:05:06Z');
  write(root, page, 'revised');
  commit(root, '2026-05-05T05:06:07Z');
  assert.equal(lastCommitDate(page, root), '2026-05-05T05:06:07Z');
  assert.equal(firstCommitDate(page, root), first);
  const newPage = 'src/content/docs/new.md';
  write(root, newPage, 'new');
  commit(root, '2026-06-06T06:07:08Z');
  assert.equal(firstCommitDate(newPage, root), '2026-06-06T06:07:08Z');
  assert.equal(lastCommitDate(newPage, root), '2026-06-06T06:07:08Z');
  write(root, 'README.md', 'unrelated');
  commit(root, '2026-07-07T07:08:09Z');
  assert.equal(lastCommitDate(page, root), '2026-05-05T05:06:07Z');
  assert.equal(lastCommitDate(newPage, root), '2026-06-06T06:07:08Z');
});

test('source archive uses known baseline and refuses unknown page, even inside another repo', (t) => {
  const outer = fixture(t);
  const root = path.join(outer, 'archive');
  write(root, page, 'revised');
  write(root, baselineFile, JSON.stringify({ [page]: { first, last } }));
  assert.equal(firstCommitDate(page, root), first);
  assert.equal(lastCommitDate(page, root), last);
  assert.equal(firstCommitDate('src/content/docs/health.md', root), null);
  assert.equal(lastCommitDate('src/content/docs/health.md', root), null);
  write(root, 'src/content/docs/new.md', 'new');
  assert.throws(() => lastCommitDate('src/content/docs/new.md', root), /archive.*baseline/i);
  assert.throws(() => firstCommitDate('src/content/docs/new.md', root), /archive.*baseline/i);
});

test('rejects shallow history instead of assigning the shallow boundary date', (t) => {
  const root = fixture(t);
  addBaseline(root);
  const shallow = path.join(root, 'shallow');
  git(root, 'clone', '-q', '--depth=1', `file://${root}`, shallow);
  assert.throws(() => firstCommitDate(page, shallow), /shallow/i);
  assert.throws(() => lastCommitDate(page, shallow), /shallow/i);
});

test('rejects multiple reachable roots', (t) => {
  const root = fixture(t);
  addBaseline(root);
  const original = git(root, 'rev-parse', 'HEAD');
  const tree = git(root, 'rev-parse', 'HEAD^{tree}');
  const other = git(root, 'commit-tree', tree, '-m', 'Other root');
  const merged = git(root, 'commit-tree', tree, '-p', original, '-p', other, '-m', 'Merge roots');
  git(root, 'checkout', '-q', '--detach', merged);
  assert.throws(() => firstCommitDate(page, root), /single.*root|multiple.*root/i);
  assert.throws(() => lastCommitDate(page, root), /single.*root|multiple.*root/i);
});

test('worktree file and inherited git overrides do not select another repository', (t) => {
  const root = fixture(t);
  addBaseline(root);
  const worktree = path.join(root, 'worktree');
  git(root, 'worktree', 'add', '-q', '--detach', worktree);
  const saved = Object.fromEntries(['GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE'].map((key) => [key, process.env[key]]));
  try {
    process.env.GIT_DIR = '/does-not-exist';
    process.env.GIT_WORK_TREE = '/does-not-exist';
    process.env.GIT_INDEX_FILE = '/does-not-exist';
    assert.equal(firstCommitDate(page, worktree), first);
    assert.equal(lastCommitDate(page, worktree), last);
    assert.equal(sourceFileFor('example', worktree), page);
  } finally {
    for (const [key, value] of Object.entries(saved)) {
      if (value === undefined) delete process.env[key];
      else process.env[key] = value;
    }
  }
});

test('baseline generator records tracked page dates and refuses uncommitted page changes', (t) => {
  const root = fixture(t);
  const generator = path.resolve('scripts/record-page-dates.mjs');
  execFileSync(process.execPath, [generator, root], { env: gitEnv() });
  assert.deepEqual(JSON.parse(fs.readFileSync(path.join(root, baselineFile), 'utf8')), { [page]: { first, last } });
  const original = fs.readFileSync(path.join(root, baselineFile), 'utf8');
  write(root, page, 'uncommitted edit');
  assert.throws(() => execFileSync(process.execPath, [generator, root], { env: gitEnv(), stdio: 'pipe' }), /uncommitted/i);
  assert.equal(fs.readFileSync(path.join(root, baselineFile), 'utf8'), original);
});
