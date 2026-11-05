import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { chromium } from 'playwright-core';

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'og-'));
let browser;
try {
  const temp = path.join(dir, 'og.png');
  execFileSync(process.execPath, ['scripts/make-og.mjs', temp], { stdio: 'ignore' });
  browser = await chromium.launch({ executablePath: process.env.CHROME_PATH ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: true });
  const page = await browser.newPage();
  const same = await page.evaluate(async (images) => {
    const pixels = await Promise.all(images.map(async (src) => {
      const image = new Image();
      image.src = src;
      await image.decode();
      const canvas = document.createElement('canvas');
      canvas.width = image.width;
      canvas.height = image.height;
      const context = canvas.getContext('2d');
      context.drawImage(image, 0, 0);
      return { width: image.width, height: image.height, data: context.getImageData(0, 0, image.width, image.height).data };
    }));
    const [expected, actual] = pixels;
    return expected.width === actual.width && expected.height === actual.height && expected.data.every((value, i) => value === actual.data[i]);
  }, [temp, process.env.OG_FILE ?? 'public/og.png'].map((file) => `data:image/png;base64,${fs.readFileSync(file).toString('base64')}`));
  console.log(`public/og.png pixels ${same ? 'match' : 'differ from'} scripts/make-og.mjs output`);
  process.exitCode = same ? 0 : 1;
} finally {
  await browser?.close();
  fs.rmSync(dir, { recursive: true, force: true });
}
