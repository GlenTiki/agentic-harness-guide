---
goal: Add a dark theme to the settings page
status: not started
branch: feat/dark-theme
base_sha: b5d8f2e4af9c18f0df393f69a78979c5cd8e6369
created_at: 2026-11-17T01:40:10Z
---

# Dark theme on the settings page

Progress log: goals/2026-11-17-dark-theme.progress.md

## Objective

Add a dark theme to the settings page. Done means every item below passes with its evidence shown.

## Done list

Tick an item only after you have run its check and the output is in the session.

- D1: The settings page has a theme switch. Evidence: `npm test -- settings` exits 0 and prints "theme switch renders". Reviewer: none.
- D2: The choice survives a reload. Evidence: `npm test -- persist` exits 0 and prints "theme persists". Reviewer: none.
- D3: A person checks contrast in both themes. Evidence: a comment from the user on the pull request that says "contrast ok". Reviewer: person.
- Out of scope: other pages.

## Slices

| id | outcome | paths | proof | rollback |
|----|---------|-------|-------|----------|
| ws-001 | The settings page has a theme switch | src/settings/Theme.jsx | D1 | `git restore --source=<last known good sha> -- src/settings/Theme.jsx` |
| ws-002 | The theme choice persists across reloads | src/settings/store.js | D2 | `git restore --source=<last known good sha> -- src/settings/store.js` |
| ws-003 | Contrast check by a person | none | D3 | none. Stop and ask the user for the contrast check. Do not continue this slice without a yes. |

Commit each slice when its proof passes, with the slice id in the subject, for example `feat: [ws-001] add the theme switch`. Append one entry to the progress log after each slice: time, slice id, commit, proof output, next slice.

## Recovery (run on the first turn and on every resume)

1. Read this anchor and goals/2026-11-17-dark-theme.progress.md.
2. Run `git status --short`, `git log --oneline -10` and `git worktree list`.
3. Find the last `[ws-NNN]` commit. That commit is the last known good point. If there is none, it is the base commit b5d8f2e.
4. If a slice was interrupted, rerun its proof. If it passes, commit the slice. If it fails, log the failure, then restore only that slice's paths with `git restore --source=<sha> -- <paths>`.
5. Never run a command that resets, cleans or checks out the whole working copy.

## Assumptions

- The base commit is b5d8f2e. The prompt gave 3c9e0f2, which does not exist in this repository.
- The test files for D1 and D2 do not exist yet. [NEEDED: which file paths hold them, and how `npm test -- settings` selects them, since `package.json` runs `node --test`.]
- Status card on every stop: Done and proved / Last known good / Next or blocked on / Resume "Resume goals/2026-11-17-dark-theme.md at <slice id>."
