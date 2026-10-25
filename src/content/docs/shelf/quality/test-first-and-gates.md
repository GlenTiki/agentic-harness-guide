---
title: Test-first and quality gates
description: Write the failing test first, and run the same automated gates locally and in CI on every change.
---

*Deep dive for [level 5: Check the work](../../../journey/05-check-the-work/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** have the agent write a failing test before it writes the code, and run one fixed set of gates on every change: types, lint, formatting, complexity and the full test suite. Run them in a pre-commit hook and again in CI. Never skip a hook to get a commit through.

## Why it matters

[Level 5](../../../journey/05-check-the-work/) introduces the test. A command can exit with status 0 and still be wrong: weakening a test or special-casing an input also gives green. The guide did not measure how often an agent does this. A failing test written first defines the target. Automated gates define the floor. Together they make "done" something a machine can check.

## What to enable

**1. Red, green, refactor.** Instruct the agent to write the test, run it, and confirm it fails for the right reason before implementing. A test that has never failed has not proved anything.

**2. One command for all gates.** Give the project a single entry point, so the agent, the hook and CI all run the same thing:

```make
check:
	ruff check .
	ruff format --check .
	mypy --strict src
	pytest -q
```

Substitute your own tools. The principle is the same set everywhere.

**3. Pick gates that are deterministic.** A gate does not read the agent's argument. Static types, a linter, a formatter, a cyclomatic complexity limit and the full suite all give the same verdict for the same input. Set a complexity ceiling per function so a large change is harder to hide in one dense routine.

**4. Run them at three points.** In the agent loop, through a post-edit hook for the quick ones and a stop hook for the full suite. In pre-commit, so a red commit is rejected where the hook runs. In CI, so a red push fails the required check. See [Hooks](../../control/hooks/).

**5. Never skip hooks.** Do not use flags that bypass pre-commit. If a hook fails, fix the cause. If the hook is wrong, fix the hook in its own change. Tell the agent this in the instruction file. If you want the harness to refuse it, add a pre-tool hook that blocks a command containing the bypass flag. The hook covers only commands it sees, as the [hooks page](../../control/hooks/) explains.

**6. Test behaviour, not implementation.** Assert whole outcomes. Prefer full equality over a substring check, which passes when extra wrong content is present.

**7. Inject dependencies instead of patching.** Pass the clock, the client and the file path as parameters with production defaults. Tests then pass fakes without reaching into other modules. When a test needs to patch an internal name, the code is missing a seam.

**8. Watch for gate gaming.** Review test diffs as closely as code diffs. Flag deleted assertions, widened tolerances, new skip markers and new lint suppressions.

## Failure modes it reduces

- A "fix" turns the suite green by deleting the failing assertion.
- Code lands that passes locally and fails in CI because the commands differ.
- A hook failure leads to `--no-verify`, and the next bug ships.
- A test passes before the fix exists, so it never guarded anything.

## First step for the maintainer

Create the single `check` command. Wire it to a pre-commit hook and to your CI workflow. Add one line to your instruction file: "Run `make check` before declaring any task done."

<p class="verified">Docs page fetched on 2026-10-24: https://code.claude.com/docs/en/hooks. Quoted line: "Blocking error: your hook exits 2." Claude Code on that date: 2.1.310. The docs page states no version of its own.</p>

**Next:** [Independent review](../independent-review/)
