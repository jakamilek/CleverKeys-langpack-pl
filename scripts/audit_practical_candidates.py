#!/usr/bin/env python3
"""Revalidate the frozen candidate bundle, without producing an installable pack."""
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from importlib.metadata import distribution, version
import io
import json
from pathlib import Path
import zipfile

from build_practical_candidate_modules import (
    BASE_SHA, DICT_SHA, SourceOracle, MORFEUSZ_VERSION, DICTIONARY_ID,
    WORDFREQ_COMMIT, ordinary, selected, lexical_matches, compact_entry,
    CompactPool, decode_entry, read_base, key_shape, source_candidates,
    canonical_bytes, sha256, nodes)
from build_shared_metadata_trial import serialize

BUNDLE_SHA = '6c7a7c2be951f6b32c1b65be24f3e907ad3a3f5bc161eaadf1b4ae0e794ffe77'

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base', type=Path, required=True)
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    import morfeusz2, wordfreq
    native = morfeusz2.Morfeusz(case_handling=morfeusz2.CONDITIONALLY_CASE_SENSITIVE)
    direct = json.loads(distribution('wordfreq').read_text('direct_url.json') or '{}')
    assert str(morfeusz2.__version__) == MORFEUSZ_VERSION
    assert native.dict_id() == DICTIONARY_ID
    assert version('wordfreq') == '3.2.0'
    assert direct.get('vcs_info', {}).get('commit_id') == WORDFREQ_COMMIT
    oracle = SourceOracle(native)
    freq = lambda key: wordfreq.zipf_frequency(key, 'pl')
    raw = a.base.read_bytes()
    members, manifest, doc, words, _, _ = read_base(raw, BASE_SHA, DICT_SHA, 11, 3)
    base = {word.lower(): word for word, _ in words}
    assert len(base) == 204463 and len(doc['entries']) == 114299
    doc_before = canonical_bytes(doc)
    pool = CompactPool(doc)
    anchors = {}
    for e in doc['entries']:
        value = freq(e['surfaceKey'])
        if value < 2.5:
            continue
        for r in decode_entry(pool, e).get('metadata', {}).get('sourceEvidence', {}).get('lexicalReadings', []):
            if e['surfaceKey'] in r['surfaces'] and ordinary(dict(tag=r['partOfSpeech'], nameClasses=r.get('nameClasses', []), labels=r.get('labels', []))):
                anchors[r['lemma']] = max(anchors.get(r['lemma'], 0), value)
    bundle = a.bundle.read_bytes()
    assert sha256(bundle) == BUNDLE_SHA
    z = zipfile.ZipFile(io.BytesIO(bundle))
    assert len(z.namelist()) == len(set(z.namelist()))
    lock_raw = z.read('sources/intake-lock.json')
    lock = json.loads(lock_raw)
    source_files = []
    for meta in lock['files']:
        assert Path(meta['path']).name == meta['path']
        data = z.read('sources/' + meta['path'])
        assert len(data) == meta['bytes'] and sha256(data) == meta['sha256']
        source_files.append((meta, json.loads(data)))
    source_maps = dict(zip(('digital-terms', 'apps-and-services'), source_candidates(source_files)))
    grouped = defaultdict(list)
    checks = Counter()
    module_counts = {}
    for module in ('common-families', 'digital-terms', 'apps-and-services'):
        rows = [json.loads(line) for line in z.read('modules/' + module + '/candidates.jsonl').splitlines()]
        assert len(rows) == len({r['surfaceKey'] for r in rows})
        counts = Counter()
        for r in rows:
            key = r['surfaceKey']
            assert key == key.lower()
            assert r['inBase'] == (key in base) and r['keyShape'] == key_shape(key)
            assert r['wordfreqZipfPl'] == freq(key)
            checks['frequencyRevalidated'] += 1
            if module in source_maps:
                assert r['sourceUnits'] == source_maps[module][key]
                assert r['sourceSpellings'] == sorted({s['surface'] for s in r['sourceUnits']})
                checks['sourceUnitsReconstructed'] += 1
            evidence = oracle.evidence(key) if r['keyShape'] == 'single-key' else None
            assert evidence == r['nativeEvidence']
            checks['nativeEvidenceRevalidated'] += evidence is not None
            matching = lexical_matches(key, evidence) if evidence else []
            family = max((anchors.get(x['lemma'], 0) for x in matching), default=0)
            if module == 'common-families':
                assert r['familyZipf'] == family
                assert matching and selected(freq(key), family)
            if r['metadataProposal'] is not None:
                proposal = pool.encode(compact_entry(key, evidence))
                assert proposal == r['metadataProposal']
                assert r['runtimeEstimate'] == dict(nodes=nodes(proposal), bytes=len(canonical_bytes(proposal)))
                checks['metadataProposalsRevalidated'] += 1
            if r['inBase']:
                state, reason = 'excluded', 'already-in-v11'
            elif r['keyShape'] != 'single-key':
                state, reason = 'separate-scope', 'phrase-or-punctuation-not-a-single-key'
            elif module == 'apps-and-services':
                state, reason = 'needs-evidence', 'official-spelling-current-identity-polish-usage-and-metadata-needed'
            elif not matching:
                state, reason = 'needs-evidence', 'no-exact-ordinary-SGJP-proof-not-proof-of-error'
            elif module == 'digital-terms' and key not in r['sourceSpellings']:
                state, reason = 'needs-evidence', 'source-capitalization-not-proven-by-lowercase-SGJP'
            elif not selected(freq(key), family):
                state, reason = 'rejected-this-selection', 'below-existing-frequency-policy-not-a-spelling-rejection'
            else:
                state, reason = 'confirmed', 'exact-SGJP-and-existing-frequency-policy'
            counts[state] += 1
            grouped[key].append(dict(module=module, state=state, reason=reason, familyZipf=family, original=r))
        module_counts[module] = dict(counts)
        print(module, dict(counts), flush=True)
    output = []
    for key, records in sorted(grouped.items()):
        if key in base or records[0]['original']['keyShape'] != 'single-key':
            continue
        states = {r['state'] for r in records}
        # Never let an ordinary homonym silently approve a brand identity.
        if any(r['module'] == 'apps-and-services' for r in records):
            state = 'needs-evidence'
        elif 'confirmed' in states:
            state = 'confirmed'
        elif 'needs-evidence' in states:
            state = 'needs-evidence'
        else:
            state = 'rejected-this-selection'
        proposals = [r['original']['metadataProposal'] for r in records if r['state'] == 'confirmed']
        assert len({canonical_bytes(x) for x in proposals}) <= 1
        output.append(dict(surfaceKey=key, state=state, records=records,
                           approvedMetadata=proposals[0] if state == 'confirmed' else None))
    assert len(output) == 2913
    accepted = [r['approvedMetadata'] for r in output if r['state'] == 'confirmed']
    simulated = deepcopy(doc)
    simulated['entries'] = sorted(simulated['entries'] + accepted, key=lambda x: x['surfaceKey'])
    assert len({e['surfaceKey'] for e in simulated['entries']}) == len(simulated['entries'])
    audit_provenance = dict(candidateBundleSha256=BUNDLE_SHA, basePackSha256=BASE_SHA,
        policy='exact-SGJP; Zipf>=2 or Zipf>=1 and attested-v11-family>=2.5; no branded homonym approval',
        morfeuszVersion=MORFEUSZ_VERSION, sgjpDictionaryId=DICTIONARY_ID,
        wordfreqVersion='3.2.0', wordfreqCommit=WORDFREQ_COMMIT,
        sourceLockSha256=sha256(lock_raw))
    entries_only_bytes = len(serialize(simulated)) - len(members['language-intelligence.json'])
    entries_only_nodes = nodes(simulated) - nodes(doc)
    simulated['provenance']['practicalCandidateAudit'] = audit_provenance
    old_by_key = {e['surfaceKey']: e for e in doc['entries']}
    assert all(e == old_by_key[e['surfaceKey']] for e in simulated['entries'] if e['surfaceKey'] in old_by_key)
    assert canonical_bytes(doc) == doc_before
    total_bytes, total_nodes = len(serialize(simulated)), nodes(simulated)
    assert total_bytes <= 32*1024*1024 and total_nodes <= 2000000 and len(simulated['entries']) <= 120000
    report = dict(basePackSha256=BASE_SHA, candidateBundleSha256=BUNDLE_SHA,
        provenance=audit_provenance, candidateOnly=True, installable=False,
        uniqueSingleKeys=len(output), decisions=dict(Counter(x['state'] for x in output)),
        modules=module_counts, checks=dict(checks),
        cost=dict(entries=len(accepted), entriesOnlyBytes=entries_only_bytes, entriesOnlyNodes=entries_only_nodes,
            withProvenanceBytes=total_bytes-len(members['language-intelligence.json']),
            withProvenanceNodes=total_nodes-nodes(doc),
            totalMetadataEntries=len(simulated['entries']), totalMetadataBytes=total_bytes, totalMetadataNodes=total_nodes,
            remainingEntries=120000-len(simulated['entries']), remainingBytes=32*1024*1024-total_bytes, remainingNodes=2000000-total_nodes),
        limitations=['Confirmation concerns the word/form and preserved SGJP readings, not the technical sense from an index.',
            'Frequency is pinned wordfreq, not a contemporary corpus or Top-3 measurement.',
            'Apps require separate evidence; missing SGJP or frequency is not a spelling rejection.',
            'Cost is an in-memory metadata simulation, not a built/import-tested langpack or Android RAM measurement.'])
    a.out.mkdir(parents=True, exist_ok=False)
    (a.out/'audit-report.json').write_bytes(canonical_bytes(report))
    (a.out/'decisions.jsonl').write_bytes(b''.join(canonical_bytes(x) for x in output))
    for state in report['decisions']:
        (a.out/(state+'.txt')).write_text(''.join(x['surfaceKey']+'\n' for x in output if x['state']==state))
    (a.out/'excluded-and-separate.jsonl').write_bytes(b''.join(canonical_bytes(dict(surfaceKey=k, records=v)) for k,v in sorted(grouped.items()) if k in base or v[0]['original']['keyShape']!='single-key'))
    probes = ['WhatsApp', 'ChatGPT', 'TikTok', 'Discord', 'WiFi', 'powerbank',
              'streamować', 'scrollować', 'googlować', 'messenger', 'bluetooth',
              'smartfon', 'newsletter', 'zaloguję', 'udostępnię']
    (a.out/'coverage-probes.json').write_bytes(canonical_bytes([
        dict(spelling=s, key=s.lower(), inBase=s.lower() in base,
             baseSpelling=base.get(s.lower()), inCandidateMaterial=s.lower() in grouped,
             modules=[r['module'] for r in grouped.get(s.lower(), [])]) for s in probes]))
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
