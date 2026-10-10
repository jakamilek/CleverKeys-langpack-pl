"""Context gain probe of the unchanged graph, frozen before real inference."""
import argparse
import json
import os
import sys
from pathlib import Path

from policy import context_gain, evaluate

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'herbert_form_diagnostic_v2'))
import replay as v2
v1 = v2.v1
PROTOCOL = 'herbert-context-gain-v3'


def validate_new_cases(payload, source, old_contexts):
    v1.require(payload['schemaVersion'] == 1 and payload['contextWords'] == 32, 'new case schema')
    cases = payload['cases']
    v1.require(len(cases) == 24 and {c['id'] for c in cases} ==
               {f'gain-case-{i:02}' for i in range(1, 25)}, 'new case identities')
    entries = {e['surfaceKey']: e for e in source['entries']}
    families = {}
    contexts = set()
    for c in cases:
        key = c['candidateKey']
        v1.require(key in entries, 'missing source key')
        declared = [v['surface'] for v in entries[key]['capitalization']['variants']]
        v1.require(c['surfaces'] == declared and len(declared) == len(set(declared)) == 2 and
                   {s.lower() for s in declared} == {key} and c['gold'] in declared, 'source surfaces/gold')
        context = c['context']
        v1.require(context.endswith(' ') and 1 <= len(context.split()) <= 32 and
                   len(context) <= 4096 and not any(s in context for s in ['<mask>', '<s>', '</s>']) and
                   context.strip() not in old_contexts and context.strip() not in contexts, 'new context overlap/budget')
        contexts.add(context.strip())
        family = families.setdefault(key, dict(cases=0, upper=0))
        family['cases'] += 1
        family['upper'] += c['gold'][0].isupper()
    v1.require(len(families) == 6 and all(g == dict(cases=4, upper=2) for g in families.values()), 'balanced six families')
    return cases


def verify_freeze():
    freeze = v1.read(ROOT / 'freeze-manifest.json')
    v1.require(freeze['protocol'] == PROTOCOL and freeze['createdBeforeInference'] is True, 'v3 freeze protocol')
    for path, expected in freeze['files'].items():
        v1.require(v1.sha(ROOT / path) == expected, 'v3 freeze mismatch: ' + path)
    v2.verify_freeze()
    old = v1.read(ROOT.parent / 'herbert_form_diagnostic_results/2026-10-10-v2/scores.json')
    first = v1.read(ROOT.parent / 'herbert_form_diagnostic_v1/cases.json')
    old_contexts = {r['context'].strip() for r in old['predictions']} | {r['context'].strip() for r in first['cases']}
    validate_new_cases(v1.read(ROOT / 'new-cases.json'),
                       v1.read(ROOT.parent / 'ai_compare_v5/source-snapshot.json'), old_contexts)
    return freeze


def check_reproduction(fresh, archived):
    v1.require(len(fresh) == len(archived) == 232 and
               len({r['id'] for r in fresh}) == 232, 'historical reproduction completeness')
    refs = {r['id']: r for r in archived}
    v1.require(set(refs) == {r['id'] for r in fresh}, 'historical reproduction IDs')
    for r in fresh:
        old = refs[r['id']]
        for k in ['caseId', 'context', 'suite', 'population', 'window', 'surfaces', 'gold', 'targetTokenCounts']:
            v1.require(r[k] == old[k], 'historical reproduction identity: ' + k)
        for k in ['meanScores', 'sumScores']:
            v1.require(set(r[k]) == set(old[k]) and
                       max(abs(r[k][s] - old[k][s]) for s in r['surfaces']) <= .001 and
                       v1.rank(r['surfaces'], r[k]) == v1.rank(r['surfaces'], old[k]), 'historical reproduction scores/ranks')


def check_neutral_targets(packed, contextual):
    for key in ['target_ids', 'target_mask']:
        v1.require(packed[key] == contextual[key], 'neutral target identity: ' + key)


