#!/usr/bin/env python3
"""Add corpus-backed ordinary Polish forms to the verified v5 pack, without subtraction.

The private dictionary is never a build input. SGJP exact analyse/generate links
prove forms; wordfreq 3.2 selects useful forms and source-backed lexical families.
Full evidence stays in the audit; compact API-v1 readings retain the same facts.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import io
import json
import math
from pathlib import Path
import struct
import zipfile

from build_variant_trial import canonical_bytes, read_json, sha256
from build_global_casing_trial import SourceOracle, classify, json_nodes, runtime_entry
from build_function_word_trial import MORFEUSZ_VERSION, DICTIONARY_ID
from build_pl_preview import is_candidate, normalize_accents

BASE_PACK_SHA256 = 'aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb'
BASE_DICTIONARY_SHA256 = 'a32f6a55bce7375e744d3d261d6ec9aad96dc64725ac429d4cb1d7225aed3c2a'
WORDFREQ_COMMIT = '912caf64b657478d1dff1138efdc078947d54bb1'
MAX_BYTES = 32 * 1024 * 1024
MAX_TOTAL_BYTES = 64 * 1024 * 1024
MAX_NODES = 2_000_000
MAX_ENTRIES = 120_000
NONLEXICAL_POS = {'ign', 'interp', 'brev', 'romandig', 'frag'}
OBSOLETE_LABELS = ('daw.', 'przest.', 'hist.', 'gwar.')
REGRESSION_WORDS = ('dodam', 'grzeje', 'kasami', 'nawilżane', 'odpowiadam',
                    'patrzysz', 'poczekaj', 'podpowie', 'pozdrawiam')


def ordinary(reading):
    return (reading['tag'].split(':')[0] not in NONLEXICAL_POS
            and not any(n != 'nazwa_pospolita' for n in reading['nameClasses'])
            and not any(label.startswith(OBSOLETE_LABELS) for label in reading['labels']))


def selected(form_zipf, family_zipf):
    return form_zipf >= 2.0 or (form_zipf >= 1.0 and family_zipf >= 2.5)


def parse_dictionary(raw):
    if len(raw) < 48:
        raise ValueError('short CKDT')
    magic, version, language, count, start, normalized, accent = struct.unpack_from('<4sI4sIIII', raw)
    if magic != b'CKDT' or version != 2 or language != b'pl\0\0' or not (start == 48 < normalized < accent < len(raw)):
        raise ValueError('invalid CKDT header')
    def string(pos):
        if pos + 2 > len(raw): raise ValueError('short string')
        length, = struct.unpack_from('<H', raw, pos)
        end = pos + 2 + length
        if not length or end > len(raw): raise ValueError('invalid string length')
        return raw[pos + 2:end].decode('utf-8'), end
    records, keys, pos = [], set(), start
    for _ in range(count):
        word, pos = string(pos)
        if pos >= normalized or word.lower() in keys: raise ValueError('invalid canonical record')
        records.append((word, raw[pos])); keys.add(word.lower()); pos += 1
    if pos != normalized: raise ValueError('canonical boundary')
    normalized_count, = struct.unpack_from('<I', raw, pos); pos += 4
    norms = []
    for _ in range(normalized_count):
        word, pos = string(pos); norms.append(word)
    if pos != accent or len(set(norms)) != len(norms): raise ValueError('normalized boundary/duplicates')
    aliases = {}
    for norm in norms:
        if pos >= len(raw): raise ValueError('short aliases')
        n = raw[pos]; pos += 1
        if not n or pos + 4 * n > len(raw): raise ValueError('invalid aliases')
        indices = list(struct.unpack_from('<' + 'I' * n, raw, pos)); pos += 4 * n
        if len(set(indices)) != len(indices) or any(i >= count or normalize_accents(records[i][0]) != norm for i in indices):
            raise ValueError('invalid alias index')
        aliases[norm] = indices
    if pos != len(raw) or sorted(i for indices in aliases.values() for i in indices) != list(range(count)):
        raise ValueError('unconsumed bytes or incomplete alias coverage')
    return records, aliases, normalized


def read_base(raw, expected_sha256=BASE_PACK_SHA256, expected_dictionary=BASE_DICTIONARY_SHA256):
    if len(raw) > MAX_TOTAL_BYTES or sha256(raw) != expected_sha256:
        raise ValueError('base checksum/size')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names = z.namelist()
        required = {'dictionary.bin', 'manifest.json', 'language-intelligence.json', 'unigrams.txt', 'NOTICE.txt'}
        if len(names) != len(set(names)) or set(names) != required:
            raise ValueError('unexpected or duplicate members')
        if any(i.file_size > MAX_BYTES for i in z.infolist()) or sum(i.file_size for i in z.infolist()) > MAX_TOTAL_BYTES:
            raise ValueError('input decompression budget')
        members = {name: z.read(name) for name in names}
    if sha256(members['dictionary.bin']) != expected_dictionary: raise ValueError('base dictionary checksum')
    records, aliases, boundary = parse_dictionary(members['dictionary.bin'])
    manifest, side = read_json(members['manifest.json']), read_json(members['language-intelligence.json'])
    if (manifest.get('code') != 'pl' or manifest.get('version') != 5 or manifest.get('apiVersion') != 1
            or manifest.get('wordCount') != len(records) or side.get('languageCode') != 'pl' or side.get('schemaVersion') != 1
            or manifest.get('languageIntelligence', {}).get('sha256') != sha256(members['language-intelligence.json'])):
        raise ValueError('base manifest/sidecar mismatch')
    by_key = {w.lower(): w for w, _ in records}
    entries = side['entries']
    if len({e['surfaceKey'] for e in entries}) != len(entries) or any(e['surfaceKey'] not in by_key or e['canonicalForm'] != by_key[e['surfaceKey']] for e in entries):
        raise ValueError('base sidecar identities')
    return members, manifest, side, records, aliases, boundary


def anchors_from_audit(path, expected_hash, base_keys, zipf):
    if path.stat().st_size > 112 * 1024 * 1024: raise ValueError('base audit size')
    anchors, seen, digest = defaultdict(float), set(), hashlib.sha256()
    with path.open('rb') as stream:
        for line in stream:
            digest.update(line); row = json.loads(line)
            key = row['surfaceKey']
            if key in seen or key not in base_keys: raise ValueError('base audit key mismatch')
            seen.add(key); value = zipf(key)
            if value >= 2.5:
                for reading in row['interpretations']:
                    if ordinary(reading): anchors[reading['lemma']] = max(anchors[reading['lemma']], value)
    if seen != base_keys or digest.hexdigest() != expected_hash:
        raise ValueError('base audit checksum/coverage')
    return dict(anchors)


def compact_entry(key, evidence):
    decision = classify(key, key, evidence)
    entry = runtime_entry(key, key, decision, evidence)
    # One ordinary lowercase spelling needs no capitalization declaration. The
    # decoder's exact CKDT spelling remains authoritative. Ambiguous forms keep
    # both declared spellings, default and every source reading.
    if len(entry['capitalization']['variants']) == 1:
        del entry['capitalization']; del entry['canonicalForm']
    source = entry['metadata']['sourceEvidence']
    for reading in source['lexicalReadings']:
        for field in ('labels', 'nameClasses'):
            if not reading[field]: del reading[field]
    # Category IDs are recoverable from the preserved POS/name classes; avoid
    # duplicating them in a larger pack. The consumer reads lexicalReadings.
    del source['variantCategoryIds']
    return entry


def extend_dictionary(raw, old, old_aliases, boundary, additions, frequency):
    records = old + [(key, rank) for key, rank in additions]
    appended = bytearray()
    for key, rank in additions:
        data = key.encode('utf-8'); appended += struct.pack('<H', len(data)) + data + bytes([rank])
    canonical = raw[48:boundary] + bytes(appended)
    aliases = copy.deepcopy(old_aliases)
    for index in range(len(old), len(records)):
        key = records[index][0]; norm = normalize_accents(key)
        group = aliases.setdefault(norm, [])
        value = frequency(key)
        position = next((p for p, i in enumerate(group) if frequency(records[i][0]) < value), len(group))
        group.insert(position, index)
    normalized = bytearray(struct.pack('<I', len(aliases))); accent = bytearray()
    for norm in sorted(aliases):
        data = norm.encode('utf-8'); normalized += struct.pack('<H', len(data)) + data
        group = aliases[norm]
        if not 1 <= len(group) <= 255: raise ValueError('accent group budget')
        accent += bytes([len(group)]) + struct.pack('<' + 'I' * len(group), *group)
    header = bytearray(raw[:48])
    struct.pack_into('<IIII', header, 12, len(records), 48, 48 + len(canonical), 48 + len(canonical) + len(normalized))
    result = bytes(header) + canonical + normalized + accent
    after, after_aliases, _ = parse_dictionary(result)
    if after[:len(old)] != old or result[48:boundary] != raw[48:boundary]: raise ValueError('old records changed')
    for norm, group in old_aliases.items():
        if [i for i in after_aliases[norm] if i < len(old)] != group: raise ValueError('old alias order changed')
    return result


def build(base_raw, audit_path, out_dir, oracle, ranked_words, zipf, frequency, source_provenance,
          expected_sha256=BASE_PACK_SHA256, expected_dictionary=BASE_DICTIONARY_SHA256):
    members, manifest, side, old, aliases, boundary = read_base(base_raw, expected_sha256, expected_dictionary)
    base_keys = {w.lower() for w, _ in old}
    anchors = anchors_from_audit(audit_path, side['provenance']['fullAudit']['sha256'], base_keys, zipf)
    out_dir.mkdir(parents=True, exist_ok=True)
    source = SourceOracle(oracle)
    additions, entries, stats, groups = [], copy.deepcopy(side['entries']), Counter(), Counter()
    max_freq = max(frequency(w) for w, _ in old)
    full_digest, count = hashlib.sha256(), 0
    with (out_dir / 'common-forms-audit.jsonl').open('wb') as stream:
        for rank, key in enumerate(ranked_words):
            if key in base_keys: continue
            evidence = source.evidence(key)
            eligible = [r for r in evidence['interpretations'] if ordinary(r)]
            lower_ids = {p['interpretationId'] for p in evidence['generatedFormProofs'] if p['form'] == key}
            eligible = [r for r in eligible if r['id'] in lower_ids]
            family = max((anchors.get(r['lemma'], 0.0) for r in eligible), default=0.0)
            value = zipf(key)
            if not eligible: reason = 'no-current-ordinary-source-proof'
            elif not selected(value, family): reason = 'below-form-and-family-threshold'
            else: reason = 'corpus-form' if value >= 2.0 else 'attested-common-family'
            accepted = reason in {'corpus-form', 'attested-common-family'}
            stats[reason] += 1
            if accepted:
                f = frequency(key)
                new_rank = max(0, min(255, int((1 - math.log(f + 1) / math.log(max_freq + 1)) * 255)))
                additions.append((key, new_rank)); entries.append(compact_entry(key, evidence))
                groups.update({r['tag'].split(':')[0] for r in eligible})
            record = canonical_bytes({'surfaceKey': key, 'candidateRank': rank, 'zipf': value,
                'familyZipf': family, 'reason': reason, 'accepted': accepted, **evidence})
            stream.write(record); full_digest.update(record); count += 1
            if count % 25000 == 0: print(f'Audited {count} new candidate keys; admitted {len(additions)}', flush=True)
    if len({key for key, _ in additions}) != len(additions) or any(k in base_keys for k, _ in additions):
        raise ValueError('duplicate additions')
    binary = extend_dictionary(members['dictionary.bin'], old, aliases, boundary, additions, frequency)
    previous_entries = {e['surfaceKey']: e for e in side['entries']}
    side['entries'] = sorted(entries, key=lambda e: e['surfaceKey'])
    updated_entries = {e['surfaceKey']: e for e in side['entries']}
    if any(updated_entries[key] != value for key, value in previous_entries.items()):
        raise ValueError('old source metadata changed')
    side['provenance']['commonFormsExpansion'] = {'inputPackSha256': sha256(base_raw),
        'dictionarySha256': sha256(binary), 'auditSha256': full_digest.hexdigest(), **source_provenance}
    side['provenance']['dictionarySha256'] = sha256(binary)
    side_bytes = canonical_bytes(side); node_count = json_nodes(side)
    if len(side_bytes) > MAX_BYTES or node_count > MAX_NODES or len(entries) > MAX_ENTRIES:
        raise ValueError(f'consumer metadata budget exceeded: bytes={len(side_bytes)}, nodes={node_count}, entries={len(entries)}')
    manifest['version'] = 6; manifest['wordCount'] = len(old) + len(additions)
    manifest['languageIntelligence']['sha256'] = sha256(side_bytes)
    manifest['attribution'] += ' Additive ordinary-form coverage from source-linked SGJP and pinned wordfreq.'
    members['dictionary.bin'] = binary; members['language-intelligence.json'] = side_bytes
    members['manifest.json'] = canonical_bytes(manifest)
    members['NOTICE.txt'] += (b'\nAdditive ordinary Polish form trial v6. All v5 words, rank bytes, case variants and readings retained.\n'
        b'Sources: Morfeusz 2 / SGJP 2026.06.01; wordfreq 3.2 commit 912caf64b657478d1dff1138efdc078947d54bb1.\n'
        b'Keep existing source attribution. Full source proofs accompany the build report, not the runtime ZIP.\n')
    if any(len(v) > MAX_BYTES for v in members.values()) or sum(map(len, members.values())) > MAX_TOTAL_BYTES:
        raise ValueError('output archive budget')
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as z:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0)); info.create_system = 3
            info.external_attr = 0o100644 << 16
            z.writestr(info, members[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    package = output.getvalue(); path = out_dir / 'cleverkeys-pl-common-forms-trial.zip'; path.write_bytes(package)
    new_keys = {k for k, _ in additions}
    report = {'trialOnly': True, 'packVersion': 6, 'before': len(old), 'added': len(additions),
        'after': len(old) + len(additions), 'removed': 0, 'changedOldRanks': 0,
        'changedOldCanonicalRecords': 0, 'changedOldMetadataEntries': 0, 'candidateDecisions': dict(stats),
        'sourcePosCoverage': dict(groups), 'runtimeEntries': len(entries), 'runtimeBytes': len(side_bytes),
        'runtimeJsonNodes': node_count, 'requiredConsumerNodeBudget': MAX_NODES,
        'packageSha256': sha256(package), 'dictionarySha256': sha256(binary),
        'languageIntelligenceSha256': sha256(side_bytes), 'auditSha256': full_digest.hexdigest(),
        'unigramsSha256': sha256(members['unigrams.txt']), 'regressions': {k: k in base_keys or k in new_keys for k in REGRESSION_WORDS},
        'sources': source_provenance, 'selection': {'directFormZipf': 2.0, 'familyAnchorZipf': 2.5, 'familyFormZipf': 1.0},
        'limitations': ['No independent swipe ranking or phone performance measurement.',
            'Ordinary vocabulary stage; proper-only names, brands, abbreviations and personal literals are separate stages.',
            'Consumer must support 2M JSON nodes; byte, depth, entry and source-identity bounds stay enforced.']}
    (out_dir / 'common-forms-report.json').write_bytes(canonical_bytes(report))
    (out_dir / 'cleverkeys-pl-common-forms-trial.sha256').write_text(sha256(package) + '  ' + path.name + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-pack', type=Path, required=True)
    parser.add_argument('--base-audit', type=Path, required=True)
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    import morfeusz2
    import wordfreq
    from importlib.metadata import version, distribution
    oracle = morfeusz2.Morfeusz(case_handling=morfeusz2.CONDITIONALLY_CASE_SENSITIVE)
    direct_url = json.loads(distribution('wordfreq').read_text('direct_url.json') or '{}')
    if (str(morfeusz2.__version__) != MORFEUSZ_VERSION or oracle.dict_id() != DICTIONARY_ID
            or version('wordfreq') != '3.2.0' or direct_url.get('vcs_info', {}).get('commit_id') != WORDFREQ_COMMIT):
        raise ValueError('source snapshot differs from pinned build')
    words, seen = [], set()
    for raw in wordfreq.iter_wordlist('pl'):
        key = raw.lower()
        if key in seen or not is_candidate(key): continue
        seen.add(key); words.append(key)
        if len(words) == 300000: break
    provenance = {'morfeuszVersion': MORFEUSZ_VERSION, 'sgjpDictionaryId': DICTIONARY_ID,
        'wordfreqVersion': '3.2.0', 'wordfreqCommit': WORDFREQ_COMMIT, 'candidateLimit': 300000}
    report = build(args.base_pack.read_bytes(), args.base_audit, args.out_dir, oracle, words,
        lambda w: wordfreq.zipf_frequency(w, 'pl'),
        lambda w: max(1.0, wordfreq.word_frequency(w, 'pl') * 1e8), provenance)
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
