#!/usr/bin/env python3
"""Rank the repeated manual steps in an actions log. Standard library only.

Usage: python3 -I improvement_queue.py ACTIONS.jsonl
ACTIONS.jsonl has one JSON object per line, in the format of the observability page: time, session, seq, phase, tool, id, target.
A line may also carry "minutes", the time one run of the step took you. A line without it counts as 1 minute.
Only "post" lines count, because a "pre" line is an attempt and a "post" line is a finished step.
A step is the pair of tool and target. It is repeated when it appears at least twice.
The top three steps by total minutes get a recommendation.
Exit code 1 and a message on stderr when a line is not valid. Exit code 0 when the log is empty.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

TOP = 3
MINIMUM_REPEATS = 2
DEFAULT_MINUTES = 1


class LogError(ValueError):
    pass


def read_steps(lines):
    """Return {(tool, target): [minutes, ...]} for every finished step."""
    steps = defaultdict(list)
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            phase, tool, target = record["phase"], record["tool"], record["target"]
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            raise LogError(f"line {number}: not a valid log line ({error!r})") from error
        minutes = record.get("minutes", DEFAULT_MINUTES)
        if isinstance(minutes, bool) or not isinstance(minutes, (int, float)) or minutes < 0:
            raise LogError(f"line {number}: minutes must be a number of 0 or more, got {minutes!r}")
        if phase == "post":
            steps[(tool, target)].append(minutes)
    return steps


def rank(steps):
    repeated = [(key, runs) for key, runs in steps.items() if len(runs) >= MINIMUM_REPEATS]
    repeated.sort(key=lambda item: (-sum(item[1]), item[0]))
    return repeated[:TOP]


def recommendation(key, runs):
    return (
        f"You did '{key[1]}' by hand {len(runs)} times. Recommend automating it. "
        f"Estimated saving: up to {sum(runs):g} minutes for this log."
    )


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    try:
        steps = read_steps(Path(argv[0]).read_text().splitlines())
    except LogError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if not steps:
        print("The log has no finished steps.")
        return 0
    top = rank(steps)
    if not top:
        print("No step repeated.")
        return 0
    for position, (key, runs) in enumerate(top, start=1):
        print(f"{position}. {recommendation(key, runs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
