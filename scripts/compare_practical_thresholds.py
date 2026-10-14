#!/usr/bin/env python3
"""Compare frozen frequency thresholds without changing candidate decisions."""
import argparse
import hashlib
import json
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--decisions',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args()
raw=a.decisions.read_bytes()
all_rows=[json.loads(x) for x in raw.splitlines()]
rows=[x for x in all_rows if x['state']=='rejected-this-selection']
if len(rows)!=911 or len({x['surfaceKey'] for x in rows})!=911:
    raise ValueError('Expected exactly 911 unique rejected keys')
items=[]
for r in rows:
    records=r['records']
    freq={x['original']['wordfreqZipfPl'] for x in records}
    if len(freq)!=1:raise ValueError('Conflicting frequency')
    estimate=records[0]['original']['runtimeEstimate']
    if estimate is None:raise ValueError('Missing metadata estimate')
    items.append(dict(key=r['surfaceKey'],zipf=freq.pop(),estimate=estimate))
items.sort(key=lambda x:(-x['zipf'],x['key']))
report=dict(inputSha256=hashlib.sha256(raw).hexdigest(),baseVersion=11,
    scope='Only the 911 formerly frequency-rejected keys; no weights or decisions changed',
    knownConfirmedOutsideThisPool=1336,
    zeroScoreCount=sum(x['zipf']==0 for x in items),
    positiveBelowOne=sum(0<x['zipf']<1 for x in items),scenarios=[])
a.out.mkdir(parents=True,exist_ok=False)
for threshold in [2.0,1.8,1.5,1.2,1.0,0.5,0.0]:
    admitted=[x for x in items if x['zipf']>=threshold]
    remaining=[x for x in items if x['zipf']<threshold]
    report['scenarios'].append(dict(threshold=threshold,passes=len(admitted),fails=len(remaining),
        combinedWithPrevious1336=1336+len(admitted),remainingMetadataSlots=4365-len(admitted),
        sumStoredEntryBytes=sum(x['estimate']['bytes'] for x in admitted),
        sumStoredEntryNodes=sum(x['estimate']['nodes'] for x in admitted)))
    (a.out/f'threshold-{threshold:.1f}.json').write_text(json.dumps(dict(passes=admitted,fails=remaining),ensure_ascii=False,indent=2)+'\n')
report['caveats']=[
    'Frequency scores are frozen historical wordfreq values, not current measurements.',
    'Zero is the API default floor, not proof of nonexistence or uselessness.',
    'SGJP ordinary-form proof does not prove the technical/slang sense suggested by the source index.',
    'Metadata bytes/nodes sum existing proposals only; future provenance and packaging excluded.',
    'Threshold zero means bypassing the frequency filter for this pool, not attesting frequency.']
(a.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
