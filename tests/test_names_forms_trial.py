import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import morfeusz2
import build_names_forms_trial as trial
from build_global_casing_trial import SourceOracle
from build_common_forms_trial import compact_entry
from build_variant_trial import canonical_bytes, sha256
from test_common_forms_trial import dictionary


class NamesFormsTrialTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = morfeusz2.Morfeusz(case_handling=morfeusz2.CONDITIONALLY_CASE_SENSITIVE)
        cls.source = trial.NameOracle(cls.oracle)

    def base(self):
        entries = [compact_entry(k, SourceOracle(self.oracle).evidence(k)) for k in ['kasa', 'malina']]
        side = canonical_bytes(dict(schemaVersion=1, languageCode='pl', entries=entries,
                                    provenance=dict(previous='unchanged')))
        members = {'dictionary.bin': dictionary([('kasa', 33), ('malina', 44)]),
            'language-intelligence.json': side, 'unigrams.txt': b'unchanged frequencies\n',
            'NOTICE.txt': b'Original credit\n', 'manifest.json': canonical_bytes(dict(
                code='pl', version=7, apiVersion=1, wordCount=2, attribution='Original',
                capabilities=['metadata', 'capitalization'], languageIntelligence=dict(
                    file='language-intelligence.json', schemaVersion=1, sha256=sha256(side))))}
        return trial.write_pack(members), members

    def build(self, out, words=('google', 'usb', 'jana', 'from', 'qzzfoo'), foreign=None):
        raw, members = self.base()
        values = {'kasa': 5, 'malina': 3, 'google': 4, 'usb': 3, 'jana': 4, 'jan': 5,
                  'from': 4, 'qzzfoo': 6}
        report = trial.build(raw, out, self.oracle, list(words), lambda w: values.get(w.lower(), 0),
            lambda w: 10 ** values.get(w.lower(), 0), {'Oleksandr'}, {'test': True},
            sha256(raw), sha256(members['dictionary.bin']), foreign_zipf=foreign)
        return report, members

    def test_only_atomic_alphabetic_forms_and_exact_generator_case(self):
        for w in ['np.', 'czarno-biały', 'Google’a', 'San Francisco', 'F16', 'a', 'q'*26]:
            self.assertFalse(trial.candidate(w), w)
        self.assertTrue(trial.candidate('Linux'))
        self.assertTrue(trial.candidate('USB'))
        evidence = self.source.evidence('malina')
        self.assertNotIn('MALINA', {p['form'] for p in evidence['generatedFormProofs']})
        self.assertEqual(self.source.evidence('qzzfoo')['interpretations'], [])
        # A component of a name is not an independently attested whole name.
        r = dict(id='x', lemma='x', tag='subst:sg:nom:m3', nameClasses=['człon_nazwy_firmy'], labels=[])
        self.assertEqual(trial.admissions('xx', dict(interpretations=[r],
            generatedFormProofs=[dict(form='Xx', interpretationId='x')]), set()), [])

    def test_source_case_not_forced_and_family_anchor_beats_acronym_collision(self):
        surface, e = trial.entry('jana', self.source.evidence('jana'),
            lambda w: {'Jan': 5, 'JANA': 3}.get(w, 0))
        self.assertEqual(surface, 'Jana')
        self.assertIn('JANA', {s for r in e['metadata']['sourceEvidence']['lexicalReadings'] for s in r['surfaces']})
        surface, e = trial.entry('usb', self.source.evidence('usb'))
        self.assertEqual(surface, 'USB')
        self.assertNotIn('capitalization', e)  # API-v1 never receives an unsupported all-caps policy.
        self.assertEqual(trial.entry('malina', self.source.evidence('malina'))[0], 'malina')
        surface, e = trial.entry('bps', self.source.evidence('bps'))
        self.assertEqual(surface, 'BPS')  # brev:npun is not an ordinary noun case default.

    def test_common_class_alias_and_obsolete_reading_do_not_invent_case(self):
        r = dict(id='x', lemma='xx', tag='subst:sg:nom:m3', nameClasses=['nazwa pospolita'], labels=[])
        self.assertEqual(trial.proper_classes(r), set())
        e = dict(interpretations=[r], generatedFormProofs=[dict(form='xx', interpretationId='x')])
        self.assertEqual(trial.entry('xx', e)[0], 'xx')
        self.assertFalse(trial.current({**r, 'labels': ['hist.']}))
        self.assertFalse(trial.current({**r, 'tag': 'brev:pun'}))

    def test_explicit_source_exclusions_are_pinned_and_apply_to_inflections(self):
        path = Path(__file__).resolve().parents[1] / 'sources/staging/first_name_source_exclusions.tsv'
        self.assertIn('Oleksandr', trial.load_exclusions(path))
        eligible = trial.admissions('oleksandra', self.source.evidence('oleksandra'), {'Oleksandr'})
        self.assertTrue(all(r['lemma'].split(':')[0] != 'Oleksandr' for r, _, _ in eligible))
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'bad.tsv'; p.write_text('name\tstatus\nX\texclude\n')
            with self.assertRaisesRegex(ValueError, 'exclusions checksum'): trial.load_exclusions(p)

    def test_additive_records_metadata_aliases_and_source_identities_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp); report, members = self.build(out)
            with zipfile.ZipFile(out / trial.PACK_NAME) as z:
                records, aliases, _ = trial.parse_dictionary(z.read('dictionary.bin'))
                side = json.loads(z.read('language-intelligence.json'))
                self.assertEqual(z.read('unigrams.txt'), members['unigrams.txt'])
            old, old_aliases, _ = trial.parse_dictionary(members['dictionary.bin'])
            self.assertEqual(records[:len(old)], old)
            for key, indices in old_aliases.items(): self.assertEqual([i for i in aliases[key] if i < len(old)], indices)
            by_key = {e['surfaceKey']: e for e in side['entries']}
            for entry in json.loads(members['language-intelligence.json'])['entries']:
                self.assertEqual(by_key[entry['surfaceKey']], entry)
            words = {w.lower(): w for w, _ in records}
            self.assertEqual(words['google'], 'Google')
            self.assertEqual(words['usb'], 'USB')
            self.assertEqual(words['jana'], 'Jana')
            self.assertNotIn('qzzfoo', words)
            self.assertEqual(report['removed'], 0)
            self.assertEqual(report['changedOldRanks'], 0)
            for word in set(words) - {w.lower() for w, _ in old}:
                readings = by_key[word]['metadata']['sourceEvidence']['lexicalReadings']
                self.assertTrue(readings)
                self.assertTrue(all(word in {s.lower() for s in r['surfaces']} for r in readings))

    def test_full_measurement_precedes_capacity_and_foreign_name_collisions_are_deferred(self):
        with tempfile.TemporaryDirectory() as tmp:
            report, _ = self.build(Path(tmp)/'foreign', foreign=lambda k, lang: 7 if k=='from' and lang=='en' else 0)
            audit = [json.loads(s) for s in (Path(tmp)/'foreign/name-forms-audit.jsonl').read_text().splitlines()]
            from_row = next(r for r in audit if r['surfaceKey']=='from')
            self.assertFalse(from_row['accepted'])
            self.assertEqual(from_row['reason'], 'foreign-word-name-collision')
            raw, members = self.base()
            baseline = trial.json_nodes(json.loads(members['language-intelligence.json'])) + 15
            with patch.object(trial, 'MAX_NODES', baseline + 100):
                report, _ = self.build(Path(tmp)/'capacity')
                self.assertGreater(report['qualifiedNewKeys'], report['added'])
                self.assertGreater(report['candidateDecisions']['measured-runtime-capacity'], 0)
                self.assertLessEqual(report['runtimeJsonNodes'], baseline + 100)

    def test_determinism_and_failed_gate_never_leaves_installable_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp)/'a', Path(tmp)/'b'
            self.assertEqual(self.build(a)[0], self.build(b)[0])
            self.assertEqual((a/trial.PACK_NAME).read_bytes(), (b/trial.PACK_NAME).read_bytes())
            with self.assertRaisesRegex(ValueError, 'already contains'): self.build(a)
            with patch.object(trial, 'MAX_NODES', 10), self.assertRaisesRegex(ValueError, 'empty additions'):
                self.build(Path(tmp)/'bad')
            self.assertFalse((Path(tmp)/'bad'/trial.PACK_NAME).exists())

    def test_base_checksum_member_and_canonical_identity_guards(self):
        raw, members = self.base()
        with self.assertRaisesRegex(ValueError, 'checksum'):
            trial.read_base(raw, '0'*64, sha256(members['dictionary.bin']))
        stream = io.BytesIO(raw)
        with zipfile.ZipFile(stream, 'a') as z: z.writestr('NOTICE.txt', b'duplicate')
        changed = stream.getvalue()
        with self.assertRaisesRegex(ValueError, 'members'):
            trial.read_base(changed, sha256(changed), sha256(members['dictionary.bin']))
        side = json.loads(members['language-intelligence.json'])
        side['entries'][0]['canonicalForm'] = 'different'
        members['language-intelligence.json'] = canonical_bytes(side)
        manifest = json.loads(members['manifest.json'])
        manifest['languageIntelligence']['sha256'] = sha256(members['language-intelligence.json'])
        members['manifest.json'] = canonical_bytes(manifest)
        changed = trial.write_pack(members)
        with self.assertRaisesRegex(ValueError, 'sidecar identity'):
            trial.read_base(changed, sha256(changed), sha256(members['dictionary.bin']))


if __name__ == '__main__': unittest.main()
