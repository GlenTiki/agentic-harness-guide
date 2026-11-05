"""Re-run a command when a file in a directory changes. Standard library only."""
import argparse
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def snapshot(directory: Path) -> dict[str, int]:
    return {
        str(path): path.stat().st_mtime_ns
        for path in sorted(directory.rglob("*"))
        if path.is_file() and "__pycache__" not in path.parts
    }


def run_command(command: list[str], directory: Path, now=utc_now, out=sys.stdout) -> int:
    result = subprocess.run(command, cwd=directory, capture_output=True, text=True)
    verdict = "PASS" if result.returncode == 0 else "FAIL"
    print(f"{verdict} {now()} exit={result.returncode}", file=out, flush=True)
    detail = (result.stdout + result.stderr).strip()
    if result.returncode != 0 and detail:
        print(detail, file=out, flush=True)
    return result.returncode


def watch(directory, command, interval=0.2, debounce=0.3, max_runs=None, now=utc_now, sleep=time.sleep, out=sys.stdout):
    runs = 0
    seen = snapshot(directory)
    run_command(command, directory, now, out)
    runs += 1
    while max_runs is None or runs < max_runs:
        sleep(interval)
        if snapshot(directory) == seen:
            continue
        sleep(debounce)  # let a burst of saves settle, then compare once more
        seen = snapshot(directory)
        run_command(command, directory, now, out)
        runs += 1
    return runs


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-run a command whenever a file in DIRECTORY changes.")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--interval", type=float, default=0.2, help="seconds between polls")
    parser.add_argument("--debounce", type=float, default=0.3, help="seconds to wait for saves to settle")
    parser.add_argument("--max-runs", type=int, default=None, help="stop after this many runs")
    parser.add_argument("command", nargs="+", help="command to run, after --")
    args = parser.parse_args()
    watch(args.directory, args.command, args.interval, args.debounce, args.max_runs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
