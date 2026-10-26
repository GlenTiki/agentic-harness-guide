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

    def test_no_fire_case_fires_nothing(self):
        self.assertIsNone(fire_check.first_row(TABLE, CASES[-1]["cues"]))

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
        self.assertIn("FAIL no order on file: fired no row, wanted R5", text)

    def test_a_row_that_never_fires_is_reported_as_a_failure_when_a_case_expects_it(self):
        broken = copy.deepcopy(TABLE)
        broken["rows"][3]["when"] = {"total_vs_order": "over_larg"}
        code, _ = run(broken, CASES)
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
