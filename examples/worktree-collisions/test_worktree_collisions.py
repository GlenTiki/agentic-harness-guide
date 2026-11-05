import os
import pathlib
import subprocess
import sys
import tempfile
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


class GitEnvironmentRoles(unittest.TestCase):
    def test_each_variable_selects_a_different_thing(self):
        result = subprocess.run(["sh", str(HERE / "git_env_roles.sh")], capture_output=True, text=True, timeout=60, check=True,
                                env={**os.environ, "GIT_DIR": "/nonexistent", "GIT_WORK_TREE": "/nonexistent", "GIT_INDEX_FILE": "/nonexistent"})
        self.assertEqual(
            result.stdout.splitlines(),
            ["-- GIT_DIR names outer's metadata, git -C inner --", "last commit: commit in outer",
             "-- GIT_WORK_TREE names inner's folder, git -C outer --", "git dir: .git", "status:  M f",
             "-- GIT_INDEX_FILE names an empty index, git -C outer --", "D  f", "?? f"],
        )


class PortAndBase(unittest.TestCase):
    def test_port_collision_and_base_check(self):
        lines = run("port_and_base.py").splitlines()
        self.assertEqual(lines[1:3], ["process in folder-a bound", "process in folder-b failed: EADDRINUSE"])
        self.assertEqual(lines[4:7], ["process in folder-a bound", "process in folder-b bound", "ports differ: True"])
        self.assertEqual(lines[8], "branch descends from current main, exit code: 1")
        self.assertEqual(lines[9], "after rebasing the branch onto main, exit code: 0")
        self.assertEqual(lines[11:], ["inner exists in the main checkout: True", "inner exists in the worktree: False"])

    def test_wait_is_bounded_and_children_are_cleaned_up(self):
        sys.path.insert(0, str(HERE))
        import port_and_base

        silent = subprocess.Popen([sys.executable, "-I", "-c", "import time; time.sleep(60)"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        try:
            with self.assertRaises(TimeoutError):
                port_and_base.read_line(silent, seconds=0.5)
        finally:
            port_and_base.stop([silent])
        self.assertIsNotNone(silent.poll())

    def test_second_process_fails_on_the_port_the_first_really_holds(self):
        sys.path.insert(0, str(HERE))
        import port_and_base

        with tempfile.TemporaryDirectory() as tmp:
            folder = pathlib.Path(tmp)
            first = port_and_base.start(folder, 0, "first")
            second = None
            try:
                port = port_and_base.bound_port(port_and_base.read_line(first))
                second = port_and_base.start(folder, port, "second")
                self.assertEqual(port_and_base.read_line(second), "second failed: EADDRINUSE")
            finally:
                port_and_base.stop([p for p in (first, second) if p])


if __name__ == "__main__":
    unittest.main()
