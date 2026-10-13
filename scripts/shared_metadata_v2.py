#!/usr/bin/env python3
"""Lossless schema-v2 sharing of exact source headers and attributes.

Never merges case, POS, source suffixes, labels or missing/empty fields.
Only repeated objects whose references save JSON nodes are shared.
"""
from collections import Counter
import copy
import json

PACK_SHA = '0362cf38e06d821af96947104f7f714bfb63e9ea2ddf505ec466bc29140001f7'
SIDE_SHA = '9e737fcb1ac0b03847fbdec97fa03c85cd742a57d89c0d04891ba520c9eda15e'
ATTR_FIELDS = ('nameClasses', 'labels')


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()


def nodes(value):
    pending = [value]
    count = 0
    while pending:
        value = pending.pop()
        count += 1
        if isinstance(value, dict): pending.extend(value.values())
        elif isinstance(value, list): pending.extend(value)
    return count


def readings(document):
    for entry in document['entries']:
        yield from entry.get('metadata', {}).get('sourceEvidence', {}).get('lexicalReadings', [])


def header(row):
    assert 'lemma' in row and 'partOfSpeech' in row and 'surfaces' in row
    assert set(row) <= {'lemma', 'partOfSpeech', 'nameClasses', 'labels', 'surfaces'}
    return {k: v for k, v in row.items() if k != 'surfaces'}


def selected_headers(document, selective):
    definitions = {}
    counts = Counter()
    for row in readings(document):
        h = header(row); key = canonical(h)
        definitions.setdefault(key, h); counts[key] += 1
    # New reference adds one scalar node per occurrence; source table adds one
    # complete object per distinct header. Share only when the total node cost falls.
    selected = [k for k in sorted(definitions) if not selective or
        counts[k] * (nodes(definitions[k]) - 2) > nodes(definitions[k])]
    return [definitions[k] for k in selected], {k: i for i, k in enumerate(selected)}, counts


def share_lemmas(document, selective):
    definitions, refs, counts = selected_headers(document, selective)
    out = copy.deepcopy(document)
    out['schemaVersion'] = 2
    out['sourceLexemes'] = copy.deepcopy(definitions)
    replaced = 0
    for entry in out['entries']:
        evidence = entry.get('metadata', {}).get('sourceEvidence', {})
        if 'lexicalReadings' not in evidence: continue
        rows = []
        for row in evidence['lexicalReadings']:
            key = canonical(header(row))
            if key in refs:
                rows.append({'sourceRef': refs[key], 'surfaces': row['surfaces']}); replaced += 1
            else: rows.append(row)
        evidence['lexicalReadings'] = rows
    return out, dict(distinctExactSourceHeaders=len(counts), sourceTableRecords=len(definitions),
        readingReferences=replaced, inlineReadings=sum(counts.values())-replaced)


def attribute_objects(document):
    yield from document['sourceLexemes']
    yield from readings(document)


def share_attributes(document):
    definitions = {}; counts = Counter()
    for obj in attribute_objects(document):
        attrs = {k: obj[k] for k in ATTR_FIELDS if k in obj}
        if not attrs: continue
        key = canonical(attrs); definitions.setdefault(key, attrs); counts[key] += 1
    selected = [k for k in sorted(definitions) if
        counts[k] * (nodes(definitions[k]) - 2) > nodes(definitions[k])]
    refs = {k: i for i, k in enumerate(selected)}
    document['sourceAttributes'] = [copy.deepcopy(definitions[k]) for k in selected]
    changed = 0
    for obj in attribute_objects(document):
        key = canonical({k: obj[k] for k in ATTR_FIELDS if k in obj})
        if key not in refs: continue
        for k in ATTR_FIELDS: obj.pop(k, None)
        obj['sourceAttributesRef'] = refs[key]; changed += 1
    return dict(attributeTableRecords=len(selected), attributeReferences=changed)


def index(table, ref):
    assert type(ref) is int and 0 <= ref < len(table), 'Invalid reference'
    return table[ref]


def expand(document):
    # Simulate a fresh reader by accepting only the reloaded serialized document.
    out = copy.deepcopy(document)
    attrs = out.get('sourceAttributes', [])
    for obj in attribute_objects(out):
        if 'sourceAttributesRef' in obj:
            shared = index(attrs, obj.pop('sourceAttributesRef'))
            assert not set(obj) & set(shared), 'Conflicting attribute fields'
            obj.update(copy.deepcopy(shared))
    table = out.pop('sourceLexemes')
    for entry in out['entries']:
        evidence = entry.get('metadata', {}).get('sourceEvidence', {})
        if 'lexicalReadings' not in evidence: continue
        rows = []
        for row in evidence['lexicalReadings']:
            if 'sourceRef' in row:
                shared = index(table, row.pop('sourceRef'))
                assert not set(row) & set(shared), 'Conflicting source fields'
                row = {**copy.deepcopy(shared), **row}
            rows.append(row)
        evidence['lexicalReadings'] = rows
    out.pop('sourceAttributes', None)
    out['schemaVersion'] = 1
    return out
