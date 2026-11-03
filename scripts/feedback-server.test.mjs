import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { mkdtemp, mkdir, copyFile, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { once } from 'node:events';

test('receiver refuses cross-origin and non-JSON writes', async () => {
  const dir = await mkdtemp(path.join(tmpdir(), 'feedback-test-'));
  await mkdir(path.join(dir, 'scripts'));
  await mkdir(path.join(dir, 'public'));
  await copyFile('scripts/feedback-server.mjs', path.join(dir, 'scripts/feedback-server.mjs'));
  await copyFile('public/feedback-url.mjs', path.join(dir, 'public/feedback-url.mjs'));
  const child = spawn(process.execPath, [path.join(dir, 'scripts/feedback-server.mjs')], { env: { ...process.env, FEEDBACK_HOST: '127.0.0.1', FEEDBACK_PORT: '0' } });
  try {
    const listening = await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('receiver did not start')), 5000);
      child.once('exit', (code) => { clearTimeout(timer); reject(new Error(`receiver exited ${code}`)); });
      child.once('error', (error) => { clearTimeout(timer); reject(error); });
      child.stdout.on('data', (chunk) => {
        const match = chunk.toString().match(/listening at (http:\/\/127\.0\.0\.1:\d+)/);
        if (match) { clearTimeout(timer); resolve(match[1]); }
      });
    });
    const url = `${listening}/api/feedback`;
    const send = (origin, type) => fetch(url, { method: 'POST', headers: { origin, 'content-type': type }, body: JSON.stringify({ feedback: 'test' }) });
    assert.equal((await send('https://evil.example', 'application/json')).status, 403);
    assert.equal((await send('http://localhost:4321', 'text/plain')).status, 415);
    assert.equal((await send('http://localhost:4321', 'application/json')).status, 201);
    const lines = (await readFile(path.join(dir, 'data/feedback-inbox.jsonl'), 'utf8')).trim().split('\n');
    assert.equal(lines.length, 1);
  } finally {
    if (child.exitCode === null && child.signalCode === null) {
      const exited = once(child, 'exit');
      child.kill();
      await exited;
    }
    await rm(dir, { recursive: true, force: true });
  }
});
