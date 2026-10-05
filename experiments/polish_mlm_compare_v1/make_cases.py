"""New authored probes; all lexical alternatives come from the frozen source snapshot."""
import json
from pathlib import Path

ROOT = Path(__file__).parent
NATURAL = {
    'łódź': ('Podczas postoju załoga zauważyła przeciek w kadłubie, dlatego do naprawy trafiła nasza',
             'Po przejrzeniu ofert muzeów i połączeń kolejowych uznaliśmy, że celem weekendowej podróży będzie'),
    'malina': ('Ogrodnik pokazał mi krzew owocowy, na którym po ostatnich deszczach dojrzała pierwsza',
               'W przychodni poproszono mnie o nazwisko lekarza prowadzącego i odpowiedziałem doktor'),
    'jagoda': ('Wśród owoców zerwanych podczas spaceru po lesie znalazła się jedna szczególnie słodka',
               'Koleżanka z kursu przedstawiła swoją córkę i powiedziała, że dziewczynka ma na imię'),
    'róża': ('Na konkursie ogrodniczym jury wyróżniło kwiat z naszej rabaty, którym była czerwona',
             'W sekretariacie zapytałem o imię nowej nauczycielki, a pracownik odpowiedział pani'),
    'warszawska': ('Porównując transport w kilku polskich aglomeracjach, zauważyliśmy, że najlepiej rozbudowana jest sieć',
                  'Po zmianie numeracji sprawdziłem nazwę ulicy na tabliczce przy domu i odczytałem ulica'),
    'ale': ('Przygotowałem dokumenty i zarezerwowałem termin wizyty,',
            'Dwie uczennice noszą imię Ala i obie dostały wyróżnienie, więc na scenę weszły dwie'),
    'lub': ('W zależności od pogody pojedziemy na miejsce autobusem',
            'Dwie sąsiadki mają imię Luba, a zarządca nadal nie zna telefonów do obu'),
    'tutaj': ('Sprawdziłem wskazówki na mapie i poprosiłem kierowcę, aby zatrzymał samochód właśnie',
              'W formularzu trzeba wpisać nazwisko właściciela lokalu, a w umowie widnieje pan'),
    'lis': ('Przyrodnik ustawił kamerę obok nory i na pierwszym nagraniu pojawił się rudy',
            'Recepcjonistka sprawdziła rezerwację i potwierdziła, że gość ma na nazwisko'),
    'wilk': ('Po analizie tropów w śniegu leśnicy uznali, że nocą przeszedł tędy samotny',
             'Po odczytaniu listy kandydatów przewodnicząca ogłosiła nazwisko wybranego prezesa, którym został pan'),
    'kruk': ('Ornitolog obserwował ptaki nad polaną, aż na wierzchołku sosny usiadł czarny',
             'Na odwrocie obrazu znaleźliśmy podpis autora i ustaliliśmy, że jego nazwisko brzmi'),
    'sowa': ('Wolontariuszka ośrodka rehabilitacji ptaków pokazała nam nocnego drapieżnika, którym była młoda',
             'Po telefonie do kancelarii dowiedziałem się, że sprawę prowadzi mecenas'),
    'piła': ('Stolarz sprawdził wyposażenie warsztatu i uznał, że do cięcia desek potrzebna będzie ręczna',
             'Patrząc na mapę północnej Wielkopolski, wybraliśmy miasto z dobrym połączeniem kolejowym, czyli'),
    'buk': ('Podczas spaceru dendrolog opisał korę i liście drzewa, po czym stwierdził, że to',
            'Na umowie najmu widnieje podpis właściciela, którego nazwisko to'),
    'zając': ('W czasie liczenia zwierząt przy polu zauważyliśmy długie uszy, a potem wyskoczył szary',
              'Na konferencji poprosiłem o nazwisko prelegenta i usłyszałem profesor'),
    'kot': ('Po powrocie z zakupów usłyszałem miauczenie przy drzwiach, gdzie czekał nasz',
            'Kurier zapytał o nazwisko adresata przesyłki i na etykiecie znalazł pan'),
}
DISTANT = {
    'łódź': ('Załoga sprawdza sprzęt pływający przed rejsem.', 'Planujemy wycieczkę do miasta w centralnej Polsce.'),
    'malina': ('Zbieramy dojrzałe owoce z krzewów na działce.', 'Weryfikujemy nazwiska pracowników odpowiedzialnych za dokument.'),
    'jagoda': ('Oglądamy owoce zebrane na leśnej polanie.', 'Rodzice uzgadniają imię nowo narodzonej córki.'),
    'róża': ('Porównujemy kwiaty posadzone na słonecznej rabacie.', 'Ustalamy imię nowej koleżanki z zespołu.'),
    'warszawska': ('Porównujemy miejskie oferty, szczególnie te ze stolicy.', 'Odczytujemy nazwę ulicy z miejskiego wykazu.'),
    'ale': ('Wypowiedź przeciwstawia sobie dwa możliwe rezultaty.', 'Obie uczestniczki mają na imię Ala.'),
    'lub': ('Zdanie daje wybór między dwiema możliwościami.', 'Obie właścicielki lokali mają imię Luba.'),
    'tutaj': ('Wskazujemy miejsce, w którym właśnie stoimy.', 'Sprawdzamy nazwiska osób zatrudnionych w urzędzie.'),
    'lis': ('Rozmowa dotyczy rudych zwierząt z pobliskiego lasu.', 'Sprawdzamy nazwisko autora podpisanego protokołu.'),
    'wilk': ('Opisujemy drapieżniki obserwowane przy granicy lasu.', 'Sprawdzamy nazwisko nowego kierownika placówki.'),
    'kruk': ('Liczymy czarne ptaki siedzące na drzewach.', 'Rozmowa dotyczy nazwiska właściciela galerii.'),
    'sowa': ('Omawiamy nocne ptaki przyjęte do ośrodka.', 'Weryfikujemy nazwisko kobiety prowadzącej naszą sprawę.'),
    'piła': ('Opisujemy narzędzia służące do cięcia drewna.', 'Przeglądamy miasta położone w północnej Wielkopolsce.'),
    'buk': ('Opisujemy drzewa o gładkiej szarej korze.', 'Ustalamy nazwisko osoby podpisującej nową umowę.'),
    'zając': ('Obserwujemy zwierzęta o długich uszach na łące.', 'Sprawdzamy nazwisko profesora prowadzącego badania.'),
    'kot': ('Rozmawiamy o domowych zwierzętach, które miauczą.', 'Odczytujemy nazwisko adresata dostarczonej przesyłki.'),
}
# Deliberate distance control, reported separately from natural diagnostics.
BRIDGE = (' Informację sprawdzono, porównano wcześniejsze zapisy, omówiono wyniki '
          'podczas spotkania, a po zakończeniu rozmowy ustalono, że brakujący wpis to')
