---
title: AGENTS.md vs CLAUDE.md files
description: "AGENTS.md vs CLAUDE.md: layer, size and scope the instruction files that tell an agent how your project works, and share one file across tools."
---

*Deep dive for [level 2: House rules](../../../journey/02-house-rules/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** keep one short, project-level instruction file, and write it as a list of commands and non-obvious rules. Put it in `AGENTS.md` if you use more than one tool. Import it from a tool-specific file only where that tool needs its own filename. Target well under 200 lines.

## Why it matters

The harness loads the instruction file into every session. Every line costs context on every turn, and a long file dilutes the lines that matter. The model also treats the file as advice, as [level 2](../../../journey/02-house-rules/) explains. The file does not block anything, so a rule that must hold on every call belongs in a [hook](../../control/hooks/) or a [permission rule](../../control/permissions-and-sandboxing/).

## What to enable

**1. Use layers, and remove conflicts.** Two common conventions exist. Claude Code behaviour: it loads your organisation's managed file, if there is one, and your user file at `~/.claude/CLAUDE.md`. Then it loads `CLAUDE.md` and `CLAUDE.local.md` from each directory, from the filesystem root down to the working directory, and concatenates them. A file in a subdirectory below the working directory loads later, when the agent works in that subdirectory. Codex CLI reads `AGENTS.md` from its home directory (`~/.codex` by default), then from the project root down to the working directory, one file per directory, and concatenates those. In both, text nearer the working directory comes later. The Codex docs say later files override earlier guidance. The Claude Code docs say that when two instructions contradict each other, Claude may pick one arbitrarily. Do not depend on the order. Remove the conflict. Put personal preferences in the home file, team rules at the repository root, and package-specific rules in the package directory.

**2. Share one file across tools.** `AGENTS.md` is an open convention read by many tools. Claude Code v2.1.277 or later reads `AGENTS.md` directly, and by default only when no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` exists in the working directory or above it. If one exists, only the `CLAUDE.md` files are read, unless one of them imports `AGENTS.md` or you change the project instructions setting. If you need both, make the tool-specific file a thin wrapper that imports the shared one:

```markdown
@AGENTS.md

## Tool-specific notes
Keep only the settings that apply to this one tool here.
```

**3. Use imports to split, not to grow.** Claude Code expands `@path/to/file` imports at launch, and imports can nest to a "maximum depth of four hops". Imported files load every session, so an import saves you from editing one big file but does not save context. For rules that apply to part of the tree, use path-scoped rule files or nested instruction files that load on demand.

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

## Learn the controls you already have

Before adding another instruction file, inspect your agent's settings and help. Find the active model, output style, loaded instructions, enabled tools and permission mode. Check whether a change affects this session, this project or every project. Save the old value before changing it.

In the **Claude Code terminal**, `/config` opens a settings dialog. It is not a complete view of `settings.json`. Output styles are one useful control: select one there, or use `/output-style`. Style-file edits need a restart. If you customise a style for coding, read the reference on `keep-coding-instructions` before relying on it. See the [settings guide](https://code.claude.com/docs/en/settings) and [output-style reference](https://code.claude.com/docs/en/output-styles).

In **Codex**, personal settings live in `~/.codex/config.toml`; trusted projects can supply `.codex/config.toml` overrides. Reusable working instructions belong in `AGENTS.md`, with personal defaults under `~/.codex` unless you changed its home. Configuration settings and a working agreement are different things. Use the [configuration guide](https://learn.chatgpt.com/docs/config-file/config-basic) to check the controls your client supports; do not assume Claude's slash commands transfer.

Use a settings screen or local editor to prepare a small excerpt first. Remove credentials, account identifiers and private paths before sharing it. Do not attach a whole configuration file: it may contain secrets. Then ask:

```text
Review only the redacted settings excerpt and working rules I paste below.
Do not open other files, retrieve credentials or change settings.
Which setting or instruction could reduce needless clarification questions?
Show its scope, any conflicting rule and how I would undo the change.
Mark anything you cannot inspect as unknown.
```

Check its answer against the files or settings screen. Then change one thing and try an ordinary task and a task that needs your decision. A reply that repeats the rule proves less than behaviour that follows it. The [Mako example](../../../method/product-manager-and-team-lead/#configure-the-working-relationship) shows a working agreement you can adapt.

<p class="verified">Documentation checked on 2026-11-04: <a href="https://code.claude.com/docs/en/settings">Claude Code settings</a>, <a href="https://code.claude.com/docs/en/output-styles">output styles</a>, <a href="https://learn.chatgpt.com/docs/config-file/config-basic">Codex configuration</a> and <a href="https://learn.chatgpt.com/docs/agent-configuration/agents-md">Codex instructions</a>. The output-style page says: "Run `/output-style &lt;style&gt;` in the terminal, or run `/config` and select your style under Output style." The Codex configuration page says: "For security, Codex loads project `.codex/` layers only when you trust the project." Locally installed clients: Claude Code 2.1.318 and Codex CLI 0.166.0. The pages do not identify a release version. These are documented controls, not an executed comparison of their effects.</p>

## Failure modes it reduces

- The agent guesses the test command and runs the wrong suite.
- Two layers give conflicting rules, and nothing defines which one the agent follows. Review the layers together when you edit any of them, and remove the conflict.
- A 600-line file buries the one rule that matters, and adherence drops.
- Codex stops adding files once the combined instructions reach its size limit, which defaults to 32 KiB. Content past the limit is silently absent.

## First step for the maintainer

Write `AGENTS.md` with three sections: commands, rules the agent cannot discover, and where specs live. Run a fresh session and ask it to run the tests. If it succeeds without help, the file works.

<p class="verified">Docs page fetched on 2026-11-02: https://code.claude.com/docs/en/memory. Quoted line: "By default, Claude reads `AGENTS.md` only when you have no `CLAUDE.md` in your working directory or above it." Claude Code on that date: 2.1.316. The docs page states no version of its own. The same page gives a feature floor: "Reading `AGENTS.md` directly requires Claude Code v2.1.277 or later."</p>

<p class="verified">Docs page fetched on 2026-11-02: https://learn.chatgpt.com/docs/agent-configuration/agents-md (the Codex AGENTS.md guide, which https://developers.openai.com/codex/guides/agents-md redirects to). Quoted line: "Files closer to your current directory override earlier guidance because they appear later in the combined prompt." The same page gives the size limit: "`project_doc_max_bytes` (32 KiB by default)". Codex CLI on that date: 0.166.0. The docs page states no version of its own.</p>

**Next:** [Prompt structure and validation](../prompt-structure/)
