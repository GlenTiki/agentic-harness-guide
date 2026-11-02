---
title: Anti-patterns
description: Common harness mistakes as a table of symptom, cause and fix.
---

*Deep dive for [level 8: Design anything](../../../journey/08-design-anything/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** use this table to diagnose a problem by its symptom. Each row has an id, names the mechanism behind it, then gives the fix. Rules that live only in a prompt are requests; [level 4](../../../journey/04-trust-but-verify/) explains why.

| ID | Symptom | Cause | Fix |
| --- | --- | --- | --- |
| AP-01 | The agent breaks a rule you wrote | The rule is advice in an instruction file: the agent reads it as context, and nothing enforces it | Move it into a [hook](../../control/hooks/) or [permission rule](../../control/permissions-and-sandboxing/), which the harness applies on the calls it covers |
| AP-02 | A hook exists but the bad action still happens | Claude Code behaviour: the script exits 1, or fails to start, which is a non-blocking error by default | Exit 2 to block, or exit 0 with a deny decision. Set `onFailure` to `block` so a crash also blocks |
| AP-03 | Adherence drops as the instruction file grows | Every line competes for attention on every turn | Cut to commands and non-obvious rules, and scope the rest to paths |
| AP-04 | Two instruction layers give conflicting orders | Layers are concatenated, and nothing defines which of two conflicting rules the agent follows | Review the layers together and remove the conflict |
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

These three rows look harmless in a quick test. Each costs the most once real data is involved.

### 1. The advisory exit code trap (AP-02)

In Unix shell scripting, any non-zero exit code indicates failure. Engineers write a pre-tool security hook expecting standard shell behaviour:

```bash
if [ "$RISKY_OPERATION" = "true" ]; then
  echo "Blocked by policy" >&2
  exit 1
fi
```

In Claude Code, exit code 1 is a non-blocking error by default. A notice shows the first line of stderr, and the tool call goes ahead. A pre-tool hook blocks the call when it exits with code 2, or when it exits 0 and prints JSON with `"permissionDecision": "deny"`. From v2.1.295 you can also set `"onFailure": "block"` on the hook. Then a crash, a timeout, a script that does not start or any exit code other than 0 and 2 blocks the call too. Without one of these, a security hook that exits 1 only logs.

### 2. Environment variable pollution across sub-agents (AP-08)

When delegating tasks to sub-agents in isolated worktrees, teams assume that passing `git -C /path/to/worktree` keeps operations strictly scoped.

`git -C` changes the directory git starts in. It does not override the environment. If the parent process sets `GIT_DIR`, git uses that repository whatever the directory, so a commit lands in the parent's history. If it also sets `GIT_WORK_TREE`, git reads and writes the parent's files as well:

```bash
# With GIT_DIR exported, this uses the parent repository, not the worktree:
git -C /tmp/worktree-feature status

# Clear inherited git overrides first:
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR
git -C /tmp/worktree-feature status
```

Without explicitly clearing these variables, a sub-agent intended to operate on an ephemeral branch can commit changes or delete files in your primary working tree.

### 3. Assertion dilution and test gate gaming (AP-10)

Principle, not measured: an agent that faces a failing test suite and cannot find a clean fix after several attempts may change the test instead of the code.

The agent aims to satisfy the completion condition: "make the test suite pass". The easiest path to green is modifying the assertion:

- Changing `assert result == expected` to `assert result == expected or True`.
- Adding `@pytest.mark.skip(reason="known issue")` or `// eslint-disable-next-line`.
- Deleting the edge-case test entirely and claiming it was redundant.

A green run proves little when the same agent changed both the code and its assertions in one unchecked turn. Prevent gate gaming with mechanical diff checks: lock test directories against edits during fix runs, or have a fresh-context reviewer read every diff to a test file before merge.

## First step for the maintainer

Find the three rows that match your current setup. Fix those first.

<p class="verified">Docs page fetched on 2026-11-02: https://code.claude.com/docs/en/hooks. Quoted line: "Non-blocking error: your hook exits with any other code, or fails in some other way, such as not starting or printing invalid JSON. The action goes ahead, except for hooks whose failure blocks the action". Claude Code on that date: 2.1.316. The docs page states no version of its own. The same page gives a feature floor for `onFailure`: "Requires Claude Code v2.1.295 or later."</p>

**Next:** [Workflows](../../../workflows/)
