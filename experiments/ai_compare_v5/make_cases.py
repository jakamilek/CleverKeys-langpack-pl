"""Fresh authored diagnostic contexts; dictionary meanings are never authored here."""
import json
from pathlib import Path

# Four new contexts per source-attested case pair: ordinary/name, direct/distant.
PAIRS = {
 'łódź': [
  'Po remoncie silnika na wodę wróciła nasza',
  'Nie wybieramy się nad jezioro. Planujemy zwiedzanie miasta, a kolejnym punktem podróży jest',
  'Przewoźnik ma nowy sprzęt pływający. Po sprawdzeniu wyposażenia do rejsu była gotowa',
  'Rozmawiamy o miastach wojewódzkich. Na liście pozostała jeszcze'],
 'malina': [
  'Do deseru dodaję owoce, a na samym wierzchu będzie jedna',
  'Nowy kierownik podpisał dokument nazwiskiem',
  'Zbieraliśmy owoce z krzewów. W koszyku została tylko jedna',
  'To zebranie pracowników, a nie rozmowa o roślinach. Odpowiedzialny za projekt jest pan'],
 'jagoda': [
  'Na palcu został mi sok z owocu, bo pękła dojrzała',
  'Rodzice wybrali córce imię',
  'Jesteśmy w lesie i zbieramy owoce. Na dnie naczynia została jeszcze jedna',
  'Ustalamy listę uczestniczek szkolenia. Jako pierwsza zgłosiła się'],
 'róża': [
  'W bukiecie obok tulipanów znalazła się biała',
  'Nasza sąsiadka ma na imię',
  'Pielęgnuję kwiaty na rabacie. W tym miejscu najlepiej przyjęła się',
  'To spotkanie z nową koleżanką. Na zaproszeniu widnieje imię'],
 'warszawska': [
  'W zestawieniu cen wyróżnia się średnia',
  'Protokół podpisała pani',
  'Porównujemy oferty z różnych miast. Najdroższa okazała się propozycja',
  'Chodzi o nazwisko osoby prowadzącej spotkanie. W dokumentach zapisana jest pani'],
 'ale': [
  'Chciałem przyjechać wcześniej,',
  'W grupie są dwie dziewczyny o imieniu Ala. Do konkursu zgłosiły się obie',
  'Plan był już gotowy. Wydawało się, że wszystko pójdzie sprawnie,',
  'Dwie uczestniczki noszą imię Ala. Z całej listy zaproszeń odpowiedziały właśnie te dwie'],
 'lub': [
  'Na śniadanie możesz wybrać kaszę',
  'Znam dwie kobiety o imieniu Luba. Nie pamiętam adresów obu',
  'W menu są dwie propozycje. Kelner zapytał, czy zamówimy kawę',
  'W archiwum są dwie osoby o imieniu Luba. Brakuje akt obu'],
 'tutaj': [
  'Nie odkładaj tego na półkę, zostaw to',
  'Nazwisko nowego członka komisji to',
  'Pokazuję miejsce na mapie. Przygotowany znacznik należy postawić właśnie',
  'Rozmawiamy o osobie podpisującej umowę. W rubryce nazwisko widnieje'],
 'lis': [
  'Z lasu wyszedł rudy',
  'Umowę podpisał pan',
  'Obserwujemy dzikie zwierzęta. Po dłuższej chwili z zarośli wybiegł',
  'To sprawa nazwiska autora raportu. Na okładce zapisano doktor'],
 'wilk': [
  'Na skraju lasu pojawił się szary',
  'Kierownik przedstawił się jako pan',
  'Rozmawiamy o drapieżnikach. Najbliżej kamery zatrzymał się',
  'Ustalamy dane osoby upoważnionej do podpisu. Nazwisko tej osoby to'],
 'kruk': [
  'Na gałęzi usiadł czarny',
  'Nowy lekarz nosi nazwisko',
  'Obserwujemy ptaki przy karmniku. Jako ostatni przyleciał',
  'Przeglądamy listę pracowników. Dyżur pełni dziś doktor'],
 'sowa': [
  'Z dziupli wyglądała mała',
  'List zaadresowano do pana',
  'Badamy nocne ptaki. Na zdjęciu została wyraźnie uchwycona',
  'Nie chodzi o ptaka, tylko o nazwisko rozmówcy. Telefon odebrał pan'],
 'piła': [
  'Do cięcia drewna przyda się ostra',
  'Na trasie kolejowej znajduje się miasto',
  'Warsztat kupił nowe narzędzia. Jako pierwsza została uruchomiona',
  'Planujemy podróż po miastach. Kolejną miejscowością na liście jest'],
 'buk': [
  'W parku rośnie stary',
  'Pismo podpisał pan',
  'Oglądamy drzewa w ogrodzie. Największy cień daje tam',
  'Rozmowa dotyczy autora dokumentu. Jego nazwisko brzmi'],
 'zając': [
  'Przez łąkę przebiegł mały',
  'Protokół sporządził pan',
  'Śledzimy zwierzęta przy polu. Po chwili z wysokiej trawy wyskoczył',
  'Sprawdzamy nazwiska świadków. Na końcu listy znajduje się pan'],
 'kot': [
  'Na parapecie zasnął domowy',
  'Zamówienie odebrał pan',
  'Opowiadamy o zwierzętach w domu. Na fotelu drzemie nasz',
  'To dane osoby, a nie opis zwierzęcia. W rubryce nazwisko wpisano'],
}

