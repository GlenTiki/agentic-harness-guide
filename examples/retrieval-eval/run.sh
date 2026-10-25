#!/bin/sh
# Reproduce every row of the retrieval table. Run from this folder.
# Needs: Python 3.9 or newer; Ollama running with nomic-embed-text installed (`ollama pull nomic-embed-text`);
# for the cross-encoder: a Python with sentence-transformers, named in CROSS_ENCODER_PYTHON.
#   uv venv /tmp/retrieval-venv && uv pip install --python /tmp/retrieval-venv/bin/python sentence-transformers
#   CROSS_ENCODER_PYTHON=/tmp/retrieval-venv/bin/python sh run.sh
set -eu
cd "$(dirname "$0")"
mkdir -p outputs
run() { python3 -I retrieval_eval.py "$@" 2>/dev/null; }
run bm25 > outputs/bm25.txt
run lexical > outputs/lexical-rerank.txt
run dense > outputs/dense.txt
run dense-prefixes > outputs/dense-prefixes.txt
run hybrid > outputs/hybrid.txt
run hybrid-prefixes > outputs/hybrid-prefixes.txt
CE="${CROSS_ENCODER_PYTHON:-python3}"
"$CE" -I retrieval_eval.py cross-encoder 2>/dev/null | grep -v '^Loading weights' > outputs/cross-encoder.txt
{
  "$CE" -I retrieval_eval.py cross-encoder --latency --repeats 5 2>/dev/null
  echo
  echo "--- determinism: 10 repeats ---"
  "$CE" -I retrieval_eval.py cross-encoder --latency --repeats 10 2>/dev/null | grep -v '^date\|^machine\|^python\|^packages\|^system\|^command\|^model'
} > outputs/latency.txt
echo "done"
