#!/usr/bin/env python3
"""Measure source-attested names/initialisms, then append within API-v1 budgets.

Existing v7 records and metadata are immutable. SGJP exact analysis/generation
proves every new spelling; wordfreq ranks candidates, never establishes spelling.
No guessed suffixes, manually written senses, private exports or trademark dump.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import re

from build_common_forms_trial import (MAX_BYTES, MAX_TOTAL_BYTES, MAX_NODES, MAX_ENTRIES,
    WORDFREQ_COMMIT, NONLEXICAL_POS, OBSOLETE_LABELS, REGRESSION_WORDS,
    parse_dictionary, extend_dictionary)
from build_global_casing_trial import json_nodes
from build_function_word_trial import MORFEUSZ_VERSION, DICTIONARY_ID
from build_variant_trial import canonical_bytes, sha256
from build_thematic_forms_trial import write_pack

BASE_PACK_SHA256 = '3f105ed66661b120a23c0b03cd2571651609c9fd766a4e36c6a264cbe14831df'
BASE_DICTIONARY_SHA256 = '7b081aff64b0c386650ed0f986a570633e2d02af057196b9f63dcde2a1c6c129'
EXCLUSIONS_SHA256 = '2eda1f002aa3b631cbf919d71c43421190531d784d8545d8d6f2cd8c55faccea'
PACK_NAME = 'cleverkeys-pl-names-forms-trial.zip'
COMMON = {'nazwa_pospolita', 'nazwa pospolita'}
TRADE = {'marka', 'nazwa_firmy', 'nazwa_oprogramowania', 'nazwa_języka_programowania'}
TOKEN = re.compile(r'^[a-ząćęłńóśźż]{2,25}$', re.IGNORECASE)
FOREIGN_LANGS = ('en', 'cs', 'sk', 'ru', 'uk', 'de', 'es', 'it', 'fr', 'pt', 'nl')


def candidate(form):
    return bool(TOKEN.fullmatch(form)) and form.isalpha()


def current(reading):
    return (reading['tag'].split(':')[0] not in NONLEXICAL_POS
            and not any(label.startswith(OBSOLETE_LABELS) for label in reading['labels']))


def proper_classes(reading):
    return {n for n in reading['nameClasses'] if n not in COMMON and not n.startswith('człon_')}


def load_exclusions(path):
    raw = path.read_bytes()
    if sha256(raw) != EXCLUSIONS_SHA256:
        raise ValueError('source exclusions checksum')
    return {row['name'] for row in csv.DictReader(raw.decode().splitlines(), delimiter='\t')
            if row['status'] == 'exclude'}


class NameOracle:
    def __init__(self, oracle):
        self.oracle = oracle

    @lru_cache(maxsize=4000)
    def forms(self, lemma):
        return self.oracle.generate(lemma)

    def evidence(self, key):
        # Uppercase probing is NOT evidence: exact generator forms must match.
        probes = {key, key[:1].upper() + key[1:], key.upper()}
        interpretations, proofs = {}, {}
        for probe in sorted(probes):
            for start, end, payload in self.oracle.analyse(probe):
                if (start, end) != (0, 1) or len(payload) < 5:
                    continue
                orth, lemma, tag, names, labels = payload[:5]
                source = dict(lemma=lemma, tag=tag, nameClasses=sorted(set(names)), labels=sorted(set(labels)))
                if orth != probe or tag.split(':')[0] in {'ign', 'interp'}:
                    continue
                rid = sha256(canonical_bytes(source))[:16]
                for form, gen_lemma, gen_tag, gen_names, gen_labels in self.forms(lemma):
                    if (form not in probes or gen_lemma != lemma or gen_tag != tag
                            or sorted(set(gen_names)) != source['nameClasses']
                            or sorted(set(gen_labels)) != source['labels']):
                        continue
                    interpretations[rid] = dict(id=rid, **source)
                    proof = dict(form=form, interpretationId=rid, tag=gen_tag,
                                 nameClasses=sorted(set(gen_names)), labels=sorted(set(gen_labels)))
                    proofs[canonical_bytes(proof)] = proof
        return dict(interpretations=sorted(interpretations.values(), key=lambda r: r['id']),
                    generatedFormProofs=[proofs[p] for p in sorted(proofs)])


def admissions(key, evidence, exclusions):
    by_id = {r['id']: r for r in evidence['interpretations']}
    result = []
    for proof in evidence['generatedFormProofs']:
        r = by_id[proof['interpretationId']]
        if not current(r) or r['lemma'].split(':')[0] in exclusions:
            continue
        groups = set()
        names = proper_classes(r)
        if names & TRADE: groups.add('brands_and_software')
        if proof['form'] == key.upper(): groups.add('initialisms')
        if names and not names <= TRADE: groups.add('proper_names')
        if groups: result.append((r, proof, groups))
    return result


def entry(key, evidence, zipf=lambda w: 0):
    by_id = {r['id']: r for r in evidence['interpretations']}
    spellings = sorted({p['form'] for p in evidence['generatedFormProofs']})
    ordinary_lower = any(p['form'] == key and current(by_id[p['interpretationId']])
                         and not (set(by_id[p['interpretationId']]['nameClasses']) - COMMON)
                         for p in evidence['generatedFormProofs'])
    title = key[:1].upper() + key[1:]
    # A frequent case of Jan must not lose to a JANA institution merely because
    # its acronym exists. Compare attested lexical-family anchors, not letter case.
    preferred = sorted((p for p in evidence['generatedFormProofs']
                        if current(by_id[p['interpretationId']])),
        key=lambda p: (-zipf(by_id[p['interpretationId']]['lemma'].split(':')[0]),
                       p['form'] != title, p['form']))
    default = key if ordinary_lower else preferred[0]['form'] if preferred else title
    if default not in spellings: raise ValueError('no canonical source spelling')
    rows = {}
    for proof in evidence['generatedFormProofs']:
        source = by_id[proof['interpretationId']]
        reading = dict(lemma=source['lemma'], partOfSpeech=source['tag'].split(':')[0])
        for field in ('nameClasses', 'labels'):
            if source[field]: reading[field] = source[field]
        identity = canonical_bytes(reading)
        row = rows.setdefault(identity, dict(**reading, surfaces=set()))
        row['surfaces'].add(proof['form'])
    readings = [dict(**{k: v for k, v in rows[i].items() if k != 'surfaces'},
                     surfaces=sorted(rows[i]['surfaces'])) for i in sorted(rows)]
    identities = {(r['lemma'], r['partOfSpeech']) for r in readings}
    if not identities or len(identities) > 32: raise ValueError('source identity budget')
    value = dict(surfaceKey=key, metadata=dict(sourceEvidence=dict(lexicalReadings=readings)))
    # API-v1 supports lower/title only. All-caps stays exact in CKDT/canonicalForm;
    # source readings keep other attestations without fabricating case policies.
    if default != key: value['canonicalForm'] = default
    if len(spellings) == 2 and set(spellings) == {key, title}:
        value['canonicalForm'] = default
        value['capitalization'] = dict(defaultSurface=default, variants=[
            dict(surface=s, casePolicy='lowercase' if s == key else 'capitalized')
            for s in sorted(spellings, key=lambda s: (s != default, s))])
    return default, value


def read_base(raw, expected_sha256=BASE_PACK_SHA256, expected_dictionary=BASE_DICTIONARY_SHA256):
    # Validate the pinned v7 archive before admitting any new source family.
    import io, zipfile
    from build_variant_trial import read_json
    if len(raw) > MAX_TOTAL_BYTES or sha256(raw) != expected_sha256: raise ValueError('base checksum/size')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names = z.namelist()
        if len(names) != len(set(names)) or set(names) != {'dictionary.bin', 'manifest.json',
                'language-intelligence.json', 'unigrams.txt', 'NOTICE.txt'}: raise ValueError('base members')
        if any(i.file_size > MAX_BYTES for i in z.infolist()) or sum(i.file_size for i in z.infolist()) > MAX_TOTAL_BYTES:
            raise ValueError('base decompression budget')
        members = {n: z.read(n) for n in names}
    if sha256(members['dictionary.bin']) != expected_dictionary: raise ValueError('base dictionary checksum')
    records, aliases, boundary = parse_dictionary(members['dictionary.bin'])
    manifest, side = read_json(members['manifest.json']), read_json(members['language-intelligence.json'])
    if (manifest.get('code') != 'pl' or manifest.get('version') != 7 or manifest.get('apiVersion') != 1
            or manifest.get('wordCount') != len(records) or side.get('languageCode') != 'pl'
            or side.get('schemaVersion') != 1 or manifest.get('languageIntelligence', {}).get('sha256')
            != sha256(members['language-intelligence.json'])): raise ValueError('base identity')
    canonical = {w.lower(): w for w, _ in records}
    entries = side['entries']
    if len({e['surfaceKey'] for e in entries}) != len(entries) or any(e['surfaceKey'] not in canonical or
            ('canonicalForm' in e and e['canonicalForm'] != canonical[e['surfaceKey']]) for e in entries):
        raise ValueError('base sidecar identity')
    return members, manifest, side, records, aliases, boundary


def build(base_raw, out, oracle, ranked_words, zipf, frequency, exclusions, provenance,
          expected_sha256=BASE_PACK_SHA256, expected_dictionary=BASE_DICTIONARY_SHA256,
          foreign_zipf=None):
    members, manifest, side, old, aliases, boundary = read_base(base_raw, expected_sha256, expected_dictionary)
    out.mkdir(parents=True, exist_ok=True)
    if (out / PACK_NAME).exists(): raise ValueError('output already contains installable pack')
    base_keys = {w.lower() for w, _ in old}
    source = NameOracle(oracle)
    families = set(); seeds = Counter(); digest = hashlib.sha256()
    with (out / 'name-seed-audit.jsonl').open('wb') as sink:
        for index, key in enumerate(ranked_words):
            if not candidate(key) or key != key.lower(): raise ValueError('invalid corpus candidate')
            if key in base_keys: continue
            evidence = source.evidence(key); eligible = admissions(key, evidence, exclusions)
            families.update(r['lemma'] for r, _, _ in eligible)
            reason = 'attested-name-or-initialism' if eligible else 'no-current-whole-name-proof'
            seeds[reason] += 1
            row = canonical_bytes(dict(surfaceKey=key, corpusRank=index, reason=reason, **evidence))
            sink.write(row); digest.update(row)
            if sum(seeds.values()) % 25000 == 0: print(f'Name seeds audited: {sum(seeds.values())}; families={len(families)}', flush=True)
    candidates = set()
    for lemma in sorted(families):
        for form, gen_lemma, tag, names, labels in source.forms(lemma):
            if gen_lemma == lemma and candidate(form): candidates.add(form.lower())
    qualified = []; decisions = Counter(); measured_groups = Counter(); audit_digest = hashlib.sha256()
    for key in sorted(candidates - base_keys):
        evidence = source.evidence(key)
        eligible = [item for item in admissions(key, evidence, exclusions) if item[0]['lemma'] in families]
        if not eligible: decisions['no-current-linked-family-proof'] += 1; continue
        try: surface, metadata = entry(key, evidence, zipf)
        except ValueError: decisions['source-identity-budget'] += 1; continue
        groups = sorted({g for _, _, gs in eligible for g in gs})
        value = zipf(key)
        foreign = max(((foreign_zipf(key, lang), lang) for lang in FOREIGN_LANGS), default=(0, '')) if foreign_zipf else (0, '')
        # Keep measured category data. Filter surname/foreign-word collisions
        # before capacity selection; confirmed trade names/initialisms are separate.
        foreign_dominant = (key.isascii() and groups == ['proper_names']
                            and foreign[0] >= 3.0 and foreign[0] > value + 1.0)
        qualified.append(dict(surfaceKey=key, surface=surface, entry=metadata, groups=groups,
                              zipf=value, foreign=foreign, foreignDominant=foreign_dominant, evidence=evidence))
        measured_groups.update(groups)
    # Measure the whole source category first. Capacity is the actual remaining
    # API-v1 metadata space, never a reason to remove an existing word.
    side['provenance']['namesFormsExpansion'] = dict(inputPackSha256=sha256(base_raw), **provenance)
    nodes = json_nodes(side); bytes_used = len(canonical_bytes(side)); count = len(side['entries'])
    measured_nodes = sum(json_nodes(r['entry']) for r in qualified)
    measured_bytes = sum(len(canonical_bytes(r['entry'])) for r in qualified)
    qualified.sort(key=lambda r: ('brands_and_software' not in r['groups'], 'initialisms' not in r['groups'],
                                  -r['zipf'], r['surfaceKey']))
    retained = []; covered = Counter(); max_freq = max(frequency(w) for w, _ in old)
    with (out / 'name-forms-audit.jsonl').open('wb') as sink:
        for row in qualified:
            cost = json_nodes(row['entry']); byte_cost = len(canonical_bytes(row['entry']))
            fits = nodes + cost <= MAX_NODES and bytes_used + byte_cost <= MAX_BYTES and count < MAX_ENTRIES
            accepted = fits and not row['foreignDominant']
            reason = ('foreign-word-name-collision' if row['foreignDominant'] else
                      'source-attested-addition' if accepted else 'measured-runtime-capacity')
            decisions[reason] += 1
            if accepted:
                nodes += cost; bytes_used += byte_cost; count += 1; covered.update(row['groups'])
                f = frequency(row['surfaceKey'])
                rank = max(0, min(255, int((1 - math.log(f + 1) / math.log(max_freq + 1)) * 255)))
                retained.append((row['surface'], rank, row['entry']))
            audit = canonical_bytes(dict(surfaceKey=row['surfaceKey'], canonicalForm=row['surface'],
                groups=row['groups'], zipf=row['zipf'], runtimeNodes=cost, accepted=accepted, reason=reason,
                foreignZipf=row['foreign'][0], foreignLanguage=row['foreign'][1],
                **row['evidence']))
            sink.write(audit); audit_digest.update(audit)
    if not retained: raise ValueError('empty additions')
    binary = extend_dictionary(members['dictionary.bin'], old, aliases, boundary,
        [(word, rank) for word, rank, _ in retained], frequency)
    old_entries = {e['surfaceKey']: e for e in side['entries']}
    side['entries'] = sorted(side['entries'] + [e for _, _, e in retained], key=lambda e: e['surfaceKey'])
    updated = {e['surfaceKey']: e for e in side['entries']}
    if len(updated) != len(side['entries']) or any(updated[k] != e for k, e in old_entries.items()):
        raise ValueError('old source metadata changed/duplicate new key')
    side['provenance']['dictionarySha256'] = sha256(binary)
    side_bytes = canonical_bytes(side); node_count = json_nodes(side)
    if len(side_bytes) > MAX_BYTES or node_count > MAX_NODES or len(updated) > MAX_ENTRIES: raise ValueError('output metadata budget')
    manifest.update(version=8, wordCount=len(old) + len(retained))
    manifest['languageIntelligence']['sha256'] = sha256(side_bytes)
    notice = ('\nAdditive names/initialisms trial v8. All v7 words/ranks/metadata retained.\n'
              'Source: pinned Morfeusz2/SGJP exact analysis and generation, https://morfeusz.sgjp.pl/doc/about/\n'
              'Selection/ranks: pinned wordfreq. Full category measured, then retained within existing API-v1 limits.\n'
              'Only source-attested whole alphabetic forms; no guessed declension, case policy or meaning.\n'
              'All-caps initialisms keep exact CKDT spelling; no unsupported capitalization policy is emitted.\n')
    members.update({'dictionary.bin': binary, 'language-intelligence.json': side_bytes,
                    'manifest.json': canonical_bytes(manifest), 'NOTICE.txt': members['NOTICE.txt'] + notice.encode()})
    if any(len(v) > MAX_BYTES for v in members.values()) or sum(map(len, members.values())) > MAX_TOTAL_BYTES:
        raise ValueError('output archive budget')
    package = write_pack(members)
    report = dict(trialOnly=True, packVersion=8, before=len(old), added=len(retained), after=len(old)+len(retained),
        removed=0, changedOldRanks=0, changedOldCanonicalRecords=0, changedOldMetadataEntries=0,
        corpusCandidateKeys=len(ranked_words), seedDecisions=dict(seeds), sourceFamilies=len(families),
        generatedCandidateKeys=len(candidates), alreadyCoveredCandidateKeys=len(candidates & base_keys),
        qualifiedNewKeys=len(qualified), fullMeasuredGroupCoverageOverlapping=dict(measured_groups),
        fullMeasuredAdditionalNodes=measured_nodes, fullMeasuredAdditionalBytes=measured_bytes,
        candidateDecisions=dict(decisions), addedGroupCoverageOverlapping=dict(covered),
        runtimeEntries=len(updated), runtimeBytes=len(side_bytes), runtimeJsonNodes=node_count,
        remainingConsumerNodes=MAX_NODES-node_count, requiredConsumerNodeBudget=MAX_NODES,
        packageSha256=sha256(package), dictionarySha256=sha256(binary), languageIntelligenceSha256=sha256(side_bytes),
        unigramsSha256=sha256(members['unigrams.txt']), seedAuditSha256=digest.hexdigest(),
        auditSha256=audit_digest.hexdigest(), sources=provenance,
        regressions={k: k in base_keys or k in updated for k in REGRESSION_WORDS},
        limitations=['No independent swipe accuracy or phone PSS measurement.',
            'SGJP coverage only: unsupported apps, modern brands and punctuation forms require separate databases.',
            'NAME is source classification, not a manually written semantic definition or current trademark registry.',
            'Existing key surfaces/metadata are immutable; existing lower/acronym collisions are not rewritten.',
            'All-caps spelling is canonical only; API-v1 lower/title alternatives remain unchanged.',
            'Capacity deferrals retain full source proof in audit; no old entry is removed.'])
    (out / 'names-forms-report.json').write_bytes(canonical_bytes(report))
    (out / PACK_NAME).write_bytes(package)
    (out / 'cleverkeys-pl-names-forms-trial.sha256').write_text(sha256(package)+'  '+PACK_NAME+'\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-pack', type=Path, required=True)
    parser.add_argument('--out-dir', type=Path, required=True)
    args = parser.parse_args()
    import morfeusz2, wordfreq
    from importlib.metadata import version, distribution
    oracle = morfeusz2.Morfeusz(case_handling=morfeusz2.CONDITIONALLY_CASE_SENSITIVE)
    direct = json.loads(distribution('wordfreq').read_text('direct_url.json') or '{}')
    if (str(morfeusz2.__version__) != MORFEUSZ_VERSION or oracle.dict_id() != DICTIONARY_ID
            or version('wordfreq') != '3.2.0' or direct.get('vcs_info', {}).get('commit_id') != WORDFREQ_COMMIT):
        raise ValueError('source snapshot differs from pinned build')
    words, seen = [], set()
    for raw in wordfreq.iter_wordlist('pl'):
        key = raw.lower()
        if key in seen or not candidate(key): continue
        seen.add(key); words.append(key)
        if len(words) == 300000: break
    exclusions = load_exclusions(Path(__file__).resolve().parents[1] / 'sources/staging/first_name_source_exclusions.tsv')
    provenance = dict(morfeuszVersion=MORFEUSZ_VERSION, sgjpDictionaryId=DICTIONARY_ID,
        wordfreqVersion='3.2.0', wordfreqCommit=WORDFREQ_COMMIT, candidateLimit=300000,
        sourceExclusionsSha256=EXCLUSIONS_SHA256, foreignCollisionLanguages=list(FOREIGN_LANGS),
        foreignCollisionMinZipf=3.0, foreignCollisionMargin=1.0)
    report = build(args.base_pack.read_bytes(), args.out_dir, oracle, words,
        lambda w: wordfreq.zipf_frequency(w, 'pl'),
        lambda w: max(1.0, wordfreq.word_frequency(w, 'pl') * 1e8), exclusions, provenance,
        foreign_zipf=wordfreq.zipf_frequency)
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__': main()
