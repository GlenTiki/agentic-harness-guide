#!/usr/bin/env python3
"""Merge a JSON fragment into a JSON file for the kit's merge-json mode. Print the result; never write it.

Objects merge by key. Lists join, and an item already present is not added again. Two different scalars
at the same key, or two different types, are a conflict: the script reports each one and keeps the target.

Usage: python3 -I merge_settings.py TARGET.json FRAGMENT.json
Exit 0: the merged JSON is on stdout. Exit 1: conflicts are on stderr. Exit 2: a file cannot be read.
A missing TARGET counts as an empty object.
"""

import json
import pathlib
import sys


def merge(target, fragment, path="$"):
    """Return (merged, conflicts). Each conflict is the JSON path of a value the fragment could not set."""
    if isinstance(target, dict) and isinstance(fragment, dict):
        merged, conflicts = dict(target), []
        for key, value in fragment.items():
            if key in merged:
                merged[key], found = merge(merged[key], value, f"{path}.{key}")
                conflicts += found
            else:
                merged[key] = value
        return merged, conflicts
    if isinstance(target, list) and isinstance(fragment, list):
        return target + [item for item in fragment if item not in target], []
    if type(target) is type(fragment) and target == fragment:
        return target, []
    return target, [path]


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print(__doc__.strip().splitlines()[-3], file=sys.stderr)
        return 2
    target_path, fragment_path = map(pathlib.Path, args)
    try:
        target = json.loads(target_path.read_text()) if target_path.exists() else {}
        fragment = json.loads(fragment_path.read_text())
    except (OSError, ValueError) as error:
        print(f"read-error: {error}", file=sys.stderr)
        return 2
    merged, conflicts = merge(target, fragment)
    for path in conflicts:
        print(f"conflict: {path} differs in the target and the fragment. The target value is kept.", file=sys.stderr)
    if conflicts:
        return 1
    print(json.dumps(merged, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
