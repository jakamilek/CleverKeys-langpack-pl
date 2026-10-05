"""Pure evidence/gate tests; synthetic results never count as model quality."""
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import contract
from collect_results import collect, paired
from projection import scoring_model


def synthetic(name):
    cases, entries, request = contract.prepare()
    by_id = {c['id']: c for c in cases}
    rows = []
    for row in request['requests']:
        order = contract.baseline(by_id[row['caseId']], entries)
        rows.append({'id': row['id'], 'scores': {s: -float(order.index(s)) for s in row['candidates']},
                     'prepareMs': 1., 'inferenceMs': 1., 'totalMs': 2.,
                     'retainedWords': len(row['context'].split())})
    preset = contract.MODELS[name]
    screen = json.loads((contract.ROOT.parent/'polish_mlm_screen_v2'/'results'/
                         (preset['id'].replace('/', '--')+'.json')).read_text())
    return {'protocol': contract.VERSION, 'model': preset, 'requestsSha256': contract.digest(request),
            'freezeManifestSha256': contract.digest(contract.verify_freeze()), 'codeCommit': 'a'*40,
            'tokenizerBackendSha256': screen['backendSha256'], 'predictions': rows,
            'phoneMeasured': False, 'weightsPublished': False, 'parameters': 1,
            'peakHostRssMiB': 1., 'modelFiles': [],
            'loadingInfo': {'missing_keys': [], 'mismatched_keys': [], 'unexpected_keys': [],
                            'error_msgs': [], 'projectionMaxAbsErrors': [0., 0., 0.]}}


def write_synthetic(root, name, result):
    folder = root/name
    folder.mkdir(exist_ok=True)
    (folder/'predictions.json').write_text(json.dumps(result))
    identity = {k: result[k] for k in ['model', 'requestsSha256', 'freezeManifestSha256',
                                      'codeCommit', 'tokenizerBackendSha256']}
    validation = {**identity, 'loadingInfo': result['loadingInfo'], 'modelFiles': result['modelFiles'],
                  'requestsValidated': 384, 'beforeLabelledInference': True}
    preflight = {**identity, 'requestsValidated': 384, 'beforeWeightsLoad': True}
    (folder/'validation.json').write_text(json.dumps(validation))
    (folder/'tokenizer-validation.json').write_text(json.dumps(preflight))


class Gates(unittest.TestCase):
    def test_v1_data_and_scoring_unchanged_except_protocol_label(self):
        old = contract.source_contract.prepare()[2]
        new = contract.prepare()[2]
        self.assertEqual(old['requests'], new['requests'])
        self.assertNotEqual(old['protocol'], new['protocol'])
        self.assertEqual((contract.ROOT/'mlm.py').read_bytes(),
                         (contract.ROOT.parent/'polish_mlm_compare_v1'/'mlm.py').read_bytes())
        self.assertEqual(len(new['requests']), 384)

    def test_historical_reference_is_recomputed_exactly(self):
        result, report = contract.reference()
        self.assertEqual(result['codeCommit'], contract.REFERENCE_COMMIT)
        self.assertEqual(report['groups']['new_natural/forms/32']['top1'], 24)
        self.assertEqual(len(report['decisions']), 384)

    def test_new_model_identity_and_complete_scores_required(self):
        result = synthetic('geotrend_distil')
        for mutate in [lambda r: r['predictions'].pop(),
                       lambda r: r.update(model=contract.MODELS['distilherbert']),
                       lambda r: r['predictions'][0]['scores'].update({next(iter(r['predictions'][0]['scores'])): float('nan')}),
                       lambda r: r.update(phoneMeasured=True)]:
            bad = copy.deepcopy(result); mutate(bad)
            with self.assertRaises(ValueError):
                contract.evaluate('geotrend_distil', bad)

    def test_complete_collector_and_missing_model(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'GITHUB_SHA': 'a'*40}):
            root = Path(tmp)
            write_synthetic(root, 'geotrend_distil', synthetic('geotrend_distil'))
            with self.assertRaises(ValueError): collect(root)
            write_synthetic(root, 'distilherbert', synthetic('distilherbert'))
            output = collect(root)
            self.assertFalse(output['productionApproved'])
            self.assertFalse(output['distilherbertRedistributionApproved'])
            self.assertEqual(output['reference']['codeCommit'], contract.REFERENCE_COMMIT)
            self.assertIn('new_distance_control/forms/32', output['vsHistoricalHerbert']['geotrend_distil'])

    def test_collector_rejects_stale_preflight_and_missing_head(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'GITHUB_SHA': 'a'*40}):
            root = Path(tmp)
            for name in contract.MODELS: write_synthetic(root, name, synthetic(name))
            p = root/'geotrend_distil'/'tokenizer-validation.json'
            good = p.read_text();bad = json.loads(good);bad['beforeWeightsLoad'] = False
            p.write_text(json.dumps(bad))
            with self.assertRaises(ValueError): collect(root)
            p.write_text(good)
            bad = synthetic('distilherbert');bad['loadingInfo']['missing_keys'] = ['cls.predictions.bias']
            write_synthetic(root, 'distilherbert', bad)
            with self.assertRaises(ValueError): collect(root)

    def test_collector_requires_matching_current_run_commit(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {'GITHUB_SHA': 'b'*40}):
            root = Path(tmp)
            for name in contract.MODELS: write_synthetic(root, name, synthetic(name))
            with self.assertRaises(ValueError): collect(root)

    def test_paired_comparison_rejects_changed_source_gold(self):
        report = contract.evaluate('geotrend_distil', synthetic('geotrend_distil'))
        _, original = contract.reference()
        bad = copy.deepcopy(report);bad['decisions'][0]['gold'] = 'changed'
        with self.assertRaises(ValueError): paired(original, bad)

    def test_distil_adapter_delegates_original_forward_and_head(self):
        class Original:
            distilbert = object()
            vocab_transform = staticmethod(lambda x: x+['transform'])
            activation = staticmethod(lambda x: x+['activation'])
            vocab_layer_norm = staticmethod(lambda x: x+['norm'])
            vocab_projector = staticmethod(lambda x: x+['projector'])
            def __call__(self, **kwargs): return kwargs
        model = Original();adapter = scoring_model(model, 'distilbert')
        self.assertIs(adapter.bert, model.distilbert)
        self.assertEqual(adapter.cls.predictions([]), ['transform', 'activation', 'norm', 'projector'])
        self.assertEqual(adapter(input_ids=[7]), {'input_ids': [7]})
        self.assertIs(scoring_model(model, 'bert'), model)


if __name__ == '__main__':
    unittest.main()
