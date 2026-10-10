"""Frozen two-stage host diagnostic; no Android or production scorer change."""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import agreement as algorithm
from source import extract, canonical, needed_keys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'herbert_form_diagnostic_v2'))
import replay as v2
v1 = v2.v1
sys.path.insert(0, str(ROOT.parent / 'herbert_context_gain_v3'))
import policy as metrics
PROTOCOL = 'herbert-agreement-v4'


def validate_cases(payload, fixture, old_contexts):
    v1.require(payload['schemaVersion'] == 1 and payload['contextWords'] == 32, 'case schema')
    cases = payload['cases']
    v1.require(len(cases) == 24 and {c['id'] for c in cases} ==
               {f'agree-form-{i:02}' for i in range(1, 25)}, 'new form identities')
    entries = {e['surfaceKey']: e for e in fixture['entries']}
    groups, seen = {}, set()
    for c in cases:
        keys, surfaces = c['keys'], c['surfaces']
        v1.require(len(keys) == 2 and len(set(keys)) == 2 and c['familyKey'] == keys[0] and
                   all(k in entries for k in keys) and surfaces == [v['surface'] for key in keys
                   for v in entries[key]['capitalization']['variants']] and c['gold'] in surfaces and
                   algorithm.eligibility(surfaces, entries).startswith('eligible_') and
                   bool(algorithm.source_identities(entries[keys[0]], keys[0]) &
                        algorithm.source_identities(entries[keys[1]], keys[1])), 'new source-backed forms')
        context = c['context']
        v1.require(context.endswith(' ') and 1 <= len(context.split()) <= 32 and
                   context.strip() not in old_contexts | seen and len(algorithm.probes(context)) == 2, 'new context eligibility/overlap')
        seen.add(context.strip())
        g = groups.setdefault(c['familyKey'], [])
        g.append(c['gold'])
    v1.require(len(groups) == 6 and all(len(g) == 4 and len(set(g)) == 4 for g in groups.values()), 'balanced new form families')
    return cases


def verify_freeze():
    frozen = v1.read(ROOT / 'freeze-manifest.json')
    v1.require(frozen['protocol'] == PROTOCOL and frozen['createdBeforeInference'] is True, 'v4 freeze')
    for name, expected in frozen['files'].items():
        v1.require(v1.sha(ROOT / name) == expected, 'v4 file hash: ' + name)
    old_root = ROOT.parent / 'herbert_context_gain_v3'
    old = v1.read(old_root / 'freeze-manifest.json')
    v1.require(old['protocol'] == 'herbert-context-gain-v3' and old['createdBeforeInference'] is True, 'v3 freeze protocol')
    for name, expected in old['files'].items():
        v1.require(v1.sha(old_root / name) == expected, 'v3 file hash: ' + name)
    v2.verify_freeze()
    archived = v1.read(ROOT.parent / 'herbert_form_diagnostic_results/2026-10-10-v3/scores.json')
    validate_cases(v1.read(ROOT / 'new-forms.json'), v1.read(ROOT / 'source-fixture.json'),
                   {r['context'].strip() for r in archived['predictions']})
    return frozen


def percentile(values, fraction):
    if not values:
        return None
    import math
    return sorted(values)[max(0, math.ceil(len(values) * fraction) - 1)]


