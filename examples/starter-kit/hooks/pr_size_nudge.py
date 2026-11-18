#!/usr/bin/env python3
"""PreToolUse hook for Bash. Before git push, reminds the agent when the change is large. It never blocks."""

import json
import os
import pathlib
import shlex
import subprocess
import sys


def project_dir(event, environ):
    return pathlib.Path(environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd())


def load_config(event, environ):
    path = environ.get("STARTER_KIT_CONFIG") or project_dir(event, environ) / ".claude" / "starter-kit.json"
    return json.loads(pathlib.Path(path).read_text())


def is_push(command):
    tokens = shlex.split(command)
    return any(os.path.basename(token) == "git" and "push" in tokens[index:] for index, token in enumerate(tokens))


def diff_size(cwd, base_ref):
    result = subprocess.run(
        ["git", "diff", "--numstat", f"{base_ref}...HEAD"], cwd=cwd, capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise OSError(result.stderr.strip() or "git diff failed")
    rows = [line.split("\t") for line in result.stdout.splitlines() if line]
    lines = sum(int(added) + int(deleted) for added, deleted, _ in rows if added != "-")
    return lines, len(rows)


def main(stdin=sys.stdin, environ=os.environ):
    try:
        event = json.load(stdin)
        if not isinstance(event, dict) or not is_push(str((event.get("tool_input") or {}).get("command", ""))):
            return 0
        config = load_config(event, environ)
        base_ref = config.get("base_ref", "origin/main")
        lines, files = diff_size(project_dir(event, environ), base_ref)
    except (ValueError, TypeError, OSError, subprocess.TimeoutExpired) as error:
        print(f"pr-size-nudge hook skipped: {error}", file=sys.stderr)
        return 0
    max_lines, max_files = int(config.get("pr_max_lines", 400)), int(config.get("pr_max_files", 8))
    if lines <= max_lines and files <= max_files:
        return 0
    text = (
        f"This push changes {lines} lines in {files} files against {base_ref}. The nudge starts above {max_lines} "
        f"lines or {max_files} files. Check that it is still one concept, or split it into stacked pull requests."
    )
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": text}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
