"""Paired explanation study: reused data explicitly separate from new diagnostics."""
import json
from pathlib import Path
ROOT=Path(__file__).parent
BASE=ROOT.parent/'ai_compare_v5'

NEW={
 'łódź':('Cumę przywiązano do pomostu. Przy brzegu kołysała się drewniana',
         'W formularzu adresowym podano województwo łódzkie, a w polu miasto wpisano'),
 'malina':('Na talerzu z owocami leżała jeszcze jedna świeża',
           'Inspektor podał swoje dane osobowe. Nazywa się pan'),
 'jagoda':('Z rozgniecionego owocu wypłynął sok. Była to leśna',
           'Sprawdzamy listę dziewcząt. Obok daty urodzenia zapisano imię'),
 'róża':('Ogrodnik pokazał kwiat z kolcami. Na etykiecie sadzonki widniała',
         'W klasie pojawiła się uczennica, której rodzice nadali imię'),
 'warszawska':('Największą popularność zdobyła odmiana',
              'To lista osób, nie ulic. Nową członkinią zespołu została pani'),
 'ale':('Sprawdziłem wszystkie połączenia i chciałem już wyjść,',
        'W obu rodzinach córki mają imię Ala. Na fotografii stoją obydwie'),
 'lub':('Termin można przesunąć na poniedziałek',
        'Obie ciotki noszą imię Luba. Zaginęły zaświadczenia dotyczące obu'),
 'tutaj':('Przesuń pudełko bliżej mnie i postaw je',
          'W kartotece pacjentów zmieniono adres mężczyzny o nazwisku'),
 'lis':('Na śniegu zostały ślady dzikiego zwierzęcia. Tropem przebiegł rudy',
        'Szef podał nazwisko nowego księgowego. Jest nim pan'),
 'wilk':('W stadzie drapieżników największy był szary',
         'Podpis pod opinią należy do lekarza. To doktor'),
 'kruk':('Wśród ptaków nad polem krążył duży czarny',
         'Sprawdzono tożsamość świadka. W dowodzie ma nazwisko'),
 'sowa':('Zwierzę aktywne nocą siedziało na gałęzi. Była to',
         'Na kopercie wpisano nazwisko adresata. Odbiorcą jest pan'),
 'piła':('Mechanik wyjął narzędzie do przecinania desek. Była to',
         'W wykazie miejscowości w województwie wielkopolskim znajduje się'),
 'buk':('Leśnik mierzył obwody drzew. Najgrubszy był stary',
        'Pracownik przedstawił się z nazwiska. W protokole zapisano pan'),
 'zając':('Przy miedzy poruszyły się długie uszy. Z trawy wybiegł',
          'Na liście nazwisk zawodników znalazł się pan'),
 'kot':('Zwierzę przeciągnęło się i zamiauczało. Był to nasz',
        'Rejestr dotyczy osób podpisujących umowę. Jedną z nich jest pan'),
}

def build():
    old=json.loads((BASE/'cases.json').read_text())
    cases=[{**c,'population':'reused'} for c in old['cases'] if c['suite']!='punctuation_before_word']
    for key,contexts in NEW.items():
        for i,context in enumerate(contexts):
            cases.append({'id':f'newform-{key}-{i+1}','suite':'forms','population':'new',
                          'leftContext':context,'candidates':[{'key':key,'engineScore':100}],
                          'goldSurface':key if i==0 else key[0].upper()+key[1:]})
    return {'schemaVersion':1,'dataKind':'paired-metadata-explanation-diagnostic',
            'priorCasesCommit':'00a7bf5999e8f6419a68c1884919e699c744a927',
            'cases':cases}

if __name__=='__main__':
    (ROOT/'cases.json').write_text(json.dumps(build(),ensure_ascii=False,sort_keys=True,indent=2)+'\n')
