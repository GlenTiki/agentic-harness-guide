# Judgement First: A guide to working with AI

Set the task, check the work and decide when an AI assistant is worth using. The Guide teaches practical habits; Field notes records dated lessons and corrections. Nine short levels develop the ideas. The reference shelf is for engineers and is written against Claude Code, with notes on Codex CLI; the ideas transfer. It is built with [Astro Starlight](https://starlight.astro.build/).

## Develop

```sh
npm ci
npm run dev
```

Build with `npm run build` and preview the output with `npm run preview`.

The build needs Node 22.23.4 or later, the minimum for Astro 7.

## Check

`npm run check` builds the site and then runs every `check:*` gate in `package.json`. The `check:claims` gate runs three example tests with `python3`. The `check:layout` gate drives Google Chrome; set `CHROME_PATH` if Chrome is not at `/Applications/Google Chrome.app`. Pull requests and deployment builds run these gates too. Run them locally before you push.

## Field notes

Add Markdown under `src/content/notes/` with `title`, `description`, a UTC `publishedAt` timestamp (seconds and `Z`), and `draft: false` when ready. Optional `updatedAt` must be no earlier than publication and no later than the build. Draft defaults to true; future publication requires a later build. The filename sets the stable URL. Edits do not move a note above newer publications.

Draft filtering hides built pages, not source committed to this public repository. Keep private or unapproved material outside the repository. Notes use `/field-notes/feed.xml`; `/feed.xml` retains Guide changes.

## Page dates and history migration

Builds use complete Git history. Shallow checkouts and histories with multiple roots fail explicitly. `src/data/page-dates.json` preserves publication and modification dates across a root squash. It contains only page paths and UTC dates.

Before a squash or source archive export:

1. Commit all Guide page changes.
2. Run `node scripts/record-page-dates.mjs` and commit the manifest.
3. Compare page metadata, feed dates and sitemap dates before and after the history migration.

Known pages keep their original publication date. Their baseline modification date applies only when their latest file commit is the parentless root. Later edits, including a revert to earlier content, use the actual commit date. New pages use their own history. A path rename requires migrating its baseline entry to preserve the original publication date.

An archive without `.git` uses the manifest. A page missing from the manifest fails explicitly; refresh the manifest before exporting new pages. Refresh it after page edits too, because archives cannot detect later commits. An archive inside another repository does not borrow that repository's history.

Run `node --test scripts/git-dates.test.mjs` to check the migration cases. The generator accepts an optional repository root argument for an isolated checkout.

## Deploy

Pushing to `main` runs `.github/workflows/deploy.yml`, which checks the site and publishes it to GitHub Pages. In the repository settings, set Pages to use "GitHub Actions" as the source. The site is served from `https://glentiki.dev/agentic-harness-guide/`.

## Support link

Set the GitHub repository variable `SUPPORT_URL` to your public HTTPS profile on `ko-fi.com` to show a footer link after the next deployment. Local builds accept the same environment variable. Leave it unset to hide the link. The site embeds no payment scripts.

## Licence

Content under `src/content` is licensed under CC BY 4.0. Code and configuration are licensed under MIT. See `LICENSE`.
