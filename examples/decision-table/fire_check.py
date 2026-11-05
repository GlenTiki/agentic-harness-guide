#!/usr/bin/env python3
"""Check which row of a decision table fires for each case. Exit 1 if any case fires the wrong row."""
import json
import sys


def matching_rows(table, cues):
    return [
        row["id"]
        for row in table["rows"]
        if not row.get("fallback") and all(cues.get(cue) == value for cue, value in row["when"].items())
    ]


def first_row(table, cues):
    matches = matching_rows(table, cues)
    if matches:
        return matches[0]
    return next((row["id"] for row in table["rows"] if row.get("fallback")), None)


def check(table, cases, out=sys.stdout):
    failures = 0
    for case in cases:
        matches = matching_rows(table, case["cues"])
        fired = first_row(table, case["cues"])
        ok = fired == case["expect"]
        failures += not ok
        label = fired or "no row"
        wanted = case["expect"] or "no row"
        also = f" (also matches {', '.join(matches[1:])})" if len(matches) > 1 else ""
        out.write(f"{'ok  ' if ok else 'FAIL'} {case['name']}: fired {label}, wanted {wanted}{also}\n")
    out.write(f"{len(cases) - failures} of {len(cases)} cases fired the expected row\n")
    return 1 if failures else 0


if __name__ == "__main__":
    with open(sys.argv[1]) as table_file, open(sys.argv[2]) as cases_file:
        sys.exit(check(json.load(table_file), json.load(cases_file)))
