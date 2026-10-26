#!/usr/bin/env python3
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from alias import BASELINE, DOCUMENT, INTERNAL, alias, restore  # noqa: E402

FULL = {**BASELINE, **INTERNAL}
masked, mapping = alias(DOCUMENT, FULL)
assert restore(masked, mapping) == (DOCUMENT, [])
assert masked.count("[CASE_1]") == 2 and masked.count("[ACCOUNT_1]") == 2
assert "CX-48213-ALPHA" not in masked and "ACC/2291/004417" not in masked
base_masked, base_map = alias(DOCUMENT, BASELINE)
assert "CX-48213-ALPHA" in base_masked and "ACC/2291/004417" in base_masked
assert restore(base_masked, base_map)[0] == DOCUMENT
_, unresolved = restore("Reply about [CASE_9].", mapping)
assert unresolved == ["[CASE_9]"]
try:
    alias("already [EMAIL_1] here", FULL)
    raise SystemExit("expected a refusal")
except ValueError:
    pass
print("ok")