# Exact first five candidates/scores from the maintainer's supplied playground log.
# No claim that these are fresh v5 decoder runs; contexts below are authored replay probes.
RECORDED = {
 'olej': [('olej',251),('olek',236),('oliwek',120),('ołówek',82),('innej',61)],
 'mleko': [('mleko',184),('mieli',139),('miękko',107),('miękki',89),('mięli',84)],
 'karton': [('karton',318),('kwestiom',88),('karsin',81),('kewin',61),('jesion',56)],
 'łódź': [('łódź',190),('kosz',129),('łotysz',95),('klisz',86),('łudź',63)],
}
REPLAY_CONTEXTS = [
 ('olej','Na patelni rozgrzałem','olej'),
 ('olej','Pod drzwiami czeka mój kolega','Olek'),
 ('mleko','Do ciasta dodaję','mleko'),
 ('mleko','Materac ugina się bardzo','miękko'),
 ('karton','Rzeczy spakowałem w','karton'),
 ('karton','Miejscowość na trasie nosi nazwę','Karsin'),
 ('łódź','Na mapie zaznaczyłem miasto','Łódź'),
 ('łódź','Przy bramie stoi duży','kosz'),
]
PUNCTUATION = [
 ('Wiem','że',','), ('Nie pamiętam','czy',','),
 ('Powiedz mi','kiedy',','), ('To osoba','która',','),
 ('Zostałem w domu','ponieważ',','), ('Zadzwoń','zanim',','),
 ('Przyszedłem','żeby',','), ('Nie było łatwo','ale',','),
 ('Nie on','lecz',','), ('Było trudno','jednak',','),
 ('Kupiłem chleb','i',''), ('Wybierz kawę','lub',''),
 ('Nie kupiłem chleba','ani',''), ('Odpowiedź brzmi tak','albo',''),
 ('Usiądź','tutaj',''), ('Przyszedłem','po',''),
 ('To moje zadanie','a',','), ('Zabierz parasol','bo',','),
 ('Pracuję','w',''), ('Spotkajmy się','jutro',''),
]

def build():
    rows=[]
    for key, contexts in PAIRS.items():
        for i, context in enumerate(contexts):
            rows.append({'id':f'form-{key}-{i+1}', 'suite':'forms',
                         'contextType':'direct' if i<2 else 'distant',
                         'leftContext':context,
                         'candidates':[{'key':key,'engineScore':100}],
                         'goldSurface': key if i%2==0 else key[:1].upper()+key[1:]})
    for i,(slate,context,gold) in enumerate(REPLAY_CONTEXTS):
        rows.append({'id':f'replay-{i+1}', 'suite':'recorded_replay',
                     'sourceSlate':slate, 'leftContext':context,
                     'candidates':[{'key':k,'engineScore':s} for k,s in RECORDED[slate]],
                     'goldSurface':gold})
    for key in ['jan','maria','łódzki']:
        for i,c in enumerate(['Na liście pojawia się','Rozmawialiśmy długo. W dokumencie widnieje']):
            rows.append({'id':f'single-{key}-{i}', 'suite':'single_variant',
                         'leftContext':c, 'candidates':[{'key':key,'engineScore':100}],
                         'goldSurface':{'jan':'Jan','maria':'Maria','łódzki':'łódzki'}[key]})
    for key in ['łódź','malina','tutaj','lis']:
        rows.append({'id':f'ambiguous-{key}', 'suite':'ambiguous',
                     'leftContext':'Zapisz jeszcze',
                     'candidates':[{'key':key,'engineScore':100}], 'goldSurface':None})
    for key,gold in [('łódź','Łódź'),('malina','Malina')]:
        rows.append({'id':f'missing-{key}', 'suite':'missing_key',
                     'leftContext':'Nazwa w dokumentach to',
                     'candidates':[{'key':'mleko','engineScore':100}], 'goldSurface':gold})
    for i,(context,word,punct) in enumerate(PUNCTUATION):
        rows.append({'id':f'punct-{i+1}', 'suite':'punctuation_before_word',
                     'leftContext':context, 'nextWord':word,
                     'options':['',','], 'goldPunctuation':punct})
    return {'schemaVersion':1,'dataKind':'authored-diagnostic-with-recorded-slate-replays',
            'cases':rows}

if __name__=='__main__':
    p=Path(__file__).with_name('cases.json')
    p.write_text(json.dumps(build(),ensure_ascii=False,sort_keys=True,indent=2)+'\n')
