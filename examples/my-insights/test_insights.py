#!/usr/bin/env python3
import hashlib
import importlib.util
import io
import json
import pathlib
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

HERE = pathlib.Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
CLAUDE_CODE_SESSION = "11111111-2222-4333-8444-555555555555"

spec = importlib.util.spec_from_file_location("insights", HERE / "insights.py")
insights = importlib.util.module_from_spec(spec)
spec.loader.exec_module(insights)


def digests(folder: pathlib.Path) -> dict:
    return {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.rglob("*")) if p.is_file()}


def run(argv: list) -> tuple:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        status = insights.main(argv)
    return status, out.getvalue(), err.getvalue()


class NormalisedFormat(unittest.TestCase):
    def setUp(self):
        self.result = insights.analyse(FIXTURES / "normalised")

    def test_counts_each_hard_signal_once(self):
        alpha = self.result["sessions"]["alpha"]
        self.assertEqual(alpha.counts, {"interruption": 1, "tool_error": 1, "refusal": 1})

    def test_skips_a_repeated_message_id(self):
        self.assertEqual(self.result["stats"]["duplicates"], 1)

    def test_names_a_session_without_a_session_field_after_its_file(self):
        self.assertEqual(self.result["sessions"]["beta"].friction, 0)

    def test_quotes_the_message_after_an_interruption(self):
        labels = [label for label, _ in self.result["sessions"]["alpha"].excerpts]
        self.assertIn("next user message after an interruption", labels)


class ClaudeCodeFormat(unittest.TestCase):
    def setUp(self):
        self.result = insights.analyse(FIXTURES / "claude-code")
        self.session = self.result["sessions"][CLAUDE_CODE_SESSION]

    def test_separates_a_refusal_from_a_failed_tool_call(self):
        self.assertEqual(self.session.counts, {"interruption": 1, "tool_error": 1, "refusal": 1})

    def test_skips_the_repeated_refusal_line(self):
        self.assertEqual(self.result["stats"]["duplicates"], 1)

    def test_ignores_lines_that_are_not_user_or_assistant_messages(self):
        self.assertEqual(self.result["stats"]["lines"], 13)
        self.assertEqual(list(self.result["sessions"]), [CLAUDE_CODE_SESSION])
        self.assertEqual(self.session.messages, 5)

    def test_counts_a_line_that_is_not_json_as_unreadable(self):
        self.assertEqual(self.result["stats"]["unreadable"], 1)


def claude_code_line(session: str, uuid: str, content, **extra) -> str:
    return json.dumps({"type": "user", "uuid": uuid, "sessionId": session, "message": {"role": "user", "content": content}, **extra})


def analyse_files(files: dict) -> dict:
    with tempfile.TemporaryDirectory() as folder:
        for name, lines in files.items():
            (pathlib.Path(folder) / name).write_text("\n".join(lines) + "\n")
        return insights.analyse(pathlib.Path(folder))


class ClaudeCodeShapesSeenInProbes(unittest.TestCase):
    refusal = claude_code_line("s1", "u2", [{"type": "tool_result", "tool_use_id": "t1", "is_error": True,
                                             "content": "The user doesn't want to proceed with this tool use."}],
                               toolDenialKind="user-rejected")
    tool_use_interruption = claude_code_line("s1", "u3", [{"type": "text", "text": "[Request interrupted by user for tool use]"}])

    def test_counts_a_rejected_tool_call_once(self):
        result = analyse_files({"s1.jsonl": [claude_code_line("s1", "u1", "Write a.txt"), self.refusal,
                                             self.tool_use_interruption]})
        self.assertEqual(result["sessions"]["s1"].counts, {"interruption": 0, "tool_error": 0, "refusal": 1})

    def test_counts_a_tool_use_interruption_without_a_refusal_as_an_interruption(self):
        result = analyse_files({"s1.jsonl": [claude_code_line("s1", "u1", "Run it"), self.tool_use_interruption]})
        self.assertEqual(result["sessions"]["s1"].counts["interruption"], 1)

    def test_skips_lines_that_a_forked_session_copies_under_a_new_session_id(self):
        original = [claude_code_line("s1", "u1", "Write a.txt"), self.refusal]
        fork = [line.replace('"s1"', '"s2"') for line in original] + [claude_code_line("s2", "u9", "Carry on")]
        result = analyse_files({"s1.jsonl": original, "s2.jsonl": fork})
        self.assertEqual(result["stats"]["duplicates"], 2)
        self.assertEqual(result["sessions"]["s1"].counts["refusal"], 1)
        self.assertEqual(result["sessions"]["s2"].friction, 0)


