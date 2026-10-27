import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const page = (rel) => fs.readFileSync(`src/content/docs/shelf/${rel}`, 'utf8');
const between = (text, from, to) => text.slice(text.indexOf(from), text.indexOf(to, text.indexOf(from)));

test('the one-shot stop script is called a reminder and a gate checks the test result', () => {
  const hooks = page('control/hooks.mdx');
  assert.match(hooks, /### A one-shot stop reminder/);
  assert.match(hooks, /### A stop gate that checks the result/);
  assert.doesNotMatch(page('quality/test-first-and-gates.mdx'), /The hook must fire once and then let the agent stop/);
});

test('the flaky test and its fix share one test file', () => {
  const gates = page('quality/test-first-and-gates.mdx');
  assert.match(gates, /Both versions run the same test file/);
  assert.equal(fs.readFileSync('examples/gate-gaming/gates.py', 'utf8').includes('SET_ORDER_FIXED_TEST'), false);
});

test('approval list and never list do not overlap', () => {
  const text = page('operations/human-in-the-loop.mdx');
  const approval = between(text, 'The first list holds', 'The second list holds');
  const never = between(text, 'The second list holds', '**2. Apply the lists');
  assert.doesNotMatch(approval, /orce-push(ing)? (anywhere|a shared)/);
  assert.doesNotMatch(approval, /safety control/);
  assert.match(never, /Force-pushing a shared branch/);
  assert.match(never, /safety control/);
  assert.match(text, /\| Force-push a shared branch \| Never \|/);
});

test('unmeasured behaviour claims are labelled and the frequency figure is gone', () => {
  assert.doesNotMatch(page('control/permissions-and-sandboxing.mdx'), /two hundred times a day/);
  for (const [file, claim] of [
    ['quality/spec-driven-development.mdx', 'an agent may not stop at a gap'],
    ['quality/test-first-and-gates.mdx', 'an agent that meets a flaky gate can rerun it'],
    ['delegation/skills.mdx', 'a description that says what the skill does but not what it is not for can match'],
    ['control/permissions-and-sandboxing.mdx', 'a person who is asked for approval often can stop reading'],
  ]) {
    const text = page(file);
    const at = text.indexOf(claim);
    assert.ok(at > 0, `${file}: claim missing`);
    assert.match(text.slice(Math.max(0, at - 40), at), /Principle, not measured/, file);
  }
});

test('git variables are explained separately', () => {
  const text = page('delegation/worktree-isolation.mdx');
  assert.match(text, /`GIT_DIR` selects the repository metadata/);
  assert.match(text, /`GIT_WORK_TREE` selects the folder that git reads as the working files/);
  assert.match(text, /`GIT_INDEX_FILE` selects the index/);
  assert.doesNotMatch(text, /`GIT_DIR` or `GIT_WORK_TREE` is set in the shell/);
});

test('the delegation rule separates knowing the answer from knowing its format', () => {
  const text = page('delegation/topology.mdx');
  assert.match(text, /Knowing the answer is not the same as knowing its format/);
  assert.doesNotMatch(text, /If you know the answer's shape, doing the work costs about the same as briefing it/);
  assert.match(text, /producing each part costs more than briefing and reviewing a helper/);
});

test('the release-notes skill does not rely on merge commits and reconciles', () => {
  const text = page('delegation/skills.mdx');
  assert.doesNotMatch(text, /1\. Run `git log <last-tag>\.\.HEAD --merges --oneline`/);
  assert.match(text, /Reconcile\./);
  assert.match(text, /squash merge or a rebase merge makes ordinary commits/);
});

test('the refunds example carries a CSV whose figures give the shown total and a dollar row', () => {
  const text = page('delegation/topology.mdx');
  const csv = text.split('refunds.csv (invented):\n')[1].split('\n```')[0].trim().split('\n').slice(1).map((line) => line.split(','));
  const september = csv.filter(([date]) => date.startsWith('2026-09'));
  const total = september.reduce((sum, row) => sum + Number(row[2]), 0);
  assert.equal(total.toFixed(2), '412.50');
  assert.ok(september.some((row) => row[3] === 'USD'));
  assert.ok(csv.some(([date]) => !date.startsWith('2026-09')));
});

test('the hook timeline sits inside an Example and the latency disclaimer is narrow', () => {
  const text = page('control/hooks.mdx');
  const example = between(text, 'task="A maintainer pipes eight made-up tool calls', '**5. Write good block messages.**');
  assert.match(example, /<HookTimeline /);
  assert.match(example, /standalone script measurement with made-up tool-call JSON/);
  assert.match(example, /not a harness session/);
  assert.doesNotMatch(text, /This guide did not time any hook/);
  assert.match(text, /measured no harness-level latency and no parallel-hook latency/);
});
