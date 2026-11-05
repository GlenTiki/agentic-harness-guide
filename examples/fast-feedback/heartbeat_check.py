"""Exit 1 when the newest event in a JSONL log is older than a limit. Standard library only."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

OK, STALE, BROKEN = 0, 1, 2


def parse_time(text: str) -> datetime:
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def newest_event_time(log: Path) -> str:
    times = []
    for number, line in enumerate(log.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            times.append(parse_time(json.loads(line)["t"]))
        except (ValueError, KeyError, TypeError) as error:
            raise ValueError(f"line {number} is not an event with a UTC time in t: {error!r}") from error
    if not times:
        raise ValueError("the log holds no events")
    return max(times).strftime("%Y-%m-%dT%H:%M:%SZ")


def check(log: Path, limit_seconds: int, now: datetime, out=sys.stdout, err=sys.stderr) -> int:
    try:
        newest = newest_event_time(log)
    except (OSError, ValueError) as error:
        print(f"BROKEN: {log}: {error}", file=err)
        return BROKEN
    if (now - parse_time(newest)).total_seconds() > limit_seconds:
        print(f"STALE: last event {newest}, limit {limit_seconds}s", file=out)
        return STALE
    print(f"OK: last event {newest}, limit {limit_seconds}s", file=out)
    return OK


def main() -> int:
    parser = argparse.ArgumentParser(description="Go red when the newest event in LOG is too old.")
    parser.add_argument("log", type=Path)
    parser.add_argument("--limit", type=int, required=True, help="maximum age in seconds")
    parser.add_argument("--now", help="fixed UTC time, for tests (YYYY-MM-DDTHH:MM:SSZ)")
    args = parser.parse_args()
    now = parse_time(args.now) if args.now else datetime.now(timezone.utc)
    return check(args.log, args.limit, now)


if __name__ == "__main__":
    sys.exit(main())
