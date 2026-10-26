import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { findExamples, LABELS } from './lib/example-parse.mjs';
import { countWords, prose } from './lib/prose.mjs';

const SITE_BASE = '/agentic-harness-guide/';
const HEDGES = ['may', 'might', 'usually', 'often', 'probably', 'in my experience'];
const PERSON = [['I', 'I', ''], ['my', 'my', 'i'], ['we', 'we', 'i'], ['you', 'you', 'i']];
const escape = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
// Whole token: a hyphen joins words, so "agent" does not match inside "sub-agent".
const wordPattern = (term, flags = 'giu') => new RegExp(`(?<![\\p{L}\\p{N}_-])${escape(term)}(?![\\p{L}\\p{N}_-])`, flags);
const countOf = (text, term, flags) => (text.match(wordPattern(term, flags)) ?? []).length;

const walk = (dir, out = []) => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, out);
    else if (/\.mdx?$/.test(entry.name)) out.push(full);
  }
  return out;
};

const slugOf = (root, file) => {
  const rel = path.relative(root, file).split(path.sep).join('/').replace(/\.mdx?$/, '');
  return rel === 'index' ? 'index' : rel.replace(/\/index$/, '');
};

const frontMatter = (source) => {
  const block = source.match(/^---\n([\s\S]*?)\n---\n/)?.[1] ?? '';
  const field = (key) => {
    const found = block.match(new RegExp(`^${key}:[ \\t]*(.*(?:\\n[ \\t]+.*)*)`, 'm'))?.[1] ?? '';
    return found.replace(/^[>|][-+]?\s*/, '').replace(/\s*\n\s*/g, ' ').trim().replace(/^(["'])(.*)\1$/, '$2');
  };
  return { title: field('title'), description: field('description') };
};

export const sidebarOrder = (configText) => {
  const order = new Map();
  let group = null;
  for (const line of configText.split('\n')) {
    const label = line.match(/^ {10}label:\s*'([^']+)'/);
    if (label) group = label[1];
    const slug = line.match(/\{\s*slug:\s*'([^']+)'\s*\}/);
    if (slug && !order.has(slug[1])) order.set(slug[1], { group, position: order.size + 1 });
  }
  return order;
};

const glossaryTerms = (root) => {
  const file = ['glossary.mdx', 'glossary.md'].map((name) => path.join(root, name)).find((candidate) => fs.existsSync(candidate));
  if (!file) return [];
  const headings = [...fs.readFileSync(file, 'utf8').matchAll(/^### (.+)$/gm)].map((m) => m[1].replace(/\s*\([^)]*\)\s*$/, '').trim());
  return [...new Set(headings.filter(Boolean))];
};

const hrefsOf = (source) => {
  const text = source.replace(/^```[\s\S]*?^```/gm, ' ');
  const found = [...text.matchAll(/\]\(([^)\s]+)\)/g)].map((m) => m[1]);
  found.push(...[...text.matchAll(/(?:href|link)[=:]\s*"?([^"\s>]+)"?/g)].map((m) => m[1]));
  return found;
};

export const resolveSlug = (fromSlug, href, slugs) => {
  if (/^[a-z][a-z0-9+.-]*:/i.test(href) || href.startsWith('#')) return null;
  const clean = href.split('#')[0].split('?')[0].replace(/\.mdx?$/, '');
  if (!clean) return null;
  const from = fromSlug === 'index' ? '/' : `/${fromSlug}/`;
  const absolute = clean.startsWith('/') ? clean : new URL(clean, `http://x${from}`).pathname;
  const target = absolute.replace(SITE_BASE, '/').replace(/^\/|\/$/g, '') || 'index';
  return slugs.has(target) ? target : null;
};

const countsFor = (text, families) => ({
  first_person: Object.fromEntries(PERSON.map(([word, , flag]) => [word, countOf(text, word, flag ? 'giu' : 'gu')])),
  hedges: Object.fromEntries(HEDGES.map((hedge) => [hedge, countOf(text, hedge)])),
  term_variants: Object.fromEntries(
    Object.entries(families).map(([family, words]) => [
      family,
      Object.fromEntries(Object.entries(words).map(([canonical, variants]) => [canonical, variants.reduce((sum, variant) => sum + countOf(text, variant), 0)])),
    ]),
  ),
});

export const buildFacts = ({ root, configText = '', families, previous = null }) => {
  const files = walk(root).map((file) => ({ file, slug: slugOf(root, file) }));
  const slugs = new Set(files.map((f) => f.slug));
  const sidebar = sidebarOrder(configText);
  const terms = glossaryTerms(root);
  const pages = files.map(({ file, slug }) => {
    const source = fs.readFileSync(file, 'utf8');
    const body = source.replace(/^---\n[\s\S]*?\n---\n/, '');
    const text = prose(source).replace(/`[^`]*`/g, ' ');
    const unfenced = body.replace(/^```[\s\S]*?^```/gm, ' ');
    const next = source.match(/\*\*Next:\*\*\s*\[[^\]]+\]\(([^)]+)\)/)?.[1];
    const out = [...new Set(hrefsOf(source).map((href) => resolveSlug(slug, href, slugs)).filter((s) => s && s !== slug))].sort();
    const side = sidebar.get(slug);
    return {
      slug,
      path: path.relative(process.cwd(), file).split(path.sep).join('/'),
      ...frontMatter(source),
      group: side?.group ?? slug.split('/')[0],
      order: 0,
      sha256: crypto.createHash('sha256').update(source).digest('hex'),
      words: countWords(source),
      headings: [...unfenced.matchAll(/^(#{1,6})\s+(.+?)\s*#*\s*$/gm)].map((m) => ({ level: m[1].length, text: m[2] })),
      next: next ? resolveSlug(slug, next, slugs) : null,
      links_out: out,
      links_in: [],
      example_labels: Object.fromEntries(LABELS.map((label) => [label, findExamples(source).filter((e) => e.attrs.label === label).length])),
      principle_not_measured: {
        'Principle, not measured': (body.match(/Principle, not measured/gi) ?? []).length,
        'My view, not measured': (body.match(/My view, not measured/gi) ?? []).length,
      },
      ...countsFor(text, families),
      glossary_terms_used: slug === 'glossary' ? [] : terms.filter((term) => wordPattern(term).test(text)),
      dirty: null,
      _position: slug === 'index' ? 0 : (side?.position ?? Infinity),
    };
  });
  pages.sort((a, b) => a._position - b._position || a.path.localeCompare(b.path));
  const bySlug = new Map(pages.map((p) => [p.slug, p]));
  pages.forEach((page, index) => {
    page.order = index + 1;
    for (const target of page.links_out) bySlug.get(target).links_in.push(page.slug);
    page.dirty = previous ? previous.get(page.slug) !== page.sha256 : null;
    delete page._position;
  });
  for (const page of pages) page.links_in.sort();
  return pages;
};

const arg = (name) => {
  const at = process.argv.indexOf(name);
  return at === -1 ? null : process.argv[at + 1];
};

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const root = path.resolve(arg('--root') ?? 'src/content/docs');
  const config = arg('--config') ?? 'astro.config.mjs';
  const families = JSON.parse(fs.readFileSync(new URL('./data/term-families.json', import.meta.url), 'utf8'));
  const previousFile = arg('--previous');
  const previous = previousFile
    ? new Map(fs.readFileSync(previousFile, 'utf8').split('\n').filter(Boolean).map((line) => JSON.parse(line)).map((p) => [p.slug, p.sha256]))
    : null;
  const pages = buildFacts({ root, configText: fs.existsSync(config) ? fs.readFileSync(config, 'utf8') : '', families, previous });
  const lines = pages.map((page) => JSON.stringify(page)).join('\n') + '\n';
  const outFile = arg('--out');
  if (outFile) fs.writeFileSync(outFile, lines);
  else process.stdout.write(lines);
  const groups = {};
  for (const page of pages) groups[page.group] = (groups[page.group] ?? 0) + 1;
  const groupText = Object.entries(groups).map(([name, n]) => `${name}=${n}`).join(', ');
  const dirty = previous ? pages.filter((p) => p.dirty).length : 'n/a';
  console.error(`${pages.length} pages, ${pages.reduce((sum, p) => sum + p.words, 0)} words, groups: ${groupText}, dirty: ${dirty}`);
}
