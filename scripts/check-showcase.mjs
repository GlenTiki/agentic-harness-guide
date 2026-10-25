import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';

const file = process.argv[2] ?? 'src/data/showcase.json';
const UTC_SECONDS = /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/;
const KINDS = ['tool output', 'eval results', 'recorded run', 'prompt'];
const PROVENANCE = ['guide-owned', 'observed-prompt-not-kept'];
const problems = [];
const items = JSON.parse(fs.readFileSync(file, 'utf8'));
const ids = new Set();

for (const item of items) {
  const at = (message) => problems.push(`${item.id ?? '(no id)'}: ${message}`);
  if (!item.id || ids.has(item.id)) at('id is missing or repeated');
  ids.add(item.id);
  if (!item.title) at('no title');
  if (!KINDS.includes(item.kind)) at(`kind ${item.kind} is not one of ${KINDS}`);
  if (!PROVENANCE.includes(item.provenance)) at(`provenance ${item.provenance} must be one of ${PROVENANCE}`);
  if (!UTC_SECONDS.test(item.preparedAt ?? '')) at('preparedAt is not a UTC time with seconds and Z');
  if (typeof item.imageAlt !== 'string' || item.imageAlt.trim().length < 40) at('imageAlt is missing or shorter than 40 characters');
  else if (item.imageAlt.trim() === item.title) at('imageAlt only repeats the title');
  const image = path.join('public', item.image ?? '');
  if (!item.image || !fs.existsSync(image)) at(`image ${item.image} does not exist (run npm run showcase:shots)`);
  else if (fs.readFileSync(image).subarray(1, 4).toString() !== 'PNG') at('image is not a PNG');
  const text = path.join('src/data', item.textFile ?? '');
  if (!item.textFile || !fs.existsSync(text) || fs.statSync(text).size === 0) at('text version is missing or empty');
  else {
    const body = fs.readFileSync(text, 'utf8');
    if (/\/Users\/|\/home\/[a-z]|[\w.+-]+@[\w-]+\.[a-z]{2,}/i.test(body)) at('text version contains a local path or an email address');
  }
  if (!item.learnMore) at('no learnMore page');
}
const shotsFile = process.argv[3] ?? 'src/data/showcase-shots.json';
const runFile = process.argv[4] ?? 'src/data/runs/hook-sample-run.json';
if (!fs.existsSync(shotsFile)) problems.push(`${shotsFile} is missing (run npm run showcase:shots)`);
else {
  const shots = JSON.parse(fs.readFileSync(shotsFile, 'utf8'));
  const expected = [...items.map((item) => ({ id: item.id, image: item.image, stamp: item.preparedAt })), { id: 'hook-timeline', image: 'showcase/hook-timeline.png', stamp: JSON.parse(fs.readFileSync(runFile, 'utf8')).recorded_at }];
  for (const { id, image, stamp } of expected) {
    const shot = shots[id];
    if (!shot) problems.push(`${id}: no stamp record in ${shotsFile} (run npm run showcase:shots)`);
    else {
      if (shot.stamp !== stamp) problems.push(`${id}: picture is stamped ${shot.stamp} but the data says ${stamp} (run npm run showcase:shots)`);
      const hash = fs.existsSync(path.join('public', image)) ? crypto.createHash('sha256').update(fs.readFileSync(path.join('public', image))).digest('hex') : null;
      if (hash !== shot.png_sha256) problems.push(`${id}: ${image} is not the picture that was stamped (run npm run showcase:shots)`);
    }
  }
}
console.log(`${file}: ${items.length} artefacts, ${problems.length} problems`);
for (const problem of problems) console.log(`  problem: ${problem}`);
process.exit(problems.length ? 1 : 0);
