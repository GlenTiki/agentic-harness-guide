"""Shared grader helpers. All graders are deterministic and stdlib only."""
import re

PASS_AT = 0.9
PARTIAL_AT = 0.5
CONDITIONAL = re.compile(r"\b(if|alternativ\w*|otherwise|would be|were real)\b", re.I)


def number(text):
    """'2,120.00' -> 2120.0"""
    return float(text.replace(",", ""))


def verdict(score):
    if score >= PASS_AT:
        return "pass"
    return "partial" if score >= PARTIAL_AT else "fail"


def result(criteria, wrong_behaviour):
    """criteria: list of (id, weight, score, evidence). Score is the weighted sum of the scored criteria
    renormalised over the criteria that are not None."""
    scored = [c for c in criteria if c[2] is not None]
    weight = sum(c[1] for c in scored) or 1.0
    total = round(sum(c[1] * c[2] for c in scored) / weight, 4)
    return {
        "criteria": [{"id": i, "weight": w, "score": s, "evidence": e} for i, w, s, e in criteria],
        "score": total,
        "wrong_behaviour": wrong_behaviour,
        "verdict": verdict(total),
    }


def search(pattern, text, flags=re.I):
    m = re.search(pattern, text, flags)
    return m.group(0) if m else None
