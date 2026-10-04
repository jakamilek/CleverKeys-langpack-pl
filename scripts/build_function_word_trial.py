#!/usr/bin/env python3
"""Correct function-word casing in the pinned v3 trial, preserving CKDT indices.

Separate from build_variant_trial's immutable source-evidence compilation.
Only equal-byte-length canonical replacements are permitted; all ranks and
lookup sections, unigrams and the nine-entry casing sidecar stay byte-identical.
"""
from __future__ import annotations

import argparse
import io
import struct
import zipfile
from pathlib import Path

from build_variant_trial import (MAX_ARCHIVE_BYTES, MAX_MEMBER_BYTES,
                                canonical_bytes, dictionary_entries, read_json, sha256)
from capitalization_rules import resolve_capitalization

BASE_SHA256 = '4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7'
MORFEUSZ_VERSION = '1.99.15'
DICTIONARY_ID = 'pl.sgjp.sgjp-2026.06.01'
REASON = 'attested-function-word-default-lowercase'
PACK_NAME = 'cleverkeys-pl-function-words-trial.zip'


def correct_dictionary(raw, oracle):
    original = dictionary_entries(raw)  # validates unique folded keys and records
    count, start, normalized, accent = struct.unpack_from('<IIII', raw, 12)
    if not 48 <= start < normalized < accent <= len(raw):
        raise ValueError('invalid CKDT section bounds')
    output, changes, offset = bytearray(raw), [], start
    for _ in range(count):
        length = struct.unpack_from('<H', raw, offset)[0]
        offset += 2
        end = offset + length
        surface = raw[offset:end].decode('utf-8')
        key = surface.lower()
        if surface != key:
            decision = resolve_capitalization(key=key, morfeusz=oracle)
            if decision['reason'] == REASON:
                replacement = decision['surface'].encode('utf-8')
                if len(replacement) != length or decision['surface'].lower() != key:
                    raise ValueError('correction changes record length or lexical key')
                output[offset:end] = replacement
                changes.append({'key': key, 'before': surface, 'after': decision['surface'],
                                'rank': raw[end], 'decision': decision})
        offset = end + 1
    if offset != normalized:
        raise ValueError('canonical section does not match header')
    result = bytes(output)
    if result[:start] != raw[:start] or result[normalized:] != raw[normalized:]:
        raise ValueError('header or lookup sections changed')
    if dictionary_entries(result).keys() != original.keys():
        raise ValueError('lexical membership changed')
    return result, changes


def build_corrected_trial(base_raw, oracle, provenance, expected_sha256=BASE_SHA256):
    if len(base_raw) > MAX_ARCHIVE_BYTES or sha256(base_raw) != expected_sha256:
        raise ValueError('trial input size or checksum mismatch')
    with zipfile.ZipFile(io.BytesIO(base_raw)) as archive:
        infos = archive.infolist()
        names = [item.filename for item in infos]
        if len(names) != len(set(names)) or set(names) != {
                'dictionary.bin', 'manifest.json', 'unigrams.txt',
                'language-intelligence.json', 'NOTICE.txt'}:
            raise ValueError('unexpected or duplicate trial member')
        if any(i.file_size > MAX_MEMBER_BYTES for i in infos) or sum(i.file_size for i in infos) > MAX_ARCHIVE_BYTES:
            raise ValueError('decompressed trial exceeds limit')
        members = {name: archive.read(name) for name in names}
    manifest = read_json(members['manifest.json'])
    original = dictionary_entries(members['dictionary.bin'])
    sidecar = read_json(members['language-intelligence.json'])
    if (manifest.get('code') != 'pl' or manifest.get('apiVersion') != 1
            or manifest.get('version') != 3 or manifest.get('wordCount') != len(original)
            or manifest.get('languageIntelligence', {}).get('sha256') != sha256(members['language-intelligence.json'])):
        raise ValueError('invalid v3 trial manifest or sidecar checksum')
    corrected, changes = correct_dictionary(members['dictionary.bin'], oracle)
    updated = dictionary_entries(corrected)
    # Frozen provenance describes the historical evidence snapshot, not the
    # corrected CKDT hash. Its represented entries must still match the pack.
    for entry in sidecar['entries']:
        key = entry['surfaceKey']
        if (entry['canonicalForm'] != updated[key]
                or entry['capitalization']['defaultSurface'] != updated[key]):
            raise ValueError('correction conflicts with frozen casing evidence')
    if not changes:
        raise ValueError('no function-word corrections')
    manifest['version'] = 4  # language-pack version; application version unchanged
    manifest['attribution'] = (manifest.get('attribution', '') +
                               ' Function-word default casing corrected from Morfeusz/SGJP.')
    notice = (b'\nFunction-word casing correction, 2026-10-04: the original dictionary\n'
              b'snapshot is modified only in source-attested function-word canonical case.\n'
              b'The nine-entry casing evidence remains the original historical snapshot.\n')
    members['NOTICE.txt'] += notice
    original_dictionary_hash = sha256(members['dictionary.bin'])
    members['dictionary.bin'] = corrected
    members['manifest.json'] = canonical_bytes(manifest)
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, members[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    result = out.getvalue()
    report = {
        'trialOnly': True, 'inputPackageSha256': sha256(base_raw),
        'inputDictionarySha256': original_dictionary_hash,
        'packageSha256': sha256(result), 'dictionarySha256': sha256(corrected),
        'unigramsSha256': sha256(members['unigrams.txt']),
        'languageIntelligenceSha256': sha256(members['language-intelligence.json']),
        'wordCount': len(updated), 'packVersion': 4, 'correctionCount': len(changes),
        'changes': changes, 'oracle': provenance,
        'preserved': ['lexical keys and order', 'frequency rank bytes', 'CKDT header',
                      'normalized and accent lookup sections', 'unigrams bytes',
                      'nine-entry casing sidecar bytes'],
        'limitations': ['Frozen preview corrected narrowly; not a full source rebuild.',
                        'Name readings of corrected function words need Shift or user case.',
                        'No device acceptance or context-model evaluation.'],
    }
    return result, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-pack', type=Path, required=True)
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    import morfeusz2
    oracle = morfeusz2.Morfeusz(case_handling=morfeusz2.CONDITIONALLY_CASE_SENSITIVE)
    if str(morfeusz2.__version__) != MORFEUSZ_VERSION or oracle.dict_id() != DICTIONARY_ID:
        raise ValueError('Morfeusz/SGJP snapshot differs from reviewed source')
    provenance = {'program': 'Morfeusz 2 / SGJP', 'version': MORFEUSZ_VERSION,
                  'dictionaryId': DICTIONARY_ID, 'caseHandling': 'CONDITIONALLY_CASE_SENSITIVE',
                  'documentation': 'https://morfeusz.sgjp.pl/doc/about/',
                  'resolverSha256': sha256(Path(__file__).with_name('capitalization_rules.py').read_bytes())}
    if args.base_pack.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError('trial input exceeds size limit')
    result, report = build_corrected_trial(args.base_pack.read_bytes(), oracle, provenance)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / PACK_NAME).write_bytes(result)
    (args.out_dir / 'function-word-trial-report.json').write_bytes(canonical_bytes(report))
    (args.out_dir / 'cleverkeys-pl-function-words-trial.sha256').write_text(
        report['packageSha256'] + '  ' + PACK_NAME + '\n', encoding='utf-8')
    print(f"Corrected {report['correctionCount']} forms; {report['wordCount']} lexical keys retained.")
    print(report['packageSha256'])


if __name__ == '__main__':
    main()
