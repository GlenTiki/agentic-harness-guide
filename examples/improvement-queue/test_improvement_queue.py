import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import improvement_queue

HERE = Path(__file__).resolve().parent


def post(target, minutes=None, tool="Bash"):
    record = {"time": "2026-10-01T09:00:00Z", "session": "s1", "seq": 1, "phase": "post", "tool": tool, "id": "t1", "target": target}
    if minutes is not None:
        record["minutes"] = minutes
    return json.dumps(record)


def run_cli(text):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "log.jsonl"
        path.write_text(text)
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = improvement_queue.main([str(path)])
    return code, out.getvalue(), err.getvalue()


class ImprovementQueue(unittest.TestCase):
    def test_a_rare_cheap_step_ranks_below_a_frequent_costly_one(self):
        lines = [post("rare cheap", 1)] * 2 + [post("frequent costly", 5)] * 4
        ranked = improvement_queue.rank(improvement_queue.read_steps(lines))
        self.assertEqual([key[1] for key, _ in ranked], ["frequent costly", "rare cheap"])

    def test_a_step_that_ran_once_is_not_repeated(self):
        self.assertEqual(improvement_queue.rank(improvement_queue.read_steps([post("once", 30)])), [])

    def test_only_the_top_three_get_a_recommendation(self):
        lines = [post(name, 1) for name in "abcd" for _ in range(2)]
        self.assertEqual(len(improvement_queue.rank(improvement_queue.read_steps(lines))), 3)

    def test_a_pre_line_is_ignored(self):
        pre = json.dumps({"phase": "pre", "tool": "Bash", "target": "x"})
        self.assertEqual(len(improvement_queue.read_steps([pre, post("x", 2), post("x", 2)])[("Bash", "x")]), 2)

    def test_a_line_without_minutes_counts_as_one_minute(self):
        self.assertEqual(improvement_queue.read_steps([post("x")])[("Bash", "x")], [1])

    def test_an_empty_log_exits_zero_with_a_message(self):
        code, out, _ = run_cli("")
        self.assertEqual((code, out), (0, "The log has no finished steps.\n"))

    def test_a_malformed_line_fails_loudly_and_names_the_line(self):
        code, out, err = run_cli(post("x", 1) + "\n{not json\n")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("error: line 2: not a valid log line", err)

    def test_a_line_missing_a_field_fails_loudly(self):
        code, _, err = run_cli(json.dumps({"phase": "post", "tool": "Bash"}) + "\n")
        self.assertEqual(code, 1)
        self.assertIn("line 1", err)

    def test_negative_minutes_fail_loudly(self):
        code, _, err = run_cli(post("x", -3) + "\n")
        self.assertEqual(code, 1)
        self.assertIn("line 1: minutes must be a number", err)

    def test_the_fixture_gives_three_recommendations_in_order(self):
        code, out, _ = run_cli((HERE / "fixtures" / "actions.jsonl").read_text())
        self.assertEqual(code, 0)
        self.assertEqual(
            out.splitlines(),
            [
                "1. You did 'sort bank-export.csv by date' by hand 6 times. Recommend automating it. Estimated saving: up to 24 minutes for this log.",
                "2. You did 'copy totals into summary.md' by hand 3 times. Recommend automating it. Estimated saving: up to 18 minutes for this log.",
                "3. You did 'rename receipt photos' by hand 5 times. Recommend automating it. Estimated saving: up to 15 minutes for this log.",
            ],
        )

    def test_the_fixture_has_a_frequent_cheap_step_below_the_top_three(self):
        steps = improvement_queue.read_steps((HERE / "fixtures" / "actions.jsonl").read_text().splitlines())
        self.assertEqual(sum(steps[("Bash", "open notes for Mina")]), 7)
        self.assertEqual(sum(steps[("Bash", "fix February header")]), 4)


if __name__ == "__main__":
    unittest.main()
