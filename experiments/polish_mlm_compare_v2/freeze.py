"""Bind new code/screening and unchanged historic inputs before new inference."""
import hashlib
import json
from contract import ROOT, MODELS, VERSION, digest, prepare, reference


def freeze():
    repo = ROOT.parents[1]
    files = list(ROOT.glob('*.py')) + [ROOT/name for name in ['PROTOCOL.md', 'requirements.txt', 'NOTICE.txt']]
    for directory, patterns in [
            ('ai_compare_v5', ['contract.py', 'cases.json', 'source-snapshot.json']),
            ('polish_mlm_compare_v1', ['*.py', '*.json', '*.md', '*.txt']),
            ('polish_mlm_compare_v1_results/herbert', ['*.json', '*.txt']),
            ('polish_mlm_screen_v2', ['*.py', '*.md']),
            ('polish_mlm_screen_v2/results', ['*.json'])]:
        for pattern in patterns:
            files.extend((ROOT.parent/directory).glob(pattern))
    files += [repo/'.github/workflows/polish-mlm-compare-v2.yml']
    reference()
    manifest = {'protocol': VERSION, 'models': MODELS, 'requestsSha256': digest(prepare()[2]),
                'files': {str(p.relative_to(repo)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}}
    (ROOT/'freeze-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n')


if __name__ == '__main__':
    freeze()
