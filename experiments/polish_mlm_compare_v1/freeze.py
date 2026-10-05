"""Run before upload/inference; test fixtures and every executable input are bound."""
import hashlib
import json
from pathlib import Path
from contract import ROOT, MODELS, digest, prepare


def freeze():
    repo = ROOT.parents[1]
    files = list(ROOT.glob('*.py')) + [ROOT / name for name in ['new-cases.json', 'PROTOCOL.md', 'requirements.txt', 'NOTICE.txt']]
    files += [ROOT.parent / 'ai_compare_v5' / name for name in ['contract.py', 'cases.json', 'source-snapshot.json']]
    files += [repo / '.github/workflows/polish-mlm-compare-v1.yml']
    manifest = {'protocol': 'polish-mlm-compare-v1', 'models': MODELS,
                'requestsSha256': digest(prepare()[2]),
                'files': {str(p.relative_to(repo)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}}
    (ROOT / 'freeze-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + '\n')


if __name__ == '__main__':
    freeze()
