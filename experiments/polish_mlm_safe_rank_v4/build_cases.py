"""New authored validation texts, after development calibration, before inference."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
# lower-short, upper-short, lower-long, upper-long. Metadata is copied, not authored.
TEXTS = {
    'łódź': [
        'Przy pomostach kołysała się niewielka',
        'Na mapie trasy zaznaczyliśmy miasto',
        'Rybak sprawdził pogodę i przygotował sieci, zanim wyszedł z domu nad jezioro. Obok pomostu czekała na niego stara, ale nadal sprawna',
        'Wybieramy miejsce na spotkanie zespołu z kilku regionów kraju. Po porównaniu połączeń kolejowych organizatorzy uznali, że najwygodniejszym miastem dla wszystkich będzie',
    ],
    'malina': [
        'Na krzaku została ostatnia dojrzała',
        'Formularz sprawdziła księgowa pani',
        'Dzieci zbierały owoce w ogrodzie i odkładały je do koszyka. Na najwyższej gałązce została jeszcze jedna czerwona, bardzo słodka i dojrzała',
        'Przed zamknięciem biura pracownicy uporządkowali dokumenty i policzyli wszystkie załączniki. Zgodność zestawienia z fakturami potwierdziła swoim podpisem odpowiedzialna za rozliczenia pani',
    ],
    'warszawska': [
        'Przyjechała do nas delegacja',
        'Uchwałę odczytała radna pani',
        'W zawodach uczestniczyły drużyny z całego kraju i każda miała własną koszulkę. W końcowej klasyfikacji najwięcej punktów zdobyła młoda reprezentacja sportowa',
        'Po omówieniu wszystkich spraw przewodniczący poprosił o odczytanie przygotowanej uchwały. Przy mikrofonie stanęła radna, której nazwisko zapisano w protokole jako pani',
    ],
    'buk': [
        'W parku wyrósł okazały',
        'Wniosek złożył mieszkaniec pan',
        'Leśniczy oprowadzał uczniów po starym parku i wyjaśniał różnice między gatunkami drzew. Obok kamiennej ścieżki rósł wysoki, rozłożysty i wyjątkowo zdrowy',
        'W urzędzie sprawdzono dokumenty wszystkich mieszkańców ubiegających się o pozwolenie. Ostatni kompletny wniosek wraz z wymaganymi załącznikami złożył osobiście pan',
    ],
    'kruk': [
        'Na płocie usiadł czarny',
        'Operację przeprowadził chirurg doktor',
        'Obserwatorzy ptaków ustawili aparat przy skraju lasu i czekali cierpliwie na ruch. Po kilku minutach na drewnianym ogrodzeniu usiadł duży czarny',
        'Rodzina pacjenta czekała na wiadomości po zakończeniu zabiegu i rozmawiała z pielęgniarką. Za przebieg operacji odpowiadał doświadczony chirurg, znany jako doktor',
    ],
    'zając': [
        'Wśród kapusty schował się',
        'Pismo odebrał adresat pan',
        'Rolnik zauważył ślady na grządkach i postanowił obejrzeć ogród przed śniadaniem. Pomiędzy rzędami kapusty, tuż przy niskim drewnianym płocie, schował się',
        'Listonosz przyniósł przesyłkę poleconą do sąsiedniego budynku i sprawdził dane na kopercie. Odbiór pisma potwierdził osobiście mężczyzna przedstawiający się jako pan',
    ],
    'kot': [
        'Na parapecie mruczał nasz',
        'Zamówienie przyjął sprzedawca pan',
        'Wieczorem zamknęliśmy okna i zapaliliśmy lampę w salonie, żeby spokojnie poczytać. Na szerokim parapecie, obok doniczki z kwiatami, głośno mruczał nasz',
        'Klient przyszedł do sklepu z listą części i poprosił o sprawdzenie ich dostępności. Zamówienie przyjął sprzedawca, który na identyfikatorze miał nazwisko',
    ],
    'wilk': [
        'Za drzewami przemykał samotny',
        'Zebranie poprowadził dyrektor pan',
        'Strażnik sprawdził nagranie z kamery ustawionej przy leśnym dukcie i przybliżył obraz. Pomiędzy wysokimi drzewami, daleko od zabudowań, powoli przemykał samotny',
        'Pracownicy zebrali się rano w sali konferencyjnej, aby omówić plan na kolejny miesiąc. Spotkanie rozpoczął i osobiście poprowadził dyrektor zakładu pan',
    ],
    'koza': [
        'Przy zagrodzie skubała trawę',
        'Rozliczenie podpisał właściciel pan',
        'Gospodarz otworzył furtkę i przyniósł zwierzętom świeżą wodę, zanim zrobiło się gorąco. Przy drewnianej zagrodzie spokojnie skubała zieloną trawę młoda biała',
        'Po zakończeniu remontu wykonawca przygotował zestawienie kosztów i przekazał je do zatwierdzenia. Rozliczenie odebrał oraz podpisał właściciel domu przedstawiający się jako',
    ],
    'wrona': [
        'Nad trawnikiem krążyła hałaśliwa',
        'Konkurs oceniła jurorka pani',
        'Ogrodnik rozsypał nasiona na przygotowanej ziemi i poszedł po konewkę do szopy. Nad świeżo obsianym trawnikiem krążyła już jedna wyjątkowo hałaśliwa',
        'Uczestnicy konkursu czekali za kulisami na ogłoszenie wyników i ostateczną ocenę występów. W imieniu komisji werdykt odczytała przewodnicząca jury pani',
    ],
    'sikora': [
        'Do karmnika przyleciała mała',
        'Listę sprawdziła sekretarka pani',
        'Zimą regularnie uzupełniamy nasiona w karmniku zawieszonym przy kuchennym oknie i obserwujemy odwiedzające go ptaki. Dzisiaj pierwsza przyleciała niewielka ruchliwa',
        'Przed rozpoczęciem zebrania trzeba było potwierdzić obecność zaproszonych gości i przygotować identyfikatory. Aktualną listę nazwisk sprawdziła zatrudniona w biurze sekretarka pani',
    ],
    'kula': [
        'Po stole potoczyła się',
        'Projekt zatwierdził inżynier pan',
        'Uczniowie wykonywali doświadczenie z ruchem i nachyleniem powierzchni, zapisując wyniki w zeszytach. Po gładkim stole powoli potoczyła się mała metalowa',
        'Zespół przygotował rysunki techniczne oraz obliczenia potrzebne do przebudowy hali i przekazał je do sprawdzenia. Projekt zatwierdził odpowiedzialny za konstrukcję inżynier',
    ],
    'mucha': [
        'Przy lampie brzęczała uparta',
        'Reklamację rozpatrzyła kierowniczka pani',
        'Zamknęliśmy okno, żeby chłodne powietrze nie wpadało do pokoju, i wróciliśmy do czytania. Przy zapalonej lampie nadal brzęczała jedna bardzo uparta',
        'Klient zgłosił uszkodzenie zakupionego produktu i dołączył zdjęcia oraz paragon do formularza. Reklamację rozpatrzyła osobiście kierowniczka działu obsługi klienta pani',
    ],
    'wierzba': [
        'Nad stawem rosła stara',
        'Wyniki omówiła badaczka doktor',
        'Spacerowaliśmy ścieżką przy wodzie i szukaliśmy spokojnego miejsca, w którym można odpocząć w cieniu. Nad niewielkim stawem rosła stara rozłożysta',
        'Po zakończeniu pomiarów zespół zebrał wszystkie dane i przygotował wykresy na konferencję naukową. Wyniki doświadczenia szczegółowo omówiła kierująca badaniami doktor',
    ],
    'orzeł': [
        'Wysoko nad skałami szybował',
        'Decyzję ogłosił sędzia pan',
        'Turyści zatrzymali się na górskim szlaku, aby podziwiać widok i zrobić kilka zdjęć. Wysoko nad stromymi skałami, bez poruszania skrzydłami, szybował',
        'Po wysłuchaniu zawodników komisja zakończyła obrady i poprosiła wszystkich uczestników o podejście do stolika. Ostateczną decyzję dotyczącą wyniku spotkania ogłosił sędzia',
    ],
    'ryś': [
        'Na skraju lasu pojawił się',
        'Umowę przygotował prawnik pan',
        'Pracownicy parku narodowego przeglądali zdjęcia z fotopułapek i zaznaczali na mapie miejsca obserwacji zwierząt. Na skraju gęstego lasu pojawił się samotny',
        'Przed podpisaniem dokumentów wspólnicy poprosili o sprawdzenie wszystkich zapisów i wyjaśnienie kwestii odpowiedzialności. Ostateczną wersję umowy przygotował współpracujący z firmą prawnik',
    ],
}


def build():
    previous = json.loads((ROOT.parent/'polish_mlm_fresh_v3/cases.json').read_text())['cases']
    source = json.loads((ROOT.parent/'polish_mlm_fresh_v3/source-snapshot.json').read_text())
    entries = {e['surfaceKey']: e for e in source['entries']}
    known = {'łódź','malina','warszawska','buk','kruk','zając','kot','wilk'}
    old_contexts = {c['leftContext'] for c in previous}
    cases = []
    for key,texts in TEXTS.items():
        forms = [v['surface'] for v in entries[key]['capitalization']['variants']]
        for i,text in enumerate(texts):
            short, upper = i < 2, i % 2 == 1
            gold = next(f for f in forms if f[0].isupper() == upper)
            assert text not in old_contexts
            assert len(text.split()) <=16 if short else 17<=len(text.split())<=32, (key,len(text.split()))
            cases.append({'id':f'validation/{key}/{i}', 'suite':'forms',
                          'population':f"fresh_{'short' if short else 'long'}_{'known_key' if key in known else 'new_key'}",
                          'leftContext':text, 'candidates':[{'key':key,'geometryRank':0}],
                          'goldSurface':gold})
    # Explicit development replay, never treated as unseen validation.
    cases += [c for c in previous if c['population']=='regression_v5']
    (ROOT/'cases.json').write_text(json.dumps({'cases':cases},ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    (ROOT/'source-snapshot.json').write_bytes((ROOT.parent/'polish_mlm_fresh_v3/source-snapshot.json').read_bytes())
    print('64 new authored contexts + 64 marked development replay; source metadata unchanged')


if __name__ == '__main__':build()
