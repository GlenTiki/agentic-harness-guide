import io
import unittest

import seam

CASES = seam.CASES


class Seam(unittest.TestCase):
    def test_classify_normalises_case_and_whitespace(self):
        self.assertEqual(seam.classify("x", seam.FakeClient({"x": "  URGENT\n"})), "urgent")

    def test_classify_rejects_an_unexpected_reply(self):
        with self.assertRaises(ValueError):
            seam.classify("x", seam.FakeClient({"x": "maybe"}))

    def test_same_cases_run_against_any_client(self):
        perfect = seam.FakeClient(dict(CASES))
        self.assertEqual(seam.score(perfect, CASES), {"right": 6, "bad_replies": 0, "total": 6})
        self.assertEqual(perfect.calls, 6)

    def test_a_chatty_client_is_counted_as_bad_replies_not_wrong_answers(self):
        chatty = seam.FakeClient({}, default="I think this is urgent!")
        self.assertEqual(seam.score(chatty, CASES), {"right": 0, "bad_replies": 6, "total": 6})

    def test_swapping_the_client_changes_nothing_else(self):
        first = seam.score(seam.FakeClient({"Fridge alarm is sounding": "urgent"}), CASES)
        second = seam.score(seam.FakeClient({"Fridge alarm is sounding": "urgent"}), CASES)
        self.assertEqual(first, second)

    def test_demo_output_is_stable(self):
        out = io.StringIO()
        seam.demo(out)
        self.assertEqual(
            out.getvalue(),
            'small-fake: {"right": 4, "bad_replies": 0, "total": 6} calls=6\n'
            'large-fake: {"right": 6, "bad_replies": 0, "total": 6} calls=6\n'
            'chatty-fake: {"right": 0, "bad_replies": 6, "total": 6} calls=6\n',
        )


if __name__ == "__main__":
    unittest.main()
