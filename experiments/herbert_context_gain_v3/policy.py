"""Pre-registered diagnostic scores; no trained coefficients or live changes."""
import math


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(surfaces, scores):
    require(bool(surfaces) and len(surfaces) == len(set(surfaces)) and
            all(isinstance(s, str) and s for s in surfaces) and
            set(scores) == set(surfaces), 'unaligned scores')
    require(all(type(v) in (int, float) and math.isfinite(v) for v in scores.values()),
            'nonfinite/non-numeric score')
    return sorted(surfaces, key=lambda s: -scores[s])


def context_gain(surfaces, contextual_sums, neutral_sums):
    """sum_logp(context, surface) - sum_logp(empty, identical surface).

    This is a score difference, NOT a calibrated probability or a true
    autoregressive likelihood ratio. The original WWM graph stays identical.
    """
    rank(surfaces, contextual_sums)
    rank(surfaces, neutral_sums)
    result = {s: contextual_sums[s] - neutral_sums[s] for s in surfaces}
    rank(surfaces, result)  # reject arithmetic overflow too
    return result


def outcomes(surfaces, gold, scores):
    ordered = rank(surfaces, scores)
    require(gold is None or isinstance(gold, str) and bool(gold), 'invalid gold')
    if gold is None:
        return dict(order=ordered, labelled=False, missingGold=False,
                    exactTop1=False, rawTop3=False, formTop1=False,
                    formComparable=False, caseComparable=False, caseGivenGoldForm=False)
    same_key = [s for s in surfaces if s.lower() == gold.lower()]
    available = gold in surfaces
    # Initial-case correctness on an entirely wrong word is misleading. Compare
    # case within the actual gold form, and expose its own eligible denominator.
    case_comparable = available and len(same_key) > 1
    return dict(order=ordered, labelled=True, missingGold=not available,
                exactTop1=ordered[0] == gold, rawTop3=gold in ordered[:3],
                formTop1=ordered[0].lower() == gold.lower(),
                formComparable=available and len({s.lower() for s in surfaces}) > 1,
                caseComparable=case_comparable,
                caseGivenGoldForm=case_comparable and rank(same_key, {s: scores[s] for s in same_key})[0] == gold)


def evaluate(rows):
    require(bool(rows) and len({r['id'] for r in rows}) == len(rows), 'empty/duplicate IDs')
    groups, changes = {}, []
    for row in rows:
        before = outcomes(row['surfaces'], row['gold'], row['meanScores'])
        after = outcomes(row['surfaces'], row['gold'], row['gainScores'])
        key = '/'.join([row['suite'], row['population'], row['window']])
        g = groups.setdefault(key, dict(requests=0, labelled=0, missingGold=0,
                                       meanTop1=0, gainTop1=0, meanTop3=0, gainTop3=0,
                                       repairs=0, regressions=0, top3Regressions=0,
                                       formComparable=0, meanFormTop1=0, gainFormTop1=0,
                                       formRepairs=0, formRegressions=0,
                                       caseComparable=0, meanCaseGivenGoldForm=0,
                                       gainCaseGivenGoldForm=0, caseRepairs=0,
                                       caseRegressions=0, rankChanges=0))
        g['requests'] += 1
        g['rankChanges'] += before['order'] != after['order']
        if before['labelled']:
            g['labelled'] += 1
            g['missingGold'] += before['missingGold']
            for field, left, right in [('exactTop1', 'meanTop1', 'gainTop1'),
                                       ('rawTop3', 'meanTop3', 'gainTop3')]:
                g[left] += before[field]
                g[right] += after[field]
            g['repairs'] += not before['exactTop1'] and after['exactTop1']
            g['regressions'] += before['exactTop1'] and not after['exactTop1']
            g['top3Regressions'] += before['rawTop3'] and not after['rawTop3']
            for eligible, metric, prefix in [('formComparable', 'formTop1', 'FormTop1'),
                                             ('caseComparable', 'caseGivenGoldForm', 'CaseGivenGoldForm')]:
                if before[eligible]:
                    g[eligible] += 1
                    g['mean' + prefix] += before[metric]
                    g['gain' + prefix] += after[metric]
                    name = 'form' if eligible == 'formComparable' else 'case'
                    g[name + 'Repairs'] += not before[metric] and after[metric]
                    g[name + 'Regressions'] += before[metric] and not after[metric]
        if before != after:
            changes.append(dict(id=row['id'], group=key, gold=row['gold'],
                                before=before, after=after, meanScores=row['meanScores'],
                                gainScores=row['gainScores']))
    return dict(groups=groups, changes=changes,
                preservationPassed=all(all(g[k] == 0 for k in
                                           ['regressions', 'top3Regressions', 'formRegressions', 'caseRegressions'])
                                       for g in groups.values()))
