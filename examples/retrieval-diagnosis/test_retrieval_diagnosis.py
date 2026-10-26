import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import diagnose
from vector_index import IndexMismatch, load_index, save_index


class FailureKind(unittest.TestCase):
    def test_a_correct_note_in_the_top_three_is_ok(self):
        self.assertEqual(diagnose.failure_kind(["x", "y", "a"], ["a"]), "ok")

    def test_a_correct_note_below_the_top_three_but_in_the_pool_is_ranked_wrong(self):
        self.assertEqual(diagnose.failure_kind(["x", "y", "z", "a"], ["a"]), "ranked wrong")

    def test_a_correct_note_outside_the_pool_or_absent_is_retrieved_wrong(self):
        self.assertEqual(diagnose.failure_kind([str(i) for i in range(10)] + ["a"], ["a"]), "retrieved wrong")
        self.assertEqual(diagnose.failure_kind([], ["a"]), "retrieved wrong")

    def test_the_best_of_several_correct_notes_decides(self):
        self.assertEqual(diagnose.failure_kind(["x", "b", "y", "a"], ["a", "b"]), "ok")


class Fusion(unittest.TestCase):
    def test_scores_are_summed_across_lists(self):
        fused = dict(diagnose.reciprocal_rank_fusion([["a", "b"], ["b", "c"]]))
        self.assertAlmostEqual(fused["b"], 1 / 62 + 1 / 61)
        self.assertAlmostEqual(fused["a"], 1 / 61)
        self.assertAlmostEqual(fused["c"], 1 / 62)

    def test_a_note_high_in_both_lists_beats_a_note_first_in_one(self):
        ordered = [name for name, _ in diagnose.reciprocal_rank_fusion([["a", "b", "c"], ["b", "c", "d"]])]
        self.assertEqual(ordered[0], "b")

    def test_ties_break_by_name(self):
        ordered = [name for name, _ in diagnose.reciprocal_rank_fusion([["b"], ["a"]])]
        self.assertEqual(ordered, ["a", "b"])


class StoredOutputs(unittest.TestCase):
    def test_the_stored_dense_output_has_all_34_queries(self):
        self.assertEqual(len(diagnose.stored_top3("dense")), 34)

    def test_live_bm25_agrees_with_the_stored_bm25_output(self):
        memories, queries = diagnose.load_eval()
        stored = diagnose.stored_top3("bm25")
        for q in queries:
            self.assertEqual(diagnose.bm25_names(memories, q["query"])[:3], stored[q["query"]], q["query"])


class Sections(unittest.TestCase):
    def test_classify_counts_match_the_stored_bm25_hit_count(self):
        memories, queries = diagnose.load_eval()
        kinds = [diagnose.failure_kind(diagnose.bm25_names(memories, q["query"]), q["relevant"]) for q in queries]
        self.assertEqual(kinds.count("ok"), 27)
        self.assertEqual(len(kinds), 34)

    def test_the_identifier_token_is_in_one_note_and_that_note_ranks_first(self):
        memories, _ = diagnose.load_eval()
        self.assertEqual(diagnose.bm25_names(memories, "8601"), ["utc-timestamps"])

    def test_the_off_topic_and_correct_score_ranges_overlap(self):
        memories, queries = diagnose.load_eval()
        best = diagnose.tfidf_similarity(memories)
        correct = [best(q["query"])[0] for q in queries if best(q["query"])[1] in q["relevant"]]
        self.assertGreater(max(best(q)[0] for q in diagnose.OFF_TOPIC), min(correct))

    def test_unknown_section_prints_usage(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(diagnose.main(["nonsense"]), 2)


class VectorIndex(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "index.json"
        save_index(self.path, "one", ["a", "b"], [[1, 2, 3], [4, 5, 6]])

    def test_the_matching_embedder_and_length_load(self):
        ids, vectors = load_index(self.path, "one", 3)
        self.assertEqual((ids, vectors), (["a", "b"], [[1, 2, 3], [4, 5, 6]]))

    def test_a_different_embedder_is_refused(self):
        with self.assertRaisesRegex(IndexMismatch, "built with embedder 'one', asked for 'two'"):
            load_index(self.path, "two", 3)

    def test_a_different_vector_length_is_refused(self):
        with self.assertRaisesRegex(IndexMismatch, "stored vector length 3, the embedder now gives 4"):
            load_index(self.path, "one", 4)

    def test_a_damaged_vector_is_refused(self):
        record = json.loads(self.path.read_text())
        record["vectors"][1] = [4, 5]
        self.path.write_text(json.dumps(record))
        with self.assertRaisesRegex(IndexMismatch, r"vector\(s\) \[1\]"):
            load_index(self.path, "one", 3)

    def test_a_missing_field_is_refused(self):
        self.path.write_text(json.dumps({"ids": [], "vectors": []}))
        with self.assertRaisesRegex(IndexMismatch, "no field"):
            load_index(self.path, "one", 3)

    def test_saving_ragged_vectors_fails(self):
        with self.assertRaises(ValueError):
            save_index(self.path, "one", ["a", "b"], [[1, 2], [3]])

    def test_saving_a_different_number_of_ids_and_vectors_fails(self):
        with self.assertRaises(ValueError):
            save_index(self.path, "one", ["a"], [[1], [2]])


if __name__ == "__main__":
    unittest.main()
