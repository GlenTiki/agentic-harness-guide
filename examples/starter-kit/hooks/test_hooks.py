#!/usr/bin/env python3
"""Feed each starter-kit hook a hook event on stdin and check the exit code and the output."""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
PASS = f"{sys.executable} -c pass"
FAIL = f"{sys.executable} -c exit(3)"


def run_hook(script, event, env=None):
    raw = event if isinstance(event, str) else json.dumps(event)
    environ = {key: value for key, value in os.environ.items() if not key.startswith(("STARTER_KIT_", "CLAUDE_"))}
    result = subprocess.run(
        [sys.executable, "-I", str(HERE / script)],
        input=raw,
        env={**environ, **(env or {})},
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result


def context_of(result):
    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"] if result.stdout.strip() else None


class HookCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.config = self.root / "starter-kit.json"
        self.state = self.root / "state"
        self.write_config()

    def tearDown(self):
        self.tmp.cleanup()

    def write_config(self, **values):
        base = {"test_command": PASS, "lint_command": PASS, "verification_gap_files": 2, "delegation_limit": 3,
                "recall_every": 2, "recall_file": "INDEX.md", "pr_max_lines": 5, "pr_max_files": 2}
        self.config.write_text(json.dumps({**base, **values}))

    def env(self, **extra):
        return {"STARTER_KIT_CONFIG": str(self.config), "STARTER_KIT_STATE_DIR": str(self.state),
                "CLAUDE_PROJECT_DIR": str(self.root), **extra}


class Thresholds(HookCase):
    CASES = [("verification_gap.py", "verification_gap_files", {"tool_name": "Write", "tool_input": {"file_path": "a"}}),
             ("delegation_counter.py", "delegation_limit", {"tool_name": "Read"}),
             ("recall_reinject.py", "recall_every", {"prompt": "next"})]

    def test_a_threshold_below_1_is_reported_and_never_blocks(self):
        for script, key, event in self.CASES:
            for value in [0, -1, "3"]:
                with self.subTest(script=script, value=value):
                    self.write_config(**{key: value})
                    result = run_hook(script, {"session_id": "s1", **event}, self.env())
                    self.assertEqual((result.returncode, result.stdout), (0, ""))
                    self.assertIn(f"{key} must be a whole number of 1 or more", result.stderr)


class BlockDestructiveGit(HookCase):
    BLOCK = ["git push -f", "git push --force origin main", "git push --force-with-lease", "git push origin +main",
             "git -C . push -fu origin main", "git reset --hard", "git reset --hard HEAD~1", "git clean -fd",
             "git clean -fdx", "git clean --force", "git status && git push -f", "git status; git reset --hard",
             "bash -c 'git push --force'", "echo $(git push --force)", "(git reset --hard)", "env git clean -f",
             "GIT_SSH_COMMAND=x git push -f", "/usr/bin/git push -f", 'bash -lc "git reset --hard"',
             "zsh -xc 'git clean -fd'", "sudo git push --force", "sudo -u build git reset --hard",
             "find . -name x | xargs git clean -f", 'eval "git reset --hard"', "nice -n 10 git push -f",
             "timeout 5 git push origin +main"]
    ALLOW = ["git status", "git push origin main", "git push -u origin feature", "git reset --soft HEAD~1",
             "git clean -n", "git commit -m 'push -f notes'", "git log --grep reset", "sudo git status",
             'eval "git status"', "grep -r git README.md"]
    KNOWN_LIMITS = ["F=-f; git push $F", "g=git; $g push -f", "git config alias.wipe 'reset --hard'; git wipe",
                    "./scripts/reset-all.sh"]

    def call(self, command):
        return run_hook("block_destructive_git.py", {"tool_name": "Bash", "tool_input": {"command": command}})

    def test_blocks_destructive_commands(self):
        for command in self.BLOCK:
            with self.subTest(command=command):
                result = self.call(command)
                self.assertEqual(result.returncode, 2)
                self.assertIn("Blocked", result.stderr)

    def test_allows_safe_commands(self):
        for command in self.ALLOW:
            with self.subTest(command=command):
                self.assertEqual(self.call(command).returncode, 0)

    def test_known_limits_still_pass_as_the_readme_says(self):
        for command in self.KNOWN_LIMITS:
            with self.subTest(command=command):
                self.assertEqual(self.call(command).returncode, 0)

    def test_blocks_input_it_cannot_read(self):
        for raw in ["", "not json", "null", "{}", '{"tool_input":{"command":["git"]}}', '{"tool_input":{"command":"\'"}}']:
            with self.subTest(raw=raw):
                self.assertEqual(run_hook("block_destructive_git.py", raw).returncode, 2)


class BlockDestructiveGitOnCopilotCli(HookCase):
    """Constructed inputs in the shapes of the GitHub Copilot hooks reference, fetched 2026-11-23."""

    def event(self, command):
        return {"hook_event_name": "PreToolUse", "session_id": "s1", "timestamp": "2026-11-23T10:00:00Z",
                "cwd": "/repo", "tool_name": "Bash", "tool_input": {"command": command}}

    def test_pascal_case_input_blocks_and_allows_as_on_claude_code(self):
        self.assertEqual(run_hook("block_destructive_git.py", self.event("git push --force")).returncode, 2)
        self.assertEqual(run_hook("block_destructive_git.py", self.event("git status")).returncode, 0)

    def test_camel_case_input_is_unreadable_so_the_registration_must_use_pascal_case(self):
        event = {"sessionId": "s1", "timestamp": 1704614400000, "cwd": "/repo", "toolName": "bash",
                 "toolArgs": json.dumps({"command": "git status"})}
        self.assertEqual(run_hook("block_destructive_git.py", event).returncode, 2)

    def test_arguments_left_as_text_are_unreadable_and_block(self):
        event = {**self.event("x"), "tool_input": "not json"}
        self.assertEqual(run_hook("block_destructive_git.py", event).returncode, 2)


class TestsBeforeStop(HookCase):
    def stop(self, active=False, **env):
        return run_hook("tests_before_stop.py", {"session_id": "s1", "stop_hook_active": active}, self.env(**env))

    def test_passing_tests_let_the_stop_through(self):
        self.assertEqual(self.stop().returncode, 0)

    def test_failing_tests_block_with_the_reason(self):
        self.write_config(test_command=FAIL)
        result = self.stop()
        self.assertEqual(result.returncode, 2)
        self.assertIn("The tests fail (exit 3)", result.stderr)

    def test_stop_hook_active_lets_the_stop_through(self):
        self.write_config(test_command=FAIL)
        self.assertEqual(self.stop(active=True).returncode, 0)

    def test_env_command_overrides_the_config(self):
        self.assertEqual(self.stop(STARTER_KIT_TEST_COMMAND=FAIL).returncode, 2)

    def test_missing_command_blocks(self):
        self.write_config(test_command=None)
        result = self.stop()
        self.assertEqual(result.returncode, 2)
        self.assertIn("no test command", result.stderr)

    def test_blank_command_blocks_with_a_clear_reason(self):
        self.write_config(test_command="   ")
        result = self.stop()
        self.assertEqual(result.returncode, 2)
        self.assertIn("no test command", result.stderr)

    def test_unbalanced_quote_blocks_with_a_clear_reason(self):
        self.write_config(test_command="npm test 'oops")
        result = self.stop()
        self.assertEqual(result.returncode, 2)
        self.assertIn("could not check this stop", result.stderr)

    def test_command_that_cannot_start_blocks(self):
        self.write_config(test_command="no-such-program-starter-kit")
        result = self.stop()
        self.assertEqual(result.returncode, 2)
        self.assertIn("could not start no-such-program-starter-kit", result.stderr)

    def test_command_runs_without_a_shell(self):
        marker = self.root / "marker"
        self.write_config(test_command=f"{sys.executable} -c pass ; touch {marker}")
        self.stop()
        self.assertFalse(marker.exists())


class LintAfterWrite(HookCase):
    def write(self):
        event = {"session_id": "s1", "tool_name": "Write", "tool_input": {"file_path": str(self.root / "a.py")}}
        return run_hook("lint_after_write.py", event, self.env())

    def test_clean_lint_adds_nothing(self):
        result = self.write()
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_lint_errors_go_back_as_context(self):
        self.write_config(lint_command=f"{sys.executable} -c \"print('E501 line too long');exit(1)\"")
        result = self.write()
        self.assertEqual(result.returncode, 0)
        self.assertIn("E501 line too long", context_of(result))

    def test_bad_input_never_blocks(self):
        self.assertEqual(run_hook("lint_after_write.py", "not json", self.env()).returncode, 0)

    def test_blank_lint_command_adds_nothing(self):
        self.write_config(lint_command="   ")
        result = self.write()
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))


