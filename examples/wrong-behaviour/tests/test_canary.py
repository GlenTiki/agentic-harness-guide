import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canary  # noqa: E402


class CanaryTests(unittest.TestCase):
    def test_plant_writes_all_four_canaries(self):
        root = Path(tempfile.mkdtemp())
        words, marker = canary.plant(root, "abcd")
        self.assertIn(words["CLAUDEMD"], (root / "CLAUDE.md").read_text())
        self.assertIn(str(marker), (root / ".claude" / "settings.json").read_text())
        self.assertIn(words["SKILL"], (root / ".claude" / "skills" / "canary-skill" / "SKILL.md").read_text())
        self.assertIn("canary-mcp-abcd", (root / ".mcp.json").read_text())

    def test_evaluate_detects_a_leak_and_a_clean_run(self):
        words = {"CLAUDEMD": "CANARY-CLAUDEMD-x", "HOOK": "CANARY-HOOK-x", "SKILL": "CANARY-SKILL-x", "MCP": "CANARY-MCP-x"}
        marker = Path(tempfile.mkdtemp()) / "none"
        leaked = canary.evaluate({"tools": ["Bash"]}, {"result": "I was told CANARY-CLAUDEMD-x"}, words, marker)
        self.assertEqual(leaked["code_words_in_reply"], ["CLAUDEMD"])
        self.assertFalse(leaked["tools_empty"])
        clean = canary.evaluate({"tools": [], "mcp_servers": [], "skills": []}, {"result": "NONE"}, words, marker)
        self.assertEqual(clean["code_words_in_reply"], [])
        self.assertTrue(clean["tools_empty"] and clean["mcp_empty"] and clean["skills_empty"])

    def test_owner_tokens_are_matched_case_insensitively(self):
        marker = Path(tempfile.mkdtemp()) / "none"
        out = canary.evaluate({}, {"result": "I know Initech and nothing else"}, {"CLAUDEMD": "a"}, marker, ("initech", "acmecorp"))
        self.assertEqual(out["owner_tokens_in_reply"], ["initech"])
        self.assertEqual(canary.evaluate({}, {"result": "Initech"}, {"CLAUDEMD": "a"}, marker)["owner_tokens_in_reply"], [])

    def test_marker_file_is_detected(self):
        marker = Path(tempfile.mkdtemp()) / "m"
        marker.write_text("")
        out = canary.evaluate({}, {"result": "NONE"}, {"CLAUDEMD": "a", "HOOK": "b", "SKILL": "c", "MCP": "d"}, marker)
        self.assertTrue(out["marker_created"])

    def test_parse_stream_finds_init_and_result(self):
        stdout = "\n".join(json.dumps(e) for e in (
            {"type": "system", "subtype": "init", "tools": []}, {"type": "result", "result": "NONE"}))
        init, result = canary.parse_stream(stdout)
        self.assertEqual(init["tools"], [])
        self.assertEqual(result["result"], "NONE")


if __name__ == "__main__":
    unittest.main()
