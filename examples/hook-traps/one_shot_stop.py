#!/usr/bin/env python3
"""Stop hook that blocks once per session. State lives in the directory named by STOP_STATE_DIR."""

import json
import os
import pathlib
import re
import sys


def main() -> None:
    try:
        session_id = json.load(sys.stdin)["session_id"]
        if not isinstance(session_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", session_id):
            raise ValueError("session_id must be a plain filename starting with a letter or digit")
        marker = pathlib.Path(os.environ["STOP_STATE_DIR"]) / f"{session_id}.done"
        if marker.exists():
            return
        marker.touch()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f"Blocked: the hook could not read this call ({error}).", file=sys.stderr)
        sys.exit(2)
    print("Run the test suite and report the result before you stop.", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
