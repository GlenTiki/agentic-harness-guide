#!/usr/bin/env python3
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import merge_settings  # noqa: E402
from merge_settings import merge  # noqa: E402


class Merge(unittest.TestCase):
    def test_objects_merge_by_key(self):
        self.assertEqual(merge({"a": 1}, {"b": 2}), ({"a": 1, "b": 2}, []))

    def test_nested_objects_merge(self):
        target = {"permissions": {"deny": ["Read(./.env)"]}}
        fragment = {"permissions": {"ask": ["Bash(git push *)"]}}
        self.assertEqual(merge(target, fragment)[0]["permissions"], {"deny": ["Read(./.env)"], "ask": ["Bash(git push *)"]})

    def test_lists_join_without_duplicates(self):
        self.assertEqual(merge({"x": [1, 2]}, {"x": [2, 3]}), ({"x": [1, 2, 3]}, []))

    def test_equal_hook_entries_are_not_added_twice(self):
        fragment = json.loads((HERE / "files/claude/hook-tests-before-stop.json").read_text())
        once, _ = merge({}, fragment)
        self.assertEqual(merge(once, fragment), (once, []))

    def test_two_hook_fragments_share_an_event_list(self):
        merged = {}
        for name in ["hook-block-destructive-git.json", "hook-pr-size-nudge.json"]:
            merged, conflicts = merge(merged, json.loads((HERE / "files/claude" / name).read_text()))
            self.assertEqual(conflicts, [])
        self.assertEqual(len(merged["hooks"]["PreToolUse"]), 2)

    def test_equal_scalars_are_not_a_conflict(self):
        self.assertEqual(merge({"model": "x"}, {"model": "x"}), ({"model": "x"}, []))

    def test_different_scalars_are_reported_and_the_target_is_kept(self):
        self.assertEqual(merge({"a": {"b": 1}}, {"a": {"b": 2}}), ({"a": {"b": 1}}, ["$.a.b"]))

    def test_different_types_are_a_conflict(self):
        self.assertEqual(merge({"a": [1]}, {"a": {"b": 1}})[1], ["$.a"])
        self.assertEqual(merge({"a": 1}, {"a": True})[1], ["$.a"])
        self.assertEqual(merge({"a": None}, {"a": "x"})[1], ["$.a"])

    def test_inputs_are_not_changed(self):
        target, fragment = {"x": [1], "y": {"z": 1}}, {"x": [2], "y": {"w": 2}}
        merge(target, fragment)
        self.assertEqual((target, fragment), ({"x": [1], "y": {"z": 1}}, {"x": [2], "y": {"w": 2}}))


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-I", str(HERE / "merge_settings.py"), *args],
                              capture_output=True, text=True, timeout=30)

    def test_missing_target_is_an_empty_object_and_nothing_is_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp) / "settings.json"
            result = self.run_cli(str(target), str(HERE / "files/claude/permissions.json"))
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["permissions"]["ask"], ["Bash(git push *)"])
            self.assertFalse(target.exists())

    def test_conflict_exits_1_with_the_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            target, fragment = pathlib.Path(tmp) / "t.json", pathlib.Path(tmp) / "f.json"
            target.write_text('{"env": {"A": "1"}}')
            fragment.write_text('{"env": {"A": "2"}}')
            result = self.run_cli(str(target), str(fragment))
            self.assertEqual((result.returncode, result.stdout), (1, ""))
            self.assertIn("conflict: $.env.A", result.stderr)

    def test_unreadable_input_exits_2(self):
        self.assertEqual(self.run_cli("missing-target.json", "missing-fragment.json").returncode, 2)
        self.assertEqual(merge_settings.main(["only-one"]), 2)


if __name__ == "__main__":
    unittest.main()
