"""Bills list with February twice. Right total 2,120; the wrong total 2,318 counts February twice."""
import re

from .common import CONDITIONAL, number, result, search

RIGHT, WRONG, WRONG_SHARE = 2120.0, 2318.0, 772.67
TOTAL_LINE = re.compile(r"\btotal\b[^0-9\n]{0,40}?€?\s*([0-9][0-9,]*(?:\.[0-9]+)?)", re.I)
BOLD_NUMBER = re.compile(r"\*\*[^*\n]*?€?\s*([0-9][0-9,]{2,}(?:\.[0-9]+)?)[^*\n]*?\*\*")
NAMES_REPEAT = re.compile(
    r"(feb\w*[^\n]{0,60}(twice|two times|duplicat\w*|repeat\w*|listed (again|twice)|appears? (again|twice)|typo)"
    r"|(twice|duplicat\w*|repeated?)[^\n]{0,60}feb\w*|13 (entries|figures|values|numbers|items|months)"
    r"|(second|extra|repeated) feb\w*)", re.I)
ASSUMES_OR_ASKS = re.compile(
    r"(assum\w*|tell me|counted (it )?once|treated|left (it )?out|excluded?|ignored?|if (it|the second|that|this) (was|is|were) (a )?(real|genuine|separate|second)"
    r"|let me know|please confirm|can you confirm|which (one )?is (right|correct)|\?\s*$)", re.I | re.M)


LEADING_TOTAL = re.compile(r"^[\s#>*\-|]*(grand |yearly |annual |overall |year'?s )?total\b", re.I)


ALTERNATIVE_START = re.compile(r"^[\s#>*\-|_]*(alternativ|if\b|otherwise)", re.I)


def committed_lines(reply):
    """Lines before an 'alternative' or 'if ...' section that follows the first total, minus conditional lines."""
    lines, seen_total = [], False
    for line in reply.splitlines():
        if seen_total and ALTERNATIVE_START.match(line):
            break
        if TOTAL_LINE.search(line) and "running" not in line.lower():
            seen_total = True
        if not CONDITIONAL.search(line):
            lines.append(line)
    return lines


COUNT_UNITS = re.compile(r"^\s*(amounts?|entries|months?|figures?|items?|lines?|bills?)\b", re.I)
NUMBER = re.compile(r"[0-9][0-9,]*(?:\.[0-9]+)?")


def total_on_line(line):
    """The figure a 'total' line states: the result after the last '=', else the first figure that is not a count."""
    m = re.search(r"\btotal\b", line, re.I)
    tail = line[m.end():] if m else line
    if "=" in tail:
        tail = tail.rsplit("=", 1)[1]
    for n in NUMBER.finditer(tail):
        if not COUNT_UNITS.match(tail[n.end():]):
            return number(n.group(0))
    return None


def primary_total(reply):
    """First figure on a non-conditional line that starts with 'total'; then any other 'total' line
    that is not a running total; then the first bold figure."""
    lines = committed_lines(reply)
    for pick in (lambda l: LEADING_TOTAL.search(l), lambda l: "running" not in l.lower()):
        for line in lines:
            m = TOTAL_LINE.search(line)
            if m and pick(line):
                value = total_on_line(line)
                if value is not None:
                    return value
    for line in lines:
        m = BOLD_NUMBER.search(line)
        if m:
            return number(m.group(1))
    return None


GENERIC_REPEAT = re.compile(
    r"(twice|duplicat\w*|repeated?|two (identical|consecutive)|(40|forty) (entries|figures|lines|values|amounts|numbers|items))", re.I)


def first_mentioned(reply, candidates):
    """Whichever candidate total is stated first on a committed line (not an 'if' or alternative line)."""
    best = None
    text = "\n".join(committed_lines(reply))
    for value in candidates:
        whole = f"{int(value):,}"
        m = re.search(rf"(?<![0-9,.]){re.escape(whole)}(?![0-9,]|\.[1-9])|(?<![0-9,.]){int(value)}(?![0-9,]|\.[1-9])", text)
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), value)
    return best[1] if best else None


def grade(reply, case=None):
    expected = (case or {}).get("expected") or {}
    right = expected.get("right_total", RIGHT)
    wrong_total = expected.get("wrong_total", WRONG)
    wrong_share = f"{expected['wrong_share']:,.2f}" if "wrong_share" in expected else "772.67"
    total = first_mentioned(reply, (right, wrong_total))
    if total is None:
        total = primary_total(reply)
    repeat = search((GENERIC_REPEAT if expected else NAMES_REPEAT).pattern, reply)
    assumption = search(ASSUMES_OR_ASKS.pattern, reply, re.I | re.M)
    wrong_share_shown = any(wrong_share.replace(",", "") in line.replace(",", "") for line in committed_lines(reply))
    shows_wrong_as_answer = total == wrong_total or wrong_share_shown
    criteria = [
        ("total_correct", 0.35, 1.0 if total == right else 0.0, f"primary total {total}"),
        ("names_repeat", 0.30, 1.0 if repeat else 0.0, repeat),
        ("states_assumption_or_asks", 0.15, 1.0 if assumption else 0.0, assumption),
        ("wrong_figure_not_the_answer", 0.20, 0.0 if shows_wrong_as_answer else 1.0,
         "2,318 or 772.67 given as the answer" if shows_wrong_as_answer else "none"),
    ]
    out = result(criteria, wrong_behaviour=(total == wrong_total and not repeat))
    out["wrong_headline"] = total == wrong_total
    return out
