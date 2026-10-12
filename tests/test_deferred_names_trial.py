import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import morfeusz2
import build_deferred_names_trial as trial
from build_names_forms_trial import NameOracle, entry, admissions
from build_variant_trial import canonical_bytes, sha256
from shared_metadata_v2 import header, nodes
from test_common_forms_trial import dictionary


class DeferredNamesTrialTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = morfeusz2.Morfeusz(case_handling=morfeusz2.CONDITIONALLY_CASE_SENSITIVE)
        cls.source = NameOracle(cls.oracle)

    def base(self):
        _, name = entry('eleonora', self.source.evidence('eleonora'), lambda w: 2)
        record = header(name['metadata']['sourceEvidence']['lexicalReadings'][0])
        _, ordinary = entry('malina', self.source.evidence('malina'), lambda w: 2)
        side = dict(schemaVersion=2, languageCode='pl', provenance=dict(original='unchanged'),
            sourceAttributes=[dict(nameClasses=['imię']), dict(nameClasses=['nazwisko'])],
            sourceLexemes=[record], entries=[ordinary, dict(surfaceKey='eleonorą', canonicalForm='Eleonorą',
                metadata=dict(sourceEvidence=dict(lexicalReadings=[dict(sourceRef=0, surfaces=['Eleonorą'])])))])
        side_bytes = trial.serialize(side)
        members = {'dictionary.bin': dictionary([('malina', 33), ('Eleonorą', 44)]),
            'language-intelligence.json': side_bytes, 'unigrams.txt': b'unchanged frequencies\n',
            'NOTICE.txt': b'original attribution\n', 'manifest.json': canonical_bytes(dict(code='pl',
                version=9, apiVersion=2, wordCount=2, capabilities=['capitalization', 'metadata'],
                languageIntelligence=dict(file='language-intelligence.json', schemaVersion=2, sha256=sha256(side_bytes))))}
        return trial.write_pack(members), members

    def audit(self):
        rows = []
        for key in ['eleonora', 'gajewska', 'ronalda', 'odessa']:
            evidence = self.source.evidence(key)
            surface, value = entry(key, evidence, lambda w: 2)
            groups = sorted({g for _, _, gs in admissions(key, evidence, set()) for g in gs})
            rows.append(dict(surfaceKey=key, canonicalForm=surface, groups=groups, zipf=2,
                foreignZipf=0, foreignLanguage='en', runtimeNodes=nodes(value), accepted=False,
                reason='measured-runtime-capacity', **evidence))
        return sorted(rows, key=lambda r: ('brands_and_software' not in r['groups'],
                      'initialisms' not in r['groups'], -r['zipf'], r['surfaceKey']))

    def build(self, root, rows=None, raw=None, members=None):
        root.mkdir(parents=True, exist_ok=True)
        if raw is None: raw, members = self.base()
        audit = root/'input.jsonl'; audit.write_bytes(b''.join(canonical_bytes(r) for r in (self.audit() if rows is None else rows)))
        report = trial.build(raw, audit, root/'out', self.oracle, lambda w: 2, lambda w: 1000,
            set(), dict(test=True), sha256(raw), sha256(members['dictionary.bin']), sha256(audit.read_bytes()))
        return report, members, root/'out'

    def test_additions_preserve_all_old_records_metadata_tables_and_unigrams(self):
        with tempfile.TemporaryDirectory() as tmp:
            report, old, out = self.build(Path(tmp))
            with zipfile.ZipFile(out/trial.PACK_NAME) as z:
                records, aliases, _ = trial.parse_dictionary(z.read('dictionary.bin'))
                side = json.loads(z.read('language-intelligence.json'))
                self.assertEqual(z.read('unigrams.txt'), old['unigrams.txt'])
            original = json.loads(old['language-intelligence.json'])
            before, before_aliases, _ = trial.parse_dictionary(old['dictionary.bin'])
            self.assertEqual(records[:len(before)], before)
            for k, indices in before_aliases.items(): self.assertEqual([i for i in aliases[k] if i < len(before)], indices)
            self.assertEqual(side['sourceAttributes'], original['sourceAttributes'])
            self.assertEqual(side['sourceLexemes'], original['sourceLexemes'])
            after = {e['surfaceKey']: e for e in side['entries']}
            for e in original['entries']: self.assertEqual(after[e['surfaceKey']], e)
            self.assertEqual(after['eleonora']['metadata']['sourceEvidence']['lexicalReadings'][0]['sourceRef'], 0)
            pool = trial.ExistingPool(side)
            for key in set(after)-{e['surfaceKey'] for e in original['entries']}:
                self.assertEqual(pool.decode(after[key]), entry(key, self.source.evidence(key), lambda w: 2)[1])
            self.assertEqual(report['added'], 4)
            self.assertTrue(report['sharedTablesUnchanged'])
            self.assertEqual(report['changedOldMetadataEntries'], 0)

    def test_whole_pool_is_measured_before_entry_capacity_selection(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(trial, 'MAX_ENTRIES', 3):
            report, _, _ = self.build(Path(tmp))
            self.assertEqual(report['measured']['deferredEligibleKeys'], 4)
            self.assertEqual(report['added'], 1)
            self.assertEqual(report['candidateDecisions']['metadata-entry-limit'], 3)
            self.assertEqual(report['runtimeEntries'], 3)

    def test_foreign_word_collisions_remain_excluded_and_audited(self):
        rows = self.audit(); foreign = next(r for r in rows if r['surfaceKey']=='gajewska')
        foreign.update(foreignZipf=4, reason='foreign-word-name-collision')
        with tempfile.TemporaryDirectory() as tmp:
            report, _, out = self.build(Path(tmp), rows)
            self.assertEqual(report['added'], 3)
            self.assertEqual(report['measured']['foreignCollisions'], 1)
            self.assertEqual(report['candidateDecisions']['foreign-word-name-collision'], 1)
            with zipfile.ZipFile(out/trial.PACK_NAME) as z:
                self.assertNotIn('gajewska', {e['surfaceKey'] for e in json.loads(z.read('language-intelligence.json'))['entries']})

    def test_determinism_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, _, p = self.build(Path(tmp)/'a'); b, _, q = self.build(Path(tmp)/'b')
            self.assertEqual(a, b); self.assertEqual((p/trial.PACK_NAME).read_bytes(), (q/trial.PACK_NAME).read_bytes())
            with self.assertRaisesRegex(ValueError, 'already contains'): self.build(Path(tmp)/'a')

    def test_unverified_native_evidence_never_emits_installable_pack(self):
        raw, members = self.base(); rows = self.audit()
        with tempfile.TemporaryDirectory() as tmp, patch.object(NameOracle, 'evidence', return_value={}):
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, 'native source evidence'):
                self.build(root, rows, raw, members)
            self.assertFalse((root/'out'/trial.PACK_NAME).exists())

    def test_tampered_hash_duplicate_key_and_wrong_default_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); rows = self.audit()
            path = root/'audit'; path.write_bytes(b''.join(canonical_bytes(r) for r in rows))
            with self.assertRaisesRegex(ValueError, 'checksum'): list(trial.audit_rows(path, '0'*64))
            for i, bad in enumerate([rows+[copy.deepcopy(rows[-1])], copy.deepcopy(rows)]):
                if i: bad[0]['canonicalForm']='invented'
                with self.assertRaises(ValueError): self.build(root/str(i), bad)
                self.assertFalse((root/str(i)/'out'/trial.PACK_NAME).exists())

    def test_incompatible_base_is_rejected(self):
        raw, members = self.base()
        manifest=json.loads(members['manifest.json']);manifest['apiVersion']=1
        members['manifest.json']=canonical_bytes(manifest);raw=trial.write_pack(members)
        with self.assertRaisesRegex(ValueError, 'base identity'):
            trial.read_base(raw,sha256(raw),sha256(members['dictionary.bin']))

    def test_pool_never_merges_case_source_suffix_pos_or_empty_fields(self):
        record=dict(lemma='Name:Sf', partOfSpeech='subst', labels=[])
        pool=trial.ExistingPool(dict(sourceAttributes=[dict(labels=[])],sourceLexemes=[record]))
        for source in [record,dict(lemma='name:Sf',partOfSpeech='subst'),dict(lemma='Name:Sm1',partOfSpeech='subst'),
                       dict(lemma='Name:Sf',partOfSpeech='adj'),dict(lemma='Name:Sf',partOfSpeech='subst')]:
            value=dict(surfaceKey='name',metadata=dict(sourceEvidence=dict(lexicalReadings=[dict(**source,surfaces=['Name'])])))
            encoded=pool.encode(value)
            self.assertEqual(pool.decode(encoded),value)
            self.assertEqual('sourceRef' in encoded['metadata']['sourceEvidence']['lexicalReadings'][0],source==record)


if __name__ == '__main__': unittest.main()
