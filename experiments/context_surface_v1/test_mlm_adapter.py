import unittest

from mlm_adapter import shared_context_suffix


class WholeWordMaskContractTests(unittest.TestCase):
    def test_different_variant_lengths_keep_identical_context(self):
        self.assertEqual(shared_context_suffix([11, 12, 13, 14], [1, 2], budget=6),
                         ([13, 14], True))

    def test_short_context_is_untouched(self):
        self.assertEqual(shared_context_suffix([11, 12], [1, 3], budget=8),
                         ([11, 12], False))

    def test_empty_or_unrepresentable_variant_is_rejected(self):
        for lengths in ([], [0], [5]):
            with self.assertRaises(ValueError):
                shared_context_suffix([11], lengths, budget=6)
