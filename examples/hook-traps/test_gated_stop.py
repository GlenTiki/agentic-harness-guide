#!/usr/bin/env python3
import json
import os
import pathlib
import subprocess
import tempfile

SCRIPT = pathlib.Path(__file__).resolve().parent / "gated_stop.py"


def stop(state_dir, session_id, test_command):
    env = {**os.environ, "STOP_STATE_DIR": state_dir, "TEST_COMMAND": test_command}
    result = subprocess.run(["python3", str(SCRIPT)], input=json.dumps({"session_id": session_id}), env=env, capture_output=True, text=True)
    return result.returncode


with tempfile.TemporaryDirectory() as state_dir:
    rows = [
        ("s1", "false", 2),
        ("s1", "false", 2),
        ("s1", "true", 0),
        ("s1", "false", 2),
        ("s2", "false", 2),
        ("s2", "false", 2),
        ("s2", "false", 0),
    ]
    for session_id, command, expected in rows:
        code = stop(state_dir, session_id, command)
        print(f"session={session_id} tests={'pass' if command == 'true' else 'fail'} exit={code} expect={expected}")
        assert code == expected
    escalated = sorted(path.name for path in pathlib.Path(state_dir).glob("*.escalate"))
    print(f"escalation files: {escalated}")
    assert escalated == ["s2.escalate"]
    env = {**os.environ, "STOP_STATE_DIR": state_dir, "TEST_COMMAND": "true"}
    bad = subprocess.run(["python3", str(SCRIPT)], input="not json", env=env, capture_output=True, text=True)
    print(f"unreadable input exit={bad.returncode} expect=2")
    assert bad.returncode == 2
print("ok")
