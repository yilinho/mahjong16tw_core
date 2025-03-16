import unittest

from ..engine import get_candidates


class MyTestCase(unittest.TestCase):
    def test_can_goal1(self):
        hand = [205, 205, 206, 207, 215, 215, 215, 221, 222, 223, 225, 225, 225, 226, 227, 228]
        candidates = get_candidates(tuple(hand))
        self.assertEqual(len(candidates), 2)
        self.assertIn(205, candidates)
        self.assertIn(208, candidates)

        hand = [202, 204, 207, 208, 209, 214, 215, 216, 223, 223, 224, 225, 226]
        candidates = get_candidates(tuple(hand))
        self.assertEqual(candidates, [203])

        hand = [202, 203, 204, 207, 208, 209, 214, 215, 216, 223, 223, 224, 225]
        candidates = get_candidates(tuple(hand))
        self.assertEqual(candidates, [223, 226])


if __name__ == '__main__':
    unittest.main()
