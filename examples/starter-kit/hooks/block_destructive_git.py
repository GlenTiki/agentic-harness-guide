#!/usr/bin/env python3
"""PreToolUse hook for Bash. Exit 2 blocks a force push, git reset --hard and a forced git clean."""

import json
import os
import shlex
import sys

SHELLS = {"sh", "bash", "zsh", "dash"}
WRAPPERS = {"env", "command", "nohup", "time", "exec"}
SEPARATORS = {";", "&", "&&", "|", "||", "(", ")", "$(", "`"}
GIT_OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}


def split_commands(command):
    lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    commands, current = [], []
    for token in lexer:
        if token in SEPARATORS or set(token) <= set("();&|`"):
            commands.append(current)
            current = []
        else:
            current.append(token.strip("$`"))
    commands.append(current)
    return [tokens for tokens in commands if tokens]


def short_flags(args):
    return "".join(arg[1:] for arg in args if arg.startswith("-") and not arg.startswith("--"))


def is_destructive(subcommand, args):
    if subcommand == "push":
        long_force = any(arg.startswith("--force") for arg in args)
        return long_force or "f" in short_flags(args) or any(arg.startswith("+") for arg in args)
    if subcommand == "reset":
        return "--hard" in args
    if subcommand == "clean":
        return "--force" in args or "f" in short_flags(args)
    return False


def git_subcommand(tokens):
    index = 0
    while index < len(tokens) and (tokens[index] in WRAPPERS or "=" in tokens[index].split("/")[0]):
        index += 1
    if index >= len(tokens) or os.path.basename(tokens[index]) != "git":
        return None, []
    rest = tokens[index + 1:]
    while rest and rest[0].startswith("-"):
        rest = rest[2:] if rest[0] in GIT_OPTIONS_WITH_VALUE else rest[1:]
    return (rest[0], rest[1:]) if rest else (None, [])


def is_risky(command):
    for tokens in split_commands(command):
        if os.path.basename(tokens[0]) in SHELLS and "-c" in tokens[:-1]:
            if is_risky(tokens[tokens.index("-c") + 1]):
                return True
            continue
        subcommand, args = git_subcommand(tokens)
        if subcommand and is_destructive(subcommand, args):
            return True
    return False


def main(stdin=sys.stdin):
    try:
        command = json.load(stdin)["tool_input"]["command"]
        if not isinstance(command, str):
            raise TypeError("tool_input.command is not text")
        risky = is_risky(command)
    except (ValueError, KeyError, TypeError, IndexError) as error:
        print(f"Blocked: the hook could not read this call ({error}).", file=sys.stderr)
        return 2
    if risky:
        print(
            "Blocked: this git command can destroy work or rewrite remote history. Ask the user to run it themselves.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
