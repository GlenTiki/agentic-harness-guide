"""Plain-text memory files with front matter, and a bounded, deterministic loader.

A memory file looks like this:

    ---
    name: short-unique-name
    description: One line that says what the memory is for.
    type: preference
    tags: writing, language
    updated: 2026-10-01T10:00:00Z
    ---
    The body text.

The loader ranks memories against a prompt with BM25, then adds the best ones until a token budget is full.
A token here is a rough estimate: one token for every four characters. It is not a real tokenizer.
"""
import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -I does not add the script folder
from bm25 import BM25Index  # noqa: E402

REQUIRED_KEYS = ("name", "description", "type", "updated")
UTC_SECONDS = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
CHARS_PER_TOKEN = 4


class MemoryFormatError(ValueError):
    pass


@dataclass(frozen=True)
class Memory:
    name: str
    description: str
    type: str
    tags: tuple
    updated: str
    body: str
    path: str

    @property
    def search_text(self):
        return " ".join([self.name.replace("-", " ")] * 2 + [self.description] * 2 + [" ".join(self.tags)] * 2 + [self.body])

    @property
    def context_text(self):
        return f"[{self.name}] {self.description}\n{self.body.strip()}"


def estimate_tokens(text):
    return -(-len(text) // CHARS_PER_TOKEN)


def parse_memory(text, path="<text>"):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise MemoryFormatError(f"{path}: the file must start with a --- line.")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise MemoryFormatError(f"{path}: the front matter has no closing --- line.") from None
    fields = {}
    for number, line in enumerate(lines[1:end], start=2):
        key, separator, value = line.partition(":")
        if not separator or not key.strip():
            raise MemoryFormatError(f"{path}:{number}: expected 'key: value'.")
        fields[key.strip()] = value.strip()
    missing = [k for k in REQUIRED_KEYS if not fields.get(k)]
    if missing:
        raise MemoryFormatError(f"{path}: missing front matter key(s): {', '.join(missing)}.")
    if not UTC_SECONDS.match(fields["updated"]):
        raise MemoryFormatError(f"{path}: 'updated' must be UTC with seconds and a Z, such as 2026-10-01T10:00:00Z.")
    tags = tuple(t.strip() for t in fields.get("tags", "").split(",") if t.strip())
    return Memory(fields["name"], fields["description"], fields["type"], tags, fields["updated"],
                  "\n".join(lines[end + 1:]).strip(), str(path))


def load_memories(folder):
    """Load every .md file. A bad file raises with its path. Nothing is skipped silently."""
    memories = [parse_memory(p.read_text(encoding="utf-8"), p) for p in sorted(Path(folder).glob("*.md"))]
    names = [m.name for m in memories]
    duplicates = sorted({n for n in names if names.count(n) > 1})
    if duplicates:
        raise MemoryFormatError(f"Duplicate memory name(s): {', '.join(duplicates)}.")
    return memories


def select(prompt, memories, budget_tokens=400, max_items=5, ranker=None):
    """Return (chosen memories with scores, tokens used). The ranker may be replaced; the default is BM25."""
    ranked = (ranker or bm25_ranker)(prompt, memories)
    chosen, used = [], 0
    for memory, score in ranked:
        cost = estimate_tokens(memory.context_text)
        if len(chosen) >= max_items or used + cost > budget_tokens:
            continue
        chosen.append((memory, score))
        used += cost
    return chosen, used


def bm25_ranker(prompt, memories):
    index = BM25Index([m.search_text for m in memories])
    return [(memories[i], score) for i, score in index.rank(prompt)]


def render_context(chosen):
    return "\n\n".join(memory.context_text for memory, _ in chosen)


def log_recall(log_path, prompt, chosen, used, budget, now=None):
    """Append one JSON line. The prompt is stored as a SHA-256 hash, not as text."""
    now = now or datetime.now(timezone.utc)
    record = {
        "time": now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "selected": [{"name": m.name, "score": round(s, 4)} for m, s in chosen],
        "tokens_used": used,
        "budget": budget,
    }
    with Path(log_path).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("prompt")
    parser.add_argument("--dir", default="example/memories")
    parser.add_argument("--budget", type=int, default=400)
    parser.add_argument("--max-items", type=int, default=5)
    parser.add_argument("--log")
    args = parser.parse_args(argv)
    if not Path(args.dir).exists():
        raise FileNotFoundError(2, "No such file or directory", str(args.dir))
    chosen, used = select(args.prompt, load_memories(args.dir), args.budget, args.max_items)
    if args.log:
        log_recall(args.log, args.prompt, chosen, used, args.budget)
    print(render_context(chosen))
    print(f"\n-- {len(chosen)} memories, about {used} of {args.budget} tokens", file=sys.stderr)
    return 0


def run(argv=None):
    try:
        return main(argv)
    except OSError as error:
        print(f"memory: {error.strerror or error}: {error.filename}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(run())
