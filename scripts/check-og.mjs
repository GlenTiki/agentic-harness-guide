import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const temp = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'og-')), 'og.png');
execFileSync('node', ['scripts/make-og.mjs', temp], { stdio: 'ignore' });
const same = fs.readFileSync(temp).equals(fs.readFileSync('public/og.png'));
console.log(`public/og.png ${same ? 'matches' : 'differs from'} scripts/make-og.mjs output`);
process.exit(same ? 0 : 1);
