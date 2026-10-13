import copy
import io
import json
import struct
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import morfeusz2
import build_common_forms_trial as trial
from build_global_casing_trial import SourceOracle, classify, runtime_entry
from build_variant_trial import canonical_bytes, sha256
from build_pl_preview import normalize_accents


def dictionary(records):
    header = bytearray(48)
    struct.pack_into('<4sI4s', header, 0, b'CKDT', 2, b'pl\0\0')
    canonical = bytearray()
    groups = {}
    for i, (word, rank) in enumerate(records):
        data = word.encode()
        canonical += struct.pack('<H', len(data)) + data + bytes([rank])
        groups.setdefault(normalize_accents(word), []).append(i)
    norms, aliases = bytearray(struct.pack('<I', len(groups))), bytearray()
    for key in sorted(groups):
        data = key.encode(); norms += struct.pack('<H', len(data)) + data
        group = groups[key]
        aliases += bytes([len(group)]) + struct.pack('<' + 'I' * len(group), *group)
    struct.pack_into('<IIII', header, 12, len(records), 48, 48 + len(canonical), 48 + len(canonical) + len(norms))
    return bytes(header + canonical + norms + aliases)


class CommonFormsTrialTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = morfeusz2.Morfeusz(case_handling=morfeusz2.CONDITIONALLY_CASE_SENSITIVE)

    def base(self, directory):
        records = [('kasa', 33), ('nawilżające', 149), ('Łódź', 54)]
        source = SourceOracle(self.oracle)
        audit = b''.join(canonical_bytes({'surfaceKey': w.lower(), **source.evidence(w.lower())}) for w, _ in records)
        audit_path = directory / 'input-audit.jsonl'; audit_path.write_bytes(audit)
        entries = [runtime_entry(w.lower(), w, classify(w.lower(), w, source.evidence(w.lower())), source.evidence(w.lower())) for w, _ in records]
        side = canonical_bytes({'schemaVersion': 1, 'languageCode': 'pl', 'entries': entries,
                                'provenance': {'fullAudit': {'sha256': sha256(audit)}}})
        members = {'dictionary.bin': dictionary(records), 'language-intelligence.json': side,
                   'unigrams.txt': b'original unigram data\n', 'NOTICE.txt': b'original credit\n',
                   'manifest.json': canonical_bytes({'code': 'pl', 'version': 5, 'apiVersion': 1,
                     'wordCount': 3, 'attribution': 'Original', 'capabilities': ['metadata', 'capitalization'],
                     'languageIntelligence': {'sha256': sha256(side), 'file': 'language-intelligence.json', 'schemaVersion': 1}})}
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w') as z:
            for name, data in members.items(): z.writestr(name, data)
        return output.getvalue(), members, audit_path

    def run_build(self, raw, members, audit_path, output):
        values = {'kasa': 4.67, 'nawilżające': 2.54, 'łódź': 4.0,
                  'kasami': 1.5, 'nawilżane': 1.4, 'podpowie': 2.7,
                  'qzzfoo': 6.0, 'jan': 4.0, 'kapitalizacja': 2.0}
        return trial.build(raw, audit_path, output, self.oracle,
            ['kasa', 'kasami', 'nawilżane', 'podpowie', 'qzzfoo', 'jan', 'kapitalizacja'],
            lambda w: values.get(w.lower(), 0), lambda w: 10 ** values.get(w.lower(), 0),
            {'test': True}, expected_sha256=sha256(raw), expected_dictionary=sha256(members['dictionary.bin']))

    def test_real_missing_forms_have_exact_source_proof(self):
        source = SourceOracle(self.oracle)
        for word in trial.REGRESSION_WORDS:
            evidence = source.evidence(word)
            ids = {p['interpretationId'] for p in evidence['generatedFormProofs'] if p['form'] == word}
            self.assertTrue(any(trial.ordinary(r) and r['id'] in ids for r in evidence['interpretations']), word)

    def test_global_thresholds_include_useful_rare_inflections(self):
        self.assertTrue(trial.selected(2.0, 0))
        self.assertTrue(trial.selected(1.0, 2.5))
        self.assertFalse(trial.selected(.99, 5))
        self.assertFalse(trial.selected(1.99, 2.49))
        reading = {'tag': 'subst:sg:nom:f', 'nameClasses': [], 'labels': []}
        self.assertTrue(trial.ordinary(reading))
        for field, value in [('labels', ['daw.']), ('nameClasses', ['imię']), ('tag', 'brev:npun')]:
            self.assertFalse(trial.ordinary({**reading, field: value}))

    def test_additive_build_preserves_records_metadata_unigrams_and_names(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); raw, members, audit = self.base(root)
            report = self.run_build(raw, members, audit, root / 'out')
            with zipfile.ZipFile(root / 'out/cleverkeys-pl-common-forms-trial.zip') as z:
                binary, side = z.read('dictionary.bin'), json.loads(z.read('language-intelligence.json'))
                self.assertEqual(z.read('unigrams.txt'), members['unigrams.txt'])
            old, old_aliases, boundary = trial.parse_dictionary(members['dictionary.bin'])
            new, new_aliases, _ = trial.parse_dictionary(binary)
            self.assertEqual(new[:len(old)], old)
            self.assertEqual(binary[48:boundary], members['dictionary.bin'][48:boundary])
            self.assertEqual({w for w, _ in new[len(old):]}, {'kasami', 'nawilżane', 'podpowie', 'kapitalizacja'})
            old_entries = {e['surfaceKey']: e for e in json.loads(members['language-intelligence.json'])['entries']}
            new_entries = {e['surfaceKey']: e for e in side['entries']}
            for key, entry in old_entries.items(): self.assertEqual(new_entries[key], entry)
            self.assertEqual(report['removed'], 0)
            self.assertEqual(report['added'], 4)
            audit_rows = {r['surfaceKey']: r for r in map(json.loads, (root / 'out/common-forms-audit.jsonl').read_text().splitlines())}
            self.assertEqual(audit_rows['nawilżane']['reason'], 'attested-common-family')
            self.assertFalse(audit_rows['qzzfoo']['accepted'])
            self.assertFalse(audit_rows['jan']['accepted'])

    def test_alias_expansion_preserves_original_order_and_recovers_accents(self):
        raw = dictionary([('lód', 10), ('lod', 80), ('Łódź', 20)])
        old, aliases, boundary = trial.parse_dictionary(raw)
        freq = {'lód': 100, 'lod': 20, 'Łódź': 70, 'ląd': 50, 'łód': 30}
        new = trial.extend_dictionary(raw, old, aliases, boundary, [('łód', 60), ('ląd', 55)], freq.__getitem__)
        records, after, _ = trial.parse_dictionary(new)
        self.assertEqual(after['lod'], [0, 3, 1])
        self.assertEqual([i for i in after['lod'] if i < len(old)], aliases['lod'])
        self.assertEqual(records[after['lad'][0]][0], 'ląd')

    def test_compaction_preserves_lexical_identity_and_source_case_variants(self):
        source = SourceOracle(self.oracle)
        for key in ['kasami', 'podpowie', 'malina', 'łódź']:
            evidence = source.evidence(key)
            complete = runtime_entry(key, key, classify(key, key, evidence), evidence)
            compact = trial.compact_entry(key, evidence)
            restored = copy.deepcopy(compact['metadata']['sourceEvidence']['lexicalReadings'])
            for row in restored:
                row.setdefault('nameClasses', []); row.setdefault('labels', [])
            self.assertEqual(restored, complete['metadata']['sourceEvidence']['lexicalReadings'])
            if len(complete['capitalization']['variants']) > 1:
                self.assertEqual(compact['capitalization'], complete['capitalization'])
            else: self.assertNotIn('capitalization', compact)

    def test_build_is_deterministic_and_rejects_tampered_audit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); raw, members, audit = self.base(root)
            first = self.run_build(raw, members, audit, root / 'a')
            second = self.run_build(raw, members, audit, root / 'b')
            self.assertEqual(first, second)
            self.assertEqual((root / 'a/cleverkeys-pl-common-forms-trial.zip').read_bytes(),
                             (root / 'b/cleverkeys-pl-common-forms-trial.zip').read_bytes())
            audit.write_bytes(audit.read_bytes() + b'\n')
            with self.assertRaises(ValueError): self.run_build(raw, members, audit, root / 'c')

    def test_metadata_budget_failure_does_not_emit_an_installable_pack(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); raw, members, audit = self.base(root)
            with patch.object(trial, 'MAX_NODES', 10), self.assertRaisesRegex(ValueError, 'budget'):
                self.run_build(raw, members, audit, root / 'out')
            self.assertFalse((root / 'out/cleverkeys-pl-common-forms-trial.zip').exists())

    def test_corrupt_lookup_index_and_duplicate_archive_members_are_rejected(self):
        raw = bytearray(dictionary([('łódź', 54)]))
        struct.pack_into('<I', raw, len(raw) - 4, 999)
        with self.assertRaisesRegex(ValueError, 'alias index'): trial.parse_dictionary(raw)
        with tempfile.TemporaryDirectory() as temp:
            base, members, _ = self.base(Path(temp))
            with self.assertRaisesRegex(ValueError, 'checksum'): trial.read_base(base)
            stream = io.BytesIO(base)
            with zipfile.ZipFile(stream, 'a') as z: z.writestr('NOTICE.txt', b'duplicate')
            changed = stream.getvalue()
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                trial.read_base(changed, sha256(changed), sha256(members['dictionary.bin']))


if __name__ == '__main__': unittest.main()
