#!/usr/bin/env python3
import json
import os
import pathlib
import shlex
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent / "gated_stop.py"


def stop(
    state_dir: str,
    session_id: str | int | None,
    test_command: str,
    script: pathlib.Path = SCRIPT,
    timeout: float | None = None,
) -> int:
    env = {**os.environ, "STOP_STATE_DIR": state_dir, "TEST_COMMAND": test_command}
    args = [sys.executable, "-I", str(script)]
    if timeout is not None:
        args = [
            sys.executable,
            "-I",
            "-c",
            "import runpy,sys; runpy.run_path(sys.argv[1])['main'](timeout=float(sys.argv[2]))",
            str(script),
            str(timeout),
        ]
    result = subprocess.run(
        args, input=json.dumps({"session_id": session_id}), env=env, capture_output=True, text=True, timeout=5
    )
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
    bad = subprocess.run(
        [sys.executable, "-I", str(SCRIPT)], input="not json", env=env, capture_output=True, text=True, timeout=5
    )
    print(f"unreadable input exit={bad.returncode} expect=2")
    assert bad.returncode == 2
print("ok")


class GateFailureTests(unittest.TestCase):
    def test_timeouts_count_toward_three_attempt_escalation(self) -> None:
        command = f"exec {shlex.quote(sys.executable)} -I -c {shlex.quote('import time; time.sleep(1)')}"
        with tempfile.TemporaryDirectory() as state_dir:
            for expected in (2, 2, 0):
                self.assertEqual(stop(state_dir, "timeout", command, timeout=0.01), expected)
            self.assertIn("timed out", (pathlib.Path(state_dir) / "timeout.escalate").read_text())

    def test_missing_state_directory_blocks_even_when_tests_pass(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(stop(str(pathlib.Path(root) / "absent"), "missing", "true"), 2)

    def test_corrupt_attempt_count_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            (pathlib.Path(state_dir) / "broken.attempts").write_text("not a number")
            self.assertEqual(stop(state_dir, "broken", "true"), 2)

    def test_unwritable_state_directory_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            state = pathlib.Path(state_dir)
            state.chmod(0o500)
            try:
                self.assertEqual(stop(state_dir, "read-only", "false"), 2)
            finally:
                state.chmod(0o700)

    def test_unwritable_escalation_target_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            state = pathlib.Path(state_dir)
            (state / "blocked.attempts").write_text("2")
            (state / "blocked.escalate").mkdir()
            self.assertEqual(stop(state_dir, "blocked", "false"), 2)

    def test_invalid_session_id_cannot_write_outside_state(self) -> None:
        scripts = [SCRIPT, SCRIPT.with_name("one_shot_stop.py")]
        invalid: list[str | int | None] = ["", None, 42, ".", "..", "../outside", "nested/session", "nested\\session"]
        for script in scripts:
            for identifier in invalid + ["absolute"]:
                with tempfile.TemporaryDirectory() as root:
                    state = pathlib.Path(root) / "state"
                    state.mkdir()
                    session_id = str(pathlib.Path(root) / "absolute") if identifier == "absolute" else identifier
                    with self.subTest(script=script.name, session_id=session_id):
                        self.assertEqual(stop(str(state), session_id, "false", script=script), 2)
                        self.assertEqual(list(state.iterdir()), [])
                        self.assertEqual(list(pathlib.Path(root).iterdir()), [state])


if __name__ == "__main__":
    unittest.main()
