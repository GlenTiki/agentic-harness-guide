#!/usr/bin/env python3
"""Find the compaction point that your own sessions support. Standard library only.

Usage: python3 -I compaction_point.py LOG.csv
LOG.csv has a header and the columns session, boundary, tokens_used, window, constraint_dropped (0 or 1).
Each row is one phase boundary in one session. Measure tokens_used and window in your own tool.
The rule: compact at the last phase boundary that sits below the lowest fraction of the window
at which you saw a constraint drop. Exit code 1 when the log has no row without a drop below that fraction.
"""
import csv
import sys
from pathlib import Path


def read_rows(path):
    with Path(path).open(newline="") as handle:
        return [
            {
                "session": row["session"],
                "boundary": row["boundary"],
                "fraction": int(row["tokens_used"]) / int(row["window"]),
                "dropped": row["constraint_dropped"] == "1",
            }
            for row in csv.DictReader(handle)
        ]


def compaction_point(rows):
    """Return (lowest fraction with a drop or None, fractions of clean boundaries below it)."""
    drops = [r["fraction"] for r in rows if r["dropped"]]
    lowest_drop = min(drops) if drops else None
    clean = sorted(r["fraction"] for r in rows if not r["dropped"] and (lowest_drop is None or r["fraction"] < lowest_drop))
    return lowest_drop, clean


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    rows = read_rows(argv[0])
    for row in sorted(rows, key=lambda r: r["fraction"]):
        print(f"{row['fraction']:.2f}  {row['session']:<3} {row['boundary']:<14} {'DROPPED' if row['dropped'] else 'ok'}")
    lowest_drop, clean = compaction_point(rows)
    if lowest_drop is None:
        print("no drop seen: this log cannot place a compaction point")
        return 1
    print(f"lowest fraction with a drop: {lowest_drop:.2f}")
    if not clean:
        print("no clean boundary below it: compact earlier than your first logged boundary")
        return 1
    print(f"compact at the last boundary below that fraction: about {clean[-1]:.2f} of the window")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
