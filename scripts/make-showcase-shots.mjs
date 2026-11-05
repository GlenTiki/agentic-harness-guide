import crypto from 'node:crypto';
import { createRequire } from 'node:module';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright-core');
const dist = path.resolve('dist');
const BASE = '/agentic-harness-guide';
const chrome = process.env.CHROME_PATH ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const items = JSON.parse(fs.readFileSync('src/data/showcase.json', 'utf8'));

const server = http.createServer((req, res) => {
  const url = decodeURIComponent(new URL(req.url, 'http://x').pathname).replace(BASE, '');
  const target = path.join(dist, url.endsWith('/') ? `${url}index.html` : url);
  if (!fs.existsSync(target)) return res.writeHead(404).end();
  res.writeHead(200).end(fs.readFileSync(target));
});
await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;

const browser = await chromium.launch({ executablePath: chrome, headless: true });
const context = await browser.newContext({ viewport: { width: 1008, height: 800 }, deviceScaleFactor: 1, colorScheme: 'light' });
const stamps = {};
for (const item of [...items, { id: 'hook-timeline', image: 'showcase/hook-timeline.png' }]) {
  const page = await context.newPage();
  await page.goto(`${origin}${BASE}/showcase/render/${item.id}/`, { waitUntil: 'load' });
  const shown = await page.locator('#shot').innerText();
  const stamp = shown.match(/(?:Prepared|Recorded) (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)/)?.[1];
  if (!stamp) throw new Error(`${item.id}: the rendered picture shows no Prepared or Recorded time`);
  await page.locator('#shot').screenshot({ path: path.join('public', item.image) });
  await page.close();
  const png = fs.readFileSync(path.join('public', item.image));
  stamps[item.id] = { image: item.image, stamp, png_sha256: crypto.createHash('sha256').update(png).digest('hex') };
  console.log(`public/${item.image} stamped ${stamp}`);
}
fs.writeFileSync('src/data/showcase-shots.json', `${JSON.stringify(stamps, null, 2)}\n`);
await browser.close();
server.close();
