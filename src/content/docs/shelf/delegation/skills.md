---
title: Skills
description: Package a repeatable procedure as a skill so it loads only when needed.
---

*Deep dive for [level 6: Hire a team](../../../journey/06-hire-a-team/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** write a skill for any procedure you explain to the agent more than twice and that has a clear trigger. Keep the description precise, keep the body short, and move detail into supporting files that load on demand. Use a plain prompt for one-off work.

## Why it matters

Instruction files load every session, so everything in them costs context all the time, as [level 2](../../../journey/02-house-rules/) explains. A skill splits that cost in two. Only a short description is always present. The full body loads when the task matches. This lets you hold many procedures without paying for them on every turn.

## What to enable

**1. One directory per skill.** Claude Code behaviour: a skill is a directory with a `SKILL.md` file, in `.claude/skills/<name>/` for a project or `~/.claude/skills/<name>/` for all your projects. The file has YAML frontmatter and markdown instructions:

```markdown
---
name: release-notes
description: Draft release notes from merged pull requests since the last tag. Use when asked to prepare a release.
---
1. Run `git log <last-tag>..HEAD --merges --oneline`.
2. Group entries by area. Skip dependency bumps.
3. Write one line per change. Link each pull request.
```

**2. Write the description as the trigger.** The harness uses it to decide when to load the skill. Say what the skill does and when to use it. Put the main use first, because long descriptions are truncated in the listing.

**3. Use progressive disclosure.** Keep `SKILL.md` under about 500 lines. Put reference material, examples and scripts in separate files in the skill directory, and link to them from the body. The agent reads them only when it needs them. Scripts run without being loaded into context.

**4. Control who can invoke it.** A frontmatter flag stops the model from loading a skill on its own, which suits anything with side effects, such as a deploy. Another flag hides a skill from the menu while leaving it available to the model. An `allowed-tools` field pre-approves tools for the turn that invokes the skill, and it does not restrict other tools.

**5. A skill beats a prompt when** the procedure repeats, has a stable trigger, includes scripts or templates, or must be shared across a team. A prompt beats a skill when the task is novel or the steps change each time.

**6. Treat third-party skills as code.** A skill can include scripts and can pre-approve tools. Read it before you install it, and pin the version.

## Failure modes it reduces

- A long procedure sits in the instruction file and dilutes every session.
- Each person on the team prompts the same task slightly differently and gets different results.
- A vague description causes the skill to load for unrelated tasks, or never.

## First step for the maintainer

Take the one multi-step task you most often retype. Move it into `.claude/skills/<name>/SKILL.md` with a trigger-style description, then test it in a fresh session.

<p class="verified">Docs page fetched on 2026-10-22: https://code.claude.com/docs/en/skills. Quoted line: "Skills extend what Claude can do. Create a `SKILL.md` file with instructions, and Claude adds it to its toolkit." Claude Code on that date: 2.1.309. The docs page states no version of its own.</p>

**Next:** [MCP servers](../mcp-servers/)
