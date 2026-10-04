import copy
import json
import unittest
from collections import Counter
from contract_meta import BASE,MODELS,prepare,requests,evaluate,validate_result,digest,legacy
from make_cases_meta import build
from render_metadata import explained_text,GLOSSARY,GUIDANCE
from run_metadata import mlm_inputs,nli_inputs,choice_ids,fit_context,engine

class Tokenizer:
    cls_token_id=0;sep_token_id=1;mask_token_id=2;unk_token_id=9999
    def encode(self,s,**kwargs):return list(s.encode())
    def __call__(self,a,b):return {'input_ids':self.encode(a+' '+b)}
    def apply_chat_template(self,messages,**kwargs):
        self.messages=messages
        return self.encode(json.dumps(messages,ensure_ascii=False))

class BudgetTokenizer(Tokenizer):
    def encode(self,s,**kwargs):return [10]*len(s.split())

class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.source,cls.entries,cls.cases,cls.request=prepare()
    def result(self):
        return {'protocol':self.request['protocol'],'model':MODELS['herbert'],
                'requestsSha256':digest(self.request),
                'predictions':[{'id':r['id'],'scores':{c['surface']:0. for c in r['candidates']},
                                'inferenceMs':1.} for r in self.request['requests']]}
    def test_counts_and_populations(self):
        self.assertEqual(len(self.cases['cases']),116)
        self.assertEqual(Counter(c['population'] for c in self.cases['cases']),{'reused':84,'new':32})
        self.assertEqual(len(self.request['requests']),1160)
        new=[c for c in self.cases['cases'] if c['population']=='new']
        self.assertEqual(sum(c['goldSurface'][0].islower() for c in new),16)
        self.assertEqual(sum(c['goldSurface'][0].isupper() for c in new),16)
    def test_reproducible_cases(self):self.assertEqual(build(),self.cases)
    def test_new_contexts_not_reused(self):
        old={c['leftContext'] for c in self.cases['cases'] if c['population']=='reused'}
        self.assertFalse(old&{c['leftContext'] for c in self.cases['cases'] if c['population']=='new'})
    def test_no_gold_or_population_in_model_requests(self):
        for r in self.request['requests']:
            self.assertFalse({'goldSurface','population','contextType','sourceSlate'}&set(r))
            self.assertTrue(all('goldSurface' not in c for c in r['candidates']))
    def test_global_glossary_covers_actual_codes(self):
        rows=[r for e in self.entries.values() for r in legacy.readings(e)]
        self.assertTrue({r['partOfSpeech'] for r in rows}<=set(GLOSSARY['partOfSpeech']))
        self.assertTrue({n for r in rows for n in r['nameClasses']}<=set(GLOSSARY['nameClasses']))
        self.assertFalse(set(self.entries)&set(GLOSSARY['partOfSpeech']))
    def test_source_fields_preserved_in_explanation(self):
        for e in self.entries.values():
            rows=legacy.readings(e);text=explained_text(rows)
            for r in rows:
                self.assertIn('„'+r['lemma']+'”',text)
                self.assertIn(' / '.join(r['surfaces']),text)
                for label in r['labels']:self.assertIn(label,text)
    def test_no_invented_word_meanings(self):
        text=explained_text(legacy.readings(self.entries['łódź']))
        self.assertNotIn('miasto',text);self.assertNotIn('sprzęt',text)
        text=explained_text(legacy.readings(self.entries['malina']))
        self.assertNotIn('owoc',text)
    def test_unknown_codes_and_missing_name_are_not_guessed(self):
        text=explained_text([{'lemma':'x','partOfSpeech':'UNKNOWN','nameClasses':[],
                              'labels':['unknown.label'],'surfaces':['x']}])
        self.assertIn('nieobjaśniony kod UNKNOWN',text)
        self.assertIn('nie podano klasy nazwy',text)
        self.assertIn('unknown.label',text);self.assertNotIn('nazwa pospolita',text)
    def test_guidance_controls_and_explained_text_match(self):
        for c in self.cases['cases']:
            for w in ['short','long']:
                rows={r['condition']:r for r in self.request['requests'] if r['caseId']==c['id'] and r['window']==w}
                self.assertEqual(rows['explained']['candidates'],rows['guided']['candidates'])
                self.assertEqual(rows['guided']['instruction'],GUIDANCE)
                self.assertEqual(rows['plain_guided']['instruction'],GUIDANCE)
                self.assertEqual(rows['plain']['candidates'],rows['plain_guided']['candidates'])
                self.assertTrue(all(not rows[n]['instruction'] for n in ['plain','raw','explained']))
                core=lambda r:[(a['key'],a['surface'],a['engineScore']) for a in r['candidates']]
                self.assertEqual(len({json.dumps(core(r)) for r in rows.values()}),1)
                self.assertEqual(len({r['context'] for r in rows.values()}),1)
    def test_reused_plain_raw_prompt_identity_all_three_adapters(self):
        old_cases=json.loads((BASE/'cases.json').read_text())
        old=legacy.requests(old_cases,self.entries)['requests'];old_by_id={r['id']:r for r in old}
        for r in self.request['requests']:
            if r['caseId'].startswith('newform-') or r['condition'] not in {'plain','raw'}:continue
            original=old_by_id[r['caseId']+'/'+r['window']+'/'+('plain' if r['condition']=='plain' else 'metadata')]
            for c,oc in zip(r['candidates'],original['candidates']):
                self.assertEqual(c,oc)
                self.assertEqual(mlm_inputs(r,r['context'],c,Tokenizer()),engine.mlm_inputs(original,original['context'],oc,Tokenizer()))
                self.assertEqual(nli_inputs(r,r['context'],c),engine.nli_inputs(original,original['context'],oc))
            self.assertEqual(choice_ids(r,r['context'],r['candidates'],Tokenizer()),
                             engine.choice_ids(original,original['context'],original['candidates'],Tokenizer()))
    def test_guidance_reaches_every_adapter(self):
        r=next(r for r in self.request['requests'] if r['condition']=='guided');c=r['candidates'][0]
        self.assertIn(GUIDANCE,nli_inputs(r,r['context'],c)[0])
        t=Tokenizer();ids=mlm_inputs(r,r['context'],c,t)[0]
        self.assertEqual(ids[1:1+len('Dane słownika:\n'.encode())],list('Dane słownika:\n'.encode()))
        self.assertIn(GUIDANCE.encode(),bytes(ids[1:-1]))
        choice_ids(r,r['context'],r['candidates'],t)
        self.assertTrue(t.messages[1]['content'].startswith(GUIDANCE))
    def test_all_conditions_share_retained_context(self):
        rows=copy.deepcopy(self.request['requests'][:5])
        for r in rows:r['context']=' '.join(['word']*700)
        retained,removed,tokens,limit=fit_context(rows,BudgetTokenizer(),'nli')
        self.assertGreater(removed,0);self.assertLess(tokens,513)
        self.assertTrue(all(len(BudgetTokenizer()(*nli_inputs(r,retained,c))['input_ids'])<=limit for r in rows for c in r['candidates']))
    def test_metadata_alone_over_budget_is_rejected(self):
        rows=copy.deepcopy(self.request['requests'][:5]);rows[-1]['instruction']=' '.join(['rule']*600)
        with self.assertRaisesRegex(ValueError,'exceed budget'):fit_context(rows,BudgetTokenizer(),'nli')
    def test_ties_keep_baseline_and_populations_separate(self):
        report=evaluate(self.cases,self.entries,self.request,self.result())
        for condition in ['plain','raw','explained','guided']:
            old=report['groups']['forms/reused/long/'+condition];new=report['groups']['forms/new/long/'+condition]
            self.assertEqual((old['top1'],old['top3']),(32,64))
            self.assertEqual((new['top1'],new['top3']),(16,32))
            self.assertEqual(new['repairs'],0);self.assertEqual(new['regressions'],0)
        for g in report['pairedConditions'].values():self.assertEqual(g['changedTop1'],0)
    def test_paired_repairs_and_regressions(self):
        result=self.result();index={p['id']:p for p in result['predictions']}
        cs=[c for c in self.cases['cases'] if c['population']=='new'][:2]
        for c in cs:
            p=index[c['id']+'/long/guided'];p['scores'][c['goldSurface']]=1.
        p=index[cs[0]['id']+'/long/guided']
        p['scores']={s:float(s!=cs[0]['goldSurface']) for s in p['scores']}
        r=evaluate(self.cases,self.entries,self.request,result)
        self.assertEqual(r['pairedConditions']['forms/new/long/explained->guided']['repairs'],1)
        self.assertEqual(r['pairedConditions']['forms/new/long/explained->guided']['regressions'],1)
    def test_invalid_predictions_rejected(self):
        for mutate in [lambda r:r['predictions'].pop(),
                       lambda r:r['predictions'].append(r['predictions'][0]),
                       lambda r:r.update(requestsSha256='wrong'),
                       lambda r:r.update(protocol='wrong'),
                       lambda r:r['predictions'][0]['scores'].update(invented=1.),
                       lambda r:r['predictions'][0]['scores'].update({next(iter(r['predictions'][0]['scores'])):float('nan')}),
                       lambda r:r['predictions'][0].update(inferenceMs=-1)]:
            result=self.result();mutate(result)
            with self.assertRaises(ValueError):validate_result(self.request,result)

if __name__=='__main__':unittest.main()
