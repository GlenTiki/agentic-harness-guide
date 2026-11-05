import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import harness  # noqa: E402
import sweep  # noqa: E402


class RedactionTests(unittest.TestCase):
    def test_email_is_replaced(self):
        at = "@"
        out = harness.redact('{"a": "mail me at someone.name+x' + at + 'example.co.uk now"}')
        self.assertEqual(out, '{"a": "mail me at [account email] now"}')

    def test_text_without_email_is_unchanged(self):
        text = "Total: 2,120 at 5 o'clock, @mention and a@b are not emails"
        self.assertEqual(harness.redact(text), text)


class SweepTests(unittest.TestCase):
    def test_planted_email_and_name_are_found(self):
        root = Path(tempfile.mkdtemp())
        (root / "ok.txt").write_text("nothing here\n")
        (root / "bad1.txt").write_text("x\nwrite to a.b" + "@" + "example.com\n")
        (root / "bad2.txt").write_text("works for Acmecorp\n")
        hits = sweep.sweep(root, ("acmecorp", "initech"))
        self.assertEqual(sorted(Path(h).name.split(":")[0] for h in hits), ["bad1.txt", "bad2.txt"])

    def test_banned_word_must_match_a_whole_word(self):
        root = Path(tempfile.mkdtemp())
        (root / "ok.txt").write_text("acmecorporation is not the word\n")
        self.assertEqual(sweep.sweep(root, ("acmecorp",)), [])

    def test_banned_words_are_read_from_the_environment(self):
        os.environ["HARNESS_BANNED_WORDS"] = " acmecorp, initech ,"
        try:
            self.assertEqual(harness.banned_words(), ("acmecorp", "initech"))
        finally:
            del os.environ["HARNESS_BANNED_WORDS"]

    def test_clean_folder_passes(self):
        root = Path(tempfile.mkdtemp())
        (root / "ok.txt").write_text("nothing here\n")
        self.assertEqual(sweep.sweep(root), [])

    def test_this_folder_is_clean(self):
        words = tuple(w for w in os.environ.get("HARNESS_BANNED_WORDS", "").split(",") if w.strip())
        self.assertEqual(sweep.sweep(HERE, words), [])


if __name__ == "__main__":
    unittest.main()
