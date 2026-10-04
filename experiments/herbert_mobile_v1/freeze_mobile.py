"""New conversion trial identity. Run once, before export or inference."""
import hashlib
from contract_mobile import ROOT, VERSION, MODEL, ORT_VERSION, canonical, prepare, previous

if __name__ == '__main__':
    target=ROOT/'freeze-manifest.json'
    if target.exists():
        raise SystemExit('Existing mobile freeze: create an explicit new version instead')
    own=['contract_mobile.py','export_validate.py','test_mobile.py','freeze_mobile.py',
         'requirements.txt','PROTOCOL.md','NOTICE.txt']
    deps=['../ai_metadata_v5/freeze-manifest.json',
          '../ai_metadata_v5_results/herbert/predictions.json']
    _,_,requests,_=prepare()
    frozen={'createdBeforeInference':True,'protocol':VERSION,'model':MODEL,
            'onnxRuntimeVersion':ORT_VERSION,'parentResultsCommit':'c4cf02a52c9c71fa1a8c3d7d6e66091f696bd07b',
            'files':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in own+deps},
            'workflowSha256':hashlib.sha256((ROOT.parents[1]/'.github/workflows/herbert-mobile-v1.yml').read_bytes()).hexdigest(),
            'requestPayloadSha256':previous.digest(requests)}
    target.write_bytes(canonical(frozen)+b'\n')
