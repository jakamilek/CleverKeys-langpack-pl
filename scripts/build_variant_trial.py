#!/usr/bin/env python3
"""Compile frozen source evidence into an API-v1 trial pack; never change CKDT."""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import struct
import zipfile
from pathlib import Path

MAX_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_MEMBER_BYTES = 32 * 1024 * 1024
MAX_EVIDENCE_BYTES = 4 * 1024 * 1024
INTELLIGENCE_FILE = 'language-intelligence.json'
SOURCE_EXTENSION = 'source-category-surface-v1'


def canonical_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON field: ' + key)
        result[key] = value
    return result


def read_json(raw):
    return json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_object,
                      parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))


def _string(value, field):
    if not isinstance(value, str) or not value or len(value) > 512:
        raise ValueError('invalid ' + field)
    return value


def _strings(value, field):
    if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
        raise ValueError('invalid ' + field)
    if value != sorted(set(value)):
        raise ValueError('unordered or duplicate ' + field)
    return value


def dictionary_entries(raw):
    if len(raw) < 48 or raw[:4] != b'CKDT' or struct.unpack_from('<I', raw, 4)[0] != 2:
        raise ValueError('expected CKDT V2')
    count, offset = struct.unpack_from('<II', raw, 12)
    if count > 1_000_000 or offset < 48 or offset > len(raw):
        raise ValueError('invalid CKDT bounds')
    result = {}
    for _ in range(count):
        if offset + 2 > len(raw):
            raise ValueError('truncated CKDT length')
        length = struct.unpack_from('<H', raw, offset)[0]
        offset += 2
        if not length or offset + length + 1 > len(raw):
            raise ValueError('truncated CKDT record')
        surface = raw[offset:offset + length].decode('utf-8')
        offset += length + 1  # leave the original rank bytes untouched
        key = surface.lower()
        if key in result:
            raise ValueError('duplicate lowercase CKDT key: ' + key)
        result[key] = surface
    return result


def compile_intelligence(evidence, canonical):
    if type(evidence.get('schemaVersion')) is not int or evidence['schemaVersion'] != 1:
        raise ValueError('unsupported evidence version')
    if evidence.get('languageCode') != 'pl' or evidence.get('experimentExtension') != SOURCE_EXTENSION:
        raise ValueError('unsupported source evidence')
    provenance = evidence.get('provenance')
    if not isinstance(provenance, dict) or not provenance.get('morfeusz'):
        raise ValueError('missing source provenance')
    entries = evidence.get('entries')
    if not isinstance(entries, list) or not 1 <= len(entries) <= 1000:
        raise ValueError('invalid trial entry count')
    compiled, seen = [], set()
    for entry in entries:
        key = _string(entry.get('surfaceKey'), 'surfaceKey')
        if key != key.lower() or key in seen or key not in canonical:
            raise ValueError('duplicate, missing or non-lowercase surfaceKey: ' + key)
        seen.add(key)
        capitalization = entry['capitalization']
        variants = capitalization['variants']
        if not isinstance(variants, list) or not 1 <= len(variants) <= 2:
            raise ValueError('trial supports one or two source forms')
        surfaces = []
        associations = {}
        for variant in variants:
            surface = _string(variant.get('surface'), 'surface')
            policy = variant.get('casePolicy')
            if surface.lower() != key or surface in surfaces or policy not in {'lowercase', 'capitalized'}:
                raise ValueError('invalid source variant')
            if surface != (key if policy == 'lowercase' else key[:1].upper() + key[1:]):
                raise ValueError('surface contradicts casePolicy')
            surfaces.append(surface)
            associations[surface] = set(_strings(variant.get('categoryIds'), 'categoryIds'))
        default = capitalization['defaultSurface']
        if default not in surfaces or default != canonical[key]:
            raise ValueError('default differs from original CKDT canonical form')
        interpretations = entry['interpretations']
        raw_by_id = {}
        for interpretation in interpretations:
            payload = {field: interpretation[field] for field in ('lemma', 'tag', 'nameClasses', 'labels')}
            _string(payload['lemma'], 'lemma')
            _string(payload['tag'], 'tag')
            _strings(payload['nameClasses'], 'nameClasses')
            _strings(payload['labels'], 'labels')
            rid = sha256(canonical_bytes(payload))[:16]
            if interpretation['id'] != rid or rid in raw_by_id:
                raise ValueError('changed or duplicated source interpretation')
            raw_by_id[rid] = payload
        linked, expected = set(), {surface: set() for surface in surfaces}
        for proof in entry['generatedFormProofs']:
            rid = proof['interpretationId']
            if rid not in raw_by_id or proof['form'] not in expected:
                raise ValueError('dangling source form proof')
            origin = raw_by_id[rid]
            if (proof['lemma'] != origin['lemma'] or proof['nameClasses'] != origin['nameClasses']
                    or proof['tag'].split(':')[0] != origin['tag'].split(':')[0]):
                raise ValueError('form proof changes source interpretation')
            _strings(proof['labels'], 'proof labels')
            linked.add(rid)
            expected[proof['form']].update(['NAME:' + name for name in proof['nameClasses']]
                                           or ['POS:' + proof['tag'].split(':')[0]])
        if not raw_by_id or linked != set(raw_by_id) or any(not value for value in expected.values()):
            raise ValueError('missing interpretation or variant proof')
        categories = entry['categories']
        category_ids = set()
        for category in categories:
            field = category['sourceField']
            prefix = {'NAME': 'NAME:', 'TAG': 'POS:'}.get(field)
            if prefix is None or category['id'] != prefix + category['sourceValue']:
                raise ValueError('invalid source category')
            if category['id'] in category_ids:
                raise ValueError('duplicate source category')
            category_ids.add(category['id'])
        if associations != expected or set().union(*expected.values()) != category_ids:
            raise ValueError('source category/form association changed')
        # Runtime needs the two small surface fields. Keep full evidence in optional
        # metadata for audit and future context ranking, without inventing meanings.
        compiled.append({
            'surfaceKey': key, 'canonicalForm': canonical[key],
            'capitalization': {'defaultSurface': default, 'variants': [
                {'surface': surface, 'casePolicy': next(v['casePolicy'] for v in variants if v['surface'] == surface)}
                for surface in sorted(surfaces, key=lambda s: (s != default, s))]},
            'metadata': {'sourceEvidence': copy.deepcopy({
                field: entry[field] for field in ('categories', 'interpretations', 'generatedFormProofs', 'sourceRecords')})},
        })
    return {'schemaVersion': 1, 'languageCode': 'pl',
            'provenance': copy.deepcopy(provenance),
            'entries': sorted(compiled, key=lambda e: e['surfaceKey'])}


