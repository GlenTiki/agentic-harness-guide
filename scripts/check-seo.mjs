import fs from 'node:fs';
import path from 'node:path';

const dist = path.resolve(process.argv[2] ?? 'dist');
const ORIGIN = 'https://glentiki.dev/agentic-harness-guide/';
const terms = JSON.parse(fs.readFileSync('scripts/data/schema-terms.json', 'utf8')).types;
const problems = [];
const fail = (page, message) => problems.push(`${page}: ${message}`);

const htmlFiles = [];
const walk = (dir) => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory() && entry.name !== 'pagefind' && entry.name !== '_astro') walk(full);
    else if (entry.name === 'index.html') htmlFiles.push(full);
  }
};
walk(dist);

const meta = (html, attr, name) => html.match(new RegExp(`<meta ${attr}="${name}" content="([^"]*)"`))?.[1];
const jsonLdTypes = new Map();
const keywords = new Set(['@context', '@graph', '@type', '@id']);

const checkNode = (page, node) => {
  const type = node['@type'];
  if (!type) return;
  jsonLdTypes.set(type, (jsonLdTypes.get(type) ?? 0) + 1);
  const allowed = terms[type];
  if (!allowed) return fail(page, `JSON-LD type ${type} is not in the checked schema.org set`);
  for (const [key, value] of Object.entries(node)) {
    if (!keywords.has(key) && !allowed.includes(key)) fail(page, `JSON-LD property ${key} is not valid on ${type}`);
    for (const child of Array.isArray(value) ? value : [value]) if (child && typeof child === 'object') checkNode(page, child);
    if (type !== 'Person' && typeof value === 'string' && /^(url|item|image|mainEntityOfPage)$/.test(key) && !value.startsWith(ORIGIN)) fail(page, `JSON-LD ${key} is not under ${ORIGIN}`);
  }
  if (type === 'ListItem' && (!Number.isInteger(node.position) || !node.name || !node.item)) fail(page, 'ListItem needs position, name and item');
  if (type === 'TechArticle' && !(node.headline && node.datePublished && node.dateModified && node.author)) fail(page, 'TechArticle needs headline, dates and author');
  for (const key of ['datePublished', 'dateModified']) {
    if (node[key] !== undefined && !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(node[key])) fail(page, `${key} is not UTC seconds with Z`);
  }
};

for (const file of htmlFiles) {
  const rel = path.relative(dist, file);
  const page = rel === 'index.html' ? 'home' : rel.replace(/\/index\.html$/, '');
  const html = fs.readFileSync(file, 'utf8');
  if (page === '404.html' || rel === '404.html') continue;
  const redirect = html.match(/http-equiv="refresh" content="0;url=([^"]*)"/)?.[1];
  if (redirect !== undefined) {
    if (!/noindex/.test(html) || !redirect.startsWith('/agentic-harness-guide/')) fail(page, `redirect to ${redirect} must be noindex and keep the base path`);
    continue;
  }
  if (/<meta name="robots" content="noindex"/.test(html)) continue;
  const isHome = rel === 'index.html';
  const stub = page === 'shelf/foundations/glossary';
  const title = html.match(/<title>([^<]*)<\/title>/)?.[1] ?? '';
  if (title.length > 65) fail(page, `title is ${title.length} characters, limit is 65`);
  const halves = title.split(' | ');
  if (halves.length === 2 && halves[0] === halves[1]) fail(page, 'title repeats the site name');
  const canonical = html.match(/<link rel="canonical" href="([^"]*)"/)?.[1];
  if (!canonical?.startsWith(ORIGIN)) fail(page, `canonical is ${canonical}`);
  if (!stub && canonical !== meta(html, 'property', 'og:url')) fail(page, 'canonical and og:url differ');
  const expectedType = isHome ? 'website' : 'article';
  if (meta(html, 'property', 'og:type') !== expectedType) fail(page, `og:type is ${meta(html, 'property', 'og:type')}, expected ${expectedType}`);
  for (const [attr, name] of [['property', 'og:image'], ['property', 'og:image:alt'], ['name', 'twitter:image'], ['name', 'twitter:image:alt']]) {
    if (!meta(html, attr, name)) fail(page, `missing ${name}`);
  }
  if (meta(html, 'property', 'og:image:width') !== '1200' || meta(html, 'property', 'og:image:height') !== '630') fail(page, 'og:image size is not declared as 1200x630');
  if (!/<link rel="alternate" type="text\/markdown" href="[^"]+\.md"/.test(html)) fail(page, 'no markdown alternate link');
  if (!stub) {
    const blocks = [...html.matchAll(/<script type="application\/ld\+json">([^<]*)<\/script>/g)];
    if (blocks.length !== 1) fail(page, `expected one JSON-LD block, found ${blocks.length}`);
    for (const block of blocks) {
      try {
        const data = JSON.parse(block[1]);
        const graph = data['@graph'] ?? [data];
        if (data['@context'] !== 'https://schema.org') fail(page, 'JSON-LD context is not https://schema.org');
        graph.forEach((node) => checkNode(page, node));
        const types = graph.map((node) => node['@type']);
        if (isHome && !types.includes('WebSite')) fail(page, 'home has no WebSite');
        if (!isHome && !types.includes('BreadcrumbList')) fail(page, 'no BreadcrumbList');
        if (page === 'journey' && !types.includes('LearningResource')) fail(page, 'journey has no LearningResource');
        if (!isHome && page !== 'journey' && !types.includes('TechArticle')) fail(page, 'no TechArticle');
      } catch (error) {
        fail(page, `JSON-LD does not parse: ${error.message}`);
      }
    }
  }
}

const ogPath = path.join(dist, 'og.png');
if (!fs.existsSync(ogPath)) fail('og.png', 'missing');
else {
  const png = fs.readFileSync(ogPath);
  if (png.readUInt32BE(16) !== 1200 || png.readUInt32BE(20) !== 630) fail('og.png', `size is ${png.readUInt32BE(16)}x${png.readUInt32BE(20)}`);
}

const sitemap = fs.readFileSync(path.join(dist, 'sitemap-0.xml'), 'utf8');
const urls = [...sitemap.matchAll(/<url>([\s\S]*?)<\/url>/g)].map((m) => m[1]);
if (urls.some((u) => !/<lastmod>/.test(u))) fail('sitemap', 'a URL has no lastmod');
if (/shelf\/foundations\/glossary/.test(sitemap)) fail('sitemap', 'the hidden glossary stub is listed');
if (/\/404/.test(sitemap)) fail('sitemap', '404 is listed');

const feed = fs.readFileSync(path.join(dist, 'feed.xml'), 'utf8');
if (!/<feed xmlns="http:\/\/www.w3.org\/2005\/Atom">/.test(feed) || !/<entry>/.test(feed)) fail('feed.xml', 'not an Atom feed with entries');
if (/<updated>(?!\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)/.test(feed)) fail('feed.xml', 'updated is not UTC seconds with Z');

console.log(`${htmlFiles.length} pages, ${urls.length} sitemap URLs, JSON-LD types: ${[...jsonLdTypes].map(([k, v]) => `${k} x${v}`).join(', ')}, ${problems.length} problems`);
for (const problem of problems) console.log(`  problem: ${problem}`);
process.exit(problems.length ? 1 : 0);
