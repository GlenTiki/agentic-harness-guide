"""Shared helpers: build the isolated claude command and run one call."""
import json
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
ACCOUNT_EMAIL = "[account email]"


def banned_words():
    """Owner-specific words that must not appear in the repo, from HARNESS_BANNED_WORDS (comma-separated)."""
    return tuple(w.strip() for w in os.environ["HARNESS_BANNED_WORDS"].split(",") if w.strip())


def redact(text):
    """Replace every email-shaped string before anything is written to disk."""
    return EMAIL.sub(ACCOUNT_EMAIL, text)


ISOLATION_FLAGS = [
    "--safe-mode",
    "--restricted",
    "--tools", "",
    "--strict-mcp-config",
    "--disable-slash-commands",
    "--setting-sources", "",
    "--no-session-persistence",
]
GIT_VARS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")


def build_command(model, output_format="json", isolated=True, extra=()):
    cmd = ["nice", "-n", "10", "claude", "-p", "--model", model, "--output-format", output_format]
    if output_format == "stream-json":
        cmd.append("--verbose")
    if isolated:
        cmd += ISOLATION_FLAGS
    return cmd + list(extra)


def clean_env():
    return {k: v for k, v in os.environ.items() if k not in GIT_VARS}


def run_claude(prompt, model, output_format="json", isolated=True, cwd=None, extra=(), timeout=300):
    """Run one call with the prompt on stdin. Returns dict with stdout, stderr, returncode, wall_seconds."""
    own_dir = cwd is None
    workdir = tempfile.mkdtemp(prefix="ahg-eval.") if own_dir else cwd
    started = time.time()
    try:
        proc = subprocess.run(
            build_command(model, output_format, isolated, extra),
            input=prompt, capture_output=True, text=True, cwd=workdir, env=clean_env(), timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": f"timeout after {timeout}s", "returncode": -1,
                "wall_seconds": round(time.time() - started, 2), "cwd": workdir}
    wall = round(time.time() - started, 2)
    if own_dir:
        try:
            os.rmdir(workdir)
        except OSError:
            pass
    return {"stdout": proc.stdout, "stderr": proc.stderr, "returncode": proc.returncode, "wall_seconds": wall,
            "cwd": workdir}


def parse_json_result(stdout):
    """Parse --output-format json. Returns (reply_text, model_reported, usage, error)."""
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return "", None, {}, f"unparseable output: {exc}"
    if isinstance(data, list):
        data = next((d for d in reversed(data) if d.get("type") == "result"), {})
    models = list((data.get("modelUsage") or {}).keys())
    error = data.get("result") if data.get("is_error") else None
    return data.get("result") or "", ",".join(models) or None, data.get("usage") or {}, error


def claude_version():
    out = subprocess.run(["claude", "--version"], capture_output=True, text=True, env=clean_env())
    return out.stdout.strip()


def repo_dir():
    return Path(__file__).resolve().parent