class VerificationGap(HookCase):
    def call(self, tool_name, **tool_input):
        event = {"session_id": "s1", "tool_name": tool_name, "tool_input": tool_input}
        return run_hook("verification_gap.py", event, self.env())

    def test_nudges_at_the_threshold_and_resets_after_tests(self):
        self.assertIsNone(context_of(self.call("Write", file_path="a.py")))
        self.assertIsNone(context_of(self.call("Edit", file_path="a.py")))
        self.assertIn("2 files since the last test run", context_of(self.call("Edit", file_path="b.py")))
        self.assertIsNone(context_of(self.call("Bash", command=f"{PASS}  -q")))
        self.assertIsNone(context_of(self.call("Write", file_path="c.py")))

    def test_bad_input_never_blocks(self):
        self.assertEqual(run_hook("verification_gap.py", {"session_id": "../x"}, self.env()).returncode, 0)


class DelegationCounter(HookCase):
    def call(self, tool_name):
        return run_hook("delegation_counter.py", {"session_id": "s1", "tool_name": tool_name}, self.env())

    def test_nudges_after_the_limit_and_resets_on_a_sub_agent(self):
        self.assertIsNone(context_of(self.call("Read")))
        self.assertIsNone(context_of(self.call("Agent")))
        self.assertIsNone(context_of(self.call("Read")))
        self.assertIsNone(context_of(self.call("Edit")))
        self.assertIn("3 tool calls in a row", context_of(self.call("Bash")))
        self.assertIsNone(context_of(self.call("Read")))


