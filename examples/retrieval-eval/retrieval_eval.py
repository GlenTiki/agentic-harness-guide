"""Score one retrieval system on the evaluation set and print a header, one row and per-query details.

Usage: python3 -I retrieval_eval.py SYSTEM [--text-field FIELD] [--latency] [--repeats N]
SYSTEM: bm25, lexical, cross-encoder, dense, dense-prefixes, hybrid, hybrid-prefixes
"""
import argparse
import datetime
import hashlib
import json
import platform
import statistics
import sys
import time
import urllib.request
from importlib import metadata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "kit"))
import memory  # noqa: E402
import rerank  # noqa: E402

K = 3
CANDIDATES = 20
RRF_K = 60
OLLAMA = "http://127.0.0.1:11434"
EMBED_MODEL = "nomic-embed-text"
QUERY_PREFIX, DOCUMENT_PREFIX = "search_query: ", "search_document: "


def embed(texts):
    body = json.dumps({"model": EMBED_MODEL, "input": texts}).encode()
    request = urllib.request.Request(f"{OLLAMA}/api/embed", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=300) as response:
        return json.load(response)["embeddings"]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / ((sum(x * x for x in a) ** 0.5) * (sum(y * y for y in b) ** 0.5))


def dense_ranker(memories, queries, prefixes, text_field):
    documents = [getattr(m, text_field) for m in memories]
    document_vectors = embed([(DOCUMENT_PREFIX if prefixes else "") + d for d in documents])
    query_vectors = dict(zip(queries, embed([(QUERY_PREFIX if prefixes else "") + q for q in queries])))

    def ranker(prompt, _memories):
        scored = [(i, cosine(query_vectors[prompt], v)) for i, v in enumerate(document_vectors)]
        scored.sort(key=lambda pair: (-pair[1], pair[0]))
        return [(memories[i], s) for i, s in scored]

    return ranker


def hybrid_ranker(first, second):
    def ranker(prompt, memories):
        fused = {}
        for ranking in (first(prompt, memories), second(prompt, memories)):
            for rank, (item, _) in enumerate(ranking, start=1):
                fused[item.name] = fused.get(item.name, 0.0) + 1 / (RRF_K + rank)
        by_name = {m.name: m for m in memories}
        ordered = sorted(fused.items(), key=lambda pair: (-pair[1], pair[0]))
        return [(by_name[n], s) for n, s in ordered]

    return ranker


def build(system, memories, queries, text_field):
    names = [q["query"] for q in queries]
    prefixes = system.endswith("prefixes")
    if system == "bm25":
        return memory.bm25_ranker
    if system == "lexical":
        return rerank.rerank_ranker(rerank.LexicalScorer(), CANDIDATES)
    if system == "cross-encoder":
        return rerank.rerank_ranker(rerank.CrossEncoderScorer(), CANDIDATES)
    dense = dense_ranker(memories, names, prefixes, text_field)
    if system.startswith("dense"):
        return dense
    return hybrid_ranker(memory.bm25_ranker, dense)


def metrics(ranker, memories, queries):
    precisions, hits, reciprocal, details = [], 0, [], []
    for q in queries:
        ranked = [m.name for m, _ in ranker(q["query"], memories)]
        relevant = set(q["relevant"])
        top = ranked[:K]
        precisions.append(sum(n in relevant for n in top) / K)
        hit = any(n in relevant for n in top)
        hits += hit
        first = next((r for r, n in enumerate(ranked, start=1) if n in relevant), None)
        reciprocal.append(1 / first if first else 0.0)
        details.append((q["query"], top, sorted(relevant), hit, first))
    count = len(queries)
    return sum(precisions) / count, hits / count, sum(reciprocal) / count, hits, details


def package_versions():
    found = {}
    for name in ("sentence-transformers", "torch", "transformers", "numpy"):
        try:
            found[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            pass
    return found


def ollama_info():
    try:
        with urllib.request.urlopen(f"{OLLAMA}/api/version", timeout=10) as r:
            version = json.load(r)["version"]
        tags = json.load(urllib.request.urlopen(f"{OLLAMA}/api/tags", timeout=10))["models"]
        digest = next((m["digest"][:12] for m in tags if m["name"].startswith(EMBED_MODEL)), "not installed")
        return f"ollama {version}, {EMBED_MODEL} digest {digest}"
    except OSError as error:
        return f"ollama unreachable: {error}"


def header(system, args):
    lines = [
        f"date: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"machine: Apple silicon ({platform.machine()}), macOS {platform.mac_ver()[0]}",
        f"python: {platform.python_version()}",
        f"packages: {package_versions() if system == 'cross-encoder' else 'standard library only'}",
        f"system: {system}",
        f"command: {' '.join(sys.argv[:1] + sys.argv[1:])}",
    ]
    if system.startswith(("dense", "hybrid")):
        lines += [f"model: {EMBED_MODEL} via {ollama_info()}", f"document text: {args.text_field}"]
    if system == "cross-encoder":
        lines.append(f"model: {rerank.DEFAULT_MODEL}")
    if system == "hybrid" or system == "hybrid-prefixes":
        lines.append(f"fusion: reciprocal rank fusion, k = {RRF_K}, BM25 plus dense")
    return lines


def latency(memories, queries, repeats):
    started = time.perf_counter()
    scorer = rerank.CrossEncoderScorer()
    load_seconds = time.perf_counter() - started
    ranker = rerank.rerank_ranker(scorer, CANDIDATES)
    ranker(queries[0]["query"], memories)
    timings, first_signature = [], None
    for _ in range(repeats):
        signature = []
        for q in queries:
            begun = time.perf_counter()
            ranked = ranker(q["query"], memories)
            timings.append(time.perf_counter() - begun)
            signature.append([(m.name, round(s, 5)) for m, s in ranked])
        digest = hashlib.sha256(json.dumps(signature).encode()).hexdigest()
        first_signature = first_signature or digest
        print(f"repeat scores sha256: {digest[:16]} identical_to_first: {digest == first_signature}")
    print(f"load_seconds: {load_seconds:.2f}")
    print(f"median_seconds_per_prompt: {statistics.median(timings):.4f}")
    print(f"max_seconds_per_prompt: {max(timings):.4f}")
    print(f"candidates: {CANDIDATES}, prompts: {len(queries)}, repeats: {repeats}, samples: {len(timings)}")
    try:
        import torch
        print(f"torch threads: {torch.get_num_threads()}")
    except ImportError:
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("system")
    parser.add_argument("--text-field", default="context_text", choices=("context_text", "search_text"))
    parser.add_argument("--latency", action="store_true")
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    memories = memory.load_memories(HERE / "evalset" / "memories")
    queries = json.loads((HERE / "evalset" / "queries.json").read_text(encoding="utf-8"))["queries"]
    print("\n".join(header(args.system, args)))
    print()
    if args.latency:
        latency(memories, queries, args.repeats)
        return 0
    ranker = build(args.system, memories, queries, args.text_field)
    p, h, m, hits, details = metrics(ranker, memories, queries)
    print("| system | precision@3 | hit@3 | MRR |\n| --- | --- | --- | --- |")
    print(f"| {args.system} | {p:.3f} | {h:.3f} | {m:.3f} |")
    print(f"({len(memories)} memories, {len(queries)} queries, {hits} queries with a correct note in the top 3)\n")
    for query, top, relevant, hit, first in details:
        print(f"{'HIT ' if hit else 'MISS'} first_correct_rank={first} | {query}\n     top3={top} expected={relevant}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
