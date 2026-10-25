"""Run one case for n trials in strict isolation and grade each reply.

python3 -I run.py --case C01-bills-total [--arm sonnet] [--n 5] [--max-calls 20] [--resolve]
Writes runs/<date>/<case>.jsonl (one line per trial) and runs/<date>/raw/ (verbatim replies and JSON envelopes)."""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import harness  # noqa: E402
from graders import REGISTRY  # noqa: E402
from graders.doi import crossref_resolver  # noqa: E402

CONCURRENCY = 2


def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


def grader_version(name):
    return f"{name} sha256 {sha256((HERE / 'graders' / (name + '.py')).read_text())[:16]}"


def plan(case, arm_filter, n_override, start=1):
    """Interleave arms (A,B,A,B...) so time-of-day variation is spread across arms."""
    arms = [a for a in case["arms"] if arm_filter in (None, a["id"])]
    counts = {a["id"]: (n_override or a["n"]) for a in arms}
    jobs = []
    for trial in range(start, start + max(counts.values())):
        for a in arms:
            if trial < start + counts[a["id"]]:
                jobs.append((a, trial))
    return jobs


def one_trial(case, arm, trial, day_dir, version, resolve):
    started = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    name = f"{case['id']}-{arm['id']}-t{trial:02d}"
    call = harness.run_claude(arm["prompt"], arm["model"])
    reply, model_reported, usage, error = harness.parse_json_result(call["stdout"])
    if call["returncode"] != 0 and not error:
        error = f"exit {call['returncode']}: {call['stderr'][:300]}"
    raw = day_dir / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    (raw / f"{name}.txt").write_text(harness.redact(reply))
    (raw / f"{name}.json").write_text(harness.redact(call["stdout"]))
    record = {
        "case_id": case["id"], "arm": arm["id"], "trial": trial, "started_utc": started,
        "model_requested": arm["model"], "model_reported": model_reported, "claude_code_version": version,
        "isolation": " ".join(harness.ISOLATION_FLAGS) + " (empty mktemp cwd)",
        "prompt_sha256": sha256(arm["prompt"]), "grader_version": grader_version(arm.get("grader", case["grader"])),
        "raw_output_path": str((raw / f"{name}.txt").relative_to(HERE)), "error": harness.redact(error) if error else None,
        "input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens"),
        "cache_read_input_tokens": usage.get("cache_read_input_tokens"),
        "cache_creation_input_tokens": usage.get("cache_creation_input_tokens"),
        "wall_seconds": call["wall_seconds"],
    }
    if error:
        record.update(criteria=[], score=None, wrong_behaviour=None, verdict="error")
        return record
    grade = REGISTRY[arm.get("grader", case["grader"])]
    arm_case = {**case, "expected": arm.get("expected")}
    graded = grade(reply, arm_case, resolver=crossref_resolver) if (resolve and case["grader"] == "doi") else grade(reply, arm_case)
    record.update({k: graded[k] for k in ("criteria", "score", "wrong_behaviour", "verdict", "wrong_headline", "extras") if k in graded})
    return record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--arm")
    ap.add_argument("--start", type=int, default=1, help="first trial number (for top-ups)")
    ap.add_argument("--n", type=int)
    ap.add_argument("--max-calls", type=int, required=True, help="hard stop: refuse to start if the plan exceeds it")
    ap.add_argument("--date", default=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"))
    ap.add_argument("--resolve", action="store_true", help="doi case: resolve DOIs against Crossref")
    args = ap.parse_args()

    case = json.loads((HERE / "cases" / f"{args.case}.json").read_text())
    if case["status"] != "ready":
        sys.exit(f"{args.case} has status {case['status']}, not ready")
    jobs = plan(case, args.arm, args.n, args.start)
    print(f"planned model calls: {len(jobs)} (max {args.max_calls}), concurrency {CONCURRENCY}", flush=True)
    if len(jobs) > args.max_calls:
        sys.exit("plan exceeds --max-calls; nothing run")

    day_dir = HERE / "runs" / args.date
    day_dir.mkdir(parents=True, exist_ok=True)
    version = harness.claude_version()
    out = day_dir / f"{args.case}.jsonl"
    with concurrent.futures.ThreadPoolExecutor(CONCURRENCY) as pool, out.open("a") as handle:
        futures = [pool.submit(one_trial, case, a, t, day_dir, version, args.resolve) for a, t in jobs]
        for future in concurrent.futures.as_completed(futures):
            record = future.result()
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            print(record["arm"], record["trial"], record["verdict"], record["score"], record["wrong_behaviour"],
                  record["wall_seconds"], record["error"] or "", flush=True)


if __name__ == "__main__":
    main()
