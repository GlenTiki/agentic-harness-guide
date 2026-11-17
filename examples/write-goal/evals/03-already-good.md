# Eval 3: a goal that is already good

## Input

```text
Sharpen this /goal if it needs it.

/goal Add a dark theme to the settings page. Done means every item in goals/2026-11-17-dark-theme.md passes with its evidence shown.

Anchor: goals/2026-11-17-dark-theme.md. Branch: feat/dark-theme. Base commit: 3c9e0f2.
D1: The settings page has a theme switch. Evidence: `npm test -- settings` exits 0 and prints "theme switch renders". Reviewer: none.
D2: The choice survives a reload. Evidence: `npm test -- persist` exits 0 and prints "theme persists". Reviewer: none.
D3: A person checks contrast in both themes. Evidence: a comment from the user on the pull request that says "contrast ok". Reviewer: person.
Out of scope: other pages.
Recovery: read the anchor and goals/2026-11-17-dark-theme.progress.md, run git status --short, git log --oneline -10 and git worktree list, find the last [ws-NNN] commit, rerun an interrupted slice's proof, and restore only that slice's paths with git restore --source=<sha> -- <paths> if it fails. Never reset the whole working copy.
Slices: ws-001 switch (src/settings/Theme.jsx, proof D1), ws-002 persistence (src/settings/store.js, proof D2), ws-003 stop and ask the user for the contrast check (D3). Commit each slice with its id in the subject. Append to the progress log after each slice. Status card on every stop.
```

## A good output must

- Say that the goal is already good, near the top.
- Keep the done items, evidence lines and reviewer kinds as they are.
- Change nothing of substance. A change of layout into the skill's section order is acceptable if the reply says it is layout only.
- Keep the stop in ws-003.

## It fails if

- It adds new requirements or slices that the user did not ask for.
- It removes the person review from D3, or turns it into a review by a separate session or another model.
- It changes an evidence line into a weaker one.
- It starts the work.
