#!/usr/bin/env python3
"""List which ledger constraints a compaction summary kept and which it lost. Standard library only.

Usage: python3 -I compaction_audit.py LEDGER.json SUMMARY.txt
A constraint counts as kept when every phrase in its "keep_if_mentions" list appears in the summary (case-insensitive).
Exit code 1 when any constraint is lost.
"""
import json
import sys
from pathlib import Path


def lost_constraints(ledger, summary):
    text = summary.lower()
    kept, lost = [], []
    for constraint in ledger["constraints"]:
        present = all(phrase.lower() in text for phrase in constraint["keep_if_mentions"])
        (kept if present else lost).append(constraint)
    return kept, lost


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    ledger = json.loads(Path(argv[0]).read_text())
    kept, lost = lost_constraints(ledger, Path(argv[1]).read_text())
    for constraint in kept:
        print(f"kept  {constraint['id']}: {constraint['text']}")
    for constraint in lost:
        print(f"LOST  {constraint['id']}: {constraint['text']}")
    print(f"{len(kept)} of {len(kept) + len(lost)} constraints survive the summary")
    return 1 if lost else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
