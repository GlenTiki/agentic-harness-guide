import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import reply_check

HERE = Path(__file__).resolve().parent
CASES = json.loads((HERE / "cases.json").read_text())
CLEAN = CASES["clean"]["figures"]


class FixtureVerdicts(unittest.TestCase):
    def test_every_good_reply_is_accepted_and_every_bad_reply_is_rejected(self):
        paths = sorted((HERE / "fixtures").glob("*/*.txt"))
        self.assertGreaterEqual(len(paths), 8)
        for path in paths:
            errors = reply_check.validate(path.read_text(), CASES[path.parent.name]["figures"])
            self.assertEqual(not errors, path.stem.startswith("good"), f"{path.name}: {errors}")

    def test_a_reply_that_drops_the_check_still_parses(self):
        text = (HERE / "fixtures/clean/bad-check-dropped.txt").read_text()
        self.assertTrue(reply_check.syntax_only(text))
        self.assertEqual(reply_check.validate(text, CLEAN), ["missing key: check"])


class EdgeCases(unittest.TestCase):
    def test_json_that_is_not_an_object_is_rejected(self):
        self.assertEqual(reply_check.validate("[]", CLEAN), ["reply is not a JSON object"])

    def test_a_boolean_is_not_a_count(self):
        reply = json.loads((HERE / "fixtures/clean/good-ok.txt").read_text())
        reply["check"]["count"] = True
        self.assertTrue(reply_check.validate(json.dumps(reply), CLEAN))

    def test_a_missing_month_needs_a_stop_that_names_it(self):
        figures = CASES["june-missing"]["figures"]
        good = '{"status": "stop", "months_counted": 11, "reason": "Jun is missing."}'
        vague = '{"status": "stop", "months_counted": 11, "reason": "A month is missing."}'
        self.assertEqual(reply_check.validate(good, figures), [])
        self.assertEqual(reply_check.validate(vague, figures), ["reason does not name the problem month Jun"])


class Regression(unittest.TestCase):
    def run_model(self, model):
        with redirect_stdout(io.StringIO()):
            return reply_check.run_regression(model)

    def test_the_pinned_model_passes(self):
        self.assertEqual(self.run_model("model-v1"), 0)

    def test_the_changed_model_fails_the_same_case_set(self):
        self.assertEqual(self.run_model("model-v2"), 1)

    def test_a_model_with_no_stored_replies_fails(self):
        self.assertEqual(self.run_model("model-unknown"), 1)


if __name__ == "__main__":
    unittest.main()
