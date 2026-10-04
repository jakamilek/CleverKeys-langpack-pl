#!/usr/bin/env python3
"""Audit every CKDT key and export source-attested case homonyms (pack v5).

No word/category allowlist. Exact single-token analyses are linked to exact
generated forms; casing is never inferred from a capitalized input probe.
The full audit is separate from the bounded runtime sidecar.
"""
from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import io
import struct
import zipfile
from pathlib import Path

from build_variant_trial import (MAX_ARCHIVE_BYTES, MAX_MEMBER_BYTES,
                                canonical_bytes, dictionary_entries, read_json, sha256)
from build_function_word_trial import MORFEUSZ_VERSION, DICTIONARY_ID

BASE_SHA256 = '3767c76dbf87589182d6b26b8f8d64d80ec635764cee15d350015b60d41e21af'
PACK_NAME = 'cleverkeys-pl-global-casing-trial.zip'
COMMON_CLASS = 'nazwa_pospolita'


class SourceOracle:
    def __init__(self, oracle):
        self.oracle = oracle

    @lru_cache(maxsize=16000)
    def forms(self, lemma):
        return self.oracle.generate(lemma)

    def evidence(self, key):
        title = key[:1].upper() + key[1:]
        interpretations, proofs = {}, {}
        for probe in dict.fromkeys((key, title)):
            for start, end, payload in self.oracle.analyse(probe):
                if (start, end) != (0, 1) or len(payload) < 5:
                    continue
                orth, lemma, tag, names, labels = payload[:5]
                if orth != probe or tag.split(':')[0] in {'ign', 'interp'}:
                    continue
                source = {'lemma': lemma, 'tag': tag,
                          'nameClasses': sorted(set(names)), 'labels': sorted(set(labels))}
                rid = sha256(canonical_bytes(source))[:16]
                linked = []
                for form, gen_lemma, gen_tag, gen_names, gen_labels in self.forms(lemma):
                    # Full tag equality, not just POS; no component/fragment proofs.
                    if (form not in {key, title} or gen_lemma != lemma or gen_tag != tag
                            or sorted(set(gen_names)) != source['nameClasses']):
                        continue
                    proof = {'form': form, 'interpretationId': rid, 'tag': gen_tag,
                             'nameClasses': sorted(set(gen_names)),
                             'labels': sorted(set(gen_labels))}
                    linked.append(proof)
                if linked:
                    interpretations[rid] = {'id': rid, **source}
                    for proof in linked:
                        proofs[canonical_bytes(proof)] = proof
        return {'interpretations': sorted(interpretations.values(), key=lambda x: x['id']),
                'generatedFormProofs': [proofs[k] for k in sorted(proofs)]}


def classify(key, current, evidence):
    title = key[:1].upper() + key[1:]
    by_id = {i['id']: i for i in evidence['interpretations']}
    associations = {key: set(), title: set()}
    ordinary_lower = False
    proper_upper = False
    for proof in evidence['generatedFormProofs']:
        source = by_id[proof['interpretationId']]
        names = source['nameClasses']
        proper = any(n != COMMON_CLASS for n in names)
        form = proof['form']
        associations[form].update(['NAME:' + n for n in names]
                                  or ['POS:' + source['tag'].split(':')[0]])
        ordinary_lower |= form == key and not proper
        proper_upper |= form == title and proper
    forms = sorted((s for s, categories in associations.items() if categories),
                   key=lambda s: (s != key, s))
    default = key if ordinary_lower else title if proper_upper else current
    # Preserve source spellings that the current API cannot represent (e.g. all-caps).
    if current not in {key, title} or default not in forms:
        default = current
    return {'defaultSurface': default, 'ordinaryLower': ordinary_lower,
            'properUpper': proper_upper, 'attestedForms': forms,
            'associations': {s: sorted(associations[s]) for s in forms}}


def runtime_entry(key, default, decision, evidence):
    forms = sorted(decision['attestedForms'], key=lambda s: (s != default, s))
    by_id = {i['id']: i for i in evidence['interpretations']}
    groups = {}
    for proof in evidence['generatedFormProofs']:
        source = by_id[proof['interpretationId']]
        reading = {'lemma': source['lemma'], 'partOfSpeech': source['tag'].split(':')[0],
                   'nameClasses': source['nameClasses'], 'labels': source['labels']}
        identity = canonical_bytes(reading)
        group = groups.setdefault(identity, {**reading, 'surfaces': set()})
        group['surfaces'].add(proof['form'])
    readings = [{**groups[g], 'surfaces': sorted(groups[g]['surfaces'])} for g in sorted(groups)]
    return {'surfaceKey': key, 'canonicalForm': default,
            'capitalization': {'defaultSurface': default, 'variants': [
                {'surface': s, 'casePolicy': 'lowercase' if s == key else 'capitalized'}
                for s in forms]},
            'metadata': {'sourceEvidence': {
                'lexicalReadings': readings,
                'variantCategoryIds': decision['associations']}}}


