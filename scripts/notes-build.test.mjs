import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { gunzipSync } from 'node:zlib';

const root = path.resolve(import.meta.dirname, '..');
const now = '2026-11-05T00:08:51Z';
const url = 'https://glentiki.dev/agentic-harness-guide/field-notes/';

const filesUnder = (directory) => fs.readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
  const file = path.join(directory, entry.name);
  return entry.isDirectory() ? filesUnder(file) : [file];
});

const fixture = (title, fields) => `---\ntitle: "${title}"\ndescription: "A publication boundary fixture."\n${fields}\n---\n\n${title} body.\n`;

test('built routes, sitemap, search and exports share one publication boundary', { timeout: 120000 }, () => {
  fs.mkdirSync(path.join(root, '.astro'), { recursive: true });
  const directory = fs.mkdtempSync(path.join(root, '.astro', 'field-notes-build-'));
  try {
    fs.cpSync(path.join(root, 'src'), path.join(directory, 'src'), { recursive: true });
    for (const file of ['astro.config.mjs', 'package.json']) fs.copyFileSync(path.join(root, file), path.join(directory, file));
    for (const folder of ['scripts', 'public', 'examples', 'node_modules']) fs.symlinkSync(path.join(root, folder), path.join(directory, folder));
    const guidePage = 'src/content/docs/fixture-new-guide.mdx';
    const baseline = JSON.parse(fs.readFileSync(path.join(directory, 'src/data/page-dates.json'), 'utf8'));
    assert.equal(baseline[guidePage], undefined);
    fs.writeFileSync(path.join(directory, guidePage), '---\ntitle: New Guide fixture\ndescription: A new Guide page absent from the date baseline.\n---\n\nA new Guide page.\n');
    const notes = path.join(directory, 'src/content/notes');
    fs.rmSync(notes, { recursive: true, force: true });
    fs.mkdirSync(notes);
    fs.writeFileSync(path.join(notes, 'published.md'), fixture('PublishedCanary', `publishedAt: "${now}"\ndraft: false`));
    fs.writeFileSync(path.join(notes, 'edited.md'), fixture('EditedCanary', `publishedAt: "2026-11-01T00:00:00Z"\nupdatedAt: "${now}"\ndraft: false`));
    fs.writeFileSync(path.join(notes, 'draft.md'), fixture('DraftCanary', `publishedAt: "2026-11-01T00:00:00Z"\ndraft: true`));
    fs.writeFileSync(path.join(notes, 'default-draft.md'), fixture('DefaultDraftCanary', `publishedAt: "2026-11-01T00:00:00Z"`));
    fs.writeFileSync(path.join(notes, 'future.md'), fixture('FutureCanary', 'publishedAt: "2026-11-05T00:08:52Z"\ndraft: false'));
    const env = { ...process.env, NOTES_BUILD_NOW: now, SUPPORT_URL: 'https://ko-fi.com/example' };
    delete env.GIT_DIR; delete env.GIT_WORK_TREE; delete env.GIT_INDEX_FILE;
    const git = (...args) => {
      const result = spawnSync('git', args, { cwd: directory, env: { ...env, GIT_AUTHOR_DATE: now, GIT_COMMITTER_DATE: now }, encoding: 'utf8' });
      assert.equal(result.status, 0, `${result.stdout}\n${result.stderr}`);
    };
    git('init', '-q');
    git('config', 'commit.gpgsign', 'false');
    git('config', 'core.hooksPath', path.join(directory, '.fixture-hooks'));
    git('config', 'user.name', 'Fixture');
    git('config', 'user.email', 'fixture@example.invalid');
    git('add', 'src/content/docs');
    git('commit', '-qm', 'fixture');
    const build = spawnSync(path.join(root, 'node_modules/.bin/astro'), ['build'], { cwd: directory, env, encoding: 'utf8', timeout: 90000, maxBuffer: 10 * 1024 * 1024 });
    assert.equal(build.status, 0, `${build.stdout}\n${build.stderr}`);
    const dist = path.join(directory, 'dist');
    const read = file => fs.readFileSync(path.join(dist, file), 'utf8');
    for (const id of ['draft', 'default-draft', 'future']) {
      assert.equal(fs.existsSync(path.join(dist, 'field-notes', id)), false, `${id} HTML`);
      assert.equal(fs.existsSync(path.join(dist, 'field-notes', `${id}.md`)), false, `${id} Markdown`);
    }
    for (const file of filesUnder(dist)) {
      const data = fs.readFileSync(file);
      const text = (data[0] === 0x1f && data[1] === 0x8b ? gunzipSync(data) : data).toString('utf8');
      assert.doesNotMatch(text, /DraftCanary|DefaultDraftCanary|FutureCanary/, path.relative(dist, file));
    }
    for (const file of ['field-notes/index.html', 'field-notes.md', 'field-notes/feed.xml']) {
      const content = read(file);
      assert.ok(content.indexOf('PublishedCanary') < content.indexOf('EditedCanary'), file);
      assert.match(content, /EditedCanary/);
    }
    const newGuide = read('fixture-new-guide/index.html');
    assert.match(newGuide, /New Guide fixture/);
    assert.ok(newGuide.includes(`"datePublished":"${now}"`));
    assert.ok(newGuide.includes(`"dateModified":"${now}"`));
    const html = read('field-notes/published/index.html');
    assert.match(html, /"@type":"BlogPosting"/);
    assert.match(html, /href="https:\/\/ko-fi.com\/example"[^>]*>Support this guide on Ko-fi<\/a>/);
    assert.doesNotMatch(html, /(?:script|iframe)[^>]*src="https:\/\/ko-fi.com/);
    assert.ok(html.includes(`href="${url}published/"`));
    assert.ok(html.includes(`href="${url}published.md"`));
    assert.ok(html.includes(`datetime="${now}"`));
    assert.ok(read('field-notes/feed.xml').includes(`<id>${url}published/</id>`));
    assert.ok(read('sitemap-0.xml').includes(`<loc>${url}published/</loc>`));
    const fragments = filesUnder(path.join(dist, 'pagefind/fragment')).map(file => gunzipSync(fs.readFileSync(file)).toString('utf8')).join('\n');
    assert.match(fragments, /PublishedCanary/);
    for (const file of ['feed.xml', 'llms-full.txt', 'agent-rules.txt']) assert.doesNotMatch(read(file), /PublishedCanary|EditedCanary/, file);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});
