"""Original AutoTokenizer preflight, no Torch/model weights, pinned full v5 pack.

USE_TORCH=0 USE_TF=0 python screen_tokenizers.py --metadata /path --pack /path --out /path
Dependencies: transformers4.57.6/tokenizers0.22.2; record installed environment.
Old v1 scoring cases and gates remain immutable. This screen does not prove MLM quality.
"""
import argparse
import hashlib
import importlib.metadata
import json
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'polish_mlm_compare_v1'))
from contract import prepare, digest, verify_freeze
from mlm import encode

MODELS = {
    'Geotrend/distilbert-base-pl-cased': '9002d311e35aac14575bf53ad4fa3d8f8b853c2b',
    'BartekK/distilHerBERT-base-cased': '7276461b7a8fd668aaf30313c03a68bd11aad642',
    'Geotrend/bert-base-pl-cased': '5c87e45fdc3ce85e1dc718daddc39c9e3d3dbf40',
}
PACK_SHA = 'aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb'
SIDECAR_SHA = '5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d'
DICTIONARY_SHA = 'a32f6a55bce7375e744d3d261d6ec9aad96dc64725ac429d4cb1d7225aed3c2a'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_source(pack):
    if sha(pack.read_bytes()) != PACK_SHA:
        raise ValueError('wrong pack')
    with zipfile.ZipFile(pack) as z:
        binary = z.read('dictionary.bin')
        sidecar = z.read('language-intelligence.json')
    if sha(binary) != DICTIONARY_SHA or sha(sidecar) != SIDECAR_SHA:
        raise ValueError('wrong source members')
    if binary[:4] != b'CKDT' or struct.unpack_from('<I', binary, 4)[0] != 2:
        raise ValueError('wrong CKDT version')
    count, start, normalized = struct.unpack_from('<III', binary, 12)
    pos, dictionary = start, {}
    for _ in range(count):
        if pos + 2 > normalized:
            raise ValueError('truncated length')
        size = struct.unpack_from('<H', binary, pos)[0]
        pos += 2
        if not size or pos + size + 1 > normalized:
            raise ValueError('truncated word')
        surface = binary[pos:pos+size].decode('utf-8')
        pos += size + 1  # immutable rank byte
        key = surface.lower()
        if key in dictionary:
            raise ValueError('duplicate key')
        dictionary[key] = surface
    if pos != normalized or count != 106363:
        raise ValueError('wrong dictionary size/boundary')
    entries = json.loads(sidecar)['entries']
    if len(entries) != 16199:
        raise ValueError('wrong sidecar count')
    variants, pairs = set(dictionary.values()), []
    for entry in entries:
        key = entry['surfaceKey']
        forms = [v['surface'] for v in entry['capitalization']['variants']]
        if key not in dictionary or entry['capitalization']['defaultSurface'] != dictionary[key]:
            raise ValueError('sidecar differs from CKDT')
        if not forms or any(s.lower() != key for s in forms) or len(forms) != len(set(forms)):
            raise ValueError('invalid source variants')
        variants.update(forms)
        if len(forms) > 1:
            pairs.append((key, forms))
    return dictionary, sorted(variants), pairs


