"""Coverage diagnosis only; install tokenizers==0.22.2, no Torch/Transformers.

python diagnose_tokenizer.py /path/to/original/tokenizer.json --out diagnosis.json
Original file: sdadas/polish-distilroberta at 849b664fa3134beae84095d28a184c145c6a3aa5.
This records the failed frozen v1, never changes its cases or evaluation gates.
"""
import argparse
import hashlib
import importlib.metadata
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'polish_mlm_compare_v1'))
from contract import prepare, digest, verify_freeze
from mlm import target_positions


def diagnose(path):
    from tokenizers import Tokenizer
    assert importlib.metadata.version('tokenizers') == '0.22.2'
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    assert sha == '108af881c403092a16ee515c2ad4a9a72122a3846cfd5c9f2bb860a3fd2bdafa', sha
    verify_freeze()
    tokenizer = Tokenizer.from_file(str(path))
    assert tokenizer.token_to_id('<unk>') == 3
    request = prepare()[2]
    failures = []
    for row in request['requests']:
        for surface in row['candidates']:
            text = row['context'] + ' ' + surface
            encoded = tokenizer.encode(text)
            positions = target_positions(text, len(row['context']) + 1, encoded.offsets)
            unknowns = [{'id': encoded.ids[i], 'token': encoded.tokens[i],
                         'offset': list(encoded.offsets[i]),
                         'text': text[slice(*encoded.offsets[i])]} for i in positions if encoded.ids[i] == 3]
            if unknowns:
                failures.append({'requestId': row['id'], 'surface': surface, 'unknowns': unknowns,
                                 'targetTokenIds': [encoded.ids[i] for i in positions]})
    probes = {}
    for surface in ['Łódź', 'łódź', 'Łotysz', 'Ł', 'Ą', 'Ć', 'Ę', 'Ń', 'Ó', 'Ś', 'Ź', 'Ż']:
        encoded = tokenizer.encode(surface)
        probes[surface] = {'ids': encoded.ids, 'tokens': encoded.tokens}
    return {'model': 'sdadas/polish-distilroberta',
            'revision': '849b664fa3134beae84095d28a184c145c6a3aa5', 'tokenizers': '0.22.2',
            'tokenizerSha256': sha, 'requestsSha256': digest(request),
            'requests': len(request['requests']),
            'candidateSpans': sum(len(row['candidates']) for row in request['requests']),
            'affectedRequests': len({row['requestId'] for row in failures}),
            'affectedSurfaces': sorted({row['surface'] for row in failures}),
            'failures': failures, 'standaloneProbes': probes,
            'method': 'Original tokenizer.json via tokenizers.Tokenizer; same target_positions as frozen v1; no model inference'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('tokenizer', type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    result = diagnose(args.tokenizer)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['requests', 'candidateSpans', 'affectedRequests', 'affectedSurfaces']}, ensure_ascii=False))
