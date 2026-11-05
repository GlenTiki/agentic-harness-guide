import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent


def check(root):
    result = subprocess.run([sys.executable, str(HERE / "check_citations.py"), str(root)], capture_output=True, text=True, check=False)
    return result.returncode, result.stdout.splitlines()


class CheckCitations(unittest.TestCase):
    def test_citations_resolve_before_the_move(self):
        self.assertEqual(check(HERE / "fixtures/before"), (0, ["0 unresolved, 1 snapshot exempt"]))

    def test_moved_function_fails_both_citations(self):
        code, lines = check(HERE / "fixtures/after")
        self.assertEqual(code, 1)
        self.assertEqual(lines[0], "docs/spec.md:3: src/pricing.py:3 does not hold vat_inclusive")
        self.assertEqual(lines[1], "docs/spec.md:5: src/pricing.py:7 does not hold round_to_cent")

    def test_missing_file_and_line_past_end_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "a.py").write_text("one\n")
            (root / "doc.md").write_text("See `a.py:2` and `b.py:1`.\n")
            code, lines = check(root)
        self.assertEqual(code, 1)
        self.assertEqual(lines[:2], ["doc.md:1: a.py:2 is outside the 1-line file", "doc.md:1: b.py does not exist"])

    def test_snapshot_marker_must_be_the_first_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            (root / "doc.md").write_text("intro\n<!-- snapshot: 2026-01-01 -->\nSee `gone.py:1`.\n")
            code, _ = check(root)
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
