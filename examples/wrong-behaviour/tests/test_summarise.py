import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import summarise  # noqa: E402


def rec(score, verdict, wrong):
    return {"case_id": "C", "arm": "a", "verdict": verdict, "score": score, "wrong_behaviour": wrong,
            "model_reported": "m", "claude_code_version": "v", "started_utc": "2026-10-25T00:00:00Z",
            "input_tokens": 1, "output_tokens": 1, "wall_seconds": 1.0, "grader_version": "test sha256 new"}


class SummariseTests(unittest.TestCase):
    def test_main_writes_separate_report_and_preserves_historical_bytes(self):
        preserved = {p: p.read_bytes() for p in (summarise.HERE / "results.json", summarise.HERE / "RESULTS.md")}
        with tempfile.TemporaryDirectory() as directory:
            summarise.main(["--out", directory])
            self.assertTrue((Path(directory) / "results.json").exists())
            self.assertTrue((Path(directory) / "RESULTS.md").exists())
        for path, original in preserved.items():
            self.assertEqual(path.read_bytes(), original)

    def test_main_refuses_canonical_output_before_writing(self):
        preserved = {p: p.read_bytes() for p in (summarise.HERE / "results.json", summarise.HERE / "RESULTS.md")}
        with self.assertRaisesRegex(ValueError, "preserved historical"):
            summarise.main(["--out", str(summarise.HERE)])
        for path, original in preserved.items():
            self.assertEqual(path.read_bytes(), original)

    def test_main_refuses_output_symlink_to_preserved_file(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / "results.json").symlink_to(summarise.HERE / "results.json")
            with self.assertRaisesRegex(ValueError, "preserved historical"):
                summarise.main(["--out", directory])
            self.assertFalse((Path(directory) / "RESULTS.md").exists())

    def test_main_selects_only_new_run_corpus(self):
        with tempfile.TemporaryDirectory() as directory:
            runs = Path(directory) / "runs"
            runs.mkdir()
            (runs / "new.jsonl").write_text(json.dumps(rec(1.0, "pending", None)) + "\n")
            out = Path(directory) / "report"
            summarise.main(["--runs", str(runs), "--out", str(out)])
            rows = json.loads((out / "results.json").read_text())
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["grader_version"], "test sha256 new")

    def test_main_rejects_mixed_versions_before_creating_output(self):
        with tempfile.TemporaryDirectory() as directory:
            runs = Path(directory) / "runs"
            runs.mkdir()
            records = [rec(1.0, "pending", None), {**rec(1.0, "pending", None), "grader_version": "older"}]
            (runs / "mixed.jsonl").write_text("\n".join(json.dumps(r) for r in records))
            out = Path(directory) / "report"
            with self.assertRaisesRegex(ValueError, "Mixed grader versions"):
                summarise.main(["--runs", str(runs), "--out", str(out)])
            self.assertFalse(out.exists())

    def test_legacy_hashes_match_actual_historical_records(self):
        for case, grader in (("C01-bills-total", "bills"), ("C02-doi-citation", "doi")):
            records = [json.loads(line) for path in (summarise.HERE / "runs/2026-10-25").glob(f"{case}*.jsonl")
                       for line in path.read_text().splitlines() if line.strip()]
            self.assertTrue(records)
            self.assertEqual({r["grader_version"] for r in records}, {summarise.LEGACY_GRADERS[grader]})

    def test_mixed_grader_versions_are_rejected(self):
        records = [{**rec(1.0, "pass", False), "grader_version": "doi sha256 bedc748645292ca1"},
                   {**rec(1.0, "pending", None), "grader_version": "doi sha256 new"}]
        with self.assertRaisesRegex(ValueError, "Mixed grader versions"):
            summarise.summarise_group(records)

    def test_pure_new_grader_does_not_receive_legacy_wording_or_counts(self):
        for case, arm in (("C02-doi-citation", "asis"), ("C01-bills-total", "long-unlabelled")):
            with self.subTest(case=case):
                record = {**rec(1.0, "pending", None), "case_id": case, "arm": arm}
                out = summarise.summarise_group([record])
                self.assertEqual(out["grader_version"], "test sha256 new")
                self.assertNotIn("unresolved_doi_k", out)
                self.assertNotIn("Historical DOI", out["wording"])
                self.assertNotIn("Legacy author-reference", out["wording"])

    def test_known_historical_grader_keeps_qualified_legacy_wording(self):
        record = {**rec(1.0, "pass", False), "case_id": "C02-doi-citation", "arm": "asis",
                  "grader_version": "doi sha256 bedc748645292ca1"}
        out = summarise.summarise_group([record])
        self.assertIn("Historical DOI", out["wording"])
        self.assertIn("unresolved_doi_k", out)

    def test_pending_doi_verification_is_not_a_pass_or_a_known_error(self):
        out = summarise.summarise_group([rec(1.0, "pending", None)])
        self.assertEqual(out["pending"], 1)
        self.assertEqual((out["pass"], out["partial"], out["fail"]), (0, 0, 0))
        self.assertEqual(out["wrong_n"], 0)
        self.assertIsNone(out["wilson95"])

    def test_wilson_known_value(self):
        lo, hi = summarise.wilson(0, 10)
        self.assertEqual(lo, 0.0)
        self.assertAlmostEqual(hi, 0.2775, places=3)

    def test_zero_of_five_uses_rule_of_three_and_is_insufficient(self):
        out = summarise.summarise_group([rec(1.0, "pass", False)] * 5)
        self.assertEqual(out["rule_of_three_upper"], 0.6)
        self.assertEqual(out["stability"], "insufficient")
        self.assertIn("never happened in 5", out["wording"])

    def test_headline_sample_excludes_unmeasured_and_failed_runs(self) -> None:
        records = [rec(1.0, "pass", False),
                   {**rec(1.0, "pass", False), "wrong_headline": None},
                   {**rec(1.0, "pass", False), "wrong_headline": False},
                   {**rec(0.0, "fail", True), "wrong_headline": True},
                   {**rec(0.0, "error", None), "wrong_headline": True}]
        out = summarise.summarise_group(records)
        self.assertEqual((out["headline_wrong_k"], out["headline_wrong_n"]), (1, 2))

    def test_unmeasured_headlines_have_no_sample(self) -> None:
        out = summarise.summarise_group([rec(1.0, "pass", False)])
        self.assertEqual(out["headline_wrong_n"], 0)

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
