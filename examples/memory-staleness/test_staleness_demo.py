import io
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import staleness_demo
from staleness_demo import memory

HERE = Path(__file__).resolve().parent


class Staleness(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.scratch)
        self.folder = Path(self.scratch) / "notes"
        shutil.copytree(HERE / "notes", self.folder)

    def test_the_stale_note_ranks_first_and_both_notes_load(self):
        chosen, _ = memory.select(staleness_demo.PROMPT, memory.load_memories(self.folder))
        self.assertEqual([m.name for m, _ in chosen], ["staging-host", "staging-moved"])

    def test_the_text_sent_to_the_assistant_carries_no_date(self):
        chosen, _ = memory.select(staleness_demo.PROMPT, memory.load_memories(self.folder))
        self.assertNotIn("2026", memory.render_context(chosen))

    def test_only_the_staging_pair_is_flagged(self):
        pairs = staleness_demo.shared_topic_pairs(memory.load_memories(self.folder))
        self.assertEqual([(a.name, b.name) for a, b in pairs], [("staging-host", "staging-moved")])

    def test_the_repair_leaves_one_current_note(self):
        staleness_demo.repair_in_place(self.folder, "staging-host", "staging-moved", "Where staging runs.", "Staging runs on the new platform.")
        notes = memory.load_memories(self.folder)
        self.assertEqual(sorted(m.name for m in notes), ["line-length", "staging-host"])
        staging = next(m for m in notes if m.name == "staging-host")
        self.assertEqual(staging.updated, staleness_demo.REPAIR_TIME)
        self.assertEqual(staging.body, "Staging runs on the new platform.")

    def test_the_stored_notes_are_not_changed_by_the_demo(self):
        before = sorted(p.name for p in (HERE / "notes").glob("*.md"))
        with redirect_stdout(io.StringIO()):
            staleness_demo.main()
        self.assertEqual(sorted(p.name for p in (HERE / "notes").glob("*.md")), before)


if __name__ == "__main__":
    unittest.main()
