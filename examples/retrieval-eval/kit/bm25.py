"""BM25 ranking, written from the published formula. Standard library only. Same input gives the same output."""
import math
import re
from collections import Counter

K1 = 1.5
B = 0.75
STOPWORDS = frozenset(
    "a an and are as at be but by for from has have i in is it its me my of on or our so that the their "
    "then there this to was we were what when which who will with you your".split()
)


def tokenize(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS]


class BM25Index:
    def __init__(self, documents, k1=K1, b=B):
        """documents: a list of strings. The position in the list is the document id."""
        self.k1, self.b = k1, b
        self.counts = [Counter(tokenize(d)) for d in documents]
        self.lengths = [sum(c.values()) for c in self.counts]
        self.average_length = (sum(self.lengths) / len(documents)) if documents else 0.0
        self.document_frequency = Counter(term for c in self.counts for term in c)

    def idf(self, term):
        n = self.document_frequency.get(term, 0)
        return math.log(1 + (len(self.counts) - n + 0.5) / (n + 0.5))

    def score(self, query, doc_id):
        counts, length = self.counts[doc_id], self.lengths[doc_id]
        total = 0.0
        for term in set(tokenize(query)):
            tf = counts.get(term, 0)
            if not tf:
                continue
            norm = 1 - self.b + self.b * length / self.average_length
            total += self.idf(term) * tf * (self.k1 + 1) / (tf + self.k1 * norm)
        return total

    def rank(self, query):
        """Return (doc_id, score) for every document with a score above zero. Best first, ties by id."""
        scored = [(i, self.score(query, i)) for i in range(len(self.counts))]
        return sorted(((i, s) for i, s in scored if s > 0), key=lambda pair: (-pair[1], pair[0]))
