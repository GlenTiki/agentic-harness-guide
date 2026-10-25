# Retrieval evaluation

This folder holds the stored output of every row in the retrieval tables of the guide (the relevance page, case-study chapter 6 and chapter 12). Each file in `outputs/` starts with a header: date, machine class, Python and package versions, model, command.

## What it measures

The set has 44 memory notes (`evalset/memories/`) and 34 queries with the notes a person marked as correct (`evalset/queries.json`). The set is the one in the chapter 6 kit. Metrics at k = 3: precision@3 is the share of the top three that are correct. hit@3 is the share of queries with a correct note in the top three. MRR is the mean of 1 / rank of the first correct note.

## Files

| File | Content |
| --- | --- |
| `retrieval_eval.py` | Scores one system and prints a header, one table row and the result for each of the 34 queries. |
| `kit/` | Copies of `bm25.py`, `memory.py` and `rerank.py` from the chapter 6 kit. |
| `evalset/` | The 44 notes and 34 queries, copied unchanged from the kit. |
| `run.sh` | Reproduces every file in `outputs/`. |
| `outputs/bm25.txt` | BM25. |
| `outputs/lexical-rerank.txt` | Lexical re-rank, no model. |
| `outputs/cross-encoder.txt` | Cross-encoder `cross-encoder/ms-marco-MiniLM-L6-v2`, top 20 BM25 candidates. |
| `outputs/dense.txt` | Dense retrieval, `nomic-embed-text` through Ollama, no prefixes. |
| `outputs/dense-prefixes.txt` | The same with `search_query: ` and `search_document: ` prefixes. |
| `outputs/hybrid.txt` | BM25 plus dense, reciprocal rank fusion with k = 60. |
| `outputs/hybrid-prefixes.txt` | The same with the prefixes. |
| `outputs/latency.txt` | Cross-encoder timing over 34 prompts, 5 repeats (170 samples), then a 10-repeat determinism check. |

## Reproduce

1. Install Ollama and run `ollama pull nomic-embed-text`.
2. Make a Python environment with `sentence-transformers`: `uv venv /tmp/retrieval-venv` then `uv pip install --python /tmp/retrieval-venv/bin/python sentence-transformers`.
3. Run `CROSS_ENCODER_PYTHON=/tmp/retrieval-venv/bin/python sh run.sh`.

BM25, lexical re-rank, dense and hybrid use only the standard library and the Ollama HTTP API. Dense rows embed each note as `[name] description` then the body (`context_text` in `kit/memory.py`). The first run downloads the cross-encoder model.

## Measured on 2026-10-25

Apple silicon laptop, macOS 26.5, Ollama 0.34.2, `nomic-embed-text` digest `0a109f422b47`, `sentence-transformers` 6.2.0, torch 2.14.1 (4 threads), CPU only.

| System | precision@3 | hit@3 | MRR |
| --- | --- | --- | --- |
| BM25 | 0.265 | 0.794 | 0.643 |
| Lexical re-rank | 0.235 | 0.706 | 0.670 |
| Cross-encoder | 0.275 | 0.794 | 0.803 |
| Dense | 0.333 | 0.941 | 0.905 |
| Dense with prefixes | 0.333 | 0.971 | 0.911 |
| Hybrid, k = 60 | 0.275 | 0.824 | 0.795 |
| Hybrid with prefixes | 0.275 | 0.824 | 0.808 |

The scores are deterministic: the cross-encoder gave identical scores over 10 repeats, and two dense runs gave identical output. Latency is not deterministic. It varied between runs on a machine with other work running, so read it as a rough size.

Limits: 34 queries, so one query moves hit@3 by 0.029. One person wrote the set, and it uses other words than the notes, so it favours meaning-based methods.
