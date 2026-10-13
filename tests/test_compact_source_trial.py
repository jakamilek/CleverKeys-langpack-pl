import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build_compact_source_trial as trial
from build_deferred_names_trial import ExistingPool
from build_variant_trial import canonical_bytes,sha256
from test_common_forms_trial import dictionary


class CompactSourceTrialTest(unittest.TestCase):
    def document(self):
        return dict(schemaVersion=2,languageCode='pl',provenance=dict(previous='unchanged'),
            sourceAttributes=[dict(nameClasses=['nazwisko'])],sourceLexemes=[dict(lemma='Malina:Sf',partOfSpeech='subst',sourceAttributesRef=0)],
            entries=[dict(surfaceKey=f'word{i}',metadata=dict(sourceEvidence=dict(lexicalReadings=[
                dict(lemma='name:Sm1',partOfSpeech='subst',sourceAttributesRef=0,surfaces=[f'Word{i}']),
                dict(lemma='word',partOfSpeech='adj',surfaces=[f'word{i}'])]))) for i in range(6)])

    def base(self):
        d=self.document();side=trial.serialize(d)
        members={'dictionary.bin':dictionary([(f'word{i}',33+i) for i in range(6)]),
            'unigrams.txt':b'unchanged frequencies\n','NOTICE.txt':b'original credit\n','language-intelligence.json':side,
            'manifest.json':canonical_bytes(dict(code='pl',version=10,apiVersion=2,wordCount=6,
                languageIntelligence=dict(file='language-intelligence.json',schemaVersion=2,sha256=sha256(side))))}
        return trial.write_pack(members),members

    def test_exact_source_views_and_original_table_prefix_are_preserved(self):
        original=self.document();encoded,report=trial.factor(original)
        a=ExistingPool(original);b=ExistingPool(encoded)
        self.assertEqual(encoded['schemaVersion'],3)
        self.assertGreater(report['appendedSourceRecords'],0)
        self.assertEqual(encoded['sourceAttributes'],original['sourceAttributes'])
        self.assertEqual(encoded['sourceLexemes'][:1],original['sourceLexemes'])
        for x,y in zip(original['entries'],encoded['entries']):self.assertEqual(a.decode(x),trial.decode_entry(b,y))
        self.assertEqual(report['decodedEntryViewsSha256'],report['reconstructedEntryViewsSha256'])

    def test_only_exact_lower_title_upper_lists_are_encoded(self):
        for values,mask in [(['malina'],1),(['Malina'],2),(['MALINA'],4),(['MALINA','Malina','malina'],7)]:
            self.assertEqual(trial.mask_for('malina',values),mask)
            self.assertEqual(trial.surfaces('malina',mask),values)
        for values in [['mAlina'],['Malina','malina','MALINA'],['malina','malina'],[]]:
            self.assertIsNone(trial.mask_for('malina',values))
        self.assertIsNone(trial.mask_for('\U00010428',['\U00010428']))
        for value in [0,8,-1,0.5,True,'1']:
            with self.assertRaises(ValueError):trial.surfaces('malina',value)

    def test_missing_empty_case_suffix_and_pos_are_not_merged(self):
        d=self.document()
        d['entries'][0]['metadata']['sourceEvidence']['lexicalReadings'] += [
            dict(lemma='name:Sm1',partOfSpeech='adj',surfaces=['word0']),
            dict(lemma='Name:Sm1',partOfSpeech='subst',labels=[],surfaces=['Word0']),
            dict(lemma='name:Sf',partOfSpeech='subst',surfaces=['word0'])]
        out,_=trial.factor(d)
        self.assertEqual(ExistingPool(d).decode(d['entries'][0]),trial.decode_entry(ExistingPool(out),out['entries'][0]))

    def test_deterministic_package_keeps_dictionary_and_frequencies(self):
        raw,members=self.base()
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a',Path(tmp)/'b'
            x=trial.build(raw,a,sha256(raw),sha256(members['dictionary.bin']))
            y=trial.build(raw,b,sha256(raw),sha256(members['dictionary.bin']))
            self.assertEqual(x,y);self.assertEqual((a/trial.PACK_NAME).read_bytes(),(b/trial.PACK_NAME).read_bytes())
            with zipfile.ZipFile(a/trial.PACK_NAME) as z:
                self.assertEqual(z.read('dictionary.bin'),members['dictionary.bin'])
                self.assertEqual(z.read('unigrams.txt'),members['unigrams.txt'])
                m=json.loads(z.read('manifest.json'));self.assertEqual((m['version'],m['apiVersion'],m['languageIntelligence']['schemaVersion']),(11,3,3))
            with self.assertRaisesRegex(ValueError,'already contains'):trial.build(raw,a,sha256(raw),sha256(members['dictionary.bin']))

    def test_bad_source_and_failed_budget_never_write_installable_pack(self):
        raw,members=self.base()
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'bad'
            with self.assertRaisesRegex(ValueError,'checksum'):trial.build(raw,out,'0'*64)
            with patch.object(trial,'nodes',return_value=3_000_000),self.assertRaisesRegex(ValueError,'runtime budget'):
                trial.build(raw,out,sha256(raw),sha256(members['dictionary.bin']))
            self.assertFalse((out/trial.PACK_NAME).exists())


if __name__=='__main__':unittest.main()
