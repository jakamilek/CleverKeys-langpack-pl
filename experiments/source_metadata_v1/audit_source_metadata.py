#!/usr/bin/env python3
"""Report source-backed metadata without inventing per-word meanings.

Use the pinned Morfeusz build and a downloaded, SHA-verified preview artifact.
This does not generate a production sidecar or change any dictionary key.
"""
import argparse
import collections
import csv
import hashlib
import importlib.metadata
import json
import struct
from pathlib import Path
import zipfile

import morfeusz2

ARTIFACT_SHA = '827a20f8489fad51023e1c0d58319dca030d304f7e213ef4973141251c3ad9ff'
KEYS = ['łódź', 'łodzi', 'łódzki', 'malina', 'jagoda', 'róża', 'polska', 'warszawska', 'warszawski']


def sha(data):
    return hashlib.sha256(data).hexdigest()


def analyses(m, surface):
    out = []
    for start, end, payload in m.analyse(surface):
        orth, lemma, tag, names, labels = payload
        # Report complete single-token interpretations; exclude unknowns and
        # partial segmentation rather than asserting coverage for a component.
        if start != 0 or end != 1 or orth != surface or tag == 'ign':
            continue
        out.append({'orth': orth, 'lemma': lemma, 'tag': tag,
                    'nameClasses': sorted(names), 'labels': sorted(labels)})
    return sorted(out, key=lambda x: json.dumps(x, ensure_ascii=False, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--artifact', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    archive = args.artifact.read_bytes()
    assert sha(archive) == ARTIFACT_SHA, 'unexpected source artifact bytes'
    assert importlib.metadata.version('morfeusz2') == '1.99.15'
    m = morfeusz2.Morfeusz(case_handling=morfeusz2.CONDITIONALLY_CASE_SENSITIVE)
    assert m._morfeusz_obj.getDictID() == 'pl.sgjp.sgjp-2026.06.01'
    source_rows = {}
    file_hashes = {}
    with zipfile.ZipFile(args.artifact) as z:
        wordbytes = z.read('build/pl_words_preview.txt')
        words = [w.strip() for w in wordbytes.decode().splitlines()
                 if w.strip() and not w.startswith('#')]
        packagebytes = z.read('build/cleverkeys-langpack-pl-preview.zip')
        import io
        with zipfile.ZipFile(io.BytesIO(packagebytes)) as package:
            package_members = sorted(package.namelist())
            manifest = json.loads(package.read('manifest.json'))
            binary = package.read('dictionary.bin')
            dictionary_sha = sha(binary)
            assert binary[:4] == b'CKDT' and struct.unpack_from('<I', binary, 4)[0] == 2
            binary_count = struct.unpack_from('<I', binary, 12)[0]
            cursor = 48
            binary_words = []
            for _ in range(binary_count):
                length = struct.unpack_from('<H', binary, cursor)[0]
                cursor += 2
                binary_words.append(binary[cursor:cursor + length].decode('utf-8'))
                cursor += length + 1
            assert len(binary_words) == manifest['wordCount']
            assert set(binary_words) == set(words), 'wordlist differs from CKDT surfaces'
        for filename, column in [('pl-city-source.tsv', 'name'),
                                 ('pl-city-inflections.tsv', 'form'),
                                 ('pl-first-name-inflections.tsv', 'form')]:
            raw = z.read('build/' + filename)
            file_hashes[filename] = sha(raw)
            rows = list(csv.DictReader(raw.decode().splitlines(), delimiter='\t'))
            source_rows[filename] = [r for r in rows if r[column].lower() in KEYS]
    assert len(words) == manifest['wordCount'] == 106363
    assert len({w.lower() for w in words}) == len(words)
    counts = collections.Counter()
    names_count = collections.Counter()
    pos_count = collections.Counter()
    case_only = []
    examples = []
    for surface in words:
        key = surface.lower()
        probes = {p: analyses(m, p) for p in dict.fromkeys([key, key[:1].upper() + key[1:]])}
        allrows = [r for rows in probes.values() for r in rows]
        names = {n for r in allrows for n in r['nameClasses']}
        pos = {r['tag'].split(':', 1)[0] for r in allrows}
        counts['keys'] += 1
        counts['recognized_any_probe' if allrows else 'unrecognized_complete_token'] += 1
        counts['recognized_lower_probe'] += bool(probes[key])
        counts['name_class_present'] += bool(names)
        counts['labels_present'] += any(r['labels'] for r in allrows)
        counts['multiple_lemmas'] += len({r['lemma'] for r in allrows}) > 1
        counts['multiple_pos'] += len(pos) > 1
        counts['common_name_class_present'] += 'nazwa_pospolita' in names
        counts['common_and_other_name_class'] += 'nazwa_pospolita' in names and bool(names - {'nazwa_pospolita'})
        for name in names:
            names_count[name] += 1
        for p in pos:
            pos_count[p] += 1
        if allrows and not probes[key]:
            case_only.append(key)
        if key in KEYS:
            examples.append({'surfaceKey': key, 'packCanonicalSurface': surface,
                             'probes': probes,
                             'sourceRecords': {f: [r for r in rows
                                                  if r.get('form', r.get('name', '')).lower() == key]
                                               for f, rows in source_rows.items()}})
    assert {e['surfaceKey'] for e in examples} == set(KEYS)
    result = {
        'auditVersion': 'source-metadata-v1',
        'artifact': {'runId': 36916501466, 'artifactId': 11189614575,
                     'sourceCommit': 'a1fa0193fc504e5fe81d9d43c23fd9a1e52ad307',
                     'sha256': sha(archive), 'wordlistSha256': sha(wordbytes),
                     'dictionarySha256': dictionary_sha, 'packageSha256': sha(packagebytes),
                     'binarySurfaceSetVerified': True,
                     'packageMembers': package_members, 'manifest': manifest,
                     'sourceFileHashes': file_hashes},
        'morfeusz': {'version': importlib.metadata.version('morfeusz2'),
                     'dictionaryId': m._morfeusz_obj.getDictID(),
                     'tagsetId': m._morfeusz_obj.getIdResolver().getTagsetId(),
                     'caseHandling': 'CONDITIONALLY_CASE_SENSITIVE',
                     'fields': ['orth', 'lemma', 'tag', 'nameClasses', 'labels']},
        'coverage': dict(sorted(counts.items())),
        'nameClassKeyCounts': dict(sorted(names_count.items())),
        'posKeyCounts': dict(sorted(pos_count.items())),
        'recognizedOnlyWithCapitalizedProbe': {'count': len(case_only), 'examples': case_only[:20]},
        'selectedExamples': sorted(examples, key=lambda e: KEYS.index(e['surfaceKey'])),
        'limitations': ['Historical successful preview artifact, not a regenerated current build.',
                        'Coverage is morphological recognition, not semantic accuracy.',
                        'No per-word semantic glosses, street classifications or absent surnames invented.',
                        'No production sidecar, candidate ranking, model inference or Android changes.'],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result['coverage'], sort_keys=True))


if __name__ == '__main__':
    main()