REDACTION_CASES = {
    "sk_dash": ("error: key sk-test-FAKE1234567890abcd rejected", "sk-test-FAKE"),
    "sk_live_underscore": ("key sk_live_FAKE1234567890abcd", "FAKE1234567890abcd"),
    "github_token": ("push with ghp_FAKE1234567890abcdefghij failed", "ghp_FAKE"),
    "aws_access_key": ("AKIAFAKEFAKEFAKEFAKE is the key", "AKIAFAKE"),
    "bearer": ("Authorization: Bearer FAKEfake.1234567890", "FAKEfake"),
    "jwt": ("cookie eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJGQUtFIn0.FAKEsignature", "eyJhbGci"),
    "google_api_key": ("url ?key=AIzaFAKEfakeFAKEfakeFAKEfake123 ", "AIzaFAKE"),
    "private_key_block": ("-----BEGIN RSA PRIVATE KEY-----\nFAKEFAKE\n-----END RSA PRIVATE KEY-----", "FAKEFAKE"),
    "underscore_prefixed_names": ("DB_PASSWORD=hunter2fake GITHUB_TOKEN=abc123fake aws_secret_access_key=xyz789fake",
                                  "fake"),
    "json_password": ('{"user": "sam", "password": "hunter2fake"}', "hunter2fake"),
    "quoted_value_with_space": ("secret = 'correct horse fake staple'", "horse"),
    "email": ("mail sam@example.com now", "sam@example.com"),
    "home_path": ("open /home/samfake/notes.txt", "samfake"),
}


class Redaction(unittest.TestCase):
    pass


def redaction_test(text: str, leaked: str):
    def test(self):
        self.assertNotIn(leaked, insights.redact(text))
    return test


for case, (text, leaked) in REDACTION_CASES.items():
    setattr(Redaction, f"test_redacts_{case}", redaction_test(text, leaked))


class Report(unittest.TestCase):
    def test_redacts_the_planted_secret_and_the_email(self):
        text = insights.report(insights.analyse(FIXTURES))
        self.assertNotIn("sk-test-FAKE", text)
        self.assertNotIn("sam@example.com", text)
        self.assertIn("API_KEY=<secret>", text)

    def test_lists_at_most_three_top_sessions_and_totals(self):
        text = insights.report(insights.analyse(FIXTURES))
        self.assertIn("| all friction | 6 |", text)
        self.assertEqual(text.count("\n### "), 2)

    def test_says_so_when_there_is_no_friction(self):
        with tempfile.TemporaryDirectory() as folder:
            line = {"id": "c1", "event": "message", "text": "All good."}
            (pathlib.Path(folder) / "clean.jsonl").write_text(json.dumps(line) + "\n")
            self.assertIn("No friction signals found.", insights.report(insights.analyse(pathlib.Path(folder))))

    def test_shortens_a_long_excerpt(self):
        self.assertEqual(len(insights.excerpt("x " * 200)), insights.EXCERPT_CHARS)


class ReadOnly(unittest.TestCase):
    def test_leaves_every_transcript_unchanged(self):
        before = digests(FIXTURES)
        with tempfile.TemporaryDirectory() as out:
            status, _, _ = run([str(FIXTURES), "--out", str(pathlib.Path(out) / "report.md")])
        self.assertEqual(status, 0)
        self.assertEqual(digests(FIXTURES), before)

    def test_refuses_to_write_the_report_inside_the_transcript_folder(self):
        status, _, err = run([str(FIXTURES), "--out", str(FIXTURES / "report.md")])
        self.assertEqual(status, 2)
        self.assertIn("refusing", err)
        self.assertFalse((FIXTURES / "report.md").exists())


if __name__ == "__main__":
    unittest.main()
