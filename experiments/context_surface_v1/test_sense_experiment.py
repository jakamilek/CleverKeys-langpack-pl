"""Meaning-association and user top-3 contract checks; no model download in CI."""
import copy
import unittest

from prototype import digest, validate_predictions
from sense_experiment import (MAIN, archived_prediction, build_fixture, evaluate,
                              hypotheses, prepare_senses, validate_senses)


class SenseExperimentTest(unittest.TestCase):
    def setUp(self):
        self.cases, self.sidecar = build_fixture()
        self.request = prepare_senses(self.cases, self.sidecar)

    def test_gold_labels_do_not_enter_model_requests(self):
        for row in self.request['requests']:
            self.assertNotIn('expected', row)
            self.assertNotIn('diagnostic', row)
            self.assertNotIn('sourceId', row)
        self.assertEqual(digest({k: v for k, v in self.request.items() if k != 'requestSha256'}),
                         self.request['requestSha256'])

    def test_original_contexts_and_probe_partition(self):
        import json
        from sense_experiment import ROOT
        original = json.loads((ROOT/'diagnostic-cases.json').read_text())
        self.assertEqual(self.cases['cases'][:48], original['cases'])
        self.assertEqual(len(self.cases['cases']), 80)
        self.assertEqual(len(self.request['requests']), 160)
        self.assertEqual(sum(c['diagnostic']['category'] in MAIN for c in self.cases['cases']), 32)
        originals = {c['id']: c for c in original['cases']}
        for probe in self.cases['cases'][48:]:
            source = originals[probe['diagnostic']['sourceId']]
            self.assertEqual(probe['beforeCursor'], source['beforeCursor'])
            self.assertEqual(probe['expected'], source['expected'])
            self.assertEqual(probe['candidates'][1]['surface'], source['expected']['surfaceKey'])

    def test_single_key_two_surfaces_with_explicit_senses(self):
        entries = validate_senses(self.sidecar)
        boat = entries['łódź']
        self.assertEqual([v['senseIds'] for v in boat['capitalization']['variants']], [['boat'], ['city']])
        self.assertEqual(len(entries), 4)

    def test_reject_dangling_or_duplicate_sense_references(self):
        broken = copy.deepcopy(self.sidecar)
        broken['entries'][0]['capitalization']['variants'][0]['senseIds'] = ['missing']
        with self.assertRaises(ValueError):
            validate_senses(broken)
        broken = copy.deepcopy(self.sidecar)
        broken['entries'][0]['senses'].append(broken['entries'][0]['senses'][0])
        with self.assertRaises(ValueError):
            validate_senses(broken)

    def test_multiple_senses_may_share_a_surface(self):
        changed = copy.deepcopy(self.sidecar)
        changed['entries'][0]['senses'].append(
            {'id': 'vessel_other', 'kind': 'common_noun', 'descriptionPl': 'inny statek'})
        changed['entries'][0]['capitalization']['variants'][0]['senseIds'].append('vessel_other')
        validate_senses(changed)

    def test_swap_is_mapping_control_and_generic_has_no_descriptions(self):
        group = self.request['requests'][0]['candidates'][0]
        intact, swapped = hypotheses(group, 'attributes'), hypotheses(group, 'swapped_attributes')
        self.assertEqual(intact['łódź'], swapped['Łódź'])
        self.assertEqual(intact['Łódź'], swapped['łódź'])
        generic = str(hypotheses(group, 'no_attributes'))
        self.assertNotIn('jednostkę pływającą', generic)
        self.assertNotIn('miasto', generic)

    def test_top3_has_real_pressure_in_separate_probe(self):
        report = evaluate(self.cases, self.request)
        self.assertEqual(report['metrics']['long']['main']['displayTop3Correct'], 32)
        probe = report['metrics']['long']['top3_probe']
        self.assertEqual(probe['displayTop1Correct'], 0)
        self.assertEqual(probe['displayTop3Correct'], 16)
        self.assertEqual(probe['expectedSurfaceReachable'], 32)

    def test_unlabelled_cases_have_no_accuracy(self):
        report = evaluate(self.cases, self.request)
        self.assertIsNone(report['metrics']['long']['ambiguous']['displayTop3Correct'])

    def test_archive_replay_preserves_baseline_and_missing_competitor(self):
        import json
        from sense_experiment import ROOT
        archived = json.loads((ROOT/'diagnostic-results-2026-10-02/diagnostic-polbert-wwm.json').read_text())
        prediction = archived_prediction(self.request, archived, self.cases)
        validate_predictions(prediction, self.request)
        report = evaluate(self.cases, self.request, prediction)
        self.assertEqual(report['metrics']['long']['main']['displayTop1Correct'], 23)
        self.assertEqual(report['metrics']['long']['top3_probe']['displayTop3Correct'], 23)
        self.assertTrue(prediction['unscoredCompetitorsUseNeutralDefault'])


if __name__ == '__main__':
    unittest.main()
