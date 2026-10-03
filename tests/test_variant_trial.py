import copy
import io
import json
import struct
import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_variant_trial import (build_trial, canonical_bytes, compile_intelligence,
                                 dictionary_entries, read_json, sha256)

FIXTURE = ROOT / 'tests/fixtures/source-casing-proof-v1.json'
FIXTURE_SHA = '6bbdf928c338d44ab3eddb76f8a1fe9f0b4a789cb1d51f55740f55826a21e2e2'


def dictionary(words):
    raw = bytearray(48)
    raw[:4] = b'CKDT'
    struct.pack_into('<I', raw, 4, 2)
    struct.pack_into('<II', raw, 12, len(words), 48)
    for rank, word in enumerate(words):
        encoded = word.encode('utf-8')
        raw.extend(struct.pack('<H', len(encoded)) + encoded + bytes([rank]))
    return bytes(raw)


def make_base(raw_dictionary, duplicate=False, traversal=False):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as archive:
        archive.writestr('dictionary.bin', raw_dictionary)
        archive.writestr('manifest.json', canonical_bytes({
            'code': 'pl', 'name': 'Polish', 'version': 2,
            'wordCount': len(dictionary_entries(raw_dictionary)), 'hasPrefixBoost': False}))
        archive.writestr('unigrams.txt', b'unchanged\n')
        if duplicate:
            archive.writestr('dictionary.bin', raw_dictionary)
        if traversal:
            archive.writestr('../NOTICE.txt', b'not an allowed member')
    return out.getvalue()


