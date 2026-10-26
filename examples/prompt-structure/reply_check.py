#!/usr/bin/env python3
"""Check a structured reply to the shared-bills ask, and run a small regression over stored replies. Standard library only.

Usage:
  python3 -I reply_check.py fixtures        Check every stored reply in fixtures/ and compare with a syntax-only check.
  python3 -I reply_check.py regress MODEL   Check the stored replies of MODEL against the case set. Exit 1 if any fails.
"""
import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONEY = re.compile(r"^\d+\.\d\d$")
OK_KEYS = {"status", "months_counted", "total", "each_pays", "sam_pays", "check"}
STOP_KEYS = {"status", "months_counted", "reason"}
CHECK_KEYS = {"count", "sum"}


def money(value):
    return f"{Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):.2f}"


def key_errors(reply, expected):
    missing = sorted(expected - reply.keys())
    extra = sorted(reply.keys() - expected)
    return ([f"missing key: {', '.join(missing)}"] if missing else []) + ([f"unexpected key: {', '.join(extra)}"] if extra else [])


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def check_ok(reply, figures):
    if reply.get("status") != "ok":
        return ['status must be "ok" for a complete set of 12 months']
    errors = key_errors(reply, OK_KEYS)
    if errors:
        return errors
    amounts = [Decimal(a) for _, a in figures]
    total = sum(amounts)
    share = Decimal(money(total / 3))
    expected = {"total": money(total), "each_pays": money(share), "sam_pays": money(total - 2 * share)}
    errors = [f"{name} should be {value}, got {reply[name]!r}" for name, value in expected.items() if reply[name] != expected[name]]
    check = reply["check"]
    if not isinstance(check, dict):
        return errors + ["check must be an object"]
    check_errors = key_errors(check, CHECK_KEYS)
    if check_errors:
        return errors + check_errors
    if check["count"] != len(figures) or not is_int(check["count"]):
        errors.append(f"check.count should be {len(figures)}, got {check['count']!r}")
    if check["sum"] != money(total):
        errors.append(f"check.sum should be {money(total)}, got {check['sum']!r}")
    if reply["months_counted"] != len(figures):
        errors.append(f"months_counted should be {len(figures)}, got {reply['months_counted']!r}")
    return errors


def check_stop(reply, figures):
    if reply.get("status") != "stop":
        return [f'status must be "stop": {len(figures)} figures, not 12 distinct months']
    errors = key_errors(reply, STOP_KEYS)
    if errors:
        return errors
    names = [m for m, _ in figures]
    repeated = sorted({m for m in names if names.count(m) > 1})
    missing = [m for m in MONTHS if m not in names]
    errors = []
    if reply["months_counted"] != len(figures):
        errors.append(f"months_counted should be {len(figures)}, got {reply['months_counted']!r}")
    reason = reply["reason"] if isinstance(reply["reason"], str) else ""
    errors += [f"reason does not name the problem month {m}" for m in repeated + missing if m not in reason]
    return errors


def validate(text, figures):
    """Return a list of reasons to reject the reply. An empty list means accept."""
    try:
        reply = json.loads(text)
    except json.JSONDecodeError as error:
        return [f"not JSON: {error.msg}"]
    if not isinstance(reply, dict):
        return ["reply is not a JSON object"]
    names = [m for m, _ in figures]
    complete = len(names) == 12 and len(set(names)) == 12
    return check_ok(reply, figures) if complete else check_stop(reply, figures)


def syntax_only(text):
    try:
        return isinstance(json.loads(text), dict)
    except json.JSONDecodeError:
        return False


def load_cases():
    return json.loads((HERE / "cases.json").read_text())


def run_fixtures():
    cases = load_cases()
    wrong = 0
    print(f"{'case':<10} {'reply':<22} {'syntax-only':<12} {'validator':<9} reason")
    for path in sorted((HERE / "fixtures").glob("*/*.txt")):
        case, text = path.parent.name, path.read_text()
        errors = validate(text, cases[case]["figures"])
        wrong += (not errors) != path.stem.startswith("good")
        print(f"{case:<10} {path.stem:<22} {'accept' if syntax_only(text) else 'reject':<12} {'accept' if not errors else 'reject':<9} {'; '.join(errors)}")
    print(f"validator verdicts that disagree with the file name: {wrong}")
    return 1 if wrong else 0


def run_regression(model):
    cases = load_cases()
    pin = json.loads((HERE / "regression" / "pin.json").read_text())["model"]
    print(f"model under test: {model}   pinned model: {pin}")
    failed = 0
    for case, spec in cases.items():
        paths = sorted((HERE / "regression" / "replies" / model / case).glob("*.txt"))
        passes = sum(not validate(p.read_text(), spec["figures"]) for p in paths)
        failed += passes != len(paths) or not paths
        print(f"{case:<13} {passes} of {len(paths)} replies pass")
    print("criterion: every stored reply for every case passes")
    print("result: " + ("FAIL" if failed else "PASS"))
    return 1 if failed else 0


def main(argv):
    if argv[:1] == ["fixtures"]:
        return run_fixtures()
    if len(argv) == 2 and argv[0] == "regress":
        return run_regression(argv[1])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
