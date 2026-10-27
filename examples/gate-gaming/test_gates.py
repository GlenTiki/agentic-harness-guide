import pathlib
import subprocess
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent


def run(command):
    return subprocess.run([sys.executable, str(HERE / "gates.py"), command], capture_output=True, text=True, timeout=120, check=True).stdout


class Gates(unittest.TestCase):
    def test_vacuous_test_passes_every_implementation_and_real_test_does_not(self):
        rows = [line.split() for line in run("matrix").splitlines()[1:]]
        self.assertEqual(
            rows,
            [["vacuous", "correct", "0"], ["vacuous", "buggy", "0"], ["vacuous", "stub", "0"],
             ["real", "correct", "0"], ["real", "buggy", "1"], ["real", "stub", "1"]],
        )

    def test_real_test_is_red_before_green(self):
        lines = run("red-green").splitlines()
        self.assertEqual(lines[0], "real test against stub: exit code 1 AssertionError: 12300 != 0")
        self.assertEqual(lines[1], "real test against correct: exit code 0")

    def test_set_order_test_is_flaky_and_the_sorted_one_is_not(self):
        lines = run("flaky").splitlines()
        codes = lines[0].rsplit(": ", 1)[1]
        self.assertEqual(set(codes), {"0", "1"})
        self.assertEqual(lines[2], "sorted, same seeds, exit codes: 0000000000")

    def test_sorted_version_passes_the_unchanged_test_under_every_seed(self):
        sys.path.insert(0, str(HERE))
        import gates

        codes = [
            gates.run_unittest({"tags.py": gates.SET_ORDER_FIXED, "test_tags.py": gates.SET_ORDER_TEST}, {"PYTHONHASHSEED": str(seed)}).returncode
            for seed in range(10)
        ]
        self.assertEqual(codes, [0] * 10)
        self.assertFalse(hasattr(gates, "SET_ORDER_FIXED_TEST"))


if __name__ == "__main__":
    unittest.main()
