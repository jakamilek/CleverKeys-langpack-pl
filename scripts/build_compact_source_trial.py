#!/usr/bin/env python3
"""Lossless API/schema-v3 source surface references with append-only source tables."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path

from build_deferred_names_trial import ExistingPool
from build_shared_metadata_trial import serialize
from build_thematic_forms_trial import write_pack
from build_variant_trial import canonical_bytes, sha256
from shared_metadata_v2 import nodes, header, ATTR_FIELDS

BASE_SHA = '11dee57bc161bd18f1f8e0e6bbee80099a039a5240b70419f971fc297e4e78b7'
BASE_DICTIONARY_SHA = 'c8c3870be1aaaeee0cd20f47e7e807b45897024dd032bccd45358cf70d8e4cdc'
PACK_NAME = 'cleverkeys-pl-compact-source-trial.zip'


def surfaces(key, mask):
    if type(mask) is not int or not 1 <= mask <= 7: raise ValueError('surface mask')
    if any(ord(ch) > 0xffff or 0xd800 <= ord(ch) <= 0xdfff for ch in key): raise ValueError('surface key')
    forms = [key, key[:1].upper()+key[1:], key.upper()]
    result = sorted({s for i, s in enumerate(forms) if mask & (1 << i)})
    if any(not 1 <= len(s) <= 96 for s in result): raise ValueError('surface length')
    return result


def mask_for(key, values):
    if not isinstance(values, list) or not values or values != sorted(set(values)): return None
    forms = [key, key[:1].upper()+key[1:], key.upper()]
    if any(s not in forms for s in values): return None
    mask = sum(1 << forms.index(s) for s in values)
    try: return mask if surfaces(key, mask) == values else None
    except ValueError: return None


def decode_entry(pool, value):
    out = copy.deepcopy(value)
    for row in out.get('metadata', {}).get('sourceEvidence', {}).get('lexicalReadings', []):
        if 'surfaceMask' in row:
            if 'surfaces' in row: raise ValueError('conflicting surfaces')
            row['surfaces'] = surfaces(out['surfaceKey'], row.pop('surfaceMask'))
    return pool.decode(out)


def factor(document):
    original = ExistingPool(document)
    definitions = {}; costs = Counter(); counts = Counter()
    for value in document['entries']:
        full = original.decode(value)
        packed_rows = value.get('metadata', {}).get('sourceEvidence', {}).get('lexicalReadings', [])
        full_rows = full.get('metadata', {}).get('sourceEvidence', {}).get('lexicalReadings', [])
        for row, decoded in zip(packed_rows, full_rows):
            if 'sourceRef' in row: continue
            source = header(decoded); key = canonical_bytes(source)
            definitions[key] = source; counts[key] += 1
            costs[key] += nodes({k: v for k, v in row.items() if k != 'surfaces'}) - 2
    def packed_header(value):
        out = copy.deepcopy(value)
        attrs = {k: out[k] for k in ATTR_FIELDS if k in out}
        ref = original.attribute_refs.get(canonical_bytes(attrs))
        if ref is not None and nodes(attrs) > 2:
            for k in ATTR_FIELDS: out.pop(k, None)
            out['sourceAttributesRef'] = ref
        return out
    selected = [k for k in sorted(definitions) if k not in original.source_refs and
                costs[k] > nodes(packed_header(definitions[k]))]
    out = copy.deepcopy(document)
    out['schemaVersion'] = 3
    refs = dict(original.source_refs)
    for key in selected:
        refs[key] = len(out['sourceLexemes'])
        out['sourceLexemes'].append(packed_header(definitions[key]))
    stats = Counter()
    for value in out['entries']:
        full = original.decode(value)
        rows = value.get('metadata', {}).get('sourceEvidence', {}).get('lexicalReadings', [])
        full_rows = full.get('metadata', {}).get('sourceEvidence', {}).get('lexicalReadings', [])
        for i, (row, decoded) in enumerate(zip(rows, full_rows)):
            stats['readings'] += 1
            if 'sourceRef' not in row:
                ref = refs.get(canonical_bytes(header(decoded)))
                if ref is not None:
                    row = dict(sourceRef=ref, surfaces=row['surfaces']); rows[i] = row
                    stats['promotedReadings'] += 1
            mask = mask_for(value['surfaceKey'], row.get('surfaces'))
            if mask is not None:
                del row['surfaces']; row['surfaceMask'] = mask; stats['surfaceMasks'] += 1
            else: stats['literalSurfaces'] += 1
    pool = ExistingPool(out); before_digest = hashlib.sha256(); after_digest = hashlib.sha256()
    for before, after in zip(document['entries'], out['entries']):
        original_value = canonical_bytes(original.decode(before)); result = canonical_bytes(decode_entry(pool, after))
        if original_value != result: raise ValueError('source view changed')
        before_digest.update(original_value); after_digest.update(result)
    if out['sourceLexemes'][:len(document['sourceLexemes'])] != document['sourceLexemes'] or out['sourceAttributes'] != document['sourceAttributes']:
        raise ValueError('source prefix changed')
    return out, dict(stats, appendedSourceRecords=len(selected), originalSourceRecords=len(document['sourceLexemes']),
                    sourceRecords=len(out['sourceLexemes']), decodedEntryViewsSha256=before_digest.hexdigest(),
                    reconstructedEntryViewsSha256=after_digest.hexdigest())


def build(raw, out, expected=BASE_SHA, expected_dictionary=BASE_DICTIONARY_SHA):
    # The same strict API-v2 base validator, with the pinned accepted v10 version.
    from build_deferred_names_trial import read_base as checked_base
    members, manifest, document, records, _, _ = checked_base(raw, expected, expected_dictionary, expected_version=10)
    converted, stats = factor(document)
    converted['provenance']['compactSourceRepresentation'] = dict(inputPackSha256=sha256(raw),
        sourceRecordPrefixPreserved=True, surfaceMaskBits=dict(lower=1, initialUpper=2, allUpper=4),
        exactSourceViews=True)
    encoded = serialize(converted)
    if len(encoded)>32*1024*1024 or nodes(converted)>2_000_000 or len(converted['entries'])>120_000:
        raise ValueError('runtime budget')
    if len(converted['sourceAttributes'])+len(converted['sourceLexemes'])>120_000: raise ValueError('source table budget')
    manifest.update(version=11, apiVersion=3)
    manifest['languageIntelligence'].update(schemaVersion=3, sha256=sha256(encoded))
    members.update({'manifest.json':canonical_bytes(manifest),'language-intelligence.json':encoded})
    members['NOTICE.txt'] += (b'\nCompact source representation v11, API/schema-v3. Install compatible APK first.\n'
        b'All v10 words/ranks/source views retained. Exact surface references and append-only source records only.\n')
    if any(len(v)>32*1024*1024 for v in members.values()) or sum(map(len,members.values()))>64*1024*1024: raise ValueError('archive budget')
    package = write_pack(members)
    report = dict(trialOnly=True, representationOnly=True, version=11, apiVersion=3, schemaVersion=3,
        inputPackSha256=sha256(raw), wordCount=len(records), metadataEntries=len(converted['entries']),
        added=0, removed=0, changedRanks=0, changedCaseVariants=0, changedSourceEvidence=0,
        originalMetadataBytes=len(serialize(document)), metadataBytes=len(encoded),
        originalNodes=nodes(document), metadataNodes=nodes(converted), remainingNodes=2_000_000-nodes(converted),
        packageSha256=sha256(package), dictionarySha256=sha256(members['dictionary.bin']),
        unigramsSha256=sha256(members['unigrams.txt']), languageIntelligenceSha256=sha256(encoded), **stats)
    out.mkdir(parents=True,exist_ok=True)
    if (out/PACK_NAME).exists(): raise ValueError('output already contains installable pack')
    (out/'compact-source-report.json').write_bytes(canonical_bytes(report))
    (out/PACK_NAME).write_bytes(package)
    (out/'cleverkeys-pl-compact-source-trial.sha256').write_text(sha256(package)+'  '+PACK_NAME+'\n')
    return report


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-pack',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True)
    a=p.parse_args();print(json.dumps(build(a.base_pack.read_bytes(),a.out_dir),ensure_ascii=False,indent=2))
