#!/usr/bin/env python3
"""One-function seam between your code and a model, plus a runner that scores any client on your own cases."""
import json
import sys

LABELS = ("urgent", "routine")


def classify(text, client):
    """Ask a client for a label. The client is anything with a complete(prompt) -> str method."""
    reply = client.complete(f"Answer with one word, urgent or routine.\n\n{text}").strip().lower()
    if reply not in LABELS:
        raise ValueError(f"unexpected reply: {reply!r}")
    return reply


def score(client, cases):
    right, bad_replies = 0, 0
    for text, expected in cases:
        try:
            right += classify(text, client) == expected
        except ValueError:
            bad_replies += 1
    return {"right": right, "bad_replies": bad_replies, "total": len(cases)}


class FakeClient:
    """Answers from a fixed table and counts calls. Stands in for any model during tests."""

    def __init__(self, answers, default="routine"):
        self.answers, self.default, self.calls = answers, default, 0

    def complete(self, prompt):
        self.calls += 1
        text = prompt.split("\n\n", 1)[1]
        return self.answers.get(text, self.default)


CASES = [
    ("Fridge alarm is sounding", "urgent"),
    ("Please update the opening hours", "routine"),
    ("Card machine is down at the till", "urgent"),
    ("Invoice 114 attached", "routine"),
    ("Supplier says the delivery is a day late", "routine"),
    ("Water is coming through the stockroom ceiling", "urgent"),
]


def demo(out=sys.stdout):
    small = FakeClient({"Fridge alarm is sounding": "urgent"})
    large = FakeClient({text: label for text, label in CASES})
    chatty = FakeClient({}, default="I think this is urgent!")
    tiers = {"small-fake": small, "large-fake": large, "chatty-fake": chatty}
    for name, client in tiers.items():
        out.write(f"{name}: {json.dumps(score(client, CASES))} calls={client.calls}\n")


if __name__ == "__main__":
    demo()
