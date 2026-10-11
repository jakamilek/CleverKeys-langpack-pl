#!/usr/bin/env python3
"""Repackage accepted v8 losslessly as shared metadata schema/API-v2 trial v9."""
import argparse
import io
import json
from pathlib import Path
import zipfile

from shared_metadata_v2 import canonical, nodes, share_lemmas, share_attributes, expand, PACK_SHA, SIDE_SHA
from build_variant_trial import sha256, read_json
from build_thematic_forms_trial import write_pack

PACK_NAME = 'cleverkeys-pl-shared-metadata-trial.zip'


def serialize(document):
    # Tables precede entries so the actual bounded reader never buffers unresolved words.
    order = ['schemaVersion', 'languageCode', 'sourceAttributes', 'sourceLexemes', 'provenance', 'entries']
    assert set(document) == set(order)
    return b'{' + b','.join(json.dumps(k).encode() + b':' + canonical(document[k]).rstrip(b'\n')
                           for k in order) + b'}\n'


def build(raw, out, expected_pack=PACK_SHA, expected_side=SIDE_SHA):
    if len(raw) > 64*1024*1024 or sha256(raw) != expected_pack: raise ValueError('base checksum/size')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names = z.namelist()
        if len(names) != 5 or set(names) != {'dictionary.bin', 'manifest.json', 'language-intelligence.json',
                'unigrams.txt', 'NOTICE.txt'}: raise ValueError('base members')
        if max(i.file_size for i in z.infolist()) > 32*1024*1024 or sum(i.file_size for i in z.infolist()) > 64*1024*1024:
            raise ValueError('base decompression budget')
        members = {name: z.read(name) for name in names}
    original_bytes = members['language-intelligence.json']
    manifest = read_json(members['manifest.json']); original = read_json(original_bytes)
    if (sha256(original_bytes) != expected_side or manifest.get('version') != 8 or manifest.get('apiVersion') != 1
            or manifest.get('code') != 'pl' or original.get('schemaVersion') != 1 or original.get('languageCode') != 'pl'
            or manifest.get('languageIntelligence', {}).get('sha256') != expected_side
            or manifest.get('languageIntelligence', {}).get('schemaVersion') != 1): raise ValueError('base identity')
    if canonical(original) != original_bytes: raise ValueError('base canonical JSON')
    document, stats = share_lemmas(original, True)
    stats.update(share_attributes(document))
    encoded = serialize(document)
    restored = canonical(expand(json.loads(encoded)))
    if restored != original_bytes: raise ValueError('lossless reconstruction failed')
    node_count = nodes(document)
    if len(encoded) > 32*1024*1024 or node_count > 2_000_000 or len(document['entries']) > 120_000:
        raise ValueError('runtime budget')
    manifest.update(version=9, apiVersion=2)
    manifest['languageIntelligence'].update(schemaVersion=2, sha256=sha256(encoded))
    members['manifest.json'] = canonical(manifest)
    members['language-intelligence.json'] = encoded
    members['NOTICE.txt'] += (b'\nShared source metadata representation trial v9. Requires API/schema-v2 compatible APK.\n'
        b'All v8 words, ranks, source evidence and capitalization are unchanged.\n'
        b'Only exact profitable source records/attributes are shared. No new lexical data or model.\n')
    package = write_pack(members)
    report = dict(trialOnly=True, representationOnly=True, version=9, apiVersion=2, schemaVersion=2,
        inputPackSha256=sha256(raw), originalMetadataSha256=sha256(original_bytes),
        reconstructedMetadataSha256=sha256(restored), byteExactReconstruction=True,
        wordCount=manifest['wordCount'], metadataEntries=len(document['entries']), added=0, removed=0,
        changedRanks=0, changedCaseVariants=0, changedSourceEvidence=0,
        originalMetadataBytes=len(original_bytes), metadataBytes=len(encoded),
        originalNodes=nodes(original), metadataNodes=node_count, remainingNodes=2_000_000-node_count,
        packageSha256=sha256(package), dictionarySha256=sha256(members['dictionary.bin']),
        unigramsSha256=sha256(members['unigrams.txt']), languageIntelligenceSha256=sha256(encoded), **stats)
    out.mkdir(parents=True, exist_ok=True)
    if (out/PACK_NAME).exists(): raise ValueError('output already contains installable pack')
    (out/'shared-metadata-report.json').write_bytes(canonical(report))
    (out/PACK_NAME).write_bytes(package)
    (out/'cleverkeys-pl-shared-metadata-trial.sha256').write_text(sha256(package)+'  '+PACK_NAME+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-pack', type=Path, required=True)
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.base_pack.read_bytes(), args.out_dir), ensure_ascii=False, indent=2))