def json_nodes(value):
    if isinstance(value, dict):
        return 1 + sum(json_nodes(v) for v in value.values())
    if isinstance(value, list):
        return 1 + sum(json_nodes(v) for v in value)
    return 1


def build_global_trial(base_raw, oracle, provenance, audit_sink,
                       expected_sha256=BASE_SHA256):
    if len(base_raw) > MAX_ARCHIVE_BYTES or sha256(base_raw) != expected_sha256:
        raise ValueError('v4 input size or checksum mismatch')
    with zipfile.ZipFile(io.BytesIO(base_raw)) as archive:
        infos = archive.infolist()
        names = [i.filename for i in infos]
        if len(set(names)) != len(names) or set(names) != {
                'dictionary.bin', 'manifest.json', 'unigrams.txt',
                'language-intelligence.json', 'NOTICE.txt'}:
            raise ValueError('unexpected or duplicate v4 member')
        if any(i.file_size > MAX_MEMBER_BYTES for i in infos) or sum(i.file_size for i in infos) > MAX_ARCHIVE_BYTES:
            raise ValueError('decompressed input exceeds limit')
        members = {n: archive.read(n) for n in names}
    manifest, old_sidecar = read_json(members['manifest.json']), read_json(members['language-intelligence.json'])
    raw = members['dictionary.bin']
    canonical = dictionary_entries(raw)
    if (manifest.get('code') != 'pl' or manifest.get('version') != 4
            or manifest.get('apiVersion') != 1 or manifest.get('wordCount') != len(canonical)
            or manifest.get('languageIntelligence', {}).get('sha256') != sha256(members['language-intelligence.json'])
            or old_sidecar.get('schemaVersion') != 1 or old_sidecar.get('languageCode') != 'pl'):
        raise ValueError('invalid v4 manifest/sidecar')
    entries = {e['surfaceKey']: e for e in old_sidecar['entries']}
    if len(entries) != len(old_sidecar['entries']) or any(
            k not in canonical or e['canonicalForm'] != canonical[k]
            or e['capitalization']['defaultSurface'] != canonical[k] for k, e in entries.items()):
        raise ValueError('invalid historical sidecar entries')
    count, start, normalized, accent = struct.unpack_from('<IIII', raw, 12)
    if not 48 <= start < normalized < accent <= len(raw):
        raise ValueError('invalid CKDT section bounds')
    source = SourceOracle(oracle)
    output, changes, counters, offset = bytearray(raw), [], Counter(), start
    audit_digest = hashlib.sha256()
    for _ in range(count):
        length = struct.unpack_from('<H', raw, offset)[0]
        offset += 2
        end = offset + length
        current = raw[offset:end].decode('utf-8')
        key = current.lower()
        evidence = source.evidence(key)
        decision = classify(key, current, evidence)
        default = decision['defaultSurface']
        if default != current:
            encoded = default.encode('utf-8')
            if len(encoded) != length or default.lower() != key:
                raise ValueError('case correction changes CKDT record length/key')
            output[offset:end] = encoded
            changes.append({'key': key, 'before': current, 'after': default, 'rank': raw[end]})
        # Export all discovered case ambiguity, plus corrected/control entries.
        # Keep richer historical GUS/source evidence where the decision is unchanged.
        if default in decision['attestedForms'] and (len(decision['attestedForms']) == 2 or default != current):
            if key not in entries or default != current:
                entries[key] = runtime_entry(key, default, decision, evidence)
        counters['auditedKeys'] += 1
        counters['sourceCoveredKeys'] += bool(decision['attestedForms'])
        counters['dualFormKeys'] += len(decision['attestedForms']) == 2
        counters['ordinaryAndProperKeys'] += decision['ordinaryLower'] and decision['properUpper']
        counters['unresolvedKeys'] += not decision['attestedForms']
        counters['unrepresentableCanonicalKeys'] += current not in {key, key[:1].upper() + key[1:]}
        audit_record = canonical_bytes({'surfaceKey': key, 'before': current,
                                        'decision': decision, **evidence})
        audit_sink.write(audit_record)
        audit_digest.update(audit_record)
        offset = end + 1
    if offset != normalized or counters['auditedKeys'] != count:
        raise ValueError('canonical section/count mismatch')
    corrected = bytes(output)
    if corrected[:start] != raw[:start] or corrected[normalized:] != raw[normalized:]:
        raise ValueError('header or lookup sections changed')
    updated = dictionary_entries(corrected)
    if list(updated) != list(canonical):
        raise ValueError('lexical keys/order changed')
    for key, entry in entries.items():
        cap = entry['capitalization']
        if entry['canonicalForm'] != updated[key] or cap['defaultSurface'] != updated[key]:
            raise ValueError('sidecar default contradicts CKDT')
        if cap['defaultSurface'] not in [v['surface'] for v in cap['variants']]:
            raise ValueError('default absent from source variants')
    sidecar = {'schemaVersion': 1, 'languageCode': 'pl',
               'provenance': {'globalCasingAudit': provenance,
                              'inputDictionarySha256': sha256(raw),
                              'dictionarySha256': sha256(corrected),
                              'fullAudit': {'file': 'global-casing-audit.jsonl',
                                            'sha256': audit_digest.hexdigest(), 'keyField': 'surfaceKey'},
                              'historicalNineEntryEvidence': old_sidecar.get('provenance')},
               'entries': sorted(entries.values(), key=lambda e: e['surfaceKey'])}
    side_bytes = canonical_bytes(sidecar)
    nodes = json_nodes(sidecar)
    if len(side_bytes) > 32 * 1024 * 1024 or nodes > 1_000_000 or len(entries) > 120_000:
        raise ValueError('runtime sidecar exceeds Android API-v1 limits')
    manifest['version'] = 5
    manifest['languageIntelligence']['sha256'] = sha256(side_bytes)
    manifest['attribution'] = manifest.get('attribution', '') + ' Global source-attested case-homonym audit.'
    members['manifest.json'] = canonical_bytes(manifest)
    members['dictionary.bin'] = corrected
    members['language-intelligence.json'] = side_bytes
    members['NOTICE.txt'] += (b'\nGlobal casing trial v5: every lexical key audited with Morfeusz 2 / SGJP;\n'
                             b'case homonyms retain source readings and generated-form links.\n')
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type, info.create_system, info.external_attr = zipfile.ZIP_DEFLATED, 3, 0o100644 << 16
            archive.writestr(info, members[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    result = out.getvalue()
    report = {'trialOnly': True, 'packVersion': 5, 'inputPackageSha256': sha256(base_raw),
              'packageSha256': sha256(result), 'dictionarySha256': sha256(corrected),
              'languageIntelligenceSha256': sha256(side_bytes), 'unigramsSha256': sha256(members['unigrams.txt']),
              'auditSha256': audit_digest.hexdigest(),
              'wordCount': count, 'runtimeEntries': len(entries), 'runtimeBytes': len(side_bytes),
              'runtimeJsonNodes': nodes, 'correctionCount': len(changes),
              'changeListSha256': sha256(canonical_bytes(changes)),
              'coverage': dict(counters), 'changes': changes, 'oracle': provenance,
              'preserved': ['CKDT keys/order/rank bytes', 'header and lookup sections', 'unigrams'],
              'limitations': ['No per-interpretation corpus weights or context AI.',
                              'Source-unresolved keys keep their existing spelling.',
                              'Full audit is separate; runtime metadata covers case conflicts/corrections and historical controls.',
                              'Phone acceptance and Android sidecar parse must be checked separately.']}
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
    if args.base_pack.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError('input exceeds archive limit')
    provenance = {'program': 'Morfeusz 2 / SGJP', 'version': MORFEUSZ_VERSION,
                  'dictionaryId': DICTIONARY_ID, 'caseHandling': 'CONDITIONALLY_CASE_SENSITIVE',
                  'documentation': 'https://morfeusz.sgjp.pl/doc/about/',
                  'builderSha256': sha256(Path(__file__).read_bytes())}
    args.out_dir.mkdir(parents=True, exist_ok=True)
    audit_path = args.out_dir / 'global-casing-audit.jsonl'
    with audit_path.open('wb') as sink:
        result, report = build_global_trial(args.base_pack.read_bytes(), oracle, provenance, sink)
    (args.out_dir / PACK_NAME).write_bytes(result)
    (args.out_dir / 'global-casing-trial-report.json').write_bytes(canonical_bytes(report))
    (args.out_dir / 'global-casing-reviewed-summary.json').write_bytes(
        canonical_bytes({k: v for k, v in report.items() if k != 'changes'}))
    (args.out_dir / 'cleverkeys-pl-global-casing-trial.sha256').write_text(
        report['packageSha256'] + '  ' + PACK_NAME + '\n', encoding='utf-8')
    print(f"Audited {report['wordCount']} keys; corrected {report['correctionCount']}; runtime entries {report['runtimeEntries']}")
    print(report['packageSha256'])


if __name__ == '__main__':
    main()
