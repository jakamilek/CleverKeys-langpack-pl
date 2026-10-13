#!/usr/bin/env python3
"""Resume source-attested names additively on accepted compact-schema v11."""
from collections import Counter
import argparse
import hashlib
import math
from pathlib import Path
import json

from build_deferred_names_trial import (ExistingPool, read_base, audit_rows, source_value,
    NameOracle, MAX_BYTES, MAX_TOTAL_BYTES, MAX_NODES, MAX_ENTRIES, WORDFREQ_COMMIT,
    REGRESSION_WORDS, extend_dictionary, load_exclusions, MORFEUSZ_VERSION,
    DICTIONARY_ID, FOREIGN_LANGS, serialize, write_pack, canonical_bytes, sha256,
    AUDIT_SHA)
from build_compact_source_trial import mask_for, decode_entry
from shared_metadata_v2 import nodes

BASE_SHA = '8169a8ac33261fc245d46a344193759a0c1a84b0eb49cf2436e46ccaed90a229'
BASE_DICTIONARY_SHA = 'c8c3870be1aaaeee0cd20f47e7e807b45897024dd032bccd45358cf70d8e4cdc'
PACK_NAME = 'cleverkeys-pl-compact-names-trial.zip'


class CompactPool(ExistingPool):
    def encode(self, value):
        encoded = super().encode(value)
        for row in encoded['metadata']['sourceEvidence']['lexicalReadings']:
            mask = mask_for(value['surfaceKey'], row.get('surfaces'))
            if mask is not None:
                del row['surfaces']; row['surfaceMask'] = mask
        if decode_entry(self, encoded) != value: raise ValueError('compact source view changed')
        return encoded


def build(raw, source_audit, out, oracle, zipf, frequency, exclusions, provenance,
          expected_base=BASE_SHA, expected_dictionary=BASE_DICTIONARY_SHA, expected_audit=AUDIT_SHA):
    members, manifest, side, old, aliases, boundary = read_base(raw, expected_base, expected_dictionary, expected_version=11, expected_schema=3)
    if (out / PACK_NAME).exists(): raise ValueError('output already contains installable pack')
    base_keys = {word.lower() for word, _ in old}; pool = CompactPool(side)
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
    side['provenance']['compactDeferredNamesExpansion'] = dict(inputPackSha256=sha256(raw), auditSha256=expected_audit,
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
                refs['surfaceMasks'] += sum('surfaceMask' in r for r in rows)
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
    manifest.update(version=12, wordCount=len(old) + len(retained))
    manifest['languageIntelligence']['sha256'] = sha256(side_bytes)
    notice = ('\nAdditive deferred source-attested names trial v12; all v11 words/ranks/metadata retained.\n'
              'Source: pinned v8 source audit and native Morfeusz2/SGJP revalidation of every addition.\n'
              'Selection/ranks: pinned wordfreq; previous foreign-name collision rules retained.\n'
              'Shared API/schema-v3 tables and indexes unchanged for compatible snapshot reuse.\n')
    members.update({'dictionary.bin': binary, 'language-intelligence.json': side_bytes,
                    'manifest.json': canonical_bytes(manifest), 'NOTICE.txt': members['NOTICE.txt'] + notice.encode()})
    if any(len(v) > MAX_BYTES for v in members.values()) or sum(map(len, members.values())) > MAX_TOTAL_BYTES:
        raise ValueError('output archive budget')
    package = write_pack(members)
    report = dict(trialOnly=True, packVersion=12, apiVersion=3, schemaVersion=3,
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
    (out / 'compact-names-report.json').write_bytes(canonical_bytes(report))
    (out / PACK_NAME).write_bytes(package)
    (out / 'cleverkeys-pl-compact-names-trial.sha256').write_text(sha256(package)+'  '+PACK_NAME+'\n')
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
