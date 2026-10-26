---
title: Change control for the harness
description: Decide who may change an instruction file, hook or permission, review each change, manage model changes, respond to a failed guard and set retention.
---

*Deep dive for [level 7: Run it for real](../../../journey/07-run-it-for-real/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** treat the harness as production code. Name who may change an instruction file, a hook or a permission. Review each change in a small, single-concept commit, and test every hook change. Pin the model and rerun a fixed case set before you change it. When a guard fails, stop and add a test that fails first.

*Principle, not measured: this page is process advice. The guide ran no test of any of it and gives no numbers for it.*

## Why it matters

The files that steer an agent are also the files that limit it. An instruction file sets behaviour. A hook blocks a call. A permission rule allows one. A change to any of them changes what the agent can do next time, and a bad change gives no error: the agent just behaves differently. Ordinary change control applies, because these files are ordinary code with unusual reach.

## What to enable

**1. Name who may change each control.** Write a short table: the file or setting, the person who may approve a change, and whether an agent may edit it. A sound default is that an agent may propose a change to an instruction file, a hook or a permission and a named person approves it. Deny the agent's write access to those paths, as [permissions and sandboxing](../../control/permissions-and-sandboxing/) explains, so that an agent cannot widen its own limits.

**2. Review each change as code.** Keep it small and about one concept. Do not mix a new hook with a rewrite of the instruction file. For a hook, require a test that feeds it a call it must block, a call it must allow and an input it cannot read, as the [hooks page](../../control/hooks/) shows. For a permission, the commit message states what the rule now allows and why. For an instruction file, state the behaviour you want to change and the case that showed the need.

**3. Pin the model and rerun the cases before you change it.** A model name that points to "the latest" can change under you, and behaviour changes with it. Pin the name where your tool lets you. Keep a fixed set of cases with known good answers, as the [evals page](../../quality/evals/) describes. Before you switch, run the set on the old and the new model and compare case by case. Accept the change only when you have read every case that got worse. Record the model name and the date with the result.

**4. Respond to a failed guard in a fixed order.**

1. Stop the run. Do not let the agent continue to "fix" it.
2. Read the audit log and the transcript. Find what the agent did and which check was meant to catch it. See [observability](../observability/).
3. Name the missing check. Was there no guard, a guard with a gap, or a guard that was skipped?
4. Write a test that reproduces the failure and watch it fail.
5. Fix the guard until the test passes, then rerun the full gates.
6. Record the incident: what happened, the missing check and the new test. Keep the failure trail. Do not delete logs to tidy up.

**5. Set retention on purpose.** The [small-firm default](../../../journey/professional-guardrails/) has you read the tool's retention period and write it down. Past that default, decide per record how long you keep it. The records are the change history of the controls, the case-set results for each model change, the incident notes and the audit log. Your legal and regulatory duties set the period, not this guide. Write the period, the owner and the deletion step in one place. A harness that deletes transcripts on its own schedule may remove evidence you need, so copy out what you must keep, as [observability](../observability/) says.

## Failure modes it reduces

- An agent widens its own permissions.
- A hook change blocks the wrong calls, or none, and nobody notices.
- A model update changes behaviour and no one can say when.
- A failed guard is patched in place, and the same gap fails again.
- Evidence of an incident is deleted before anyone reads it.

## First step for the maintainer

Write the table from step 1 for your own setup, with one row per control. Then add one test to your most important hook.

**Next:** [Recommended baseline](../../reference/baseline/)
