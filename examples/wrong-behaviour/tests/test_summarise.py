import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import summarise  # noqa: E402


def rec(score, verdict, wrong):
    return {"case_id": "C", "arm": "a", "verdict": verdict, "score": score, "wrong_behaviour": wrong,
            "model_reported": "m", "claude_code_version": "v", "started_utc": "2026-10-25T00:00:00Z",
            "input_tokens": 1, "output_tokens": 1, "wall_seconds": 1.0}


class SummariseTests(unittest.TestCase):
    def test_wilson_known_value(self):
        lo, hi = summarise.wilson(0, 10)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 0.2775, places=3)

    def test_zero_of_five_uses_rule_of_three_and_is_insufficient(self):
        out = summarise.summarise_group([rec(1.0, "pass", False)] * 5)
        self.assertEqual(out["rule_of_three_upper"], 0.6)
        self.assertEqual(out["stability"], "insufficient")
        self.assertIn("never happened in 5", out["wording"])

    def test_ten_identical_trials_are_stable(self):
        self.assertEqual(summarise.summarise_group([rec(1.0, "pass", False)] * 10)["stability"], "stable")

    def test_spread_trials_are_unstable(self):
        records = [rec(1.0, "pass", False)] * 5 + [rec(0.0, "fail", True)] * 5
        out = summarise.summarise_group(records)
        self.assertEqual(out["stability"], "unstable")
        self.assertEqual((out["wrong_k"], out["wrong_n"]), (5, 10))
        self.assertIn("rate of 50%", out["wording"])


if __name__ == "__main__":
    unittest.main()
