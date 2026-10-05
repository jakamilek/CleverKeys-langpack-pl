"""Contract tests reject leakage, incomplete results and wrong word/offset boundaries."""
import copy
import json
import math
import tempfile
import unittest
from collections import Counter
from unittest.mock import patch
import contract
from collect_results import collect
from mlm import target_positions
from make_cases import build


def valid_result():
    cases, entries, request = contract.prepare()
    return {'protocol': contract.VERSION, 'model': contract.MODELS['distilroberta'],
            'phoneMeasured': False, 'requestsSha256': contract.digest(request),
            'predictions': [{'id': r['id'], 'scores': {s: -float(i) for i, s in enumerate(r['candidates'])},
                             'prepareMs': 1., 'inferenceMs': 2., 'totalMs': 3.,
                             'retainedWords': len(r['context'].split())} for r in request['requests']]}


class ContractTests(unittest.TestCase):
    def test_exact_populations_and_saved_generated_cases(self):
        cases, _, request = contract.prepare()
        self.assertEqual(Counter(c['population'] for c in cases),
                         {'regression_v5': 104, 'new_natural': 32, 'new_distance_control': 32, 'new_punctuation': 24})
        self.assertEqual(len(request['requests']), 384)
        self.assertEqual(json.loads((contract.ROOT / 'new-cases.json').read_text()), build())

    def test_label_free_requests_and_preserved_source_forms(self):
        cases, entries, request = contract.prepare()
        for r in request['requests']:
            self.assertEqual(set(r), {'id', 'caseId', 'window', 'context', 'candidates'})
        for c in cases:
            if c['population'].startswith('new_') and c['suite'] == 'forms':
                key = c['candidates'][0]['key']
                self.assertIn(c['goldSurface'], [v['surface'] for v in entries[key]['capitalization']['variants']])

    def test_window_retains_case_punctuation_and_whitespace(self):
        self.assertEqual(contract.retain('Ala\nma  Łódź,\t i łódź.', 3), 'Łódź,\t i łódź.')
        self.assertEqual(contract.retain('Łódź.', 16), 'Łódź.')
        for r in contract.prepare()[2]['requests']:
            self.assertLessEqual(len(r['context'].split()), r['window'])

    def test_distance_cues_visible32_removed16_and_balanced_gold(self):
        cases, _, request = contract.prepare()
        by_id = {r['id']: r for r in request['requests']}
        distant = [c for c in cases if c['population'] == 'new_distance_control']
        self.assertEqual(sum(c['goldSurface'][0].isupper() for c in distant), 16)
        for c in distant:
            self.assertEqual(by_id[c['id'] + '/32']['context'], c['leftContext'])
            self.assertNotEqual(by_id[c['id'] + '/16']['context'], c['leftContext'])

    def test_strict_missing_duplicate_and_wrong_candidate_outputs(self):
        request = contract.prepare()[2]
        for change in ['missing', 'duplicate', 'candidate']:
            r = valid_result()
            if change == 'missing': r['predictions'].pop()
            if change == 'duplicate': r['predictions'].append(r['predictions'][0])
            if change == 'candidate': r['predictions'][0]['scores']['outside'] = 1.
            with self.assertRaises(ValueError): contract.validate_result('distilroberta', request, r)

    def test_wrong_identity_nonfinite_score_and_retained_words(self):
        request = contract.prepare()[2]
        for change in ['revision', 'nan', 'words', 'phone']:
            r = copy.deepcopy(valid_result())
            if change == 'revision': r['model']['revision'] = '0' * 40
            if change == 'nan': r['predictions'][0]['scores'][next(iter(r['predictions'][0]['scores']))] = math.nan
            if change == 'words': r['predictions'][0]['retainedWords'] += 1
            if change == 'phone': r['phoneMeasured'] = True
            with self.assertRaises(ValueError): contract.validate_result('distilroberta', request, r)

    def test_quantile_definition_and_invalid_timings(self):
        self.assertEqual(contract.quantiles(list(range(1, 21))), {'p50': 10.5, 'p95': 19})
        for values in [[], [-1.], [math.nan], [math.inf]]:
            with self.assertRaises(ValueError): contract.quantiles(values)

    def test_offset_boundary_specials_and_whitespace(self):
        self.assertEqual(target_positions('A Łódź', 2, [(0, 0), (0, 1), (1, 3), (3, 6), (0, 0)]), [2, 3])
        with self.assertRaises(ValueError): target_positions('AŁódź', 1, [(0, 3), (3, 5)])
        with self.assertRaises(ValueError): target_positions('A Łódź', 2, [(0, 0), (0, 1)])

    def test_evaluation_separates_populations_and_no_top3_advantage(self):
        report = contract.evaluate('distilroberta', valid_result())
        self.assertIn('new_natural/forms/16', report['groups'])
        self.assertNotIn('all/forms/16', report['groups'])
        self.assertEqual(report['groups']['new_natural/forms/16']['top3'], 32)
        self.assertEqual(report['windowPairs']['new_distance_control/forms']['cases'], 32)

    def test_freeze_detects_modified_executable(self):
        original = contract.Path.read_bytes
        def changed(path):
            data = original(path)
            return data + b'x' if path.name == 'mlm.py' else data
        with patch.object(contract.Path, 'read_bytes', changed):
            with self.assertRaises(ValueError): contract.verify_freeze()

    def test_collector_requires_both_models_and_recomputes_screening(self):
        with tempfile.TemporaryDirectory() as temp:
            root = contract.Path(temp)
            r = valid_result()
            r.update(codeCommit='a' * 40, freezeManifestSha256=contract.digest(contract.verify_freeze()),
                     parameters=1, peakHostRssMiB=1., loadingInfo={})
            folder = root / 'distilroberta'
            folder.mkdir()
            (folder / 'predictions.json').write_bytes(contract.canonical(r))
            with self.assertRaises(ValueError): collect(root)
            folder = root / 'herbert'
            folder.mkdir()
            r['model'] = contract.MODELS['herbert']
            (folder / 'predictions.json').write_bytes(contract.canonical(r))
            with patch.dict('os.environ', {'GITHUB_SHA': 'a' * 40}):
                result = collect(root)
            self.assertTrue(result['screening']['caseOnlyMobileCandidate'])
            self.assertFalse(result['screening']['productionApproved'])
            with patch.dict('os.environ', {'GITHUB_SHA': 'b' * 40}):
                with self.assertRaises(ValueError): collect(root)


if __name__ == '__main__':
    unittest.main()
