import { createRequire } from 'node:module';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright-core');
const dist = path.resolve('dist');
const BASE = '/agentic-harness-guide';
const chrome = process.env.CHROME_PATH ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
if (!fs.existsSync(chrome)) {
  console.error(`check-layout: Chrome not found at ${chrome}. Set CHROME_PATH.`);
  process.exit(1);
}

const WIDTHS = [320, 360, 390, 412, 768];
const SCHEMES = ['light', 'dark'];
const HOME = '/';
const OTHER_PAGES = ['/journey/00-hello-robot/', '/journey/05-check-the-work/', '/setup/relevance-and-reranking/', '/case-study/ch06-rerank/', '/case-study/ch02-hooks/', '/evidence/', '/showcase/'];

const server = http.createServer((req, res) => {
  const url = decodeURIComponent(new URL(req.url, 'http://x').pathname).replace(BASE, '');
  const target = path.join(dist, url.endsWith('/') ? `${url}index.html` : url);
  if (!fs.existsSync(target)) return res.writeHead(404).end();
  const type = target.endsWith('.css') ? 'text/css' : target.endsWith('.js') ? 'text/javascript' : target.endsWith('.html') ? 'text/html' : 'application/octet-stream';
  res.writeHead(200, { 'content-type': type }).end(fs.readFileSync(target));
});
await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;

const browser = await chromium.launch({ executablePath: chrome, headless: true });
const failures = [];
let runs = 0;
for (const scheme of SCHEMES) {
  for (const width of WIDTHS) {
    const context = await browser.newContext({
      viewport: { width, height: 800 },
      deviceScaleFactor: 3,
      isMobile: true,
      hasTouch: true,
      colorScheme: scheme,
    });
    const pages = width === 390 ? [HOME, ...OTHER_PAGES] : [HOME];
    for (const route of pages) {
      const page = await context.newPage();
      await page.goto(`${origin}${BASE}${route}`, { waitUntil: 'load' });
      const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      runs += 1;
      if (scrollWidth > width) failures.push(`${route} at ${width}px ${scheme}: scrollWidth ${scrollWidth}`);
      await page.close();
    }
    await context.close();
  }
}
await browser.close();
server.close();
for (const failure of failures) console.error(`overflow: ${failure}`);
console.log(`layout: ${runs} page loads, ${failures.length} horizontal overflows`);
process.exit(failures.length === 0 ? 0 : 1);
