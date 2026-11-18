#!/usr/bin/env python3
"""PostToolUse hook for Write and Edit. Returns lint errors to the agent as context. It never blocks."""

import json
import os
import pathlib
import shlex
import subprocess
import sys

OUTPUT_TAIL = 3000


def project_dir(event, environ):
    return pathlib.Path(environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd())


def load_config(event, environ):
    path = environ.get("STARTER_KIT_CONFIG") or project_dir(event, environ) / ".claude" / "starter-kit.json"
    return json.loads(pathlib.Path(path).read_text())


def context(text):
    return json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}})


def lint_report(event, environ):
    command = environ.get("STARTER_KIT_LINT_COMMAND") or load_config(event, environ).get("lint_command")
    if not isinstance(command, str) or not command:
        return None
    try:
        result = subprocess.run(
            shlex.split(command), cwd=project_dir(event, environ), capture_output=True, text=True, timeout=120
        )
    except FileNotFoundError as error:
        return f"The lint hook could not start {error.filename}."
    except subprocess.TimeoutExpired:
        return "The lint command did not finish in 120 seconds."
    if result.returncode == 0:
        return None
    return f"Lint errors after this write (exit {result.returncode}):\n{(result.stdout + result.stderr)[-OUTPUT_TAIL:]}"


def main(stdin=sys.stdin, environ=os.environ):
    try:
        event = json.load(stdin)
        if not isinstance(event, dict):
            raise TypeError("the hook event is not an object")
        report = lint_report(event, environ)
    except (ValueError, TypeError, OSError) as error:
        report = f"The lint hook could not run ({error})."
    if report:
        print(context(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
