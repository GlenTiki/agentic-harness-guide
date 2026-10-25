"""Re-grade stored raw replies with the current graders. No model calls.

The original file moves to runs/<date>/superseded/ (never deleted) and the re-graded records replace it.
python3 -I regrade.py runs/2026-10-25/C07-reviewer.jsonl"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from graders import REGISTRY  # noqa: E402
from run import grader_version  # noqa: E402


def regrade(path):
    path = Path(path)
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    case = json.loads((HERE / "cases" / f"{records[0]['case_id']}.json").read_text())
    arms = {a["id"]: a for a in case["arms"]}
    out = []
    for r in records:
        if r["verdict"] != "error":
            reply = (HERE / r["raw_output_path"]).read_text()
            arm_case = {**case, "expected": arms[r["arm"]].get("expected")}
            name = arms[r["arm"]].get("grader", case["grader"])
            graded = REGISTRY[name](reply, arm_case)
            for stale in ("wrong_headline", "extras"):
                r.pop(stale, None)
            r = {**r, **{k: graded[k] for k in ("criteria", "score", "wrong_behaviour", "verdict", "wrong_headline", "extras") if k in graded},
                 "grader_version": grader_version(name), "regraded": True}
        out.append(r)
    old = path.parent / "superseded"
    old.mkdir(exist_ok=True)
    path.rename(old / f"{path.stem}.v{len(list(old.glob(path.stem + '.v*')) ) + 1}.jsonl")
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        regrade(arg)
