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
      sidebar: [
        {
          label: 'Foundations',
          items: [
            { slug: 'foundations/principles' },
            { slug: 'foundations/adoption-path' },
            { slug: 'foundations/glossary' },
          ],
        },
        {
          label: 'Instructions and context',
          items: [
            { slug: 'context/instruction-files' },
            { slug: 'context/context-management' },
            { slug: 'context/memory' },
          ],
        },
        {
          label: 'Control',
          items: [
            { slug: 'control/hooks' },
            { slug: 'control/permissions-and-sandboxing' },
            { slug: 'control/capability-gating' },
            { slug: 'control/untrusted-input' },
          ],
        },
        {
          label: 'Delegation',
          items: [
            { slug: 'delegation/sub-agents' },
            { slug: 'delegation/worktree-isolation' },
            { slug: 'delegation/skills' },
            { slug: 'delegation/mcp-servers' },
          ],
        },
        {
          label: 'Quality',
          items: [
            { slug: 'quality/spec-driven-development' },
            { slug: 'quality/test-first-and-gates' },
            { slug: 'quality/independent-review' },
            { slug: 'quality/evals' },
            { slug: 'quality/small-prs' },
          ],
        },
        {
          label: 'Operations',
          items: [
            { slug: 'operations/observability' },
            { slug: 'operations/cost-and-resources' },
            { slug: 'operations/human-in-the-loop' },
          ],
        },
        {
          label: 'Reference',
          items: [
            { slug: 'reference/baseline' },
            { slug: 'reference/anti-patterns' },
          ],
        },
      ],
    }),
  ],
});
