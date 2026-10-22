---
title: Spec-driven development
description: Write a short spec before the agent writes code, and make the spec the contract for tests and review.
---

*Deep dive for [level 5: Check the work](../../../journey/05-check-the-work/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** for any change larger than a few lines, write a one-page spec first. Put it in the repository, have a second agent or person challenge it, and trace every test and commit back to it. Skip the spec for trivial edits.

## Why it matters

[Level 5](../../../journey/05-check-the-work/) calls this the definition of done. An agent produces plausible code from whatever it is given. When the request is vague, the code is plausible and wrong in ways that are hard to see in a diff. A spec forces the decisions into text that you can review before any code exists, when changing your mind is cheap.

## What to enable

**1. A standard spec shape.** Keep it to one page:

```markdown
# <Change name>

## Intent
One paragraph: what changes for whom, and why.

## Acceptance criteria
- Given X, when Y, then Z. (Each one maps to a test.)

## Out of scope
- Things a reader might assume are included.

## Failure behaviour
- What happens on duplicate calls, retries, partial writes, a dependency being down.

## Open questions
- Each has an owner.
```

**2. Challenge the spec.** Ask a second agent, ideally from a different provider, to find missing criteria, ambiguous wording and unstated assumptions. Resolve each finding in the text. The [independent review](../independent-review/) page covers why a fresh context matters.

**3. Write acceptance criteria that a test can check.** "Handles errors well" is not checkable. "Returns 503 with a retry-after header when the database is unreachable" is.

**4. Include failure behaviour.** Name the edge cases up front: concurrent calls, duplicates and retries, stale state, cancellation, restart and resource exhaustion. For each, state the expected behaviour and the test that proves it. Keep the solution proportionate to measured load, and do not design for scale you have not measured.

**5. Trace work to the spec.** Reference the spec in the branch name, the commit messages and the pull request. When scope shifts, update the spec first. The spec is the contract.

**6. List rejected alternatives.** One line per option you considered and why you dropped it. This saves the next reader, human or agent, from re-proposing it.

**7. Keep the spec where agents read it.** A path in the instruction file is enough: "Specs live in `docs/specs/`. Read the relevant one before changing code."

## Failure modes it reduces

- The agent solves a different problem from the one you meant.
- Scope grows silently during implementation.
- Tests assert whatever the code does, because nothing else defined correct.
- A reviewer cannot tell whether a behaviour is a bug or a decision.

## First step for the maintainer

For the next non-trivial change, write only the Intent and Acceptance criteria sections, and ask the agent to turn each criterion into a failing test before it writes the implementation.

**Next:** [Test-first and quality gates](../test-first-and-gates/)
