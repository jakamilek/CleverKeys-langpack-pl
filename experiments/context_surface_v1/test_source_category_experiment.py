"""Source provenance, absent categories, gold isolation and ranking boundaries."""
import copy
import json
import unittest

from source_category_experiment import (ROOT, PHRASES, associated_scores, evaluate,
                                        prepare_requests, validate_sidecar)
from source_category_cases import MAIN, build
from prototype import digest


class SourceCategoryTest(unittest.TestCase):
    def setUp(self):
        self.sidecar=json.loads((ROOT/'source-category-sidecar.json').read_text())
        self.cases=build(self.sidecar)
        self.request=prepare_requests(self.cases,self.sidecar)
        self.entries=validate_sidecar(self.sidecar)

    def test_missing_surname_and_street_are_not_invented(self):
        self.assertEqual([v['surface'] for v in self.entries['łódzki']['capitalization']['variants']],['łódzki'])
        self.assertEqual({c['id'] for c in self.entries['warszawska']['categories']},{'NAME:nazwisko','POS:adj'})
        self.assertNotIn('street',json.dumps(self.sidecar,ensure_ascii=False))
        self.assertNotIn('fruit',json.dumps(self.sidecar,ensure_ascii=False))

    def test_all_extra_source_classes_are_preserved(self):
        self.assertEqual({c['id'] for c in self.entries['malina']['categories']},
                         {'NAME:nazwa_pospolita','NAME:imię','NAME:nazwisko','NAME:nazwa_geograficzna'})
        self.assertIn('Malin',{r['lemma'] for r in self.entries['malina']['interpretations']})
        self.assertIn('Łodzia',{r['lemma'] for r in self.entries['łodzi']['interpretations']})

    def test_capitalized_common_input_is_not_a_case_proof(self):
        common=[p for p in self.entries['łódź']['generatedFormProofs'] if p['lemma']=='łódź']
        self.assertTrue(common)
        self.assertEqual({p['form'] for p in common},{'łódź'})
        lower=self.entries['łódź']['capitalization']['variants'][0]
        self.assertEqual(lower['categoryIds'],['NAME:nazwa_pospolita'])

    def test_swapped_mapping_and_fabricated_proof_are_rejected(self):
        broken=copy.deepcopy(self.sidecar)
        entry=next(e for e in broken['entries'] if e['surfaceKey']=='łódź')
        a,b=entry['capitalization']['variants'];a['categoryIds'],b['categoryIds']=b['categoryIds'],a['categoryIds']
        with self.assertRaises(ValueError):validate_sidecar(broken)
        broken=copy.deepcopy(self.sidecar)
        broken['entries'][0]['generatedFormProofs'][0]['lemma']='invented'
        with self.assertRaises(ValueError):validate_sidecar(broken)

    def test_dangling_and_duplicate_categories_rejected(self):
        for value in [['NAME:absent'],['NAME:nazwa_pospolita','NAME:nazwa_pospolita']]:
            broken=copy.deepcopy(self.sidecar);broken['entries'][0]['capitalization']['variants'][0]['categoryIds']=value
            with self.assertRaises(ValueError):validate_sidecar(broken)

    def test_counts_and_reuse_are_explicit(self):
        self.assertEqual(len(self.cases['cases']),184)
        self.assertEqual(len(self.request['requests']),368)
        main=[c for c in self.cases['cases'] if c['diagnostic']['category'] in MAIN]
        self.assertEqual(len(main),68)
        self.assertEqual(sum('reuseFrom' in c['diagnostic'] for c in main),60)
        self.assertEqual(sum(c['expected']['surface'][0].isupper() for c in main),32)
        self.assertEqual(sum(c['diagnostic']['category']=='unsupported_street' for c in self.cases['cases']),4)

    def test_gold_does_not_enter_requests(self):
        for row in self.request['requests']:
            for k in ['expected','expectedCategoryIds','diagnostic','reuseFrom','sourceId']:
                self.assertNotIn(k,row)
        self.assertEqual(digest({k:v for k,v in self.request.items() if k!='requestSha256'}),self.request['requestSha256'])

    def test_generic_renderer_does_not_add_per_word_semantics(self):
        self.assertNotIn('owoc',' '.join(PHRASES.values()))
        self.assertNotIn('miasto',' '.join(PHRASES.values()))
        self.assertNotIn('ulica',' '.join(PHRASES.values()))

    def test_many_categories_map_to_one_variant_and_require_complete_scores(self):
        group=next(g for r in self.request['requests'] for g in r['candidates'] if g['surfaceKey']=='malina')
        values={c['id']:-10. for c in group['categories']};values['NAME:imię']=-1.
        self.assertEqual(associated_scores(group,values),{'malina':-10.,'Malina':-1.})
        values.pop('NAME:nazwisko')
        with self.assertRaises(ValueError):associated_scores(group,values)

    def test_top_three_guarantee_and_slot_limits_are_mechanical(self):
        report=evaluate(self.cases,self.request)['metrics']['long']
        self.assertEqual(report['main']['top3'],68)
        self.assertEqual(report['main']['top1'],36)
        self.assertEqual(report['byCategory']['top3_probe']['top3'],36)
        self.assertEqual(report['byCategory']['source_single_variant']['top1'],8)
        self.assertEqual(report['byCategory']['sentence_start']['top1'],9)
        self.assertEqual(report['byCategory']['missing_key']['reachable'],0)
        self.assertEqual(report['byCategory']['slot_limit']['top3'],0)
        self.assertEqual(report['byCategory']['slot_limit']['reachable'],9)
        self.assertIsNone(report['byCategory']['ambiguous']['top3'])


if __name__=='__main__':unittest.main()
