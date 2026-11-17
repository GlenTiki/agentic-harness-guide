---
goal: Add a dark theme to the settings page
status: not started
branch: feat/dark-theme
base_sha: 009167ab8dc4399f6aa7edeec00bddd37246bbfc
created_at: 2026-11-17T00:00:00Z
---

# Objective
Add a dark theme to the settings page. Out of scope: other pages.

# Done list
- D1: The settings page has a theme switch. Evidence: `npm test -- settings` exits 0 and prints `theme switch renders`. Reviewer: none.
- D2: The choice survives a reload. Evidence: `npm test -- persist` exits 0 and prints `theme persists`. Reviewer: none.
- D3: A person checks contrast in both themes. Evidence: `gh pr view <PR number> --comments` shows a comment from the user that says `contrast ok`. Reviewer: person (the user).

# Slices
| id | outcome | paths | proof | rollback |
|----|---------|-------|-------|----------|
| ws-000 | commit this anchor and the progress log | goals/ | `git log --oneline -1` shows `[ws-000]` | `git rm --cached -r -- goals/` |
| ws-001 | theme switch renders | src/settings/Theme.jsx, plus a new test file [NEEDED: exact test path] | D1 command | `git restore --source=<sha before ws-001> -- src/settings/Theme.jsx`, delete the new test file |
| ws-002 | choice persists | src/settings/store.js, plus a new test file [NEEDED: exact test path] | D2 command | `git restore --source=<sha before ws-002> -- src/settings/store.js`, delete the new test file |
| ws-003 | contrast check (D3) | none | D3 command | none |

# Recovery
1. Read this file and goals/2026-11-17-dark-theme.progress.md.
2. Run `git status --short`, `git log --oneline -10`, `git worktree list`.
3. The last `[ws-NNN]` commit subject is the last known good point.
4. Interrupted slice: run its proof. Pass -> commit. Fail -> log it, `git restore --source=<last good sha> -- <slice paths>`, delete only files that slice created.
5. Leftover helper worktree: commit partial work to a salvage branch, remove only that worktree.
6. Never reset, clean or checkout the whole working copy.

# Assumptions
- Base commit is 009167a (HEAD of feat/dark-theme). The earlier 3c9e0f2 does not exist in this repository.
- The repo has no tests, no test config and no JSX toolchain (`package.json` only has `"test": "node --test"`). The tests are new work in ws-001 and ws-002.
- How a "reload" is simulated in the ws-002 test is a technical choice for the session to record in the progress log.
