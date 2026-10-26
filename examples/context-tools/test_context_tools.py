import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import compaction_audit
import compaction_point

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"


class CompactionAudit(unittest.TestCase):
    def test_the_fixture_summary_loses_two_constraints(self):
        ledger = json.loads((FIXTURES / "ledger.json").read_text())
        kept, lost = compaction_audit.lost_constraints(ledger, (FIXTURES / "summary-after-compaction.txt").read_text())
        self.assertEqual([c["id"] for c in kept], ["C3"])
        self.assertEqual([c["id"] for c in lost], ["C1", "C2"])

    def test_a_summary_that_restates_every_constraint_loses_none(self):
        ledger = json.loads((FIXTURES / "ledger.json").read_text())
        summary = "Keep the signature of sync(). Cap at 5 retries, limit resets in 60 s. Write the test first."
        self.assertEqual(compaction_audit.lost_constraints(ledger, summary)[1], [])

    def test_the_command_exits_1_when_a_constraint_is_lost(self):
        with redirect_stdout(io.StringIO()):
            code = compaction_audit.main([str(FIXTURES / "ledger.json"), str(FIXTURES / "summary-after-compaction.txt")])
        self.assertEqual(code, 1)


class CompactionPoint(unittest.TestCase):
    def write_log(self, rows):
        handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="")
        self.addCleanup(Path(handle.name).unlink)
        writer = csv.writer(handle)
        writer.writerow(["session", "boundary", "tokens_used", "window", "constraint_dropped"])
        writer.writerows(rows)
        handle.close()
        return handle.name

    def test_the_fixture_log_gives_the_last_clean_boundary_below_the_lowest_drop(self):
        lowest_drop, clean = compaction_point.compaction_point(compaction_point.read_rows(FIXTURES / "boundaries.csv"))
        self.assertAlmostEqual(lowest_drop, 0.69)
        self.assertAlmostEqual(clean[-1], 0.60 + 0.005, places=2)

    def test_a_log_with_no_drop_cannot_place_a_point(self):
        path = self.write_log([["s1", "spec", 1000, 10000, 0]])
        with redirect_stdout(io.StringIO()):
            self.assertEqual(compaction_point.main([path]), 1)

    def test_a_drop_at_the_first_boundary_leaves_no_clean_boundary(self):
        path = self.write_log([["s1", "spec", 1000, 10000, 1]])
        with redirect_stdout(io.StringIO()):
            self.assertEqual(compaction_point.main([path]), 1)


if __name__ == "__main__":
    unittest.main()