class MemorySaveOnStop(HookCase):
    def stop(self, session_id="s1", active=False):
        event = {"session_id": session_id, "stop_hook_active": active}
        return run_hook("memory_save_on_stop.py", event, self.env())

    def test_blocks_once_per_session(self):
        first = self.stop()
        self.assertEqual(first.returncode, 2)
        self.assertIn("durable facts", first.stderr)
        self.assertEqual(self.stop().returncode, 0)
        self.assertEqual(self.stop("s2").returncode, 2)

    def test_stop_hook_active_lets_the_stop_through(self):
        self.assertEqual(self.stop(active=True).returncode, 0)

    def test_unsafe_session_id_never_blocks(self):
        self.assertEqual(self.stop("../escape").returncode, 0)
        self.assertFalse((self.root / "escape.memory-asked").exists())


class RecallReinject(HookCase):
    def prompt(self):
        return run_hook("recall_reinject.py", {"session_id": "s1", "prompt": "next"}, self.env())

    def test_adds_the_index_every_nth_prompt(self):
        (self.root / "INDEX.md").write_text("release-needs-two-reviews.md: a release needs two reviews.\n")
        self.assertIsNone(context_of(self.prompt()))
        self.assertIn("release-needs-two-reviews.md", context_of(self.prompt()))
        self.assertIsNone(context_of(self.prompt()))

    def test_cuts_a_long_index(self):
        (self.root / "INDEX.md").write_text("x" * 20000)
        self.prompt()
        self.assertIn("[cut at 9,000 characters]", context_of(self.prompt()))

    def test_missing_index_never_blocks(self):
        self.prompt()
        result = self.prompt()
        self.assertEqual((result.returncode, result.stdout), (0, ""))


