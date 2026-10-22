---
title: Memory
description: What an agent should remember across sessions, what it should forget, and how to keep memory correct.
---

*Deep dive for [level 2: House rules](../../../journey/02-house-rules/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** persist durable facts and corrected behaviour, never session state. When memory is wrong, edit the existing entry. Do not append a correction below it. Add a recall step so memory is read before a risky action, not only at session start.

## Why it matters

A new session starts with no history. Memory is how corrections survive. It is also a second, silent source of instructions, so a wrong entry works like a wrong rule in an instruction file ([level 2](../../../journey/02-house-rules/)). A stale or wrong entry misleads every later session, so memory needs the same care as code.

## What to enable

**1. Split memory by kind.** Keep two stores, even if both are plain markdown files:

- Facts about the world: who owns what, which environments exist, which tool does which job.
- Behaviour: corrections you gave the agent, such as "never widen this exception handler".

Different review cadence applies. Facts go stale when the world changes. Behaviour goes stale when your practice changes.

**2. Persist this, not that.**

| Persist | Do not persist |
| --- | --- |
| A rule you corrected twice | Today's task list |
| The reason behind a non-obvious decision | The content of the current conversation |
| A stable fact, such as where the staging environment lives | A value that changes daily |
| A pointer to the source of truth | A copy of the source of truth |

Never store secrets or personal data in memory files that are committed or shared.

**3. Refine, do not append.** When a session disproves or narrows an entry, rewrite the entry where it stands. Merge duplicates into the older file and delete the leftover. An appended correction leaves the wrong claim in place, and recall will inject the wrong claim by itself.

**4. Cap what loads at startup.** Claude Code behaviour: it loads the first 200 lines or 25 KB of its auto-generated memory index at the start of each session, so keep the index to short one-line pointers and put detail in topic files that load on demand.

**5. Add recall hooks.** Search memory against the text of an outgoing action. A pre-tool hook can take the prompt for a sub-agent, or the content of an edit, run a keyword search over memory and add the top matches to context. Make it advisory. A wrong match should cost a glance, not a block.

**6. Date entries and cite sources.** Record the date and where the fact came from. A future reader can then judge whether to trust it.

## Failure modes it reduces

- The agent repeats a mistake you corrected last month.
- A correction is appended below a wrong claim, and the wrong claim is the one that gets recalled.
- Memory fills with session chatter and the useful rules drown.
- A remembered fact outlives the system it described.

## First step for the maintainer

Create one `memory/` directory with an index file of one-line entries. Add an entry the next time you correct the agent. Review the index monthly and delete what is no longer true.

<p class="verified">Docs page fetched on 2026-10-22: https://code.claude.com/docs/en/memory. Quoted line: "Each Claude Code session begins with a fresh context window." Claude Code on that date: 2.1.309. The docs page states no version of its own. The hooks reference was not re-fetched for this page: Not checked against current docs.</p>

**Next:** [Hooks](../../control/hooks/)
