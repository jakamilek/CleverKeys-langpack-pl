"""Test stale/incomplete evidence rejection; fixture scores are never model quality."""
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import contract
from collect_results import collect, paired
from loading import expected_unused_keys, validate_loading_info


def synthetic(name):
    cases,entries,request=contract.prepare();by_id={c['id']:c for c in cases}
    rows=[]
    for row in request['requests']:
        order=contract.baseline(by_id[row['caseId']],entries)
        scores={s:-float(order.index(s)) for s in row['candidates']}
        rows.append({'id':row['id'],'scores':scores,'prepareMs':1.,'inferenceMs':1.,'totalMs':2.,
                     'retainedWords':len(row['context'].split()),'inputTokens':[3]*2,
                     'trace':[{'targetPositions':[1],'targetTokenIds':[99],'inputTokens':3,
                               'meanLogProbability':scores[s],'sumLogProbability':scores[s]} for s in row['candidates']]})
    screen=json.loads((contract.ROOT.parent/'polish_mlm_screen_v2/results/BartekK--distilHerBERT-base-cased.json').read_text())
    return {'protocol':contract.VERSION,'model':contract.MODELS[name],
            'requestsSha256':contract.digest(request),'freezeManifestSha256':contract.digest(contract.verify_freeze()),
            'codeCommit':'a'*40,'tokenizerBackendSha256':screen['backendSha256'],'predictions':rows,
            'phoneMeasured':False,'weightsPublished':False,'parameters':1,'peakHostRssMiB':1.,
            'modelFiles':[{'path':'pytorch_model.bin','bytes':10,'sha256':'b'*64}],
            'loadingInfo':{'missing_keys':[],'mismatched_keys':[],'unexpected_keys':sorted(expected_unused_keys(name)),
                           'error_msgs':[],'projectionMaxAbsErrors':[0.,0.,0.]}}


def write(root,name,result):
    p=root/name;p.mkdir(exist_ok=True);(p/'predictions.json').write_text(json.dumps(result))
    ident={k:result[k] for k in ['model','requestsSha256','freezeManifestSha256','codeCommit','tokenizerBackendSha256']}
    validation={**ident,'loadingInfo':result['loadingInfo'],'modelFiles':result['modelFiles'],
                'requestsValidated':256,'beforeLabelledInference':True,'sourceCasePreservation':True}
    preflight={**ident,'requestsValidated':256,'beforeWeightsLoad':True}
    (p/'validation.json').write_text(json.dumps(validation));(p/'tokenizer-validation.json').write_text(json.dumps(preflight))
    (p/'report.json').write_text(json.dumps(contract.evaluate(name,result)))


