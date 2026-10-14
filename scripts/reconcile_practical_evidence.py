#!/usr/bin/env python3
"""Deterministic reconciliation of source observations; never a langpack builder.

Source-page assessment is recorded human-readable evidence, not an automatic
proof from a language model. This script validates joins, provenance and counts.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

def digest(data):
    return hashlib.sha256(data).hexdigest()

def reconcile(decisions, observations, probes):
    old = {r['surfaceKey']:r for r in decisions}
    if len(old) != len(decisions) or len(old) != 2913:
        raise ValueError('duplicate or unexpected baseline')
    if Counter(r['state'] for r in decisions) != {'confirmed':1336, 'rejected-this-selection':911, 'needs-evidence':666}:
        raise ValueError('wrong baseline decisions')
    known_probes = {p['key']:p for p in probes}
    reviewed = {}; supplements = []
    for r in observations['records']:
        key = r['key']
        if key != key.lower() or key in reviewed or r['spelling'].lower() != key:
            raise ValueError('key mismatch or duplicate')
        if not r['url'].startswith('https://') or not r['sourceVersion'] or not r['locator']:
            raise ValueError('missing source provenance')
        if r['spellingSupported'] and r['spelling'] not in r['attestedForms']:
            raise ValueError('unsupported exact spelling')
        if key in old:
            if old[key]['state'] != 'needs-evidence':
                raise ValueError('unexpected replacement of prior confirmation/rejection')
            freq = old[key]['records'][0]['original']['wordfreqZipfPl']
        else:
            p = known_probes.get(key)
            if not p or p['inBase'] or p['inCandidateMaterial']:
                raise ValueError('new key lacks verified absence probe')
            freq = None
        state = ('deferred-retired-service' if r['kind']=='retired-service' else
                 'needs-exact-spelling' if not r['spellingSupported'] else
                 'source-supported-not-runtime-approved')
        row = dict(surfaceKey=key, baselineMembership='original-2913' if key in old else 'new-gap-intake',
            evidenceState=state, frozenZipf=freq, sourceObservation=r,
            frequencyAssessment='unmeasured' if freq is None else 'frozen-key-value-not-current-sense-frequency',
            runtimeMetadata=None, runtimeCost=None, runtimeApproved=False,
            remainingChecks=['source-schema-mapping', 'exact-case-and-homonym-policy',
                'current-usefulness-selection', 'metadata-cost-and-consumer-validation'])
        reviewed[key] = row; supplements.append(row)
    remaining = [r for r in decisions if r['state']=='needs-evidence' and r['surfaceKey'] not in reviewed]
    report = dict(candidateOnly=True, importable=False, baselineUniqueSingleKeys=2913,
        baselineConfirmedUnchanged=1336, baselineFrequencyRejectedUnchanged=911,
        observations=len(supplements), observationStates=dict(Counter(r['evidenceState'] for r in supplements)),
        reviewedOriginalKeys=sum(r['baselineMembership']=='original-2913' for r in supplements),
        newGapKeys=sum(r['baselineMembership']=='new-gap-intake' for r in supplements),
        originalKeysWithoutNewSourceReview=len(remaining),
        runtimeApprovedAdditions=0, additionalRuntimeCost=None,
        note='Source-supported is not runtime-ready; morphology lists are evidence, not automatic new candidate keys.')
    return supplements, remaining, report

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--decisions',type=Path,required=True)
    p.add_argument('--observations',type=Path,required=True)
    p.add_argument('--probes',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    raw=a.decisions.read_bytes(); obs=a.observations.read_bytes(); probes=a.probes.read_bytes()
    rows,remaining,report=reconcile([json.loads(x) for x in raw.splitlines()],json.loads(obs),json.loads(probes))
    report['inputSha256']={'decisions':digest(raw),'observations':digest(obs),'probes':digest(probes)}
    a.out.mkdir(parents=True,exist_ok=False)
    def write(name,value):
        (a.out/name).write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    write('evidence-report.json',report)
    write('source-assessments.json',rows)
    write('unreviewed-keys.json',[r['surfaceKey'] for r in remaining])
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
