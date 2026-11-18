---
title: Distributed-systems primitives
description: An agent setup is a small distributed system. Eighteen common terms, and the lesson each one holds for agent work.
---

*Deep dive for [level 6: Hire a team](../../../journey/06-hire-a-team/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page unless the user asks for it in the current session.*

**Recommendation:** when an agent setup misbehaves, ask which distributed-systems problem it is. Several [helpers](../../../glossary/#helper) (sub-agents) share state, fail part-way, retry, and disagree about what is true. Teams that build services met these problems first and named them. The names come with known fixes.

## Why it matters

A single chat with one assistant is a single process. Once you run helpers in parallel, keep memory between sessions and let a loop drive work to a goal, you have a distributed system. It has the same failures as any other: stale reads, double work after a retry, two writers on one file and a queue that grows faster than it drains. The tables below give each term its plain meaning and then the lesson for agent work.

## The shape of an application

| Term | What it means | Lesson for agent work |
| --- | --- | --- |
| Frontend | The code that runs in the user's browser or app and draws the screen. | Ask the agent for a screenshot or a browser test, not "it should look right". The browser is the only judge. |
| Backend | The code on servers that holds the rules and talks to the data. | Put business rules here, behind tests. An agent can change a backend rule safely only if a test pins it. |
| Data persistence | Where data survives a restart: a database, object storage, files. | A chat is memory that ends with the session. Git, notes and a progress log persist. Write state to disk before you rely on it. |
| API gateway | One front door for many services. It checks identity, limits rates and routes each request. | Give agents one front door too: a hook or a tool server that checks every tool call, logs it and refuses what is out of scope. |
| CDN | Copies of content on servers near users. It serves a cached copy until the copy expires or is purged. | A cache is fast and can be stale. Memory notes are a cache: date them, and let a newer fact replace an old one. |
| Serverless | Functions that start on demand and run briefly. You cannot rely on anything kept between calls. | Treat each agent session as serverless. It starts cold, so everything it needs must be in the brief, the files or the memory. |

## Scale, failure and agreement

| Term | What it means | Lesson for agent work |
| --- | --- | --- |
| Vertical scaling | A bigger machine for the same job. | A larger model or more effort on one agent. It is simple, but it has a ceiling and the cost rises fast. |
| Horizontal scaling | More machines that share the job. | More helpers in parallel [worktrees](../../delegation/worktree-isolation/). It works only when the work splits cleanly and each part has its own space and its own check. |
| [Eventual consistency](../../../glossary/#eventual-consistency) | Copies of data agree only after updates spread, so a read can be out of date for a while. | Two helpers can hold different views of the repository. Re-read the files and run `git status` before you act on what you saw earlier. |
| [Idempotent](../../../glossary/#idempotent) step | Doing it twice has the same effect as doing it once. | Make agent steps safe to retry: "create the branch if it is missing", not "create the branch". Then recovery after a crash is a rerun. |
| Queues and backpressure | Work waits in a queue, and producers slow down when consumers fall behind. | Cap the number of helpers you start. Your review time is the slowest consumer, so limit open pull requests to what you can read. |
| Kubernetes (control loop) | Software that runs containers and keeps changing the cluster towards the state you declared. | Declare the done state and let a loop drive towards it. The loop needs evidence it can see, or it never settles. |
| Observability | Logs, metrics and traces that show why a system did something. | Keep transcripts, a progress log and command output. When an agent fails, you debug the record, not your memory of the chat. |

<p class="verified">Docs page fetched on 2026-11-18: https://kubernetes.io/docs/concepts/architecture/controller/. Quoted line: "In Kubernetes, controllers are control loops that watch the state of your cluster, then make or request changes where needed."</p>

In Claude Code, the `/goal` command is one such loop. It keeps the agent working across turns until a condition holds or the goal clears.

<p class="verified">Docs page fetched on 2026-11-18: https://code.claude.com/docs/en/commands. Quoted line: "Claude keeps working across turns until the condition is met or the goal clears for another reason." Claude Code on that date: 2.1.326. The docs page states no version of its own.</p>

## Design and boundaries

| Term | What it means | Lesson for agent work |
| --- | --- | --- |
| Domain-driven design | Model the software on the business, in the words the business uses. | Write the domain words into the [instruction file](../../context/instruction-files/). An agent that uses your terms makes fewer wrong guesses. |
| [Bounded context](../../../glossary/#bounded-context) | A part of the system where each word has one meaning, usually owned by one team. | Give each helper one bounded context per task: its folder, its files and its check. A step that crosses the boundary is a reason to stop and ask. |
| Contract | The agreed shape of an API, an event or a schema, which both sides test against. | Brief a helper with a contract: inputs, outputs and a done check. Review the result against the contract. |
| [Least privilege](../../../glossary/#least-privilege) | Each part gets only the access it needs. | Allow routine commands, ask before risky ones and deny secrets. Widen access when a task needs it, then narrow it again. |
| Agentic harness | Everything around the model: instructions, memory, tools, hooks, review and the loop that runs it. | The model is one part. When the same mistake happens twice, change the harness, not only the prompt. The [principles](../principles/) explain why. |

## Where the analogy breaks

- **An agent is not deterministic.** A retried idempotent call has the same effect. A retried agent step can return a different answer. An idempotent step design limits the damage, but a check after each step still decides what is true.
- **A person is in the loop.** Services scale by adding machines. An agent setup also depends on how fast a person can review, and that capacity does not scale.
- **The words carry over, the numbers do not.** Uptime targets and latency budgets from service design have no direct counterpart here. Measure your own setup before you set a target.

## Failure modes they reduce

- A helper acts on a stale view of the repository (eventual consistency).
- A crash leaves work half done, and a rerun doubles it (idempotency).
- Too many helpers produce more pull requests than anyone reads (backpressure).
- A helper edits files outside its task (bounded context, least privilege).
- A loop never stops, because its done state names nothing it can see (control loop).

## First step for the maintainer

Pick the last failure in your setup. Find its row in the tables above, and apply that row's lesson as one check or one rule.

**Next:** [AGENTS.md vs CLAUDE.md files](../../context/instruction-files/)
