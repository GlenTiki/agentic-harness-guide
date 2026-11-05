#!/usr/bin/env python3
"""Compare a model judge with human labels: raw agreement, Cohen's kappa and failure recall, against a criterion set in advance."""
import csv
import sys


def read_labels(path):
    with open(path, newline="") as handle:
        return [(row["human"], row["judge"]) for row in csv.DictReader(handle)]


def agreement(pairs):
    return sum(human == judge for human, judge in pairs) / len(pairs)


def cohen_kappa(pairs):
    n = len(pairs)
    observed = agreement(pairs)
    labels = {label for pair in pairs for label in pair}
    expected = sum((sum(h == label for h, _ in pairs) / n) * (sum(j == label for _, j in pairs) / n) for label in labels)
    if expected == 1:
        raise ValueError("kappa is undefined when both raters use one label for every case")
    return (observed - expected) / (1 - expected)


def failure_recall(pairs):
    judged = [judge for human, judge in pairs if human == "fail"]
    return sum(judge == "fail" for judge in judged) / len(judged)


def verdict(pairs, min_kappa, min_failure_recall):
    kappa, recall = cohen_kappa(pairs), failure_recall(pairs)
    return kappa >= min_kappa and recall >= min_failure_recall


def report(pairs, min_kappa, min_failure_recall, out=sys.stdout):
    kappa, recall = cohen_kappa(pairs), failure_recall(pairs)
    passed = verdict(pairs, min_kappa, min_failure_recall)
    out.write(f"cases {len(pairs)}\n")
    out.write(f"raw agreement {agreement(pairs):.3f}\n")
    out.write(f"kappa {kappa:.3f} (criterion at least {min_kappa})\n")
    out.write(f"failures caught {recall:.3f} (criterion at least {min_failure_recall})\n")
    out.write(f"judge {'accepted' if passed else 'rejected'}\n")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(report(read_labels(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])))
