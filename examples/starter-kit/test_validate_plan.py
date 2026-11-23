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
        self.assertEqual(merged[".github/hooks/starter-kit.json"][0]["version"], 1)

    def test_copilot_cli_alone_gets_its_hook_and_skill_and_no_claude_registration(self):
        _, resolution = self.resolve("valid-copilot-cli")
        self.assertEqual([write["path"] for write in resolution["writes"]], [
            "AGENTS.md", ".claude/starter-kit.json", ".github/hooks/block_destructive_git.py",
            ".github/hooks/starter-kit.json", ".github/skills/prompt-refiner/SKILL.md"])

    def test_copilot_registration_uses_the_pascal_case_event_so_the_script_reads_claude_shaped_input(self):
        fragment = json.loads((HERE / "files/copilot/hook-block-destructive-git.json").read_text())
        self.assertEqual(fragment["version"], 1)
        [entry] = fragment["hooks"]["PreToolUse"]
        self.assertEqual((entry["type"], entry["matcher"], entry["cwd"]), ("command", "Bash", "."))
        self.assertIn(".github/hooks/block_destructive_git.py", entry["bash"])

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
            self.assertIn("claude-code", option["hosts"])
            self.assertLessEqual(set(option["hosts"]), {"claude-code", "copilot-cli"})
            if "copilot-cli" in option["hosts"]:
                self.assertTrue((HERE / "files/copilot" / f"hook-{option['value']}.json").is_file())
                self.assertIn(f"hook-{option['value']}-copilot", item_ids)

    def test_every_blocking_hook_is_refused_exactly_when_no_chosen_host_runs_it(self):
        hooks = next(question for question in MANIFEST["questions"] if question["id"] == "hooks")
        hosts = [option["value"] for option in next(q for q in MANIFEST["questions"] if q["id"] == "hosts")["options"]]
        choices = [[host for bit, host in enumerate(hosts) if mask >> bit & 1] for mask in range(1, 2 ** len(hosts))]
        for option in hooks["options"]:
            if not option["blocking"]:
                continue
            for chosen in choices:
                with self.subTest(hook=option["value"], hosts=chosen):
                    errors, _, _ = validate_plan.validate(
                        {"answers": {"hosts": chosen, "hooks": [option["value"]], "memory": True, "test_command": "pytest"}},
                        MANIFEST)
                    host_errors = [rule_id for rule_id, _ in errors if rule_id.startswith(f"{option['value']}-needs-")
                                   and rule_id.endswith(("-host", "-claude-code"))]
                    self.assertEqual(bool(host_errors), not set(chosen) & set(option["hosts"]))

    def test_hook_scripts_use_only_the_standard_library_and_no_network(self):
        allowed = {"json", "os", "pathlib", "re", "shlex", "subprocess", "sys", "tempfile"}
        for script in (HERE / "hooks").glob("[!t]*.py"):
            imports = set(re.findall(r"^\s*(?:import|from) (\w+)", script.read_text(), re.M))
            self.assertLessEqual(imports, allowed, script.name)

    def test_command_pattern_refuses_each_shell_character(self):
        question = next(question for question in MANIFEST["questions"] if question["id"] == "test_command")
        refused = [";", "&", "|", "`", "$", "<", ">", '"', "'", "\\", "(", ")", "*", "?", "[", "]", "{", "}", "\x7f"]
        for char in refused + [chr(code) for code in range(0x20)]:
            with self.subTest(char=repr(char)):
                self.assertIsNone(re.fullmatch(question["pattern"], f"pytest {char} x"))
        for blank in [" ", "   "]:
            self.assertIsNone(re.fullmatch(question["pattern"], blank))
        self.assertIsNotNone(re.fullmatch(question["pattern"], "uv run pytest -q tests/unit"))
        self.assertIsNotNone(re.fullmatch(question["pattern"], "npm run test:unit -- --ci=true"))

    def test_lint_command_uses_the_same_pattern(self):
        patterns = {question["id"]: question.get("pattern") for question in MANIFEST["questions"]}
        self.assertEqual(patterns["lint_command"], patterns["test_command"])

    def test_pattern_message_names_every_refused_kind(self):
        _, message = validate_plan.check_string(next(q for q in MANIFEST["questions"] if q["id"] == "test_command"),
                                                "a'b")[0]
        for word in ["quote", "bracket", "wildcard", "control"]:
            self.assertIn(word, message)


class JsonRender(unittest.TestCase):
    def test_answer_inside_a_json_string_is_escaped(self):
        source = (HERE / "files/claude/permissions-test.json").read_text()
        for value in ['a"b', "a\\b", "a\tb", "a\x00b"]:
            with self.subTest(value=repr(value)):
                text = validate_plan.render(source, {"test_command": value}, True)
                self.assertEqual(json.loads(text)["permissions"]["allow"], [f"Bash({value})"])


if __name__ == "__main__":
    unittest.main()
