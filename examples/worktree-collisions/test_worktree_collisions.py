import pathlib
import subprocess
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent


def run(script):
    result = subprocess.run([sys.executable, str(HERE / script)], capture_output=True, text=True, timeout=60, check=True)
    return result.stdout


class SharedCheckout(unittest.TestCase):
    def test_last_writer_wins_in_one_checkout(self):
        out = run("shared_checkout.py").split("-- two worktrees")[0]
        self.assertIn("status: writer B", out)
        self.assertIn("owner: nobody", out)
        self.assertNotIn("writer A", out)

    def test_separate_worktrees_keep_both_edits_on_different_lines(self):
        out = run("shared_checkout.py").split("-- two worktrees, writer B edits 'status' --")[1].split("--")[0]
        self.assertIn("exit code: 0", out)
        self.assertIn("owner: writer A", out)
        self.assertIn("status: writer B", out)

    def test_same_line_conflict_is_loud(self):
        out = run("shared_checkout.py").split("writer B edits 'owner' --")[1]
        self.assertIn("exit code: 1", out)
        self.assertIn("<<<<<<< HEAD", out)


class PortAndBase(unittest.TestCase):
    def test_port_collision_and_base_check(self):
        lines = run("port_and_base.py").splitlines()
        self.assertEqual(lines[1:3], ["process in folder-a bound", "process in folder-b failed: EADDRINUSE"])
        self.assertEqual(lines[4:6], ["process in folder-a bound", "process in folder-b bound"])
        self.assertEqual(lines[7], "branch descends from current main, exit code: 1")
        self.assertEqual(lines[8], "after rebasing the branch onto main, exit code: 0")
        self.assertEqual(lines[10:], ["inner exists in the main checkout: True", "inner exists in the worktree: False"])


if __name__ == "__main__":
    unittest.main()
