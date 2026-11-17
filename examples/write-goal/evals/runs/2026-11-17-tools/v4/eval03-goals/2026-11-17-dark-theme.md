---
goal: Add a dark theme to the settings page
status: not-started
branch: feat/dark-theme
base_sha: 464daa129a6f4aaba51db5ec9db748dd36e63c9c
created_at: 2026-11-17T10:02:01Z
---

# Goal: dark theme on the settings page

Done means every item below passes with its evidence shown.
Progress log: goals/2026-11-17-dark-theme.progress.md

## Done list
- D1: The settings page has a theme switch. Evidence: `npm test -- settings` exits 0 and prints "theme switch renders". Reviewer: none.
- D2: The choice survives a reload. Evidence: `npm test -- persist` exits 0 and prints "theme persists". Reviewer: none.
- D3: A person checks contrast in both themes. Evidence: a comment from the user on the pull request that says "contrast ok" (`gh pr view <PR> --comments` shows it). Reviewer: person.
- Out of scope: other pages.

## Slices
| id | outcome | paths | proof | rollback (only if baseline clean) |
|----|---------|-------|-------|------------------------------------|
| ws-001 | Theme switch renders on the settings page | src/settings/Theme.jsx, [NEEDED: test file path for "settings"] | D1 command and output | `git restore --staged --worktree --source=<last known good sha> -- <paths>` |
| ws-002 | Theme choice persists across reload | src/settings/store.js, [NEEDED: test file path for "persist"] | D2 command and output | same form, paths of this slice |
| ws-003 | Contrast check by a person | none | D3 | Stop and ask the user. Do not continue this slice without a yes. |

## Recovery
Run on the first turn and on every resume.
1. Read this file and the progress log.
2. Run `git status --short`, `git log --oneline -10` and `git worktree list`.
3. Find the last `[ws-NNN]` commit. It is the last known good point.
4. If a slice was interrupted, run its proof on the current files. If it passes, commit the slice. If it fails, log the failure and read the slice baseline in the progress log.
5. If a slice path had staged or unstaged changes in the baseline, or there is no baseline, stop and ask the user. Otherwise run `git restore --staged --worktree --source=<last known good sha> -- <slice paths>` and delete only the new files the baseline shows the slice created.
6. Remove a helper worktree only if the progress log shows this goal created it and the helper has finished. Commit partial work to a salvage branch first.
7. Never run a command that resets, cleans or checks out the whole working copy.

## Assumptions and open items
- Base commit is 464daa1 (HEAD of feat/dark-theme). The prompt said 3c9e0f2, which is not in this repository.
- The repo has no tests, no test runner config and no dependencies (`package.json` only has `"test": "node --test"`). The D1 and D2 commands depend on test files that do not exist yet. [NEEDED: how tests load `.jsx`, since plain `node --test` cannot import it, and where the test files live.]
- A pull request does not exist yet. [NEEDED: PR number for D3.] Opening one is the user's decision, handled in ws-003.
