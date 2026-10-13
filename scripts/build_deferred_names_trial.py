#!/usr/bin/env python3
"""Resume the pinned v8 source audit additively on the phone-accepted v9 pack.

Shared tables and all previous encoded entries stay immutable. New readings
reuse exact existing records/attributes; other source headers remain inline.
This permits snapshot reuse with the already-installed schema-v2 APK.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import io
import json
import math
from pathlib import Path
import zipfile

from build_common_forms_trial import (MAX_BYTES, MAX_TOTAL_BYTES, MAX_NODES, MAX_ENTRIES,
    WORDFREQ_COMMIT, REGRESSION_WORDS, parse_dictionary, extend_dictionary)
from build_names_forms_trial import (NameOracle, admissions, entry, candidate,
    load_exclusions, MORFEUSZ_VERSION, DICTIONARY_ID, FOREIGN_LANGS)
from build_shared_metadata_trial import serialize
from build_variant_trial import canonical_bytes, read_json, sha256
from build_thematic_forms_trial import write_pack
from shared_metadata_v2 import nodes, header, ATTR_FIELDS

BASE_SHA = 'c1ffdac5ef607f183996abf6a4804490a0b5c43c39b6d4215975936062ba8677'
BASE_DICTIONARY_SHA = '6b86f55c09114f38b17acc5e397a8864961de6a347b024205bf69f8be4125ecb'
AUDIT_SHA = '18af9ce13103aeb969c6079729574ec327e8e4326daf9c5b5f5f3753b4c33177'
PACK_NAME = 'cleverkeys-pl-deferred-names-trial.zip'
MAX_AUDIT_BYTES = 128 * 1024 * 1024
MAX_AUDIT_LINE = 2 * 1024 * 1024


class ExistingPool:
    def __init__(self, document):
        self.attributes = document['sourceAttributes']
        self.records = []
        self.attribute_refs = {canonical_bytes(a): i for i, a in enumerate(self.attributes)}
        for packed in document['sourceLexemes']:
            record = copy.deepcopy(packed)
            if 'sourceAttributesRef' in record:
                attrs = self.attributes[record.pop('sourceAttributesRef')]
                if set(record) & set(attrs): raise ValueError('conflicting base attributes')
                record.update(copy.deepcopy(attrs))
            self.records.append(record)
        self.source_refs = {canonical_bytes(r): i for i, r in enumerate(self.records)}
        if len(self.source_refs) != len(self.records) or len(self.attribute_refs) != len(self.attributes):
            raise ValueError('duplicate base definitions')

    def encode(self, value):
        encoded = copy.deepcopy(value)
        rows = encoded['metadata']['sourceEvidence']['lexicalReadings']
        for i, row in enumerate(rows):
            source = header(row)
            ref = self.source_refs.get(canonical_bytes(source))
            if ref is not None:
                rows[i] = dict(sourceRef=ref, surfaces=row['surfaces'])
            else:
                attrs = {key: source[key] for key in ATTR_FIELDS if key in source}
                ref = self.attribute_refs.get(canonical_bytes(attrs))
                if ref is not None and nodes(attrs) > 2:
                    for key in ATTR_FIELDS: row.pop(key, None)
                    row['sourceAttributesRef'] = ref
        if self.decode(encoded) != value: raise ValueError('new source evidence changed')
        return encoded

    def decode(self, value):
        result = copy.deepcopy(value)
        rows = result.get('metadata', {}).get('sourceEvidence', {}).get('lexicalReadings', [])
        for i, row in enumerate(rows):
            if 'sourceRef' in row:
                if set(row) != {'sourceRef', 'surfaces'}: raise ValueError('conflicting source fields')
                rows[i] = {**copy.deepcopy(self.records[row['sourceRef']]), 'surfaces': row['surfaces']}
            elif 'sourceAttributesRef' in row:
                attrs = self.attributes[row.pop('sourceAttributesRef')]
                if set(row) & set(attrs): raise ValueError('conflicting attributes')
                row.update(copy.deepcopy(attrs))
        return result


def read_base(raw, expected=BASE_SHA, expected_dictionary=BASE_DICTIONARY_SHA, expected_version=9, expected_schema=2):
    if len(raw) > MAX_TOTAL_BYTES or sha256(raw) != expected: raise ValueError('base checksum/size')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names = z.namelist()
        if len(names) != 5 or set(names) != {'dictionary.bin', 'manifest.json',
                'language-intelligence.json', 'unigrams.txt', 'NOTICE.txt'}: raise ValueError('base members')
        if any(i.file_size > MAX_BYTES for i in z.infolist()) or sum(i.file_size for i in z.infolist()) > MAX_TOTAL_BYTES:
            raise ValueError('base decompression budget')
        members = {name: z.read(name) for name in names}
    if sha256(members['dictionary.bin']) != expected_dictionary: raise ValueError('base dictionary checksum')
    records, aliases, boundary = parse_dictionary(members['dictionary.bin'])
    manifest = read_json(members['manifest.json']); side = read_json(members['language-intelligence.json'])
    if (manifest.get('code') != 'pl' or manifest.get('version') != expected_version or manifest.get('apiVersion') != expected_schema
            or manifest.get('wordCount') != len(records) or side.get('languageCode') != 'pl'
            or side.get('schemaVersion') != expected_schema or manifest.get('languageIntelligence', {}).get('schemaVersion') != expected_schema
            or manifest['languageIntelligence'].get('sha256') != sha256(members['language-intelligence.json'])):
        raise ValueError('base identity')
    if serialize(side) != members['language-intelligence.json']: raise ValueError('base canonical JSON')
    canonical = {word.lower(): word for word, _ in records}
    keys = [e['surfaceKey'] for e in side['entries']]
    if (len(set(keys)) != len(keys) or any(e['surfaceKey'] not in canonical or
            ('canonicalForm' in e and e['canonicalForm'] != canonical[e['surfaceKey']]) for e in side['entries'])):
        raise ValueError('base sidecar identity')
    return members, manifest, side, records, aliases, boundary


def audit_rows(path, expected):
    if path.stat().st_size > MAX_AUDIT_BYTES: raise ValueError('audit size')
    digest = hashlib.sha256()
    with path.open('rb') as f:
        while line := f.readline(MAX_AUDIT_LINE + 1):
            if len(line) > MAX_AUDIT_LINE: raise ValueError('audit line size')
            digest.update(line)
            yield read_json(line)
    if digest.hexdigest() != expected: raise ValueError('audit checksum')


def source_value(row, zipf, exclusions):
    key = row['surfaceKey']
    if not candidate(key) or key != key.lower(): raise ValueError('invalid audit key')
    if row['reason'] not in {'source-attested-addition', 'measured-runtime-capacity', 'foreign-word-name-collision'}:
        raise ValueError('invalid audit decision')
    evidence = {k: row[k] for k in ('interpretations', 'generatedFormProofs')}
    for reading in evidence['interpretations']:
        source = {k: reading[k] for k in ('lemma', 'tag', 'nameClasses', 'labels')}
        if sha256(canonical_bytes(source))[:16] != reading['id']: raise ValueError('source interpretation identity')
    eligible = admissions(key, evidence, exclusions)
    eligible_groups = {g for _, _, groups in eligible for g in groups}
    if not eligible or not row['groups'] or not set(row['groups']) <= eligible_groups:
        raise ValueError('missing current source admission')
    surface, value = entry(key, evidence, zipf)
    if surface != row['canonicalForm'] or nodes(value) != row['runtimeNodes'] or zipf(key) != row['zipf']:
        raise ValueError('source snapshot/default differs')
    foreign = (key.isascii() and row['groups'] == ['proper_names'] and row['foreignZipf'] >= 3.0
               and row['foreignZipf'] > row['zipf'] + 1.0)
    if foreign != (row['reason'] == 'foreign-word-name-collision') or row['foreignLanguage'] not in FOREIGN_LANGS:
        raise ValueError('foreign collision policy differs')
    return surface, value, eligible, foreign


def build(raw, source_audit, out, oracle, zipf, frequency, exclusions, provenance,
          expected_base=BASE_SHA, expected_dictionary=BASE_DICTIONARY_SHA, expected_audit=AUDIT_SHA):
    members, manifest, side, old, aliases, boundary = read_base(raw, expected_base, expected_dictionary)
    if (out / PACK_NAME).exists(): raise ValueError('output already contains installable pack')
    base_keys = {word.lower() for word, _ in old}; pool = ExistingPool(side)
    # Measure every deferred category before using any capacity limit.
    measured = Counter(); classes = Counter(); seen = set(); previous_order = None
    for row in audit_rows(source_audit, expected_audit):
        key = row['surfaceKey']
        if key in seen: raise ValueError('duplicate audit key')
        seen.add(key)
        order = ('brands_and_software' not in row['groups'], 'initialisms' not in row['groups'], -row['zipf'], key)
        if previous_order is not None and order < previous_order: raise ValueError('audit order')
        previous_order = order
        surface, value, eligible, foreign = source_value(row, zipf, exclusions)
        if row['accepted'] and key not in base_keys: raise ValueError('previous admitted key disappeared')
        if key in base_keys: measured['alreadyCovered'] += 1; continue
        if foreign: measured['foreignCollisions'] += 1; continue
        encoded = pool.encode(value)
        measured['deferredEligibleKeys'] += 1
        measured['fullAdditionalNodes'] += nodes(encoded)
        measured['fullAdditionalBytes'] += len(canonical_bytes(encoded))
        classes.update({name for reading, _, _ in eligible for name in reading['nameClasses']})
    if measured['deferredEligibleKeys'] == 0: raise ValueError('empty deferred pool')
    side['provenance']['deferredNamesExpansion'] = dict(inputPackSha256=sha256(raw), auditSha256=expected_audit,
        stableSharedTables=True, **provenance)
    # Changing an existing 64-character dictionary hash does not change serialized size/nodes.
    side['provenance']['dictionarySha256'] = sha256(members['dictionary.bin'])
    node_count = nodes(side); byte_count = len(serialize(side)); entry_count = len(side['entries'])
    before_entries = dict((e['surfaceKey'], e) for e in side['entries'])
    table_digest = sha256(canonical_bytes(dict(sourceAttributes=side['sourceAttributes'], sourceLexemes=side['sourceLexemes'])))
    source = NameOracle(oracle); retained = []; decisions = Counter(); covered = Counter(); refs = Counter()
    source_families = set(); examples = []; max_freq = max(frequency(word) for word, _ in old)
    audit_digest = hashlib.sha256(); expanded_digest = hashlib.sha256(); out.mkdir(parents=True, exist_ok=True)
    with (out / 'deferred-forms-audit.jsonl').open('wb') as sink, (out / 'new-entries-expanded.jsonl').open('wb') as expanded_sink:
        for row in audit_rows(source_audit, expected_audit):
            key = row['surfaceKey']; surface, value, eligible, foreign = source_value(row, zipf, exclusions)
            encoded = pool.encode(value)
            cost = nodes(encoded); byte_cost = len(canonical_bytes(encoded))
            if key in base_keys: reason = 'already-covered'
            elif foreign: reason = 'foreign-word-name-collision'
            elif entry_count >= MAX_ENTRIES: reason = 'metadata-entry-limit'
            elif node_count + cost > MAX_NODES: reason = 'metadata-node-limit'
            elif byte_count + byte_cost > MAX_BYTES: reason = 'metadata-byte-limit'
            else: reason = 'source-attested-addition'
            accepted = reason == 'source-attested-addition'
            decisions[reason] += 1
            if accepted:
                # Revalidate every installed addition with the pinned native source now.
                expected = {k: row[k] for k in ('interpretations', 'generatedFormProofs')}
                if source.evidence(key) != expected: raise ValueError('native source evidence differs')
                expanded_bytes = canonical_bytes(value)
                expanded_sink.write(expanded_bytes); expanded_digest.update(expanded_bytes)
                node_count += cost; byte_count += byte_cost; entry_count += 1
                rank = max(0, min(255, int((1 - math.log(frequency(key) + 1) / math.log(max_freq + 1)) * 255)))
                retained.append((surface, rank, encoded))
                covered.update({name for reading, _, _ in eligible for name in reading['nameClasses']})
                source_families.update(reading['lemma'] for reading, _, _ in eligible)
                rows = encoded['metadata']['sourceEvidence']['lexicalReadings']
                refs['sourceReferences'] += sum('sourceRef' in r for r in rows)
                refs['attributeReferences'] += sum('sourceAttributesRef' in r for r in rows)
                if len(examples) < 30: examples.append(surface)
            audit = canonical_bytes(dict(**{k: v for k, v in row.items() if k not in {'accepted', 'reason'}},
                previousAccepted=row['accepted'], previousReason=row['reason'], accepted=accepted, reason=reason,
                encodedNodes=cost, encodedBytes=byte_cost))
            sink.write(audit); audit_digest.update(audit)
            if sum(decisions.values()) % 25000 == 0:
                print(f'Deferred candidates checked: {sum(decisions.values())}; admitted={len(retained)}', flush=True)
    if not retained: raise ValueError('empty additions')
    binary = extend_dictionary(members['dictionary.bin'], old, aliases, boundary,
        [(word, rank) for word, rank, _ in retained], frequency)
    side['entries'] = sorted(side['entries'] + [value for _, _, value in retained], key=lambda e: e['surfaceKey'])
    after_entries = {e['surfaceKey']: e for e in side['entries']}
    if len(after_entries) != len(side['entries']) or any(after_entries[k] != value for k, value in before_entries.items()):
        raise ValueError('old metadata changed/duplicate addition')
    if sha256(canonical_bytes(dict(sourceAttributes=side['sourceAttributes'], sourceLexemes=side['sourceLexemes']))) != table_digest:
        raise ValueError('shared source tables changed')
    side['provenance']['dictionarySha256'] = sha256(binary)
    side_bytes = serialize(side)
    if len(side_bytes) != byte_count or nodes(side) != node_count: raise ValueError('capacity accounting differs')
    if len(side_bytes) > MAX_BYTES or node_count > MAX_NODES or len(after_entries) > MAX_ENTRIES: raise ValueError('output metadata budget')
    manifest.update(version=10, wordCount=len(old) + len(retained))
    manifest['languageIntelligence']['sha256'] = sha256(side_bytes)
    notice = ('\nAdditive deferred source-attested names trial v10; all v9 words/ranks/metadata retained.\n'
              'Source: pinned v8 source audit and native Morfeusz2/SGJP revalidation of every addition.\n'
              'Selection/ranks: pinned wordfreq; previous foreign-name collision rules retained.\n'
              'Shared API/schema-v2 tables and indexes unchanged for compatible snapshot reuse.\n')
    members.update({'dictionary.bin': binary, 'language-intelligence.json': side_bytes,
                    'manifest.json': canonical_bytes(manifest), 'NOTICE.txt': members['NOTICE.txt'] + notice.encode()})
    if any(len(v) > MAX_BYTES for v in members.values()) or sum(map(len, members.values())) > MAX_TOTAL_BYTES:
        raise ValueError('output archive budget')
    package = write_pack(members)
    report = dict(trialOnly=True, packVersion=10, apiVersion=2, schemaVersion=2,
        before=len(old), added=len(retained), after=len(old)+len(retained), removed=0,
        changedOldRanks=0, changedOldCanonicalRecords=0, changedOldMetadataEntries=0,
        sharedTablesUnchanged=True, sharedTablesSha256=table_digest,
        inputPackSha256=sha256(raw), inputAuditSha256=expected_audit, inputAuditKeys=len(seen),
        measured=dict(measured), fullMeasuredNameClassesOverlapping=dict(classes),
        candidateDecisions=dict(decisions), addedNameClassesOverlapping=dict(covered), addedSourceFamilies=len(source_families),
        newReferenceCounts=dict(refs), sampleNewSourceSpellings=examples,
        runtimeEntries=len(after_entries), runtimeBytes=len(side_bytes), runtimeJsonNodes=node_count,
        remainingConsumerNodes=MAX_NODES-node_count, remainingMetadataEntries=MAX_ENTRIES-len(after_entries),
        packageSha256=sha256(package), dictionarySha256=sha256(binary), languageIntelligenceSha256=sha256(side_bytes),
        unigramsSha256=sha256(members['unigrams.txt']), outputAuditSha256=audit_digest.hexdigest(),
        expandedAdditionsSha256=expanded_digest.hexdigest(), sources=provenance,
        regressions={key: key in base_keys for key in REGRESSION_WORDS},
        limitations=['No independent swipe/SI accuracy or phone PSS measurement.',
            'Capacity deferrals remain audited; no existing word is removed.',
            'Only prior SGJP-attested categories; no new manual spellings, semantics or private export.',
            'Shared source tables stay fixed; unshared new headers remain inline.',
            'Unsupported modern brands, punctuation forms and all-caps alternative policies remain separate.'])
    (out / 'deferred-names-report.json').write_bytes(canonical_bytes(report))
    (out / PACK_NAME).write_bytes(package)
    (out / 'cleverkeys-pl-deferred-names-trial.sha256').write_text(sha256(package)+'  '+PACK_NAME+'\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('base-pack', 'source-audit', 'out-dir'): parser.add_argument('--'+key, type=Path, required=True)
    args = parser.parse_args()
    import morfeusz2, wordfreq
    from importlib.metadata import distribution, version
    oracle = morfeusz2.Morfeusz(case_handling=morfeusz2.CONDITIONALLY_CASE_SENSITIVE)
    direct = json.loads(distribution('wordfreq').read_text('direct_url.json') or '{}')
    if (str(morfeusz2.__version__) != MORFEUSZ_VERSION or oracle.dict_id() != DICTIONARY_ID
            or version('wordfreq') != '3.2.0' or direct.get('vcs_info', {}).get('commit_id') != WORDFREQ_COMMIT):
        raise ValueError('source snapshot differs')
    exclusions = load_exclusions(Path(__file__).resolve().parents[1] / 'sources/staging/first_name_source_exclusions.tsv')
    provenance = dict(morfeuszVersion=MORFEUSZ_VERSION, sgjpDictionaryId=DICTIONARY_ID,
        wordfreqVersion='3.2.0', wordfreqCommit=WORDFREQ_COMMIT, resumedAuditRun=38167348861,
        sourceExclusionsSha256='2eda1f002aa3b631cbf919d71c43421190531d784d8545d8d6f2cd8c55faccea',
        foreignCollisionLanguages=list(FOREIGN_LANGS), foreignCollisionMinZipf=3.0, foreignCollisionMargin=1.0)
    report = build(args.base_pack.read_bytes(), args.source_audit, args.out_dir, oracle,
        lambda word: wordfreq.zipf_frequency(word, 'pl'),
        lambda word: max(1.0, wordfreq.word_frequency(word, 'pl') * 1e8), exclusions, provenance)
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
