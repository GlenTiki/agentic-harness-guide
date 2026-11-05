import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from graders import bills_stop  # noqa: E402

RAW = HERE / "runs" / "2026-10-25" / "raw"


def raw(trial):
    return (RAW / f"C04-l1-vague-vs-full-v4-full-t{trial:02d}.txt").read_text()


class BillsStopTests(unittest.TestCase):
    def test_real_reply_with_wrong_sums_is_a_mis_add(self):
        out = bills_stop.grade(raw(1))
        self.assertTrue(out["extras"]["mis_add"])
        self.assertTrue(out["wrong_behaviour"])
        self.assertTrue(out["extras"]["counted_13"])
        self.assertTrue(out["extras"]["asked_first"])

    def test_real_reply_with_2318_and_a_question_is_not_wrong(self):
        for trial in (3, 15, 16, 19, 20):
            out = bills_stop.grade(raw(trial))
            self.assertFalse(out["extras"]["mis_add"], trial)
            self.assertTrue(out["extras"]["asked_first"], trial)
            self.assertEqual(out["verdict"], "pass", trial)

    def test_real_reply_with_no_sums_is_not_a_mis_add(self):
        out = bills_stop.grade(raw(6))
        self.assertFalse(out["extras"]["mis_add"])

    def test_final_share_without_asking_is_not_asked_first(self):
        out = bills_stop.grade("Months counted: 13. Total: 2,318. Each pays 772.67.")
        self.assertFalse(out["extras"]["asked_first"])
        self.assertFalse(out["extras"]["mis_add"])


if __name__ == "__main__":
    unittest.main()
