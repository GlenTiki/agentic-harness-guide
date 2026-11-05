import { spawnSync } from 'node:child_process';
import fs from 'node:fs';

const now = () => new Date().toISOString().replace(/\.\d+Z$/, 'Z');
const checks = [
  ['links', 'Internal links resolve', 'scripts/check-links.mjs', 'Every internal link and anchor in the built site points at a real target.'],
  ['skill-coverage', 'Skill coverage', 'scripts/check-skill-coverage.mjs', 'Every rule in the sample skill is explained on the walkthrough page.'],
  ['todos', 'No unfinished markers', 'scripts/check-todos.mjs', 'No placeholder markers or banned phrases remain in the pages.'],
  ['examples', 'Examples carry all five parts', 'scripts/check-examples.mjs', 'Every Example has a valid label, a task, input, output, notice and shows, and an Observed example has evidence that resolves.'],
  ['evidence', 'Evidence page matches the test results', 'scripts/make-evidence.mjs --check', 'The evidence page equals the output of the generator run on examples/wrong-behaviour/results.json.'],
  ['llms', 'Machine layer (llms.txt, twins, rules)', 'scripts/check-llms.mjs', 'llms.txt, llms-full.txt, agent-rules.txt and every Markdown twin are present and consistent.'],
  ['contrast', 'Colour contrast of the design tokens', 'scripts/check-contrast.mjs', 'Every token pair meets WCAG AA in light and dark.'],
  ['seo', 'Search and sharing metadata', 'scripts/check-seo.mjs', 'Titles, canonical links, social card, JSON-LD, sitemap and feed pass.'],
  ['og', 'Social card matches its generator', 'scripts/check-og.mjs', 'public/og.png is byte-identical to the generator output.'],
  ['orphans', 'No orphan pages', 'scripts/check-orphans.mjs', 'Every page is linked from at least one other page.'],
  ['showcase', 'Showcase data', 'scripts/check-showcase.mjs', 'Every artefact has alt text, a text version and a UTC preparation time.'],
];

const commit = spawnSync('git', ['rev-parse', '--short', 'HEAD'], { encoding: 'utf8' }).stdout.trim() || 'unknown';
const rows = checks.map(([id, label, script, covers]) => {
  const result = spawnSync('node', script.split(' '), { encoding: 'utf8' });
  const lines = `${result.stdout}${result.stderr}`.trim().split('\n').filter(Boolean);
  return {
    id,
    label,
    covers,
    status: result.status === 0 ? 'pass' : 'fail',
    source: script,
    observed: now(),
    detail: lines.find((line) => /\d/.test(line) && !line.startsWith('  ')) ?? lines.at(-1) ?? '',
  };
});
rows.push({
  id: 'axe',
  label: 'Accessibility scan (axe-core, 13 pages, light and dark)',
  covers: 'No automated WCAG 2.2 AA violations on the audited pages.',
  status: 'unknown',
  source: 'not run by npm scripts',
  observed: null,
  detail: 'No automated source feeds this row. Run the browser audit by hand and record the result.',
});

const health = { generated_at: now(), commit, rows };
fs.writeFileSync('src/data/health.json', `${JSON.stringify(health, null, 2)}\n`);
console.log(`health.json: ${rows.filter((r) => r.status === 'pass').length} pass, ${rows.filter((r) => r.status === 'fail').length} fail, ${rows.filter((r) => r.status === 'unknown').length} unknown`);
