#!/usr/bin/env python3
"""Count hard friction signals in a folder of agent session transcripts and write a Markdown report.

Usage: python3 insights.py <transcript folder> [--out <report.md>]

The script only reads the transcripts. It never changes them, and it sends nothing anywhere.
"""
import argparse
import json
import pathlib
import re
import sys
from dataclasses import dataclass, field

SIGNALS = ("interruption", "tool_error", "refusal")
SIGNAL_NAMES = {"interruption": "interruption", "tool_error": "failed tool call", "refusal": "refused permission"}
EXCERPT_CHARS = 160
EXCERPTS_PER_SESSION = 3
TOP_SESSIONS = 3

# Claude Code 2.1.323 writes this text as a user message when the person presses Escape.
CLAUDE_CODE_INTERRUPTION = "[Request interrupted by user"
# Claude Code 2.1.326 writes this text straight after a refused permission, as part of the same refusal.
CLAUDE_CODE_TOOL_USE_INTERRUPTION = "[Request interrupted by user for tool use]"

SECRET_NAME = r"\w*(?:password|passwd|secret|token|api_?key)\w*"
REDACTIONS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?(-----END [A-Z ]*PRIVATE KEY-----|$)", re.S), "<private key>"),
    (re.compile(r"(?<![A-Za-z0-9])(?:sk|pk|rk)[-_][A-Za-z0-9_-]{8,}"), "<secret>"),
    (re.compile(r"(?<![A-Za-z0-9])(?:ghp|gho|ghs|github_pat)_[A-Za-z0-9_]{10,}"), "<secret>"),
    (re.compile(r"(?<![A-Za-z0-9])xox[abprs]-[A-Za-z0-9-]{10,}"), "<secret>"),
    (re.compile(r"(?<![A-Za-z0-9])AKIA[0-9A-Z]{16}(?![A-Za-z0-9])"), "<secret>"),
    (re.compile(r"(?<![A-Za-z0-9])AIza[0-9A-Za-z_-]{20,}"), "<secret>"),
    (re.compile(r"(?<![A-Za-z0-9])eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}(?:\.[A-Za-z0-9_-]*)?"), "<secret>"),
    (re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{8,}", re.I), "Bearer <secret>"),
    (re.compile(r"((?:^|[^A-Za-z0-9])" + SECRET_NAME + r"[\"']?\s*[:=]\s*)(\"[^\"]*\"|'[^']*'|\S+)", re.I), r"\1<secret>"),
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "<email>"),
    (re.compile(r"/(?:Users|home)/[^/\s\"']+"), "<home>"),
]


@dataclass
class Session:
    name: str
    messages: int = 0
    counts: dict = field(default_factory=lambda: {s: 0 for s in SIGNALS})
    excerpts: list = field(default_factory=list)
    awaiting_redirect: bool = False
    previous_kind: str = ""

    @property
    def friction(self) -> int:
        return sum(self.counts.values())


@dataclass
class Event:
    session: str
    message_id: str
    kind: str
    text: str
    scope: str = ""


def redact(text: str) -> str:
    for pattern, replacement in REDACTIONS:
        text = pattern.sub(replacement, text)
    return text


def excerpt(text: str) -> str:
    flat = " ".join(redact(text).split())
    return flat if len(flat) <= EXCERPT_CHARS else flat[: EXCERPT_CHARS - 3] + "..."


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(text_of(block.get("text", block.get("content", ""))) for block in content if isinstance(block, dict))
    return ""


def normalised_events(record: dict, default_session: str) -> list:
    """One line of the documented normalised format: {"session", "id", "event", "text"}."""
    session = str(record.get("session") or default_session)
    return [Event(session, str(record["id"]), record["event"], str(record.get("text", "")), scope=session)]


def user_text_kind(text: str) -> str:
    if text.startswith(CLAUDE_CODE_TOOL_USE_INTERRUPTION):
        return "tool_use_interruption"
    return "interruption" if text.startswith(CLAUDE_CODE_INTERRUPTION) else "message"


def claude_code_events(record: dict) -> list:
    """One user or assistant line of a Claude Code transcript. The format is not a documented API.

    A forked session copies earlier lines into a new file under a new session id, with the same uuid,
    so the uuid alone is the message id."""
    session = str(record.get("sessionId") or "unknown")
    message_id = str(record.get("uuid") or (record.get("message") or {}).get("id") or "")
    content = (record.get("message") or {}).get("content")
    if record["type"] == "assistant":
        return [Event(session, message_id, "message", "", scope="claude-code")]
    if isinstance(content, str):
        return [Event(session, message_id, user_text_kind(content), content, scope="claude-code")]
    refused = bool(record.get("toolDenialKind")) or (record.get("permissionDecision") or {}).get("decision") == "reject"
    events = []
    for block in content or []:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_result" and block.get("is_error"):
            kind = "refusal" if refused else "tool_error"
            events.append(Event(session, message_id, kind, text_of(block.get("content")), scope="claude-code"))
        elif block.get("type") == "text":
            text = block.get("text", "")
            events.append(Event(session, message_id, user_text_kind(text), text, scope="claude-code"))
    return events or [Event(session, message_id, "message", "", scope="claude-code")]