def run(bundle, out):
    freeze = verify_freeze()
    bundle, out = Path(bundle), Path(out)
    # Re-run every original trust/token/feed/score gate. Archived outputs are
    # reproduction checks only; gain uses actual outputs from this run.
    v2.run(bundle, out / 'replay')
    history = v1.read(out / 'replay/scores.json')['predictions']
    check_reproduction(history, v1.read(ROOT.parent / 'herbert_form_diagnostic_results/2026-10-10-v2/scores.json')['predictions'])
    forms = v1.read(out / 'replay/fresh24/scores.json')['predictions']
    cases = v1.read(ROOT / 'new-cases.json')['cases']
    sys.path.insert(0, str(ROOT.parent / 'herbert_fp32_benchmark_v1'))
    from portable import PortableTokenizer
    import numpy as np
    import onnxruntime as ort
    from tokenizers import Tokenizer
    tables = v1.read(bundle / 'portable-tokenizer.json')
    tokenizer, special = PortableTokenizer(tables), tables['specialTokenIds']
    fast = Tokenizer.from_file(str(bundle / 'tokenizer.json'))
    for text in [''] + [s for c in cases for s in [c['context']] + c['surfaces']]:
        v1.require(tokenizer.encode(text) == fast.encode(text, add_special_tokens=False).ids, 'new/empty tokenizer parity')
    v1.require(tokenizer.encode('') == [], 'neutral context not empty')
    options = ort.SessionOptions()
    options.intra_op_num_threads, options.inter_op_num_threads = 2, 1
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    session = ort.InferenceSession(str(bundle / 'model.onnx'), sess_options=options, providers=['CPUExecutionProvider'])
    v1.require(ort.__version__ == '1.21.1' and tuple(i.name for i in session.get_inputs()) == v1.INPUTS and
               tuple(o.name for o in session.get_outputs()) == v1.OUTPUTS, 'graph/runtime signature')
    calls, single_error = 0, 0.0

    def score(surfaces, packed):
        nonlocal calls
        feed = {k: np.asarray(v, dtype=np.float32 if k == 'target_mask' else np.int64) for k, v in packed.items()}
        means, sums = session.run(list(v1.OUTPUTS), feed)
        calls += 1
        return v1.check_scores(surfaces, packed, means, sums)

    neutral_cache, single_cache, neutral_reports = {}, {}, []

    def neutral(surfaces, contextual_pack):
        nonlocal single_error
        key = tuple(surfaces)
        if key not in neutral_cache:
            packed = v1.prepare(tokenizer, special, '', surfaces)
            means, sums = score(surfaces, packed)
            for s in surfaces:
                if s not in single_cache:
                    single_cache[s] = score([s], v1.prepare(tokenizer, special, '', [s]))
                for candidate, reference in zip((means, sums), single_cache[s]):
                    error = abs(candidate[s] - reference[s])
                    single_error = max(single_error, error)
                    v1.require(error <= .001, 'neutral single/batched parity')
            record = dict(id=f'neutral-{len(neutral_reports):03}', context='', surfaces=surfaces,
                          inputs=packed, meanScores=means, sumScores=sums,
                          targetTokenIds={s: tokenizer.encode(s) for s in surfaces})
            neutral_cache[key] = record
            neutral_reports.append(record)
        record = neutral_cache[key]
        # Baseline MUST score identical target IDs/masks, even when a word has
        # a different token count from another capitalization of that word.
        check_neutral_targets(record['inputs'], contextual_pack)
        return record

    original_vectors = {v['id']: v for v in v1.read(bundle / 'android-score-vectors.json')['vectors']}
    scored = []

    def append(row, packed):
        n = neutral(row['surfaces'], packed)
        row = dict(row, neutralId=n['id'],
                   gainScores=context_gain(row['surfaces'], row['sumScores'], n['sumScores']),
                   targetTokenIds={s: tokenizer.encode(s) for s in row['surfaces']})
        scored.append(row)

    for row in history:
        append(dict(row, dataset='history'), original_vectors[row['id']]['inputs'])
    for row in forms:
        append(dict(id='form24/' + row['id'], dataset='form24', context=row['context'],
                    suite='form24', population=row['origin'], window=row['group'],
                    surfaces=row['surfaces'], gold=row['gold'], meanScores=row['scores'],
                    sumScores=row['sumScores'], targetTokenCounts=[int(sum(m)) for m in row['inputs']['target_mask']]), row['inputs'])
    for c in cases:
        packed = v1.prepare(tokenizer, special, c['context'], c['surfaces'])
        means, sums = score(c['surfaces'], packed)
        for s in c['surfaces']:
            a, b = score([s], v1.prepare(tokenizer, special, c['context'], [s]))
            for candidate, reference in [(means, a), (sums, b)]:
                error = abs(candidate[s] - reference[s])
                single_error = max(single_error, error)
                v1.require(error <= .001, 'new-context single/batched parity')
        append(dict(id=c['id'], dataset='new24', context=c['context'],
                    suite='new24', population=c['candidateKey'], window='short',
                    surfaces=c['surfaces'], gold=c['gold'], meanScores=means, sumScores=sums,
                    inputs=packed, targetTokenCounts=[int(sum(m)) for m in packed['target_mask']]), packed)
    v1.require(len(scored) == len({r['id'] for r in scored}) == 280, 'v3 all requests')
    results = {d: evaluate([r for r in scored if r['dataset'] == d]) for d in ['history', 'form24', 'new24']}
    report = dict(protocol=PROTOCOL, codeCommit=os.environ.get('GITHUB_SHA', 'local-unpublished'),
                  formula='sum(context, same surface) - sum(empty context, same surface)',
                  frozenInputs=freeze, modelSha256=v1.TRUST['model.onnx'][1],
                  results=results, predictions=scored, neutralBatches=neutral_reports,
                  extraNativeCalls=calls, maxSingleBatchScoreError=single_error,
                  allPreservationPassed=all(r['preservationPassed'] for r in results.values()),
                  limitations=['A score difference is not calibrated probability or a true likelihood ratio',
                               'Frozen/authored gold is not independent blinded evaluation',
                               'New24 is a capitalization challenge using six known source families; new contexts, not unseen vocabulary',
                               'Form24 has only existing four form families; no broad morphological accuracy claim',
                               'Empty context changes target position and sentence-start prior; subtraction may remove useful frequency information',
                               'Host direct inference, not phone route/latency or whole-strip Top3',
                               'Diagnostic only; no live scorer, APK, model, langpack or threshold change'])
    (out / 'scores.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# HerBERT — wpływ kontekstu V3', '',
             'Metoda: sum(context) − sum(empty) dla tej samej pisowni i tych samych tokenów.',
             f"allPreservationPassed={report['allPreservationPassed']}. Wynik diagnostyczny; aplikacja bez zmian.", '',
             '| Zbiór / grupa | Gold | Mean Top1 | Gain Top1 | Naprawy | Regresje | Regresje Top3 | Formy: mean→gain / eligible | Case przy gold form: mean→gain / eligible |',
             '|---|---:|---:|---:|---:|---:|---:|---|---|']
    for dataset, result in results.items():
        for key, g in result['groups'].items():
            lines.append(f"| {dataset}/{key} | {g['labelled']} | {g['meanTop1']} | {g['gainTop1']} | {g['repairs']} | {g['regressions']} | {g['top3Regressions']} | {g['meanFormTop1']}→{g['gainFormTop1']} / {g['formComparable']} | {g['meanCaseGivenGoldForm']}→{g['gainCaseGivenGoldForm']} / {g['caseComparable']} |")
    lines += ['', 'Wszystkie scores, tokeny, neutral feeds i zmiany w scores.json.',
              'Preservation wymaga zero regresji exact Top1, raw Top3, formy i case w każdej grupie. SUCCESS CI oznacza wykonanie pomiaru, nie zatwierdzenie metody.']
    (out / 'SUMMARY.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'HerBERT context gain: 232 historical + 24 forms + 24 new-case paired measurements; {len(neutral_reports)} neutral batches; single/batched PASS')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract-only', action='store_true')
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.contract_only:
        verify_freeze()
        print('HerBERT context gain: transitive freeze, balanced new cases and source surfaces PASS')
    else:
        v1.require(args.bundle is not None and args.out is not None, 'bundle/out required')
        run(args.bundle, args.out)
