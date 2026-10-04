"""Fresh-fixture, many-meaning spelling and top-three boundary checks."""
import copy
import json
import unittest

from natural_cases import SPECS, build
from natural_experiment import (MAIN, ROOT, associated_scores, evaluate, prepare_requests,
                                sense_hypothesis, validate_sidecar)
from prototype import digest


class NaturalExperimentTest(unittest.TestCase):
    def setUp(self):
        self.cases, self.sidecar = build()
        self.request = prepare_requests(self.cases,self.sidecar)

    def test_counts_balance_and_no_old_context_reuse(self):
        main = [c for c in self.cases['cases'] if c['diagnostic']['category'] in MAIN]
        self.assertEqual(len(main),64)
        self.assertEqual(len(self.cases['cases']),164)
        self.assertEqual(len(self.request['requests']),328)
        self.assertEqual(len({c['id'] for c in self.cases['cases']}),164)
        self.assertEqual(len({c['beforeCursor'] for c in main}),64)
        for category in MAIN:
            group = [c for c in main if c['diagnostic']['category']==category]
            self.assertEqual(len(group),16)
            self.assertEqual(sum(c['expected']['surface'][0].isupper() for c in group),8)
        old = json.loads((ROOT/'diagnostic-cases.json').read_text())
        old_contexts = {c['beforeCursor'] for c in old['cases']}
        self.assertFalse(old_contexts & {c['beforeCursor'] for c in main})

    def test_labels_do_not_enter_requests_and_hash_is_valid(self):
        for row in self.request['requests']:
            self.assertNotIn('expected',row)
            self.assertNotIn('expectedSenseIds',row)
            self.assertNotIn('diagnostic',row)
            self.assertNotIn('sourceId',row)
        self.assertEqual(digest({k:v for k,v in self.request.items() if k!='requestSha256'}),self.request['requestSha256'])

    def test_street_and_surname_share_capitalized_surface(self):
        entries=validate_sidecar(self.sidecar)
        street=entries['warszawska']
        variants=street['capitalization']['variants']
        self.assertEqual(variants[0]['senseIds'],['adjective'])
        self.assertEqual(variants[1]['senseIds'],['street','surname'])
        self.assertEqual(next(s['kind'] for s in street['senses'] if s['id']=='adjective'),'adjective')
        self.assertEqual(len(entries),7)

    def test_inflected_form_has_its_own_surface_key(self):
        entries=validate_sidecar(self.sidecar)
        self.assertIn('łódź',entries)
        self.assertIn('łodzi',entries)
        self.assertEqual(entries['łodzi']['capitalization']['variants'][1]['surface'],'Łodzi')

    def test_many_senses_reduce_to_best_allowed_surface(self):
        group=next(g for r in self.request['requests'] for g in r['candidates'] if g['surfaceKey']=='warszawska')
        self.assertEqual(associated_scores(group,{'adjective':-4,'street':-3,'surname':-1}),
                         {'warszawska':-4,'Warszawska':-1})
        with self.assertRaises(ValueError):associated_scores(group,{'adjective':-4,'street':-3})

    def test_association_rejects_orphan_unknown_and_duplicate(self):
        for change in ('orphan','unknown','duplicate'):
            broken=copy.deepcopy(self.sidecar)
            if change=='orphan':broken['entries'][0]['senses'].append({'id':'unused','kind':'common_noun','descriptionPl':'rzecz'})
            if change=='unknown':broken['entries'][0]['capitalization']['variants'][0]['senseIds']=['absent']
            if change=='duplicate':broken['entries'][0]['capitalization']['variants'][0]['senseIds']=['boat','boat']
            with self.assertRaises(ValueError):validate_sidecar(broken)

    def test_top3_pressure_missing_key_and_slot_limits_are_separate(self):
        report=evaluate(self.cases,self.request)['metrics']['long']
        self.assertEqual(report['main']['top3'],64)
        self.assertEqual(report['byCategory']['top3_probe']['top3'],32)
        self.assertEqual(report['byCategory']['top3_probe']['reachable'],64)
        self.assertEqual(report['byCategory']['missing_key']['reachable'],0)
        self.assertEqual(report['byCategory']['slot_limit']['top3'],0)
        self.assertEqual(report['byCategory']['slot_limit']['reachable'],7)

    def test_sentence_initial_display_does_not_define_meaning(self):
        report=evaluate(self.cases,self.request)
        self.assertEqual(report['metrics']['long']['byCategory']['sentence_start']['top1'],14)
        for row in report['rows']:
            if row['category']=='sentence_start':
                self.assertTrue(row['suggestions'][0]['surface'][0].isupper())
                self.assertEqual(row['suggestions'][0]['variantSurface'],row['surfaceKey'])

    def test_ambiguous_has_no_fake_accuracy_and_controls_repeat_source_only(self):
        report=evaluate(self.cases,self.request)['metrics']['long']['byCategory']
        self.assertIsNone(report['ambiguous']['top3'])
        originals={c['id']:c for c in self.cases['cases'] if c['diagnostic']['category'] in MAIN}
        for case in self.cases['cases']:
            if 'sourceId' in case['diagnostic']:
                source=originals[case['diagnostic']['sourceId']]
                self.assertEqual(case['beforeCursor'],source['beforeCursor'])
                self.assertEqual(case['expected'],source['expected'])

    def test_global_hypothesis_is_unchanged_and_current_is_explicit(self):
        self.assertEqual(sense_hypothesis('łódź','miasto','global_attributes'),
                         'W tym kontekście słowo „łódź” oznacza miasto.')
        self.assertIn('Ostatnie dopisywane słowo',sense_hypothesis('łódź','miasto','current_attributes'))


if __name__=='__main__':unittest.main()
