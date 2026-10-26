#!/usr/bin/env python3
"""Exact binomial and Fisher computations for reading failure counts from few runs."""
import sys
from math import comb


def at_most(k, n, p):
    """Probability of k or fewer failures in n runs when each run fails with probability p."""
    return sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k + 1))


def fisher_one_sided(old_failures, old_runs, new_failures, new_runs):
    """Probability, with the failure total fixed, of the new prompt having this few failures or fewer by chance alone."""
    failures = old_failures + new_failures
    runs = old_runs + new_runs
    total = comb(runs, failures)
    return sum(comb(new_runs, i) * comb(old_runs, failures - i) for i in range(new_failures + 1)) / total


if __name__ == "__main__":
    old_failures, old_runs, new_failures, new_runs = (int(arg) for arg in sys.argv[1:5])
    rate = old_failures / old_runs
    print(f"old prompt: {old_failures} failures in {old_runs} runs (rate {rate:.2f})")
    print(f"new prompt: {new_failures} failures in {new_runs} runs")
    print(f"P({new_failures} or fewer failures in {new_runs} runs | true rate unchanged at {rate:.2f}) = {at_most(new_failures, new_runs, rate):.3f}")
    print(f"Fisher exact, one-sided: {fisher_one_sided(old_failures, old_runs, new_failures, new_runs):.3f}")
