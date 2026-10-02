import unittest

from build_diagnostic_fixture import build, TAIL
from prototype import prepare
from diagnostic_runner import masked_tasks, aggregate
from diagnostic_evaluate import evaluate_diagnostic


class DiagnosticFixtureTests(unittest.TestCase):
    def setUp(self):
        self.cases, self.sidecar = build()
        self.request = prepare(self.cases, self.sidecar)

    def test_counts_and_gold_do_not_enter_model_requests(self):
        self.assertEqual(len(self.cases['cases']), 48)
        self.assertEqual(len(self.request['requests']), 96)
        self.assertEqual(sum('expected' not in c for c in self.cases['cases']), 8)
        for row in self.request['requests']:
            self.assertNotIn('expected', row)
            self.assertNotIn('diagnostic', row)

    def test_pair_information_is_lost_in_short_but_retained_in_long(self):
        rows = {r['requestId']: r for r in self.request['requests']}
        paired = {}
        for case in self.cases['cases']:
            info = case['diagnostic']
            if info['category'] in ('previous', 'distant_retained', 'conflicting', 'context_lost'):
                paired.setdefault(info['pairId'], []).append(case)
        for name, pair in paired.items():
            a, b = pair
            self.assertEqual(rows[a['id']+'/two_words']['context']['text'],
                             rows[b['id']+'/two_words']['context']['text'])
            long_a = rows[a['id']+'/long']['context']
            long_b = rows[b['id']+'/long']['context']
            if name.endswith('/context_lost'):
                self.assertEqual(long_a['text'], long_b['text'])
                self.assertTrue(long_a['word_truncated'])
            else:
                self.assertNotEqual(long_a['text'], long_b['text'])
                self.assertFalse(long_a['word_truncated'])

    def test_distant_retained_has_more_than_thirty_words(self):
        rows = {r['requestId']: r for r in self.request['requests']}
        for case in self.cases['cases']:
            if case['diagnostic']['category'] == 'distant_retained':
                self.assertGreater(rows[case['id']+'/long']['context']['word_count'], 30)

    def test_known_candidates_and_alternates_are_identical_across_windows(self):
        rows = self.request['requests']
        for a, b in zip(rows[::2], rows[1::2]):
            self.assertEqual(a['candidates'], b['candidates'])
            self.assertEqual(len(a['candidates'][0]['variants']), 2)

    def test_ambiguous_cases_have_no_accuracy_and_controls_do_not_enter_main(self):
        report, rows = evaluate_diagnostic(self.cases, self.request)
        for window in ('two_words', 'long'):
            data = report['metrics'][window]
            self.assertEqual(data['main']['cases'], 32)
            self.assertEqual(data['main']['correct'], 16)
            self.assertEqual(data['byCategory']['context_lost']['cases'], 8)
            self.assertIsNone(data['byCategory']['ambiguous']['correct'])


class DiagnosticScoreTests(unittest.TestCase):
    def test_single_token_wwm_is_exactly_variant_pll(self):
        values, context = aggregate([('context', -3), ('variant', -5)], 1, 1)
        self.assertEqual(values['wwm'], values['pll_variant'])
        self.assertEqual(values['pll_full_mean'], -4)

    def test_mask_positions_and_original_targets_for_multitoken_word(self):
        tasks = masked_tasks([11, 12], [21, 22], 0, 2, 99)
        self.assertEqual(len(tasks), 5)
        self.assertEqual(tasks[0], ([0, 99, 12, 21, 22, 2], [1], [11], 'context'))
        self.assertEqual(tasks[-1], ([0, 11, 12, 99, 99, 2], [3, 4], [21, 22], 'wwm'))

    def test_special_tokens_never_become_reconstruction_targets(self):
        tasks = masked_tasks([11], [21], 0, 2, 99)
        self.assertEqual(len(tasks), 2)
        self.assertEqual({t[2][0] for t in tasks}, {11, 21})
