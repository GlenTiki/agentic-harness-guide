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

## Mantras for working with agents

These rules of thumb come from thousands of hours of pairing with agents across production systems:

- **Investing in your tooling invests in your time, and yourself.** Every hour spent building a mechanical check or a test gate pays a daily dividend in returned focus.
- **Hope is not an engineering strategy: account for probability.** Wrap probabilistic text models in hard deterministic gates.
- **Think big, act small.** Scopes larger than a single sitting invite comprehension debt. Pull requests over 400 lines are rarely reviewed with care.
- **Compounding formulas change your life, for worse or better.** A loose prompt habit compounds into exponential technical debt; an automated test suite compounds into exponential calm.
- **Target the destination, watch the path.** Keep the architectural outcome fixed, but inspect every step of the trajectory so the agent does not wander into an architectural dead end.
- **Code is cheap: ship it, refine it, let the agent do its thing.** Do not agonise over drafting boilerplate. Direct the intent, let the agent draft, and hold the output to strict standards.
- **Capture your thought processes and refine them.** When a session goes sideways, document the failure mode in a memory file. Post-mortems compound across future runs; code rots.
- **Holistic design beats reactive design when reactive design is compensating for fundamental flaws.** If code requires complex monkey-patching or endless retries, the design has a missing seam. Fix the underlying abstraction.
- **Comprehension debt is a workflow problem, not a code review problem.** You cannot fix comprehension debt at the final pull request gate after an agent has freestyled for forty minutes. Move the quality gate upstream into the harness.
- **Stop reviewing every diff: let the quality gate make the agent fix its own mess.** The agent pays the compliance cost because it does not care about deadlines. Save human attention for intent and architecture.
- **Never coerce absent to empty.** Missing data is signal. Coercing a missing value to a blank string hides absence and corrupts downstream telemetry.
- **Stop, collaborate and listen: observe, draft, sign-off.** The agent observes context and drafts solutions; the human retains ownership of intent and external commitments.
- **Silence is not acceptance.** An agent failing to object does not mean the design is sound. Require explicit independent peer confirmation.

## When meeting a principle gets expensive

A principle can be met in a way that makes you stop meeting it. Here is a Constructed case, invented for teaching. It is not a recorded run.

A small shop's assistant drafts a reminder to a customer who owes an invoice. Principle 7 says an outbound message needs a person. The shop has 40 overdue customers each month, and sending each draft for approval one by one is slow enough that the owner starts approving without reading. That breaks principle 6, because an approval that was not read is not bound to evidence. The tension is between how you meet principle 7 and what principle 6 needs. Neither principle has to give way. The approval workload is what has to change.

How to choose:

1. **Keep the principle that guards the irreversible edge.** An email to a customer cannot be recalled. A slow queue can be fixed. Every message still goes through a person.
2. **Make the review cheaper.** Show the owner the customer, the amount, the invoice date and the draft on one line each, and sort the large or unusual ones to the top.
3. **Write the decision down.** Note what you changed, why, and what would reopen it, for example "if reviewing 40 drafts takes more than the owner is willing to spend, cut the list, not the review".

Sometimes a principle really does cost another and no cheaper review exists. For example, if the owner will not spend any time on approvals, the only options are to drop the reminders or to send them unreviewed. Then the trade is real. Keep the principle that guards the irreversible edge, and record which one gave way and why.

## Failure modes they reduce

- A rule in a prompt is forgotten after compaction. Principle 1 moves it to a hook.
- A fetched web page tells the agent to run a command. Principle 4 tells the agent to treat the page as data. A permission rule or a hook is what stops it if the agent acts anyway.
- A reviewer approves code that changed after the review. Principle 6 makes that visible when a merge check compares digests.

## First step for the maintainer

Pick the three rules you would least like the agent to break. Write each as a hook or permission rule instead of a sentence in an instruction file. Then read [the adoption path](../adoption-path/).

**Next:** [The adoption path](../adoption-path/)
