#!/usr/bin/env python3
"""Stop hook that blocks once per session. State lives in the directory named by STOP_STATE_DIR."""
import json
import os
import pathlib
import sys


def main():
    try:
        session_id = json.load(sys.stdin)["session_id"]
        marker = pathlib.Path(os.environ["STOP_STATE_DIR"]) / f"{session_id}.done"
    except (ValueError, KeyError, TypeError) as error:
        print(f"Blocked: the hook could not read this call ({error}).", file=sys.stderr)
        sys.exit(2)
    if marker.exists():
        return
    marker.touch()
    print("Run the test suite and report the result before you stop.", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
