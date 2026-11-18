#!/usr/bin/env python3
"""Run validate_plan.py against every fixture and check the manifest is complete and consistent."""

import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import validate_plan  # noqa: E402

MANIFEST = json.loads((HERE / "kit-manifest.json").read_text())
FIXTURES = {path.stem: json.loads(path.read_text()) for path in sorted((HERE / "fixtures").glob("*.json"))}
VOCABULARY = set(MANIFEST["kit"]["condition_vocabulary"])


def conditions():
    for rule in MANIFEST["rules"]:
        yield from rule["when"]
        then = rule["then"]
        if "forbid" in then:
            yield then["forbid"]
        elif "require" not in then:
            yield then
    for item in MANIFEST["items"]:
        yield from item["when"]


class Fixtures(unittest.TestCase):
    def test_each_fixture_gives_its_expected_outcome(self):
        for name, fixture in FIXTURES.items():
            with self.subTest(fixture=name):
                errors, warnings, _ = validate_plan.validate(fixture["plan"], MANIFEST)
                expect = fixture["expect"]
                self.assertEqual(not errors, expect["valid"])
                self.assertEqual(sorted(rule_id for rule_id, _ in errors), sorted(expect["errors"]))
                self.assertEqual(sorted(rule_id for rule_id, _ in warnings), sorted(expect["warnings"]))

    def test_every_rule_has_a_fixture_that_fires_it_alone(self):
        for rule in MANIFEST["rules"]:
            key = "errors" if rule["level"] == "error" else "warnings"
            hits = [name for name, fixture in FIXTURES.items() if fixture["expect"][key] == [rule["id"]]]
            self.assertTrue(hits, f"no fixture fires only {rule['id']}")

    def test_cli_exit_codes_and_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            def cli(name):
                plan = pathlib.Path(tmp) / name
                if name in FIXTURES:
                    plan.write_text(json.dumps(FIXTURES[name]["plan"]))
                return subprocess.run([sys.executable, "-I", str(HERE / "validate_plan.py"), str(plan)],
                                      capture_output=True, text=True, timeout=30)

            valid = cli("valid-minimal")
            self.assertEqual(valid.returncode, 0)
            self.assertIn("write AGENTS.md (create) from files/AGENTS.md", valid.stdout)
            invalid = cli("invalid-recall-reinject-needs-memory")
            self.assertEqual(invalid.returncode, 1)
            self.assertIn("recall-reinject-needs-memory: The recall-reinject hook reads memory/INDEX.md.", invalid.stdout)
            warned = cli("warning-hooks-without-claude-code")
            self.assertEqual(warned.returncode, 0)
            self.assertIn("warning: hooks-without-claude-code: ", warned.stdout)
            self.assertEqual(cli("no-such-plan").returncode, 2)


class Resolution(unittest.TestCase):
    def resolve(self, name):
        _, _, answers = validate_plan.validate(FIXTURES[name]["plan"], MANIFEST)
        return answers, validate_plan.resolve(answers, MANIFEST)

    def test_minimal_plan_writes_only_the_instruction_files_and_permissions(self):
        _, resolution = self.resolve("valid-minimal")
        self.assertEqual(resolution["items"], ["agents-md", "claude-md", "permissions"])
        self.assertEqual(resolution["run"], [])

    def test_codex_alone_gets_no_claude_files(self):
        _, resolution = self.resolve("valid-codex-node")
        self.assertEqual([write["path"] for write in resolution["writes"]], ["AGENTS.md", "orca.yaml"])
        self.assertEqual([step["command"] for step in resolution["run"]], ["brew install --cask stablyai/orca/orca"])

    def test_full_plan_renders_every_json_file_to_valid_json(self):
        answers, resolution = self.resolve("valid-full")
        self.assertEqual(resolution["skills_to_find"], ["independent-review"])
        merged = {}
        for write in resolution["writes"]:
            text = validate_plan.render((HERE / write["source"]).read_text(), answers, write["source"].endswith(".json"))
            self.assertNotIn("{{", text, write["source"])
            if write["source"].endswith(".json"):
                merged.setdefault(write["path"], []).append(json.loads(text))
        settings = merged[".claude/settings.json"]
        events = {event for fragment in settings for event in fragment.get("hooks", {})}
        self.assertEqual(events, {"PreToolUse", "PostToolUse", "Stop", "UserPromptSubmit"})
        self.assertEqual(merged[".claude/starter-kit.json"][0]["test_command"], "uv run pytest")

    def test_unset_command_renders_as_null_in_json(self):
        answers = validate_plan.with_defaults(MANIFEST, {"hosts": ["claude-code"]})
        text = validate_plan.render((HERE / "files/claude/starter-kit.json").read_text(), answers, True)
        self.assertIsNone(json.loads(text)["lint_command"])


class Manifest(unittest.TestCase):
    def test_conditions_use_only_the_fixed_vocabulary(self):
        for condition in conditions():
            self.assertEqual(set(condition) - {"answer"}, set(condition) & VOCABULARY, condition)
            self.assertEqual(len(set(condition) & VOCABULARY), 1, condition)

    def test_every_source_file_exists(self):
        for item in MANIFEST["items"]:
            for write in item["writes"]:
                self.assertTrue((HERE / write["source"]).is_file(), write["source"])

    def test_every_hook_option_has_a_script_a_registration_and_an_item(self):
        hooks = next(question for question in MANIFEST["questions"] if question["id"] == "hooks")
        item_ids = {item["id"] for item in MANIFEST["items"]}
        for option in hooks["options"]:
            self.assertTrue((HERE / "hooks" / option["file"]).is_file())
            self.assertTrue((HERE / "files/claude" / f"hook-{option['value']}.json").is_file())
            self.assertIn(f"hook-{option['value']}", item_ids)
            self.assertEqual(option["hosts"], ["claude-code"])

    def test_every_blocking_hook_has_a_claude_code_rule(self):
        hooks = next(question for question in MANIFEST["questions"] if question["id"] == "hooks")
        rule_ids = {rule["id"] for rule in MANIFEST["rules"]}
        for option in hooks["options"]:
            if option["blocking"]:
                self.assertIn(f"{option['value']}-needs-claude-code", rule_ids)

    def test_hook_scripts_use_only_the_standard_library_and_no_network(self):
        allowed = {"json", "os", "pathlib", "re", "shlex", "subprocess", "sys", "tempfile"}
        for script in (HERE / "hooks").glob("[!t]*.py"):
            imports = set(re.findall(r"^\s*(?:import|from) (\w+)", script.read_text(), re.M))
            self.assertLessEqual(imports, allowed, script.name)

    def test_command_pattern_refuses_each_shell_character(self):
        question = next(question for question in MANIFEST["questions"] if question["id"] == "test_command")
        for char in [";", "&", "|", "`", "$", "<", ">", '"', "\\", "\n", "\r"]:
            with self.subTest(char=repr(char)):
                self.assertIsNone(re.fullmatch(question["pattern"], f"pytest {char} x"))
        self.assertIsNotNone(re.fullmatch(question["pattern"], "uv run pytest -q tests/unit"))


if __name__ == "__main__":
    unittest.main()
