---
title: Cost and resource discipline
description: Bound loops, timeouts and heavy jobs so an agent has a limit on the money and machine time it can use.
---

*Deep dive for [level 7: Run it for real](../../../journey/07-run-it-for-real/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** put an explicit upper bound on every loop, poll, retry, timeout and background job. Run heavy local work at lower priority. Spend capability budgets deliberately, and record cost per session.

## Why it matters

An agent can keep polling a build that never finishes, retry a call that always fails, or start a heavy job in the background and forget it. Principle, not measured. Each costs tokens, money or machine time, and none of them stops by itself. [Level 7](../../../journey/07-run-it-for-real/) explains the limits that a run needs. The bound has to exist in the instruction, the command or the harness.

## What to enable

**1. Cap every poll.** Any wait for an external condition needs a maximum count or a deadline:

```bash
for i in $(seq 1 30); do
  if ./is-ready.sh; then exit 0; fi
  sleep 10
done
echo "Gave up after 300 seconds" >&2
exit 1
```

**2. Set command timeouts.** Give shell calls an explicit timeout. A command that hangs holds the whole session.

**3. Limit retries and say what happens at the limit.** Use at most two retries, so three attempts in all, with a pause that grows after each failure. Add random jitter to the pause, so many runs that fail together do not retry together. Then stop and report. Do not retry a failure that a retry cannot change, such as a permission denial. Give each run a retry budget as well as each call, so ten failing steps cannot make thirty attempts. When a provider returns a rate-limit response, wait as long as it asks before the next attempt. If calls to one service keep failing, a circuit breaker stops all calls to it for a while, and a person decides when to resume.

**4. Know that each turn resends the history.** The assistant does not remember your last message. Each turn sends the whole conversation again, so the cost of a turn grows with the length of the chat unless your provider caches the repeated part. Made-up numbers, stated assumptions: a chat adds 2,000 tokens per turn and has no caching. Turn 1 sends 2,000 tokens, turn 2 sends 4,000, and turn 20 sends 40,000. Twenty turns send 2,000 x (1 + 2 + ... + 20) = 2,000 x 210 = 420,000 tokens in total, although only 40,000 are new. Clear the conversation between unrelated tasks.

**5. Run heavy work at lower priority.** Prefix CPU-bound jobs such as indexing, renders, large test runs and local model loads with `nice -n 10`. Your foreground applications stay responsive. Run long jobs in the background and check them with a bounded poll.

**6. Reap what you start.** A background process that survives its session keeps consuming memory. Prefer a harness mechanism that tracks background jobs and reports their exit. If you spawn one yourself, record its process ID and stop it at the end.

**7. Cap sub-agent fan-out.** Parallel agents multiply token use. Set a maximum number of simultaneous agents and a maximum depth. See [Sub-agents](../../delegation/sub-agents/).

**8. Use the smallest model that passes the eval.** Route routine steps to a smaller model and keep the large one for planning and review. Let an [eval](../../quality/evals/) decide, not intuition.

**9. Mind memory on a shared machine.** Local models, container stacks and several agent sessions all compete for RAM. When swap grows, stop the least important process first.

**10. Alert on the trend.** Record cost per session (see [Observability](../observability/)) and review the totals weekly. Set a hard spending limit at the provider if one is available.

## Failure modes it reduces

- A poll loop runs overnight against a job that failed at the start.
- A retry storm trips a rate limit and blocks real work.
- An orphaned process holds a model in memory for hours.
- Parallel agents multiply the bill without multiplying the result.

## First step for the maintainer

Search your instructions, hooks and scripts for `while`, `sleep` and `retry`. Add a maximum to every one that lacks one.

**Next:** [Human-in-the-loop](../human-in-the-loop/)