def build_trial(base_raw, evidence_raw, notice_raw, expected_evidence_sha256):
    if len(base_raw) > MAX_ARCHIVE_BYTES or len(evidence_raw) > MAX_EVIDENCE_BYTES:
        raise ValueError('trial input exceeds limit')
    if sha256(evidence_raw) != expected_evidence_sha256:
        raise ValueError('source evidence checksum mismatch')
    evidence = read_json(evidence_raw)
    artifact = evidence['provenance']['artifact']
    if sha256(base_raw) != artifact['packageSha256']:
        raise ValueError('base package differs from evidence snapshot')
    with zipfile.ZipFile(io.BytesIO(base_raw)) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)) or set(names) != {'dictionary.bin', 'manifest.json', 'unigrams.txt'}:
            raise ValueError('unexpected or duplicate base ZIP member')
        if any(info.file_size > MAX_MEMBER_BYTES for info in infos) or sum(i.file_size for i in infos) > MAX_ARCHIVE_BYTES:
            raise ValueError('decompressed base exceeds limit')
        members = {name: archive.read(name) for name in names}
    if sha256(members['dictionary.bin']) != artifact['dictionarySha256']:
        raise ValueError('dictionary differs from source evidence')
    canonical = dictionary_entries(members['dictionary.bin'])
    manifest = read_json(members['manifest.json'])
    if manifest.get('code') != 'pl' or manifest.get('wordCount') != len(canonical):
        raise ValueError('manifest differs from CKDT')
    if type(manifest.get('version')) is not int or not 1 <= manifest['version'] < 2_147_483_647:
        raise ValueError('invalid base pack version')
    if not notice_raw.strip() or len(notice_raw) > 64 * 1024:
        raise ValueError('missing or oversized attribution notice')
    notice_raw.decode('utf-8')
    intelligence = compile_intelligence(evidence, canonical)
    sidecar_raw = canonical_bytes(intelligence)
    manifest.update({
        'version': manifest['version'] + 1, 'apiVersion': 1,
        'capabilities': ['lexicon', 'frequency', 'capitalization', 'metadata'],
        'languageIntelligence': {'file': INTELLIGENCE_FILE, 'schemaVersion': 1, 'sha256': sha256(sidecar_raw)},
        'attribution': 'Original preview sources plus selected source casing evidence; see NOTICE.txt.',
    })
    members.update({'manifest.json': canonical_bytes(manifest), INTELLIGENCE_FILE: sidecar_raw,
                    'NOTICE.txt': notice_raw})
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, members[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    result = out.getvalue()
    dual = sum(len(e['capitalization']['variants']) == 2 for e in intelligence['entries'])
    report = {'trialOnly': True, 'basePackageSha256': sha256(base_raw),
              'sourceEvidenceSha256': sha256(evidence_raw), 'packageSha256': sha256(result),
              'dictionarySha256': sha256(members['dictionary.bin']),
              'unigramsSha256': sha256(members['unigrams.txt']),
              'languageIntelligenceSha256': sha256(sidecar_raw), 'wordCount': len(canonical),
              'metadataEntries': len(intelligence['entries']), 'dualVariantEntries': dual,
              'singleVariantEntries': len(intelligence['entries']) - dual,
              'sidecarBytes': len(sidecar_raw), 'zipMembers': sorted(members),
              'sourceSnapshot': copy.deepcopy(artifact),
              'limitations': ['Historical preview base, not a regenerated current-main dictionary.',
                              'Selected source evidence only; not full vocabulary coverage.',
                              'No Android integration or decoder/model accuracy measurement.']}
    return result, sidecar_raw, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-pack', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--evidence-sha256', required=True)
    parser.add_argument('--notice', type=Path, required=True)
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    for path, limit in [(args.base_pack, MAX_ARCHIVE_BYTES), (args.evidence, MAX_EVIDENCE_BYTES), (args.notice, 64 * 1024)]:
        if path.stat().st_size > limit:
            raise ValueError('input file exceeds limit: ' + str(path))
    result, sidecar, report = build_trial(args.base_pack.read_bytes(), args.evidence.read_bytes(),
                                         args.notice.read_bytes(), args.evidence_sha256)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / 'cleverkeys-pl-variants-trial.zip').write_bytes(result)
    (args.out_dir / INTELLIGENCE_FILE).write_bytes(sidecar)
    (args.out_dir / 'variant-trial-report.json').write_bytes(canonical_bytes(report))
    (args.out_dir / 'cleverkeys-pl-variants-trial.sha256').write_text(
        report['packageSha256'] + '  cleverkeys-pl-variants-trial.zip\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
