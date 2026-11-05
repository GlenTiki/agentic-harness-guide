import io
import unittest
from pathlib import Path

import binomial
import calibrate

HERE = Path(__file__).resolve().parent
PAIRS = calibrate.read_labels(HERE / "labels.csv")


class Calibrate(unittest.TestCase):
    def test_perfect_judge_has_kappa_one(self):
        pairs = [("pass", "pass"), ("fail", "fail"), ("pass", "pass")]
        self.assertEqual(calibrate.cohen_kappa(pairs), 1.0)

    def test_chance_level_judge_has_kappa_zero(self):
        pairs = [("pass", "pass"), ("pass", "fail"), ("fail", "pass"), ("fail", "fail")]
        self.assertEqual(calibrate.cohen_kappa(pairs), 0.0)

    def test_a_judge_that_always_passes_scores_high_agreement_and_zero_kappa(self):
        pairs = [("pass", "pass")] * 9 + [("fail", "pass")]
        self.assertEqual(calibrate.agreement(pairs), 0.9)
        self.assertEqual(calibrate.cohen_kappa(pairs), 0.0)

    def test_one_label_everywhere_is_undefined(self):
        with self.assertRaises(ValueError):
            calibrate.cohen_kappa([("pass", "pass")] * 3)

    def test_fixture_numbers(self):
        self.assertEqual(calibrate.agreement(PAIRS), 0.8)
        self.assertAlmostEqual(calibrate.cohen_kappa(PAIRS), 0.5833, places=4)
        self.assertEqual(calibrate.failure_recall(PAIRS), 0.75)

    def test_criterion_decides_the_verdict(self):
        self.assertFalse(calibrate.verdict(PAIRS, 0.6, 0.8))
        self.assertTrue(calibrate.verdict(PAIRS, 0.5, 0.7))

    def test_report_exit_code_follows_the_verdict(self):
        self.assertEqual(calibrate.report(PAIRS, 0.6, 0.8, io.StringIO()), 1)
        self.assertEqual(calibrate.report(PAIRS, 0.5, 0.7, io.StringIO()), 0)


class Binomial(unittest.TestCase):
    def test_all_runs_clean_matches_power(self):
        self.assertAlmostEqual(binomial.at_most(0, 20, 0.05), 0.95**20)

    def test_whole_distribution_sums_to_one(self):
        self.assertAlmostEqual(binomial.at_most(20, 20, 0.3), 1.0)

    def test_fisher_equal_results_is_above_half(self):
        self.assertGreater(binomial.fisher_one_sided(3, 20, 3, 20), 0.5)

    def test_fisher_large_difference_is_small(self):
        self.assertLess(binomial.fisher_one_sided(12, 20, 2, 20), 0.01)

    def test_fisher_matches_hand_count_on_a_tiny_case(self):
        self.assertAlmostEqual(binomial.fisher_one_sided(1, 2, 0, 2), 0.5)


if __name__ == "__main__":
    unittest.main()