def run(bundle, pack, out):
    frozen = verify_freeze()
    v1.require(canonical(extract(pack, needed_keys())) == (ROOT / 'source-fixture.json').read_bytes(), 'actual source re-extraction')
    bundle, out = Path(bundle), Path(out)
    v2.run(bundle, out / 'replay')
    previous = v1.read(ROOT.parent / 'herbert_form_diagnostic_results/2026-10-10-v3/scores.json')
    archived = {r['id']: r for r in previous['predictions']}
    history = v1.read(out / 'replay/scores.json')['predictions']
    forms = v1.read(out / 'replay/fresh24/scores.json')['predictions']
    sys.path.insert(0, str(ROOT.parent / 'herbert_fp32_benchmark_v1'))
    from portable import PortableTokenizer
    import numpy as np
    import onnxruntime as ort
    from tokenizers import Tokenizer
    tables = v1.read(bundle / 'portable-tokenizer.json')
    tokenizer, special = PortableTokenizer(tables), tables['specialTokenIds']
    fast = Tokenizer.from_file(str(bundle / 'tokenizer.json'))
    opts = ort.SessionOptions()
    opts.intra_op_num_threads, opts.inter_op_num_threads = 2, 1
    opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    session = ort.InferenceSession(str(bundle / 'model.onnx'), sess_options=opts, providers=['CPUExecutionProvider'])
    v1.require(ort.__version__ == '1.21.1' and tuple(i.name for i in session.get_inputs()) == v1.INPUTS and
               tuple(o.name for o in session.get_outputs()) == v1.OUTPUTS, 'actual graph signature')
    fixture = v1.read(ROOT / 'source-fixture.json')
    entries = {e['surfaceKey']: e for e in fixture['entries']}
    calls, max_error = 0, 0.0

    def score(labels, packed):
        nonlocal calls
        began = time.perf_counter()
        feed = {k: np.asarray(v, dtype=np.float32 if k == 'target_mask' else np.int64) for k, v in packed.items()}
        mean, total = session.run(list(v1.OUTPUTS), feed)
        calls += 1
        scores = v1.check_scores(labels, packed, mean, total)
        return scores, (time.perf_counter() - began) * 1000

    def token_parity(strings):
        for text in strings:
            v1.require(tokenizer.encode(text) == fast.encode(text, add_special_tokens=False).ids, 'new tokenizer parity')

    work = []
    for r in history:
        work.append(dict(r, dataset='history'))
    for r in forms:
        work.append(dict(id='form24/' + r['id'], dataset='form24', context=r['context'], surfaces=r['surfaces'],
                         gold=r['gold'], suite='form24', population=r['origin'], window=r['group'],
                         meanScores=r['scores'], sumScores=r['sumScores']))
    controls = v1.read(ROOT.parent / 'herbert_context_gain_v3/new-cases.json')['cases']
    holdout = v1.read(ROOT / 'new-forms.json')['cases']
    for dataset, cases in [('caseControl24', controls), ('newForms24', holdout)]:
        for c in cases:
            surfaces = c['surfaces']
            token_parity([c['context']] + surfaces)
            (means, sums), elapsed = score(surfaces, v1.prepare(tokenizer, special, c['context'], surfaces))
            work.append(dict(id=(('case24/' + c['id']) if dataset == 'caseControl24' else c['id']), dataset=dataset,
                             context=c['context'], surfaces=surfaces, gold=c['gold'], suite=dataset,
                             population=c.get('familyKey', c.get('candidateKey')), window='short',
                             meanScores=means, sumScores=sums, baselineBatchHostMs=elapsed))
    rows = []
    for r in work:
        r = dict(r)
        surfaces, context, baseline = r['surfaces'], r['context'], r['meanScores']
        if r['dataset'] != 'newForms24':
            old_id = r['id'].removeprefix('case24/')
            old = archived[old_id]
            for k in ['context', 'surfaces', 'gold']:
                v1.require(r[k] == old[k], 'earlier identity')
            v1.require(max(abs(baseline[s] - old['meanScores'][s]) for s in surfaces) <= .001 and
                       v1.rank(surfaces, baseline) == v1.rank(surfaces, old['meanScores']), 'earlier mean reproduction')
        status = algorithm.eligibility(surfaces, entries)
        r['agreementEligibility'] = status
        before_presentation = algorithm.ordered(surfaces, baseline)
        stage_scores, case_scores = None, baseline
        if status.startswith('eligible_'):
            selected = algorithm.probes(context)
            if not selected:
                r['agreementEligibility'] = 'no_lexical_context'
            else:
                pipeline_began = time.perf_counter()
                labels, packed, selected = algorithm.prepare(tokenizer, special, context, surfaces, selected)
                token_parity([context] + [context[:p['start']] for p in selected] +
                             [p['text'] for p in selected] + [context[p['end']:] for p in selected] +
                             [context + ' ' + s for s in surfaces])
                (probe_scores, probe_sums), batch_ms = score(labels, packed)
                stage_scores = algorithm.form_scores(surfaces, probe_scores, len(selected))
                key_order = algorithm.rank(list(stage_scores), stage_scores)
                chosen = [s for s in surfaces if s.lower() == key_order[0]]
                (winner_scores, winner_sums), case_ms = score(chosen, v1.prepare(tokenizer, special, context, chosen))
                for s in chosen:
                    for actual, expected in [(winner_scores[s], baseline[s]),
                                             (winner_sums[s], r['sumScores'][s])]:
                        error = abs(actual - expected)
                        max_error = max(max_error, error)
                        v1.require(error <= .001, 'case-stage native reproduction')
                v1.require(v1.rank(chosen, winner_scores) == v1.rank(chosen, {s: baseline[s] for s in chosen}), 'case stage ranks unchanged')
                # Preserve exact-case tie order from the earlier full batch.
                case_scores = baseline
                pipeline_ms = (time.perf_counter() - pipeline_began) * 1000
                r.update(grammarInputs=packed, probeLabels=labels, probes=selected,
                         probeMeanScores=probe_scores, probeSumScores=probe_sums,
                         formScores=stage_scores, chosenKey=key_order[0], actualCaseStageScores=winner_scores,
                         actualCaseStageSums=winner_sums, grammarBatchRows=len(labels),
                         grammarBatchHostMs=batch_ms, caseStageHostMs=case_ms,
                         primaryPipelineHostMs=pipeline_ms, primaryNativeCalls=2)
                # Validation calls are outside the prospective two-call pipeline.
                for p_index, probe in enumerate(selected):
                    for s in surfaces:
                        one_labels, one_pack, _ = algorithm.prepare(tokenizer, special, context, [s], [probe])
                        (one, one_sums), _ = score(one_labels, one_pack)
                        label = f'{p_index}/{s}'
                        for actual, expected in [(one[one_labels[0]], probe_scores[label]),
                                                 (one_sums[one_labels[0]], probe_sums[label])]:
                            error = abs(actual - expected)
                            max_error = max(max_error, error)
                            v1.require(error <= .001, 'middle-target single/batched parity')
        proposed = algorithm.ordered(surfaces, case_scores, stage_scores) if stage_scores is not None else before_presentation
        # Unsupported groups keep their full original mean order; no new form
        # policy is silently applied to historical unrelated large slates.
        if not r['agreementEligibility'].startswith('eligible_'):
            proposed = before_presentation = v1.rank(surfaces, baseline)
        r.update(presentationBaselineOrder=before_presentation, proposedOrder=proposed,
                 proposedOrdinalScores=algorithm.ordinal(proposed),
                 presentationBaselineOrdinalScores=algorithm.ordinal(before_presentation))
        rows.append(r)
    v1.require(len(rows) == len({r['id'] for r in rows}) == 304, '304 request completeness')
    results = {}
    for dataset in ['history', 'form24', 'caseControl24', 'newForms24']:
        sample = [r for r in rows if r['dataset'] == dataset]
        flat = metrics.evaluate([dict(r, gainScores=r['proposedOrdinalScores']) for r in sample])
        same_presentation = metrics.evaluate([dict(r, meanScores=r['presentationBaselineOrdinalScores'],
                                                  gainScores=r['proposedOrdinalScores']) for r in sample])
        results[dataset] = dict(versusFlatMean=flat, versusSamePresentation=same_presentation,
                               preservationPassed=flat['preservationPassed'] and same_presentation['preservationPassed'])
    active = [r for r in rows if 'primaryPipelineHostMs' in r]
    eligibility_counts = {}
    for r in rows:
        k = r['dataset'] + '/' + r['agreementEligibility']
        eligibility_counts[k] = eligibility_counts.get(k, 0) + 1
    timing = {k: dict(p50=percentile([r[k] for r in active], .5), p95=percentile([r[k] for r in active], .95))
              for k in ['grammarBatchHostMs', 'caseStageHostMs', 'primaryPipelineHostMs']}
    report = dict(protocol=PROTOCOL, codeCommit=os.environ.get('GITHUB_SHA', 'local-unpublished'), frozenInputs=frozen,
                  modelSha256=v1.TRUST['model.onnx'][1], predictions=rows, results=results,
                  allPreservationPassed=all(r['preservationPassed'] for r in results.values()),
                  hasFormImprovement=any(g['formRepairs'] > 0 for d in ['form24', 'newForms24']
                                         for g in results[d]['versusSamePresentation']['groups'].values()),
                  eligibilityCounts=eligibility_counts, extraNativeCalls=calls, maxSingleBatchScoreError=max_error,
                  hostTimingMs=timing,
                  limitations=['Agreement is a diagnostic hypothesis, not a parser, calibrated probability or full sentence likelihood',
                               'Case is averaged in stage1 but can still influence form scores; not fully independent semantics',
                               'Stage2 retains existing mean case ranking; case preservation in controls is by construction, not new accuracy',
                               'Historical unrelated slates bypass stage1; their preservation does not validate grammatical ranking',
                               'Fixed last two lexical words, six new known-source form families and authored labels; not blinded general accuracy',
                               'Host timing is not Android latency; primary pipeline timing includes diagnostic token parity checks',
                               'No actual phone swipe, geometry, full-strip Top3 or runtime threshold change',
                               'No APK, scorer, model, langpack, editor logging or release changes'])
    report['qualityGatePassed'] = report['allPreservationPassed'] and report['hasFormImprovement']
    (out / 'scores.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# HerBERT — zgodność formy, następnie kapitalizacja V4', '',
             f"allPreservationPassed={report['allPreservationPassed']}; nowy scorer wyłącznie diagnostyczny.", '',
             '| Dataset / grupa (flat mean baseline) | Gold | Mean Top1 | Dwa etapy Top1 | Naprawy | Regresje | Regresje Top3 |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for dataset, data in results.items():
        for key, g in data['versusFlatMean']['groups'].items():
            lines.append(f"| {dataset}/{key} | {g['labelled']} | {g['meanTop1']} | {g['gainTop1']} | {g['repairs']} | {g['regressions']} | {g['top3Regressions']} |")
    lines += ['', 'Eligibility: ' + json.dumps(eligibility_counts, ensure_ascii=False),
              'Host p50/p95 ms (nie Android): ' + json.dumps(timing),
              'Stage1: jeden batch do8 rows; stage2: jeden batch do2 case variants. Baseline/parity calls poza tym kosztem.',
              'Wszystkie feeds/score/rank/zmiany i drugi comparator z identyczną prezentacją w scores.json.',
              'SUCCESS workflow oznacza wykonanie pomiaru, nie zatwierdzenie jakości.']
    (out / 'SUMMARY.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('HerBERT agreement: original parity; 304 requests; source extraction; middle-mask single/batched and case-stage reproduction PASS')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract-only', action='store_true')
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--source-pack', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.contract_only:
        verify_freeze()
        print('HerBERT agreement: frozen source-backed two-stage protocol PASS')
    else:
        v1.require(all(v is not None for v in [args.bundle, args.source_pack, args.out]), 'bundle/pack/out required')
        run(args.bundle, args.source_pack, args.out)
