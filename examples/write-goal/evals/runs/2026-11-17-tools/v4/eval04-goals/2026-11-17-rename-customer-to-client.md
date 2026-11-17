---
goal: Rename the "customer" field to "client" in the API (src/api) and add a database migration for it, without touching src/billing or docs/
status: not-started
branch: main
base_sha: c473ceb1293e55c7e590132c3386654c313192d8
created_at: 2026-11-17T10:00:58Z
---

# Objective

Rename "customer" to "client" in `src/api/schemas.py` and `src/api/routes.py`, and add a new migration that renames the table and the foreign key column in the database. Two other sessions share this checkout and own `src/billing/` and `docs/`. Do not edit those paths.

Progress log: `goals/2026-11-17-rename-customer-to-client.progress.md`

# Checkout state at the start (from `git status --short`)

```
 M docs/api.md              (other session: docs)
M  src/api/routes.py        (STAGED, owner unknown, "staged change made before the goal")
 M src/billing/invoice.py   (other session: billing)
?? src/billing/discount.py  (other session: billing)
```

Consequence: `src/api/routes.py` already has a staged change that is not ours. A plain `git commit` would sweep it in. Commit only with an explicit pathspec: `git commit -m "<msg>" -- <slice paths>`. Never run `git add -A`, `git add .` or `git commit -a`.

# Assumptions (technical, reversible; correct them if wrong)

- A1: Existing migrations `migrations/0001_initial.py` and `migrations/0002_invoice.py` are history and may already be applied. Do not edit them. Add `migrations/0003_rename_customer_to_client.py` instead.
- A2: The rename covers: class `Customer` -> `Client`, field `customer_id` -> `client_id`, table `customer` -> `client`, and the `customer_id` foreign key on the invoice table -> `client_id`.
- A3: The route path `GET /customer/{id}` is documented in `docs/api.md` only. This repo has no route code for it in `src/api/routes.py` (the file holds an import and a comment). Docs are out of scope.

# Done list

- D1: Migration 0003 exists and renames the table and the foreign key column. Evidence: `grep -c -i "client" migrations/0003_rename_customer_to_client.py` prints a number >= 2, and the file text mentions both `customer` -> `client` (table) and `customer_id` -> `client_id` (column). Reviewer: person.
- D2: `src/api` no longer uses the old name. Evidence: `grep -rni customer src/api` prints nothing and exits 1. Reviewer: none.
- D3: The API package still imports. Evidence: `PYTHONPATH=src python -c "import api.routes"` exits 0 and prints no traceback. (Run it once on the base commit before ws-002 to confirm the command itself works; if it fails at base, replace it and note the change in the progress log.) Reviewer: none.
- D4: The old migrations are untouched. Evidence: `git diff c473ceb1293e55c7e590132c3386654c313192d8 -- migrations/0001_initial.py migrations/0002_invoice.py` prints nothing. Reviewer: none.
- D5: No other session's work was touched or committed by this goal. Evidence: `git diff --name-only c473ceb1293e55c7e590132c3386654c313192d8 HEAD` lists only `migrations/0003_rename_customer_to_client.py`, `src/api/schemas.py`, `src/api/routes.py` and `goals/` files. Reviewer: none.
- D6: Each slice has its own commit with the slice id in the subject. Evidence: `git log --oneline c473ceb..HEAD` shows `[ws-001]` and `[ws-002]`. Reviewer: none.
- Out of scope: `src/billing/`, `docs/` (including the `GET /customer/{id}` line in `docs/api.md`), `migrations/0001_*`, `migrations/0002_*`. The docs session owns the docs update. Record "docs/api.md still says customer" in the progress log as a hand-off, not as a failure. There are no tests in the repo (`git ls-files` shows none), so `make test` is not evidence here.

# Slices

| id | outcome | paths | proof | baseline | rollback |
|---|---|---|---|---|---|
| ws-001 | Add migration 0003 that renames table `customer` -> `client` and column `customer_id` -> `client_id` | `migrations/0003_rename_customer_to_client.py` (new file) | D1 check passes, and D4 check prints nothing | `git status --porcelain -- migrations/0003_rename_customer_to_client.py` (expect empty) | Delete only that new file, and only if the baseline was empty |
| ws-002 | Rename `Customer` -> `Client` and `customer_id` -> `client_id` in the API | `src/api/schemas.py`, `src/api/routes.py` | D2 and D3 checks pass | `git status --porcelain -- src/api/schemas.py src/api/routes.py` (at the start, `routes.py` shows `M ` staged) | `git restore --staged --worktree --source=<last known good sha> -- src/api/schemas.py`, and `routes.py` only after the user says how to treat the staged change |

## ws-002 stop (consent)

`src/api/routes.py` has a staged change from before this goal, with an owner we do not know. Stop and ask the user. Do not continue this slice without a yes. Ask: (a) whose change is it, (b) may the ws-002 commit include it, or should it be committed or unstaged first. If the user says the staged change is theirs and may go into the ws-002 commit, record that answer in the progress log, then proceed. Until then, ws-001 may still run.

# Recovery (run on the first turn and on every resume)

1. Read this file and the progress log.
2. Run `git status --short`, `git log --oneline -10` and `git worktree list`.
3. Find the last slice id in the commit subjects. That commit is the last known good point.
4. If a slice was interrupted, run its proof on the current files. If the proof passes, commit the slice with the pathspec form. If it fails, write the failure in the progress log, then read the slice's baseline in the progress log.
5. If the baseline shows that a slice path had staged or unstaged changes before the slice, or if there is no baseline, stop and ask the user. Do not restore that path. This is already true for `src/api/routes.py`. Otherwise restore only the slice paths: `git restore --staged --worktree --source=<last known good sha> -- <slice paths>`. Delete only the new files that the slice created, as shown by the baseline.
6. If a helper worktree is still listed, check that the progress log shows this goal created it and that the helper is no longer running. If either check fails, leave it and wait. If both pass, commit any partial work to a salvage branch, then remove only that worktree.
7. Do not run a command that resets, cleans or checks out the whole working copy. Do not touch `src/billing/` or `docs/`, even if they look wrong or half-done: other sessions are working there.

# Coordination

- The main session reads state, commits and updates the progress log. The work is small (two source files and one new file); use a helper only if the scope grows beyond three files.
- At the start of each slice, append its baseline to the progress log: slice id, time, and the output of `git status --porcelain -- <slice paths>`.
- Commit with `git commit -m "<type>: [ws-00N] <summary>" -- <slice paths>` so that other sessions' staged changes stay out. End the commit message with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
- Other sessions commit to the same branch. If HEAD moves, that is expected: re-read `git log --oneline -10` and use the newest commit that carries a `[ws-00N]` subject from this goal as the last known good point.

# Stop rules and status card

- Make technical choices yourself and record each one in the progress log.
- Stop only for a consent decision, a choice that changes what the user gets, or a blocker that repeats with no other safe work left.
- Do not make the done list smaller to finish.
- Each time you stop, write this card in the progress log and in your reply:
  Done and proved: <slice ids and commits>
  Last known good: <branch and sha>
  Next or blocked on: <next slice, or the exact action needed from the user>
  Resume: "Resume goals/2026-11-17-rename-customer-to-client.md at <slice id>."
- Before you say the goal is complete, check D1 to D6 one at a time. Run each check now and show its output. Do not mark an item done from memory.
