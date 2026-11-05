#!/usr/bin/env python3
"""Stop hook that checks the current test result at every stop. State lives in STOP_STATE_DIR."""

import json
import os
import pathlib
import re
import subprocess
import sys

MAX_ATTEMPTS = 3


def main(timeout: float = 300) -> None:
    try:
        session_id = json.load(sys.stdin)["session_id"]
        if not isinstance(session_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", session_id):
            raise ValueError("session_id must be a plain filename starting with a letter or digit")
        state = pathlib.Path(os.environ["STOP_STATE_DIR"])
        if not state.is_dir():
            raise NotADirectoryError("STOP_STATE_DIR must name an existing directory")
        command = os.environ["TEST_COMMAND"]
        attempts_file = state / f"{session_id}.attempts"
        attempts = int(attempts_file.read_text()) if attempts_file.exists() else 0
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            result = subprocess.CompletedProcess(command, 1, "", f"Test command timed out after {timeout} seconds.\n")
        if result.returncode == 0:
            attempts_file.unlink(missing_ok=True)
            return
        attempts += 1
        attempts_file.write_text(str(attempts))
        if attempts >= MAX_ATTEMPTS:
            (state / f"{session_id}.escalate").write_text(result.stdout + result.stderr)
            print(
                f"The tests still fail after {attempts} attempts. A person must review this session.", file=sys.stderr
            )
            return
        print(
            f"The tests fail (attempt {attempts} of {MAX_ATTEMPTS}). Fix them, then stop again.\n"
            f"{result.stdout}{result.stderr}",
            file=sys.stderr,
        )
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f"Blocked: the hook could not check this stop ({error}).", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
