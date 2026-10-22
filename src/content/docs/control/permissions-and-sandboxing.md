---
title: Permissions and sandboxing
description: Use least privilege, deny rules and an operating system sandbox to limit what a runaway agent can touch.
---

**Recommendation:** combine three layers. Permission rules decide which tool calls need approval. A sandbox limits what shell commands can reach at the operating system level. A container or virtual machine bounds everything else. Start with deny rules for secrets and a sandbox with an empty network allow list.

## Why it matters

Approval prompts do not scale. A person who clicks "yes" two hundred times a day stops reading. Rules and a sandbox let the safe majority of actions run unattended and put the human attention on the few that matter.

## What to enable

**1. Deny first.** In Claude Code, rules are evaluated deny, then ask, then allow, and the first match wins. A broad deny rule cannot be overridden by a narrower allow rule. Deny the files and commands you never want touched:

```json
{
  "permissions": {
    "allow": ["Bash(npm run lint)", "Bash(npm run test *)"],
    "deny": ["Read(./.env)", "Read(./.env.*)", "Read(./secrets/**)"]
  }
}
```

**2. Allow narrowly.** Allow exact commands that you run all the time. Avoid wildcards over a whole tool. A rule matches the command text as written, so the same program invoked in another form may not match. Treat a deny rule on a shell command as a speed bump and rely on the sandbox for real isolation.

**3. Turn on the sandbox.** Claude Code's sandbox covers shell commands only. It uses the macOS Seatbelt framework, or `bubblewrap` and `socat` on Linux and WSL2, and it is off by default. Writes are limited to the working directory and a temporary directory. Network access goes through a proxy that checks each host against an allowed-domains list, and that list starts empty. Enable it with the `/sandbox` command or the `sandbox.enabled` setting, and add domains one at a time with `sandbox.network.allowedDomains`.

**4. Know what the sandbox does not cover.** File tools, web tools, MCP servers and hooks run outside the sandbox. They follow permission rules instead. A sandbox denial on reads does not stop the file-read tool, so deny the same paths in both places.

**5. Do not use "skip all prompts" modes on a machine you care about.** Run those modes only inside a disposable container or virtual machine with no credentials. You can also disable them in settings so a shared repository cannot turn them on.

**6. Check where settings come from.** Managed settings override command-line settings, which override project-local, shared project and user settings. List-type keys such as `allow` merge across files. Run the harness's status command to see which files loaded.

**7. Control network egress separately.** Prefer an allow list of domains over a deny list. For web fetches, allow specific domains by rule.

## Failure modes it prevents

- A prompt-injected command reads your cloud credentials and sends them out.
- A build script the agent runs writes outside the repository.
- Approval fatigue leads to a blanket "always allow".
- A shared repository ships a settings file that quietly widens permissions.

## Start here

Add the `deny` rules above, enable the sandbox, leave the network allow list empty and add only the registries your build needs.

<p class="verified">Verified against the Claude Code permissions, settings and sandboxing documentation (code.claude.com/docs/en/permissions, settings and sandboxing) on 2026-10-22.</p>
