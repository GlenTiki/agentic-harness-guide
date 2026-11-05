#!/usr/bin/env python3
import json
import os
import pathlib
import subprocess
import tempfile

SCRIPT = pathlib.Path(__file__).resolve().parent / "one_shot_stop.py"


def stop(state_dir, session_id):
    env = {**os.environ, "STOP_STATE_DIR": state_dir}
    result = subprocess.run(["python3", str(SCRIPT)], input=json.dumps({"session_id": session_id}), env=env, capture_output=True, text=True)
    return result.returncode


with tempfile.TemporaryDirectory() as state_dir:
    rows = [("s1", 2), ("s1", 0), ("s1", 0), ("s2", 2), ("s2", 0)]
    for session_id, expected in rows:
        code = stop(state_dir, session_id)
        print(f"session={session_id} exit={code} expect={expected}")
        assert code == expected
    env = {**os.environ, "STOP_STATE_DIR": state_dir}
    bad = subprocess.run(["python3", str(SCRIPT)], input="not json", env=env, capture_output=True, text=True)
    print(f"unreadable input exit={bad.returncode} expect=2")
    assert bad.returncode == 2
print("ok")
