import assert from 'node:assert/strict';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { chromium } from 'playwright-core';

const base = '/agentic-harness-guide';
const pages = ['why-bother', 'how-to-read', 'consistency-fast-track', 'professional-route', 'engineer-route', 'cheat-sheet', 'what-the-time-is-for'].map((slug) => `start-here/${slug}`);
pages.push(...['engineer-weak-spots', 'product-manager-and-team-lead', 'the-feedback-loop', 'be-the-product-manager-of-your-own-tooling'].map((slug) => `method/${slug}`));
const server = http.createServer((req, res) => {
  const pathname = new URL(req.url, 'http://localhost').pathname.slice(base.length);
  const file = path.join(process.cwd(), 'dist', pathname.endsWith('/') ? `${pathname}index.html` : pathname);
  if (!fs.existsSync(file)) return res.writeHead(404).end();
  const type = file.endsWith('.css') ? 'text/css' : /\.m?js$/.test(file) ? 'text/javascript' : 'text/html';
  res.writeHead(200, { 'content-type': type }).end(fs.readFileSync(file));
});
await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
let browser;
const failures = [];
try {
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await page.goto(`http://127.0.0.1:${server.address().port}${base}/`);
  assert.match(await page.title(), /Judgement First/);
  assert.equal(await page.locator('h1').innerText(), 'Put your judgement in charge of AI.');
  assert.equal(await page.getByRole('link', { name: 'Start with your own task', exact: true }).count(), 1);
  assert.equal(await page.getByRole('link', { name: 'Read Field notes', exact: true }).count(), 1);
  assert.equal(await page.locator('iframe[src*="ko-fi.com"], script[src*="ko-fi.com"]').count(), 0);
  assert.equal(await page.locator('body').evaluate((el) => el.scrollWidth <= window.innerWidth), true);
  for (const route of pages) {
    await page.goto(`http://127.0.0.1:${server.address().port}${base}/${route}/`);
    const links = await page.evaluate(() => {
      const paragraph = [...document.querySelectorAll('.sl-markdown-content p')].find((el) => el.textContent.startsWith('Next:'));
      return [paragraph?.querySelector('a')?.href, document.querySelector('a[rel="next"]')?.href];
    });
    if (!links[0] || links[0] !== links[1]) failures.push(`${route}: recommended Next differs from navigation card`);
    const overlaps = await page.evaluate(() => {
      const article = document.querySelector('.sl-markdown-content').getBoundingClientRect();
      const feedback = document.querySelector('.feedback-button').getBoundingClientRect();
      return feedback.top < article.bottom;
    });
    if (overlaps) failures.push(`${route}: phone Feedback occupies article space`);
  }
  await page.goto(`http://127.0.0.1:${server.address().port}${base}/method/engineer-weak-spots/`);
  const demo = page.locator('[data-diagram="weak-spot-loop"]');
  assert.equal(await demo.locator('figcaption').count(), 1);
  if (!(await demo.innerText()).includes('simulation')) failures.push('weak-spot diagram does not identify its simulation');
  await demo.locator('[data-action="toggle-red"]').click();
  if (!(await demo.innerText()).includes('Example: duplicate detected')) failures.push('weak-spot diagram implies an executed test');
  await page.locator('.feedback-button').focus();
  assert.equal(await page.locator('.feedback-button').evaluate((el) => el === document.activeElement), true);
  const selectedQuote = await page.evaluate(() => {
    const paragraph = document.querySelector('.sl-markdown-content p');
    const range = document.createRange();
    range.selectNodeContents(paragraph);
    const selection = getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    const quote = selection.toString().trim();
    document.querySelector('.feedback-button').dispatchEvent(new PointerEvent('pointerdown'));
    selection.removeAllRanges();
    return quote;
  });
  await page.locator('.feedback-button').click();
  assert.equal(await page.locator('#feedback-modal').evaluate((el) => el.open), true);
  assert.equal(await page.locator('[data-feedback-quote]').isVisible(), true);
  assert.ok((await page.locator('[data-feedback-quote]').innerText()).includes(selectedQuote.slice(0, 160)));
  await page.getByRole('button', { name: 'Close dialog' }).click();
  assert.equal(await page.locator('#feedback-modal').evaluate((el) => el.open), false);
  await page.goto(`http://127.0.0.1:${server.address().port}${base}/evidence/`);
  const filter = page.locator('[data-filter-template="B"]');
  assert.equal(await filter.getAttribute('aria-pressed'), 'false');
  await filter.click();
  assert.equal(await filter.getAttribute('aria-pressed'), 'true');
  assert.equal(await page.locator('[data-filter-template="all"]').getAttribute('aria-pressed'), 'false');
  await page.goto(`http://127.0.0.1:${server.address().port}${base}/journey/06-hire-a-team/`);
  const team = page.locator('[data-diagram="team-orchestrator-flow"]');
  await team.getByRole('button', { name: 'Next simulated step' }).click();
  assert.equal(await team.locator('.tof-log-line').count(), 2);
} finally {
  await browser?.close();
  await new Promise((resolve) => server.close(resolve));
}
for (const failure of failures) console.error(failure);
console.log(`entry flows: ${pages.length} routes, ${failures.length} failures`);
process.exitCode = failures.length ? 1 : 0;
