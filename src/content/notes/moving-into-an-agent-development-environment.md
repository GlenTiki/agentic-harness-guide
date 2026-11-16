---
title: Moving my harness into an agent development environment
description: What changed, what broke on the first night, and what I would do again after moving my agent sessions into an agent development environment.
publishedAt: "2026-11-16T22:20:16Z"
draft: true
---

On 12 and 13 November I decided to stop hosting my own agent sessions. My setup had grown a dashboard chat that resumed agent sessions, and hooks that kept each agent in its own worktree. An [agent development environment](../../setup/one-workspace-per-task/) hosts any agent that runs in a terminal, each in its own worktree. So the plan gives the environment the agent hosting, and my hooks stay where they are. My own code shrinks to the parts that are specific to me: the [memory](../../setup/second-brain/) and the preferences. That move is still in progress.

The first change to this guide's repository after that decision was four lines: a setup script that every new worktree runs. It installs from the lockfile at low priority, and stops at the first error.

## What broke on the first night

An agent worked on this guide overnight, in small pull requests. Four things went wrong outside the writing.

1. **A check failed on `main`.** The site's health file must be less than 14 days old. It was last written on 25 October, so by 16 November `npm run check` failed. A time-based check fails during any pause, so it needs a scheduled refresh. Until then, it needs a note that says how to refresh it.
2. **Two agents ran the full check in one folder.** A reviewer ran `npm run check` in the shared checkout while the author's run was in progress. One run reported 159 links that did not resolve, and a later one reported 11 missing anchors. Both checks passed when they ran alone. A reviewer that runs commands needs its own worktree, the same as an author.
3. **The second-provider reviewer hit its usage limit.** The night's reviews came from the same provider. Each pull request says so. A review from the same provider is still useful, but it is not the independent check I wanted.
4. **An ignore rule for private files reached only the top folder.** In another of my repositories, private notes in subfolders were one `git add -A` away from a commit. A read-only audit found it before anything was committed.

## What I would do again

- Check in the setup script first. Every later worktree depends on it.
- Keep one concept per pull request, and stack each one on the fix that makes the checks pass.
- Record the reviewer, the findings and each resolution in the pull request thread.
