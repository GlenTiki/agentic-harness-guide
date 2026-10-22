---
title: Anti-patterns
description: Common harness mistakes as a table of symptom, cause and fix.
---

**Recommendation:** use this table to diagnose a problem by its symptom. Each row names the mechanism behind it, then the fix.

| Symptom | Cause | Fix |
| --- | --- | --- |
| The agent breaks a rule you wrote | The rule is advice in an instruction file, which is loaded as context and lost after compaction | Enforce it with a [hook](../../control/hooks/) or [permission rule](../../control/permissions-and-sandboxing/) |
| A hook exists but the bad action still happens | The script exits 1, which is a non-blocking error in Claude Code | Exit 2 to block, or return a deny decision |
| Adherence drops as the instruction file grows | Every line competes for attention on every turn | Cut to commands and non-obvious rules, and scope the rest to paths |
| Two instruction layers give conflicting orders | Layers are concatenated and the model picks one | Review the layers together and delete the duplicate |
| The agent repeats a corrected mistake | The correction was never stored, or was appended below the wrong claim | [Refine the memory entry](../../context/memory/) where it stands |
| A constraint vanishes mid-session | It lived only in the conversation and compaction summarised it away | Write it to the [ledger](../../context/context-management/) |
| A sub-agent redoes finished work | The brief was vague or missing | Build the brief from the ledger with scope, known facts and answer format |
| Parallel agents overwrite each other | They share one working directory | Give each writer a [worktree](../../delegation/worktree-isolation/) |
| An isolated agent lacks recent work | The worktree branched from the default branch, not the current one | Merge first, or state the base and verify it |
| The suite is green but a bug shipped | The agent weakened or deleted the failing assertion | Review test diffs, and add a [gate](../../quality/test-first-and-gates/) on skips and suppressions |
| A commit lands that CI rejects | Local and CI run different commands | Use one `check` command in both places |
| A reviewer approved but the merged code differs | Approval was not bound to a digest | [Record the diff hash](../../quality/independent-review/) and re-review after any edit |
| The reviewer finds nothing, repeatedly | Same model, same context as the author | Use a fresh context and a different provider |
| A check always passes | The grader cannot fail | [Make it fail on purpose](../../quality/evals/) and add a control |
| A prompt change makes output worse unnoticed | No eval on the model-driven step | Add cases, run them repeatedly, hold the rubric still |
| Injected text causes a command to run | Fetched content was treated as an instruction | State [authority channels](../../control/untrusted-input/) and limit what the agent can reach |
| A new connector sends data you did not expect | The capability was enabled by default | [Default off](../../control/capability-gating/) and fail closed |
| An MCP server starts doing something new | The version was unpinned and the server upgraded | Pin the version and review its tools |
| A 3,000-line change is merged unread | The change was too large to review | [Slice work](../../quality/small-prs/) before you start |
| A poll runs all night | No deadline on the wait | Cap [every loop](../../operations/cost-and-resources/) |
| You cannot say what the agent did yesterday | No harness-written log | Add an [action log hook](../../operations/observability/) |
| Approvals are clicked without reading | Too many prompts for low-risk actions | Allow the safe majority, ask only for the [irreversible](../../operations/human-in-the-loop/) |
| Bypass mode wipes a directory | Prompts were skipped on a machine with real data | Use that mode only in a disposable container |

## Start here

Find the three rows that match your current setup. Fix those first.
