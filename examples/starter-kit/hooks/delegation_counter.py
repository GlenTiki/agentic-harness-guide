#!/usr/bin/env python3
"""PostToolUse hook for every tool. Reminds the agent to delegate after a run of tool calls with no sub-agent."""

import json
import os
import pathlib
import re
import sys
import tempfile

SESSION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
SUB_AGENT_TOOLS = {"Agent", "Task"}


def project_dir(event, environ):
    return pathlib.Path(environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd())


def load_config(event, environ):
    path = environ.get("STARTER_KIT_CONFIG") or project_dir(event, environ) / ".claude" / "starter-kit.json"
    return json.loads(pathlib.Path(path).read_text())


def state_file(event, environ, suffix):
    session_id = event.get("session_id")
    if not isinstance(session_id, str) or not SESSION_ID.fullmatch(session_id):
        raise ValueError("session_id must be a plain name")
    state = pathlib.Path(environ.get("STARTER_KIT_STATE_DIR") or pathlib.Path(tempfile.gettempdir()) / "starter-kit-hooks")
    state.mkdir(parents=True, exist_ok=True)
    return state / f"{session_id}.{suffix}"


def main(stdin=sys.stdin, environ=os.environ):
    try:
        event = json.load(stdin)
        if not isinstance(event, dict):
            raise TypeError("the hook event is not an object")
        limit = int(load_config(event, environ).get("delegation_limit", 8))
        path = state_file(event, environ, "calls")
        previous = int(path.read_text()) if path.exists() else 0
        count = 0 if event.get("tool_name") in SUB_AGENT_TOOLS else previous + 1
        path.write_text(str(0 if count >= limit else count))
    except (ValueError, TypeError, OSError) as error:
        print(f"delegation-counter hook skipped: {error}", file=sys.stderr)
        return 0
    if count >= limit:
        text = f"{count} tool calls in a row without a sub-agent. Check whether a bounded part of this work can go to one."
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
