import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://glentiki.github.io',
  base: '/agentic-harness-guide',
  integrations: [
    starlight({
      title: 'The Agentic Harness Guide',
      description: 'What to enable in a modern agentic coding harness, and why.',
      customCss: ['./src/styles/custom.css'],
      social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/GlenTiki/agentic-harness-guide' }],
      editLink: { baseUrl: 'https://github.com/GlenTiki/agentic-harness-guide/edit/main/' },
      lastUpdated: false,
      disable404Route: true,
      sidebar: [
        {
          label: 'Start here',
          items: [{ slug: 'start-here/how-to-read' }, { slug: 'glossary' }],
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
          ],
        },
        {
          label: 'Workflows',
          items: [
            { slug: 'workflows' },
            { slug: 'workflows/improve-code' },
            { slug: 'workflows/improve-design' },
            { slug: 'workflows/build-a-budget' },
            { slug: 'workflows/connect-systems' },
            { slug: 'workflows/review-content' },
            { slug: 'workflows/define-a-workflow' },
            { slug: 'workflows/research-a-decision' },
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
            { slug: 'shelf/foundations/glossary' },
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
