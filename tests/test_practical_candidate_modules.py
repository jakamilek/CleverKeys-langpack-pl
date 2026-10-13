import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build_practical_candidate_modules as trial
from build_variant_trial import canonical_bytes,sha256


class PracticalCandidateModulesTest(unittest.TestCase):
    def test_shapes_and_links_preserve_phrases_punctuation_case_and_accents(self):
        self.assertEqual(trial.key_shape('czarno-biały'),'punctuation-or-unsupported-key')
        self.assertEqual(trial.key_shape('Microsoft Copilot'),'phrase-no-splitting')
        self.assertEqual(trial.link_targets('[[Wi-Fi|wifi]] [[ChatGPT]] [[Microsoft Copilot]] [[łódź#polski]] [[Plik:x]]'),
                         ['ChatGPT','Microsoft Copilot','Wi-Fi','łódź'])
        self.assertNotEqual('łódź'.lower(),'lodz'.lower())

    def test_category_identity_and_label_spelling_are_kept_without_guessed_names(self):
        files=[({'kind':'wikipedia-category-membership','title':'Kategoria:Chatboty'},
                {'query':{'categorymembers':[{'pageid':1}]}}),
               ({'kind':'wikipedia-article-identities'},{'query':{'pages':[{'pageid':1,'title':'Thing (aplikacja)',
                'pageprops':{'wikibase_item':'Q1'},'revisions':[{'revid':7}]}]}}),
               ({'kind':'wikidata-entities'},{'entities':{'Q1':{'lastrevid':9,'labels':{'pl':{'language':'pl','value':'ChatGPT'}},
                'claims':{'P31':[{'mainsnak':{'snaktype':'value','datavalue':{'value':{'id':'Q2'}}}}]}}}})]
        terms,names=trial.source_candidates(files)
        self.assertFalse(terms)
        self.assertEqual(names['chatgpt'][0]['surface'],'ChatGPT')
        self.assertEqual(names['chatgpt'][0]['articleTitle'],'Thing (aplikacja)')
        self.assertEqual(names['chatgpt'][0]['wikidataRevision'],9)
        del files[-1][1]['entities']['Q1']['labels']['pl']
        _,names=trial.source_candidates(files)
        self.assertIn('thing (aplikacja)',names)
        self.assertNotIn('thing',names)

    def test_native_admission_requires_matching_full_lowercase_proof(self):
        evidence={'interpretations':[{'id':'ordinary','tag':'subst','nameClasses':[],'labels':[]},
            {'id':'name','tag':'subst','nameClasses':['nazwisko'],'labels':[]}],
            'generatedFormProofs':[{'form':'Malina','interpretationId':'ordinary'},
                                  {'form':'malina','interpretationId':'name'}]}
        self.assertEqual(trial.lexical_matches('malina',evidence),[])
        evidence['generatedFormProofs'].append({'form':'malina','interpretationId':'ordinary'})
        self.assertEqual([r['id'] for r in trial.lexical_matches('malina',evidence)],['ordinary'])

    def test_unmeasured_cost_is_distinct_from_zero_and_overlap_is_visible(self):
        rows=[{'surfaceKey':'a','keyShape':'single-key','inBase':False,'status':'pending','runtimeEstimate':None},
              {'surfaceKey':'b','keyShape':'single-key','inBase':False,'status':'native','runtimeEstimate':{'nodes':8,'bytes':80}},
              {'surfaceKey':'old','keyShape':'single-key','inBase':True,'status':'already','runtimeEstimate':{'nodes':8,'bytes':80}},
              {'surfaceKey':'two words','keyShape':'phrase-no-splitting','inBase':False,'status':'phrase','runtimeEstimate':None}]
        count=trial.capacity(rows)
        self.assertEqual((count['newSingleKeys'],count['baseOverlap'],count['newOtherShapes']),(2,1,1))
        self.assertEqual((count['estimatedRecords'],count['unestimatedRecords'],count['estimatedNodes']),(1,1,8))

    def test_frozen_source_checksum_and_path_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);data=canonical_bytes({'query':{}});(p/'source.json').write_bytes(data)
            lock={'files':[{'path':'source.json','bytes':len(data),'sha256':sha256(data),'kind':'test'}]}
            (p/'intake-lock.json').write_bytes(canonical_bytes(lock))
            self.assertEqual(len(trial.read_snapshot(p)[1]),1)
            (p/'source.json').write_bytes(b'{}')
            with self.assertRaisesRegex(ValueError,'checksum'):trial.read_snapshot(p)
            lock['files'][0]['path']='../source.json';(p/'intake-lock.json').write_bytes(canonical_bytes(lock))
            with self.assertRaisesRegex(ValueError,'source path'):trial.read_snapshot(p)


    def test_complete_candidate_build_is_deterministic_and_not_an_importable_pack(self):
        import test_compact_source_trial as fixture
        from build_compact_source_trial import factor
        from build_deferred_names_trial import serialize
        raw,members=fixture.CompactSourceTrialTest().base()
        doc,_=factor(json.loads(members['language-intelligence.json']))
        members['language-intelligence.json']=serialize(doc)
        manifest=json.loads(members['manifest.json']);manifest.update(version=11,apiVersion=3)
        manifest['languageIntelligence'].update(schemaVersion=3,sha256=sha256(members['language-intelligence.json']))
        members['manifest.json']=canonical_bytes(manifest);raw=trial.write_pack(members)
        evidence={'interpretations':[{'id':'r','lemma':'word','tag':'adj','nameClasses':[],'labels':[]}],
            'generatedFormProofs':[{'form':'nowe','interpretationId':'r','tag':'adj','nameClasses':[],'labels':[]}]}
        class Oracle:
            def evidence(self,key):return evidence
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);sources=root/'sources';sources.mkdir()
            (sources/'intake-lock.json').write_bytes(canonical_bytes({'files':[]}))
            audit=root/'ordinary.jsonl';audit.write_bytes(canonical_bytes(dict(surfaceKey='nowe',zipf=1.5,
                reason='below-form-and-family-threshold',**evidence)))
            def build(out):return trial.build(raw,audit,sources,out,Oracle(),lambda k:1.5 if k=='nowe' else 3,
                {},sha256(raw),sha256(members['dictionary.bin']),sha256(audit.read_bytes()),1)
            a,b=root/'a',root/'b';ra,rb=build(a),build(b)
            self.assertEqual(ra,rb);self.assertEqual((a/trial.BUNDLE_NAME).read_bytes(),(b/trial.BUNDLE_NAME).read_bytes())
            self.assertEqual(ra['modules']['common-families']['newSingleKeys'],1)
            self.assertFalse(ra['importable'])
            with zipfile.ZipFile(a/trial.BUNDLE_NAME) as z:
                self.assertFalse(any(Path(n).name in {'manifest.json','dictionary.bin','language-intelligence.json'} for n in z.namelist()))
            with self.assertRaisesRegex(ValueError,'already exists'):build(a)

    def test_source_projection_keeps_literal_labels_and_claims_without_inventing_values(self):
        from intake_practical_candidates import project_entities
        original={'entities':{'Q1':{'id':'Q1','lastrevid':7,'labels':{'pl':{'language':'pl','value':'ChatGPT'}},
            'claims':{'P31':[{'id':'claim','rank':'normal','mainsnak':{'snaktype':'somevalue'},'references':['unused']}],
                      'P856':[{'mainsnak':{'snaktype':'value','datavalue':{'value':'https://example.test/'}}}],
                      'P999':[{'irrelevant':True}]}}}}
        view=project_entities(original)['entities']['Q1']
        self.assertEqual(view['labels'],original['entities']['Q1']['labels'])
        self.assertEqual(view['claims']['P31'][0]['mainsnak'],{'snaktype':'somevalue'})
        self.assertNotIn('P999',view['claims'])
        self.assertNotIn('references',view['claims']['P31'][0])


if __name__=='__main__':unittest.main()
