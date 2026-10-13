import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_shared_metadata_trial as trial
from shared_metadata_v2 import canonical, nodes, share_lemmas, share_attributes, expand


class SharedMetadataTrialTest(unittest.TestCase):
    def document(self):
        rows = [dict(lemma='Malina:Sf', partOfSpeech='subst', nameClasses=['nazwisko'], labels=[], surfaces=['Malina']),
                dict(lemma='malina', partOfSpeech='subst', surfaces=['malina']),
                dict(lemma='malina', partOfSpeech='adj', labels=[], surfaces=['malina']),
                dict(lemma='Malina:Sm1', partOfSpeech='subst', nameClasses=['nazwisko'], surfaces=['Malina'])]
        return dict(schemaVersion=1, languageCode='pl', provenance=dict(source='unaltered'),
                    entries=[dict(surfaceKey='malina', metadata=dict(sourceEvidence=dict(lexicalReadings=copy.deepcopy(rows))))
                             for _ in range(8)])

    def base(self, document=None):
        side = canonical(document or self.document())
        members = {'dictionary.bin': b'unchanged binary', 'unigrams.txt': b'unchanged frequencies\n',
                   'NOTICE.txt': b'Original credit\n', 'language-intelligence.json': side,
                   'manifest.json': canonical(dict(code='pl', version=8, apiVersion=1, wordCount=1,
                        capabilities=['metadata'], languageIntelligence=dict(file='language-intelligence.json',
                        schemaVersion=1, sha256=trial.sha256(side))))}
        return trial.write_pack(members), members

    def build(self, out, raw=None, members=None):
        if raw is None: raw, members = self.base()
        return trial.build(raw, out, trial.sha256(raw), trial.sha256(members['language-intelligence.json']))

    def test_exact_round_trip_retains_homonyms_case_pos_suffix_and_missing_fields(self):
        original = self.document()
        encoded, _ = share_lemmas(original, True); share_attributes(encoded)
        self.assertEqual(canonical(expand(json.loads(trial.serialize(encoded)))), canonical(original))
        self.assertEqual(len(encoded['sourceLexemes']), 4)
        self.assertLess(nodes(encoded), nodes(original))
        self.assertNotIn('sourceLexemes', original)

    def test_unique_objects_stay_inline_and_tables_are_deterministic(self):
        doc = self.document(); doc['entries'] = doc['entries'][:1]
        encoded, _ = share_lemmas(doc, True)
        self.assertEqual(encoded['sourceLexemes'], [])
        one, _ = share_lemmas(self.document(), True); share_attributes(one)
        reversed_doc = self.document(); reversed_doc['entries'].reverse()
        two, _ = share_lemmas(reversed_doc, True); share_attributes(two)
        self.assertEqual(one['sourceLexemes'], two['sourceLexemes'])
        self.assertEqual(one['sourceAttributes'], two['sourceAttributes'])

    def test_package_preserves_binary_frequencies_and_requires_new_reader(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = self.build(Path(tmp)); _, old = self.base()
            with zipfile.ZipFile(Path(tmp)/trial.PACK_NAME) as z:
                self.assertEqual(z.read('dictionary.bin'), old['dictionary.bin'])
                self.assertEqual(z.read('unigrams.txt'), old['unigrams.txt'])
                manifest = json.loads(z.read('manifest.json'))
                self.assertEqual((manifest['version'], manifest['apiVersion'], manifest['languageIntelligence']['schemaVersion']), (9, 2, 2))
                keys = list(json.loads(z.read('language-intelligence.json')))
                self.assertLess(keys.index('sourceAttributes'), keys.index('sourceLexemes'))
                self.assertLess(keys.index('sourceLexemes'), keys.index('entries'))
            self.assertEqual(report['originalMetadataSha256'], report['reconstructedMetadataSha256'])
            self.assertEqual((report['added'], report['removed'], report['changedRanks']), (0, 0, 0))

    def test_reproducible_output_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp)/'a', Path(tmp)/'b'
            self.assertEqual(self.build(a), self.build(b))
            self.assertEqual((a/trial.PACK_NAME).read_bytes(), (b/trial.PACK_NAME).read_bytes())
            with self.assertRaisesRegex(ValueError, 'already contains'): self.build(a)

    def test_bad_identity_noncanonical_json_and_members_leave_no_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/'bad'; raw, members = self.base()
            with self.assertRaisesRegex(ValueError, 'checksum'): trial.build(raw, out, '0'*64)
            members['extra.txt'] = b'bad'; raw = trial.write_pack(members)
            with self.assertRaisesRegex(ValueError, 'members'): self.build(out, raw, members)
            del members['extra.txt']
            members['language-intelligence.json'] = json.dumps(self.document()).encode()
            manifest = json.loads(members['manifest.json']); manifest['languageIntelligence']['sha256'] = trial.sha256(members['language-intelligence.json'])
            members['manifest.json'] = canonical(manifest); raw = trial.write_pack(members)
            with self.assertRaisesRegex(ValueError, 'canonical'): self.build(out, raw, members)
            self.assertFalse((out/trial.PACK_NAME).exists())

    def test_lossy_transform_is_rejected_before_any_installable_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/'bad'
            with patch.object(trial, 'expand', return_value={}), self.assertRaisesRegex(ValueError, 'lossless'):
                self.build(out)
            self.assertFalse((out/trial.PACK_NAME).exists())

    def test_negative_fractional_and_conflicting_references_cannot_expand(self):
        encoded, _ = share_lemmas(self.document(), True); share_attributes(encoded)
        for ref in (-1, 999, 0.5, True):
            bad = copy.deepcopy(encoded)
            bad['entries'][0]['metadata']['sourceEvidence']['lexicalReadings'][0]['sourceRef'] = ref
            with self.assertRaises(AssertionError): expand(bad)
        bad = copy.deepcopy(encoded)
        bad['entries'][0]['metadata']['sourceEvidence']['lexicalReadings'][0]['lemma'] = 'invented'
        with self.assertRaises(AssertionError): expand(bad)


if __name__ == '__main__': unittest.main()
