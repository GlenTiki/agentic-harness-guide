#!/usr/bin/env python3
"""UserPromptSubmit hook. Adds the memory index to the context every Nth prompt. It never blocks."""

import json
import os
import pathlib
import re
import sys
import tempfile

SESSION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
MAX_CHARS = 9000


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
        every = positive_setting(config, "recall_every", 10)
        path = state_file(event, environ, "prompts")
        count = (int(path.read_text()) if path.exists() else 0) + 1
        path.write_text(str(count))
        if count % every:
            return 0
        recall = project_dir(event, environ) / config.get("recall_file", "memory/INDEX.md")
        facts = recall.read_text()
    except (ValueError, TypeError, OSError) as error:
        print(f"recall-reinject hook skipped: {error}", file=sys.stderr)
        return 0
    if len(facts) > MAX_CHARS:
        facts = facts[:MAX_CHARS] + "\n[cut at 9,000 characters]"
    text = f"Memory index, added every {every} prompts. Read the notes that apply before you act:\n{facts}"
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": text}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
