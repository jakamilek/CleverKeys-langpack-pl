import copy
import unittest
from replay import compare, verify_freeze


def row(id='one', gold='A', means=None, sums=None, window='short'):
    return dict(id=id, gold=gold, surfaces=['a', 'A', 'b', 'B'], suite='s', population='p', window=window,
                meanScores=means or {'a': -3., 'A': -1., 'b': -2., 'B': -4.},
                sumScores=sums or {'a': -3., 'A': -1., 'b': -2., 'B': -4.})


class HistoricalPreservationTest(unittest.TestCase):
    def test_transitive_v1_and_v2_freeze(self):
        verify_freeze()

    def test_improvement_does_not_hide_regression_in_a_different_window(self):
        repair = row(gold='a', sums={'a': -1., 'A': -3., 'b': -2., 'B': -4.})
        regression = row(id='two', window='long', sums={'a': -1., 'A': -3., 'b': -2., 'B': -4.})
        result = compare([repair, regression])
        self.assertFalse(result['preservationPassed'])
        self.assertEqual(1, result['groups']['s/p/short']['repairs'])
        self.assertEqual(1, result['groups']['s/p/long']['regressions'])

    def test_gold_beyond_top3_is_reported_as_top3_regression(self):
        result = compare([row(sums={'a': -1., 'A': -4., 'b': -2., 'B': -3.})])
        self.assertEqual(1, result['groups']['s/p/short']['top3Regressions'])
        self.assertFalse(result['preservationPassed'])

    def test_unlabelled_is_retained_but_not_counted_as_accuracy(self):
        result = compare([row(gold=None)])
        self.assertEqual(1, result['groups']['s/p/short']['requests'])
        self.assertEqual(0, result['groups']['s/p/short']['labelled'])

    def test_absent_gold_does_not_silently_become_a_correct_prediction(self):
        result = compare([row(gold='absent')])
        self.assertEqual(1, result['groups']['s/p/short']['missingGold'])
        self.assertEqual(0, result['groups']['s/p/short']['sumTop1'])

    def test_changed_ranks_with_same_correct_winner_preserve_full_trace(self):
        result = compare([row(sums={'a': -2., 'A': -1., 'b': -3., 'B': -4.})])
        self.assertTrue(result['preservationPassed'])
        self.assertEqual(1, len(result['changes']))
        self.assertEqual(['A', 'a', 'b', 'B'], result['changes'][0]['sumOrder'])

    def test_duplicate_requests_and_unaligned_scores_fail(self):
        for rows in [[row(), row()], [row(means={'a': -1.})], []]:
            with self.assertRaises(ValueError):
                compare(rows)


if __name__ == '__main__':
    unittest.main()
