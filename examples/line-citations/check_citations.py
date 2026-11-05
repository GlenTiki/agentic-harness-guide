#!/usr/bin/env python3
"""Check path:line citations in Markdown files. Usage: check_citations.py ROOT. Exit 1 if a live document has an unresolved citation."""
import pathlib
import re
import sys

CITATION = re.compile(r"`(?P<path>[\w./-]+\.\w+):(?P<start>\d+)(?:-(?P<end>\d+))?`(?: (?:defines|calls|sets) `(?P<symbol>[\w.]+)`)?")
SNAPSHOT_MARKER = re.compile(r"\A<!-- snapshot: \d{4}-\d{2}-\d{2} -->")


def check_file(document, root):
    problems = []
    for number, line in enumerate(document.read_text().splitlines(), start=1):
        for match in CITATION.finditer(line):
            problem = resolve(match, root)
            if problem:
                problems.append(f"{document.relative_to(root)}:{number}: {problem}")
    return problems


def resolve(match, root):
    target = root / match["path"]
    if not target.is_file():
        return f"{match['path']} does not exist"
    lines = target.read_text().splitlines()
    start, end = int(match["start"]), int(match["end"] or match["start"])
    if not 1 <= start <= end <= len(lines):
        return f"{match['path']}:{match['start']} is outside the {len(lines)}-line file"
    symbol = match["symbol"]
    if symbol and symbol.split(".")[-1] not in lines[start - 1]:
        return f"{match['path']}:{start} does not hold {symbol}"
    return None


def main(root):
    problems, exempt = [], 0
    for document in sorted(root.rglob("*.md")):
        if SNAPSHOT_MARKER.match(document.read_text()):
            exempt += 1
            continue
        problems += check_file(document, root)
    if problems:
        print("\n".join(problems))
    print(f"{len(problems)} unresolved, {exempt} snapshot exempt")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(pathlib.Path(sys.argv[1])))
