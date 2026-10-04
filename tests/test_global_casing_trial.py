import io
import json
import struct
import sys
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import morfeusz2
from build_variant_trial import canonical_bytes, dictionary_entries, read_json, sha256
from build_global_casing_trial import SourceOracle, classify, build_global_trial
from capitalization_rules import resolve_capitalization
from test_function_word_trial import dictionary


def base_pack(words, entries=()):
    side = canonical_bytes({'schemaVersion': 1, 'languageCode': 'pl', 'entries': list(entries)})
    members = {'dictionary.bin': dictionary(words), 'unigrams.txt': b'unchanged\n',
               'NOTICE.txt': b'Original source attribution\n', 'language-intelligence.json': side,
               'manifest.json': canonical_bytes({'code': 'pl', 'version': 4, 'apiVersion': 1,
                    'wordCount': len(words), 'capabilities': ['lexicon', 'frequency', 'capitalization', 'metadata'],
                    'languageIntelligence': {'sha256': sha256(side)}})}
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as archive:
        for name, data in members.items(): archive.writestr(name, data)
    return out.getvalue(), members


class GlobalCasingTrialTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = morfeusz2.Morfeusz(case_handling=morfeusz2.CONDITIONALLY_CASE_SENSITIVE)

    def decision(self, key, current=None):
        evidence = SourceOracle(self.oracle).evidence(key)
        return classify(key, current or key, evidence), evidence

    def build(self, words, entries=()):
        raw, members = base_pack(words, entries)
        audit = io.BytesIO()
        result, report = build_global_trial(raw, self.oracle, {'testSnapshot': True}, audit,
                                             expected_sha256=sha256(raw))
        with zipfile.ZipFile(io.BytesIO(result)) as archive:
            output = {n: archive.read(n) for n in archive.namelist()}
        return result, report, audit.getvalue(), members, output

    def test_real_homonyms_keep_ordinary_and_name_readings(self):
        for key in ['ale', 'lub', 'tutaj', 'malina', 'warszawska', 'łódź']:
            with self.subTest(key=key):
                d, e = self.decision(key, key.capitalize())
                self.assertEqual(d['defaultSurface'], key)
                self.assertEqual(d['attestedForms'], [key, key.capitalize()])
                self.assertTrue(d['ordinaryLower'] and d['properUpper'])
                self.assertTrue(any(i['nameClasses'] for i in e['interpretations']))

    def test_adverbs_and_verbs_are_not_limited_to_function_word_pos(self):
        for key in ['tutaj', 'bada', 'bać', 'bał']:
            d, _ = self.decision(key, key.capitalize())
            self.assertEqual(d['defaultSurface'], key)
            self.assertTrue(d['ordinaryLower'])

    def test_proper_only_names_do_not_get_a_fabricated_lower_variant(self):
        for key in ['jan', 'ala', 'maria']:
            d, _ = self.decision(key, key.capitalize())
            self.assertFalse(d['ordinaryLower'])
            self.assertEqual(d['attestedForms'], [key.capitalize()])

    def test_capitalized_probe_does_not_fabricate_a_capitalized_adjective(self):
        d, _ = self.decision('łódzki')
        self.assertEqual(d['attestedForms'], ['łódzki'])

    def test_fragment_analyses_cannot_prove_whole_word_case(self):
        class Oracle:
            def analyse(self, surface): return [(0, 1, ('no', 'no', 'part', [], []))]
            def generate(self, lemma): return [('no', 'no', 'part', [], [])]
        self.assertEqual(SourceOracle(Oracle()).evidence('nobody')['interpretations'], [])

    def test_exact_generated_case_is_required_even_without_name_labels(self):
        class Oracle:
            def analyse(self, surface): return [(0, 1, (surface, 'Nova', 'brev:npun', [], []))]
            def generate(self, lemma): return [('Nova', lemma, 'brev:npun', [], [])]
        e = SourceOracle(Oracle()).evidence('nova')
        d = classify('nova', 'Nova', e)
        self.assertFalse(d['ordinaryLower'])
        self.assertEqual(d['attestedForms'], ['Nova'])

    def test_generation_with_a_different_tag_cannot_link_an_interpretation(self):
        class Oracle:
            def analyse(self, surface): return [(0, 1, (surface, 'x', 'impt:sg:sec:imperf', [], []))]
            def generate(self, lemma): return [('x', lemma, 'fin:sg:ter:imperf', [], [])]
        self.assertEqual(SourceOracle(Oracle()).evidence('x')['interpretations'], [])

    def test_every_key_is_audited_and_ckdt_rank_sections_are_preserved(self):
        _, report, audit, old, new = self.build(['Tutaj', 'ale', 'lub', 'jan', 'Qzxfoo'])
        records = [json.loads(l) for l in audit.splitlines()]
        self.assertEqual([r['surfaceKey'] for r in records], ['tutaj', 'ale', 'lub', 'jan', 'qzxfoo'])
        self.assertEqual(report['coverage']['auditedKeys'], 5)
        self.assertEqual(report['auditSha256'], sha256(audit))
        self.assertEqual(list(dictionary_entries(old['dictionary.bin'])), list(dictionary_entries(new['dictionary.bin'])))
        self.assertEqual(dictionary_entries(new['dictionary.bin'])['tutaj'], 'tutaj')
        self.assertEqual(dictionary_entries(new['dictionary.bin'])['jan'], 'Jan')
        self.assertEqual(dictionary_entries(new['dictionary.bin'])['qzxfoo'], 'Qzxfoo')
        for raw in [old['dictionary.bin'], new['dictionary.bin']]:
            offset = 48
            for rank in range(5):
                n = struct.unpack_from('<H', raw, offset)[0]
                self.assertEqual(raw[offset + 2 + n], rank)
                offset += 3 + n
        start, normalized = struct.unpack_from('<II', old['dictionary.bin'], 16)
        self.assertEqual(old['dictionary.bin'][:start], new['dictionary.bin'][:start])
        self.assertEqual(old['dictionary.bin'][normalized:], new['dictionary.bin'][normalized:])
        self.assertEqual(old['unigrams.txt'], new['unigrams.txt'])

    def test_runtime_readings_retain_source_lemmas_classes_and_surface_links(self):
        _, _, audit, _, new = self.build(['Ale', 'Lub', 'Tutaj'])
        side = read_json(new['language-intelligence.json'])
        full = {r['surfaceKey']: r for r in map(json.loads, audit.splitlines())}
        for entry in side['entries']:
            key = entry['surfaceKey']
            readings = entry['metadata']['sourceEvidence']['lexicalReadings']
            for source in full[key]['interpretations']:
                matches = [r for r in readings if r['lemma'] == source['lemma']
                           and r['partOfSpeech'] == source['tag'].split(':')[0]
                           and r['nameClasses'] == source['nameClasses'] and r['labels'] == source['labels']]
                self.assertEqual(len(matches), 1)
                forms = sorted({p['form'] for p in full[key]['generatedFormProofs']
                                if p['interpretationId'] == source['id']})
                self.assertTrue(set(forms) <= set(matches[0]['surfaces']))
            self.assertEqual(entry['capitalization']['defaultSurface'], key)

    def test_historical_richer_metadata_is_preserved_when_default_is_unchanged(self):
        entry = {'surfaceKey': 'łódź', 'canonicalForm': 'łódź',
                 'capitalization': {'defaultSurface': 'łódź', 'variants': [
                     {'surface': 'łódź', 'casePolicy': 'lowercase'}, {'surface': 'Łódź', 'casePolicy': 'capitalized'}]},
                 'metadata': {'sourceEvidence': {'sourceRecords': {'GUS': ['historical-proof']}}}}
        _, _, _, _, new = self.build(['łódź', 'Tutaj'], [entry])
        side = read_json(new['language-intelligence.json'])
        self.assertEqual(next(e for e in side['entries'] if e['surfaceKey'] == 'łódź'), entry)

    def test_deterministic_archive_manifest_and_audit_provenance(self):
        result, report, audit, _, output = self.build(['Tutaj', 'ale', 'lub'])
        self.assertEqual(result, self.build(['Tutaj', 'ale', 'lub'])[0])
        manifest = read_json(output['manifest.json'])
        self.assertEqual(manifest['version'], 5)
        self.assertEqual(manifest['languageIntelligence']['sha256'], sha256(output['language-intelligence.json']))
        side = read_json(output['language-intelligence.json'])
        self.assertEqual(side['provenance']['fullAudit']['sha256'], sha256(audit))
        self.assertEqual(report['packageSha256'], sha256(result))

    def test_bad_input_checksum_and_runtime_complexity_are_rejected(self):
        raw, _ = base_pack(['Tutaj'])
        with self.assertRaisesRegex(ValueError, 'checksum'):
            build_global_trial(raw, self.oracle, {}, io.BytesIO())
        with patch('build_global_casing_trial.json_nodes', return_value=1_000_001):
            with self.assertRaisesRegex(ValueError, 'Android'):
                self.build(['Tutaj'])

    def test_shared_future_resolver_prefers_generated_ordinary_usage_and_keeps_names(self):
        d = resolve_capitalization(key='tutaj', morfeusz=self.oracle)
        self.assertEqual(d['surface'], 'tutaj')
        self.assertEqual(d['reason'], 'attested-ordinary-form-default-lowercase')
        self.assertTrue(d['proper_name_matches'])
        self.assertEqual(resolve_capitalization(key='jan', morfeusz=self.oracle)['surface'], 'Jan')


if __name__ == '__main__': unittest.main()
