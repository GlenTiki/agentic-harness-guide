# The Agentic Harness Guide

A plain-English guide to getting reliable, checkable work from AI assistants, from your first chat to systems of several assistants. Nine short levels teach the ideas. The reference shelf is for engineers and is written against Claude Code, with notes on Codex CLI; the ideas transfer. It is built with [Astro Starlight](https://starlight.astro.build/).

## Develop

```sh
npm ci
npm run dev
```

Build with `npm run build` and preview the output with `npm run preview`.

## Deploy

Pushing to `main` runs `.github/workflows/deploy.yml`, which builds the site and publishes it to GitHub Pages. In the repository settings, set Pages to use "GitHub Actions" as the source. The site is served from `https://glentiki.dev/agentic-harness-guide/`.

## Licence

Content under `src/content` is licensed under CC BY 4.0. Code and configuration are licensed under MIT. See `LICENSE`.
