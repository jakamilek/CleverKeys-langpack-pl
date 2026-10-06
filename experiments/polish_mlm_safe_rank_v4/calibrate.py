"""Select a single global threshold exclusively from archived v3 development data."""
import hashlib
import json
from pathlib import Path
from policy import calibrate

ROOT = Path(__file__).parent
ARCHIVE = ROOT.parent / 'polish_mlm_fresh_v3_loading_fix_v1_results'


def calculate():
    result = json.loads((ARCHIVE/'distilherbert/predictions.json').read_text())
    report = json.loads((ARCHIVE/'distilherbert/report.json').read_text())
    if (result['codeCommit'] != '83fa31fd6071ba48b8e7828c58bb28ff2d49f2f1'
            or result['requestsSha256'] != 'a20cad29b09554a9718f1d520d68c4e695c9274aac0b708801463f498097f53d'):
        raise ValueError('wrong development identity')
    decisions = {r['id']: r for r in report['decisions']}
    if len(decisions) != 256 or len(result['predictions']) != 256:
        raise ValueError('incomplete development evidence')
    rows = [{**decisions[p['id']], 'scores': p['scores']} for p in result['predictions']]
    out = calibrate(rows)
    out['sourceCodeCommit'] = result['codeCommit']
    out['sourceRequestsSha256'] = result['requestsSha256']
    out['sourceFilesSha256'] = {str(p.relative_to(ROOT.parents[1])): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in [ARCHIVE/'distilherbert/predictions.json', ARCHIVE/'distilherbert/report.json']}
    return out


def build():
    out = calculate()
    (ROOT/'calibration.json').write_text(json.dumps(out, ensure_ascii=False, sort_keys=True, indent=2)+'\n')
    print(json.dumps(out, ensure_ascii=False))
    return out


if __name__ == '__main__':
    build()
