---
title: The adoption path
description: A staged checklist for building a harness, ordered by effort and not by calendar.
---

*Deep dive for [level 7: Run it for real](../../../journey/07-run-it-for-real/).*

**Recommendation:** adopt in the order below. Each stage is cheap relative to the risk it removes, and each assumes the previous one is in place. Do not wait for a calendar. Move on when the exit check of a stage passes.

## Why it matters

Teams often start with the most visible feature, such as a fleet of parallel agents, and add guardrails after an incident. The reverse order costs less. Controls are small. Orchestration is large and amplifies every mistake that controls would have caught.

## Stage 1: bound the blast radius

- [ ] Run the agent in a repository with a clean working tree and a remote.
- [ ] Set a deny list for secrets files and a short allow list for routine commands. See [Permissions and sandboxing](../../control/permissions-and-sandboxing/).
- [ ] Turn on the sandbox for shell commands if your harness has one.

Exit check: the agent cannot read your secrets file and cannot reach a host you did not list.

## Stage 2: write the instructions

- [ ] Create one short project instruction file. See [Instruction files](../../context/instruction-files/).
- [ ] List the exact commands for build, test and lint.

Exit check: a fresh session runs the test command without being told.

## Stage 3: add enforcement

- [ ] Add a post-tool hook that formats or lints edited files.
- [ ] Add a pre-tool hook that blocks one dangerous action. See [Hooks](../../control/hooks/).
- [ ] Add a stop hook that runs the test suite.

Exit check: you can trigger each hook on purpose and see it fire.

## Stage 4: add review and gates

- [ ] Run types, lint and the full test suite in pre-commit and CI. See [Test-first and quality gates](../../quality/test-first-and-gates/).
- [ ] Review each change with a fresh-context reviewer. See [Independent review](../../quality/independent-review/).

Exit check: a deliberately broken change is rejected by a gate, not by you.

## Stage 5: delegate

- [ ] Hand bounded research tasks to sub-agents. See [Sub-agents](../../delegation/sub-agents/).
- [ ] Isolate any agent that writes files in its own worktree. See [Worktree isolation](../../delegation/worktree-isolation/).

Exit check: two agents work in parallel and neither changes the other's files.

## Stage 6: operate

- [ ] Keep an action log. See [Observability and audit trail](../../operations/observability/).
- [ ] Cap loops and heavy jobs. See [Cost and resource discipline](../../operations/cost-and-resources/).
- [ ] Write down which actions always need a person. See [Human-in-the-loop](../../operations/human-in-the-loop/).

Exit check: you can answer "what did the agent do yesterday?" from a file.

## Failure modes it prevents

Skipping to stage 5 gives you parallel agents with no tests, no review and no log. The first sign of trouble is a broken main branch that nobody can trace.

## Start here

Do stage 1 today. It takes minutes and it is the stage that limits damage from every later mistake.
