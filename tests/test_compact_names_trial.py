import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_compact_names_trial as trial
from build_compact_source_trial import factor, decode_entry
import test_deferred_names_trial as fixtures
from build_names_forms_trial import NameOracle, entry
from build_variant_trial import canonical_bytes, sha256


class CompactNamesTrialTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.DeferredNamesTrialTest.setUpClass()
        cls.fixture = fixtures.DeferredNamesTrialTest()
        cls.oracle = cls.fixture.oracle
        cls.source = cls.fixture.source

    def base(self):
        raw, members = self.fixture.base()
        side, _ = factor(json.loads(members['language-intelligence.json']))
        members['language-intelligence.json'] = trial.serialize(side)
        manifest = json.loads(members['manifest.json'])
        manifest.update(version=11, apiVersion=3)
        manifest['languageIntelligence'].update(schemaVersion=3, sha256=sha256(members['language-intelligence.json']))
        members['manifest.json'] = canonical_bytes(manifest)
        return trial.write_pack(members), members

    def build(self, root, rows=None, base=None):
        raw, members = self.base() if base is None else base; root.mkdir(parents=True, exist_ok=True)
        audit = root / 'input.jsonl'
        audit.write_bytes(b''.join(canonical_bytes(r) for r in (self.fixture.audit() if rows is None else rows)))
        report = trial.build(raw, audit, root/'out', self.oracle, lambda w: 2, lambda w: 1000,
            set(), dict(test=True), sha256(raw), sha256(members['dictionary.bin']), sha256(audit.read_bytes()))
        return report, members, root/'out'

    def test_all_previous_data_and_exact_new_native_views_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            report, old, out = self.build(Path(tmp))
            with zipfile.ZipFile(out / trial.PACK_NAME) as z:
                after = json.loads(z.read('language-intelligence.json'))
                before_records, before_aliases, _ = trial.read_base(trial.write_pack(old), sha256(trial.write_pack(old)),
                    sha256(old['dictionary.bin']), 11, 3)[3:]
                from build_common_forms_trial import parse_dictionary
                records, aliases, _ = parse_dictionary(z.read('dictionary.bin'))
                self.assertEqual(records[:len(before_records)], before_records)
                for key, indices in before_aliases.items():
                    self.assertEqual([i for i in aliases[key] if i < len(before_records)], indices)
                self.assertEqual(z.read('unigrams.txt'), old['unigrams.txt'])
                manifest = json.loads(z.read('manifest.json'))
                self.assertEqual((manifest['version'], manifest['apiVersion'], manifest['languageIntelligence']['schemaVersion']), (12,3,3))
            before = json.loads(old['language-intelligence.json'])
            self.assertEqual(after['sourceAttributes'], before['sourceAttributes'])
            self.assertEqual(after['sourceLexemes'], before['sourceLexemes'])
            indexed = {e['surfaceKey']: e for e in after['entries']}
            for e in before['entries']: self.assertEqual(indexed[e['surfaceKey']], e)
            pool = trial.ExistingPool(after)
            for key in set(indexed) - {e['surfaceKey'] for e in before['entries']}:
                self.assertEqual(decode_entry(pool, indexed[key]), entry(key, self.source.evidence(key), lambda w: 2)[1])
            self.assertEqual(indexed['eleonora']['metadata']['sourceEvidence']['lexicalReadings'][0], dict(sourceRef=0, surfaceMask=2))
            self.assertEqual(report['added'], 4)
            self.assertEqual(report['packVersion'], 12)
            self.assertEqual(report['changedOldMetadataEntries'], 0)

    def test_all_candidates_measured_before_entry_limit_and_deterministic_output(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(trial, 'MAX_ENTRIES', 3):
            a, _, p = self.build(Path(tmp)/'a'); b, _, q = self.build(Path(tmp)/'b')
            self.assertEqual(a, b)
            self.assertEqual(a['measured']['deferredEligibleKeys'], 4)
            self.assertEqual(a['added'], 1)
            self.assertEqual(a['candidateDecisions']['metadata-entry-limit'], 3)
            self.assertEqual((p/trial.PACK_NAME).read_bytes(), (q/trial.PACK_NAME).read_bytes())
            with self.assertRaisesRegex(ValueError, 'already contains'): self.build(Path(tmp)/'a')

    def test_already_covered_and_foreign_collisions_never_become_duplicate_additions(self):
        rows = self.fixture.audit(); rows.append(copy.deepcopy(rows[-1]))
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'duplicate audit'): self.build(Path(tmp)/'duplicate', rows)
            rows = self.fixture.audit(); row = next(r for r in rows if r['surfaceKey']=='gajewska')
            row.update(foreignZipf=4, reason='foreign-word-name-collision')
            report, _, out = self.build(Path(tmp)/'collision', rows)
            self.assertEqual(report['added'], 3)
            self.assertEqual(report['candidateDecisions']['foreign-word-name-collision'], 1)

    def test_native_mismatch_and_audit_tampering_never_emit_installable_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = self.base(); rows = self.fixture.audit()
            with patch.object(NameOracle, 'evidence', return_value={}), self.assertRaisesRegex(ValueError, 'native source evidence'):
                self.build(Path(tmp)/'native', rows, base)
            self.assertFalse((Path(tmp)/'native'/'out'/trial.PACK_NAME).exists())
            bad = self.fixture.audit(); bad[0]['canonicalForm']='invented'
            with self.assertRaises(ValueError): self.build(Path(tmp)/'bad', bad)
            self.assertFalse((Path(tmp)/'bad'/'out'/trial.PACK_NAME).exists())

    def test_wrong_api_schema_version_and_base_hash_refuse(self):
        _, members = self.base()
        for api, schema, version in [(2,3,11),(3,2,11),(3,3,10)]:
            changed = copy.deepcopy(members); m=json.loads(changed['manifest.json'])
            m.update(apiVersion=api,version=version);m['languageIntelligence']['schemaVersion']=schema
            changed['manifest.json']=canonical_bytes(m); raw=trial.write_pack(changed)
            with self.assertRaisesRegex(ValueError, 'base identity'):
                trial.read_base(raw,sha256(raw),sha256(changed['dictionary.bin']),11,3)
        raw=trial.write_pack(members)
        with self.assertRaisesRegex(ValueError, 'checksum'):
            trial.read_base(raw,'0'*64,sha256(members['dictionary.bin']),11,3)

    def test_masks_keep_exact_literal_case_and_distinct_source_fields(self):
        pool = trial.CompactPool(dict(sourceAttributes=[],sourceLexemes=[]))
        value=dict(surfaceKey='mail',metadata=dict(sourceEvidence=dict(lexicalReadings=[
            dict(lemma='Mail:Sf',partOfSpeech='subst',labels=[],surfaces=['mAil']),
            dict(lemma='Mail:Sm1',partOfSpeech='adj',surfaces=['Mail']),
            dict(lemma='mail',partOfSpeech='subst',surfaces=['mail'])])))
        encoded=pool.encode(value)
        self.assertEqual(decode_entry(pool, encoded), value)
        rows=encoded['metadata']['sourceEvidence']['lexicalReadings']
        self.assertEqual(rows[0]['surfaces'], ['mAil'])
        self.assertEqual(rows[1]['surfaceMask'], 2)
        self.assertEqual(rows[2]['surfaceMask'], 1)


if __name__ == '__main__': unittest.main()
