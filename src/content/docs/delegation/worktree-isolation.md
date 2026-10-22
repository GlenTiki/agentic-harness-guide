---
title: Worktree isolation
description: Give every agent that writes files its own checkout so parallel work cannot collide.
---

**Recommendation:** run each write-capable agent in its own git worktree on its own branch. Read-only agents can share the main checkout. Name the base branch explicitly and check it before you merge.

## Why it matters

Two agents in one working directory share the same files, the same index and the same `HEAD`. One agent's `git checkout` or `git stash` changes what the other sees. The symptoms are confusing: edits that disappear, commits on the wrong branch, tests that fail for a reason nobody introduced. A worktree is a second checkout of the same repository, so each agent gets its own files and branch while sharing history.

## What to enable

**1. Create one worktree per writer.**

```bash
git worktree add ../repo-feature-a -b agent/feature-a main
git worktree add ../repo-feature-b -b agent/feature-b main
```

**2. Let the harness do it if it can.** In Claude Code, a sub-agent with `isolation: worktree` in its frontmatter runs in a temporary worktree. The worktree is cleaned up automatically if the agent makes no changes. When it does make changes, you get the branch and path back to review.

**3. Know where the worktree branches from.** In Claude Code the worktree branches from your default branch, not from the parent session's current `HEAD`. If the lead agent is on an unmerged feature branch, the isolated agent does not see that work. Either merge first, or tell the agent the base in the brief and check it afterwards:

```bash
git merge-base --is-ancestor <base-commit> <agent-branch> && echo "based on the right commit"
```

**4. Keep each worktree's identity clear.** Give worktrees a path and a branch name that say who owns them. Do not nest one inside another.

**5. Beware of environment variables that point git elsewhere.** If `GIT_DIR` or `GIT_WORK_TREE` is set in the shell, `git -C <path>` still operates on the repository those variables name. Unset them in scripts and in agent briefs, or pass them explicitly.

**6. Sequence writers on the same files.** Worktrees stop file collisions, not merge conflicts. If two agents edit the same function, you resolve it at merge. Split the work by file or module instead.

**7. Merge deliberately, then clean up.** Review each branch like any other change. A squash merge does not make the agent branch an ancestor of main, so judge "merged" by the pull request, not by ancestry. Remove the worktree with `git worktree remove`, and delete the branch separately.

## Failure modes it prevents

- Parallel agents overwrite each other's edits.
- An agent works from a stale base and its changes conflict with everything.
- A cleanup command run in the wrong directory deletes someone else's work.
- A leftover worktree holds a branch you want to reuse.

## Start here

Before the next parallel task, create two worktrees by hand, point one agent at each, and merge both back. You will see the base-branch behaviour first-hand.

<p class="verified">Verified against the Claude Code sub-agents documentation (code.claude.com/docs/en/sub-agents) on 2026-10-22.</p>
