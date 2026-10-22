---
title: Recommended baseline
description: The minimum viable harness as one checklist.
---

*Deep dive for [level 8: Design anything](../../../journey/08-design-anything/).*

**Recommendation:** treat this list as the floor for any repository where an agent can edit code. Each item links to the page that explains it. Add the rest of the guide as your risk grows.

## The checklist

### Boundaries

- [ ] Deny rules cover secrets files and credential directories. [Permissions and sandboxing](../../control/permissions-and-sandboxing/)
- [ ] The shell sandbox is on, with an empty network allow list plus the hosts your build needs.
- [ ] Skip-all-prompts modes are disabled, or confined to a disposable environment.
- [ ] Every external action has a capability switch, default off. [Capability gating](../../control/capability-gating/)

### Instructions and memory

- [ ] One short project instruction file with build, test and lint commands. [Instruction files](../../context/instruction-files/)
- [ ] The file states which channels carry authority. [Untrusted input](../../control/untrusted-input/)
- [ ] A ledger file holds intent and decisions. [Context management](../../context/context-management/)
- [ ] Memory is refined in place and reviewed monthly. [Memory](../../context/memory/)

### Enforcement

- [ ] A post-tool hook formats or lints edited files. [Hooks](../../control/hooks/)
- [ ] A pre-tool hook blocks the one action you fear most, using exit code 2 or a deny decision.
- [ ] A stop hook runs the test suite.
- [ ] An action log is written by a hook. [Observability](../../operations/observability/)

### Quality

- [ ] One `check` command runs types, lint, format, complexity and tests. [Test-first and quality gates](../../quality/test-first-and-gates/)
- [ ] The same command runs in pre-commit and CI, and nobody skips hooks.
- [ ] Non-trivial changes start from a one-page spec. [Spec-driven development](../../quality/spec-driven-development/)
- [ ] Each change is reviewed by a fresh-context reviewer, with the verdict bound to the diff digest. [Independent review](../../quality/independent-review/)
- [ ] Each model-driven step has an eval. [Evals](../../quality/evals/)
- [ ] Changes are small, single-concern and tested. [Small PRs](../../quality/small-prs/)

### Delegation

- [ ] Sub-agents get bounded briefs and return summaries. [Sub-agents](../../delegation/sub-agents/)
- [ ] Write-capable agents run in their own worktrees. [Worktree isolation](../../delegation/worktree-isolation/)
- [ ] Each MCP server is reviewed, pinned and least-privilege. [MCP servers](../../delegation/mcp-servers/)

### Operations

- [ ] Every loop, poll and retry has a bound. [Cost and resource discipline](../../operations/cost-and-resources/)
- [ ] Pushes, spend, outbound messages and destructive operations need a person. [Human-in-the-loop](../../operations/human-in-the-loop/)

## Failure modes it prevents

Each unchecked box corresponds to a row in [Anti-patterns](../anti-patterns/). If you can name which row you are exposed to, you know which item to do next.

## Start here

Check what you already have. Do the first unchecked item under Boundaries, then Enforcement, then Quality.
