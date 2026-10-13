#!/usr/bin/env python3
"""Add source-indexed ordinary thematic forms to the verified v6, without subtraction.

Pinned public Wiktionary indices locate families; exact SGJP analyse/generate
links prove spellings and lexical identities; pinned wordfreq controls ranks.
No private dictionary, hand-written forms or invented semantic descriptions.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
import math
from pathlib import Path
import re
import unicodedata
import zipfile

from build_common_forms_trial import (MAX_BYTES, MAX_TOTAL_BYTES, MAX_NODES, MAX_ENTRIES,
    WORDFREQ_COMMIT, REGRESSION_WORDS, ordinary, compact_entry, parse_dictionary, extend_dictionary)
from build_global_casing_trial import SourceOracle, json_nodes
from build_function_word_trial import MORFEUSZ_VERSION, DICTIONARY_ID
from build_variant_trial import canonical_bytes, read_json, sha256
from build_pl_preview import is_candidate

BASE_PACK_SHA256 = '01ea95d26a32a9784d3de10495a89e91a28f77230b39c3ddb298ecb27e127fce'
BASE_DICTIONARY_SHA256 = '158be14d8554b11cb13835731d47865917d40297445e773fe9483938b795021b'
SOURCE_LOCK_SHA256 = '85512adfc0533928515b326633fbbb719715094cb57295809efdf032893403da'
FORM_ZIPF = 1.0
INDEX_ANCHOR_ZIPF = 2.0
GROUPS = {'colloquial', 'computing', 'home', 'shopping', 'food', 'tools', 'construction'}
PACK_NAME = 'cleverkeys-pl-thematic-forms-trial.zip'


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
    if sha256(members['dictionary.bin']) != expected_dictionary:
        raise ValueError('base dictionary checksum')
    records, aliases, boundary = parse_dictionary(members['dictionary.bin'])
    manifest, side = read_json(members['manifest.json']), read_json(members['language-intelligence.json'])
    if (manifest.get('code') != 'pl' or manifest.get('version') != 6 or manifest.get('apiVersion') != 1
            or manifest.get('wordCount') != len(records) or side.get('languageCode') != 'pl'
            or side.get('schemaVersion') != 1
            or manifest.get('languageIntelligence', {}).get('sha256') != sha256(members['language-intelligence.json'])):
        raise ValueError('base manifest/sidecar mismatch')
    by_key = {w.lower(): w for w, _ in records}
    entries = side['entries']
    # Compact v6 entries intentionally rely on CKDT for their canonical spelling.
    if (len({e['surfaceKey'] for e in entries}) != len(entries)
            or any(e['surfaceKey'] not in by_key
                   or ('canonicalForm' in e and e['canonicalForm'] != by_key[e['surfaceKey']]) for e in entries)):
        raise ValueError('base sidecar identities')
    return members, manifest, side, records, aliases, boundary


def index_words(text):
    """Use complete link targets, never split phrases or infer case from labels."""
    words = set()
    for link in re.findall(r'\[\[([^\[\]]+)\]\]', text):
        word = unicodedata.normalize('NFC', link.split('|')[0].split('#')[0].strip())
        if word == word.lower() and is_candidate(word):
            words.add(word)
    return words


def load_sources(directory, expected_lock=SOURCE_LOCK_SHA256):
    raw = (directory / 'intake-lock.json').read_bytes()
    if len(raw) > 65536 or sha256(raw) != expected_lock:
        raise ValueError('source lock checksum/size')
    lock = read_json(raw)
    if len(lock) != len(GROUPS) or {row['group'] for row in lock} != GROUPS:
        raise ValueError('source groups mismatch')
    seeds = defaultdict(set)
    for row in lock:
        data = (directory / (row['group'] + '.wikitext')).read_bytes()
        if len(data) != row['bytes'] or len(data) > 1024 * 1024 or sha256(data) != row['sha256']:
            raise ValueError('source snapshot checksum/size: ' + row['group'])
        for word in index_words(data.decode('utf-8')):
            seeds[word].add(row['group'])
    return seeds, lock


def eligible_readings(key, evidence):
    ids = {p['interpretationId'] for p in evidence['generatedFormProofs'] if p['form'] == key}
    return [r for r in evidence['interpretations'] if ordinary(r) and r['id'] in ids]


def write_pack(members):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as z:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0)); info.create_system = 3
            info.external_attr = 0o100644 << 16
            z.writestr(info, members[name], compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return output.getvalue()


def build(base_raw, seeds, source_lock, out_dir, oracle, zipf, frequency, source_provenance,
          expected_sha256=BASE_PACK_SHA256, expected_dictionary=BASE_DICTIONARY_SHA256):
    members, manifest, side, old, aliases, boundary = read_base(base_raw, expected_sha256, expected_dictionary)
    base_keys = {w.lower() for w, _ in old}
    out_dir.mkdir(parents=True, exist_ok=True)
    # Refuse reuse rather than leave a stale installable ZIP after a failed gate.
    if (out_dir / PACK_NAME).exists():
        raise ValueError('output already contains an installable pack; use a fresh directory')
    source = SourceOracle(oracle)
    lemmas, candidates = defaultdict(dict), defaultdict(set)
    seed_stats = Counter(); seed_digest = hashlib.sha256()
    with (out_dir / 'thematic-seed-audit.jsonl').open('wb') as stream:
        for key, groups in sorted(seeds.items()):
            if not is_candidate(key) or key != key.lower() or not groups or not groups <= GROUPS:
                raise ValueError('invalid thematic seed')
            evidence = source.evidence(key); eligible = eligible_readings(key, evidence)
            value = zipf(key)
            reason = 'source-ordinary-family' if eligible else 'no-current-ordinary-source-proof'
            seed_stats[reason] += 1
            for reading in eligible:
                for group in sorted(groups):
                    anchor = lemmas[reading['lemma']].get(group)
                    if anchor is None or value > anchor['zipf']:
                        lemmas[reading['lemma']][group] = {'seed': key, 'zipf': value}
            row = canonical_bytes({'surfaceKey': key, 'groups': sorted(groups), 'zipf': value,
                                   'reason': reason, **evidence})
            stream.write(row); seed_digest.update(row)
    for lemma in sorted(lemmas):
        for payload in source.forms(lemma):
            form, gen_lemma, tag, names, labels = payload[:5]
            if (gen_lemma == lemma and form == form.lower() and is_candidate(form)
                    and ordinary({'tag': tag, 'nameClasses': names, 'labels': labels})):
                candidates[form].add(lemma)
    additions, new_entries, stats, groups, pos = [], [], Counter(), Counter(), Counter()
    max_freq = max(frequency(w) for w, _ in old)
    digest = hashlib.sha256()
    with (out_dir / 'thematic-forms-audit.jsonl').open('wb') as stream:
        for key, families in sorted(candidates.items()):
            if key in base_keys: continue
            value = zipf(key)
            anchor = max((a['zipf'] for lemma in families for a in lemmas[lemma].values()), default=0)
            evidence, eligible = None, []
            if value < FORM_ZIPF or anchor < INDEX_ANCHOR_ZIPF:
                reason = 'below-indexed-family-threshold'
            else:
                evidence = source.evidence(key)
                eligible = [r for r in eligible_readings(key, evidence) if r['lemma'] in families]
                anchor = max((a['zipf'] for r in eligible for a in lemmas[r['lemma']].values()), default=0)
                reason = ('indexed-attested-family' if eligible and anchor >= INDEX_ANCHOR_ZIPF
                          else 'no-eligible-indexed-source-proof')
            accepted = reason == 'indexed-attested-family'; stats[reason] += 1
            proof_groups = sorted({g for r in eligible for g in lemmas[r['lemma']]})
            if accepted:
                f = frequency(key)
                rank = max(0, min(255, int((1 - math.log(f + 1) / math.log(max_freq + 1)) * 255)))
                additions.append((key, rank)); new_entries.append(compact_entry(key, evidence))
                groups.update(proof_groups); pos.update({r['tag'].split(':')[0] for r in eligible})
            row = {'surfaceKey': key, 'indexedLemmas': sorted(families), 'zipf': value,
                   'familyZipf': anchor, 'reason': reason, 'accepted': accepted, 'groups': proof_groups}
            if evidence is not None: row.update(evidence)
            data = canonical_bytes(row); stream.write(data); digest.update(data)
    if not additions or len({k for k, _ in additions}) != len(additions):
        raise ValueError('empty/duplicate additions')
    binary = extend_dictionary(members['dictionary.bin'], old, aliases, boundary, additions, frequency)
    old_entries = {e['surfaceKey']: e for e in side['entries']}
    side['entries'] = sorted(side['entries'] + new_entries, key=lambda e: e['surfaceKey'])
    updated = {e['surfaceKey']: e for e in side['entries']}
    if any(updated[k] != e for k, e in old_entries.items()):
        raise ValueError('old source metadata changed')
    provenance = {'inputPackSha256': sha256(base_raw), 'dictionarySha256': sha256(binary),
                  'seedAuditSha256': seed_digest.hexdigest(), 'auditSha256': digest.hexdigest(),
                  'sourceLockCanonicalSha256': sha256(canonical_bytes(source_lock)),
                  'thematicIndices': source_lock, **source_provenance}
    side['provenance']['thematicFormsExpansion'] = provenance
    side['provenance']['dictionarySha256'] = sha256(binary)
    side_bytes = canonical_bytes(side); nodes = json_nodes(side)
    if len(side_bytes) > MAX_BYTES or nodes > MAX_NODES or len(side['entries']) > MAX_ENTRIES:
        raise ValueError(f'consumer metadata budget exceeded: bytes={len(side_bytes)}, nodes={nodes}')
    manifest['version'] = 7; manifest['wordCount'] = len(old) + len(additions)
    manifest['languageIntelligence']['sha256'] = sha256(side_bytes)
    manifest['attribution'] += ' Thematic indices: Polish Wiktionary contributors, CC BY-SA 4.0; exact revision/history in NOTICE.'
    notice = ('\nAdditive ordinary thematic trial v7. All v6 words, rank bytes, spellings and metadata retained.\n'
        'Index selection adapted from Polish Wiktionary contributors, CC BY-SA 4.0.\n'
        'https://creativecommons.org/licenses/by-sa/4.0/\n'
        'Changes: extracted single-token ordinary targets; SGJP-verified inflections; corpus frequency filtering.\n'
        'The derived thematic selection and bundled source snapshots are CC BY-SA 4.0; existing resource licences/credits remain.\n'
        'No definitions or semantic descriptions copied. Full source proofs accompany the build audit, not the runtime ZIP.\n')
    for row in source_lock:
        notice += row['title'] + '\nRevision: ' + row['url'] + '\nContributors: ' + row['history'] + '\n'
    members.update({'dictionary.bin': binary, 'language-intelligence.json': side_bytes,
                    'manifest.json': canonical_bytes(manifest), 'NOTICE.txt': members['NOTICE.txt'] + notice.encode()})
    if any(len(v) > MAX_BYTES for v in members.values()) or sum(map(len, members.values())) > MAX_TOTAL_BYTES:
        raise ValueError('output archive budget')
    package = write_pack(members)
    report = {'trialOnly': True, 'packVersion': 7, 'before': len(old), 'added': len(additions),
        'after': len(old) + len(additions), 'removed': 0, 'changedOldRanks': 0,
        'changedOldCanonicalRecords': 0, 'changedOldMetadataEntries': 0,
        'indexedSeedKeys': len(seeds), 'seedDecisions': dict(seed_stats), 'sourceFamilies': len(lemmas),
        'sourceGeneratedCandidateKeys': len(candidates), 'alreadyCoveredCandidateKeys': sum(k in base_keys for k in candidates),
        'candidateDecisions': dict(stats), 'addedGroupCoverageOverlapping': dict(groups), 'sourcePosCoverage': dict(pos),
        'runtimeEntries': len(side['entries']), 'runtimeBytes': len(side_bytes), 'runtimeJsonNodes': nodes,
        'requiredConsumerNodeBudget': MAX_NODES, 'remainingConsumerNodes': MAX_NODES - nodes,
        'packageSha256': sha256(package), 'dictionarySha256': sha256(binary),
        'languageIntelligenceSha256': sha256(side_bytes), 'auditSha256': digest.hexdigest(),
        'seedAuditSha256': seed_digest.hexdigest(), 'unigramsSha256': sha256(members['unigrams.txt']),
        'regressions': {k: k in base_keys or k in updated for k in REGRESSION_WORDS},
        'sources': provenance, 'selection': {'formZipf': FORM_ZIPF, 'indexedAnchorZipf': INDEX_ANCHOR_ZIPF},
        'limitations': ['No independent swipe ranking or phone performance measurement.',
            'Domain membership selects families; it does not prove a particular sense of a homonym or instruct the AI.',
            'Unsupported modern words, multiword expressions, proper-only names, brands and abbreviations await separate source stages.',
            'No old canonical records, ranks, case variants, source metadata or unigram bytes removed or changed.']}
    (out_dir / 'thematic-forms-report.json').write_bytes(canonical_bytes(report))
    (out_dir / PACK_NAME).write_bytes(package)
    (out_dir / 'cleverkeys-pl-thematic-forms-trial.sha256').write_text(sha256(package) + '  ' + PACK_NAME + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-pack', type=Path, required=True)
    parser.add_argument('--sources', type=Path, default=Path(__file__).resolve().parents[1] / 'source/thematic-v7')
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    import morfeusz2, wordfreq
    from importlib.metadata import version, distribution
    oracle = morfeusz2.Morfeusz(case_handling=morfeusz2.CONDITIONALLY_CASE_SENSITIVE)
    direct_url = json.loads(distribution('wordfreq').read_text('direct_url.json') or '{}')
    if (str(morfeusz2.__version__) != MORFEUSZ_VERSION or oracle.dict_id() != DICTIONARY_ID
            or version('wordfreq') != '3.2.0' or direct_url.get('vcs_info', {}).get('commit_id') != WORDFREQ_COMMIT):
        raise ValueError('source snapshot differs from pinned build')
    seeds, lock = load_sources(args.sources)
    provenance = {'morfeuszVersion': MORFEUSZ_VERSION, 'sgjpDictionaryId': DICTIONARY_ID,
                  'wordfreqVersion': '3.2.0', 'wordfreqCommit': WORDFREQ_COMMIT,
                  'sourceLockFileSha256': SOURCE_LOCK_SHA256}
    report = build(args.base_pack.read_bytes(), seeds, lock, args.out_dir, oracle,
        lambda w: wordfreq.zipf_frequency(w, 'pl'),
        lambda w: max(1.0, wordfreq.word_frequency(w, 'pl') * 1e8), provenance)
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
