import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import tool_cost

HERE = Path(__file__).resolve().parent
TOOLS = tool_cost.tool_list(json.loads((HERE / "sample_tools.json").read_text()))


class ToolCost(unittest.TestCase):
    def test_definition_size_counts_name_description_and_compact_schema(self):
        tool = {"name": "ab", "description": "cde", "input_schema": {"type": "object"}}
        self.assertEqual(tool_cost.definition_chars(tool), 2 + 3 + len('{"type":"object"}'))

    def test_mcp_input_schema_spelling_is_measured(self):
        tool = {"name": "ab", "description": "cde", "inputSchema": {"type": "object"}}
        self.assertEqual(tool_cost.definition_chars(tool), 2 + 3 + len('{"type":"object"}'))

    def test_the_snake_case_alias_gives_the_same_size(self):
        schema = {"type": "object"}
        camel = {"name": "a", "description": "b", "inputSchema": schema}
        snake = {"name": "a", "description": "b", "input_schema": schema}
        self.assertEqual(tool_cost.definition_chars(camel), tool_cost.definition_chars(snake))

    def test_a_full_tools_list_response_and_its_result_object_give_the_same_tools(self):
        response = {"jsonrpc": "2.0", "id": 1, "result": {"tools": TOOLS}}
        self.assertEqual(tool_cost.tool_list(response), tool_cost.tool_list(response["result"]))

    def test_the_fixture_is_a_tools_list_response_with_mcp_field_names(self):
        document = json.loads((HERE / "sample_tools.json").read_text())
        self.assertEqual(document["jsonrpc"], "2.0")
        self.assertTrue(all("inputSchema" in tool and "input_schema" not in tool for tool in document["result"]["tools"]))

    def test_tokens_round_up(self):
        self.assertEqual([tool_cost.estimate_tokens(n) for n in (0, 1, 4, 5)], [0, 1, 1, 2])

    def test_the_sample_list_totals_1940_characters(self):
        self.assertEqual(sum(tool_cost.definition_chars(t) for t in TOOLS), 1940)

    def test_the_command_prints_a_total_line(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            self.assertEqual(tool_cost.main([str(HERE / "sample_tools.json")]), 0)
        self.assertIn("total", buffer.getvalue().splitlines()[-2])

    def test_no_argument_prints_usage_and_exits_2(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(tool_cost.main([]), 2)


if __name__ == "__main__":
    unittest.main()
