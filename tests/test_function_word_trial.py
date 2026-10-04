import io
import struct
import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import morfeusz2
from build_variant_trial import canonical_bytes, dictionary_entries, read_json, sha256
from build_function_word_trial import (correct_dictionary, build_corrected_trial,
                                       DICTIONARY_ID, MORFEUSZ_VERSION, REASON)
from capitalization_rules import resolve_capitalization


def dictionary(words):
    raw = bytearray(48)
    raw[:4] = b'CKDT'
    struct.pack_into('<I', raw, 4, 2)
    for rank, word in enumerate(words):
        data = word.encode('utf-8')
        raw.extend(struct.pack('<H', len(data)) + data + bytes([rank]))
    normalized = len(raw)
    raw.extend(b'normalized sentinel')
    accent = len(raw)
    raw.extend(b'accent sentinel')
    struct.pack_into('<IIII', raw, 12, len(words), 48, normalized, accent)
    return bytes(raw)


def pack(words, sidecar=None):
    sidecar = sidecar or {'entries': []}
    sidecar_raw = canonical_bytes(sidecar)
    members = {
        'dictionary.bin': dictionary(words), 'unigrams.txt': b'weights unchanged\n',
        'NOTICE.txt': b'Original attribution\n', 'language-intelligence.json': sidecar_raw,
        'manifest.json': canonical_bytes({'code': 'pl', 'apiVersion': 1, 'version': 3,
            'wordCount': len(words), 'languageIntelligence': {'sha256': sha256(sidecar_raw)}}),
    }
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w') as archive:
        for name, data in members.items():
            archive.writestr(name, data)
    return out.getvalue(), members


class FunctionWordTrialTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = morfeusz2.Morfeusz(case_handling=morfeusz2.CONDITIONALLY_CASE_SENSITIVE)

    def test_reviewed_source_snapshot(self):
        self.assertEqual(str(morfeusz2.__version__), MORFEUSZ_VERSION)
        self.assertEqual(self.oracle.dict_id(), DICTIONARY_ID)

    def test_real_function_word_and_name_homonyms(self):
        for key in ['ale', 'lub', 'ani', 'tylko', 'ponieważ', 'wedle']:
            with self.subTest(key=key):
                result = resolve_capitalization(key=key, morfeusz=self.oracle,
                    explicit_policy=(key.capitalize(), 'capitalized'), policies=['capitalized'],
                    secondary_linguistic_evidence={'resolved': True, 'policy': 'capitalized'})
                self.assertEqual(result['surface'], key)
                self.assertEqual(result['reason'], REASON)
                self.assertTrue(result['explicit_policy_conflict'])
                self.assertTrue(result['function_word_matches'])
        for key in ['ale', 'lub']:
            self.assertTrue(resolve_capitalization(key=key, morfeusz=self.oracle)['proper_name_matches'])

    def test_real_names_and_common_forms_retain_existing_policy(self):
        for key, surface in [('jan', 'Jan'), ('ala', 'Ala'), ('maria', 'Maria'),
                             ('łódź', 'łódź'), ('malina', 'malina'),
                             ('warszawska', 'warszawska'), ('łódzki', 'łódzki')]:
            with self.subTest(key=key):
                result = resolve_capitalization(key=key, morfeusz=self.oracle)
                self.assertEqual(result['surface'], surface)
                self.assertNotEqual(result['reason'], REASON)

    def test_only_exact_lowercase_non_name_function_reading_qualifies(self):
        class Oracle:
            def __init__(self, orth, tag, classes=(), lowercase=False):
                self.orth, self.tag, self.classes, self.lowercase = orth, tag, classes, lowercase

            def analyse(self, surface):
                name = (0, 1, (surface, 'Xena', 'subst:sg:nom:f', ['imię'], []))
                if surface == 'xena' and not self.lowercase:
                    return [name]
                return [name, (0, 1, (self.orth, 'xena', self.tag, self.classes, []))]

        for oracle in [Oracle('xena', 'conj'), Oracle('xe', 'conj', lowercase=True),
                       Oracle('xena', 'conj', ['imię'], True),
                       Oracle('xena', 'brev:npun', lowercase=True),
                       Oracle('xena', 'impt:sg:sec:imperf', lowercase=True)]:
            self.assertEqual(resolve_capitalization(key='xena', morfeusz=oracle)['surface'], 'Xena')
        self.assertEqual(resolve_capitalization(key='xena',
            morfeusz=Oracle('xena', 'conj', lowercase=True))['surface'], 'xena')

    def test_ckdt_indices_ranks_and_lookup_sections_preserved(self):
        raw = dictionary(['Ale', 'Lub', 'Jan', 'Łódź'])
        result, changes = correct_dictionary(raw, self.oracle)
        self.assertEqual([c['key'] for c in changes], ['ale', 'lub'])
        self.assertEqual([c['rank'] for c in changes], [0, 1])
        self.assertEqual(list(dictionary_entries(result).values()), ['ale', 'lub', 'Jan', 'Łódź'])
        # Only the two initial ASCII capitals change anywhere in the binary.
        diffs = [(a, b) for a, b in zip(raw, result) if a != b]
        self.assertEqual(diffs, [(ord('A'), ord('a')), (ord('L'), ord('l'))])
        self.assertEqual(len(raw), len(result))

    def test_deterministic_pack_retains_case_variants_and_checksums(self):
        entry = {'surfaceKey': 'łódź', 'canonicalForm': 'łódź', 'capitalization': {
            'defaultSurface': 'łódź', 'variants': [{'surface': 'łódź'}, {'surface': 'Łódź'}]}}
        base, members = pack(['Ale', 'Lub', 'Jan', 'łódź'], {'entries': [entry]})
        args = (base, self.oracle, {'dictionaryId': DICTIONARY_ID}, sha256(base))
        result, report = build_corrected_trial(*args)
        self.assertEqual(build_corrected_trial(*args), (result, report))
        with zipfile.ZipFile(io.BytesIO(result)) as archive:
            for name in ['unigrams.txt', 'language-intelligence.json']:
                self.assertEqual(archive.read(name), members[name])
            manifest = read_json(archive.read('manifest.json'))
            self.assertEqual(manifest['version'], 4)
            self.assertEqual(manifest['wordCount'], 4)
            self.assertEqual(manifest['languageIntelligence']['sha256'], sha256(members['language-intelligence.json']))
        self.assertEqual(report['packageSha256'], sha256(result))
        self.assertEqual(report['correctionCount'], 2)

    def test_reject_wrong_base_and_conflicting_case_evidence(self):
        base, _ = pack(['Ale', 'Lub'])
        with self.assertRaisesRegex(ValueError, 'checksum'):
            build_corrected_trial(base, self.oracle, {})
        entry = {'surfaceKey': 'ale', 'canonicalForm': 'Ale',
                 'capitalization': {'defaultSurface': 'Ale'}}
        base, _ = pack(['Ale', 'Lub'], {'entries': [entry]})
        with self.assertRaisesRegex(ValueError, 'frozen casing evidence'):
            build_corrected_trial(base, self.oracle, {}, sha256(base))

    def test_reject_bad_dictionary_bounds_and_duplicate_keys(self):
        raw = bytearray(dictionary(['Ale']))
        struct.pack_into('<I', raw, 20, 48)
        with self.assertRaisesRegex(ValueError, 'bounds'):
            correct_dictionary(bytes(raw), self.oracle)
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            correct_dictionary(dictionary(['Ale', 'ale']), self.oracle)


if __name__ == '__main__':
    unittest.main()
