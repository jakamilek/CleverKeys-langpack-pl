"""Deterministic authored diagnostic cases. Never change after inference."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent
PACK_SHA = 'aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb'
SIDECAR_SHA = '5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d'
# Contexts only: no new dictionary semantics, category labels or descriptions.
# Each row: source key, short lowercase/uppercase, longer lowercase/uppercase.
TEXTS = [
('łódź', 'Przy pomoście kołysała się niewielka drewniana', 'Najbliższym przystankiem tego pociągu będzie',
 'Rybacy wrócili z połowu późnym wieczorem i od razu zajęli się sprzętem, ponieważ podczas burzy ucierpiały sieci, kilka skrzynek oraz ich stara drewniana',
 'Po kilku dniach spędzonych w stolicy chcemy pojechać dalej koleją, obejrzeć dawne fabryki i spotkać się z przyjaciółmi; następnym miastem na naszej trasie będzie'),
('malina', 'W miseczce została tylko jedna dojrzała', 'Autorem tej opinii jest doktor Tomasz',
 'Przez cały ranek zbieraliśmy owoce w ogrodzie, a potem myliśmy je i układaliśmy na talerzach, lecz na krzaku przy płocie została jeszcze jedna duża dojrzała',
 'W poradni zmienił się lekarz prowadzący i trzeba było ponownie omówić wyniki badań, ale dyżurna pielęgniarka uspokoiła nas, że konsultację poprowadzi znany nam doktor Tomasz'),
('warszawska', 'Ta linia autobusowa jest typowo', 'Na kopercie zapisano adres ulica',
 'Porównywaliśmy komunikację w kilku polskich miastach, sprawdzając rozkłady autobusów, ceny biletów oraz połączenia nocne, i po tej rozmowie okazało się, że najbardziej odpowiada nam sieć',
 'W małym miasteczku nie ma numeracji według osiedli, więc kurier poprosił o pełny adres odbiorcy, a na formularzu przesyłki wpisałem nazwę ulicy i numer domu: ulica'),
('buk', 'Przy leśnej ścieżce rośnie stary', 'Ten podpoznański kierunek to miasto',
 'Od dawna spacerujemy tą samą trasą przez las, lecz dopiero podczas ostatniej wycieczki zauważyliśmy, że tuż obok ścieżki, pomiędzy sosnami, rośnie ogromny rozłożysty',
 'Szukaliśmy niewielkiego miasta blisko Poznania, do którego można dotrzeć pociągiem i wrócić jeszcze tego samego dnia, a znajomy polecił nam jako cel wycieczki'),
('kruk', 'Na kominie usiadł duży czarny', 'Na pytania odpowiedział profesor Jan',
 'Kiedy skończyliśmy remont dachu, przez kilka dni nic nie zakłócało spokoju w ogrodzie, aż pewnego ranka na najwyższym kominie usiadł wielki czarny',
 'Uczestnicy konferencji długo dyskutowali o wynikach badań i prosili organizatorów o dodatkowe wyjaśnienia, ale ostatecznie najwięcej pytań dostał zaproszony do panelu profesor Jan'),
('zając', 'Z wysokiej trawy wyskoczył młody', 'Dokument podpisał prezes Adam',
 'Po nocnym deszczu wybraliśmy się na spacer wzdłuż pól, gdzie między mokrymi kłosami zauważyliśmy ruch, a chwilę później z wysokiej trawy wyskoczył przestraszony',
 'Zebranie spółki przeciągnęło się do późnego popołudnia, ponieważ wspólnicy zgłaszali jeszcze poprawki do umowy, którą po zakończeniu wszystkich rozmów podpisał prezes Adam'),
('kot', 'Pod krzesłem śpi nasz rudy', 'Zwycięzcą zawodów został zawodnik Maciej',
 'Po powrocie do mieszkania szukaliśmy zwierzaka w kuchni, na balkonie i za kanapą, aż w końcu okazało się, że pod krzesłem spokojnie śpi nasz rudy',
 'Przez cały weekend śledziliśmy transmisję zawodów i wyniki kolejnych prób, a po ostatniej serii komentator ogłosił, że zwycięzcą został polski skoczek narciarski Maciej'),
('wilk', 'Przez drogę przebiegł samotny szary', 'W zastępstwie dyrektora wystąpił Marek',
 'Strażnik parku opowiadał nam o zwierzętach żyjących w pobliskim lesie i radził zachować ciszę, bo niedaleko miejsca, w którym staliśmy, pojawił się samotny szary',
 'Dyrektor nie mógł przyjechać na spotkanie z rodzicami, dlatego przesłał pisemne stanowisko szkoły i poprosił swojego zastępcę o przedstawienie zmian; głos zabrał Marek'),
('koza', 'Za drewnianym płotem pasie się biała', 'Tę decyzję zatwierdził dyrektor Paweł',
 'Przyjechaliśmy na wieś wczesnym rankiem i zajrzeliśmy do gospodarstwa, gdzie dzieci karmiły zwierzęta, a za drewnianym płotem obok starej stodoły spokojnie pasła się biała',
 'Firma długo szukała odpowiedniego wykonawcy remontu, porównywała oferty i terminy prac, a po zakończeniu negocjacji ostateczną decyzję zatwierdził nowy dyrektor, który nazywa się Paweł'),
('wrona', 'Na latarni siedzi czarna', 'Medal odebrał siatkarz Andrzej',
 'Podczas oczekiwania na autobus obserwowałem puste podwórko, mokre drzewa i samochody przejeżdżające przez skrzyżowanie, aż nagle na latarni przy przystanku usiadła duża czarna',
 'Po zakończeniu meczu kibice zostali jeszcze na trybunach, by zobaczyć ceremonię wręczenia nagród, podczas której medal za udział w turnieju odebrał siatkarz Andrzej'),
('sikora', 'Na gałęzi skacze mała', 'Wyniki ogłosił trener Tomasz',
 'Zimą regularnie uzupełniamy karmnik na balkonie i obserwujemy ptaki przez szybę, a dziś jako pierwsza na cienkiej gałęzi obok pojemnika pojawiła się mała',
 'Trening rozpoczął się później niż zwykle, ponieważ zawodnicy musieli jeszcze sprawdzić sprzęt, a po zakończeniu ostatniego ćwiczenia wyniki całej grupy ogłosił trener Tomasz'),
('kula', 'Z lufy wypadła metalowa', 'Za projekt odpowiada inżynier Piotr',
 'W muzeum pokazano nam starą armatę, wyjaśniono sposób jej ładowania i przedstawiono sprzęt używany podczas ćwiczeń, a obok na drewnianym stojaku leżała ciężka metalowa',
 'Przy budowie nowego mostu pracuje kilka zespołów, które muszą uzgodnić harmonogram i zasady kontroli jakości, a za całość projektu odpowiada doświadczony inżynier Piotr'),
('mucha', 'Do szklanki wpadła niewielka', 'Na scenę wszedł aktor Leszek',
 'Przez otwarte okno do kuchni dostało się kilka owadów, więc zamknęliśmy drzwi i przykryliśmy jedzenie, ale do pozostawionej na stole szklanki zdążyła wpaść mała',
 'Widzowie długo czekali na rozpoczęcie przedstawienia, ponieważ trzeba było poprawić dekoracje i sprawdzić światła, a po podniesieniu kurtyny jako pierwszy na scenę wszedł aktor Leszek'),
('wierzba', 'Nad strumieniem rośnie stara', 'Wniosek podpisał urzędnik Adam',
 'Po przejściu przez most skręciliśmy w wąską ścieżkę biegnącą wzdłuż brzegu, gdzie pomiędzy trzcinami i mokrymi kamieniami rosła pochylona nad strumieniem stara',
 'Sprawa wymagała sprawdzenia kilku dokumentów i uzupełnienia danych w rejestrze, dlatego dopiero po zakończeniu wszystkich czynności gotowy wniosek podpisał odpowiedzialny za niego urzędnik Adam'),
('orzeł', 'Nad skalnym szczytem krążył ogromny', 'Do komisji dołączył radny Piotr',
 'Wędrowaliśmy od rana stromą ścieżką i zatrzymaliśmy się na odpoczynek przy schronisku, kiedy nad skalnym szczytem, wysoko ponad linią lasu, pojawił się ogromny',
 'Komisja miała już zakończyć obrady, lecz przewodniczący zaproponował jeszcze omówienie planu remontów ulic, a do rozmowy po krótkiej przerwie dołączył radny Piotr'),
('ryś', 'Między drzewami przemknął cętkowany', 'Zebraniu przewodniczył profesor Grzegorz',
 'Podczas zimowej wyprawy długo szukaliśmy śladów zwierząt w śniegu, a gdy zapadła cisza, pomiędzy drzewami na drugim brzegu potoku przemknął duży cętkowany',
 'Organizatorzy spotkania zaprosili przedstawicieli kilku uczelni, żeby wspólnie omówić program konferencji i zaplanować kolejne wystąpienia, a całemu zebraniu przewodniczył profesor Grzegorz'),
]


def build(pack):
    data = pack.read_bytes()
    if hashlib.sha256(data).hexdigest() != PACK_SHA:
        raise ValueError('wrong full source pack')
    with zipfile.ZipFile(pack) as z:
        side = z.read('language-intelligence.json')
    if hashlib.sha256(side).hexdigest() != SIDECAR_SHA:
        raise ValueError('wrong sidecar')
    source = json.loads((ROOT.parent/'ai_compare_v5/source-snapshot.json').read_text())
    full = {e['surfaceKey']:e for e in json.loads(side)['entries']}
    # Verbatim attested entries; no crafted per-word source descriptions.
    entries = {e['surfaceKey']:e for e in source['entries']}
    entries.update({row[0]:full[row[0]] for row in TEXTS})
    source['entries'] = [entries[k] for k in sorted(entries)]
    source['diagnosticExtraction'] = {'fullPackSha256': PACK_SHA, 'sidecarSha256': SIDECAR_SHA,
                                    'authoredContexts': True, 'externalIndependentBenchmark': False}
    old = json.loads((ROOT.parent/'polish_mlm_compare_v1/new-cases.json').read_text())['cases']
    old_keys = {c['candidates'][0]['key'] for c in old if c['suite']=='forms'}
    cases = []
    for key, *contexts in TEXTS:
        surfaces = {v['surface'] for v in entries[key]['capitalization']['variants']}
        if surfaces != {key,key[0].upper()+key[1:]}:
            raise ValueError('not an exact source pair: '+key)
        for i, text in enumerate(contexts):
            gold = key if i%2==0 else key[0].upper()+key[1:]
            length = 'short' if i<2 else 'long'
            cases.append({'id':f'fresh-{key}-{length}-{i%2}', 'leftContext':text,
                          'goldSurface':gold, 'population':f'fresh_{length}_'+('known_key' if key in old_keys else 'new_key'),
                          'suite':'forms', 'candidates':[{'key':key,'engineScore':100}]})
    regression = json.loads((ROOT.parent/'ai_compare_v5/cases.json').read_text())['cases']
    cases += [{**c,'id':'regression/'+c['id'],'population':'regression_v5'}
              for c in regression if c['suite']=='forms']
    (ROOT/'source-snapshot.json').write_text(json.dumps(source,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    (ROOT/'cases.json').write_text(json.dumps({'authoredBeforeInference':True,'cases':cases},ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'cases':len(cases),'fresh':64,'lengths':sorted({len(c['leftContext'].split()) for c in cases[:64]})}))


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--pack',type=Path,required=True);build(p.parse_args().pack)
