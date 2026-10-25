---
title: Context management
description: Keep decisions in files, not in the conversation, so compaction and restarts cost nothing.
---

*Deep dive for [level 2: House rules](../../../journey/02-house-rules/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** treat the conversation as disposable and keep a durable ledger of intent and decisions in a file in the repository. Checkpoint it at phase boundaries. Brief sub-agents from the ledger, never from the chat.

## Why it matters

The context window is finite, as [level 2](../../../journey/02-house-rules/) explains. When it fills, the harness compacts older turns into a summary, and detail is lost. A decision that exists only in the conversation can vanish at the worst moment. A decision written to a file survives compaction, a crashed session and a hand-over to another agent.

## What to enable

**1. A ledger file.** One file, in the repository, written by the agent as it works. A minimal shape:

```json
{
  "intent": "Replace the retry loop in the sync job with a bounded backoff",
  "decisions": [
    {"at": "2026-03-02T10:14:09Z", "what": "Cap retries at 5", "why": "Upstream rate limit resets in 60 s"}
  ],
  "failures": [
    {"at": "2026-03-02T10:31:40Z", "what": "Unbounded sleep hung the worker", "next": "Add a timeout"}
  ],
  "open": ["Decide whether to jitter"]
}
```

Use second-resolution UTC timestamps. They sort, compare and survive time zones.

**2. Checkpoints at boundaries.** Write a summary to the ledger when a phase ends: spec agreed, tests written, implementation passing, review done. Do it by instruction ("update the ledger before moving on") and back it with a hook where your harness has a compaction event. Claude Code behaviour: it exposes `PreCompact` and `PostCompact` hook events, so a hook can remind the agent to write state before the summary replaces it, and to reread the ledger afterwards.

**3. Bounded briefs.** When you delegate, build the brief from the ledger: the intent, the relevant decisions, the files in scope and the form of the answer. Do not paste the conversation. See [Sub-agents](../../delegation/sub-agents/).

**4. Compact deliberately.** Compact when a phase ends and the ledger is current, not when the window is nearly full. Clear the conversation between unrelated tasks.

**5. Prefer pointers to pastes.** Tell the agent which file to read. A path costs a few tokens, and the file is read at its current state.

## Failure modes it reduces

- A constraint stated at the start of a long session is lost after compaction, and the agent contradicts it.
- A sub-agent receives a vague brief and redoes work that is already done.
- A crash loses an hour of reasoning because it lived only in the chat.

## First step for the maintainer

Create `ledger.json` with the four keys above. Add one line to your instruction file: "Update the ledger after each decision and before ending a phase."

<p class="verified">Docs page fetched on 2026-10-24: https://code.claude.com/docs/en/hooks. Quoted line: "`PreCompact` | Before context compaction". Claude Code on that date: 2.1.310. The docs page states no version of its own.</p>

**Next:** [Agent memory across sessions](../memory/)
