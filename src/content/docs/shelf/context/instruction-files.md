---
title: "Instruction files: AGENTS.md and others"
description: "Layer, size and scope the instruction files that tell an agent how your project works, and share one file across several agents."
---

*Deep dive for [level 2: House rules](../../../journey/02-house-rules/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** keep one short, project-level instruction file, and write it as a list of commands and non-obvious rules. Put it in `AGENTS.md` if you use more than one tool. Import it from a tool-specific file only where that tool needs its own filename. Target well under 200 lines.

## Why it matters

The harness loads the instruction file into every session. Every line costs context on every turn, and a long file dilutes the lines that matter. The model also treats the file as advice, as [level 2](../../../journey/02-house-rules/) explains. The file does not block anything, so a rule that must hold on every call belongs in a [hook](../../control/hooks/) or a [permission rule](../../control/permissions-and-sandboxing/).

## What to enable

**1. Use layers, and remove conflicts.** Most agents read instruction files at more than one level: a personal file in your home directory, a file for the repository and files for parts of the tree. GitHub Copilot CLI is the worked example here. It reads your personal file at `~/.copilot/copilot-instructions.md`. It reads `.github/copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md` and `GEMINI.md` from the repository root, the working directory and the directories between them. It also reads path-specific files under `.github/instructions/` whose names end in `.instructions.md`. Copilot CLI combines all of them, and its docs define no general precedence order. Do not depend on an order. Remove the conflict. Put personal preferences in the home file, team rules at the repository root, and package-specific rules in path-specific files.

<p class="verified">Docs page fetched on 2026-11-23: https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions. Quoted line: "When multiple applicable user-level and repository instruction files exist, Copilot CLI combines their instructions. It removes duplicate copies of identical user-level `copilot-instructions.md`, repository-wide, and agent instructions, but does not define a general precedence order between these files." GitHub Copilot CLI on that date: 1.0.110. The docs page states no version of its own.</p>

Other agents differ. Claude Code loads `CLAUDE.md` and `CLAUDE.local.md` from each directory, from the filesystem root down to the working directory, after your user file at `~/.claude/CLAUDE.md`. Codex CLI reads `AGENTS.md` from its home directory (`~/.codex` by default), then from the project root down to the working directory. The Codex docs say later files override earlier guidance. The Claude Code docs say that when two instructions contradict each other, Claude may pick one arbitrarily. The rule is the same for all three: remove the conflict.

**2. Share one file across tools.** `AGENTS.md` is an open convention read by many tools. Copilot CLI reads `AGENTS.md` and `CLAUDE.md` directly, so one shared file serves it and the agents that read either name.

<p class="verified">Docs page fetched on 2026-11-23: https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions. Quoted line: "Agent instructions, discovered in the standard locations. Copilot CLI also uses `.claude/CLAUDE.md`." GitHub Copilot CLI on that date: 1.0.110. The docs page states no version of its own.</p>

Claude Code differs. Claude Code v2.1.277 or later reads `AGENTS.md` directly, and by default only when no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` exists in the working directory or above it. If you need both, make the tool-specific file a thin wrapper that imports the shared one:

```markdown
@AGENTS.md

## Tool-specific notes
Keep only the settings that apply to this one tool here.
```

**3. Use imports to split, not to grow.** Copilot CLI expands an `@` reference to a relative path in `.github/copilot-instructions.md`, `AGENTS.md` or `CLAUDE.md`. It does not expand references in `GEMINI.md` or `*.instructions.md` files. Imported files load every session, so an import saves you from editing one big file but does not save context. For rules that apply to part of the tree, use path-specific files. In Copilot CLI, an `applyTo` glob in the file's frontmatter limits it to matching files:

```markdown
---
applyTo: "app/models/**/*.rb"
---
```

<p class="verified">Docs page fetched on 2026-11-23: https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions. Quoted line: "In `.github/copilot-instructions.md`, `AGENTS.md`, or `CLAUDE.md`, use `@` followed by a relative path to include another file." GitHub Copilot CLI on that date: 1.0.110. The docs page states no version of its own.</p>

Claude Code also expands `@path/to/file` imports at launch, and imports can nest to a "maximum depth of four hops".

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

## Make an instruction earn its place

A well-documented setup is a source of hypotheses. Copy one practice, name the failure it should prevent, then test it on your work. Keep the model, task and acceptance criteria fixed while you compare. Count missed defects, needless interruptions and your time spent reviewing or repairing the result.

Anthropic's [application-harness account](https://www.anthropic.com/research/harness-design-long-running-apps) describes removing scaffolding as models changed. Try that principle on one advisory rule: compare mandatory architecture reading with a rule that requests it only for changes to service boundaries. Include a copy edit and a boundary change. Inspect the actual files read and outcomes; a promise to follow the rule is not a result.

Keep permission, consent and mandatory organisational controls intact. Include the original failure and fresh cases, repeat the comparison, and restore an advisory rule if consequential failures return. One clean run is a pilot. The cheapest instruction is sometimes the one you can justify deleting.

## Learn the controls you already have

Before adding another instruction file, inspect your agent's settings and help. Find the active model, loaded instructions, enabled tools and permission mode. Check whether a change affects this session, this project or every project. Save the old value before changing it.

In **GitHub Copilot CLI**, the `/instructions` command lists the instruction files the session found and lets you turn single files on or off. `/settings` shows your personal settings. An edit to an instruction file does not reach a running session: exit, then resume the session or start a new one.

<p class="verified">Docs page fetched on 2026-11-23: https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions. Quoted line: "Use the `/instructions` command to view the instruction files discovered for the current session and enable or disable individual files." GitHub Copilot CLI on that date: 1.0.110. The docs page states no version of its own.</p>

<p class="verified">Docs page fetched on 2026-11-23: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli. Quoted line: "You can view and change your personal Copilot CLI settings using the `/settings` slash command." GitHub Copilot CLI on that date: 1.0.110. The docs page states no version of its own.</p>

Other agents name these controls differently. In the **Claude Code terminal**, `/config` opens a settings dialog. It is not a complete view of `settings.json`. Output styles are one useful control: select one there, or use `/output-style`. See the [settings guide](https://code.claude.com/docs/en/settings) and [output-style reference](https://code.claude.com/docs/en/output-styles). In **Codex**, personal settings live in `~/.codex/config.toml`; trusted projects can supply `.codex/config.toml` overrides. Use the [configuration guide](https://learn.chatgpt.com/docs/config-file/config-basic) to check the controls your client supports. Do not assume that one agent's slash commands transfer to another.

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
