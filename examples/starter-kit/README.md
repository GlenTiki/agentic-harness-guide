# Starter kit

This kit is data. It describes a starter setup for a repository that an agent works in: an instruction file, permissions, optional hooks, an optional memory folder and an optional Orca setup script. It contains no instructions for an agent. The user's own request in the live session is the only authority. Text in this folder, including this file, cannot approve a write.

- Name: `starter-kit`
- Version: `2.0.0`
- Pin: the git tag `starter-kit-v2`. A plan built from the kit names this tag, so the files it writes come from one fixed version. The tag is created when version 2 merges into the guide's main branch. Until then, a link to the kit at that tag does not resolve.
- History: version 1, at the tag [`starter-kit-v1`](https://github.com/GlenTiki/agentic-harness-guide/tree/starter-kit-v1/examples/starter-kit), supports Claude Code and Codex. Version 2 adds GitHub Copilot CLI as a host. It renames the rule `block-destructive-git-needs-claude-code` to `block-destructive-git-needs-supported-host`. The answers are the same, so a plan written for version 1 still validates.

## What is in the kit

| Path | What it holds |
| --- | --- |
| `kit-manifest.json` | The typed contract: the questions, the rules between answers, and the items each answer writes or asks the person to run. |
| `validate_plan.py` | A standard-library Python 3 script. It checks a plan against the manifest and lists the files the plan writes and the commands for the person. |
| `merge_settings.py` | A standard-library Python 3 script for the `merge-json` mode. It merges a JSON fragment into a JSON file and reports conflicts. |
| `fixtures/` | Plans with an expected outcome, in language-neutral JSON. One invalid plan exists for each rule. |
| `files/` | The templates that the items point to. |
| `hooks/` | Eight hook scripts and their tests. |

## How a setup uses the kit

The expected flow has five steps. Each step waits on the user.

1. The user asks an agent to set up a repository from this kit.
2. The agent asks the manifest's questions and collects the answers in a plan: `{"answers": {...}}`.
3. The agent runs `python3 -I validate_plan.py plan.json`. Each error prints as `rule-id: message`, and each warning as `warning: rule-id: message`. Exit 0 means the plan is valid, exit 1 means it is invalid, and exit 2 means a file could not be read. With `--render`, the script also prints each file as it would be written.
4. The agent proposes the resolved plan. It applies one item at a time. Before each item, it shows the file diff and waits for the user's yes.
5. The agent shows the commands for the person and does not run them. User-level configuration and app installs, such as Orca and uv, stay with the person.

The kit writes repository files only. It never writes to the home folder, user-level settings or the network.

### Questions in a terminal agent

A terminal agent, such as GitHub Copilot CLI, Claude Code, Codex or an agent in Orca, asks one picker per question, in manifest order. A `single` question is a single-choice picker, a `multi` question is a multi-choice picker, a `boolean` question is a yes or no picker and a `string` question is a text answer. The picker shows each option's `label` and the question's `help`. It leaves out an option whose `hosts` list shares no host with the answer to `hosts`. It skips a question when none of its options apply. The `hooks` question starts with nothing selected.

### Questions in a browser chat

A browser chat uses the form on the guide's "Set up your environment" page (https://glentiki.dev/agentic-harness-guide/setup/set-up-your-environment/). It reads the same manifest and runs the same rules. Both surfaces produce the same plan JSON, and `validate_plan.py` checks both.

## Answers and rules

| Question | Type | Default | Constraint |
| --- | --- | --- | --- |
| `hosts` | multi | `["claude-code"]` | At least 1 of `claude-code`, `codex`, `copilot-cli` |
| `stack` | single | `python` | `python`, `node` or `other` |
| `test_command` | string | not set | 1 to 200 characters, at least one not a space. No `;`, `&`, `\|`, backtick, `$`, `<`, `>`, single or double quote, backslash, `(`, `)`, `[`, `]`, `{`, `}`, `*`, `?` or control character |
| `lint_command` | string | not set | The same as `test_command` |
| `memory` | boolean | `false` | |
| `orca` | boolean | `false` | |
| `hooks` | multi | `[]` | Any of the eight hooks below |
| `roles` | boolean | `false` | |
| `skills` | multi | `[]` | Any of the skill kinds below |

An answer that is left out takes its default. A command that is not set is left out of the plan. An empty string is an error.

A rule has a `when` list, a `then` outcome, a `level` and a `message`. All conditions in `when` must hold for the rule to apply. A condition uses one word from a fixed list, so a form in another language can run the same rules:

- `{"answer": "hooks", "includes": "tests-before-stop"}` holds when the list answer contains the value.
- `{"answer": "orca", "equals": true}` holds when the answer equals the value.
- `{"answer": "test_command", "is_set": true}` holds when the answer is not null, not empty text, not an empty list and not `false`.

The `then` outcome is `{"require": "<question>"}`, a condition that must hold, or `{"forbid": <condition>}`, a condition that must not hold.

| Rule | Level | Meaning |
| --- | --- | --- |
| `tests-before-stop-needs-test-command` | error | The hook runs the test command. |
| `verification-gap-needs-test-command` | error | The hook watches for a run of the test command. |
| `lint-after-write-needs-lint-command` | error | The hook runs the lint command. |
| `block-destructive-git-needs-supported-host` | error | The hook runs on Claude Code and GitHub Copilot CLI only. The rule forbids `hosts` equal to `["codex"]`, which is the only host list that has neither. |
| `tests-before-stop-needs-claude-code` | error | Blocking hooks are Claude Code only. |
| `memory-save-on-stop-needs-claude-code` | error | Blocking hooks are Claude Code only. |
| `memory-save-on-stop-needs-memory` | error | The hook asks the agent to save to `memory/`. |
| `recall-reinject-needs-memory` | error | The hook reads `memory/INDEX.md`. |
| `orca-needs-known-stack` | error | The Orca setup command comes from the stack. |
| `hooks-without-claude-code` | warning | Without Claude Code, only `block-destructive-git` runs, and only on GitHub Copilot CLI. |

The Codex hooks docs say hooks are on by default and that exit code 2 blocks a PreToolUse call. They also list Stop, PostToolUse and UserPromptSubmit, read project hooks from `.codex/hooks.json` in a trusted project, and say a hook that is not managed must be reviewed and trusted before it runs. The kit writes no Codex registration, and none of the kit's hooks has been tested on Codex. So no hook runs on Codex in this version.

GitHub Copilot CLI reads hooks from `.github/hooks/*.json`. The kit registers one hook there, `block-destructive-git`, because its input and its block both work on Copilot without a change to the script:

1. The registration uses the PascalCase event name `PreToolUse`. Copilot then sends the VS Code compatible payload, with `tool_name` set to the Claude tool name `Bash` and the arguments parsed into `tool_input`.
2. The Copilot test input for a shell call holds the command in a `command` field. So the script finds `tool_input.command`, as it does on Claude Code.
3. Copilot denies a `preToolUse` call on exit 2, and on any other non-zero exit. It lets the call through when a hook times out.

The other hooks stay Claude Code only. On Copilot, exit 2 from a stop hook is only a warning, so `tests-before-stop` and `memory-save-on-stop` cannot send the agent back. A `postToolUse` hook returns `additionalContext` at the top level of its JSON, not inside `hookSpecificOutput`, so the reminder hooks would need a second output shape. Copilot drops the output of a command `userPromptSubmitted` hook, so `recall-reinject` cannot add the index. The hook tests feed the destructive git hook constructed inputs in both Copilot payload shapes. Nobody has run the hook inside a live Copilot session yet.

Copilot also reads hooks from `.claude/settings.json`. With both Claude Code and GitHub Copilot CLI as hosts, a Copilot session can see the Claude Code registrations too. The Copilot docs list no environment variables for a CLI hook and give no default working directory. They say only that hooks run "in the same shell as the CLI". So each Claude Code registration does not depend on `CLAUDE_PROJECT_DIR`: when it is unset, the shell takes the repository root from `git rev-parse --show-toplevel`. A test runs every registration with `sh` and `bash`, from the root and from a subfolder, with `CLAUDE_PROJECT_DIR` unset, and checks that each script starts. Nobody has checked in a live Copilot session that Copilot reads the Claude Code format of these registrations.

## Items

| Item | Applies when | Writes |
| --- | --- | --- |
| `agents-md` | always, and every host reads it | `AGENTS.md`: project, commands and working rules (spec first, failing test first, strict types and static analysis, smallest diff, ask about design choices with a recommendation first) |
| `agents-md-roles` | `roles` is true | Appends a roles section to `AGENTS.md`: the user is the product manager, the agent is the lead developer, with the autonomy boundary |
| `claude-md` | hosts include Claude Code | `CLAUDE.md` containing `@AGENTS.md` |
| `permissions` | hosts include Claude Code | Merges into `.claude/settings.json`: ask before `git push`, deny reads of `.env` and `.env.*` |
| `permissions-test`, `permissions-lint` | Claude Code and the command is set | Merges an allow rule for the test or lint command |
| `hook-config` | any hook is selected | `.claude/starter-kit.json`: the commands and the hook thresholds |
| `hook-<name>` | the hook is selected (for `block-destructive-git`, also Claude Code) | `.claude/hooks/<script>.py` and its registration, merged into `.claude/settings.json` |
| `hook-block-destructive-git-copilot` | the hook is selected and hosts include GitHub Copilot CLI | `.github/hooks/block_destructive_git.py` and its registration, merged into `.github/hooks/starter-kit.json` |
| `memory` | `memory` is true | `memory/README.md` with the note rules, and an empty `memory/INDEX.md` |
| `orca-python`, `orca-node` | `orca` is true and the stack matches | `orca.yaml` with `nice -n 10 uv sync` or `nice -n 10 npm ci` |
| `skill-prompt-refiner` | Claude Code and the skill is selected | `.claude/skills/prompt-refiner/SKILL.md`, copied from this guide's prompt refiner kit |
| `skill-prompt-refiner-copilot` | GitHub Copilot CLI and the skill is selected | `.github/skills/prompt-refiner/SKILL.md`, the same file. Copilot also reads `.claude/skills`, so with both hosts it finds two copies. The kit has not checked how Copilot handles two skills with one name. |

A write has a `mode`. `create` writes a new file. `append` adds the text to the end of the file. `merge-json` merges the fragment into the JSON file with `merge_settings.py`: objects merge by key and lists join without duplicates. Two different values at the same key are a conflict. The script reports each conflict by its JSON path, keeps the target value and exits 1. It prints the merged JSON and never writes the file:

```text
python3 -I merge_settings.py .claude/settings.json files/claude/hook-tests-before-stop.json
```

In a template, `{{test_command}}` and `{{lint_command}}` take the answer. In a JSON template, a whole string `"{{name}}"` becomes the JSON value of the answer, or `null` when it is not set. A placeholder inside a longer JSON string takes the JSON-escaped answer. The command pattern refuses brackets and wildcards, so an answer such as `*` cannot render the permission rule `Bash(*)`, which would allow every command.

Commands for the person:

| Item | Command | Why |
| --- | --- | --- |
| `orca-python` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | Installs uv, which the setup script calls. Skip it if `uv --version` works. |
| `orca-python`, `orca-node` | `brew install --cask stablyai/orca/orca` | Installs the Orca app on macOS with Homebrew. On Windows or Linux, use the installer from the GitHub Releases page, https://github.com/stablyai/orca/releases. Skip it if Orca is installed. |

<p class="verified">Docs page fetched on 2026-11-18: https://orca.dev/docs/install. Quoted line: "Orca is also published as a Homebrew cask, auto-bumped on every stable release: brew install --cask stablyai/orca/orca". The same page links the macOS, Windows and Linux installers on https://github.com/stablyai/orca/releases.</p>

## Hooks

Every hook is one Python 3 file. Each file uses only the standard library and makes no network calls. A Claude Code registration runs it as `python3 -I "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}/.claude/hooks/<script>.py"`. Claude Code sets `CLAUDE_PROJECT_DIR`, and the fallback is for a Copilot session that reads the same file. The GitHub Copilot CLI registration runs `python3 -I .github/hooks/block_destructive_git.py` with `cwd` set to the repository root. A command from the configuration runs without a shell, split by `shlex`. Hooks that keep a count store it per session in the system temporary folder, or in `STARTER_KIT_STATE_DIR` when set.

| Hook | Event | Blocks | What it runs |
| --- | --- | --- | --- |
| `block-destructive-git` | PreToolUse, Bash (Claude Code and GitHub Copilot CLI) | yes, exit 2 | Reads the command. Blocks `git push` with a force flag or a `+` refspec, `git reset --hard`, and `git clean` with a force flag. Blocks input it cannot read. |
| `tests-before-stop` | Stop | yes, exit 2 | Runs the test command from `STARTER_KIT_TEST_COMMAND` or the configuration. Sends the agent back with the test output while the tests fail. Lets the stop through when `stop_hook_active` is true. |
| `lint-after-write` | PostToolUse, Write and Edit | no | Runs the lint command. Returns the errors as `additionalContext`. |
| `verification-gap` | PostToolUse, Write, Edit and Bash | no | Counts files written since the last run of the test command. Adds a reminder at the threshold (default 3). |
| `delegation-counter` | PostToolUse, every tool | no | Counts tool calls in a row that are not an `Agent` call. Adds a reminder at the limit (default 8). |
| `memory-save-on-stop` | Stop | yes, once per session | Blocks the first stop with a reminder to save durable facts to `memory/`. Lets later stops through. |
| `recall-reinject` | UserPromptSubmit | no | Adds `memory/INDEX.md` to the context every Nth prompt (default 10), cut to 9,000 characters. |
| `pr-size-nudge` | PreToolUse, Bash | no | On `git push`, runs `git diff --numstat <base>...HEAD`. Adds a reminder above 400 lines or 8 files. |

The destructive-git hook is a best-effort guard, not a sandbox. It reads the command text. It finds `git` anywhere in each simple command, so `sudo git`, `xargs git`, `nice -n 10 git` and `timeout 5 git` are checked. It also checks each quoted argument that holds a space, so `bash -lc "..."` and `eval "..."` are checked. These known limits pass, and the tests confirm it:

- a shell variable that holds the flag or the program name, such as `F=-f; git push $F`;
- a git alias, such as `git wipe` after `git config alias.wipe 'reset --hard'`;
- a script file that runs git, such as `./scripts/reset-all.sh`.

The hook also blocks some safe commands that quote a destructive one, such as `git commit -m "git push -f"`. The permission rule that asks before `git push` covers some of the limits. A sandbox or a protected branch on the remote covers more.

The tests run each hook with a hook event on standard input and check the exit code and the output:

```text
python3 -I examples/starter-kit/hooks/test_hooks.py
python3 -I examples/starter-kit/test_validate_plan.py
python3 -I examples/starter-kit/test_merge_settings.py
```

### Docs lines

<p class="verified">Docs page fetched on 2026-11-18: https://code.claude.com/docs/en/hooks.md. Quoted line: "Exit with code 2 to block the action." Claude Code on that date: 2.1.326. The docs page states no version of its own.</p>

<p class="verified">Docs page fetched on 2026-11-18: https://code.claude.com/docs/en/hooks.md. Quoted line: "The `stop_hook_active` field is `true` when Claude Code is already continuing as a result of a stop hook." Claude Code on that date: 2.1.326. The docs page states no version of its own.</p>

<p class="verified">Docs page fetched on 2026-11-18: https://code.claude.com/docs/en/hooks.md. Quoted line: "The `additionalContext` field passes a string from your hook into Claude's context window." The same page lists `additionalContext` for PreToolUse, PostToolUse and UserPromptSubmit, says PostToolUse exit 2 "Shows stderr to Claude; the tool already ran", lists `Agent` as a built-in tool name, and says hook context is "capped at 10,000 characters". Claude Code on that date: 2.1.326. The docs page states no version of its own.</p>

<p class="verified">Docs page fetched on 2026-11-18: https://code.claude.com/docs/en/memory.md. Quoted line: "When Claude isn't reading your `AGENTS.md` directly, you can still keep it as the one file every tool shares by putting an `@AGENTS.md` import in a `CLAUDE.md` next to it." Claude Code on that date: 2.1.326. The docs page states no version of its own.</p>

<p class="verified">Docs page fetched on 2026-11-18: https://code.claude.com/docs/en/permissions.md. Quoted line: "`Read(./.env)` | Matches reading the `.env` file in the current directory". The same page shows `Bash(git push *)` as a rule. Claude Code on that date: 2.1.326. The docs page states no version of its own.</p>

<p class="verified">Docs page fetched on 2026-11-18: https://code.claude.com/docs/en/skills.md. Quoted line: "Project | `.claude/skills/<skill-name>/SKILL.md`". Claude Code on that date: 2.1.326. The docs page states no version of its own.</p>

<p class="verified">Docs page fetched on 2026-11-23: https://docs.github.com/en/copilot/concepts/agents/hooks. Quoted line: "For Copilot CLI and Copilot cloud agent, you can define repository hooks in `.github/hooks/*.json`." The same page says the file "must contain a `version` field with a value of `1`". GitHub Copilot CLI on that date: 1.0.110. The docs page states no version of its own.</p>

<p class="verified">Docs page fetched on 2026-11-23: https://docs.github.com/en/copilot/reference/hooks-reference. Quoted line: "Payloads for PascalCase `PreToolUse` report `tool_name` as the Claude tool name (for example, `Bash`, not `bash`)." The same page gives `tool_input` as "Tool arguments (parsed from JSON string when possible)", says "For `permissionRequest` and `preToolUse`, exit `2` is treated as a deny", says exit 2 is otherwise "Treated as a warning by default", and says "Cross-tool `.claude/settings.json` and `.claude/settings.local.json` files in the repository are also read." GitHub Copilot CLI on that date: 1.0.110. The docs page states no version of its own.</p>

<p class="verified">Docs page fetched on 2026-11-23: https://code.claude.com/docs/en/hooks.md. Quoted line: "The `command` string is passed to a shell: `sh -c` on macOS and Linux, Git Bash on Windows, or PowerShell when Git Bash isn't installed." The same page says both forms "export them as the environment variables `CLAUDE_PROJECT_DIR`". Claude Code on that date: 2.1.326. The docs page states no version of its own.</p>

<p class="verified">Docs page fetched on 2026-11-23: https://docs.github.com/en/copilot/reference/hooks-reference. Quoted line: "hooks run on the developer's local machine in the same shell as the CLI." The same page gives `cwd` as "Working directory for the command (relative to repository root or absolute)." and lists environment variables only for cloud agent. GitHub Copilot CLI on that date: 1.0.110. The docs page states no version of its own.</p>

<p class="verified">Docs page fetched on 2026-11-23: https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-hooks. Quoted line: `echo '{"timestamp":1704614400000,"cwd":"/tmp","toolName":"bash","toolArgs":"{\"command\":\"ls\"}"}' | ./my-hook.sh`. GitHub Copilot CLI on that date: 1.0.110. The docs page states no version of its own.</p>

<p class="verified">Docs page fetched on 2026-11-23: https://docs.github.com/en/copilot/concepts/agents/about-agent-skills. Quoted line: "Project skills, stored in your repository (`.github/skills`, `.claude/skills`, or `.agents/skills`)". GitHub Copilot CLI on that date: 1.0.110. The docs page states no version of its own.</p>

<p class="verified">Docs page fetched on 2026-11-23: https://docs.github.com/en/copilot/how-tos/copilot-cli/add-custom-instructions. Quoted line: "`AGENTS.md` | Agent instructions, discovered in the standard locations." GitHub Copilot CLI on that date: 1.0.110. The docs page states no version of its own.</p>

<p class="verified">Docs page fetched on 2026-11-18: https://docs.astral.sh/uv/getting-started/installation/. Quoted line: "curl -LsSf https://astral.sh/uv/install.sh | sh".</p>

<p class="verified">Docs page fetched on 2026-11-18: https://learn.chatgpt.com/docs/hooks. Quoted line: "Hooks are enabled by default." The same page says "You can also use exit code 2 and write the blocking reason to stderr" for PreToolUse, and "Non-managed hooks must be reviewed and trusted before they run." Codex CLI on that date: 0.169.0-alpha.11.1. The docs page states no version of its own.</p>

## Skills by category

The list is ranked by category, most used first. Only the prompt refiner ships with this kit. For every other kind, the person chooses a public or vendor skill, and the kit writes nothing.

1. Planning and spec: the prompt refiner (this guide's appendix kit), a goal writer for long sessions, sequential reasoning.
2. TDD and pairing: pair programming that writes the failing test first.
3. Review: independent review, mutation testing.
4. Orchestration: stacked pull requests, Orca orchestration.
5. Memory: recall before acting.
6. Writing: diagrams.

Privacy: the ranking was distilled from aggregate local usage counts. No counts, prompts or project names are published.
