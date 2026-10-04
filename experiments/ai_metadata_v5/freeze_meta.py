"""Run only before inference; never silently regenerate a frozen result's identity."""
import hashlib
from pathlib import Path
from contract_meta import ROOT,BASE,MODELS,VERSION,prepare,digest,canonical

def build():
    own=['NOTICE.txt','PROTOCOL.md','glossary.json','render_metadata.py','contract_meta.py',
         'run_metadata.py','collect_metadata.py','test_metadata.py','make_cases_meta.py',
         'freeze_meta.py','cases.json']
    dependencies=['../ai_compare_v5/'+p for p in ['contract.py','run_model.py','cases.json',
                                                'source-snapshot.json','requirements.txt','extract_sources.py']]
    return {'createdBeforeInference':True,'protocol':VERSION,'priorFreezeCommit':
            '00a7bf5999e8f6419a68c1884919e699c744a927',
            'files':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in own+dependencies},
            'workflowSha256':hashlib.sha256((ROOT.parents[1]/'.github/workflows/ai-metadata-v5.yml').read_bytes()).hexdigest(),
            'modelPresets':MODELS,'requestPayloadSha256':digest(prepare()[3])}

if __name__=='__main__':
    target=ROOT/'freeze-manifest.json'
    if target.exists():raise SystemExit('Existing freeze: create a new explicit trial instead of overwriting.')
    target.write_bytes(canonical(build())+b'\n')