def events_in_line(line: str, default_session: str) -> list | None:
    record = json.loads(line)
    if not isinstance(record, dict):
        return None
    if "event" in record and "id" in record:
        return normalised_events(record, default_session)
    if record.get("type") in ("user", "assistant") and isinstance(record.get("message"), dict):
        if record.get("isMeta"):
            return []
        return claude_code_events(record)
    return []


def analyse(folder: pathlib.Path) -> dict:
    sessions, seen = {}, set()
    stats = {"files": 0, "lines": 0, "duplicates": 0, "unreadable": 0}
    for path in sorted(folder.rglob("*.jsonl")):
        stats["files"] += 1
        with path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if not line.strip():
                    continue
                stats["lines"] += 1
                try:
                    events = events_in_line(line, path.stem)
                except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
                    events = None
                if events is None:
                    stats["unreadable"] += 1
                    continue
                if not events:
                    continue
                key = (events[0].scope, events[0].message_id)
                if events[0].message_id and key in seen:
                    stats["duplicates"] += 1
                    continue
                seen.add(key)
                for event in events:
                    record_event(sessions.setdefault(event.session, Session(event.session)), event)
    return {"sessions": sessions, "stats": stats}


def record_event(session: Session, event: Event) -> None:
    previous, session.previous_kind = session.previous_kind, event.kind
    if event.kind == "tool_use_interruption":
        if previous == "refusal":
            session.awaiting_redirect = True
            return
        event = Event(event.session, event.message_id, "interruption", event.text, event.scope)
    if event.kind not in SIGNALS:
        session.messages += 1
        if session.awaiting_redirect and event.text.strip():
            add_excerpt(session, "next user message after an interruption", event.text)
            session.awaiting_redirect = False
        return
    session.counts[event.kind] += 1
    if event.kind == "interruption":
        session.awaiting_redirect = True
    else:
        add_excerpt(session, SIGNAL_NAMES[event.kind], event.text)


def add_excerpt(session: Session, label: str, text: str) -> None:
    if len(session.excerpts) < EXCERPTS_PER_SESSION:
        session.excerpts.append((label, excerpt(text)))


def report(result: dict) -> str:
    sessions = sorted(result["sessions"].values(), key=lambda s: (-s.friction, s.name))
    stats = result["stats"]
    totals = {signal: sum(s.counts[signal] for s in sessions) for signal in SIGNALS}
    lines = [
        "# Insights report",
        "",
        f"Files read: {stats['files']}. Lines read: {stats['lines']}. Duplicate messages skipped: {stats['duplicates']}. "
        f"Unreadable lines: {stats['unreadable']}.",
        "",
        "## Totals",
        "",
        "| Signal | Count |",
        "| --- | --- |",
    ]
    lines += [f"| {SIGNAL_NAMES[signal]} | {totals[signal]} |" for signal in SIGNALS]
    lines += [f"| all friction | {sum(totals.values())} |", "", "## Sessions", ""]
    lines += ["| Session | Messages | Interruptions | Failed tool calls | Refusals | Friction |"]
    lines += ["| --- | --- | --- | --- | --- | --- |"]
    for s in sessions:
        c = s.counts
        lines.append(f"| {s.name} | {s.messages} | {c['interruption']} | {c['tool_error']} | {c['refusal']} | {s.friction} |")
    lines += ["", "## Top sessions by friction", ""]
    top = [s for s in sessions if s.friction][:TOP_SESSIONS]
    if not top:
        lines += ["No friction signals found.", ""]
    for rank, s in enumerate(top, 1):
        lines += [f"### {rank}. {s.name} (friction {s.friction})", ""]
        lines += [f"- {label}: \"{text}\"" for label, text in s.excerpts]
        lines.append("")
    lines += [
        "## Not counted",
        "",
        "Corrections in the wording of a message are not counted. A rule that guesses them from words has not been "
        "checked against real examples.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description="Count friction signals in agent session transcripts.")
    parser.add_argument("folder", type=pathlib.Path)
    parser.add_argument("--out", type=pathlib.Path, help="write the Markdown report here instead of printing it")
    args = parser.parse_args(argv)
    folder = args.folder.resolve()
    if not folder.is_dir():
        print(f"not a folder: {args.folder}", file=sys.stderr)
        return 2
    text = report(analyse(folder))
    if args.out is None:
        sys.stdout.write(text)
        return 0
    out = args.out.resolve()
    if out == folder or folder in out.parents:
        print("refusing to write the report inside the transcript folder", file=sys.stderr)
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"report written: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
