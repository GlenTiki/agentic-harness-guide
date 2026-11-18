#!/usr/bin/env python3
"""Stop hook. Exit 2 sends the agent back to work while the configured test command fails."""

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


def test_command(event, environ):
    command = environ.get("STARTER_KIT_TEST_COMMAND") or load_config(event, environ).get("test_command")
    args = shlex.split(command) if isinstance(command, str) else []
    if not args:
        raise ValueError("no test command is configured")
    return args


def main(stdin=sys.stdin, environ=os.environ):
    try:
        event = json.load(stdin)
        if not isinstance(event, dict):
            raise TypeError("the hook event is not an object")
        if event.get("stop_hook_active") is True:
            return 0
        args = test_command(event, environ)
        timeout = float(environ.get("STARTER_KIT_TEST_TIMEOUT", "300"))
        result = subprocess.run(args, cwd=project_dir(event, environ), capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as error:
        print(f"The tests did not finish in {error.timeout} seconds. Make them faster or raise the limit.", file=sys.stderr)
        return 2
    except FileNotFoundError as error:
        print(f"Blocked: the hook could not start {error.filename}.", file=sys.stderr)
        return 2
    except (ValueError, TypeError, OSError) as error:
        print(f"Blocked: the hook could not check this stop ({error}).", file=sys.stderr)
        return 2
    if result.returncode == 0:
        return 0
    output = (result.stdout + result.stderr)[-OUTPUT_TAIL:]
    print(f"The tests fail (exit {result.returncode}). Fix them, then stop again.\n{output}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
