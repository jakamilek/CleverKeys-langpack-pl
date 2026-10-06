"""Global abstaining case reranker; score margin is not calibrated probability."""
import math

THRESHOLDS = (0., .25, .5, 1., 2., 3., 4., 6., 8., None)
REGRESSION_COST = 4


def rank(baseline, scores, threshold):
    if (len(baseline) != 2 or len(set(baseline)) != 2 or set(scores) != set(baseline)
            or any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in scores.values())):
        raise ValueError('two complete source forms and finite scores required')
    if threshold is not None and (not isinstance(threshold, (int, float))
                                  or not math.isfinite(threshold) or threshold < 0):
        raise ValueError('invalid frozen threshold')
    default, alternative = baseline
    margin = scores[alternative] - scores[default]
    override = threshold is not None and margin > 0 and margin >= threshold
    return {'rank': [alternative, default] if override else list(baseline),
            'override': override, 'margin': margin, 'threshold': threshold}


def calibrate(rows):
    if not rows or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('nonempty unique development requests required')
    table = []
    for threshold in THRESHOLDS:
        repairs = regressions = overrides = correct = 0
        for row in rows:
            if row['gold'] not in row['baseline']:
                raise ValueError('unattested development gold')
            decision = rank(row['baseline'], row['scores'], threshold)
            base_correct = row['baseline'][0] == row['gold']
            now_correct = decision['rank'][0] == row['gold']
            repairs += now_correct and not base_correct
            regressions += base_correct and not now_correct
            overrides += decision['override']
            correct += now_correct
        table.append({'threshold': threshold, 'requests': len(rows), 'top1': correct,
                      'repairs': repairs, 'regressions': regressions, 'overrides': overrides,
                      'utility': repairs - REGRESSION_COST * regressions})
    # Fixed before calibration: maximize development utility, then fewer errors,
    # fewer changes and the larger threshold; None is abstain-all.
    selected = max(table, key=lambda r: (r['utility'], -r['regressions'], -r['overrides'],
                                        math.inf if r['threshold'] is None else r['threshold']))
    return {'threshold': selected['threshold'], 'regressionCost': REGRESSION_COST,
            'grid': list(THRESHOLDS), 'selected': selected, 'developmentTable': table,
            'calibratedProbability': False, 'holdoutUsed': False}
