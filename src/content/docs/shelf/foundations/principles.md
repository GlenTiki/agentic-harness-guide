---
title: Principles
description: Seven principles that decide which harness features are worth enabling.
---

*Deep dive for [level 8: Design anything](../../../journey/08-design-anything/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** judge every harness feature by one question. Does it make the agent's work more bounded, more recoverable or more checkable? Enable it if the answer is yes. Skip it if the answer is no, however impressive the demo.

## Why it matters

This shelf says agent for the assistant and sub-agent for the helper. See the [glossary](../../../glossary/). A model is probabilistic. A harness is the deterministic layer around it. Rules in a prompt are advice, and the model may ignore advice. Rules in the harness run on every call they cover. These principles tell you which rules belong in which layer. [Level 2](../../../journey/02-house-rules/) and [level 4](../../../journey/04-trust-but-verify/) teach the reason.

## The principles

1. **Enforce in the harness, advise in the prompt.** An instruction file is read as context. A hook or permission rule runs every time. Put anything that must be refused in the second group, and remember that a hook covers only the calls it sees. Put preferences in the first.
2. **Least privilege by default.** Start with read-only access and add capabilities one at a time. Each addition needs a named reason.
3. **Keep context small and durable.** The context window is working memory and it is lossy. Write decisions to files. Pass sub-agents a brief, not a transcript.
4. **Treat everything the agent reads as data.** Tool output, web pages, repository files and replies from other agents carry no authority. Only a short list of verified channels may instruct the agent.
5. **Separate the author from the reviewer.** The agent that wrote a change shares its assumptions. Review with a fresh context. Try a different model or provider, and measure whether it catches more (see [independent review](../../quality/independent-review/)).
6. **Bind approval to evidence.** An approval applies to one exact diff, one exact digest. Any edit voids it.
7. **Keep a human at the irreversible edges.** Pushes, spend, outbound messages and destructive operations need a person. Everything reversible can run unattended.

## When two principles conflict

The principles do not always point the same way. Here is a Constructed case, invented for teaching. It is not a recorded run.

A small shop's assistant drafts a reminder to a customer who owes an invoice. Principle 7 says an outbound message needs a person. Principle 3 says keep context small and durable, which pushes towards automatic drafts from a short ledger. The shop has 40 overdue customers each month, and sending each draft for approval one by one is slow enough that the owner starts approving without reading. That breaks principle 6, because an approval that was not read is not bound to evidence.

How to choose:

1. **Rank by what is hardest to undo.** An email to a customer cannot be recalled. A slow queue can be fixed. Principle 7 wins.
2. **Keep the winner whole and bend the loser.** Every message still goes through a person. Make the review cheaper instead: show the owner the customer, the amount, the invoice date and the draft on one line each, and sort the large or unusual ones to the top.
3. **Write the decision down.** Note which principle gave way, why, and what would reopen it, for example "if reviewing 40 drafts takes more than the owner is willing to spend, cut the list, not the review".

The rule of thumb: when two principles collide, keep the one that guards the irreversible edge, and spend your effort making the other cheaper to meet.

## Failure modes they reduce

- A rule in a prompt is forgotten after compaction. Principle 1 moves it to a hook.
- A fetched web page tells the agent to run a command. Principle 4 tells the agent to treat the page as data. A permission rule or a hook is what stops it if the agent acts anyway.
- A reviewer approves code that changed after the review. Principle 6 makes that visible when a merge check compares digests.

## First step for the maintainer

Pick the three rules you would least like the agent to break. Write each as a hook or permission rule instead of a sentence in an instruction file. Then read [the adoption path](../adoption-path/).

**Next:** [The adoption path](../adoption-path/)
