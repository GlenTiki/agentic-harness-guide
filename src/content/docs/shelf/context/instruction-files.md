---
title: Instruction files
description: How to layer, size and scope the files that tell an agent how your project works.
---

*Deep dive for [level 2: House rules](../../../journey/02-house-rules/).*

**Recommendation:** keep one short, project-level instruction file, and write it as a list of commands and non-obvious rules. Put it in `AGENTS.md` if you use more than one tool. Import it from a tool-specific file only where that tool needs its own filename. Target well under 200 lines.

## Why it matters

The harness loads the instruction file into every session. Every line costs context on every turn, and a long file dilutes the lines that matter. The model also treats the file as advice. It is not enforcement, so anything that must hold belongs in a [hook](../../control/hooks/) or a [permission rule](../../control/permissions-and-sandboxing/).

## What to enable

**1. Use layers, closest wins in practice.** Two common conventions exist. Claude Code loads `CLAUDE.md` from your home directory, then from each directory from the filesystem root down to the working directory, and concatenates them. Codex CLI reads `AGENTS.md` from its home directory, then from the project root down to the working directory, one file per directory, and concatenates those. In both, text nearer the working directory comes later and tends to win a conflict. Put personal preferences in the home file, team rules at the repository root, and package-specific rules in the package directory.

**2. Share one file across tools.** `AGENTS.md` is an open convention read by many tools. Claude Code reads `AGENTS.md` directly only when no `CLAUDE.md` exists in the working directory or above it. If you need both, make the tool-specific file a thin wrapper that imports the shared one:

```markdown
@AGENTS.md

## Tool-specific notes
Keep only the settings that apply to this one tool here.
```

**3. Use imports to split, not to grow.** Claude Code expands `@path/to/file` imports at launch, and imports can nest up to four levels. Imported files load every session, so an import saves you from editing one big file but does not save context. For rules that apply to part of the tree, use path-scoped rule files or nested instruction files that load on demand.

**4. Write for a reader with no history.** State the command, not the aspiration:

```markdown
## Commands
- Test: `make test`
- Lint and types: `make check`

## Rules
- Never edit files under `generated/`. Regenerate with `make gen`.
- Migrations go through `make migrate`, never by hand.
```

**5. Leave out what the harness already knows or can discover.** Omit language tutorials, a tour of the directory tree that `ls` shows, and style rules that a formatter enforces. Omit anything that changes weekly. Omit secrets.

## Failure modes it prevents

- The agent guesses the test command and runs the wrong suite.
- Two files give conflicting rules and the agent picks one at random. Review the layers together when you edit any of them.
- A 600-line file buries the one rule that matters, and adherence drops.
- Codex stops adding files once the combined instructions reach its size limit, which defaults to 32 KiB. Content past the limit is silently absent.

## Start here

Write `AGENTS.md` with three sections: commands, rules the agent cannot discover, and where specs live. Run a fresh session and ask it to run the tests. If it succeeds without help, the file works.

<p class="verified">Verified against the Claude Code memory documentation (code.claude.com/docs/en/memory), the Codex AGENTS.md guide (learn.chatgpt.com/docs/agent-configuration/agents-md) and agents.md on 2026-10-22.</p>
