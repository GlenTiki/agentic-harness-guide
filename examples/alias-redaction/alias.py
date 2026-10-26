#!/usr/bin/env python3
"""Alias personal data with stable tokens, keep the map local, restore on output. Synthetic teaching sketch."""
import re

BASELINE = {
    "EMAIL": re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"),
    "PHONE": re.compile(r"\+\d{2,3}(?: \d{2,4}){2,3}"),
}
INTERNAL = {
    "CASE": re.compile(r"\bCX-\d{5}-[A-Z]+\b"),
    "ACCOUNT": re.compile(r"\bACC/\d{4}/\d{6}\b"),
}
TOKEN = re.compile(r"\[[A-Z]+_\d+\]")


def alias(text, recognisers):
    if TOKEN.search(text):
        raise ValueError("the document already contains token-shaped text")
    mapping, seen = {}, {}
    spans = sorted(
        (m.start(), m.end(), kind) for kind, rx in recognisers.items() for m in rx.finditer(text)
    )
    out, cursor = [], 0
    for start, end, kind in spans:
        if start < cursor:
            continue
        value = text[start:end]
        if value not in seen:
            count = sum(1 for k in seen.values() if k.startswith(f"[{kind}_")) + 1
            seen[value] = f"[{kind}_{count}]"
            mapping[seen[value]] = value
        out.append(text[cursor:start])
        out.append(seen[value])
        cursor = end
    out.append(text[cursor:])
    return "".join(out), mapping


def restore(text, mapping):
    unresolved = [t for t in TOKEN.findall(text) if t not in mapping]
    for token, value in mapping.items():
        text = text.replace(token, value)
    return text, unresolved


DOCUMENT = (
    "Case CX-48213-ALPHA was opened by dana.whitfield@example.invalid (+44 20 5550 1234).\n"
    "Refund goes to account ACC/2291/004417. Chase CX-48213-ALPHA again if the account ACC/2291/004417 "
    "is still unpaid, and copy omar.reyes@example.invalid.\n"
)


def main():
    for label, recognisers in (("baseline", BASELINE), ("baseline plus internal", {**BASELINE, **INTERNAL})):
        masked, mapping = alias(DOCUMENT, recognisers)
        restored, unresolved = restore(masked, mapping)
        print(f"--- {label}: {len(mapping)} tokens, round trip {'ok' if restored == DOCUMENT else 'FAILED'}")
        print(masked, end="")
        leaked = [v for v in ("CX-48213-ALPHA", "ACC/2291/004417") if v in masked]
        print(f"internal identifiers still visible: {leaked}")


if __name__ == "__main__":
    main()
