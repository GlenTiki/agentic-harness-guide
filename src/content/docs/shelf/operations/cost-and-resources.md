---
title: Cost and resource discipline
description: Bound loops, timeouts and heavy jobs so an agent cannot burn money or lock up your machine.
---

*Deep dive for [level 7: Run it for real](../../../journey/07-run-it-for-real/).*

**Recommendation:** put an explicit upper bound on every loop, poll, retry, timeout and background job. Run heavy local work at lower priority. Spend capability budgets deliberately, and record cost per session.

## Why it matters

An agent will keep polling a build that never finishes, retry a call that always fails, or start a heavy job in the background and forget it. Each costs tokens, money or machine time, and none of them stops by itself. The bound has to exist in the instruction, the command or the harness.

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

**3. Limit retries and say what happens at the limit.** Three attempts with backoff, then stop and report. Do not retry a failure that a retry cannot change, such as a permission denial.

**4. Run heavy work at lower priority.** Prefix CPU-bound jobs such as indexing, renders, large test runs and local model loads with `nice -n 10`. Your foreground applications stay responsive. Run long jobs in the background and check them with a bounded poll.

**5. Reap what you start.** A background process that survives its session keeps consuming memory. Prefer a harness mechanism that tracks background jobs and reports their exit. If you spawn one yourself, record its process ID and stop it at the end.

**6. Cap sub-agent fan-out.** Parallel agents multiply token use. Set a maximum number of simultaneous agents and a maximum depth. See [Sub-agents](../../delegation/sub-agents/).

**7. Use the smallest model that passes the eval.** Route routine steps to a smaller model and keep the large one for planning and review. Let an [eval](../../quality/evals/) decide, not intuition.

**8. Mind memory on a shared machine.** Local models, container stacks and several agent sessions all compete for RAM. When swap grows, stop the least important process first.

**9. Alert on the trend.** Record cost per session (see [Observability](../observability/)) and review the totals weekly. Set a hard spending limit at the provider if one is available.

## Failure modes it prevents

- A poll loop runs overnight against a job that failed at the start.
- A retry storm trips a rate limit and blocks real work.
- An orphaned process holds a model in memory for hours.
- Parallel agents multiply the bill without multiplying the result.

## Start here

Search your instructions, hooks and scripts for `while`, `sleep` and `retry`. Add a maximum to every one that lacks one.
