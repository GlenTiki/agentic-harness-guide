#!/usr/bin/env python3
"""Stop hook. Blocks the first stop of each session once, with a reminder to save durable facts."""

import json
import os
import pathlib
import re
import sys
import tempfile

SESSION_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
REMINDER = (
    "Before you stop, check this session for durable facts: decisions, constraints, roles and preferences. "
    "Save each new fact as one note in memory/ and add its line to memory/INDEX.md, following memory/README.md. "
    "Edit an existing note instead of writing a duplicate. If there is nothing to save, stop again."
)


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
        if event.get("stop_hook_active") is True:
            return 0
        marker = state_file(event, environ, "memory-asked")
        if marker.exists():
            return 0
        marker.write_text("asked\n")
    except (ValueError, TypeError, OSError) as error:
        print(f"memory-save-on-stop hook skipped: {error}", file=sys.stderr)
        return 0
    print(REMINDER, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
