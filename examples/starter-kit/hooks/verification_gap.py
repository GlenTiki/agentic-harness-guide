#!/usr/bin/env python3
"""PostToolUse hook for Write, Edit and Bash. Reminds the agent when files change and the tests have not run."""

import json
import os
import pathlib
import re
import sys
import tempfile

SESSION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")


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


def ran_tests(command, test_command):
    return bool(test_command) and " ".join(test_command.split()) in " ".join(command.split())


def update(event, config, files):
    tool_input = event.get("tool_input") or {}
    if event.get("tool_name") == "Bash":
        return [] if ran_tests(str(tool_input.get("command", "")), config.get("test_command")) else files
    path = tool_input.get("file_path")
    return files + [path] if isinstance(path, str) and path not in files else files


def positive_setting(config, key, default):
    value = config.get(key, default)
    if type(value) is not int or value < 1:
        raise ValueError(f"{key} must be a whole number of 1 or more, not {value!r}")
    return value


def main(stdin=sys.stdin, environ=os.environ):
    try:
        event = json.load(stdin)
        if not isinstance(event, dict):
            raise TypeError("the hook event is not an object")
        config = load_config(event, environ)
        threshold = positive_setting(config, "verification_gap_files", 3)
        path = state_file(event, environ, "written")
        before = json.loads(path.read_text()) if path.exists() else []
        after = update(event, config, before)
        path.write_text(json.dumps(after))
    except (ValueError, TypeError, OSError) as error:
        print(f"verification-gap hook skipped: {error}", file=sys.stderr)
        return 0
    if len(after) > len(before) and len(after) % threshold == 0:
        text = f"You changed {len(after)} files since the last test run: {', '.join(after)}. Run the tests now."
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