def screen(model, revision, metadata_root, source, request):
    from transformers import AutoTokenizer
    path = metadata_root / model.replace('/', '--')
    metadata = json.loads((path / 'metadata.json').read_text())
    if metadata['id'] != model or metadata['revision'] != revision or metadata.get('errors'):
        raise ValueError('incomplete original model metadata: ' + model)
    for item in metadata['downloaded']:
        raw = (path / item['path']).read_bytes()
        if len(raw) != item['bytes'] or sha(raw) != item['sha256']:
            raise ValueError('changed metadata ' + item['path'])
    tokenizer = AutoTokenizer.from_pretrained(str(path), use_fast=True,
                                            trust_remote_code=False, local_files_only=True)
    if not tokenizer.is_fast or any(getattr(tokenizer, a) is None for a in
                                    ['unk_token_id', 'pad_token_id', 'mask_token_id']):
        raise ValueError('required original fast tokenizer unavailable')
    dictionary, surfaces, pairs = source
    ids_by_surface, unknowns, empty = {}, [], []
    for start in range(0, len(surfaces), 1000):
        batch = surfaces[start:start+1000]
        ids = tokenizer(batch, add_special_tokens=False, truncation=False)['input_ids']
        for surface, token_ids in zip(batch, ids):
            ids_by_surface[surface] = tuple(token_ids)
            if tokenizer.unk_token_id in token_ids:
                unknowns.append({'surface': surface, 'ids': token_ids})
            if not token_ids:
                empty.append(surface)
    collapsed = [{'key': key, 'forms': forms} for key, forms in pairs
                 if len({ids_by_surface[s] for s in forms}) != len(forms)]
    pair_unknowns = [{'key': key, 'forms': forms} for key, forms in pairs
                     if any(tokenizer.unk_token_id in ids_by_surface[s] for s in forms)]
    failures, max_tokens, context_unknown_requests = [], 0, set()
    for row in request['requests']:
        for surface in row['candidates']:
            try:
                encoded = encode(row['context'], surface, tokenizer)
                max_tokens = max(max_tokens, len(encoded['ids']))
                if tokenizer.unk_token_id in encoded['ids']:
                    context_unknown_requests.add(row['id'])
            except ValueError as exc:
                failures.append({'id': row['id'], 'surface': surface, 'reason': str(exc)})
    probes = {}
    for surface in ['Łódź', 'łódź', 'Łodzi', 'łodzi', 'Malina', 'malina', 'Warszawska',
                    'warszawska', 'Ale', 'ale', 'Lub', 'lub', 'Tutaj', 'tutaj'] + list('ąćęłńóśźżĄĆĘŁŃÓŚŹŻ'):
        ids = tokenizer.encode(surface, add_special_tokens=False)
        probes[surface] = {'ids': ids, 'tokens': tokenizer.convert_ids_to_tokens(ids),
                           'unknown': tokenizer.unk_token_id in ids}
    backend = tokenizer.backend_tokenizer.to_str().encode()
    return {'id': model, 'revision': revision, 'metadata': metadata,
            'originalConfig': json.loads((path / 'config.json').read_text()),
            'tokenizerClass': type(tokenizer).__name__, 'backendSha256': sha(backend),
            'tokenizerConfig': json.loads(backend), 'dictionaryKeys': len(dictionary),
            'sourceSurfaces': len(surfaces), 'multiVariantKeys': len(pairs),
            'unknownSourceSurfaces': unknowns, 'emptySourceSurfaces': empty,
            'collapsedSourcePairs': collapsed, 'unknownSourcePairs': pair_unknowns,
            'requests': len(request['requests']), 'candidateSpans': sum(len(r['candidates']) for r in request['requests']),
            'requestFailures': failures, 'maxInputTokens': max_tokens,
            'unknownContextRequests': len(context_unknown_requests), 'probes': probes,
            'frozenRequestGatePass': not failures and not collapsed,
            'fullSourceCoveragePass': not unknowns and not empty and not collapsed,
            'weightsLoaded': False, 'qualityMeasured': False, 'phoneMeasured': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--metadata', required=True, type=Path)
    parser.add_argument('--pack', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    verify_freeze()
    source, request = load_source(args.pack), prepare()[2]
    args.out.mkdir(parents=True, exist_ok=True)
    environment = {name: importlib.metadata.version(name) for name in
                   ['transformers', 'tokenizers', 'huggingface-hub', 'numpy', 'regex', 'safetensors']}
    for model, revision in MODELS.items():
        result = screen(model, revision, args.metadata, source, request)
        result.update({'environment': environment, 'packSha256': PACK_SHA,
                       'sidecarSha256': SIDECAR_SHA, 'dictionarySha256': DICTIONARY_SHA,
                       'requestsSha256': digest(request)})
        # Backend vocab is recoverable from pinned source; keep the result compact.
        backend = result.pop('tokenizerConfig')
        result['tokenizerPipeline'] = {k: backend[k] for k in ['normalizer', 'pre_tokenizer', 'post_processor', 'decoder']}
        target = args.out / (model.replace('/', '--') + '.json')
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'model': model, 'requestGate': result['frozenRequestGatePass'],
                          'fullCoverage': result['fullSourceCoveragePass'], 'surfaces': result['sourceSurfaces'],
                          'unknownSurfaces': len(result['unknownSourceSurfaces']),
                          'collapsedPairs': len(result['collapsedSourcePairs']),
                          'requestFailures': len(result['requestFailures'])}, ensure_ascii=False), flush=True)
