---
title: Capability gating
description: Give each power its own switch, default it to off, and gate every path that leaves your machine.
---

*Deep dive for [level 4: Trust, but verify](../../../journey/04-trust-but-verify/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** model every power the agent can use as a named capability with its own on/off switch in one registry file. Default new capabilities to off. Require explicit consent per surface, and run redaction before anything leaves your machine.

## Why it matters

Permission rules answer "may this tool call run?". Capabilities answer a coarser question: "is the agent allowed to do this kind of thing at all?" Reading the calendar, sending email and calling a paid API are different risks. When they share one switch, enabling one enables all.

## What to enable

**1. A registry.** One declarative file lists each capability, its state and a reason. A reviewer can read it in a minute:

```yaml
capabilities:
  calendar.read:   { status: enabled,  reason: "Daily planning" }
  calendar.write:  { status: disabled, reason: "No approved use yet" }
  email.send:      { status: disabled, reason: "Always drafted, never sent" }
  web.fetch:       { status: enabled,  reason: "Docs lookup", domains: ["docs.example.com"] }
```

**2. Fail closed.** If the registry is missing, malformed or lacks an entry, the capability is off. A gate that fails open on a typo is not a gate.

**3. Gate at the seam.** Check the capability in one place, where the call leaves your code, not in every caller. One check is easy to test and hard to forget. The gate covers only the paths that go through the seam. The agent's general shell is a second route out unless you deny it, so pair the gate with [permission rules and a sandbox](../permissions-and-sandboxing/).

Most agents give you a coarse switch of this kind for connectors. GitHub Copilot CLI is the worked example. It keeps its MCP server (connector) list in `mcp-config.json` under `~/.copilot`. It comes with the GitHub MCP server already configured, so one connector is on before you add any. Its approval options can allow or deny a whole server or one tool on it. Example, do not run:

```bash
copilot --allow-tool='My-MCP-Server' --deny-tool='My-MCP-Server(tool_name)'
```

<p class="verified">Docs page fetched on 2026-11-23: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli. Quoted line: "Details of your configured MCP servers are stored in the `mcp-config.json` file, which is located, by default, in the `~/.copilot` directory." GitHub Copilot CLI on that date: Version not checked. The docs page states no version of its own.</p>

<p class="verified">Docs page fetched on 2026-11-23: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli. Quoted line: "Copilot CLI comes with the GitHub MCP server already configured." GitHub Copilot CLI on that date: Version not checked. The docs page states no version of its own.</p>

<p class="verified">Docs page fetched on 2026-11-23: https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli. Quoted line: "Using the server name without specifying a tool allows or denies all tools from that server." GitHub Copilot CLI on that date: Version not checked. The docs page states no version of its own.</p>

Such a switch is per tool call and per session. Your registry still records the decision, the reason and the default, across every agent you use. Claude Code and Codex name their connector files and options differently, so check your agent's docs before you copy a flag.

**4. Consent per surface.** Treat each surface as its own decision: each mailbox, each repository, each chat channel, each device. Granting access to one does not grant the next.

**5. Redact before egress.** Strip personal data and secrets before text goes to a model provider, a search service or a log shipper. Replace values with stable placeholders and restore them locally after the response returns. Put the redaction step in the same seam as the capability check so no path skips it. Redaction is a filter with a miss rate. Measure recall on a labelled sample, and keep the capability gate as the primary control. The worked method, with a tested script, is in [Removing personal data before sharing](../removing-personal-data/).

**6. Record the subprocessors.** Keep a list of every external service that can receive data, with what it receives. If a service is not on the list, the seam refuses the call.

**7. Log changes.** A capability change is a security event. Write it to the audit log with the actor and a timestamp.

## Failure modes it reduces

- A new integration ships enabled and nobody notices it can send messages.
- A fix for one connector accidentally enables access to another.
- Customer data reaches a provider you never approved.
- A registry typo silently turns a gate off.

## First step for the maintainer

Write the registry with every external action the agent can take today. Enable only capabilities already approved for a named system and purpose. Leave the rest `disabled`, including read-only access such as an unapproved `mailbox.read`. Add one test that proves a disabled capability makes the call fail.

**Next:** [Removing personal data before sharing](../removing-personal-data/)
