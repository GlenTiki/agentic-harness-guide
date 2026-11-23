# Eval runs, 2026-11-17

These runs are real. Every reply is stored unedited in `before/` and `after/`.

- Tool: Claude Code 2.1.323, run as `claude -p --model claude-sonnet-5-5 --tools "" --setting-sources "" --no-session-persistence`, in an empty folder.
- Model: `claude-sonnet-5-5`, set with the `--model` flag. The calls did not print the model they used.
- Message sent: the whole skill file, then "Use this as your instructions for this chat.", then the eval input (`extract.py` builds it). One message, no tools.
- One run per eval per version. Ten runs in all, started once each. No run was discarded or repeated.
- `SKILL.before.md` is the first draft. `SKILL.after.md` is the current `../../SKILL.md`. The change adds rule 8 (no tool calls when there are no tools) and moves the matching sentence out of step 5.
- The "before" round used an earlier `run.sh` that took only the eval file and wrote to `replies/`. The folder was renamed to `before/` afterwards. The command line to `claude` was the same.
- Grading was by hand, against each eval's two lists, by the person who wrote the skill. That is a conflict of interest, so read the replies.

## Results

Pass: every "must" met and no "fails if" true. Partial: one or two "must" items missed. Fail: any "fails if" true, or no goal in the reply.

| Eval | Before | After | Notes |
| --- | --- | --- | --- |
| 1. Vague objective | partial | fail | Before: a full goal. Every done item names a command and its output, and the rename slice has a stop. The first line says "I issued the write, but the tool calls returned no output". The run had no tools, so that write never happened. No anchor text is shown. After: the reply is one tool call written as text, and no goal. |
| 2. Pending consent | fail | fail | Both replies are tool calls written as text, and no goal. |
| 3. Already good | fail | not graded | Before: the same tool call written as text, repeated many times, and no goal. After: an API error from a safety filter, and no reply. |
| 4. Shared files | fail | not graded | Before: two tool calls written as text, and no goal. After: the same API error. |
| 5. Vague evidence (held out) | fail | fail | Both replies are tool calls written as text, and no goal. |

## What this does and does not show

- In this set-up the skill mostly fails before it writes anything. Its first step tells the assistant to read the repository. With no tools, the assistant wrote tool calls as plain text and stopped. Rule 8 was added to stop that. It did not stop it in three of three graded runs.
- The evals therefore say almost nothing yet about the goal text itself. Only eval 1 "before" produced a goal to grade.
- The set-up is not a plain chat app. The tool flags remove the tools, and the reply still looks like an agent's. A run in a chat app, or in an agent that can read the repository, may behave differently. That has not been run.
- Eval 5 was seen in the "before" round, before rule 8 was written. Rule 8 is about tool calls, not evidence, so it was not shaped on eval 5. Eval 5 is still the held-out case for the evidence rules.
- The two API errors are stored as they came back.
