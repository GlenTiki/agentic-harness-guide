#!/usr/bin/env python3
import json
import os
import shlex
import sys

RISKY_LONG = ("--force", "--force-with-lease", "--force-if-includes", "--delete", "--mirror", "--prune")
RISKY_SHORT = "fd"


def is_risky_flag(token):
    token = token.rstrip(")}`")
    if token.startswith("--"):
        name = token.split("=")[0]
        return len(name) >= 5 and any(long.startswith(name) for long in RISKY_LONG)
    if token.startswith("-"):
        return any(letter in token[1:] for letter in RISKY_SHORT)
    return token.startswith(("+", ":"))


def is_risky_push(tokens):
    for index, token in enumerate(tokens):
        if " " in token and is_risky_push(shlex.split(token)):
            return True
        if os.path.basename(token.lstrip("({$`")) == "git" and "push" in tokens[index:]:
            after_push = tokens[tokens.index("push", index) + 1:]
            return any(is_risky_flag(flag) for flag in after_push)
    return False


def main():
    try:
        command = json.load(sys.stdin)["tool_input"]["command"]
        risky = is_risky_push(shlex.split(command))
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        print(f"Blocked: the hook could not read this call ({error}).", file=sys.stderr)
        sys.exit(2)
    if risky:
        print("Blocked: this push can overwrite or delete remote history. Ask the user to run it themselves.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
