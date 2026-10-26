#!/usr/bin/env python3
"""Show how a gate can pass without proving anything. Subcommands: matrix, red-green, flaky."""
import os
import pathlib
import subprocess
import sys
import tempfile

IMPLEMENTATIONS = {
    "correct": "def vat_inclusive(net_cents, rate_percent):\n    return net_cents + net_cents * rate_percent // 100\n",
    "buggy": "def vat_inclusive(net_cents, rate_percent):\n    return net_cents + rate_percent\n",
    "stub": "def vat_inclusive(net_cents, rate_percent):\n    return 0\n",
}

TESTS = {
    "vacuous": (
        "import unittest\nfrom price import vat_inclusive\n\n\nclass Vat(unittest.TestCase):\n"
        "    def test_vat(self):\n        self.assertIsNotNone(vat_inclusive(10000, 23))\n"
    ),
    "real": (
        "import unittest\nfrom price import vat_inclusive\n\n\nclass Vat(unittest.TestCase):\n"
        "    def test_vat(self):\n        self.assertEqual(12300, vat_inclusive(10000, 23))\n"
    ),
}

SET_ORDER_CODE = "def first_tag(tags):\n    return next(iter(tags))\n"
SET_ORDER_TEST = (
    "import unittest\nfrom tags import first_tag\n\n\nclass Tags(unittest.TestCase):\n"
    "    def test_first_tag(self):\n        self.assertEqual('red', first_tag({'red', 'green', 'blue'}))\n"
)
SET_ORDER_FIXED = "def first_tag(tags):\n    return sorted(tags)[0]\n"
SET_ORDER_FIXED_TEST = SET_ORDER_TEST.replace("'red'", "'blue'")


def run_unittest(files, extra_env=None):
    with tempfile.TemporaryDirectory() as tmp:
        folder = pathlib.Path(tmp)
        for name, text in files.items():
            (folder / name).write_text(text)
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **(extra_env or {})}
        return subprocess.run(
            [sys.executable, "-m", "unittest", "-q", "test_price.py" if "test_price.py" in files else "test_tags.py"],
            cwd=folder, env=env, capture_output=True, text=True, check=False,
        )


def matrix():
    print(f"{'test':<9}{'implementation':<16}gate exit code")
    for test_name, test_text in TESTS.items():
        for impl_name, impl_text in IMPLEMENTATIONS.items():
            result = run_unittest({"price.py": impl_text, "test_price.py": test_text})
            print(f"{test_name:<9}{impl_name:<16}{result.returncode}")


def red_green():
    for impl_name in ("stub", "correct"):
        result = run_unittest({"price.py": IMPLEMENTATIONS[impl_name], "test_price.py": TESTS["real"]})
        failure = [line for line in result.stderr.splitlines() if line.startswith("AssertionError")]
        print(f"real test against {impl_name}: exit code {result.returncode}", *failure)


def flaky(seeds=range(10)):
    outcomes = []
    for seed in seeds:
        result = run_unittest({"tags.py": SET_ORDER_CODE, "test_tags.py": SET_ORDER_TEST}, {"PYTHONHASHSEED": str(seed)})
        outcomes.append(result.returncode)
    print("unsorted set, hash seeds 0 to 9, exit codes:", "".join(str(code) for code in outcomes))
    print("passes:", outcomes.count(0), "fails:", len(outcomes) - outcomes.count(0))
    fixed = [
        run_unittest({"tags.py": SET_ORDER_FIXED, "test_tags.py": SET_ORDER_FIXED_TEST}, {"PYTHONHASHSEED": str(s)}).returncode
        for s in seeds
    ]
    print("sorted, same seeds, exit codes:", "".join(str(code) for code in fixed))


if __name__ == "__main__":
    {"matrix": matrix, "red-green": red_green, "flaky": flaky}[sys.argv[1]]()
