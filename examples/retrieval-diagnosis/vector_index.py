"""Store note vectors together with the embedder that made them, and refuse to load a mismatch. Standard library only."""
import json
from pathlib import Path


class IndexMismatch(ValueError):
    pass


def save_index(path, embedder, ids, vectors):
    if len(ids) != len(vectors):
        raise ValueError(f"{len(ids)} ids but {len(vectors)} vectors")
    dimensions = {len(v) for v in vectors}
    if len(dimensions) != 1:
        raise ValueError(f"vectors have different lengths: {sorted(dimensions)}")
    record = {"embedder": embedder, "dimension": dimensions.pop(), "ids": list(ids), "vectors": [list(v) for v in vectors]}
    Path(path).write_text(json.dumps(record), encoding="utf-8")


def load_index(path, embedder, dimension):
    """Return (ids, vectors). Raise IndexMismatch when the index was not made by this embedder at this vector length."""
    record = json.loads(Path(path).read_text(encoding="utf-8"))
    missing = [key for key in ("embedder", "dimension", "ids", "vectors") if key not in record]
    if missing:
        raise IndexMismatch(f"{path}: the index has no field(s): {', '.join(missing)}")
    if record["embedder"] != embedder:
        raise IndexMismatch(f"{path}: built with embedder {record['embedder']!r}, asked for {embedder!r}. Rebuild the index.")
    if record["dimension"] != dimension:
        raise IndexMismatch(f"{path}: stored vector length {record['dimension']}, the embedder now gives {dimension}. Rebuild the index.")
    ragged = [i for i, v in enumerate(record["vectors"]) if len(v) != record["dimension"]]
    if ragged:
        raise IndexMismatch(f"{path}: vector(s) {ragged} do not have the stored length {record['dimension']}. The file is damaged.")
    return record["ids"], record["vectors"]
