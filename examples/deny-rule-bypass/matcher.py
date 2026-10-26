#!/usr/bin/env python3
"""A teaching matcher. It is not Claude Code's matcher. It shows what a text rule can and cannot see."""
import fnmatch
import os
import shlex

DENY_RULES = ["Bash(rm -rf *)", "Read(./.env)"]
FIXTURES = [
    ("rm -rf build", "bash", "the written spelling"),
    ("rm -fr build", "bash", "flags swapped"),
    ("rm -r -f build", "bash", "flags split"),
    ("/bin/rm -rf build", "bash", "full path to the program"),
    ("sh -c 'rm -rf build'", "bash", "wrapped in a shell"),
    ("python3 clean.py", "bash", "script that runs the removal"),
    ("cat .env", "bash", "second route to a denied file"),
    ("echo hi", "bash", "harmless"),
]


def text_rule_denies(command, tool, rules=DENY_RULES):
    for rule in rules:
        rule_tool, pattern = rule[:-1].split("(", 1)
        if rule_tool.lower() == tool and fnmatch.fnmatchcase(command, pattern):
            return True
    return False


def parsed_check_denies(command):
    words = shlex.split(command)
    for index, word in enumerate(words):
        if os.path.basename(word) != "rm":
            continue
        flags = "".join(w[1:] for w in words[index + 1:] if w.startswith("-") and not w.startswith("--"))
        if "r" in flags and "f" in flags:
            return True
        if any(len(w) > 1 and " " in w and parsed_check_denies(w) for w in words[index + 1:]):
            return True
    return any(" " in w and parsed_check_denies(w) for w in words)


def main():
    print(f"{'command':<24}{'text rule':<12}{'parsed check':<14}note")
    for command, tool, note in FIXTURES:
        text = "deny" if text_rule_denies(command, tool) else "no match"
        parsed = "deny" if parsed_check_denies(command) else "no match"
        print(f"{command:<24}{text:<12}{parsed:<14}{note}")


if __name__ == "__main__":
    main()
