"""Freeze new validation and selected policy before any holdout inference."""
import hashlib
import json
from contract import ROOT, MODELS, VERSION, digest, prepare


def freeze():
    repo = ROOT.parents[1]
    files = set(p for p in ROOT.iterdir() if p.is_file() and p.name != 'freeze-manifest.json')
    for name in ['polish_mlm_compare_v1','polish_mlm_fresh_v3']:
        manifest = ROOT.parent/name/'freeze-manifest.json'
        files.add(manifest)
        files.update(repo/p for p in json.loads(manifest.read_text())['files'])
    calibration = json.loads((ROOT/'calibration.json').read_text())
    files.update(repo/p for p in calibration['sourceFilesSha256'])
    files.add(repo/'.github/workflows/polish-mlm-safe-rank-v4.yml')
    manifest = {'protocol':VERSION,'models':MODELS,'requestsSha256':digest(prepare()[2]),
                'calibrationSha256':digest(calibration),'holdoutInferenceStarted':False,
                'developmentArchiveCommit':'b2c3342643a77ef01a04323034465acae8609c27',
                'files':{str(p.relative_to(repo)):hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in sorted(files)}}
    (ROOT/'freeze-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n')


if __name__=='__main__':freeze()
