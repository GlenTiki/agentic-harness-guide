import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import fs from 'node:fs';
import sitemap from '@astrojs/sitemap';
import { satteri } from '@astrojs/markdown-satteri';
import { lastCommitDate, sourceFileFor } from './scripts/lib/git-dates.mjs';
import { agentNoteFoldPlugin } from './scripts/rehype/agent-note-fold.mjs';
import { taskListLabelsPlugin } from './scripts/rehype/task-list-labels.mjs';
import { tableRegionPlugin } from './scripts/rehype/table-region.mjs';

const reviewedAt = JSON.parse(fs.readFileSync('src/data/review.json', 'utf8')).lastReviewed;
const SITE_BASE = '/agentic-harness-guide/';
const NOT_INDEXED = ['/shelf/foundations/glossary/', '/404', '/showcase/render/'];

export default defineConfig({
  site: 'https://glentiki.dev',
  base: '/agentic-harness-guide',
  redirects: { '/shelf/foundations/glossary': '/agentic-harness-guide/glossary/' },
  markdown: { processor: satteri({ hastPlugins: [tableRegionPlugin, taskListLabelsPlugin, agentNoteFoldPlugin] }) },
  integrations: [
    sitemap({
      filter: (url) => !NOT_INDEXED.some((path) => url.includes(path)),
      serialize(item) {
        const id = decodeURI(new URL(item.url).pathname).replace(SITE_BASE, '').replace(/\/$/, '') || 'index';
        const source = sourceFileFor(id === 'index' ? 'index' : id);
        const lastmod = (source ? lastCommitDate(source) : null) ?? (source ? null : reviewedAt);
        return lastmod ? { ...item, lastmod } : item;
      },
    }),
    starlight({
      title: 'The Agentic Harness Guide',
      description: 'A plain-English guide to getting reliable, checkable work from AI assistants, from your first chat to systems of several assistants.',
      customCss: ['./src/styles/tokens.css', './src/styles/custom.css'],
      social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/GlenTiki/agentic-harness-guide' }],
      editLink: { baseUrl: 'https://github.com/GlenTiki/agentic-harness-guide/edit/main/' },
      head: [
        {
          tag: 'script',
          content:
            "addEventListener('load',()=>{const b=document.querySelector('site-search button[data-open-modal]');const k=b&&b.querySelector('kbd');if(k&&getComputedStyle(k).display!=='none')b.setAttribute('aria-label',b.getAttribute('aria-label')+' '+k.textContent.trim())})",
        },
      ],
      lastUpdated: false,
      disable404Route: true,
      routeMiddleware: './src/routeData.ts',
      components: {
        Footer: './src/components/Footer.astro',
        Hero: './src/components/Hero.astro',
        PageTitle: './src/components/PageTitle.astro',
      },
      sidebar: [
        {
          label: 'Start here',
          items: [
            { slug: 'start-here/how-to-read' },
            { slug: 'start-here/consistency-fast-track' },
            { slug: 'start-here/professional-route' },
            { slug: 'start-here/engineer-route' },
            { slug: 'start-here/cheat-sheet' },
            { slug: 'glossary' },
          ],
        },
        {
          label: 'The journey',
          items: [
            { slug: 'journey' },
            { slug: 'journey/00-hello-robot' },
            { slug: 'journey/01-say-it-properly' },
            { slug: 'journey/02-house-rules' },
            { slug: 'journey/03-give-it-hands' },
            { slug: 'journey/04-trust-but-verify' },
            { slug: 'journey/05-check-the-work' },
            { slug: 'journey/06-hire-a-team' },
            { slug: 'journey/07-run-it-for-real' },
            { slug: 'journey/08-design-anything' },
            {
              label: 'Beyond the levels',
              items: [
                { slug: 'journey/progress' },
                { slug: 'journey/professional-guardrails' },
                { slug: 'journey/why-it-sounds-sure' },
              ],
            },
          ],
        },
        {
          label: 'The method',
          items: [
            { slug: 'method/engineer-weak-spots' },
            { slug: 'method/product-manager-and-team-lead' },
            { slug: 'method/the-feedback-loop' },
          ],
        },
        {
          label: 'The setup',
          items: [
            { slug: 'setup' },
            { slug: 'setup/hooks' },
            { slug: 'setup/plain-text-and-simple-english' },
            { slug: 'setup/link-and-reference-checks' },
            { slug: 'setup/memory' },
            { slug: 'setup/relevance-and-reranking' },
            { slug: 'setup/orchestrator-and-subagents' },
            { slug: 'setup/personas' },
            { slug: 'setup/retros' },
            { slug: 'setup/monitor-and-showcase' },
            { slug: 'setup/fast-feedback-and-alerts' },
            { slug: 'setup/connecting-surfaces' },
            { slug: 'setup/local-models' },
            { slug: 'setup/end-to-end-flows' },
          ],
        },
        {
          label: 'Case study',
          items: [
            { slug: 'case-study' },
            { slug: 'case-study/ch00-baseline' },
            { slug: 'case-study/ch01-plain-spec' },
            { slug: 'case-study/ch02-hooks' },
            { slug: 'case-study/ch03-link-resolver' },
            { slug: 'case-study/ch04-reference-walker' },
            { slug: 'case-study/ch05-memory' },
            { slug: 'case-study/ch06-rerank' },
            { slug: 'case-study/ch07-orchestrator' },
            { slug: 'case-study/ch08-personas' },
            { slug: 'case-study/ch09-retro' },
            { slug: 'case-study/ch10-monitor' },
            { slug: 'case-study/ch11-surfaces' },
            { slug: 'case-study/ch12-local-models' },
          ],
        },
        {
          label: 'Evidence',
          items: [{ slug: 'evidence' }],
        },
        {
          label: 'Workflows',
          collapsed: true,
          items: [
            { slug: 'workflows' },
            { slug: 'workflows/build-a-budget' },
            { slug: 'workflows/spreadsheet-monday' },
            { slug: 'workflows/review-content' },
            { slug: 'workflows/improve-code' },
            { slug: 'workflows/improve-design' },
            { slug: 'workflows/connect-systems' },
            { slug: 'workflows/small-shop-month-end' },
            { slug: 'workflows/define-a-workflow' },
            { slug: 'workflows/research-a-decision' },
            { slug: 'workflows/design-reps' },
          ],
        },
        {
          label: 'Appendix: the prompt refiner',
          items: [
            { slug: 'appendix/prompt-refiner' },
            { slug: 'appendix/prompt-refiner-line-by-line' },
          ],
        },
        {
          label: 'Reference shelf',
          collapsed: true,
          items: [
        {
          label: 'Foundations',
          items: [
            { slug: 'shelf/foundations/principles' },
            { slug: 'shelf/foundations/adoption-path' },
          ],
        },
        {
          label: 'Instructions and context',
          items: [
            { slug: 'shelf/context/instruction-files' },
            { slug: 'shelf/context/context-management' },
            { slug: 'shelf/context/memory' },
          ],
        },
        {
          label: 'Control',
          items: [
            { slug: 'shelf/control/hooks' },
            { slug: 'shelf/control/permissions-and-sandboxing' },
            { slug: 'shelf/control/capability-gating' },
            { slug: 'shelf/control/removing-personal-data' },
            { slug: 'shelf/control/untrusted-input' },
          ],
        },
        {
          label: 'Delegation',
          items: [
            { slug: 'shelf/delegation/sub-agents' },
            { slug: 'shelf/delegation/worktree-isolation' },
            { slug: 'shelf/delegation/skills' },
            { slug: 'shelf/delegation/mcp-servers' },
          ],
        },
        {
          label: 'Quality',
          items: [
            { slug: 'shelf/quality/spec-driven-development' },
            { slug: 'shelf/quality/test-first-and-gates' },
            { slug: 'shelf/quality/independent-review' },
            { slug: 'shelf/quality/evals' },
            { slug: 'shelf/quality/small-prs' },
          ],
        },
        {
          label: 'Operations',
          items: [
            { slug: 'shelf/operations/observability' },
            { slug: 'shelf/operations/cost-and-resources' },
            { slug: 'shelf/operations/human-in-the-loop' },
          ],
        },
        {
          label: 'Reference',
          items: [
            { slug: 'shelf/reference/baseline' },
            { slug: 'shelf/reference/anti-patterns' },
          ],
        },
          ],
        },
      ],
    }),
  ],
});
