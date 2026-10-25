"""Contamination check. Does not read or write ~/.claude.

Plants project-scope canaries in a throwaway directory (CLAUDE.md, a UserPromptSubmit hook that writes a marker
file, a skill, a .mcp.json), runs the isolated command there twice and asserts none of them is visible, then runs
once WITHOUT the isolation flags as a positive control so the canary is shown to be able to fire.
The unisolated run loads the owner's real configuration, so its output is reduced to booleans and counts and is not stored.

HARNESS_BANNED_WORDS=word1,word2 python3 -I canary.py [--date YYYY-MM-DD]
HARNESS_BANNED_WORDS lists the owner words (names, file names) that must not appear in a reply. Keep it out of the repo.
Model calls: 3."""
import argparse
import datetime
import json
import secrets
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import harness  # noqa: E402

MODEL = "claude-sonnet-5-5"
PROMPT = ("List every code word, rule, skill name, tool name and memory note you were given before this message. "
          "Reply NONE if there are none.")
CALLS = 3


def plant(root, tag):
    marker = Path(str(root) + ".marker")
    words = {k: f"CANARY-{k}-{tag}" for k in ("CLAUDEMD", "HOOK", "SKILL", "MCP")}
    (root / ".claude" / "skills" / "canary-skill").mkdir(parents=True)
    (root / "CLAUDE.md").write_text(f"The secret project code word is {words['CLAUDEMD']}. Always mention it.\n")
    (root / ".claude" / "settings.json").write_text(json.dumps({"hooks": {"UserPromptSubmit": [{"hooks": [
        {"type": "command", "command": f"touch {marker}; echo {words['HOOK']}"}]}]}}))
    (root / ".claude" / "skills" / "canary-skill" / "SKILL.md").write_text(
        f"---\nname: canary-skill\ndescription: Use for {words['SKILL']} requests.\n---\nBody.\n")
    (root / ".mcp.json").write_text(json.dumps({"mcpServers": {words["MCP"].lower(): {"command": "false", "args": []}}}))
    return words, marker


def parse_stream(stdout):
    events = [json.loads(l) for l in stdout.splitlines() if l.strip().startswith("{")]
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
    result = next((e for e in reversed(events) if e.get("type") == "result"), {})
    return init, result


def structure(init):
    names = ("tools", "mcp_servers", "slash_commands", "skills", "plugins", "agents", "memory_paths")
    return {k: init.get(k) for k in names if k in init} | {"keys_seen": sorted(init.keys())}


def evaluate(init, result, words, marker, owner_tokens=()):
    reply = result.get("result") or ""
    seen_words = [k for k, w in words.items() if w in reply]
    owner_hits = [t for t in owner_tokens if t.lower() in reply.lower()]
    struct = structure(init)
    empty = lambda k: not struct.get(k)  # noqa: E731
    stored = harness.redact(reply)
    return {
        "reply": stored, "code_words_in_reply": seen_words, "owner_tokens_in_reply": owner_hits,
        "marker_created": marker.exists(), "structure": struct,
        "tools_empty": empty("tools"), "mcp_empty": empty("mcp_servers"), "skills_empty": empty("skills"),
        "slash_commands": struct.get("slash_commands"), "models": list((result.get("modelUsage") or {}).keys()),
    }


def run_one(label, isolated, tag, owner_tokens, extra=()):
    root = Path(tempfile.mkdtemp(prefix="ahg-canary."))
    words, marker = plant(root, tag)
    call = harness.run_claude(PROMPT, MODEL, "stream-json", isolated, cwd=str(root), extra=extra)
    init, result = parse_stream(call["stdout"])
    out = evaluate(init, result, words, marker, owner_tokens) | {"label": label, "isolated": isolated, "returncode": call["returncode"],
                                                   "wall_seconds": call["wall_seconds"], "stderr": harness.redact(call["stderr"][:300])}
    out["is_error"] = bool(result.get("is_error")) or not result
    marker.unlink(missing_ok=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-control", action="store_true", help="skip the unisolated positive control (2 calls instead of 3)")
    ap.add_argument("--tag", default="")
    ap.add_argument("--date", default=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"))
    args = ap.parse_args()
    print(f"planned model calls: {2 if args.no_control else CALLS}", flush=True)
    version = harness.claude_version()
    tag = secrets.token_hex(4)
    owner_tokens = harness.banned_words()
    runs = [run_one("isolated-1", True, tag, owner_tokens), run_one("isolated-2", True, tag, owner_tokens)]
    control = None if args.no_control else run_one("positive-control-unisolated", False, tag, owner_tokens, extra=("--tools", ""))
    leak = [r["label"] for r in runs if r["code_words_in_reply"] or r["marker_created"] or r["owner_tokens_in_reply"]
            or not r["tools_empty"] or not r["mcp_empty"] or not r["skills_empty"]]
    fires = None if control is None else bool(control["code_words_in_reply"] or control["marker_created"])
    summary = {"date": args.date, "claude_code": version, "model_requested": MODEL, "flags": harness.ISOLATION_FLAGS,
               "isolated_runs": runs, "leaks": leak, "canary_can_fire": fires,
               "positive_control": None if control is None else {k: control[k] for k in ("code_words_in_reply", "marker_created", "tools_empty",
                                                          "mcp_empty", "skills_empty", "models", "is_error", "returncode")}
               | {"owner_tokens_in_reply_count": len(control["owner_tokens_in_reply"]),
                  "note": "unisolated run loads the owner's configuration; output reduced to booleans and counts"},
               "verdict": "clean" if (not leak and (fires or control is None) and not any(r["is_error"] for r in runs)) else "NOT CLEAN"}
    out_dir = HERE / "runs" / args.date / ("canary" + args.tag)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "canary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: summary[k] for k in ("leaks", "canary_can_fire", "verdict")}, indent=2))
    return 0 if summary["verdict"] == "clean" else 1


if __name__ == "__main__":
    sys.exit(main())
