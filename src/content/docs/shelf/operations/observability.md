---
title: Observability and audit trail
description: Record what the agent did in a file you control, so you can answer what happened and why.
---

*Deep dive for [level 7: Run it for real](../../../journey/07-run-it-for-real/).*

**Recommendation:** write an append-only action log from hooks, not from the model. Keep session transcripts for as long as your policy needs them and know when your harness deletes them. Track token use and cost per session.

## Why it matters

When something goes wrong, the question is "what did the agent do, in what order, and on whose instruction?". The model's own account is a summary and may be wrong. A log written by the harness is a record. It also supports audits, because you can show what the agent touched.

## What to enable

**1. A one-line-per-action log.** Use a post-tool hook that appends a line with a UTC timestamp, the tool and the target. Keep it append-only and keep it out of the agent's write permissions where you can.

```bash
#!/usr/bin/env bash
# PostToolUse hook: append one line per tool call.
set -euo pipefail
input=$(cat)
printf '%s | %s | %s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  "$(jq -r '.tool_name' <<<"$input")" \
  "$(jq -r '.tool_input.file_path // .tool_input.command // ""' <<<"$input" | head -c 200)" \
  >> .agent-log/actions.log
```

Do not log secrets. Truncate long commands, and redact tokens before writing. Add the log directory to `.gitignore` unless you mean to commit it.

**2. Log lifecycle events too.** Session start, session end, sub-agent start and stop, configuration changes and capability changes all belong in the trail. Claude Code exposes events for most of these, including `SessionStart`, `SessionEnd`, `SubagentStart`, `SubagentStop` and `ConfigChange`.

**3. Use second-resolution UTC timestamps.** They sort lexically, they compare without time zone arithmetic, and you convert to local time only when you display them.

**4. Know your transcript retention.** Harnesses store full session transcripts on disk, and some delete them after a set period. Check how long yours keep them, and copy out anything you must retain for audit before it expires. Do not assume an old session is still there.

**5. Treat transcripts as sensitive.** They contain file contents, command output and anything you pasted. Apply the same access controls as the code and data they touched.

**6. Track tokens and cost.** Record input tokens, output tokens and the model per session, and total them per day. A sudden jump is often a loop or an oversized context. See [Cost and resource discipline](../cost-and-resources/).

**7. Make the log queryable.** Plain lines are enough. A short script that answers "what changed since yesterday?" is worth more than a dashboard you never open.

**8. Prove it runs.** "Enabled" is not "running". After you add the hook, trigger an action and confirm a new line appears.

## Failure modes it prevents

- You cannot tell which session changed a file.
- A transcript you needed was deleted by the retention policy.
- Cost doubles for a week before anyone notices.
- A hook is configured but silently failing, so the log has gaps.

## Start here

Add the action-log hook above. Perform one edit and one command. Check that two lines appear.

<p class="verified">Verified against the Claude Code hooks reference (code.claude.com/docs/en/hooks) for the event names on 2026-10-22. Transcript retention periods vary by tool and version, so this page names no figure. Check your tool's documentation.</p>
