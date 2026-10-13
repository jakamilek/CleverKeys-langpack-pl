import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_thematic_forms_trial as trial
from build_global_casing_trial import SourceOracle
from build_variant_trial import canonical_bytes, sha256
from test_common_forms_trial import dictionary
import morfeusz2


class ThematicFormsTrialTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = morfeusz2.Morfeusz(case_handling=morfeusz2.CONDITIONALLY_CASE_SENSITIVE)

    def base(self):
        source = SourceOracle(self.oracle)
        # A compact ordinary entry plus an ambiguous case entry; both must survive.
        entries = [trial.compact_entry(w, source.evidence(w)) for w in ['kasa', 'malina']]
        side = canonical_bytes({'schemaVersion': 1, 'languageCode': 'pl', 'entries': entries,
                                'provenance': {'commonFormsExpansion': {'inputPackSha256': 'old'}}})
        members = {'dictionary.bin': dictionary([('kasa', 33), ('malina', 44)]),
            'language-intelligence.json': side, 'unigrams.txt': b'unchanged unigrams\n',
            'NOTICE.txt': b'Original source credit\n', 'manifest.json': canonical_bytes({
                'code': 'pl', 'version': 6, 'apiVersion': 1, 'wordCount': 2, 'attribution': 'Original',
                'languageIntelligence': {'file': 'language-intelligence.json', 'schemaVersion': 1, 'sha256': sha256(side)}})}
        return trial.write_pack(members), members

    def build(self, out, values=None, seeds=None):
        raw, members = self.base()
        values = values or {'kasa': 4, 'kasami': 1.2, 'kasy': .99, 'jan': 5, 'żzzzzz': 6, 'malina': 3}
        seeds = seeds or {'kasa': {'shopping', 'colloquial'}, 'jan': {'colloquial'}, 'żzzzzz': {'computing'}}
        report = trial.build(raw, seeds, [], out, self.oracle, lambda w: values.get(w, 0),
            lambda w: 10 ** values.get(w.lower(), 0), {'test': True},
            expected_sha256=sha256(raw), expected_dictionary=sha256(members['dictionary.bin']))
        return report, raw, members

    def test_link_targets_are_atomic_and_case_sensitive(self):
        words = trial.index_words('[[kasa|JAN]] [[kasami#pl|etykieta]] [[Jan]] [[kasa fiskalna]] '
                                  '[[czarno-biały]] [[Kategoria:kasa]] [[się]] [[siec\u0301]]')
        self.assertEqual(words, {'kasa', 'kasami', 'się', 'sieć'})

    def test_actual_snapshots_and_lock_reject_changed_source(self):
        root = Path(__file__).resolve().parents[1] / 'source/thematic-v7'
        seeds, lock = trial.load_sources(root)
        self.assertGreater(len(seeds), 8000)
        self.assertEqual({r['group'] for r in lock}, trial.GROUPS)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            for path in root.iterdir():
                if path.suffix in {'.json', '.wikitext'}: (out / path.name).write_bytes(path.read_bytes())
            (out / 'computing.wikitext').write_text('[[qzzfoo]]')
            with self.assertRaisesRegex(ValueError, 'snapshot checksum'): trial.load_sources(out)
            (out / 'intake-lock.json').write_bytes(b'[]')
            with self.assertRaisesRegex(ValueError, 'lock checksum'): trial.load_sources(out)

    def test_source_index_family_and_frequency_required_with_old_data_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); report, raw, members = self.build(root)
            with zipfile.ZipFile(root / trial.PACK_NAME) as z:
                words, _, _ = trial.parse_dictionary(z.read('dictionary.bin'))
                side = json.loads(z.read('language-intelligence.json'))
                self.assertEqual(z.read('unigrams.txt'), members['unigrams.txt'])
                self.assertTrue(z.read('NOTICE.txt').startswith(members['NOTICE.txt']))
            self.assertEqual(words, [('kasa', 33), ('malina', 44), ('kasami', words[-1][1])])
            old = {e['surfaceKey']: e for e in json.loads(members['language-intelligence.json'])['entries']}
            new = {e['surfaceKey']: e for e in side['entries']}
            for key, entry in old.items(): self.assertEqual(new[key], entry)
            self.assertEqual(report['added'], 1)
            self.assertEqual(report['addedGroupCoverageOverlapping'], {'colloquial': 1, 'shopping': 1})
            row = next(json.loads(line) for line in (root / 'thematic-forms-audit.jsonl').read_text().splitlines()
                       if json.loads(line)['surfaceKey'] == 'kasami')
            self.assertTrue(row['accepted'])
            self.assertTrue(row['generatedFormProofs'])
            self.assertEqual(row['indexedLemmas'], ['kasa'])
            audit = {r['surfaceKey']: r for r in map(json.loads, (root / 'thematic-seed-audit.jsonl').read_text().splitlines())}
            self.assertEqual(audit['żzzzzz']['reason'], 'no-current-ordinary-source-proof')
            self.assertEqual(audit['jan']['reason'], 'no-current-ordinary-source-proof')

    def test_low_frequency_index_anchor_is_not_enough(self):
        raw, members = self.base()
        with tempfile.TemporaryDirectory() as tmp, self.assertRaisesRegex(ValueError, 'empty'):
            trial.build(raw, {'kasa': {'shopping'}}, [], Path(tmp), self.oracle,
                lambda w: {'kasa': 1.99, 'kasami': 5}.get(w, 0), lambda w: 10,
                {}, sha256(raw), sha256(members['dictionary.bin']))

    def test_determinism_and_no_installable_pack_on_budget_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a, _, _ = self.build(root / 'a'); b, _, _ = self.build(root / 'b')
            self.assertEqual(a, b)
            self.assertEqual((root / 'a' / trial.PACK_NAME).read_bytes(), (root / 'b' / trial.PACK_NAME).read_bytes())
            with patch.object(trial, 'MAX_NODES', 10), self.assertRaisesRegex(ValueError, 'budget'):
                self.build(root / 'bad')
            self.assertFalse((root / 'bad' / trial.PACK_NAME).exists())
            with self.assertRaisesRegex(ValueError, 'output already'): self.build(root / 'a')

    def test_base_rejects_duplicate_members_and_wrong_compact_identity(self):
        raw, members = self.base()
        stream = io.BytesIO(raw)
        with zipfile.ZipFile(stream, 'a') as z: z.writestr('NOTICE.txt', b'duplicate')
        changed = stream.getvalue()
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            trial.read_base(changed, sha256(changed), sha256(members['dictionary.bin']))
        side = json.loads(members['language-intelligence.json']); side['entries'][0]['canonicalForm'] = 'qzzfoo'
        members['language-intelligence.json'] = canonical_bytes(side)
        manifest = json.loads(members['manifest.json'])
        manifest['languageIntelligence']['sha256'] = sha256(members['language-intelligence.json'])
        members['manifest.json'] = canonical_bytes(manifest)
        changed = trial.write_pack(members)
        with self.assertRaisesRegex(ValueError, 'sidecar identities'):
            trial.read_base(changed, sha256(changed), sha256(members['dictionary.bin']))


if __name__ == '__main__': unittest.main()
