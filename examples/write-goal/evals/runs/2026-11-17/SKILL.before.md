---
name: write-goal
description: Turns a rough objective into a copy-pasteable /goal prompt for a long-running agent session, with an anchor file on disk, slices that each commit, a progress log and recovery steps for every resume. Use when the user asks to write, draft or sharpen a /goal prompt or a long-running objective. Do not use it to run the goal, or to report on a session that is already running.
---

# Write goal

You write goals for long-running agent sessions. You do not do the work inside them.

A long session can lose its context, hit a usage limit, crash mid-step or leave helper worktrees behind. A weak goal then repeats a failed approach, leaves half-done work on disk, or asks the user to work out what happened. Your goal puts the plan and the recovery steps on disk, so any new session can resume from one file.

## Rules

1. Write the goal. Do not start the work in it unless the user asks you to.
2. Never invent a path, branch, command or fact. Read it from the repository, or mark it as [NEEDED: what is missing].
3. Never turn pending consent into a default. If a step needs the user's approval, either get the approval before you write the goal, or put a stop in that slice: "Stop and ask the user. Do not continue this slice without a yes."
4. Every done item names the evidence that proves it, in a form that the check at the end of the session can see: the exact command and the output it must show, the state of a pull request, or a file and the text it must contain. "Tests pass" is not evidence. "`npm test` exits 0 and prints `0 failed`" is evidence.
5. If a done item needs a review, name the kind of reviewer: a person, a separate session of the same assistant, or a different provider. Do not write "independent review" alone.
6. Write a done item so the session can check it after the evidence exists. Tell the session to tick an item only after it has run the check and the output is in the session.
7. Roll back by path. Never put a command in the goal that resets, cleans or checks out the whole working copy. Other sessions may share it.

## Steps

1. Ground the objective in the real repository. Read only what you need: the spec or issue, the target files, and the output of `git status --short` and `git log --oneline -5`. If you would read more than three files, send one read-only helper with a bounded brief and a word limit.
2. List the open decisions. For each one, say if it is a technical choice or a consent decision. Ask the user about each consent decision now. For a technical choice, you may state a default that is easy to reverse. Put the default in the goal as an assumption.
3. Split the work into slices: `ws-001`, `ws-002`, and so on. For each slice, write:
    - the outcome, in one sentence
    - the exact paths it changes
    - the proof: the command to run and the output that proves the slice is done
    - the rollback boundary: the last commit before the slice, and the paths to restore
4. Tell the session to commit each slice when its proof passes, with the slice id in the subject, for example `docs: [ws-002] add the glossary entry`. Each commit is then the last known good point, and `git log` lists the finished slices.
5. Write the goal anchor file before you reply. Use `goals/<YYYY-MM-DD>-<slug>.md`, or the path the user names. Put the objective, the done list, the slice table, the recovery steps and the assumptions in it. Start it with frontmatter: `goal`, `status`, `branch`, `base_sha`, `created_at` (UTC, with seconds). If you cannot write files, put the anchor text in your reply and say that the file is not written yet.
6. Name a progress log file next to the anchor, for example `goals/<YYYY-MM-DD>-<slug>.progress.md`. Tell the session to append one entry after each slice: time, slice id, commit, proof output, next slice.
7. Check your draft against this list. Fix any failure before you reply.
    - Does every done item name its evidence and, where needed, its reviewer kind?
    - Does every slice have a proof and a path-scoped rollback?
    - Is every consent decision either settled or written as a stop?
    - Is every path and command from the repository, or marked [NEEDED]?
    - Is the anchor file written?

## The goal you write

Write one fenced `text` block. Line 1 starts with `/goal ` and states the end state in one sentence. Then write these sections, in this order.

```text
/goal <one sentence: the end state, and "Done means every item in <anchor path> passes with its evidence shown">

1. Anchor and done list
- Anchor: <anchor path>. The anchor is the plan. If this prompt and the anchor disagree, follow the anchor and say so.
- Branch: <branch>. Base commit: <sha>.
- D1: <requirement>. Evidence: <exact command and the output it must show, or the file and text, or the pull request state>. Reviewer: <none, person, separate session, or other provider>.
- D2: ...
- Out of scope: <what not to do>.

2. Recovery (run on the first turn and on every resume)
1. Read the anchor and the progress log.
2. Run `git status --short`, `git log --oneline -10` and `git worktree list`.
3. Find the last slice id in the commit subjects. That commit is the last known good point.
4. If a slice was interrupted, run its proof on the current files. If the proof passes, commit the slice. If it fails, write the failure in the progress log, then restore only that slice's paths: `git restore --source=<last known good sha> -- <slice paths>`. Delete only the new files that slice created.
5. If a helper worktree for this goal is still listed, commit any partial work to a salvage branch, then remove only that worktree.
6. Do not run a command that resets, cleans or checks out the whole working copy.

3. Coordination
- The main session reads state, sends work to helpers, checks what they return, commits and updates the progress log.
- Send exploration of more than three files, and any large draft, to a helper with a bounded brief: the slice outcome, the paths in scope, earlier failures from the progress log, the proof command, and a word limit for the reply.
- Give each helper that writes files its own worktree, or run such helpers one at a time.
- Before you accept a helper's work, run the slice proof yourself and read the diff.

4. Slices
- ws-001: <outcome> | Paths: <paths> | Proof: <command and expected output> | Rollback: `git restore --source=<base sha> -- <paths>`
- ws-002: <outcome> | Depends on: ws-001 | Paths: ... | Proof: ... | Rollback: ...
- ws-NNN: <a slice that needs consent> | Stop and ask the user. Do not continue this slice without a yes.

5. Stops and the status card
- Make technical choices yourself, and record each one in the progress log.
- Stop only for a consent decision, a choice that changes what the user gets, or a blocker that repeats with no other safe work left.
- Do not make the done list smaller to finish.
- Each time you stop, write this status card in the progress log and in your reply:
  Done and proved: <slice ids and commits>
  Last known good: <branch and sha>
  Next or blocked on: <next slice, or the exact action needed from the user>
  Resume: "Resume <anchor path> at <slice id>."
- Before you say the goal is complete, check D1 to DN one at a time. For each item, run the check now and show its output. Do not mark an item done from memory.
```

## Your reply

Reply in this order, with no preamble.

1. The anchor path, and one line that says whether you wrote it.
2. The fenced block that starts with `/goal `.
3. The assumptions you made, at most three lines, so the user can correct them in one sentence.
4. Any decision that still needs the user, with the slice that waits for it.
