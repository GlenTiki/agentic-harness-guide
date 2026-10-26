import copy
import io
import json
import unittest
from pathlib import Path

import fire_check

HERE = Path(__file__).resolve().parent
TABLE = json.loads((HERE / "table.json").read_text())
CASES = json.loads((HERE / "cases.json").read_text())


def run(table, cases):
    out = io.StringIO()
    return fire_check.check(table, cases, out), out.getvalue()


class FireCheck(unittest.TestCase):
    def test_shipped_table_passes_every_case(self):
        code, text = run(TABLE, CASES)
        self.assertEqual(code, 0, text)

    def test_a_missing_cue_never_selects_a_payment_row(self):
        payment_rows = {row["id"] for row in TABLE["rows"] if row["choice"].startswith("pay")}
        for cue in TABLE["cues"]:
            cues = {name: value for name, value in CASES[0]["cues"].items() if name != cue}
            fired = fire_check.first_row(TABLE, cues)
            self.assertNotIn(fired, payment_rows, f"missing {cue}")

    def test_a_missing_cue_asks_and_does_not_pay(self):
        cues = {"total_vs_order": "matches"}
        self.assertEqual(fire_check.first_row(TABLE, cues), "R8")
        self.assertEqual(next(r["choice"] for r in TABLE["rows"] if r["id"] == "R8"), "ask, do not pay")

    def test_an_unrecognised_cue_value_asks(self):
        cues = {**CASES[0]["cues"], "supplier_known": "unsure"}
        self.assertEqual(fire_check.first_row(TABLE, cues), "R8")

    def test_a_table_without_a_fallback_fires_no_row(self):
        bare = {"rows": [row for row in TABLE["rows"] if not row.get("fallback")]}
        self.assertIsNone(fire_check.first_row(bare, {}))

    def test_swapping_row_order_is_caught(self):
        swapped = copy.deepcopy(TABLE)
        swapped["rows"][0], swapped["rows"][1] = swapped["rows"][1], swapped["rows"][0]
        code, text = run(swapped, CASES)
        self.assertEqual(code, 1)
        self.assertIn("FAIL new bank details and a repeat number: fired R2, wanted R1", text)

    def test_deleting_a_row_is_caught(self):
        trimmed = copy.deepcopy(TABLE)
        trimmed["rows"] = [row for row in trimmed["rows"] if row["id"] != "R5"]
        code, text = run(trimmed, CASES)
        self.assertEqual(code, 1)
        self.assertIn("FAIL no order on file: fired R8, wanted R5", text)

    def test_a_row_that_never_fires_is_reported_as_a_failure_when_a_case_expects_it(self):
        broken = copy.deepcopy(TABLE)
        broken["rows"][3]["when"] = {"total_vs_order": "over_larg"}
        code, _ = run(broken, CASES)
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
