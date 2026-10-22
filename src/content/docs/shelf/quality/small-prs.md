---
title: Small PRs and trunk-based flow
description: Slice agent work into small, single-concern changes that a person can review in one sitting.
---

*Deep dive for [level 5: Check the work](../../../journey/05-check-the-work/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** target one concept per pull request, under about eight files and four hundred lines, with the test in the same change. Branch from trunk, keep branches short-lived and limit work in progress to one open change per concern.

## Why it matters

[Level 5](../../../journey/05-check-the-work/) explains why a person must check the work. An agent can produce thousands of lines in minutes. A reviewer cannot read them with the same care. A reviewer has limited attention per change, so a very large diff tends to be skimmed or left waiting. Small changes keep the human check real, and they limit how much one mistake can break.

## What to enable

**1. State the size budget.** Put the numbers in the instruction file, so the agent plans to them. The figures above are a starting target, taken from one team's practice. Adjust them to what your reviewers can hold in their heads.

**2. Slice vertically.** Each change delivers a thin end-to-end behaviour with its test, rather than a layer without a user. A migration, a model and a view for one small feature beat a pull request that adds all the models.

**3. One concern per change.** Separate refactors, behaviour changes and dependency bumps. If the agent notices an unrelated problem, it files an issue and does not fix it in this change.

**4. Slice as you go.** Plan the slices before you start. Cutting a large finished change into smaller ones afterwards wastes the review you already did and risks breaking it.

**5. Commit atomically.** One logical change per commit, with a message that says what changed and why. A clean history makes bisecting and reverting cheap.

**6. Short-lived branches off trunk.** Merge to the main branch often. Long-lived branches drift from trunk, and a large conflict needs product knowledge that the agent resolving it may not have.

**7. Limit work in progress.** One open change per concern. When review is the bottleneck, stop opening changes and clear the queue.

**8. Describe the change plainly.** A pull request description states the change and its consequences, plus what you deliberately left for another change. Keep local measurements and open questions out of it, because they read as facts about production. Put rationale in the commit message or the linked pull request, not in code comments, so it stays with the change.

**9. Keep the pipeline fast.** Fast feedback keeps slices small. If CI takes long, run the cheap checks first and start the long ones early.

## Failure modes it reduces

- A 3,000-line agent change is approved without being read.
- A bug hides in a refactor mixed into a feature.
- Two long-running branches conflict in ways nobody can resolve cleanly.
- Review becomes a queue, and agents keep adding to it.

## First step for the maintainer

Add one line to the instruction file: "Plan the work as slices of one concept, under eight files and four hundred lines each. Stop and ask before exceeding that."

**Next:** [Observability and audit log](../../operations/observability/)
