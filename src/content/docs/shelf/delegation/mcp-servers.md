---
title: MCP servers
description: Connect tools through the Model Context Protocol with least privilege, pinned versions and reviewed descriptions.
---

*Deep dive for [level 3: Give it hands](../../../journey/03-give-it-hands/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** add an MCP server only when it replaces a manual step you do often. Prefer a read-only server. Pin its version, read its tool descriptions before enabling it, and treat everything it returns as untrusted data.

## Why it matters

An MCP server (a connector, as [level 3](../../../journey/03-give-it-hands/) calls it) adds tools to the agent. Each tool is a new capability and a new source of text that reaches the model. A tool description is itself text the model reads and may follow, so a malicious or compromised server can steer the agent through its descriptions as well as through its output. Claude Code's own documentation says to verify that you trust each server before connecting it, and warns that servers which fetch external content can expose you to prompt injection.

## What to enable

**1. Choose the scope on purpose.** Claude Code behaviour: `claude mcp add` takes a scope. `local` is the default and applies to you in one project. `project` writes to a `.mcp.json` file at the repository root, which you commit to share the server with the team. `user` applies to all your projects. Share a server through the project scope only after the team has reviewed it.

Example, do not run:

```bash
claude mcp add --transport http docs-search --scope project https://example.com/mcp
claude mcp list
```

**2. Expect an approval prompt.** Claude Code behaviour: interactive Claude Code asks you to approve project-scoped servers before use. The MCP documentation says: "In `claude -p` runs, Agent SDK sessions, and cloud sessions outside a project's threads, Claude Code can't show that prompt: it loads project-scoped servers without asking." To keep a server out anyway, add it to `disabledMcpjsonServers`, which blocks it in every permission mode. You can also exclude project settings entirely with `--setting-sources`, or start the session with `--strict-mcp-config` so that only the servers you pass with `--mcp-config` load. Skipping the approval prompt for the project servers a strict session does not load needs Claude Code v2.1.246 or later.

**3. Use the full tool name in rules.** MCP tools are named `mcp__<server>__<tool>`. Write permission rules, skill `allowed-tools` and sub-agent `tools` lists with those names. Allow a read tool and leave the write tool to ask:

```json
{
  "permissions": {
    "allow": ["mcp__docs-search__search"],
    "ask": ["mcp__tracker__create_issue"]
  }
}
```

**4. Read the descriptions.** Before you enable a server, list its tools and read every description. Look for instructions addressed to the model, requests for broad access, and tools that do more than the name says.

**5. Pin the version.** A server started with an unpinned package runs whatever the registry serves today. Pin an exact version and review upgrades like any dependency change.

**6. Give it the least credential.** Use a token scoped to the one resource and the one verb the server needs. Do not reuse your personal full-access token.

**7. Remember the sandbox boundary.** MCP servers run outside Claude Code's shell sandbox. Their reach is whatever the server process can do. Run servers that handle untrusted content in a container.

**8. Treat output as data.** A search result, a ticket body or a page the server returns can contain injected instructions. See [Untrusted input](../../control/untrusted-input/).

## Failure modes it reduces

- A tool description tells the agent to send data to another tool.
- An upgraded server silently adds a write tool.
- A personal token with wide scope leaks through a server's logs.
- A committed `.mcp.json` from a cloned repository starts a server you never reviewed.

## First step for the maintainer

List your configured servers. Remove any you have not used this month. For each one that stays, write down the credential scope and the pinned version in the repository.

<p class="verified">Docs page fetched on 2026-10-22: https://code.claude.com/docs/en/mcp. Quoted line: "Verify you trust each server before connecting it. Servers that fetch external content can expose you to prompt injection risk." Claude Code on that date: 2.1.309. The docs page states no version of its own. The sandboxing page: Not checked against current docs.</p>

**Next:** [Spec-driven development](../../quality/spec-driven-development/)