PUNCT = [
    ('Sprawdziłem w wiadomości', 'czy', ','),
    ('Nie wiedziałam jeszcze', 'kiedy', ','),
    ('Prześlę dokumenty', 'jeżeli', ','),
    ('Poprosił o pomoc', 'ponieważ', ','),
    ('Zapisz godzinę', 'zanim', ','),
    ('Wróciliśmy wcześniej', 'żeby', ','),
    ('Próbowałem zadzwonić', 'ale', ','),
    ('To jest adres', 'który', ','),
    ('Nie kupili nowego', 'lecz', ','),
    ('Nie miała czasu', 'więc', ','),
    ('Zrobię to dziś', 'chociaż', ','),
    ('Zostałem na miejscu', 'bo', ','),
    ('Zabierz zeszyt', 'i', ''),
    ('Wybierz pociąg', 'albo', ''),
    ('Możesz zamówić herbatę', 'lub', ''),
    ('Nie zna adresu', 'ani', ''),
    ('Spotkamy się', 'przy', ''),
    ('Zostawiłem przesyłkę', 'obok', ''),
    ('Potwierdzenie dostaniesz', 'jutro', ''),
    ('Dokończymy rozmowę', 'później', ''),
    ('Spójrz na ekran', 'telefonu', ''),
    ('Wyślij wiadomość', 'teraz', ''),
    ('Usiądź przy stole', 'tutaj', ''),
    ('Otwórz folder', 'ze', ''),
]


def build():
    rows = []
    for population, pairs in [('new_natural', NATURAL), ('new_distance_control', DISTANT)]:
        for key, contexts in pairs.items():
            for index, context in enumerate(contexts):
                if population == 'new_distance_control':
                    context += BRIDGE
                    assert 16 < len(context.split()) <= 32
                    assert context.split()[0] not in context.split()[-16:]
                rows.append({'id': f'{population}-{key}-{index}', 'suite': 'forms',
                             'population': population, 'leftContext': context,
                             'candidates': [{'key': key, 'engineScore': 100}],
                             'goldSurface': key if index == 0 else key[0].upper() + key[1:]})
    for index, (context, word, punctuation) in enumerate(PUNCT):
        rows.append({'id': f'new-punctuation-{index}', 'suite': 'punctuation_before_word',
                     'population': 'new_punctuation', 'leftContext': context,
                     'nextWord': word, 'options': ['', ','], 'goldPunctuation': punctuation})
    return {'schemaVersion': 1, 'kind': 'new-authored-known-lexemes-not-external-blind-test', 'cases': rows}


if __name__ == '__main__':
    (ROOT / 'new-cases.json').write_text(json.dumps(build(), ensure_ascii=False, sort_keys=True, indent=2) + '\n')
