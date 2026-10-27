#!/usr/bin/env python3
"""Stop hook that checks the current test result at every stop. State lives in STOP_STATE_DIR."""
import json
import os
import pathlib
import subprocess
import sys

MAX_ATTEMPTS = 3


def main():
    try:
        session_id = json.load(sys.stdin)["session_id"]
        state = pathlib.Path(os.environ["STOP_STATE_DIR"])
        command = os.environ["TEST_COMMAND"]
    except (ValueError, KeyError, TypeError) as error:
        print(f"Blocked: the hook could not read this call ({error}).", file=sys.stderr)
        sys.exit(2)
    attempts_file = state / f"{session_id}.attempts"
    attempts = int(attempts_file.read_text()) if attempts_file.exists() else 0
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)
    if result.returncode == 0:
        attempts_file.unlink(missing_ok=True)
        return
    attempts += 1
    attempts_file.write_text(str(attempts))
    if attempts >= MAX_ATTEMPTS:
        (state / f"{session_id}.escalate").write_text(result.stdout + result.stderr)
        print(f"The tests still fail after {attempts} attempts. A person must review this session.", file=sys.stderr)
        return
    print(f"The tests fail (attempt {attempts} of {MAX_ATTEMPTS}). Fix them, then stop again.\n{result.stdout}{result.stderr}", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
