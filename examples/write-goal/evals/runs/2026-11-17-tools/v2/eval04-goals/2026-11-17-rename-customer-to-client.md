---
goal: Rename the "customer" field to "client" across the API and the database migrations
status: in-progress (ws-001 ready, ws-002 blocked on user decision)
branch: main
base_sha: 5c26ae0aa57e084159fdf4c576381999f81b46a7
created_at: 2026-11-17T01:37:50Z
---

# Rename "customer" to "client"

Progress log: `goals/2026-11-17-rename-customer-to-client.progress.md`

## Shared checkout warning

Two other sessions work in this same checkout on `src/billing/` and `docs/`.
Their uncommitted work is on disk right now: `docs/api.md` (modified), `src/billing/invoice.py` (modified), `src/billing/discount.py` (untracked).
Do not edit, stage, restore, stash or delete anything under `src/billing/` or `docs/`.
Never run `git add -A`, `git add .`, `git commit -a`, `git stash`, `git reset`, `git clean` or `git checkout .`.
Stage and commit by explicit path only: `git add -- <paths>` then `git commit -m "<msg>" -- <paths>`.

## Occurrences found at base_sha (case-insensitive grep "customer")

| File | Line | Text |
|---|---|---|
| src/api/schemas.py | 1 | `class Customer:` |
| src/api/schemas.py | 2 | `    customer_id: int` |
| src/api/routes.py | 1 | `from .schemas import Customer` |
| migrations/0001_initial.py | 1 | `# create table customer` |
| migrations/0002_invoice.py | 1 | `# add invoice table, customer_id foreign key` |
| docs/api.md | 3 | `GET /customer/{id}` (OUT OF SCOPE: docs session owns it) |

`src/billing/` has no match.

## Done list

- D1: API code uses `Client` and `client_id`. Evidence: `grep -n -i customer src/api/schemas.py src/api/routes.py` prints nothing and exits 1; `grep -n -E "^class Client:|client_id: int" src/api/schemas.py` prints `1:class Client:` and `2:    client_id: int`; `grep -n "import Client" src/api/routes.py` prints `1:from .schemas import Client`. Reviewer: none.
- D2: Migrations carry the rename, in the form the user chose for ws-002.
  - Option A (new migration, history untouched): `migrations/0003_rename_customer_to_client.py` exists and contains the word `client`; `git diff --stat 5c26ae0 -- migrations/0001_initial.py migrations/0002_invoice.py` prints nothing.
  - Option B (rewrite 0001 and 0002 in place): `grep -rn -i customer migrations/` prints nothing and exits 1.
  - Reviewer: the user chooses the option before work starts (a person).
- D3: Only in-scope paths were touched by this goal. Evidence: `git log 5c26ae0..HEAD --grep='\[ws-00' --name-only --format=` prints only paths that start with `src/api/`, `migrations/` or `goals/`. Reviewer: none.
- D4: The docs follow-up is handed off, not done. Evidence: `grep -n "docs/api.md" goals/2026-11-17-rename-customer-to-client.progress.md` prints a line that says `GET /customer/{id}` in `docs/api.md` still needs the rename and is for the docs session. Reviewer: none.
- Out of scope: `docs/`, `src/billing/`, `README.md`, any commit to a branch other than `main`, any database that is not in this repository.

## Slices

| Id | Outcome | Paths | Proof | Rollback |
|---|---|---|---|---|
| ws-001 | `Customer` becomes `Client` and `customer_id` becomes `client_id` in the API | `src/api/schemas.py`, `src/api/routes.py`, plus this anchor and the progress log | the three D1 commands | `git restore --source=5c26ae0 -- src/api/schemas.py src/api/routes.py` |
| ws-002 | Migrations carry the rename (needs user decision A or B) | A: `migrations/0003_rename_customer_to_client.py`. B: `migrations/0001_initial.py`, `migrations/0002_invoice.py` | the D2 commands for the chosen option | A: delete only `migrations/0003_rename_customer_to_client.py`. B: `git restore --source=<ws-001 commit> -- migrations/0001_initial.py migrations/0002_invoice.py` |
| ws-003 | Hand off the docs rename in the progress log | progress log only | the D4 command | none needed (append-only log) |

ws-002 is a stop: ask the user "A: add a new 0003 migration that renames customer to client and leave 0001 and 0002 as they are, or B: rewrite 0001 and 0002 in place?" Do not continue ws-002 without an answer.
Find the ws-001 commit with `git log --grep='\[ws-001\]' --format=%h`.

## Recovery (first turn and every resume)

1. Read this file and the progress log.
2. Run `git status --short`, `git log --oneline -10` and `git worktree list`. Expect other sessions' changes under `src/billing/` and `docs/`. Leave them alone.
3. Find the last `[ws-NNN]` commit subject. That commit is the last known good point.
4. If a slice was interrupted, run its proof on the current files. If it passes, commit the slice by path. If it fails, log the failure, then restore only that slice's paths with `git restore --source=<last known good sha> -- <slice paths>`. Delete only new files that slice created.
5. If a helper worktree for this goal is listed, commit its partial work to a salvage branch, then remove only that worktree.

## Assumptions

- The rename is a breaking change to the API names. No alias for the old names is kept.
- The work stays on `main` in the shared checkout, with path-scoped commits.
- `make test` (`python -m pytest -q`) has no tests to run in this repo (no `tests/` directory), so it is not used as evidence.
