"""Source-gated form agreement followed by unchanged mean capitalization."""
import math
import re

MAX_PROBES = 2  # fixed before inference, no corpus-dependent tuning
FOLD = str.maketrans('ąćęłńóśźż', 'acelnoszz')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def rank(surfaces, scores):
    require(bool(surfaces) and len(set(surfaces)) == len(surfaces) and
            all(isinstance(s, str) and s for s in surfaces) and set(surfaces) == set(scores), 'score identity')
    require(all(type(v) in (int, float) and math.isfinite(v) for v in scores.values()), 'score finite')
    return sorted(surfaces, key=lambda s: -scores[s])


def source_identities(entry, key):
    evidence = entry.get('metadata', {}).get('sourceEvidence', {})
    result = set()
    for name in ['lexicalReadings', 'generatedFormProofs', 'interpretations']:
        for r in evidence.get(name, []):
            pos = r.get('partOfSpeech') or r.get('tag', '').split(':')[0]
            if r.get('lemma') and pos and (r.get('form', '').lower() == key or
                                          any(s.lower() == key for s in r.get('surfaces', []))):
                result.add((r['lemma'], pos))
    return result


def eligibility(surfaces, entries):
    require(bool(surfaces) and len(set(surfaces)) == len(surfaces), 'surfaces unique')
    keys = list(dict.fromkeys(s.lower() for s in surfaces))
    if len(keys) == 1:
        return 'case_only'
    if len(keys) != 2 or len(surfaces) > 4:
        return 'outside_two_key_four_surface_scope'
    for key in keys:
        if key in entries and not {s for s in surfaces if s.lower() == key} <= {
                v['surface'] for v in entries[key]['capitalization']['variants']}:
            return 'undeclared_variant'
    if keys[0].translate(FOLD) == keys[1].translate(FOLD):
        return 'eligible_fold'
    if all(k in entries for k in keys) and source_identities(entries[keys[0]], keys[0]) & source_identities(entries[keys[1]], keys[1]):
        return 'eligible_source_lemma_pos'
    return 'unrelated_or_unknown_source'


def probes(context):
    require(isinstance(context, str) and len(context) <= 4096 and
            not any(s in context for s in ['<mask>', '<s>', '</s>']), 'context bounds/special tokens')
    # Authored fixtures contain ordinary Polish text. This lexical-span rule is
    # a diagnostic tokenizer contract, not an Android cursor parser.
    spans = [(m.start(), m.end()) for m in re.finditer(r'[^\W\d_]+', context, flags=re.UNICODE)]
    return [dict(start=a, end=b, text=context[a:b]) for a, b in spans[-MAX_PROBES:]]


def prepare(tokenizer, special, context, surfaces, selected=None):
    probes(context)  # enforce context bounds also for explicit validation probes
    selected = probes(context) if selected is None else selected
    require(1 <= len(surfaces) <= 4 and all(isinstance(s, str) and s for s in surfaces) and
            len(set(surfaces)) == len(surfaces) and
            1 <= len(selected) <= MAX_PROBES, 'agreement batch budget')
    rows, labels = [], []
    for i, p in enumerate(selected):
        a, b = p['start'], p['end']
        require(0 <= a < b <= len(context) and context[a:b] == p['text'], 'probe span identity')
        left, target, right = tokenizer.encode(context[:a]), tokenizer.encode(p['text']), tokenizer.encode(context[b:])
        require(left + target + right == tokenizer.encode(context), 'context segment token parity')
        require(1 <= len(target) <= 32 and special['unk'] not in target, 'probe target token budget')
        for surface in surfaces:
            candidate = tokenizer.encode(surface)
            require(1 <= len(candidate) <= 32 and special['unk'] not in candidate and
                    left + target + right + candidate == tokenizer.encode(context + ' ' + surface), 'visible candidate token parity')
            ids = [special['cls']] + left + [special['mask']] * len(target) + right + candidate + [special['sep']]
            require(3 <= len(ids) <= 512, 'agreement sequence budget')
            rows.append(dict(ids=ids, targets=target, positions=list(range(len(left) + 1, len(left) + len(target) + 1))))
            labels.append(f'{i}/{surface}')
    require(len(rows) <= 8, 'two probes times four candidates')
    width, targets = max(len(r['ids']) for r in rows), max(len(r['targets']) for r in rows)
    packed = {k: [] for k in ['input_ids', 'attention_mask', 'target_positions', 'target_ids', 'target_mask']}
    for r in rows:
        pad, absent = width - len(r['ids']), targets - len(r['targets'])
        packed['input_ids'].append(r['ids'] + [special['pad']] * pad)
        packed['attention_mask'].append([1] * len(r['ids']) + [0] * pad)
        packed['target_positions'].append(r['positions'] + [0] * absent)
        packed['target_ids'].append(r['targets'] + [0] * absent)
        packed['target_mask'].append([1.0] * len(r['targets']) + [0.0] * absent)
    return labels, packed, selected


def form_scores(surfaces, scores, probe_count):
    require(1 <= probe_count <= MAX_PROBES and
            set(scores) == {f'{i}/{s}' for i in range(probe_count) for s in surfaces}, 'probe score identity')
    rank(list(scores), scores)
    keys = list(dict.fromkeys(s.lower() for s in surfaces))
    result = {}
    for key in keys:
        variants = [s for s in surfaces if s.lower() == key]
        require(1 <= len(variants) <= 2, 'case alternatives budget')
        pooled = []
        for i in range(probe_count):
            values = [scores[f'{i}/{s}'] for s in variants]
            largest = max(values)
            pooled.append(largest + math.log(sum(math.exp(v - largest) for v in values) / len(values)))
        result[key] = sum(pooled) / probe_count
    rank(keys, result)
    return result


def ordered(surfaces, case_scores, key_scores=None):
    original = rank(surfaces, case_scores)
    keys = list(dict.fromkeys(s.lower() for s in surfaces))
    if key_scores is None:
        keys = list(dict.fromkeys(s.lower() for s in original))
    else:
        keys = rank(keys, key_scores)
    best = [next(s for s in original if s.lower() == key) for key in keys]
    return best + [s for s in original if s not in best]


def ordinal(order):
    require(bool(order) and len(set(order)) == len(order), 'ordinal identity')
    return {s: -i for i, s in enumerate(order)}  # metrics only, never model/geometric scores
