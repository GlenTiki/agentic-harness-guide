---
goal: Move newsletter signup from the old mailing service to the new one; once the new list works, delete the old list; email subscribers only if the owner approves
status: not-started
branch: main
base_sha: f79d78e82d4c035d72d6717bcf2996f252931f06
created_at: 2026-11-17T01:35:33Z
---

# Newsletter provider move

Progress log: goals/2026-11-17-newsletter-provider-move.progress.md

## Objective
Signup writes to the new provider, the new list is proven to receive a signup, the old list is deleted (after its subscribers are exported), and subscribers are emailed about the move only if the owner says yes.

## Done list
- D1: `src/newsletter/signup.js` calls the new provider and no longer references the old one. Evidence: `grep -c oldProvider src/newsletter/signup.js` prints `0`. Reviewer: none.
- D2: A test proves signup goes to the new provider. Evidence: `npm test` exits 0 and prints `# fail 0` and a `# pass` count of at least 1. Reviewer: none.
- D3: A real signup with a test address reaches the new list. Evidence: [NEEDED: the new provider's command or dashboard view that lists the test address]. Reviewer: person (the user confirms they see it).
- D4: Old subscribers are exported before anything is deleted. Evidence: [NEEDED: export path outside git]; `wc -l <export path>` matches the old provider's subscriber count shown by [NEEDED: command or dashboard]. Reviewer: person.
- D5: The owner's decision on emailing subscribers is recorded in the progress log as `EMAIL DECISION: yes` or `EMAIL DECISION: no`, with who decided and when. Evidence: `grep "EMAIL DECISION" goals/2026-11-17-newsletter-provider-move.progress.md` prints that line. Reviewer: person (the owner).
- D6: If the decision is yes, every subscriber in the export was emailed. Evidence: [NEEDED: send report from the new provider showing a sent count equal to the export count]. If the decision is no, evidence is the `EMAIL DECISION: no` line and no send in the log. Reviewer: person.
- D7: The old list is deleted. Evidence: [NEEDED: old provider command or dashboard showing the list is gone]; `git ls-files src/newsletter/old-provider.js` prints nothing. Reviewer: person.
- Out of scope: changing the signup form markup, anything outside `src/newsletter/` and `goals/`, committing subscriber emails to git.

## Slice table
| id | outcome | paths | proof | rollback |
|---|---|---|---|---|
| ws-001 | New provider module exists | src/newsletter/new-provider.js | `node -e "import('./src/newsletter/new-provider.js').then(m=>console.log(Object.keys(m)))"` prints the export names | `git restore --source=f79d78e -- src/newsletter/new-provider.js`; delete the file if it is new |
| ws-002 | signup uses the new provider, with a test | src/newsletter/signup.js, src/newsletter/signup.test.js | `npm test` shows `# fail 0` and `# pass` >= 1; `grep -c oldProvider src/newsletter/signup.js` prints `0` | `git restore --source=<ws-001 sha> -- src/newsletter/signup.js src/newsletter/signup.test.js` |
| ws-003 | Live check on the new list | none (external) | D3 evidence | none; remove the test address in the new provider |
| ws-004 | Export old subscribers | export file outside git | D4 evidence | delete the export file |
| ws-005 | Owner decision on emailing | progress log | D5 evidence | none |
| ws-006 | Email subscribers (only if yes) | none (external) | D6 evidence | none; cannot be undone |
| ws-007 | Delete old list and old-provider.js | src/newsletter/old-provider.js | D7 evidence | `git restore --source=<ws-002 sha> -- src/newsletter/old-provider.js`; the remote list can only come back from the export |

## Stops
- ws-003: Stop and ask the user for the test address and for approval to send a real signup to the live new provider. Do not continue this slice without a yes.
- ws-005: Stop and ask the user. The user has not decided and must check with the owner. Do not continue this slice without the owner's answer.
- ws-006: Do not start unless D5 says `yes`. Then stop and ask the user to approve the final email text and the recipient count before sending.
- ws-007: Do not start unless D3, D4 and D5 pass and ws-006 is either done or skipped by a `no`. Stop and ask the user for a yes before deleting the remote list. Deletion cannot be undone.

## Recovery (run on the first turn and on every resume)
1. Read this file and the progress log.
2. Run `git status --short`, `git log --oneline -10` and `git worktree list`.
3. Find the last slice id in the commit subjects. That commit is the last known good point.
4. If a slice was interrupted, run its proof on the current files. If it passes, commit the slice. If it fails, log the failure, then run `git restore --source=<last known good sha> -- <slice paths>` and delete only the new files that slice created.
5. If a helper worktree for this goal is still listed, commit partial work to a salvage branch, then remove only that worktree.
6. Never run a command that resets, cleans or checks out the whole working copy.
7. For external slices (ws-003, ws-004, ws-006, ws-007), read the progress log first to see if the action already happened. Check the provider's state before repeating it. Never send or delete twice.

## Assumptions
- The new provider is not named in the repository: [NEEDED: provider name, API or SDK, and where credentials live].
- The old provider is a stub in `src/newsletter/old-provider.js` (`add` returns true). The real old list lives outside the repo: [NEEDED: how to export and delete it].
- `signup.js` uses `oldProvider` without importing it, and `signup.test.js` has no tests. ws-002 fixes both.
- Subscriber emails stay out of git.
- Exporting before deletion is a technical choice. It keeps the email option open.