class PrSizeNudge(HookCase):
    def git(self, *args):
        subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)

    def setUp(self):
        super().setUp()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "--allow-empty", "-m", "base")
        self.git("branch", "base")
        self.write_config(base_ref="base")

    def commit_files(self, count, lines):
        for index in range(count):
            (self.repo / f"f{index}.txt").write_text("x\n" * lines)
        self.git("add", ".")
        self.git("-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "-m", "change")

    def push(self, command="git push origin main"):
        return run_hook("pr_size_nudge.py", {"tool_name": "Bash", "tool_input": {"command": command}}, self.env(CLAUDE_PROJECT_DIR=str(self.repo)))

    def test_small_push_adds_nothing(self):
        self.commit_files(1, 2)
        self.assertIsNone(context_of(self.push()))

    def test_large_push_adds_a_reminder(self):
        self.commit_files(1, 9)
        result = self.push()
        self.assertEqual(result.returncode, 0)
        self.assertIn("changes 9 lines in 1 files", context_of(result))

    def test_many_files_add_a_reminder(self):
        self.commit_files(3, 1)
        self.assertIn("in 3 files", context_of(self.push()))

    def test_option_shaped_base_ref_is_refused(self):
        self.commit_files(1, 9)
        self.write_config(base_ref=f"--output={self.root / 'evil'}")
        result = self.push()
        self.assertEqual((result.returncode, result.stdout), (0, ""))
        self.assertIn("base_ref must not start with -", result.stderr)
        self.assertEqual(list(self.root.glob("evil*")), [])

    def test_other_commands_add_nothing(self):
        self.commit_files(1, 9)
        self.assertIsNone(context_of(self.push("git status")))


class ClaudeRegistrationsWithoutClaudeProjectDir(unittest.TestCase):
    """GitHub Copilot CLI also reads .claude/settings.json and documents no CLAUDE_PROJECT_DIR."""

    BLOCKING = {option["file"]: option["blocking"] for option in next(
        question for question in json.loads((HERE.parent / "kit-manifest.json").read_text())["questions"]
        if question["id"] == "hooks")["options"]}
    EVENT = {"session_id": "s1", "tool_name": "Bash", "tool_input": {"command": "git status"}, "prompt": "x",
             "stop_hook_active": True}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = pathlib.Path(self.tmp.name) / "state"

    def tearDown(self):
        self.tmp.cleanup()

    def project(self, name, in_git=True, with_scripts=True):
        root = pathlib.Path(self.tmp.name) / name
        (root / ".claude/hooks").mkdir(parents=True)
        (root / "src").mkdir()
        if in_git:
            subprocess.run(["git", "init", "-q", str(root)], check=True)
        if with_scripts:
            for script in set(HERE.glob("*.py")) - {HERE / "test_hooks.py"}:
                (root / ".claude/hooks" / script.name).write_text(script.read_text())
        return root

    def commands(self):
        for registration in sorted((HERE.parent / "files/claude").glob("hook-*.json")):
            for groups in json.loads(registration.read_text())["hooks"].values():
                for group in groups:
                    for handler in group["hooks"]:
                        script = handler["command"].split("/.claude/hooks/")[1].split(".py")[0] + ".py"
                        yield registration.name, script, handler["command"]

    def run_command(self, shell, command, folder):
        environ = {key: value for key, value in os.environ.items() if not key.startswith(("STARTER_KIT_", "CLAUDE_"))}
        return subprocess.run([shell, "-c", command], cwd=folder, input=json.dumps({**self.EVENT, "cwd": str(folder)}),
                              capture_output=True, text=True, timeout=30,
                              env={**environ, "STARTER_KIT_STATE_DIR": str(self.state)})

    def assert_started(self, result):
        self.assertNotIn("can't open file", result.stderr)
        self.assertNotEqual(result.returncode, 127, result.stderr)

    def test_every_command_starts_from_the_root_and_a_subfolder_of_a_path_with_a_space(self):
        root = self.project("my repo")
        for name, _, command in self.commands():
            for shell in ["sh", "bash"]:
                for folder in [root, root / "src"]:
                    with self.subTest(registration=name, shell=shell, folder=folder.name):
                        self.assert_started(self.run_command(shell, command, folder))

    def test_every_command_starts_from_the_root_of_a_folder_outside_git(self):
        root = self.project("no git", in_git=False)
        for name, _, command in self.commands():
            with self.subTest(registration=name):
                self.assert_started(self.run_command("sh", command, root))

    def test_a_missing_advisory_script_lets_the_call_through_and_a_missing_guardrail_blocks(self):
        root = self.project("empty", with_scripts=False)
        for name, script, command in self.commands():
            for shell in ["sh", "bash"]:
                with self.subTest(registration=name, shell=shell):
                    result = self.run_command(shell, command, root)
                    if self.BLOCKING[script]:
                        self.assertNotEqual(result.returncode, 0)
                    else:
                        self.assertEqual((result.returncode, result.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
