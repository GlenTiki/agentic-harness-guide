"""Re-rank the BM25 candidates for a prompt.

Two scorers share one interface: scorer.scores(query, documents) -> list of floats.
  CrossEncoderScorer  reads each (query, document) pair together. Needs the optional sentence-transformers package.
  LexicalScorer       a deterministic fallback that needs nothing. It uses word stems, prefixes and word pairs.

Pipeline: BM25 picks candidates, the scorer orders them. If BM25 finds fewer candidates than asked for, the list is
padded with the next documents in file order so that the scorer can still see a document that shares no word with
the prompt. The padding order is arbitrary. It is a choice made in this kit.
"""
import importlib.util
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -I does not add the script folder
from bm25 import BM25Index, tokenize  # noqa: E402

DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"
SUFFIXES = ("ing", "ed", "es", "ly", "s")
PREFIX_LENGTH = 5
SCORE_DECIMALS = 5


def cross_encoder_available():
    return importlib.util.find_spec("sentence_transformers") is not None


def stem(word):
    for suffix in SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def stems(text):
    return [stem(t) for t in tokenize(text)]


class LexicalScorer:
    """Whole-stem match counts 1. A shared five-letter prefix counts 0.5. A shared word pair adds 0.5."""

    def scores(self, query, documents):
        wanted = list(dict.fromkeys(stems(query)))
        pairs = set(zip(stems(query), stems(query)[1:]))
        results = []
        for document in documents:
            doc_stems = stems(document)
            doc_set, doc_prefixes = set(doc_stems), {s[:PREFIX_LENGTH] for s in doc_stems if len(s) >= PREFIX_LENGTH}
            total = 0.0
            for word in wanted:
                if word in doc_set:
                    total += 1.0
                elif len(word) >= PREFIX_LENGTH and word[:PREFIX_LENGTH] in doc_prefixes:
                    total += 0.5
            total += 0.5 * len(pairs & set(zip(doc_stems, doc_stems[1:])))
            results.append(total / (len(wanted) ** 0.5) if wanted else 0.0)
        return results


class CrossEncoderScorer:
    def __init__(self, model_name=DEFAULT_MODEL, model=None):
        """Pass `model` (any object with predict(pairs)) to test without the package."""
        if model is None:
            from sentence_transformers import CrossEncoder  # optional dependency, loaded only here
            model = CrossEncoder(model_name)
        self.model = model

    def scores(self, query, documents):
        return [float(s) for s in self.model.predict([(query, d) for d in documents])]


def rerank_ranker(scorer, candidates=20, min_score=None):
    """Return a ranker for memory.select(). It re-orders the BM25 candidates with `scorer`."""

    def ranker(prompt, memories):
        index = BM25Index([m.search_text for m in memories])
        positions = [i for i, _ in index.rank(prompt)][:candidates]
        positions += [i for i in range(len(memories)) if i not in positions][: max(0, candidates - len(positions))]
        scores = scorer.scores(prompt, [memories[i].context_text for i in positions])
        order = {p: r for r, p in enumerate(positions)}
        ranked = sorted(zip(positions, scores), key=lambda ps: (-round(ps[1], SCORE_DECIMALS), order[ps[0]], memories[ps[0]].name))
        return [(memories[p], s) for p, s in ranked if min_score is None or s > min_score]

    return ranker
