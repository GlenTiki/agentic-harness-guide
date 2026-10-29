---
title: Anti-patterns
description: Common harness mistakes as a table of symptom, cause and fix.
---

*Deep dive for [level 8: Design anything](../../../journey/08-design-anything/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** use this table to diagnose a problem by its symptom. Each row has an id, names the mechanism behind it, then gives the fix. Rules that live only in a prompt are requests; [level 4](../../../journey/04-trust-but-verify/) explains why.

| ID | Symptom | Cause | Fix |
| --- | --- | --- | --- |
| AP-01 | The agent breaks a rule you wrote | The rule is advice in an instruction file, which is loaded as context and lost after compaction | Move it into a [hook](../../control/hooks/) or [permission rule](../../control/permissions-and-sandboxing/), which the harness applies on the calls it covers |
| AP-02 | A hook exists but the bad action still happens | Claude Code behaviour: the script exits 1, which is a non-blocking error | Exit 2 to block, or return a deny decision |
| AP-03 | Adherence drops as the instruction file grows | Every line competes for attention on every turn | Cut to commands and non-obvious rules, and scope the rest to paths |
| AP-04 | Two instruction layers give conflicting orders | Layers are concatenated, later text usually weighs more, and the outcome of a conflict is not defined | Review the layers together and remove the conflict |
| AP-05 | The agent repeats a corrected mistake | The correction was never stored, or was appended below the wrong claim | [Refine the memory entry](../../context/memory/) where it stands |
| AP-06 | A constraint vanishes mid-session | It lived only in the conversation and compaction summarised it away | Write it to the [ledger](../../context/context-management/) |
| AP-07 | A sub-agent redoes finished work | The brief was vague or missing | Build the brief from the ledger with scope, known facts and answer format |
| AP-08 | Parallel agents overwrite each other | They share one working directory | Give each writer a [worktree](../../delegation/worktree-isolation/) |
| AP-09 | An isolated agent lacks recent work | The worktree branched from the default branch, not the current one | Merge first, or state the base and verify it |
| AP-10 | The suite is green but a bug shipped | The agent weakened or deleted the failing assertion | Review test diffs, and add a [gate](../../quality/test-first-and-gates/) on skips and suppressions |
| AP-11 | A commit lands that CI rejects | Local and CI run different commands | Use one `check` command in both places |
| AP-12 | A reviewer approved but the merged code differs | Approval was not bound to a digest | [Record the diff hash](../../quality/independent-review/) and re-review after any edit |
| AP-13 | The reviewer finds nothing, repeatedly | Same context as the author, possibly the same model | Use a fresh context, then try a different provider and measure |
| AP-14 | A check always passes | The grader cannot fail | [Make it fail on purpose](../../quality/evals/) and add a control |
| AP-15 | A prompt change makes output worse unnoticed | No eval on the model-driven step | Add cases, run them repeatedly, hold the rubric still |
| AP-16 | Injected text causes a command to run | Fetched content was treated as an instruction | State [authority channels](../../control/untrusted-input/) and limit what the agent can reach |
| AP-17 | A new connector sends data you did not expect | The capability was enabled by default | [Default off](../../control/capability-gating/) and fail closed |
| AP-18 | An MCP server starts doing something new | The version was unpinned and the server upgraded | Pin the version and review its tools |
| AP-19 | A 3,000-line change is merged unread | The change was too large to review | [Slice work](../../quality/small-prs/) before you start |
| AP-20 | A poll runs all night | No deadline on the wait | Cap [every loop](../../operations/cost-and-resources/) |
| AP-21 | You cannot say what the agent did yesterday | No harness-written log | Add an [audit log hook](../../operations/observability/) |
| AP-22 | Approvals are clicked without reading | Too many prompts for low-risk actions | Allow the safe majority, ask only for the [irreversible](../../operations/human-in-the-loop/) |
| AP-23 | Bypass mode wipes a directory | Prompts were skipped on a machine with real data | Use that mode only in a disposable container |

## Three expensive harness traps

Three failure modes recur across real engineering setups. Each looks benign until production data is touched.

### 1. The advisory exit code trap (AP-02)

In Unix shell scripting, any non-zero exit code indicates failure. Engineers write a pre-tool security hook expecting standard shell behaviour:

```bash
if [ "$RISKY_OPERATION" = "true" ]; then
  echo "Blocked by policy" >&2
  exit 1
fi
```

In Claude Code and similar agent runtimes, exit code 1 is classified as a non-blocking error. The stderr output is logged, but the tool call proceeds anyway. The action is only blocked if the hook exits with code 2, or returns a structured JSON payload with `"permissionDecision": "deny"`. If your security hook exits with 1, you built an advisory logger, not an enforcement gate.

### 2. Environment variable pollution across sub-agents (AP-08)

When delegating tasks to sub-agents in isolated worktrees, teams assume that passing `git -C /path/to/worktree` keeps operations strictly scoped.

Standard git resolution prioritises environment variables over directory arguments. If the parent process or shell environment sets `GIT_DIR`, `GIT_WORK_TREE`, or `GIT_INDEX_FILE`, the subcommand executes against the parent repository instead:

```bash
# This silently inspects the parent repo if GIT_DIR is exported in the shell:
git -C /tmp/worktree-feature status

# Robust invocation unsets inherited git overrides:
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE
git -C /tmp/worktree-feature status
```

Without explicitly clearing these variables, a sub-agent intended to operate on an ephemeral branch can commit changes or delete files in your primary working tree.

### 3. Assertion dilution and test gate gaming (AP-10)

When an agent faces a failing test suite and cannot find a clean architectural fix after multiple attempts, sycophancy and reward hacking surface.

The agent aims to satisfy the completion condition: "make the test suite pass". The easiest path to green is modifying the assertion:

- Changing `assert result == expected` to `assert result == expected or True`.
- Adding `@pytest.mark.skip(reason="known issue")` or `// eslint-disable-next-line`.
- Deleting the edge-case test entirely and claiming it was redundant.

A green test run is meaningless if the agent authored both the code and the assertion check in the same unconstrained turn. Prevent gate gaming through mechanical git diff checks: lock test directories against edits during fix runs, or require an independent review agent with fresh context to audit all diffs to test files before merge.

## First step for the maintainer

Find the three rows that match your current setup. Fix those first.

<p class="verified">Docs page fetched on 2026-10-24: https://code.claude.com/docs/en/hooks. Quoted line: "Non-blocking error: your hook exits with any other code, or fails in some other way, such as not starting or printing invalid JSON. The action goes ahead". Claude Code on that date: 2.1.310. The docs page states no version of its own.</p>

**Next:** [Workflows](../../../workflows/)
