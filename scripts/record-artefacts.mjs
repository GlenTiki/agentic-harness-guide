import { execFileSync, spawnSync } from 'node:child_process';
import fs from 'node:fs';

const now = () => new Date().toISOString().replace(/\.\d+Z$/, 'Z');
const write = (file, text) => fs.writeFileSync(file, text.endsWith('\n') ? text : `${text}\n`);

const matrix = spawnSync('python3', ['-I', 'examples/hook-sample/test_matrix.py'], { encoding: 'utf8' });
if (matrix.status !== 0) throw new Error(`hook matrix failed:\n${matrix.stdout}${matrix.stderr}`);
const matrixPython = execFileSync('python3', ['-I', '--version'], { encoding: 'utf8' }).trim();
const matrixDate = new Date().toISOString().slice(0, 10);
write(
  'src/data/artefacts/hook-matrix.txt',
  `Run on ${matrixDate} with ${matrixPython}\n${matrix.stdout.replace(/^OK {2}page shows.*\n/m, '').trimEnd()}`,
);

const results = fs.readFileSync('examples/prompt-refiner/evals/runs/2026-10-22/RESULTS.md', 'utf8');
const table = results.split('\n').filter((line) => line.startsWith('|'));
write('src/data/artefacts/eval-results.md', table.join('\n'));
write('src/data/artefacts/recorded-run.md', fs.readFileSync('examples/recorded-runs/l0/bills_1.txt', 'utf8').trimEnd());
write('src/data/artefacts/prompt-refiner.md', fs.readFileSync('examples/prompt-refiner/SKILL.md', 'utf8').trimEnd());

const calls = [
  ['git status', 'allow'],
  ['git log --oneline', 'allow'],
  ['git push -u origin feature-fix', 'allow'],
  ['git push --force', 'block'],
  ['git commit -m "update notes"', 'allow'],
  ['git push origin +main', 'block'],
  ['echo hello', 'allow'],
  ['git push -f origin main', 'block'],
];
const startedAt = now();
const origin = performance.now();
const events = calls.map(([command, expected], index) => {
  const input = JSON.stringify({ tool_name: 'Bash', tool_input: { command } });
  const begin = performance.now();
  const result = spawnSync('python3', ['-I', 'examples/hook-sample/block_force_push.py'], { input, encoding: 'utf8' });
  const duration = performance.now() - begin;
  const decision = result.status === 2 ? 'block' : 'allow';
  if (decision !== expected) throw new Error(`call ${index + 1}: expected ${expected}, hook said ${decision}`);
  return {
    seq: index + 1,
    event_type: 'PreToolUse',
    tool_name: 'Bash',
    offset_ms: Math.round(begin - origin),
    duration_ms: Math.round(duration),
    exit_code: result.status,
    decision,
  };
});
const python = execFileSync('python3', ['-I', '--version'], { encoding: 'utf8' }).trim();
write(
  'src/data/runs/hook-sample-run.json',
  JSON.stringify(
    {
      title: 'One recorded run of the sample pre-tool hook',
      recorded_at: startedAt,
      source: 'scripts/record-artefacts.mjs running examples/hook-sample/block_force_push.py',
      environment: python,
      fields: 'Metadata only. Command text and tool output are not stored.',
      events,
    },
    null,
    2,
  ),
);

const showcase = JSON.parse(fs.readFileSync('src/data/showcase.json', 'utf8'));
const stamp = now();
for (const item of showcase) item.preparedAt = stamp;
write('src/data/showcase.json', JSON.stringify(showcase, null, 2));
console.log(`artefacts recorded at ${stamp}; ${events.length} hook events`);
