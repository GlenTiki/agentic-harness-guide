#!/usr/bin/env python3
"""Show a stale memory note outranking a fresh one, find the conflict, and repair it in place. Standard library only.

Usage: python3 -I staleness_demo.py
The demo copies notes/ to a temporary folder, so the stored notes never change.
It uses the memory loader from examples/retrieval-eval/kit (BM25 ranking, no recency term).
"""
import shutil
import sys
import tempfile
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "retrieval-eval" / "kit"))
import memory  # noqa: E402

PROMPT = "Where is the staging environment deployed?"
REPAIR_TIME = "2026-10-26T09:00:00Z"


def shared_topic_pairs(memories):
    """Return pairs of notes with the same type and at least two shared tags. A heuristic: it finds candidates, not proof."""
    return [
        (a, b)
        for a, b in combinations(memories, 2)
        if a.type == b.type and len(set(a.tags) & set(b.tags)) >= 2
    ]


def repair_in_place(folder, keep_name, drop_name, description, body, now=REPAIR_TIME):
    """Rewrite the older note where it stands and delete the duplicate."""
    keep = next(m for m in memory.load_memories(folder) if m.name == keep_name)
    text = (
        f"---\nname: {keep.name}\ndescription: {description}\ntype: {keep.type}\ntags: {', '.join(keep.tags)}\n"
        f"updated: {now}\n---\n{body}\n"
    )
    Path(keep.path).write_text(text, encoding="utf-8")
    Path(folder, f"{drop_name}.md").unlink()


def show_ranking(folder, label):
    memories = memory.load_memories(folder)
    chosen, used = memory.select(PROMPT, memories)
    print(f"{label}: ranking for {PROMPT!r}")
    for position, (note, score) in enumerate(chosen, start=1):
        print(f"  {position}. {note.name:<15} score {score:.3f}  updated {note.updated}")
    print(f"  loaded {len(chosen)} notes, about {used} tokens")
    return chosen


def main():
    with tempfile.TemporaryDirectory() as scratch:
        folder = Path(scratch) / "notes"
        shutil.copytree(HERE / "notes", folder)
        chosen = show_ranking(folder, "before")
        print("\ntext the assistant receives:")
        print(memory.render_context(chosen))
        print("\nnotes that may contradict each other:")
        for a, b in shared_topic_pairs(memory.load_memories(folder)):
            print(f"  {a.name} (updated {a.updated}) and {b.name} (updated {b.updated})")
        repair_in_place(
            folder, "staging-host", "staging-moved",
            "Where the staging environment is deployed.",
            "Staging runs on the new platform. The old-cluster host was switched off. Deploy with the platform command.",
        )
        print()
        chosen = show_ranking(folder, "after the repair")
        print("\ntext the assistant receives:")
        print(memory.render_context(chosen))
    return 0


if __name__ == "__main__":
    sys.exit(main())
