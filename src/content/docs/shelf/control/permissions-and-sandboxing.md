---
title: Permissions and sandboxing
description: Use least privilege, deny rules and an operating system sandbox to limit what a runaway agent can touch.
---

*Deep dive for [level 4: Trust, but verify](../../../journey/04-trust-but-verify/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** combine three layers. Permission rules decide which tool calls need approval. A sandbox limits what shell commands can reach at the operating system level. A container or virtual machine bounds everything else. Start with deny rules for secrets and a sandbox with an empty network allow list.

## Why it matters

Approval prompts do not scale. A person who clicks "yes" two hundred times a day stops reading. This is approval fatigue, and [level 4](../../../journey/04-trust-but-verify/) covers it. Rules and a sandbox let the safe majority of actions run unattended and put the human attention on the few that matter.

## What to enable

**1. Deny first.** Claude Code behaviour: rules are evaluated deny, then ask, then allow, and the first match wins. A broad deny rule cannot be overridden by a narrower allow rule. Deny the files and commands you never want touched:

```json
{
  "permissions": {
    "allow": ["Bash(npm run lint)", "Bash(npm run test *)"],
    "deny": ["Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)"]
  }
}
```

**2. Allow narrowly.** Allow exact commands that you run all the time. Avoid wildcards over a whole tool. A rule matches the command text as written, so the same program invoked in another form may not match. The permissions documentation shows that `Bash(git push *)` does not match `git -C . push origin main`. A deny rule on a shell command therefore covers the forms it matches and no others. Rely on the sandbox for isolation, and see [Hooks](../hooks/) for a check that parses the command.

**An allow rule only skips the prompt.** In Claude Code's default mode, a call that matches no rule asks you. Only `dontAsk` mode refuses it. The permissions page puts it this way for Bash commands: "Approval required: Yes, except a built-in set of read-only commands". Its description of `dontAsk` mode reads: "Auto-denies every call that would otherwise prompt". So an allow list does not refuse everything else in the default mode. It removes the prompt for the calls it names. Choose `dontAsk` mode when you want unmatched calls refused, and then test that a call you did not list is refused.

**3. Turn on the sandbox.** Claude Code behaviour: the sandbox covers shell commands only. It uses the macOS Seatbelt framework, or `bubblewrap` and `socat` on Linux and WSL2, and it is off by default. Writes are limited to the working directory and a temporary directory. Network access goes through a proxy that checks each host against an allowed-domains list, and that list starts empty. Enable it with the `/sandbox` command or the `sandbox.enabled` setting, and add domains one at a time with `sandbox.network.allowedDomains`.

**4. Know what the sandbox does not cover.** File tools, web tools, MCP servers and hooks run outside the sandbox. They follow permission rules instead. A sandbox denial on reads does not stop the file-read tool, so deny the same paths in both places.

**5. Do not use "skip all prompts" modes on a machine you care about.** Run those modes only inside a disposable container or virtual machine with no credentials. You can also disable them in settings so a shared repository cannot turn them on.

**6. Check where settings come from.** Managed settings override command-line settings, which override project-local, shared project and user settings. List-type keys such as `allow` merge across files. Run the harness's status command to see which files loaded.

**7. Control network egress separately.** Prefer an allow list of domains over a deny list. For web fetches, allow specific domains by rule.

**8. Protect the files that constrain the agent.** The agent can edit what constrains it. If it can write to `.claude/settings.json`, to a hook script or to your capability registry, it can loosen its own limits. Add deny rules for writes to those paths. Add a file-integrity check or a CI check that fails when they change without review. This is the mechanism behind "turning off a safety control" in the [approval list](../../operations/human-in-the-loop/): the write is denied, and the check catches a change that gets through some other way. A deny rule on file tools does not stop a shell command from writing the same file. The project settings file sits inside the working directory, so a sandbox that allows writes there does not protect it. That is why the integrity or CI check matters more than the deny rule.

## Failure modes it reduces

- A prompt-injected command reads your cloud credentials and sends them out.
- A build script the agent runs writes outside the repository.
- Approval fatigue leads to a blanket "always allow".
- A shared repository ships a settings file that quietly widens permissions.
- The agent edits its own settings or hook script to remove a limit.

## First step for the maintainer

Add the `deny` rules above, enable the sandbox, leave the network allow list empty and add only the registries your build needs.

<p class="verified">Docs page fetched on 2026-10-22: https://code.claude.com/docs/en/permissions. Quoted line: "Auto-denies every call that would otherwise prompt". Claude Code on that date: 2.1.309. The docs page states no version of its own. The settings and sandboxing details were not re-fetched on that date and are Not checked against current docs.</p>

**Next:** [Capability gating](../capability-gating/)
