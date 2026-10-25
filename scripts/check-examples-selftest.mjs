import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

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

const cases = [
  ['good copy passes', good, 0],
  ['missing slot fails', good.replace(/<Fragment slot="notice">[\s\S]*?<\/Fragment>\n\n/, ''), 1],
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
process.exit(failed ? 1 : 0);
