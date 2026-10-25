import io
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import heartbeat_check
import watch

HERE = Path(__file__).resolve().parent
NOW = datetime(2026, 10, 25, 9, 1, 0, tzinfo=timezone.utc)


def run_check(name, limit=120):
    out, err = io.StringIO(), io.StringIO()
    code = heartbeat_check.check(HERE / "fixtures" / name, limit, NOW, out, err)
    return code, out.getvalue(), err.getvalue()


class HeartbeatCheck(unittest.TestCase):
    def test_fresh_log_exits_zero(self):
        self.assertEqual(run_check("fresh.jsonl"), (0, "OK: last event 2026-10-25T09:00:30Z, limit 120s\n", ""))

    def test_stale_log_goes_red(self):
        self.assertEqual(run_check("stale.jsonl"), (1, "STALE: last event 2026-10-25T08:00:30Z, limit 120s\n", ""))

    def test_unparseable_log_exits_two_and_says_why(self):
        code, out, err = run_check("broken.jsonl")
        self.assertEqual((code, out), (2, ""))
        self.assertIn("line 2", err)

    def test_missing_log_exits_two(self):
        out, err = io.StringIO(), io.StringIO()
        self.assertEqual(heartbeat_check.check(HERE / "fixtures" / "absent.jsonl", 120, NOW, out, err), 2)
        self.assertIn("BROKEN", err.getvalue())

    def test_empty_log_exits_two(self):
        with tempfile.TemporaryDirectory() as folder:
            empty = Path(folder) / "empty.jsonl"
            empty.write_text("")
            self.assertEqual(heartbeat_check.check(empty, 120, NOW, io.StringIO(), io.StringIO()), 2)


class Watch(unittest.TestCase):
    def test_reruns_once_after_a_change_and_reports_pass_then_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            note = directory / "note.txt"
            note.write_text("ok")
            command = ["python3", "-I", "-c", "import sys; sys.exit(1 if 'bad' in open('note.txt').read() else 0)"]
            out = io.StringIO()
            sleeps = []

            def fake_sleep(seconds):
                sleeps.append(seconds)
                if len(sleeps) == 1:
                    note.write_text("bad!")

            runs = watch.watch(directory, command, 0.1, 0.1, max_runs=2, now=lambda: "T", sleep=fake_sleep, out=out)
            self.assertEqual(runs, 2)
            self.assertEqual(out.getvalue(), "PASS T exit=0\nFAIL T exit=1\n")


if __name__ == "__main__":
    unittest.main()
