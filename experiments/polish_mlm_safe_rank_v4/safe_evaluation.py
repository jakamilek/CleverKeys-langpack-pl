"""Evaluate a label-free policy after decisions; keep replay separate."""
from policy import rank, REGRESSION_COST


def evaluate_policy(cases, entries, request, predictions, threshold):
    from contract import baseline
    by_case = {c['id']: c for c in cases}
    groups, decisions = {}, []
    for row in request['requests']:
        case, pred = by_case[row['caseId']], predictions[row['id']]
        source_order = baseline(case, entries)
        decision = rank(source_order, pred['scores'], threshold)
        gold = case['goldSurface']
        correct, base_correct = decision['rank'][0] == gold, source_order[0] == gold
        key = f"{case['population']}/forms/{row['window']}"
        group = groups.setdefault(key, {'cases':0, 'labelled':0, 'top1':0,
                                       'baselineTop1':0, 'repairs':0, 'regressions':0,
                                       'overrides':0, 'lowerTop1':0, 'upperTop1':0})
        group['cases'] += 1
        group['labelled'] += 1
        group['top1'] += correct
        group['baselineTop1'] += base_correct
        group['repairs'] += correct and not base_correct
        group['regressions'] += not correct and base_correct
        group['overrides'] += decision['override']
        group['upperTop1' if gold[0].isupper() else 'lowerTop1'] += correct
        decisions.append({'id':row['id'], 'caseId':row['caseId'], 'window':row['window'],
                          'population':case['population'], 'gold':gold,
                          'baseline':source_order, 'correct':correct, **decision})
    for group in groups.values():
        group['utility'] = group['repairs'] - REGRESSION_COST * group['regressions']
    return {'threshold':threshold, 'groups':groups, 'decisions':decisions,
            'populationRoles':{key:('developmentReplay' if key.startswith('regression_v5/')
                                    else 'newAuthoredContextValidation') for key in groups},
            'policyInputs':['sourceBaseline', 'modelScores', 'frozenGlobalThreshold'],
            'calibratedProbability':False}


def screening(candidate, reference):
    groups = candidate['gated']['groups']
    keys = [key for key in groups if key.startswith('fresh_') and key.endswith('/16')]
    if len(keys) != 4 or any(groups[k]['cases'] != 16 for k in keys):
        raise ValueError('incomplete new validation strata')
    total = {k:sum(groups[g][k] for g in keys)
             for k in ['cases','top1','baselineTop1','repairs','regressions','overrides','utility']}
    raw = {k:sum(candidate['groups'][g][k] for g in keys)
           for k in ['top1','repairs','regressions']}
    raw['utility'] = raw['repairs'] - REGRESSION_COST * raw['regressions']
    checks = {'regressionsAtMostTwo':total['regressions']<=2,
              'regressionsAtMostRaw':total['regressions']<=raw['regressions'],
              'utilityAtLeastRaw':total['utility']>=raw['utility'],
              'top1ImprovesDefault':total['top1']>total['baselineTop1'],
              'atLeastEightOverrides':total['overrides']>=8,
              'allStrataAtLeastBaseline':all(groups[k]['top1']>=groups[k]['baselineTop1'] for k in keys),
              'allStrataAtMostOneRegression':all(groups[k]['regressions']<=1 for k in keys)}
    c = candidate['groups']['regression_v5/forms/32']['top1']
    h = reference['groups']['regression_v5/forms/32']['top1']
    return {'primaryWindow':16, 'newValidationCases':64, 'gatedTotals':total,
            'rawTotals':raw, 'checks':checks, 'exploratorySafeCandidate':all(checks.values()),
            'developmentReplayReferenceQualityGate':{'candidateTop1':c,'referenceTop1':h,
                                                     'oldRequirementReferenceMinusOne':c>=h-1,
                                                     'usedForNewPolicyQualification':False},
            'productionApproved':False, 'default16Approved':False}
