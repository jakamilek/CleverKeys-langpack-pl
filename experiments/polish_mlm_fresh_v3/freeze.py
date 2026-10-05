"""Freeze all local dependencies, data and executable identity before inference."""
import hashlib
import json
from contract import ROOT, MODELS, VERSION, digest, prepare


def freeze():
    repo=ROOT.parents[1]
    files=list(ROOT.glob('*.py'))+[ROOT/n for n in ['PROTOCOL.md','NOTICE.txt','requirements.txt','cases.json','source-snapshot.json','local-tokenizer-preflight.json']]
    for directory,patterns in [('ai_compare_v5',['contract.py','cases.json','source-snapshot.json','local-tokenizer-preflight.json']),
                               ('polish_mlm_compare_v1',['*.py','*.json','*.md','*.txt']),
                               ('polish_mlm_compare_v2',['*.py','*.json','*.md','*.txt']),
                               ('polish_mlm_screen_v2/results',['BartekK--distilHerBERT-base-cased.json'])]:
        for pattern in patterns:files.extend((ROOT.parent/directory).glob(pattern))
    # v2 freeze also binds its historical reference and screening dependencies.
    frozen_v2=json.loads((ROOT.parent/'polish_mlm_compare_v2/freeze-manifest.json').read_text())
    files.extend(repo/p for p in frozen_v2['files'])
    files.append(repo/'.github/workflows/polish-mlm-fresh-v3.yml')
    manifest={'protocol':VERSION,'models':MODELS,'requestsSha256':digest(prepare()[2]),
              'files':{str(p.relative_to(repo)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}}
    (ROOT/'freeze-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n')


if __name__=='__main__':freeze()
