import copy
import json
import unittest

from measure import ROOT, check_neutral_targets, check_reproduction, validate_new_cases, verify_freeze, v1
from policy import context_gain, evaluate, outcomes, rank


def row(identity, mean, gain, gold='Praca', group='short'):
    return dict(id=identity, surfaces=list(mean), gold=gold, meanScores=mean,
                gainScores=gain, suite='forms', population='test', window=group)


class ContextGainTest(unittest.TestCase):
    def test_empty_context_self_comparison_has_zero_scores_and_stable_order(self):
        surfaces = ['Pracą', 'Praca']
        baseline = {'Pracą': -17.0, 'Praca': -12.0}
        scores = context_gain(surfaces, baseline, baseline)
        self.assertEqual(scores, {'Pracą': 0.0, 'Praca': 0.0})
        self.assertEqual(rank(surfaces, scores), surfaces)

    def test_formula_removes_surface_specific_baseline_not_target_count(self):
        surfaces = ['Jagoda', 'jagoda']
        scores = context_gain(surfaces, {'Jagoda': -5.0, 'jagoda': -8.0},
                              {'Jagoda': -6.0, 'jagoda': -13.0})
        self.assertEqual(scores, {'Jagoda': 1.0, 'jagoda': 5.0})
        self.assertEqual(rank(surfaces, scores), ['jagoda', 'Jagoda'])

    def test_same_added_surface_prior_on_both_sides_leaves_gain_unchanged(self):
        surfaces = ['A', 'a']
        a = context_gain(surfaces, {'A': -5, 'a': -8}, {'A': -6, 'a': -13})
        b = context_gain(surfaces, {'A': -105, 'a': -28}, {'A': -106, 'a': -33})
        self.assertEqual(a, b)

    def test_nonfinite_missing_duplicate_and_overflow_scores_are_rejected(self):
        for surfaces, contextual, baseline in [(['x'], {'x': float('nan')}, {'x': -1}),
                                               (['x'], {'x': -1}, {'x': float('inf')}),
                                               (['x'], {'x': -1}, {}),
                                               (['x', 'x'], {'x': -1}, {'x': -2}),
                                               (['x'], {'x': 1e308}, {'x': -1e308}),
                                               (['x'], {'x': True}, {'x': -1})]:
            with self.subTest(surfaces=surfaces, contextual=contextual):
                with self.assertRaises(ValueError):
                    context_gain(surfaces, contextual, baseline)

    def test_correct_form_wrong_case_is_form_success_but_case_failure(self):
        result = outcomes(['Praca', 'praca', 'Pracą', 'pracą'], 'Praca',
                          {'Praca': -2, 'praca': -1, 'Pracą': -3, 'pracą': -4})
        self.assertTrue(result['formComparable'])
        self.assertTrue(result['formTop1'])
        self.assertTrue(result['caseComparable'])
        self.assertFalse(result['exactTop1'])
        self.assertFalse(result['caseGivenGoldForm'])

    def test_wrong_form_can_have_correct_case_given_gold_form(self):
        result = outcomes(['Praca', 'praca', 'Pracą', 'pracą'], 'Praca',
                          {'Praca': -2, 'praca': -3, 'Pracą': -1, 'pracą': -4})
        self.assertFalse(result['formTop1'])
        self.assertTrue(result['caseGivenGoldForm'])
        self.assertFalse(result['exactTop1'])

    def test_case_regression_cannot_hide_behind_unchanged_wrong_form(self):
        data = evaluate([row('a', {'Pracą': -1, 'Praca': -2, 'praca': -3},
                             {'Pracą': 3, 'Praca': 1, 'praca': 2})])
        g = data['groups']['forms/test/short']
        self.assertEqual(g['regressions'], 0)
        self.assertEqual(g['caseRegressions'], 1)
        self.assertFalse(data['preservationPassed'])

    def test_form_regression_cannot_hide_behind_preexisting_case_error(self):
        data = evaluate([row('a', {'praca': -1, 'Praca': -3, 'pracą': -2},
                             {'praca': 2, 'Praca': 1, 'pracą': 3})])
        g = data['groups']['forms/test/short']
        self.assertEqual(g['regressions'], 0)
        self.assertEqual(g['formRegressions'], 1)
        self.assertFalse(data['preservationPassed'])

    def test_repairs_in_one_window_do_not_cancel_regressions_in_another(self):
        a = row('a', {'Praca': -1, 'praca': -2}, {'Praca': 1, 'praca': 2})
        b = row('b', {'Praca': -2, 'praca': -1}, {'Praca': 2, 'praca': 1}, group='long')
        data = evaluate([a, b])
        self.assertEqual(data['groups']['forms/test/short']['regressions'], 1)
        self.assertEqual(data['groups']['forms/test/long']['repairs'], 1)
        self.assertFalse(data['preservationPassed'])

    def test_raw_top3_regression_is_retained_without_top1_regression(self):
        a = row('a', {'a': 4, 'Praca': 3, 'b': 2, 'c': 1},
                {'a': 4, 'Praca': 1, 'b': 3, 'c': 2})
        data = evaluate([a])
        self.assertEqual(data['groups']['forms/test/short']['top3Regressions'], 1)
        self.assertFalse(data['preservationPassed'])

    def test_missing_and_unlabelled_gold_have_explicit_denominators(self):
        data = evaluate([row('a', {'a': -1}, {'a': 1}, gold=None),
                         row('b', {'a': -1}, {'a': 1}, gold='Praca')])
        g = data['groups']['forms/test/short']
        self.assertEqual((g['requests'], g['labelled'], g['missingGold']), (2, 1, 1))
        self.assertEqual((g['formComparable'], g['caseComparable'], g['gainTop1']), (0, 0, 0))

    def test_single_variant_does_not_inflate_case_metric(self):
        result = outcomes(['Praca', 'Pracą'], 'Praca', {'Praca': 2, 'Pracą': 1})
        self.assertFalse(result['caseComparable'])
        self.assertTrue(result['formComparable'])

    def test_empty_and_duplicate_requests_fail(self):
        a = row('a', {'Praca': 1}, {'Praca': 2})
        for rows in [[], [a, a]]:
            with self.assertRaises(ValueError):
                evaluate(rows)

    def test_frozen_chain_and_source_backed_balanced_new_cases(self):
        verify_freeze()

    def test_invented_surface_and_overlapping_new_contexts_fail(self):
        payload = json.loads((ROOT / 'new-cases.json').read_text())
        source = json.loads((ROOT.parent / 'ai_compare_v5/source-snapshot.json').read_text())
        bad = copy.deepcopy(payload)
        bad['cases'][0]['surfaces'][0] = 'invented'
        with self.assertRaises(ValueError):
            validate_new_cases(bad, source, set())
        with self.assertRaises(ValueError):
            validate_new_cases(payload, source, {payload['cases'][0]['context'].strip()})

    def test_original_232_reproduction_rejects_missing_or_changed_context(self):
        old = json.loads((ROOT.parent / 'herbert_form_diagnostic_results/2026-10-10-v2/scores.json').read_text())['predictions']
        check_reproduction(old, old)
        with self.assertRaises(ValueError):
            check_reproduction(old[:-1], old)
        changed = copy.deepcopy(old)
        changed[0]['context'] += 'changed'
        with self.assertRaises(ValueError):
            check_reproduction(changed, old)

    def test_empty_context_masks_have_identical_targets_and_correct_padding(self):
        class Tokenizer:
            def encode(self, text):
                return {'': [], 'word ': [20], 'Praca': [10], 'Pracą': [11, 12]}[text]
        special = dict(cls=0, sep=2, mask=4, pad=1, unk=3)
        empty = v1.prepare(Tokenizer(), special, '', ['Praca', 'Pracą'])
        context = v1.prepare(Tokenizer(), special, 'word ', ['Praca', 'Pracą'])
        check_neutral_targets(empty, context)
        self.assertEqual(empty['input_ids'], [[0, 4, 2, 1], [0, 4, 4, 2]])
        self.assertEqual(empty['attention_mask'], [[1, 1, 1, 0], [1, 1, 1, 1]])
        self.assertEqual(empty['target_positions'], [[1, 0], [1, 2]])
        bad = copy.deepcopy(empty)
        bad['target_ids'][1][1] += 1
        with self.assertRaises(ValueError):
            check_neutral_targets(bad, context)

    def test_unchanged_historical_scores_reproduce_verified_baseline_counts(self):
        history = json.loads((ROOT.parent / 'herbert_form_diagnostic_results/2026-10-10-v2/scores.json').read_text())['predictions']
        data = evaluate([dict(r, gainScores=r['meanScores']) for r in history])
        total = {k: sum(g[k] for g in data['groups'].values()) for k in
                 ['requests', 'labelled', 'missingGold', 'meanTop1', 'gainTop1', 'meanTop3', 'gainTop3']}
        self.assertEqual(total, dict(requests=232, labelled=224, missingGold=4,
                                     meanTop1=157, gainTop1=157, meanTop3=218, gainTop3=218))
        self.assertTrue(data['preservationPassed'])
        self.assertEqual(data['changes'], [])


if __name__ == '__main__':
    unittest.main()
