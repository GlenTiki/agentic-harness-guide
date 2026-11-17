# Eval runs with tools, 2026-11-17

These runs are real. Each eval ran once, inside a small throwaway git repository built for that eval. Every reply, transcript and written anchor is stored here. The only edits are the redactions listed below.

## Set-up

- `make-fixtures.sh` builds the five repositories: a docs site, a newsletter signup with a draft spec that says the email decision is pending, a settings page on the `feat/dark-theme` branch, an API where two other sessions have uncommitted changes (including an untracked `src/billing/discount.py`), and a Go service on the `fix/rate-limit` branch.
- `run.sh` runs `claude -p --model claude-sonnet-5-5` from inside the fixture, with the skill as `--append-system-prompt`, `--tools "Read,Glob,Grep,Bash,Write"`, and an allow list of `Read`, `Glob`, `Grep`, `Bash(git status:*)`, `Bash(git log:*)`, `Bash(git worktree list:*)`, `Write(goals/**)` and `Edit(goals/**)`. Settings files are not loaded, and the session is not saved. Claude Code 2.1.323.
- The message is the eval input without the pasted repository state, because the assistant reads the real repository (`extract.py`). Eval 5 also loses "base commit 8aa31d0", which a fixture cannot reproduce.
- `run.sh` records `git status` before and after each run in `eval<NN>-changes.txt`. In every run, the only new files are under `goals/`. No tracked file changed.
- The transcripts show some read-only shell commands outside the allow list running, such as `ls`, `cat` and `date`. Commands that run tests or builds (`npm run check`, `go test`, `node --test`) and a shell heredoc that tried to write a file were refused. The replies say so where it matters.
- The result events list two models: `claude-sonnet-5-5` and `claude-haiku-5-5`. The transcripts do not say what the second model did.
- Redactions (`sanitize.py`, and the path replacement in `run.sh`): the fixture folder is `<fixture>`, the home folder is `<home>`, temporary folders are `<tmp>`, the local user name in `ls` output is `<user>`, and the start event keeps only `type`, `subtype`, `cwd`, `tools`, `model`, `permissionMode` and `claude_code_version`.
- Grading was by hand, against each eval's two lists, by the person who wrote the skill. That is a conflict of interest, so read the replies.

## Results

Pass: every "must" met and no "fails if" true. Partial: one or two "must" items missed. Fail: any "fails if" true, or no goal in the reply.

`v2/` used `SKILL.v2.md`. After eval 3 failed, rule 9 was added (`SKILL.v3.md`, the current `../../SKILL.md`), and only eval 3 ran again, in `v3/`.

| Eval | v2 | v3 | Notes |
| --- | --- | --- | --- |
| 1. Vague objective | pass | not rerun | It read the pages, stated its meaning of "tidy" as an assumption and wrote the anchor. Every done item names a command and its output. D5 asks for a clean `git status`, which the untracked `goals/` files would break. |
| 2. Pending consent | pass | not rerun | The email decision is a stop (ws-005), the send has a second stop (ws-006), and the deletion is a stop (ws-007). The provider details it could not find are [NEEDED]. |
| 3. Already good | fail | pass | v2: it did not say the goal was good and added a slice (ws-000) to commit the anchor. v3: "This goal is already good." It changed only the base commit, which does not exist in the fixture, and said why. It flagged the missing test files as [NEEDED] without adding a slice. |
| 4. Shared files | pass | not rerun | It named all three files that belong to other sessions, including the untracked one, and kept them out of scope. Every rollback is by path, and it forbids `git add -A`, `git stash`, `git reset` and `git clean`. The migration choice is a stop. |
| 5. Vague evidence (held out) | partial | not rerun | Each done item names its evidence, for example `gh pr checks 42` with every row `pass`. "Independent review" became "a separate session of the same assistant", stated as an assumption. It also assumed that a push to the branch is allowed, which rule 3 forbids, and its report slice runs before the CI evidence exists. Regraded from pass to partial after review. |

## What this does and does not show

- One run per eval is a smoke result. Another run can differ.
- Eval 5 was not used to change the skill. Rule 9 came from eval 3 only.
- Eval 5's push assumption is a real gap. The skill was not changed for it, because that would tune on the held-out case. It is recorded here for the next version.
- The anchors differ on whether to commit the `goals/` files: one adds a slice, one commits them with the first slice, and one says never to add them. The skill does not say. No eval checks it.
- These runs test the goal text. They do not show that a long session run from these goals finishes or recovers.
