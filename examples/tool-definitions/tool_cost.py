#!/usr/bin/env python3
"""Measure how much context a tool list occupies before any call. Standard library only.

Usage: python3 -I tool_cost.py TOOLS.json
The size is the length of each tool's name, description and input schema as JSON text.
Tokens use the rule of thumb of 4 characters per token. It is not a real tokenizer; use your tool's own count to confirm.
"""
import json
import sys
from pathlib import Path

CHARS_PER_TOKEN = 4


def definition_chars(tool):
    return len(tool["name"]) + len(tool["description"]) + len(json.dumps(tool["input_schema"], separators=(",", ":")))


def estimate_tokens(chars):
    return -(-chars // CHARS_PER_TOKEN)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    tools = json.loads(Path(argv[0]).read_text())["tools"]
    sizes = sorted(((definition_chars(t), t["name"]) for t in tools), reverse=True)
    total = sum(chars for chars, _ in sizes)
    print(f"{'tool':<14} {'chars':>6} {'tokens':>7}")
    for chars, name in sizes:
        print(f"{name:<14} {chars:>6} {estimate_tokens(chars):>7}")
    print(f"{'total':<14} {total:>6} {estimate_tokens(total):>7}   ({len(tools)} tools)")
    description_chars = sum(len(t["description"]) for t in tools)
    print(f"descriptions alone: {description_chars} chars, {estimate_tokens(description_chars)} tokens")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