class Gates(unittest.TestCase):
    def test_exact_original_checkpoint_loading_contract(self):
        for name in contract.MODELS:
            info=synthetic(name)['loadingInfo']
            validate_loading_info(name,info)
            info['unexpected_keys'].reverse()
            validate_loading_info(name,info)
        self.assertEqual(len(expected_unused_keys('herbert')),4)
        self.assertEqual(len(expected_unused_keys('distilherbert')),0)

    def test_missing_mismatched_unknown_partial_duplicate_loading_evidence_rejected(self):
        for name in contract.MODELS:
            good=synthetic(name)['loadingInfo']
            bad=[]
            for field in ['missing_keys','mismatched_keys','error_msgs','unexpected_keys']:
                absent=copy.deepcopy(good);absent.pop(field);bad.append(absent)
                wrong=copy.deepcopy(good);wrong[field]=None;bad.append(wrong)
            for field in ['missing_keys','mismatched_keys','error_msgs']:
                wrong=copy.deepcopy(good);wrong[field]=['cls.predictions.bias'];bad.append(wrong)
            unknown=copy.deepcopy(good);unknown['unexpected_keys'].append('cls.predictions.bias');bad.append(unknown)
            if name=='herbert':
                for n in range(4):
                    partial=copy.deepcopy(good);partial['unexpected_keys']=partial['unexpected_keys'][:n];bad.append(partial)
                duplicate=copy.deepcopy(good);duplicate['unexpected_keys'][0]=duplicate['unexpected_keys'][1];bad.append(duplicate)
            else:
                wrong=copy.deepcopy(good);wrong['unexpected_keys']=sorted(expected_unused_keys('herbert'));bad.append(wrong)
            for info in bad:
                with self.subTest(name=name,info=info),self.assertRaises(ValueError):
                    validate_loading_info(name,info)

    def test_collector_rejects_herbert_loading_changes_before_quality(self):
        for keys in [[],sorted(expected_unused_keys('herbert'))[:-1],
                     sorted(expected_unused_keys('herbert'))+['cls.predictions.bias']]:
            with self.subTest(keys=keys),tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'GITHUB_SHA':'a'*40}):
                root=Path(tmp)
                for name in contract.MODELS:
                    result=synthetic(name)
                    if name=='herbert':result['loadingInfo']['unexpected_keys']=keys
                    write(root,name,result)
                with self.assertRaises(ValueError):collect(root)

    def test_fresh_contexts_are_disjoint_and_new_keys_are_not_old_gold(self):
        cases,entries,request=contract.prepare();old=contract.source_contract.cases_and_sources()[0]
        gold_keys={c['candidates'][0]['key'] for c in old if c['suite']=='forms'}
        texts={c['leftContext'] for c in old}
        fresh=[c for c in cases if c['population'].startswith('fresh_')]
        self.assertEqual(len(fresh),64)
        self.assertFalse(texts & {c['leftContext'] for c in fresh})
        for c in fresh:
            if c['population'].endswith('new_key'):self.assertNotIn(c['candidates'][0]['key'],gold_keys)
        self.assertEqual(len(request['requests']),256)

    def test_long_contexts_change_actual_16_32_input_without_changing_case(self):
        cases,_,req=contract.prepare();by_id={c['id']:c for c in cases}
        changed=0
        for a,b in zip(req['requests'][::2],req['requests'][1::2]):
            self.assertEqual(a['candidates'],b['candidates'])
            c=by_id[a['caseId']]
            if c['population'].startswith('fresh_long_'):
                self.assertNotEqual(a['context'],b['context']);self.assertEqual(len(a['context'].split()),16)
                self.assertEqual(b['context'],c['leftContext']);changed+=1
        self.assertEqual(changed,32)

    def test_labels_metadata_never_enter_model_requests(self):
        for r in contract.prepare()[2]['requests']:
            self.assertEqual(set(r),{'id','caseId','window','context','candidates'})
        self.assertEqual((contract.ROOT/'mlm.py').read_bytes(),(contract.ROOT.parent/'polish_mlm_compare_v1/mlm.py').read_bytes())

    def test_missing_model_duplicate_nan_wrong_source_rejected(self):
        for change in [lambda r:r['predictions'].pop(),lambda r:r['predictions'].append(r['predictions'][0]),
                       lambda r:r['predictions'][0]['scores'].update(fake=0.),
                       lambda r:r['predictions'][0]['scores'].update({next(iter(r['predictions'][0]['scores'])):float('nan')})]:
            r=synthetic('distilherbert');change(r)
            with self.assertRaises(ValueError):contract.evaluate('distilherbert',r)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);write(root,'distilherbert',synthetic('distilherbert'))
            with self.assertRaises(ValueError):collect(root)

    def test_complete_collector_recomputes_both_current_reports(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'GITHUB_SHA':'a'*40}):
            root=Path(tmp)
            for name in contract.MODELS:write(root,name,synthetic(name))
            out=collect(root);self.assertFalse(out['productionApproved'])
            self.assertFalse(out['screening']['default16Approved'])
            self.assertEqual(out['inputs']['differentWindows'],32)
            self.assertEqual(len(out['models']['herbert']['decisions']),256)

    def test_stale_preflight_wrong_report_and_partial_weight_evidence_rejected(self):
        edits=[('tokenizer-validation.json',lambda d:d.update(beforeWeightsLoad=False)),
               ('validation.json',lambda d:d.update(codeCommit='b'*40)),
               ('report.json',lambda d:d['decisions'][0].update(gold='fake')),
               ('predictions.json',lambda d:d.update(modelFiles=[])),
               ('predictions.json',lambda d:d['loadingInfo'].update(missing_keys=['cls.bias'])),
               ('predictions.json',lambda d:d['loadingInfo'].update(projectionMaxAbsErrors=[.1,0.,0.])),
               ('predictions.json',lambda d:d['predictions'][0]['trace'][0].update(meanLogProbability=-999.))]
        for filename,edit in edits:
            with self.subTest(filename=filename),tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'GITHUB_SHA':'a'*40}):
                root=Path(tmp)
                for name in contract.MODELS:write(root,name,synthetic(name))
                p=root/'distilherbert'/filename;d=json.loads(p.read_text());edit(d);p.write_text(json.dumps(d))
                with self.assertRaises(ValueError):collect(root)

    def test_collector_rejects_wrong_run_commit(self):
        with tempfile.TemporaryDirectory() as tmp,patch.dict(os.environ,{'GITHUB_SHA':'b'*40}):
            root=Path(tmp)
            for name in contract.MODELS:write(root,name,synthetic(name))
            with self.assertRaises(ValueError):collect(root)

    def test_paired_comparison_rejects_changed_gold(self):
        r=contract.evaluate('herbert',synthetic('herbert'));bad=copy.deepcopy(r)
        bad['decisions'][0]['gold']='fake'
        with self.assertRaises(ValueError):paired(r,bad)


if __name__=='__main__':unittest.main()
