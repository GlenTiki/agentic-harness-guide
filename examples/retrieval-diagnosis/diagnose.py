#!/usr/bin/env python3
"""Diagnose retrieval failure on the guide's 44 notes and 34 queries. Standard library only.

Usage: python3 -I diagnose.py SECTION
SECTION: classify, identifier, paraphrase, fusion, floor, index
BM25 and the lexical similarity run live. The dense (embedding) results are read from the stored outputs
in examples/retrieval-eval/outputs/, because no embedding model is installed for an offline run.
"""
import json
import math
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL = HERE.parent / "retrieval-eval"
sys.path.insert(0, str(EVAL / "kit"))
sys.path.insert(0, str(HERE))
import memory  # noqa: E402
from bm25 import BM25Index, tokenize  # noqa: E402
from vector_index import IndexMismatch, load_index, save_index  # noqa: E402

K = 3
POOL = 10
RRF_K = 60
OFF_TOPIC = [
    "What is the capital of Peru?", "Which planet is the largest?", "How do I bake sourdough bread?",
    "Who won the match last night?", "What is the best way to make pasta?", "Is the sky blue on Mars?",
    "Where do penguins live?", "What time does the museum open?",
]
FLOORS = [0.05, 0.10, 0.15, 0.20]


def load_eval():
    memories = memory.load_memories(EVAL / "evalset" / "memories")
    queries = json.loads((EVAL / "evalset" / "queries.json").read_text())["queries"]
    return memories, queries


def bm25_names(memories, query):
    return [m.name for m, _ in memory.bm25_ranker(query, memories)]


def stored_top3(system):
    """Read the top three note names for each query from a stored output file."""
    pending, result = None, {}
    for line in (EVAL / "outputs" / f"{system}.txt").read_text().splitlines():
        if line.startswith(("HIT", "MISS")):
            pending = line.split(" | ", 1)[1]
        elif pending and "top3=" in line:
            result[pending] = json.loads(re.search(r"top3=(\[.*?\])", line).group(1).replace("'", '"'))
            pending = None
    return result


def failure_kind(names, expected):
    """ok: a correct note is in the top K. ranked wrong: it is in the pool but below K. retrieved wrong: it is not in the pool."""
    positions = [names.index(n) for n in expected if n in names]
    if positions and min(positions) < K:
        return "ok"
    return "ranked wrong" if positions and min(positions) < POOL else "retrieved wrong"


def reciprocal_rank_fusion(rankings, k=RRF_K):
    scores = Counter()
    for ranking in rankings:
        for rank, name in enumerate(ranking, start=1):
            scores[name] += 1 / (k + rank)
    return sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))


def tfidf_similarity(memories):
    """Cosine similarity between a query and each note, using BM25's idf weights. Bounded between 0 and 1."""
    index = BM25Index([m.search_text for m in memories])

    def vector(text):
        return {t: (1 + math.log(n)) * index.idf(t) for t, n in Counter(tokenize(text)).items()}

    def cosine(a, b):
        norm = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
        return sum(v * b.get(t, 0.0) for t, v in a.items()) / norm if norm else 0.0

    vectors = [vector(m.search_text) for m in memories]

    def best(query):
        q = vector(query)
        return max(((cosine(q, v), m.name) for v, m in zip(vectors, memories)))

    return best


def section_classify():
    memories, queries = load_eval()
    kinds = Counter()
    for q in queries:
        kinds[failure_kind(bm25_names(memories, q["query"]), q["relevant"])] += 1
    print(f"BM25 on {len(queries)} queries, top {K} judged, candidate pool {POOL}")
    for kind in ("ok", "ranked wrong", "retrieved wrong"):
        print(f"  {kind:<16} {kinds[kind]}")
    return 0


def section_identifier():
    memories, _ = load_eval()
    query = "8601"
    holders = [m.name for m in memories if query in tokenize(m.search_text)]
    print(f"query {query!r}: notes that contain the token = {holders}")
    print(f"query {query!r}: BM25 top 3 = {bm25_names(memories, query)[:3]}")
    return 0


def section_paraphrase():
    memories, queries = load_eval()
    query = "What do I take on a trip?"
    expected = next(q["relevant"] for q in queries if q["query"] == query)
    print(f"query {query!r}, correct note {expected}")
    print(f"  BM25, run now:           top 3 = {bm25_names(memories, query)[:3]}")
    print(f"  dense, stored output:    top 3 = {stored_top3('dense')[query]}")
    return 0


def section_fusion():
    memories, _ = load_eval()
    query = "How do I protect my files if the laptop dies?"
    bm25 = bm25_names(memories, query)
    dense = stored_top3("dense")[query]
    print(f"query {query!r}, correct note ['backup-routine']")
    print(f"  BM25 rank of backup-routine: {bm25.index('backup-routine') + 1}; BM25 top 3 = {bm25[:3]}")
    print(f"  dense top 3 (stored; only three are stored) = {dense}")
    for name, score in reciprocal_rank_fusion([bm25, dense])[:4]:
        print(f"  fused {name:<18} {score:.5f}")
    return 0


def section_floor():
    memories, queries = load_eval()
    best = tfidf_similarity(memories)
    answers = [(best(q["query"]), q["relevant"]) for q in queries]
    junk = [best(q)[0] for q in OFF_TOPIC]
    print(f"{len(queries)} on-topic queries, {len(OFF_TOPIC)} off-topic queries; similarity = tf-idf cosine, 0 to 1")
    print(f"{'floor':>6} {'correct kept':>13} {'correct dropped':>16} {'off-topic still answered':>25}")
    for floor in FLOORS:
        kept = sum(s >= floor and n in rel for (s, n), rel in answers)
        dropped = sum(s < floor and n in rel for (s, n), rel in answers)
        print(f"{floor:>6.2f} {kept:>13} {dropped:>16} {sum(s >= floor for s in junk):>19} of {len(junk)}")
    print(f"highest off-topic score {max(junk):.3f}; lowest correct top score {min(s for (s, n), rel in answers if n in rel):.3f}")
    return 0


def section_index():
    ids, vectors = ["a", "b"], [[0.1, 0.2, 0.3], [0.3, 0.2, 0.1]]
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "index.json"
        save_index(path, "embedder-one", ids, vectors)
        for embedder, dimension in (("embedder-one", 3), ("embedder-two", 3), ("embedder-one", 4)):
            try:
                load_index(path, embedder, dimension)
                print(f"load with embedder {embedder!r}, vector length {dimension}: loaded")
            except IndexMismatch as error:
                print(f"load with embedder {embedder!r}, vector length {dimension}: refused")
                print("  " + str(error).replace(folder + "/", ""))
    return 0


SECTIONS = {
    "classify": section_classify, "identifier": section_identifier, "paraphrase": section_paraphrase,
    "fusion": section_fusion, "floor": section_floor, "index": section_index,
}


def main(argv):
    if len(argv) != 1 or argv[0] not in SECTIONS:
        print(__doc__)
        return 2
    return SECTIONS[argv[0]]()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