class VariantTrialTest(unittest.TestCase):
    def setUp(self):
        self.evidence = read_json(FIXTURE.read_bytes())
        self.canonical = {e['surfaceKey']: e['capitalization']['defaultSurface'] for e in self.evidence['entries']}

    def build_fixture(self, duplicate=False, traversal=False):
        # Small synthetic container; linguistic evidence is the unmodified frozen source fixture.
        raw_dictionary = dictionary(sorted(self.canonical))
        base = make_base(raw_dictionary, duplicate, traversal)
        evidence = copy.deepcopy(self.evidence)
        evidence['provenance']['artifact']['packageSha256'] = sha256(base)
        evidence['provenance']['artifact']['dictionarySha256'] = sha256(raw_dictionary)
        raw_evidence = canonical_bytes(evidence)
        return base, raw_evidence, raw_dictionary

    def test_frozen_source_fixture(self):
        self.assertEqual(sha256(FIXTURE.read_bytes()), FIXTURE_SHA)

    def test_nine_source_entries_and_full_evidence_preserved(self):
        result = compile_intelligence(self.evidence, self.canonical)
        self.assertEqual(len(result['entries']), 9)
        self.assertEqual(result['provenance'], self.evidence['provenance'])
        original = {e['surfaceKey']: e for e in self.evidence['entries']}
        for entry in result['entries']:
            source = original[entry['surfaceKey']]
            self.assertEqual(entry['canonicalForm'], source['capitalization']['defaultSurface'])
            for field in ('interpretations', 'generatedFormProofs', 'sourceRecords', 'categories'):
                self.assertEqual(entry['metadata']['sourceEvidence'][field], source[field])
        forms = {e['surfaceKey']: [v['surface'] for v in e['capitalization']['variants']] for e in result['entries']}
        self.assertEqual(forms['łódź'], ['łódź', 'Łódź'])
        self.assertEqual(forms['warszawska'], ['warszawska', 'Warszawska'])
        self.assertEqual(forms['łódzki'], ['łódzki'])

    def test_deterministic_pack_roundtrip_and_unchanged_lexicon(self):
        base, evidence, raw_dictionary = self.build_fixture()
        args = (base, evidence, b'source notice\n', sha256(evidence))
        package, sidecar, report = build_trial(*args)
        self.assertEqual(build_trial(*args), (package, sidecar, report))
        with zipfile.ZipFile(io.BytesIO(package)) as archive:
            self.assertEqual(archive.read('dictionary.bin'), raw_dictionary)
            self.assertEqual(archive.read('unigrams.txt'), b'unchanged\n')
            manifest = read_json(archive.read('manifest.json'))
            self.assertEqual(manifest['apiVersion'], 1)
            self.assertEqual(manifest['version'], 3)
            self.assertEqual(manifest['languageIntelligence']['sha256'], sha256(sidecar))
            self.assertEqual(archive.read('language-intelligence.json'), sidecar)
            self.assertEqual(archive.read('NOTICE.txt'), b'source notice\n')
            self.assertTrue(all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in archive.infolist()))
        self.assertEqual(report['dualVariantEntries'], 8)
        self.assertEqual(report['singleVariantEntries'], 1)
        self.assertTrue(report['trialOnly'])

    def test_evidence_hash_mismatch(self):
        base, evidence, _ = self.build_fixture()
        with self.assertRaisesRegex(ValueError, 'evidence checksum'):
            build_trial(base, evidence, b'notice', '0' * 64)

    def test_base_snapshot_mismatch(self):
        base, evidence, _ = self.build_fixture()
        with self.assertRaisesRegex(ValueError, 'base package'):
            build_trial(base + b'x', evidence, b'notice', sha256(evidence))

    def test_dictionary_evidence_mismatch(self):
        base, evidence, _ = self.build_fixture()
        data = read_json(evidence)
        data['provenance']['artifact']['dictionarySha256'] = '0' * 64
        changed = canonical_bytes(data)
        with self.assertRaisesRegex(ValueError, 'dictionary differs'):
            build_trial(base, changed, b'notice', sha256(changed))

    def test_duplicate_archive_member(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            base, evidence, _ = self.build_fixture(duplicate=True)
        with self.assertRaisesRegex(ValueError, 'duplicate base ZIP'):
            build_trial(base, evidence, b'notice', sha256(evidence))

    def test_archive_path_member_rejected(self):
        base, evidence, _ = self.build_fixture(traversal=True)
        with self.assertRaisesRegex(ValueError, 'base ZIP'):
            build_trial(base, evidence, b'notice', sha256(evidence))

    def test_notice_required(self):
        base, evidence, _ = self.build_fixture()
        with self.assertRaisesRegex(ValueError, 'notice'):
            build_trial(base, evidence, b'', sha256(evidence))

    def test_unknown_evidence_schema(self):
        self.evidence['schemaVersion'] = 2
        with self.assertRaisesRegex(ValueError, 'evidence version'):
            compile_intelligence(self.evidence, self.canonical)

    def test_duplicate_sidecar_key(self):
        self.evidence['entries'].append(copy.deepcopy(self.evidence['entries'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            compile_intelligence(self.evidence, self.canonical)

    def test_key_absent_from_lexicon(self):
        self.canonical.pop('łódź')
        with self.assertRaisesRegex(ValueError, 'missing'):
            compile_intelligence(self.evidence, self.canonical)

    def test_source_default_cannot_override_ckdt(self):
        self.canonical['łódź'] = 'Łódź'
        with self.assertRaisesRegex(ValueError, 'default differs'):
            compile_intelligence(self.evidence, self.canonical)

    def test_unsupported_case_policy(self):
        self.evidence['entries'][0]['capitalization']['variants'][0]['casePolicy'] = 'invented'
        with self.assertRaisesRegex(ValueError, 'variant'):
            compile_intelligence(self.evidence, self.canonical)

    def test_no_fabricated_capitalized_adjective(self):
        entry = next(e for e in self.evidence['entries'] if e['surfaceKey'] == 'łódzki')
        entry['capitalization']['variants'].append({'surface': 'Łódzki', 'casePolicy': 'capitalized', 'categoryIds': ['POS:adj']})
        with self.assertRaisesRegex(ValueError, 'proof'):
            compile_intelligence(self.evidence, self.canonical)

    def test_changed_interpretation_detected(self):
        self.evidence['entries'][0]['interpretations'][0]['labels'].append('invented')
        with self.assertRaisesRegex(ValueError, 'source interpretation'):
            compile_intelligence(self.evidence, self.canonical)

    def test_swapped_category_form_mapping_detected(self):
        variants = self.evidence['entries'][0]['capitalization']['variants']
        variants[0]['categoryIds'], variants[1]['categoryIds'] = variants[1]['categoryIds'], variants[0]['categoryIds']
        with self.assertRaisesRegex(ValueError, 'association changed'):
            compile_intelligence(self.evidence, self.canonical)

    def test_orphan_generated_proof_detected(self):
        self.evidence['entries'][0]['generatedFormProofs'][0]['interpretationId'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'dangling'):
            compile_intelligence(self.evidence, self.canonical)

    def test_duplicate_ckdt_case_key_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate lowercase CKDT'):
            dictionary_entries(dictionary(['łódź', 'Łódź']))

    def test_truncated_ckdt_rejected(self):
        with self.assertRaisesRegex(ValueError, 'truncated'):
            dictionary_entries(dictionary(['łódź'])[:-1])

    def test_duplicate_json_fields_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate JSON'):
            read_json(b'{"schemaVersion":1,"schemaVersion":2}')


if __name__ == '__main__':
    unittest.main()
