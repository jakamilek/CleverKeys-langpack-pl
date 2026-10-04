import copy
import math
import unittest
from contract_mobile import pack_rows, rank, compare

class FeedContractTest(unittest.TestCase):
    def rows(self):
        return [dict(input_ids=[0,5,4,2],target_ids=[17],target_positions=[2]),
                dict(input_ids=[0,5,4,4,2],target_ids=[18,19],target_positions=[2,3])]

    def test_candidate_padding_does_not_change_attention_or_target_count(self):
        b=pack_rows(self.rows(),1)
        self.assertEqual(b['input_ids'][0],[0,5,4,2,1])
        self.assertEqual(b['attention_mask'][0],[1,1,1,1,0])
        self.assertEqual(b['target_ids'],[[17,0],[18,19]])
        self.assertEqual(b['target_mask'],[[1.,0.],[1.,1.]])
        self.assertEqual(b['target_positions'],[[2,0],[2,3]])

    def test_original_rows_not_mutated(self):
        rows=self.rows(); before=copy.deepcopy(rows)
        pack_rows(rows,1)
        self.assertEqual(rows,before)

    def test_all_target_positions_masked_at_once(self):
        b=pack_rows(self.rows(),1)
        self.assertEqual(b['input_ids'][1][2:4],[4,4])

    def test_invalid_positions_refused(self):
        for positions in ([0],[3],[2,2],[-1]):
            row=self.rows()[0];row['target_positions']=list(positions)
            row['target_ids']=[17]*len(positions)
            with self.assertRaises(ValueError):pack_rows([row],1)

    def test_empty_oversized_and_noninteger_feeds_refused(self):
        for rows in ([],self.rows()*7,[dict(input_ids=[0]+[4]*511+[2],target_ids=[17],target_positions=[1])],
                     [dict(input_ids=[0,4,2],target_ids=[17.1],target_positions=[1])]):
            with self.assertRaises(ValueError):pack_rows(rows,1)

    def test_target_budget_refused(self):
        row=dict(input_ids=[0]+[4]*33+[2],target_ids=[17]*33,target_positions=list(range(1,34)))
        with self.assertRaises(ValueError):pack_rows([row],1)

    def test_ranking_preserves_explicit_order_on_tie(self):
        self.assertEqual(rank({'łódź':-2.,'Łódź':-2.},['Łódź','łódź']),['Łódź','łódź'])

    def test_nonfinite_missing_or_extra_scores_refused(self):
        for scores in ({'x':math.nan},{'x':math.inf},{'y':0.},{'x':0.,'y':0.}):
            with self.assertRaises(ValueError):rank(scores,['x'])

class ConversionGateTest(unittest.TestCase):
    def fixture(self):
        entries={'x':{'capitalization':{'defaultSurface':'x','variants':[{'surface':'x'},{'surface':'X'}]}}}
        cases={'cases':[{'id':'a','suite':'forms','population':'new','goldSurface':'x',
                         'candidates':[{'key':'x'}]}]}
        requests=[{'id':'a/long/plain','caseId':'a','window':'long','suite':'forms'}]
        reference={'a/long/plain':{'scores':{'x':-1.,'X':-2.}}}
        return entries,cases,requests,reference

    def run_compare(self,scores):
        e,c,r,p=self.fixture()
        return compare(r,c,e,p,{'a/long/plain':scores})

    def test_exact_scores_pass_both_gates(self):
        r=self.run_compare({'x':-1.,'X':-2.})
        self.assertTrue(r['floatParityPassed'])
        self.assertTrue(r['quantizationPreservationPassed'])

    def test_score_drift_with_same_rank_fails_float_only(self):
        r=self.run_compare({'x':-1.01,'X':-2.})
        self.assertFalse(r['floatParityPassed'])
        self.assertTrue(r['quantizationPreservationPassed'])

    def test_top_one_regression_cannot_hide_behind_top_three(self):
        r=self.run_compare({'x':-3.,'X':-2.})
        self.assertFalse(r['quantizationPreservationPassed'])
        self.assertEqual(r['groups']['forms/new/long']['regressions'],1)
        self.assertEqual(r['groups']['forms/new/long']['top3Regressions'],0)
        self.assertEqual(r['changes'][0]['after'],['X','x'])

    def test_missing_prediction_fails_closed(self):
        e,c,r,p=self.fixture()
        with self.assertRaises(ValueError):compare(r,c,e,p,{})

    def test_new_reused_short_long_remain_separate(self):
        e,c,r,p=self.fixture()
        c['cases'].append({**c['cases'][0],'id':'b','population':'reused'})
        r.append({**r[0],'id':'b/short/plain','caseId':'b','window':'short'})
        p['b/short/plain']=p['a/long/plain']
        a={key:value['scores'] for key,value in p.items()}
        report=compare(r,c,e,p,a)
        self.assertEqual(set(report['groups']),{'forms/new/long','forms/reused/short'})

if __name__=='__main__':unittest.main()
