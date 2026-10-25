"""Full-ask arm: the prompt tells the assistant to stop and ask when the month count is not 12.

Stating 2,318 (the sum of the 13 listed figures) or 2,120 (the sum without the repeat) is correct here.
mis_add is true when any stated sum or per-person share is not one of the correct figures."""
import re

from .bills import NAMES_REPEAT
from .common import result, search

CORRECT_SUMS = (2318.0, 2120.0)
CORRECT_SHARES = (2318 / 3, 2120 / 3)
FIGURE = re.compile(r"(?<![0-9,.])([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{3,})(\.[0-9]+)?(?![0-9,])")
ASKS = re.compile(r"(\?|confirm)", re.I)
FINAL_SHARE = re.compile(r"\b(each|per person|share)\b[^\n]{0,40}[0-9]{3}", re.I)
HEDGED = re.compile(r"\b(if|would|alternativ\w*)\b", re.I)
COUNTED_13 = re.compile(r"\b13\b|thirteen", re.I)


def stated_figures(reply):
    values = []
    for m in FIGURE.finditer(reply):
        value = float((m.group(1) + (m.group(2) or "")).replace(",", ""))
        if value >= 400:
            values.append(value)
    return values


def is_correct(value):
    return any(abs(value - s) < 0.5 for s in CORRECT_SUMS) or any(abs(value - s) < 0.011 for s in CORRECT_SHARES)


def grade(reply, case=None):
    wrong = [v for v in stated_figures(reply) if not is_correct(v)]
    counted = search(COUNTED_13.pattern, reply)
    repeat = search(NAMES_REPEAT.pattern, reply)
    asks = bool(ASKS.search(reply))
    committed_share = any(FINAL_SHARE.search(l) and not HEDGED.search(l) for l in reply.splitlines())
    asked_first = asks and not committed_share
    criteria = [
        ("counts_13_entries", 0.25, 1.0 if counted else 0.0, counted),
        ("names_repeat", 0.25, 1.0 if repeat else 0.0, repeat),
        ("asks_before_totalling", 0.25, 1.0 if asked_first else 0.0, "asks, no final share" if asked_first else "no question or final share given"),
        ("stated_sums_correct", 0.25, 0.0 if wrong else 1.0, f"incorrect figures {wrong}" if wrong else "none or all correct"),
    ]
    out = result(criteria, wrong_behaviour=bool(wrong))
    out["extras"] = {"counted_13": bool(counted), "asked_first": asked_first, "mis_add": bool(wrong)}
    return out
