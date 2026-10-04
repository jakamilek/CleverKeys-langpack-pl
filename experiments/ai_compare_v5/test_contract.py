import copy
import json
import math
import unittest
from contract import *
from make_cases import build,RECORDED,PAIRS
from run_model import fit_context,mlm_inputs,nli_inputs

class ContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source,cls.entries,cls.cases,cls.request=prepare()

    def result(self,request=None):
        r=request or self.request
        return {'model':MODELS['herbert'],'requestsSha256':digest(r),
                'predictions':[{'id':x['id'],'scores':{c['surface']:0. for c in x['candidates']},
                                'inferenceMs':1.} for x in r['requests']]}

    def test_fixture_is_reproducible_and_balanced(self):
        self.assertEqual(build(),self.cases)
        main=[c for c in self.cases['cases'] if c['suite']=='forms']
        self.assertEqual(len(main),64)
        self.assertEqual(sum(c['goldSurface']==c['goldSurface'].lower() for c in main),32)
        self.assertEqual(len(self.request['requests']),376)

    def test_gold_reachable_only_when_decoder_has_it(self):
        for c in self.cases['cases']:
            if c.get('goldSurface') is None:continue
            if c['suite']=='missing_key':self.assertNotIn(c['goldSurface'],baseline(c,self.entries))
            else:self.assertIn(c['goldSurface'],baseline(c,self.entries))

    def test_request_contains_no_evaluation_annotations(self):
        allowed={'id','caseId','suite','window','metadata','context','candidates','nextWord'}
        for r in self.request['requests']:
            self.assertLessEqual(set(r),allowed)
            for c in r['candidates']:
                self.assertLessEqual(set(c),{'key','surface','engineScore','sourceText','punctuation'})
        self.assertNotIn('goldSurface',canonical(self.request).decode())
        self.assertNotIn('goldPunctuation',canonical(self.request).decode())

    def test_all_source_forms_are_real_and_both_layouts_are_supported(self):
        for key in PAIRS:
            e=self.entries[key];forms={v['surface'] for v in e['capitalization']['variants']}
            self.assertEqual(forms,{key,key[:1].upper()+key[1:]})
            self.assertTrue(readings(e))
        self.assertIn('generatedFormProofs',self.entries['łódź']['metadata']['sourceEvidence'])
        self.assertIn('lexicalReadings',self.entries['tutaj']['metadata']['sourceEvidence'])

    def test_source_projection_retains_every_association(self):
        for e in self.entries.values():
            ev=e.get('metadata',{}).get('sourceEvidence',{})
            rs=readings(e)
            if 'lexicalReadings' in ev:self.assertEqual(len(rs),len(ev['lexicalReadings']))
            for p in ev.get('generatedFormProofs',[]):
                orig={i['id']:i for i in ev['interpretations']}[p['interpretationId']]
                self.assertTrue(any(r['lemma']==orig['lemma'] and r['partOfSpeech']==orig['tag'].split(':')[0]
                                    and r['nameClasses']==orig['nameClasses'] and r['labels']==orig['labels']
                                    and p['form'] in r['surfaces'] for r in rs))

    def test_wrong_source_pack_rejected(self):
        s=copy.deepcopy(self.source);s['packSha256']='wrong'
        with self.assertRaises(ValueError):validate_sources(s)

    def test_source_cannot_add_an_unoffered_form(self):
        e=copy.deepcopy(self.entries['tutaj'])
        e['metadata']['sourceEvidence']['lexicalReadings'][0]['surfaces']=['TUTAJ']
        with self.assertRaises(ValueError):readings(e)

    def test_recorded_scores_and_order_preserved_in_cases(self):
        for c in self.cases['cases']:
            if c['suite']=='recorded_replay':
                self.assertEqual([(x['key'],x['engineScore']) for x in c['candidates']],RECORDED[c['sourceSlate']])

    def test_baseline_top3_saturation_reported_without_ai_claim(self):
        report=evaluate(self.cases,self.entries,self.request,self.result())
        g=report['groups']['forms/long/plain']
        self.assertEqual((g['baselineTop1'],g['baselineTop3'],g['top1'],g['top3']),(32,64,32,64))
        self.assertEqual((g['keyTop1'],g['keyTop3']),(64,64))
        missing=report['groups']['missing_key/long/plain']
        self.assertEqual((missing['reachable'],missing['top3']),(0,0))

    def test_nonfinite_and_missing_scores_rejected(self):
        r=self.result();p=r['predictions'][0];p['scores'][next(iter(p['scores']))]=math.nan
        with self.assertRaises(ValueError):validate_scores(self.request,r)
        r=self.result();r['predictions'][0]['scores'].pop(next(iter(r['predictions'][0]['scores'])))
        with self.assertRaises(ValueError):validate_scores(self.request,r)

    def test_incomplete_duplicate_and_stale_predictions_rejected(self):
        for mutation in ['missing','duplicate','stale']:
            r=self.result()
            if mutation=='missing':r['predictions'].pop()
            elif mutation=='duplicate':r['predictions'].append(r['predictions'][0])
            else:r['requestsSha256']='wrong'
            with self.assertRaises(ValueError):validate_scores(self.request,r)

    def test_all_ties_preserve_baseline_despite_reversed_option_order(self):
        report=evaluate(self.cases,self.entries,self.request,self.result())
        for d in report['decisions']:
            self.assertEqual(d['rank'][0],d['baseline'][0])

    def test_plain_and_metadata_have_same_words_scores_and_context(self):
        rows={r['id']:r for r in self.request['requests']}
        for r in rows.values():
            if not r['metadata']:continue
            plain=rows[r['id'].replace('/metadata','/plain')]
            self.assertEqual(r['context'],plain['context'])
            for a,b in zip(r['candidates'],plain['candidates']):
                self.assertEqual({k:v for k,v in a.items() if k!='sourceText'},
                                 {k:v for k,v in b.items() if k!='sourceText'})
                self.assertEqual(b['sourceText'],'')

    def test_punctuation_options_have_correct_spacing_and_no_gold_input(self):
        for r in self.request['requests']:
            if r['suite']=='punctuation_before_word':
                self.assertEqual({c['surface'] for c in r['candidates']},{r['nextWord'],', '+r['nextWord']})
                for c in r['candidates']:
                    premise,hypothesis=nli_inputs(r,r['context'],c)
                    self.assertIn(r['nextWord'],premise)
                    self.assertNotIn('gold',hypothesis)

    def test_metadata_effect_counts_repairs_and_regressions_separately(self):
        result=self.result();rows={r['id']:r for r in self.request['requests']}
        for p in result['predictions']:
            if p['id']=='form-łódź-2/long/metadata':p['scores']['Łódź']=2.
        report=evaluate(self.cases,self.entries,self.request,result)
        self.assertEqual(report['metadataVsPlain']['forms/long']['repairs'],1)
        self.assertEqual(report['metadataVsPlain']['forms/long']['regressions'],0)

if __name__=='__main__':unittest.main()
