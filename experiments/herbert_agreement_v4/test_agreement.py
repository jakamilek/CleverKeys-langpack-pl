import copy
import json
import math
import unittest

from agreement import eligibility, form_scores, ordered, ordinal, prepare, probes, rank
from measure import ROOT, validate_cases, verify_freeze, metrics
from source import canonical, needed_keys

SPECIAL = dict(cls=0, sep=2, pad=1, unk=3, mask=4)


class Tokenizer:
    WORDS = {'raz': [10], 'dwa': [11, 12], 'Praca': [20], 'praca': [21],
             'Pracą': [22, 23], 'pracą': [24, 25]}

    def encode(self, text):
        return [token for word in text.split() for token in self.WORDS[word]]


def entry(key, lemma, pos='subst'):
    return dict(capitalization=dict(variants=[dict(surface=key), dict(surface=key.capitalize())]),
                metadata=dict(sourceEvidence=dict(lexicalReadings=[dict(form=key, lemma=lemma, partOfSpeech=pos)])))


class AgreementTest(unittest.TestCase):
    def test_fixed_last_two_lexical_spans_keep_source_spelling(self):
        self.assertEqual(probes('Najpierw, 3. WIELKA rzecz! '), [
            dict(start=13, end=19, text='WIELKA'), dict(start=20, end=25, text='rzecz')])
        self.assertEqual(probes('123. '), [])

    def test_targets_and_positions_are_identical_across_visible_candidates(self):
        labels, feed, selected = prepare(Tokenizer(), SPECIAL, 'raz dwa ', ['Praca', 'Pracą'])
        self.assertEqual(labels, ['0/Praca', '0/Pracą', '1/Praca', '1/Pracą'])
        for i in [0, 2]:
            for field in ['target_ids', 'target_positions', 'target_mask']:
                self.assertEqual(feed[field][i], feed[field][i + 1])
        self.assertEqual(feed['target_ids'], [[10, 0], [10, 0], [11, 12], [11, 12]])
        self.assertEqual(feed['target_positions'], [[1, 0], [1, 0], [2, 3], [2, 3]])
        self.assertEqual(feed['input_ids'][0], [0, 4, 11, 12, 20, 2, 1])
        self.assertEqual(feed['input_ids'][1], [0, 4, 11, 12, 22, 23, 2])
        self.assertEqual(feed['input_ids'][2], [0, 10, 4, 4, 20, 2, 1])
        self.assertEqual(feed['attention_mask'][0], [1, 1, 1, 1, 1, 1, 0])
        self.assertEqual(feed['target_mask'][0], [1., 0.])

    def test_single_row_has_identical_active_target_and_sequence(self):
        _, full, selected = prepare(Tokenizer(), SPECIAL, 'raz dwa ', ['Praca', 'Pracą'])
        _, single, _ = prepare(Tokenizer(), SPECIAL, 'raz dwa ', ['Praca'], [selected[1]])
        for field in ['input_ids', 'attention_mask']:
            self.assertEqual(single[field][0], full[field][2][:len(single[field][0])])
        for field in ['target_ids', 'target_positions', 'target_mask']:
            self.assertEqual(single[field][0], full[field][2])

    def test_eight_rows_bound_and_no_candidate_masking(self):
        surfaces = ['praca', 'Praca', 'pracą', 'Pracą']
        labels, feed, _ = prepare(Tokenizer(), SPECIAL, 'raz dwa ', surfaces)
        self.assertEqual(len(labels), 8)
        for i, label in enumerate(labels):
            active = feed['input_ids'][i][:sum(feed['attention_mask'][i])]
            candidate = Tokenizer().encode(label.split('/')[1])
            self.assertEqual(active[-len(candidate)-1:-1], candidate)
            self.assertEqual(active[-1], SPECIAL['sep'])

    def test_context_special_tokens_empty_and_bad_span_fail(self):
        for context in ['<mask> ', '</s>', 'x' * 4097, '123 ']:
            with self.assertRaises(ValueError):
                prepare(Tokenizer(), SPECIAL, context, ['Praca'])
        with self.assertRaises(ValueError):
            prepare(Tokenizer(), SPECIAL, 'raz ', ['Praca'], [dict(start=0, end=2, text='raz')])

    def test_tokenization_segment_parity_is_required(self):
        class Bad(Tokenizer):
            def encode(self, text):
                return [99] if text == 'raz dwa ' else super().encode(text)
        with self.assertRaisesRegex(ValueError, 'segment token parity'):
            prepare(Bad(), SPECIAL, 'raz dwa ', ['Praca'])

    def test_candidate_full_sentence_token_parity_is_required(self):
        class Bad(Tokenizer):
            def encode(self, text):
                return [99] if text == 'raz dwa  Praca' else super().encode(text)
        with self.assertRaisesRegex(ValueError, 'visible candidate token parity'):
            prepare(Bad(), SPECIAL, 'raz dwa ', ['Praca'])

    def test_target_unknown_and_excessive_width_fail(self):
        class Bad(Tokenizer):
            def encode(self, text):
                return [3] if text == 'dwa' else super().encode(text)
        with self.assertRaises(ValueError):
            prepare(Bad(), SPECIAL, 'dwa ', ['Praca'])
        with self.assertRaisesRegex(ValueError, 'sequence budget'):
            prepare(Tokenizer(), SPECIAL, 'raz ' * 512, ['Praca'])

    def test_declared_source_lemma_and_pos_gate(self):
        entries = {'kot': entry('kot', 'kot'), 'kotem': entry('kotem', 'kot')}
        self.assertEqual(eligibility(['kot', 'Kot', 'kotem', 'Kotem'], entries), 'eligible_source_lemma_pos')
        changed = copy.deepcopy(entries)
        changed['kotem']['metadata']['sourceEvidence']['lexicalReadings'][0]['partOfSpeech'] = 'adj'
        self.assertEqual(eligibility(['kot', 'kotem'], changed), 'unrelated_or_unknown_source')
        self.assertEqual(eligibility(['KOT', 'kotem'], entries), 'undeclared_variant')

    def test_fold_case_only_and_unrelated_slates_have_distinct_scope(self):
        self.assertEqual(eligibility(['praca', 'pracą'], {}), 'eligible_fold')
        self.assertEqual(eligibility(['kot', 'Kot'], {}), 'case_only')
        self.assertEqual(eligibility(['kot', 'dom'], {}), 'unrelated_or_unknown_source')
        self.assertEqual(eligibility(['kot', 'Kot', 'dom', 'Dom', 'las'], {}), 'outside_two_key_four_surface_scope')

    def test_generated_and_interpretation_proof_paths(self):
        a = entry('kot', 'kot')
        for name, reading in [('generatedFormProofs', dict(form='kotem', lemma='kot', tag='subst:sg:inst:m1')),
                              ('interpretations', dict(surfaces=['Kotem'], lemma='kot', partOfSpeech='subst'))]:
            b = dict(capitalization=dict(variants=[dict(surface='kotem')]),
                     metadata=dict(sourceEvidence={name: [reading]}))
            self.assertEqual(eligibility(['kot', 'kotem'], {'kot': a, 'kotem': b}), 'eligible_source_lemma_pos')

    def test_case_pool_normalizes_variant_count_and_averages_fixed_probes(self):
        surfaces = ['praca', 'Praca', 'pracą']
        score = {f'{i}/{s}': (-2. if i == 0 else -4.) for i in range(2) for s in surfaces}
        self.assertEqual(form_scores(surfaces, score, 2), {'praca': -3., 'pracą': -3.})
        score['0/Praca'] = -4.
        expected = (-2 + math.log((1 + math.exp(-2)) / 2) - 4) / 2
        self.assertAlmostEqual(form_scores(surfaces, score, 2)['praca'], expected)

    def test_pool_stable_extreme_scores_and_ties(self):
        surfaces = ['Pracą', 'Praca']
        scores = {'0/Pracą': -1e6, '0/Praca': -1e6}
        keys = form_scores(surfaces, scores, 1)
        self.assertEqual(rank(list(keys), keys), ['pracą', 'praca'])
        self.assertEqual(keys['praca'], -1e6)

    def test_score_identity_nonfinite_and_boolean_fail(self):
        for bad in [{}, {'0/Praca': float('inf')}, {'0/Praca': True}]:
            with self.assertRaises(ValueError):
                form_scores(['Praca'], bad, 1)
        with self.assertRaises(ValueError):
            rank(['Praca', 'Praca'], {'Praca': 1})

    def test_form_first_then_unchanged_case_keeps_all_alternatives(self):
        surfaces = ['Pracą', 'pracą', 'Praca', 'praca']
        case = dict(Pracą=-1, pracą=-4, Praca=-3, praca=-2)
        proposal = ordered(surfaces, case, {'praca': -1, 'pracą': -2})
        self.assertEqual(proposal, ['praca', 'Pracą', 'Praca', 'pracą'])
        self.assertEqual(set(proposal), set(surfaces))
        baseline = ordered(surfaces, case)
        self.assertEqual(baseline, ['Pracą', 'praca', 'Praca', 'pracą'])
        self.assertEqual(baseline[0], rank(surfaces, case)[0])
        for key in ['praca', 'pracą']:
            self.assertEqual([s for s in proposal if s.lower() == key][0],
                             [s for s in baseline if s.lower() == key][0])

    def test_metric_regression_not_hidden_by_other_repairs(self):
        a = dict(id='a', surfaces=['Praca', 'Pracą'], gold='Praca', suite='new', population='one', window='short',
                 meanScores=ordinal(['Praca', 'Pracą']), gainScores=ordinal(['Pracą', 'Praca']))
        b = dict(a, id='b', population='two', gold='Pracą')
        report = metrics.evaluate([a, b])
        self.assertEqual(report['groups']['new/one/short']['formRegressions'], 1)
        self.assertEqual(report['groups']['new/two/short']['formRepairs'], 1)
        self.assertFalse(report['preservationPassed'])

    def test_frozen_source_balanced_cases_and_original_entries_are_exact(self):
        verify_freeze()
        fixture = json.loads((ROOT / 'source-fixture.json').read_text())
        self.assertEqual(len(needed_keys()), 21)
        self.assertEqual(canonical(fixture), (ROOT / 'source-fixture.json').read_bytes())
        entries = {e['surfaceKey']: e for e in fixture['entries']}
        old = json.loads((ROOT.parent / 'herbert_form_diagnostic_v1/source-fixture.json').read_text())
        for e in old['entries']:
            self.assertEqual(entries[e['surfaceKey']], e)

    def test_invented_candidate_and_overlapping_contexts_fail(self):
        payload = json.loads((ROOT / 'new-forms.json').read_text())
        fixture = json.loads((ROOT / 'source-fixture.json').read_text())
        bad = copy.deepcopy(payload)
        bad['cases'][0]['surfaces'][0] = 'invented'
        with self.assertRaises(ValueError):
            validate_cases(bad, fixture, set())
        with self.assertRaises(ValueError):
            validate_cases(payload, fixture, {payload['cases'][0]['context'].strip()})


if __name__ == '__main__':
    unittest.main()
