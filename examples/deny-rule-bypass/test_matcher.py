#!/usr/bin/env python3
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from matcher import parsed_check_denies, text_rule_denies  # noqa: E402

TEXT_DENIES = {"rm -rf build"}
PARSED_DENIES = {"rm -rf build", "rm -fr build", "rm -r -f build", "/bin/rm -rf build", "sh -c 'rm -rf build'"}
ALL = TEXT_DENIES | PARSED_DENIES | {"python3 clean.py", "cat .env", "echo hi"}

for command in ALL:
    assert text_rule_denies(command, "bash") == (command in TEXT_DENIES), command
    assert parsed_check_denies(command) == (command in PARSED_DENIES), command
assert text_rule_denies("./.env", "read")
assert not text_rule_denies("./.env", "bash")
print("ok")
