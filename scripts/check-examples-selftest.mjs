import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { replaceExamples } from './lib/example-parse.mjs';

const good = `---
title: t
---

<Example label="Observed" task="Sam asks for a total." evidence="package.json" env="model, tool, date">

<Fragment slot="input">

\`\`\`text
in
\`\`\`

</Fragment>

<Fragment slot="output">

\`\`\`text
out
\`\`\`

</Fragment>

<Fragment slot="notice">

Look at line one.

</Fragment>

<Fragment slot="shows">

It shows one case, not a rate.

</Fragment>

</Example>
`;

const withoutShows = good.replace(/<Fragment slot="shows">[\s\S]*?<\/Fragment>\n\n/, '');
const mixed = `${good}\n${withoutShows.replace(/^---\ntitle: t\n---\n\n/, '')}`;

const cases = [
  ['good copy passes', good, 0],
  ['missing slot fails', good.replace(/<Fragment slot="notice">[\s\S]*?<\/Fragment>\n\n/, ''), 1],
  ['missing shows slot passes', withoutShows, 0],
  ['empty shows slot fails', good.replace('It shows one case, not a rate.\n', ''), 1],
  ['self-closing shows slot fails', good.replace(/<Fragment slot="shows">[\s\S]*?<\/Fragment>/, '<Fragment slot="shows" />'), 1],
  ['self-closing required slot fails', good.replace(/<Fragment slot="notice">[\s\S]*?<\/Fragment>/, '<Fragment slot="notice" />'), 1],
  ['mixed page passes', mixed, 0],
  ['bad label fails', good.replace('label="Observed"', 'label="Illustrative"'), 1],
  ['dead evidence path fails', good.replace('evidence="package.json"', 'evidence="examples/no-such-file.json"'), 1],
  ['foreign evidence URL fails', good.replace('evidence="package.json"', 'evidence="https://example.com/x"'), 1],
  ['empty task fails', good.replace('task="Sam asks for a total."', 'task=""'), 1],
];

let failed = 0;
for (const [name, text, expected] of cases) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'check-examples-'));
  fs.writeFileSync(path.join(dir, 'page.mdx'), text);
  const result = spawnSync('node', ['scripts/check-examples.mjs', dir], { encoding: 'utf8' });
  const ok = result.status === expected;
  if (!ok) failed += 1;
  console.log(`${ok ? 'ok  ' : 'FAIL'} ${name}: exit ${result.status}, expected ${expected}`);
  fs.rmSync(dir, { recursive: true });
}
for (const [name, text, expected] of [
  ['complete example twin carries shows', good, 1],
  ['example without shows has no empty heading', withoutShows, 0],
  ['mixed page twin carries one shows part', mixed, 1],
]) {
  const twin = replaceExamples(text);
  const found = twin.split('**What it shows.**').length - 1;
  const ok = found === expected && !twin.includes('undefined');
  if (!ok) failed += 1;
  console.log(`${ok ? 'ok  ' : 'FAIL'} ${name}: found ${found}, expected ${expected}`);
}
process.exit(failed ? 1 : 0);
