import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fullMatch, isVisible, resolve, validate } from '../src/lib/kit-rules.mjs';

const kit = path.resolve('examples/starter-kit');
const manifest = JSON.parse(fs.readFileSync(path.join(kit, 'kit-manifest.json'), 'utf8'));
const fixtures = Object.fromEntries(
  fs
    .readdirSync(path.join(kit, 'fixtures'))
    .filter((name) => name.endsWith('.json'))
    .sort()
    .map((name) => [name.replace(/\.json$/, ''), JSON.parse(fs.readFileSync(path.join(kit, 'fixtures', name), 'utf8'))]),
);
const ids = (issues) => issues.map((issue) => issue.id).sort();
const question = (id) => manifest.questions.find((q) => q.id === id);

const PYTHON = `
import json, sys
sys.path.insert(0, sys.argv[1])
import validate_plan
manifest = json.loads(open(sys.argv[2]).read())
out = {}
for name, fixture in json.loads(sys.stdin.read()).items():
    errors, warnings, answers = validate_plan.validate(fixture["plan"], manifest)
    resolution = validate_plan.resolve(answers, manifest) if not errors else None
    out[name] = {"errors": sorted(e for e, _ in errors), "warnings": sorted(w for w, _ in warnings), "messages": sorted(m for _, m in errors + warnings), "resolution": resolution}
print(json.dumps(out))
`;
const python = JSON.parse(
  execFileSync('python3', ['-I', '-c', PYTHON, kit, path.join(kit, 'kit-manifest.json')], { input: JSON.stringify(fixtures), encoding: 'utf8' }),
);

test('the fixtures exist', () => {
  assert.ok(Object.keys(fixtures).length >= 20);
});

for (const [name, fixture] of Object.entries(fixtures)) {
  test(`${name}: the JS evaluator gives the expected outcome and the same result as validate_plan.py`, () => {
    const { errors, warnings, answers } = validate(fixture.plan, manifest);
    assert.equal(errors.length === 0, fixture.expect.valid);
    assert.deepEqual(ids(errors), [...fixture.expect.errors].sort());
    assert.deepEqual(ids(warnings), [...fixture.expect.warnings].sort());
    assert.deepEqual(ids(errors), python[name].errors);
    assert.deepEqual(ids(warnings), python[name].warnings);
    assert.deepEqual([...errors, ...warnings].map((issue) => issue.message).sort(), python[name].messages);
    if (errors.length === 0) {
      const ours = resolve(answers, manifest);
      const theirs = python[name].resolution;
      assert.deepEqual(
        { items: ours.items, writes: ours.writes, run: ours.run, skills: ours.skillsToFind },
        { items: theirs.items, writes: theirs.writes, run: theirs.run, skills: theirs.skills_to_find },
      );
    }
  });
}

test('every rule is named by at least one fixture', () => {
  const named = new Set(Object.values(fixtures).flatMap((f) => [...f.expect.errors, ...f.expect.warnings]));
  for (const rule of manifest.rules) assert.ok(named.has(rule.id), rule.id);
});

test('string patterns match the whole text, as re.fullmatch does', () => {
  for (const id of ['test_command', 'lint_command']) {
    const { pattern } = question(id);
    assert.equal(fullMatch(pattern, 'uv run pytest'), true);
    assert.equal(fullMatch(pattern, 'uv run pytest\nrm -rf .'), false);
    assert.equal(fullMatch(pattern, 'pytest; rm -rf .'), false);
    assert.equal(fullMatch(pattern, 'pytest\n'), false);
    assert.equal(fullMatch(pattern, 'pytest\tx'), false);
    assert.equal(fullMatch(pattern, '   '), false);
  }
});

test('a string over the maximum counts code points, not UTF-16 units', () => {
  const max = question('test_command').max;
  const { errors } = validate({ answers: { test_command: `pytest ${'\u{1F600}'.repeat(max - 7)}` } }, manifest);
  assert.ok(!ids(errors).includes('test_command-max'));
});

test('the form hides the test command until a rule needs it, and hides hooks with no host', () => {
  const tests = question('test_command');
  const hooks = question('hooks');
  assert.equal(isVisible(tests, { hosts: ['claude-code'], hooks: [] }, manifest), false);
  assert.equal(isVisible(tests, { hosts: ['claude-code'], hooks: ['tests-before-stop'] }, manifest), true);
  assert.equal(isVisible(hooks, { hosts: ['codex'] }, manifest), false);
  assert.equal(isVisible(hooks, { hosts: ['claude-code'] }, manifest), true);
});

test('the hook menu has nothing selected by default', () => {
  assert.deepEqual(question('hooks').default, []);
});
