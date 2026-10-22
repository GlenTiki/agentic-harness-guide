#!/usr/bin/env python3
"""Run block_force_push.py against a fixed matrix. Prints one line per row and a summary."""
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE / "block_force_push.py"
PAGE = HERE.parents[1] / "src/content/docs/shelf/control/hooks.mdx"

SHOULD_BLOCK = [
    "git push --force", "git push -f origin main", "git push origin main -f", "git push origin +main",
    "git push --force-with-lease", "git push origin -d feature", "git push --del origin feature",
    "git push --delete origin feature", "git push --mirror", "git push --prune origin",
    "git push --force-if-includes", "/usr/bin/git push -f", "git -C . push --force", "status; git push -f",
    "git push origin :feature", 'sh -c "git push -f"', "bash -c 'git push --force'", "git push origin main --force",
    "git push --forc origin", "git push -fu origin main", "git push origin HEAD:main --force",
    "GIT_SSH_COMMAND=x git push -f", "env git push -f", "git push origin $(echo +main)", "(git push -f)",
    "echo $(git push --force)",
]
SHOULD_ALLOW = [
    "git status", "git push origin main", "git push -u origin feature-fix", "git log --grep push",
    "git commit -m 'push -f docs'", "echo hello",
]
MALFORMED = [
    ("empty stdin", ""), ("not json", "hello"), ("json null", "null"), ("no tool_input", "{}"),
    ("command is a list", '{"tool_input":{"command":["git","push","-f"]}}'), ("tool_input null", '{"tool_input":null}'),
]
KNOWN_BYPASSES = [
    "F=-f; git push $F", "git push origin main $'\\x2df'", "python3 -c 'import os;os.system(\"git push -f\")'",
    "git p -f", "./deploy.sh",
]


def run(raw, script=SCRIPT):
    return subprocess.run(["python3", str(script)], input=raw, capture_output=True, text=True).returncode


def call(command):
    return json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})


def main():
    bad = 0
    rows = [(c, True) for c in SHOULD_BLOCK] + [(c, False) for c in SHOULD_ALLOW]
    for command, expect_block in rows:
        code = run(call(command))
        ok = (code == 2) == expect_block
        bad += not ok
        print(f"{'OK ' if ok else 'BAD'} exit={code} expect={'block' if expect_block else 'allow'} :: {command}")
    for label, raw in MALFORMED:
        code = run(raw)
        ok = code == 2
        bad += not ok
        print(f"{'OK ' if ok else 'BAD'} exit={code} expect=block (malformed input: {label})")
    missing = subprocess.run(["python3", str(HERE / "missing.py")], capture_output=True).returncode
    print(f"{'OK ' if missing == 2 else 'BAD'} exit={missing} expect=2 (python3 on a missing script)")
    bad += missing != 2
    print("--- known bypasses: these pass through by design, see the page")
    for command in KNOWN_BYPASSES:
        print(f"    exit={run(call(command))} :: {command}")
    sample = SCRIPT.read_text()
    on_page = sample in PAGE.read_text() if PAGE.exists() else None
    label = "SKIP" if on_page is None else "OK " if on_page else "BAD"
    print(f"{label} page shows the sample file exactly: {on_page}")
    bad += on_page is False
    print(f"{len(rows)} command rows, {len(MALFORMED)} malformed rows, {bad} BAD")
    print("0 BAD" if bad == 0 else f"{bad} BAD")
    sys.exit(1 if bad else 0)


main()
