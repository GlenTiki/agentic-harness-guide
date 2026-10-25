"""Fail if any file under this folder holds an email-shaped string or a banned word.

HARNESS_BANNED_WORDS=word1,word2 python3 -I sweep.py

HARNESS_BANNED_WORDS lists the client and employer names to keep out of the repo. Keep the list itself out of the repo."""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from harness import EMAIL, banned_words  # noqa: E402


def banned_pattern(words):
    return re.compile(r"\b(" + "|".join(re.escape(w) for w in words) + r")\b", re.I) if words else None


def sweep(root, words=()):
    banned = banned_pattern(words)
    found = []
    for path in sorted(Path(root).rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        for number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
            if EMAIL.search(line) or (banned and banned.search(line)):
                found.append(f"{path}:{number}")
    return found


if __name__ == "__main__":
    hits = sweep(HERE, banned_words())
    print("\n".join(hits) or "clean")
    sys.exit(1 if hits else 0)
