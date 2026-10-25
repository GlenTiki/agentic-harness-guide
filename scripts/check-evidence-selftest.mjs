import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const source = 'examples/wrong-behaviour/results.json';
const rows = JSON.parse(fs.readFileSync(source, 'utf8'));
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'check-evidence-'));
const edited = path.join(dir, 'results.json');
rows[0].pass += 1;
fs.writeFileSync(edited, JSON.stringify(rows));
const run = (results) => spawnSync('node', ['scripts/make-evidence.mjs', '--check', '--results', results], { encoding: 'utf8' }).status;
const fresh = run(source);
const stale = run(edited);
fs.rmSync(dir, { recursive: true });
console.log(`self-test: edited results exit ${stale} (must be 1), real results exit ${fresh} (must be 0)`);
process.exit(stale === 1 && fresh === 0 ? 0 : 1);
