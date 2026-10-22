---
title: Human-in-the-loop
description: Decide in advance which actions always need a person, and batch the decisions so approvals stay meaningful.
---

**Recommendation:** run reversible, local work unattended and require a person for irreversible or outward-facing actions. Write the list down. Batch routine questions into one form, and ask a person only for what an agent cannot decide.

## Why it matters

Approval has a cost. Ask too often and people click through without reading, which is worse than not asking. Ask too rarely and an agent takes an action that cannot be undone. A written list puts the attention where the risk is.

## What to enable

**1. Always confirm these.** Treat the following as requiring explicit approval from a person in the active session:

- Pushing to a shared remote, and force-pushing anywhere.
- Opening or merging a pull request on a repository you do not own.
- Spending money or changing billing.
- Sending any message to another person: email, chat, a comment on an issue.
- Deleting data, dropping tables or removing logs and failure records.
- Writing credentials to disk or widening an access scope.
- Turning off a safety control, a hook or a capability gate.

**2. Enforce the list.** Do not rely on the agent remembering it. Use `ask` permission rules and pre-tool hooks for the commands involved, so the harness prompts. See [Permissions and sandboxing](../../control/permissions-and-sandboxing/) and [Hooks](../../control/hooks/).

**3. Separate drafting from sending.** The agent drafts a message, a pull request or a command. A person authorises the send. This fits any outward action and costs little.

**4. Make the ask self-contained.** A question should carry its own context: the situation, the options, a recommendation and what happens next. A person who returns after a break should be able to answer without reading the history. Lead with the recommendation.

**5. Batch decisions.** When three or more decisions stack up, put them in one form or one message with a recommendation for each, instead of interrupting one at a time. Reserve single questions for blockers.

**6. Do not end a turn on an open question you could have asked with a tool.** If your harness has a structured question tool, use it, so the answer comes back in the same session.

**7. Ask once.** An approval for an action stays valid for the same action in the same scope. Do not re-ask for it, and do not stretch it to cover a wider scope.

**8. Keep explicit holds in force.** If a person says "wait", nothing in the agent's plan overrides that, including a passing review.

## Failure modes it prevents

- An agent force-pushes over a colleague's work.
- A drafted email is sent because no step required confirmation.
- Approval fatigue turns every prompt into a reflex "yes".
- A person returns to ten unrelated questions with no context.

## Start here

Copy the confirm list above into your instruction file. Then add an `ask` rule for `git push` so the harness enforces the first item.
