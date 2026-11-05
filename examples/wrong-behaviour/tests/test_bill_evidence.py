import json
import re
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]


class BillEvidenceTests(unittest.TestCase):
    def test_long_prompt_supports_supplied_sum_but_not_a_unique_duplicate(self):
        case = json.loads((HERE / 'cases/C01-bills-total.json').read_text())
        arm = next(arm for arm in case['arms'] if arm['id'] == 'long-unlabelled')
        amounts = [int(line) for line in arm['prompt'].splitlines() if line.isdigit()]
        self.assertEqual((len(amounts), sum(amounts)), (40, 7414))
        self.assertEqual(sum(amounts) - arm['expected']['dup_value'], 7281)
        self.assertEqual({amount for amount, count in Counter(amounts).items() if count > 1}, {133, 152, 175, 217})
        self.assertNotIn('stop', arm['prompt'].lower())
        self.assertNotIn('duplicate', arm['prompt'].lower())

    def test_all_recorded_long_replies_flag_the_count_and_give_the_supplied_sum(self):
        replies = sorted((HERE / 'runs/2026-10-25/raw').glob('C01-bills-total-long-unlabelled-t*.txt'))
        self.assertEqual(len(replies), 20)
        for path in replies:
            with self.subTest(path=path.name):
                reply = path.read_text()
                self.assertRegex(reply, r'\b40\b')
                self.assertRegex(reply, r'\b39\b')
                self.assertIn('7,414', reply)
        for trial in (1, 10):
            reply = (HERE / f'runs/2026-10-25/raw/C01-bills-total-long-unlabelled-t{trial:02d}.txt').read_text()
            self.assertLess(re.search(r'\b40\b', reply).start(), reply.index('7,414'))


if __name__ == '__main__':
    unittest.main()
