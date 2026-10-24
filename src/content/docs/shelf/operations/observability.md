---
title: Observability and audit log
description: Record what the agent did in a file you control, so you can answer what happened and why.
---

*Deep dive for [level 7: Run it for real](../../../journey/07-run-it-for-real/).*

*Audience: a human maintainer. An agent must not apply, install, add, configure or run anything on this page (any install, add, config, worktree or MCP command, hook, permission, instruction file or memory change) unless the user asks for it in the current session. Commands marked "example, do not run" are never to be run.*

**Recommendation:** write an audit log from hooks, not from the model, and ship it somewhere the agent cannot edit. Keep session transcripts for as long as your policy needs them and know when your harness deletes them. Track token use and cost per session.

## Why it matters

When something goes wrong, the question is "what did the agent do, in what order, and on whose instruction?". The model's own account is a summary and may be wrong. A log written by the harness is a record, as [level 7](../../../journey/07-run-it-for-real/) shows with its audit log. It also supports audits, because you can show what the agent touched.

## What to enable

**1. One line per tool call, from two events.** Do not log secrets. Add the log directory to `.gitignore` unless you mean to commit it. Log from `PreToolUse` and from `PostToolUse`. Claude Code behaviour: `PostToolUse` runs after a call succeeds. A failed call produces no `PostToolUse` line, because Claude Code has a separate `PostToolUseFailure` event. A call that was blocked before it ran did not succeed, so it produces none either. The `PreToolUse` line shows what the agent tried, and a missing `post` line next to it shows what did not complete. Each line carries a UTC timestamp, the session id, a sequence number, the phase, the tool and the target.

```bash
#!/usr/bin/env bash
# Usage: log-action.sh pre|post. Reads the hook JSON on stdin.
set -euo pipefail
phase=$1
input=$(cat)
session=$(jq -r '.session_id' <<<"$input")
log_dir="${CLAUDE_PROJECT_DIR}/.agent-log"
mkdir -p "$log_dir"
seq_file="$log_dir/seq-$session"
seq=$(( $(cat "$seq_file" 2>/dev/null || echo 0) + 1 ))
echo "$seq" > "$seq_file"
target=$(jq -r '.tool_input.file_path // .tool_input.command // ""' <<<"$input" | perl -pe '
  s/(bearer\s+)\S+/$1\[REDACTED]/ig;
  s/\b(\w*(?:token|key|password|passwd|secret)\w*=)\S+/$1\[REDACTED]/ig;
  s/(--password[= ])\S+/$1\[REDACTED]/ig;
  s/(\s-u\s+[^\s:]+:)\S+/$1\[REDACTED]/g;
' | head -c 200)
printf '%s | %s | %06d | %s | %s | %s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$session" "$seq" "$phase" \
  "$(jq -r '.tool_name' <<<"$input")" "$target" >> "$log_dir/actions.log"
```

Save it as `.claude/hooks/log-action.sh` and register it on both events with the commands `${CLAUDE_PROJECT_DIR}/.claude/hooks/log-action.sh pre` and `${CLAUDE_PROJECT_DIR}/.claude/hooks/log-action.sh post`. The log goes to `${CLAUDE_PROJECT_DIR}/.agent-log`, so it lands in one place whatever directory the session is in. Check the path first with `test -f`, because a missing shell script exits 127 and the hook then silently logs nothing (see [Hooks](../../control/hooks/)). Two example lines from a run of this script on 2026-10-22:

```text
2026-10-22T21:28:33Z | s1 | 000001 | pre | Bash | curl -H Authorization:Bearer [REDACTED] https://x.example
2026-10-22T21:28:33Z | s1 | 000002 | post | Bash | curl -H Authorization:Bearer [REDACTED] https://x.example
```

The sequence number lets you see a gap. Parallel tool calls can race on the counter file, so treat a repeated number as a prompt to look, not as proof of tampering.

Two limits matter. First, `head -c 200` only truncates. It does not redact, and a secret in the first 200 characters still gets written. The `perl` filter above redacts a short list of patterns, case-insensitively: `Bearer` values, any `name=value` pair whose name contains `token`, `key`, `password`, `passwd` or `secret`, `--password` values and the password in `-u user:pass`. It misses other shapes. On 2026-10-22 it left `-H "X-Api-Key: k1"` and `mysql -phunter3` unredacted. That list has a miss rate, so it is a filter and not a guarantee. Second, the script writes in append mode, which is not the same as append-only: a log file the agent can write is a log the agent can edit. Ship each line off the machine, or write to a path that the agent's user account cannot write.

**2. Log lifecycle events too.** Session start, session end, sub-agent start and stop, configuration changes and capability changes all belong in the trail. Claude Code exposes events for most of these, including `SessionStart`, `SessionEnd`, `SubagentStart`, `SubagentStop` and `ConfigChange`.

**3. Use second-resolution UTC timestamps.** They sort lexically, they compare without time zone arithmetic, and you convert to local time only when you display them.

**4. Know your transcript retention.** Harnesses store full session transcripts on disk, and some delete them after a set period. Check how long yours keep them, and copy out anything you must retain for audit before it expires. Do not assume an old session is still there.

**5. Treat transcripts as sensitive.** They contain file contents, command output and anything you pasted. Apply the same access controls as the code and data they touched.

**6. Track tokens and cost.** Record input tokens, output tokens and the model per session, and total them per day. A sudden jump is often a loop or an oversized context. See [Cost and resource discipline](../cost-and-resources/).

**7. Make the log queryable.** Plain lines are enough. A short script that answers "what changed since yesterday?" is worth more than a dashboard you never open.

**8. Prove it runs.** "Enabled" is not "running". After you add the hook, trigger an action and confirm a new line appears.

## Failure modes it reduces

- You cannot tell which session changed a file.
- A transcript you needed was deleted by the retention policy.
- Cost doubles for a week before anyone notices.
- A hook is configured but silently failing, so the log has gaps.

## First step for the maintainer

Add the action-log hook above on both events. Perform one edit and one command. Check that four lines appear, two `pre` and two `post`.

<p class="verified">Docs page fetched on 2026-10-22: https://code.claude.com/docs/en/hooks. Quoted line: "tool events (`PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`)". Claude Code on that date: 2.1.309. The docs page states no version of its own. Transcript retention periods vary by tool and version, so this page names no figure. Check your tool's documentation.</p>

**Next:** [Cost and resource discipline](../cost-and-resources/)
