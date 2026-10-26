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

## Failure modes they reduce

- A rule in a prompt is forgotten after compaction. Principle 1 moves it to a hook.
- A fetched web page tells the agent to run a command. Principle 4 tells the agent to treat the page as data. A permission rule or a hook is what stops it if the agent acts anyway.
- A reviewer approves code that changed after the review. Principle 6 makes that visible when a merge check compares digests.

## First step for the maintainer

Pick the three rules you would least like the agent to break. Write each as a hook or permission rule instead of a sentence in an instruction file. Then read [the adoption path](../adoption-path/).

**Next:** [The adoption path](../adoption-path/)
