import fs from 'node:fs';
import path from 'node:path';
import { buildFeedbackUrl, FEEDBACK_REPO, FEEDBACK_TEMPLATE, MAX_URL_LENGTH, PREFILLED_FIELDS, READER_FIELDS } from '../public/feedback-url.mjs';

const dist = path.resolve(process.env.DIST ?? 'dist');
const templatePath = path.resolve(process.env.FEEDBACK_TEMPLATE_PATH ?? `.github/ISSUE_TEMPLATE/${FEEDBACK_TEMPLATE}`);
const problems = [];

const htmlFiles = [];
const walk = (dir) => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (/\.html$/.test(entry.name)) htmlFiles.push(full);
  }
};
walk(dist);

const issueBase = `https://github.com/${FEEDBACK_REPO}/issues/new?template=${FEEDBACK_TEMPLATE}`;
const escaped = issueBase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const hasFloatingButton = (html) => new RegExp(`<a[^>]*class="feedback-button[^"]*"[^>]*href="${escaped}[^"]*"`).test(html) || new RegExp(`<a[^>]*href="${escaped}[^"]*"[^>]*class="feedback-button`).test(html);
const hasFooterLink = (html) => new RegExp(`<a[^>]*href="${escaped}[^"]*"[^>]*data-feedback[^>]*>Send feedback</a>`).test(html);
for (const file of htmlFiles) {
  const rel = path.relative(dist, file);
  const html = fs.readFileSync(file, 'utf8');
  if (rel.startsWith(`showcase${path.sep}render${path.sep}`)) continue;
  if (/http-equiv="refresh"/i.test(html)) continue;
  if (!hasFloatingButton(html)) problems.push(`${rel}: no Feedback button with ${issueBase}`);
  else if (!hasFooterLink(html)) problems.push(`${rel}: no footer Send feedback link`);
  if (/mailto:/i.test(html)) problems.push(`${rel}: contains mailto:`);
  if (/[\w.+-]+@[\w-]+\.[\w.-]+/.test(html.replace(/@(?:astro|type|media|keyframes|font-face|import|layer|supports|container|charset|property|[a-z]+-[a-z]+)\b[^<>"]*/gi, ''))) {
    const match = html.match(/[\w.+-]+@[\w-]+\.[\w.-]+/)?.[0];
    if (match && !/\.(?:woff2?|css|js|mjs|png|svg|jpe?g|webp)$/.test(match)) problems.push(`${rel}: email-shaped string ${match}`);
  }
}

if (!fs.existsSync(templatePath)) problems.push(`missing issue template ${path.relative(process.cwd(), templatePath)}`);
else {
  const template = fs.readFileSync(templatePath, 'utf8');
  const ids = [...template.matchAll(/^\s+id:\s*(\w+)\s*$/gm)].map((m) => m[1]);
  const expected = [...READER_FIELDS, ...PREFILLED_FIELDS].sort().join(',');
  if ([...ids].sort().join(',') !== expected) problems.push(`template field ids [${ids.join(', ')}] differ from the component fields [${expected}]`);
  if (!/labels:\s*\[\s*'?feedback'?\s*\]/.test(template)) problems.push('template does not apply the feedback label');
  if (!/title:\s*'Feedback: '/.test(template)) problems.push("template title prefix is not 'Feedback: '");
  if (!/blank_issues_enabled:\s*false/.test(fs.readFileSync(path.join(path.dirname(templatePath), 'config.yml'), 'utf8'))) problems.push('config.yml does not disable blank issues');
  if (!/public/i.test(template)) problems.push('template does not say that issues are public');
  const url = buildFeedbackUrl({ page: `/agentic-harness-guide/${'p'.repeat(2000)}/`, section: 'h'.repeat(500), quote: '中&<>"'.repeat(300), device: 'd'.repeat(500) });
  if (url.length > MAX_URL_LENGTH || url.length >= 2000) problems.push(`worst-case URL is ${url.length} characters`);
  for (const key of new URL(url).searchParams.keys()) if (key !== 'template' && !ids.includes(key)) problems.push(`URL sets ${key}, which is not a template field id`);
}

if (problems.length) {
  console.error(problems.join('\n'));
  process.exit(1);
}
console.log(`feedback: ${htmlFiles.length} pages checked`);
