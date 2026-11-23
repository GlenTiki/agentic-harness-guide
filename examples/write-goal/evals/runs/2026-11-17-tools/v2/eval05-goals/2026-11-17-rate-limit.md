---
goal: Finish the rate-limit fix on PR #42 with real tests, green CI, an independent review and a written report
status: active
branch: fix/rate-limit
base_sha: 685b6aa875ff4cba4ecce49e651059576bdf710d
created_at: 2026-11-17T01:38:39Z
---

# Goal: rate-limit fix (PR #42)

Progress log: `goals/2026-11-17-rate-limit.progress.md`
Do not `git add` anything under `goals/`. Both goal files stay untracked.

## Facts read from the repo (at base_sha)
- Tracked files: `README.md`, `go.mod`, `ratelimit.go`, `ratelimit_test.go`.
- `ratelimit.go` is `func Allow(n int) bool { return n < 10 }`.
- `ratelimit_test.go` has `func TestAllow(t *testing.T) {}`. It has no assertions, so it passes whatever `Allow` does.
- Not verified when this was written (the tools asked for approval): the `go test ./...` baseline, the state of PR #42, and the CI checks on it.

## Done list
- D1: Tests are real and pass. Evidence: `go test ./...` exits 0 and prints no `FAIL`. `go test -run TestAllow -v ./...` prints `--- PASS: TestAllow`. `ratelimit_test.go` calls `t.Error`, `t.Errorf`, `t.Fatal` or `t.Fatalf` at least once. Reviewer: none.
- D2: CI is green on PR #42. Evidence: `gh pr checks 42` exits 0, lists at least one check, and every row says `pass`. `gh pr view 42 --json state -q .state` prints `OPEN`. Reviewer: none.
- D3: Independent review is done. Evidence: `reports/rate-limit-review.md` exists. It contains the line `Reviewed: <sha>` and the line `Verdict: approve`. `git diff <sha> HEAD -- ratelimit.go ratelimit_test.go` prints nothing. Reviewer: a separate session of the same assistant, started with no access to this session's context, reading the diff only.
- D4: The report is written. Evidence: `reports/rate-limit.md` exists and contains the headings `## Change`, `## Tests`, `## Review` and `## Open issues`. The `## Tests` section quotes the real output of `go test ./...`. Reviewer: none.
- Out of scope: merging PR #42, force-pushing, pushing to any branch other than `fix/rate-limit`, changing CI config, editing files outside `ratelimit.go`, `ratelimit_test.go`, `reports/` and `README.md`.

## Slices
| id | outcome | paths | proof | rollback |
|----|---------|-------|-------|----------|
| ws-001 | `TestAllow` asserts real behavior | `ratelimit_test.go` | `go test -run TestAllow -v ./...` shows `--- PASS: TestAllow`, and the file contains `t.Error` or `t.Fatal` | `git restore --source=685b6aa -- ratelimit_test.go` |
| ws-002 | `Allow` matches the behavior PR #42 describes | `ratelimit.go`, `ratelimit_test.go` | `go test ./...` exits 0 with no `FAIL` | `git restore --source=<ws-001 sha> -- ratelimit.go ratelimit_test.go` |
| ws-003 | Independent review approves | `reports/rate-limit-review.md` | file has `Verdict: approve` and `Reviewed: <sha>`, and the code diff since `<sha>` is empty | `git rm --cached -- reports/rate-limit-review.md` if it was committed, then delete that file only |
| ws-004 | Report written | `reports/rate-limit.md` | the four headings exist, and `go test ./...` output is quoted | same as ws-003, for `reports/rate-limit.md` |
| ws-005 | Push and CI green | none (remote state) | D2 evidence | none, nothing local changes |

### ws-002 stop
Read the body of PR #42 with `gh pr view 42 --json body -q .body`. If it states the intended limit, implement that. If it does not say what "fixed" means (limit value, window, per-key or global), stop and ask the user. Do not guess a rate-limit policy.

### ws-003 steps
Start a separate session of the same assistant. Give it only: the branch name, `git diff 685b6aa..HEAD`, and the instruction "review for correctness, missing tests and concurrency; reply with findings, then `Verdict: approve` or `Verdict: changes`". Save its reply in `reports/rate-limit-review.md` with the `Reviewed: <sha>` line. If the verdict is `changes`, fix the findings as new commits and run the review again. After three rounds with the verdict still `changes`, stop.

### ws-005 steps
`git push origin fix/rate-limit` (plain push, never `--force`). Then poll `gh pr checks 42` until no check is pending. If a check fails, read its log with `gh run view --log-failed`, fix it as a new commit with the slice id in the subject, and push again. After three failed rounds on the same failure, stop. If a code change in ws-005 changes `ratelimit.go` or `ratelimit_test.go`, repeat ws-003 for the new sha.

## Recovery (run on the first turn and on every resume)
1. Read this file and the progress log.
2. Run `git status --short`, `git log --oneline -10` and `git worktree list`.
3. Find the last slice id in the commit subjects. That commit is the last known good point.
4. If a slice was interrupted, run its proof on the current files. If it passes, commit the slice. If it fails, log the failure, then restore only that slice's paths with `git restore --source=<last known good sha> -- <slice paths>`. Delete only new files that slice created.
5. If a helper worktree for this goal is listed, commit its partial work to a salvage branch, then remove only that worktree.
6. Never run a command that resets, cleans or checks out the whole working copy.

## Assumptions
- A: Pushing to `fix/rate-limit` is allowed, because green CI on the PR needs it. Merging is not.
- B: "Independent review" means a separate session of the same assistant. A person or another provider is not required.
- C: CI on PR #42 has at least one check. If `gh pr checks 42` lists none, stop and ask.
