---
title: Worktree isolation
description: Give every agent that writes files its own checkout so parallel work cannot collide.
---

*Deep dive for [level 6: Hire a team](../../../journey/06-hire-a-team/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** run each write-capable agent in its own git worktree on its own branch. Read-only agents can share the main checkout. Name the base branch explicitly and check it before you merge.

## Why it matters

Two agents in one working directory share the same files, the same index and the same `HEAD`. One agent's `git checkout` or `git stash` changes what the other sees. The symptoms are confusing: edits that disappear, commits on the wrong branch, tests that fail for a reason nobody introduced. A worktree is a second checkout of the same repository, so each agent gets its own files and branch while sharing history.

A worktree isolates files. It does not isolate ports, development databases, containers, package caches, lockfile installs, environment files or external services. Two agents in two worktrees can still start a server on the same port, migrate the same database or install over the same cache. Give each worktree its own port range, its own database name suffix and its own ephemeral containers. [Level 6](../../../journey/06-hire-a-team/) makes the same point for helpers.

## What to enable

**1. Create one worktree per writer.**

Example, do not run:

```bash
git worktree add ../repo-feature-a -b agent/feature-a main
git worktree add ../repo-feature-b -b agent/feature-b main
```

**2. Let the harness do it if it can.** Claude Code behaviour: a sub-agent with `isolation: worktree` in its frontmatter runs in a temporary worktree. The worktree is cleaned up automatically if the agent makes no changes. When it does make changes, you get the branch and path back to review.

**3. Know where the worktree branches from.** Claude Code behaviour: the worktree branches from your default branch, not from the parent session's current `HEAD`. If the lead agent is on an unmerged feature branch, the isolated agent does not see that work. Either merge first, or tell the agent the base in the brief and check it afterwards:

```bash
git merge-base --is-ancestor <base-commit> <agent-branch> && echo "based on the right commit"
```

**4. Keep each worktree's identity clear.** Give worktrees a path and a branch name that say who owns them. Do not nest one inside another.

**5. Beware of environment variables that point git elsewhere.** If `GIT_DIR` or `GIT_WORK_TREE` is set in the shell, `git -C <path>` still operates on the repository those variables name. Unset them in scripts and in agent briefs, or pass them explicitly.

**6. Sequence writers on the same files.** Worktrees stop file collisions, not merge conflicts. If two agents edit the same function, you resolve it at merge. Split the work by file or module instead.

**7. Merge deliberately, then clean up.** Review each branch like any other change. A squash merge does not make the agent branch an ancestor of main, so judge "merged" by the pull request, not by ancestry. Remove the worktree with `git worktree remove`, and delete the branch separately.

## Failure modes it reduces

- Parallel agents overwrite each other's edits.
- An agent works from a stale base and its changes conflict with everything.
- A cleanup command run in the wrong directory deletes someone else's work.
- A leftover worktree holds a branch you want to reuse.
- Two worktrees collide on a port or a database that the checkout did not isolate.

## First step for the maintainer

Before the next parallel task, create two worktrees by hand, point one agent at each, and merge both back. You will see the base-branch behaviour first-hand.

<p class="verified">Docs page fetched on 2026-10-22: https://code.claude.com/docs/en/sub-agents. Quoted line: "Set to `worktree` to run the subagent in a temporary git worktree, giving it an isolated copy of the repository branched by default from your default branch rather than the parent session's `HEAD`." Claude Code on that date: 2.1.309. The docs page states no version of its own.</p>

**Next:** [Skills](../skills/)
