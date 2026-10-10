"""Reproduce exact benchmark metadata from the already verified Polish pack."""
import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PACK_SHA = 'aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb'
SIDECAR_SHA = '5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d'
DICTIONARY_SHA = 'a32f6a55bce7375e744d3d261d6ec9aad96dc64725ac429d4cb1d7225aed3c2a'
SOURCE_COMMIT = '041b28ae4587c531ef73e62933e9151cadb84c33'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode() + b'\n'


def extract(pack, keys):
    raw = Path(pack).read_bytes()
    require(len(raw) == 1713402 and hashlib.sha256(raw).hexdigest() == PACK_SHA, 'exact package identity')
    with zipfile.ZipFile(pack) as archive:
        info = archive.infolist()
        require(len(info) == 5 and {i.filename for i in info} ==
                {'NOTICE.txt', 'dictionary.bin', 'language-intelligence.json', 'manifest.json', 'unigrams.txt'} and
                sum(i.file_size for i in info) < 16000000, 'bounded package members')
        sidecar, dictionary = archive.read('language-intelligence.json'), archive.read('dictionary.bin')
    require(hashlib.sha256(sidecar).hexdigest() == SIDECAR_SHA and
            hashlib.sha256(dictionary).hexdigest() == DICTIONARY_SHA, 'sidecar/dictionary identity')
    magic, version, language, count, start, end, _ = struct.unpack_from('<4sI4sIIII', dictionary)
    require(magic == b'CKDT' and version == 2 and language == b'pl\0\0' and count == 106363, 'CKDT header')
    found, pos = {}, start
    for _ in range(count):
        size, = struct.unpack_from('<H', dictionary, pos)
        pos += 2
        word = dictionary[pos:pos + size].decode('utf-8')
        pos += size
        rank = dictionary[pos]
        pos += 1
        require(word.lower() not in found, 'duplicate CKDT key')
        found[word.lower()] = dict(surface=word, rank=rank)
    require(pos == end, 'CKDT canonical boundary')
    intelligence = json.loads(sidecar)
    supplied = {e['surfaceKey']: e for e in intelligence['entries']}
    require(len(supplied) == len(intelligence['entries']) == 16199 and
            len(set(keys)) == len(keys) and set(keys) <= set(supplied) & set(found), 'source keys')
    return dict(schemaVersion=1, languageCode='pl', packSha256=PACK_SHA,
                sidecarSha256=SIDECAR_SHA, dictionarySha256=DICTIONARY_SHA,
                producerCommit=SOURCE_COMMIT, provenance=intelligence['provenance'],
                dictionaryProof={k: found[k] for k in sorted(keys)},
                entries=[supplied[k] for k in sorted(keys)])


def needed_keys():
    old = json.loads((ROOT.parent / 'herbert_form_diagnostic_v1/source-fixture.json').read_text())
    new = json.loads((ROOT / 'new-forms.json').read_text())
    return sorted({e['surfaceKey'] for e in old['entries']} |
                  {s.lower() for c in new['cases'] for s in c['surfaces']})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack', type=Path, required=True)
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    data = canonical(extract(args.pack, needed_keys()))
    path = ROOT / 'source-fixture.json'
    if args.verify:
        require(path.read_bytes() == data, 'exact extracted fixture differs')
    else:
        path.write_bytes(data)
    print('Source pack/binary keys/full metadata extraction PASS; ' + str(len(data)) + ' bytes')
