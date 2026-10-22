---
title: Human-in-the-loop
description: Decide in advance which actions always need a person, and batch the decisions so approvals stay meaningful.
---

*Deep dive for [level 4: Trust, but verify](../../../journey/04-trust-but-verify/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** run reversible, local work unattended and require a person for irreversible or outward-facing actions. Write the list down. Batch routine questions into one form, and ask a person only for what an agent cannot decide.

## Why it matters

Approval has a cost, and [level 4](../../../journey/04-trust-but-verify/) names it approval fatigue. Ask too often and people click through without reading, which is worse than not asking. Ask too rarely and an agent takes an action that cannot be undone. A written list puts the attention where the risk is.

## What to enable

**1. Always confirm these.** Treat the following as requiring explicit approval from a person in the active session:

- Pushing to a shared remote, and force-pushing anywhere.
- Opening or merging a pull request on a repository you do not own.
- Spending money or changing billing.
- Sending any message to another person: email, chat, a comment on an issue.
- Deleting data, dropping tables or removing logs and failure records.
- Writing credentials to disk or widening an access scope.
- Turning off a safety control, a hook or a capability gate. The mechanism is a denied write to the settings files, hook scripts and capability registry, plus a check that fails when they change. See [Permissions and sandboxing](../../control/permissions-and-sandboxing/).

**2. Apply the list in the harness.** Do not rely on the agent remembering it. Claude Code behaviour: an `ask` permission rule such as `Bash(git push *)` makes the harness prompt for the commands it matches. It does not match every way to write the same command, so add a pre-tool hook that parses the command where the action matters. See [Permissions and sandboxing](../../control/permissions-and-sandboxing/) and [Hooks](../../control/hooks/).

**3. Separate drafting from sending.** The agent drafts a message, a pull request or a command. A person authorises the send. This fits any outward action and costs little.

**4. Make the ask self-contained.** A question should carry its own context: the situation, the options, a recommendation and what happens next. A person who returns after a break should be able to answer without reading the history. Lead with the recommendation.

**5. Batch decisions.** When three or more decisions stack up, put them in one form or one message with a recommendation for each, instead of interrupting one at a time. Reserve single questions for blockers.

**6. Do not end a turn on an open question you could have asked with a tool.** If your harness has a structured question tool, use it, so the answer comes back in the same session.

**7. Ask once.** An approval for an action stays valid for the same action in the same scope. Do not re-ask for it, and do not stretch it to cover a wider scope.

**8. Keep explicit holds in force.** If a person says "wait", nothing in the agent's plan overrides that, including a passing review.

## Failure modes it reduces

- An agent force-pushes over a colleague's work.
- A drafted email is sent because no step required confirmation.
- Approval fatigue turns every prompt into a reflex "yes".
- A person returns to ten unrelated questions with no context.

## First step for the maintainer

Copy the confirm list above into your instruction file. Then add an `ask` rule for `git push` so the harness prompts for the first item.

<p class="verified">Docs page fetched on 2026-10-22: https://code.claude.com/docs/en/permissions. Quoted line: "Content-scoped ask rules like `Bash(git push *)` still force a prompt". Claude Code on that date: 2.1.309. The docs page states no version of its own.</p>

**Next:** [Recommended baseline](../../reference/baseline/)
