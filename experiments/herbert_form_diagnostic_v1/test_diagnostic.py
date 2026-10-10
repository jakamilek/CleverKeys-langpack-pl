import copy
import tempfile
import unittest
from pathlib import Path

from diagnose import ROOT, check_scores, prepare, rank, read, sha, validate_cases, verify_bundle, verify_freeze


class FixedTokens:
    def encode(self, text):
        return {'left ': [10, 11], 'a': [12], 'ab': [12, 13], 'bad': [3]}[text]


class DiagnosticContractTest(unittest.TestCase):
    def setUp(self):
        self.payload = read(ROOT / 'cases.json')
        self.source = read(ROOT / 'source-fixture.json')

    def test_frozen_gold_and_source_are_all_checked_before_inference(self):
        verify_freeze()
        cases = validate_cases(self.payload, self.source)
        self.assertEqual(24, len(cases))
        self.assertEqual(['form-01'], [c['id'] for c in cases if c['origin'] == 'reported'])

    def test_invented_surface_or_missing_gold_is_rejected(self):
        for replacement in ['Pracaa', 'PRACA']:
            p = copy.deepcopy(self.payload)
            p['cases'][0]['surfaces'][1] = replacement
            with self.assertRaises(ValueError):
                validate_cases(p, self.source)

    def test_same_spelling_without_shared_source_identity_is_rejected(self):
        source = copy.deepcopy(self.source)
        for entry in source['entries']:
            if entry['surfaceKey'] == 'pracą':
                entry['metadata']['sourceEvidence']['lexicalReadings'] = []
        with self.assertRaises(ValueError):
            validate_cases(self.payload, source)

    def test_unrelated_surface_reading_cannot_create_a_false_shared_lemma(self):
        source = copy.deepcopy(self.source)
        for entry in source['entries']:
            if entry['surfaceKey'] == 'pracą':
                for row in entry['metadata']['sourceEvidence']['lexicalReadings']:
                    row['surfaces'] = ['unrelated']
        with self.assertRaises(ValueError):
            validate_cases(self.payload, source)

    def test_duplicate_case_ids_and_partial_dataset_are_rejected(self):
        for mutate in [lambda p: p['cases'].pop(), lambda p: p['cases'][1].update(id='form-01')]:
            p = copy.deepcopy(self.payload)
            mutate(p)
            with self.assertRaises(ValueError):
                validate_cases(p, self.source)

    def test_synthetic_probes_never_require_context_truncation_or_special_masks(self):
        for text in ['word ' * 33, 'a<mask> ', 'Gdzie leży wieś']:
            p = copy.deepcopy(self.payload)
            p['cases'][0]['context'] = text
            with self.assertRaises(ValueError):
                validate_cases(p, self.source)

    def test_two_target_lengths_have_attended_separator_and_unattended_padding(self):
        special = dict(cls=0, sep=1, mask=2, unk=3, pad=4)
        p = prepare(FixedTokens(), special, 'left ', ['a', 'ab'])
        self.assertEqual([[0, 10, 11, 2, 1, 4], [0, 10, 11, 2, 2, 1]], p['input_ids'])
        self.assertEqual([[1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 1]], p['attention_mask'])
        self.assertEqual([[3, 0], [3, 4]], p['target_positions'])
        self.assertEqual([[12, 0], [12, 13]], p['target_ids'])
        self.assertEqual([[1., 0.], [1., 1.]], p['target_mask'])

    def test_unknown_target_and_duplicate_surfaces_are_rejected(self):
        for surfaces in [['bad'], ['a', 'a']]:
            with self.assertRaises(ValueError):
                prepare(FixedTokens(), dict(cls=0, sep=1, mask=2, unk=3, pad=4), 'left ', surfaces)

    def test_live_mean_order_and_diagnostic_sum_can_disagree(self):
        mean, summed = check_scores(['a', 'ab'], {'target_mask': [[1., 0.], [1., 1.]]}, [-2., -1.5], [-2., -3.])
        self.assertEqual(['ab', 'a'], rank(['a', 'ab'], mean))
        self.assertEqual(['a', 'ab'], rank(['a', 'ab'], summed))

    def test_invalid_scores_length_and_mean_sum_consistency_are_rejected(self):
        for means, sums in [([float('nan')], [-2.]), ([-2.], [-5.]), ([], [])]:
            with self.assertRaises(ValueError):
                check_scores(['a'], {'target_mask': [[1.]]}, means, sums)
        for scores in [{'a': -1.}, {'a': -1., 'ab': float('inf')}]:
            with self.assertRaises(ValueError):
                rank(['a', 'ab'], scores)

    def test_ties_keep_each_supplied_candidate_order(self):
        self.assertEqual(['a', 'ab'], rank(['a', 'ab'], {'a': -1., 'ab': -1.}))
        self.assertEqual(['ab', 'a'], rank(['ab', 'a'], {'a': -1., 'ab': -1.}))

    def test_file_hashes_are_external_trust_not_imported_manifest_claims(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'test'
            path.write_bytes(b'known')
            trust = {'test': (5, sha(path))}
            verify_bundle(tmp, trust)
            path.write_bytes(b'other')
            with self.assertRaises(ValueError):
                verify_bundle(tmp, trust)

    def test_unexpected_bundle_member_and_symlink_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            file = directory / 'test'
            file.write_bytes(b'known')
            trust = {'test': (5, sha(file))}
            extra = directory / 'extra'
            extra.write_bytes(b'known')
            with self.assertRaises(ValueError):
                verify_bundle(tmp, trust)
            extra.unlink()
            file.unlink()
            file.symlink_to('/dev/null')
            with self.assertRaises(ValueError):
                verify_bundle(tmp, trust)


if __name__ == '__main__':
    unittest.main()
