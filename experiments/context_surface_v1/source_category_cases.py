"""Authored test contexts; dictionary categories are generated separately."""
import copy
from natural_cases import build as natural_build

MAIN = {'natural_direct', 'natural_history', 'natural_switch', 'natural_negation', 'source_new_warszawski'}
NEW = [
    ('warszawski', 'adjective', 'Ten teatr działa w stolicy, więc jest to teatr '),
    ('warszawski', 'surname', 'Nasz lekarz ma na nazwisko '),
    ('warszawski', 'adjective', 'Bank otworzył oddział w Warszawie. W porównaniu z krakowskim jest to oddział '),
    ('warszawski', 'surname', 'Do zespołu dołączył nowy księgowy. W jego dokumentach widnieje pan Jan '),
    ('warszawski', 'adjective', 'Listę nazwisk już zamknęliśmy. Teraz opisujemy teatr działający w Warszawie. To teatr '),
    ('warszawski', 'surname', 'O tramwajach w stolicy porozmawiamy później. Teraz przedstawiam nowego klienta, pana Jana. Jego nazwisko to '),
    ('warszawski', 'adjective', 'Nie podaję nazwiska człowieka. Określam miasto, w którym mieści się teatr. Jest to teatr '),
    ('warszawski', 'surname', 'Nie opisuję położenia sklepu. Wpisuję nazwisko pana Jana w formularzu. Pan Jan '),
]
SINGLE = [
    'Zakład znajduje się w Łodzi, więc jest to zakład ',
    'Wśród klubów z wielu miast jest także klub ',
    'Rozmawiamy o oddziale firmy w Łodzi. Na mapie zaznaczyłem oddział ',
    'Miastem gospodarzy jest Łódź. W finale wystąpi miejscowy zespół ',
    'Nazwiska pracowników już wpisaliśmy. Teraz wybieramy adres biura w Łodzi. Będzie to oddział ',
    'Rejs został odwołany. Teraz interesuje nas klub sportowy z Łodzi. To klub ',
    'Nie podaję nazwiska. Określam miejsce działania oddziału w Łodzi. To oddział ',
    'Nie opisuję jednostki pływającej. Wymieniam region związany z miastem Łódź. To region ',
]
GOLD = {'boat':['NAME:nazwa_pospolita'], 'city':['NAME:nazwa_geograficzna'],
        'fruit':['NAME:nazwa_pospolita'], 'flower':['NAME:nazwa_pospolita'],
        'surname':['NAME:nazwisko'], 'given_name':['NAME:imię'],
        'country':['NAME:nazwa_geograficzna'], 'adjective':['POS:adj','POS:adjp']}


def build(sidecar):
    natural, _ = natural_build()
    cases = []
    for original in natural['cases']:
        if original['diagnostic']['category'] not in MAIN:
            continue
        row = copy.deepcopy(original)
        sense = row.pop('expectedSenseIds')[0]
        if sense == 'street':
            row['diagnostic'] = {'category':'unsupported_street', 'sourceId':original['id']}
        else:
            row['expectedCategoryIds'] = GOLD[sense]
            row['diagnostic']['reuseFrom'] = 'natural-cases.json/' + original['id']
        cases.append(row)
    for i, (key,sense,context) in enumerate(NEW):
        cases.append({'id':f'new{i+1:03}', 'beforeCursor':context,
                      'candidates':[{'surface':key,'engineScore':650},{'surface':'dom','engineScore':100}],
                      'expected':{'languageCode':'pl','surfaceKey':key,
                                  'surface':key.capitalize() if sense=='surname' else key},
                      'expectedCategoryIds':GOLD[sense], 'diagnostic':{'category':'source_new_warszawski'}})
    main = [c for c in cases if c['diagnostic']['category'] in MAIN]
    for c in main:
        row = copy.deepcopy(c)
        key=c['expected']['surfaceKey']
        row['id']='probe-'+c['id']
        row['candidates']=[{'surface':'jagoda' if key=='malina' else 'malina','engineScore':700},
                           {'surface':key,'engineScore':650}]
        row['diagnostic']={'category':'top3_probe','sourceId':c['id']}
        cases.append(row)
    for i,context in enumerate(SINGLE):
        cases.append({'id':f'single{i+1:03}', 'beforeCursor':context,
                      'candidates':[{'surface':'łódzki','engineScore':650},{'surface':'dom','engineScore':100}],
                      'expected':{'languageCode':'pl','surfaceKey':'łódzki','surface':'łódzki'},
                      'expectedCategoryIds':GOLD['adjective'], 'diagnostic':{'category':'source_single_variant'}})
    for i,entry in enumerate(sidecar['entries']):
        key=entry['surfaceKey']
        source=next(c for c in cases if c.get('expected',{}).get('surfaceKey')==key
                    and c['diagnostic']['category'] in MAIN|{'source_single_variant'})
        for category in ['sentence_start','ambiguous','missing_key','slot_limit']:
            row=copy.deepcopy(source)
            row['id']=f'{category}{i+1:03}'
            row['diagnostic']={'category':category,'sourceId':source['id']}
            if category=='sentence_start':
                row['beforeCursor']=source['beforeCursor'].rstrip()+'. '
                row['caseMode']='sentence_start';row['expected']['surface']=key.capitalize()
            if category=='ambiguous':
                row['beforeCursor']='Oto ';row.pop('expected');row.pop('expectedCategoryIds',None)
            if category=='missing_key':
                row['candidates']=[{'surface':'dom','engineScore':650},{'surface':'lód','engineScore':100}]
            if category=='slot_limit':
                row['candidates']=[{'surface':'jagoda' if key=='malina' else 'malina','engineScore':700},
                                   {'surface':'dom','engineScore':680},{'surface':key,'engineScore':650}]
            cases.append(row)
    return {'schemaVersion':1,'fixtureKind':'source_categories_on_60_reused_and_8_new_main_contexts_with_separate_controls',
            'cases':cases}
