# Audyt metadanych opartych na źródłach — 2026-10-02

Użytkownik skorygował założenie: AI ma korzystać z atrybutów obecnego słownika albo danych możliwych do automatycznego pozyskania z dostępnych baz. Nie tworzymy ręcznie opisów znaczeń dla każdego słowa. Dotychczasowe SENSE/NATURAL były diagnostyką na ręcznych fixture’ach; ich wyniki nie dowodzą skuteczności na rzeczywistych metadanych.

## Co jest rzeczywiście dostępne

Aktualny kod main langpack ab99eb7b287932f78620d57782662333e1297c2a pobrano z GitHub. Morfeusz 2 jest już źródłem projektu. Użyto przypiętej wersji 1.99.15 i słownika pl.sgjp.sgjp-2026.06.01 / tagset pl.sgjp.morfeusz-0.8.0, zgodnie z istniejącym inventory. Nie zmieniono źródeł produkcji.

Wrapper zwraca orth, lemma, tag, nameClasses, labels. TAG opisuje gramatykę, NAME klasy nazwowe, LABELS kwalifikatory. To różne warstwy. Kod capitalization_rules.py zachowuje lemat/tag/klasy, ale jego _payload pomija piąte pole LABELS. audit_core_capitalization.py zapisuje część dowodów i rozstrzygnięć do raportów budowy; nie eksportuje pełnego inwentarza dla AI.

Preview workflow nadal sprawdza dokładnie trzy pliki pakietu: dictionary.bin, manifest.json, unigrams.txt. Pobrany ZIP potwierdził te trzy pliki. Produkcyjny sidecar inteligencji nie istnieje; API v1 pozostaje projektem. Brak metadanych w ZIP nie oznacza braku danych w pipeline.

## Pochodzenie i zakres pomiaru

Ostatni udany run preview znaleziony w historii: [36916501466](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/36916501466), source commit a1fa0193fc504e5fe81d9d43c23fd9a1e52ad307. Artefakt 11189614575 cleverkeys-pl-preview:
SHA256 827a20f8489fad51023e1c0d58319dca030d304f7e213ef4973141251c3ad9ff.

To historyczny udany build, nie regeneracja dzisiejszego main. Nie utożsamiać go ze wszystkimi obecnymi politykami. W tym etapie nie przebudowano 100k ani modułów, nie zmieniono CKDT, ZIP-a i Androida.

Audyt wykonano na 106363 rzeczywistych surfaces z pl_words_preview.txt po usunięciu dwóch komentarzy. Parsowanie sekcji słów CKDT V2 potwierdziło równość zbiorów dokładnych surfaces z tekstem, zgodność wordCount z manifestem oraz unikalność kluczy lowercase. Zbiór obejmuje rdzeń i dodatki; nie mamy wyeksportowanego base100k.txt i nie raportujemy osobnego pokrycia rdzenia.

Każdy klucz badano w formie lowercase i z wielką pierwszą literą, ustawienie CONDITIONALLY_CASE_SENSITIVE. Uznawano wyłącznie znane analizy pełnego pojedynczego tokenu; odrzucano ign i częściowe segmentacje. Zachowano surowe lematy, klasy i kwalifikatory dla dziewięciu przykładów; dla całego zbioru tylko agregaty.

| Wskaźnik | Klucze |
|---|---:|
| Zbadane | 106363 |
| Rozpoznana pełna analiza w co najmniej jednym probe | 102203 (96,09%) |
| Brak rozpoznanej pełnej analizy | 4160 |
| Co najmniej jedna klasa NAME | 56497 |
| Co najmniej jeden kwalifikator LABELS | 8813 |
| Więcej niż jeden lemat | 29970 |
| Więcej niż jedna część mowy | 16500 |
| nazwa_pospolita i dodatkowa klasa NAME | 12459 |

Kategorie mogą się nakładać. Wieloznaczność jest wynikiem analizy, nie błędem i nie dowodem wszystkich znaczeń w użyciu. Pokrycie jest rozpoznaniem morfologicznym, nie jakością kapitalizacji czy AI. Zbiór nazw to nie rejestr osób/miejsc, a brak analizy nie dowodzi nieistnienia słowa.

## Przykłady z rzeczywistego źródła

| Klucz | Potwierdzone dane | Granica wiedzy |
|---|---|---|
| łódź | subst; nazwa_pospolita oraz nazwa_geograficzna; SIMC Łódź, RM=96, ID 0957650 | Miasto potwierdza SIMC; NAME samo nie rozróżnia miasta od innych obiektów geograficznych. Nie ma definicji jednostki pływającej. |
| łodzi | lematy łódź, Łódź, Łodzia; klasy pospolita/geograficzna; generated city forms Łodzi | Dwa znaczenia ręcznego fixture nie wyczerpują analiz. |
| łódzki | adj, lemat łódzki; brak NAME w tej wersji | Nie potwierdzono nazwiska Łódzki ani jawnego powiązania słowotwórczego z miastem. |
| malina | subst; pospolita, imię, nazwisko, geograficzna; lemat Malin też jako forma fleksyjna; osobny rekord imienia Malina | Brak etykiety owoc. Nie sprowadzać wszystkich analiz do owocu i nazwiska. |
| jagoda | subst; pospolita, imię, nazwisko; rekord imienia Jagoda | Brak etykiety owoc. |
| róża | subst; pospolita, imię, nazwisko, geograficzna; rekord imienia Róża | Brak etykiety kwiat. |
| polska | adj/adjp/subst; lematy polski:A oraz Polska; geograficzna i nazwisko | Nie sprowadzać automatycznie do kraju/przymiotnika; kategorię kraju może potwierdzić osobny KSNG. |
| warszawska | adj z lematem warszawski oraz subst nazwisko Warszawska | Nazwa ulicy nie pochodzi z tych analiz. |
| warszawski | adj oraz subst nazwisko Warszawski | Forma przymiotnikowa i nazwisko są źródłowo potwierdzone. |

Szczegółowe tuple, tagi, wersje i wybrane rekordy SIMC/imion: source-metadata-audit.json. NAME obejmuje również klasy członów nazw. Nie utożsamiać członu nazwy z całą nazwą ani NAME z drobnymi znaczeniami słownikowymi. Zachowywać kombinacje klas przy konkretnym lemacie; nie tworzyć wszystkich iloczynów lemat×klasa×tag.

## Dostępne rozszerzenia i ich status

Istniejące źródła projektu: Morfeusz/SGJP, SIMC miasta, TERC jednostki administracyjne, KSNG kraje/stolice, statystyki imion i ich wygenerowane formy. Każdy rekord wymaga źródła, wersji/stanu, identyfikatora i dowodu powiązania z formą. Sama przynależność do modułu nie zastępuje analizy powierzchni.

Dwa potwierdzone publiczne kierunki rozszerzenia:
- [GUS ULIC](https://eteryt.stat.gov.pl/eTeryt/rejestr_teryt/informacje_podstawowe/informacje_podstawowe.aspx): nazwy ulic oraz identyfikatory i lokalizacje. [Struktura](https://eteryt.stat.gov.pl/eTeryt/rejestr_teryt/udostepnianie_danych/baza_teryt/uzytkownicy_indywidualni/pobieranie/pliki_pelne_struktury.aspx) i [pobieranie](https://eteryt.stat.gov.pl/eTeryt/rejestr_teryt/udostepnianie_danych/baza_teryt/uzytkownicy_indywidualni/pobieranie/pobieranie.aspx). Nie pobrano/nie wdrożono; nie twierdzimy, że konkretny rekord Warszawska został w tym etapie potwierdzony.
- [Zestaw nazwisk PESEL](https://dane.gov.pl/pl/dataset/1681%2Cnazwis): statystyka nazwisk osób żyjących; opis wyłącza pojedyncze wystąpienia. Nie pobrano, nie sprawdzono najnowszego pliku/licencji i nie potwierdzono wpisu Łódzki.

Te kierunki mogą dodać kategorie, nie pełne definicje owocu/kwiatu/przedmiotu. Nie potrzeba pełnych definicji, by zmierzyć użyteczność istniejących klas. Osobna baza semantyczna wymagałaby osobnego audytu pokrycia, mapowania i licencji; nie jest warunkiem pierwszego testu kategorii.

## Korekta kontraktu eksperymentu

1. Jeden klucz lowercase i dopuszczalne warianty pozostają zasadą.
2. Pod kluczem zachowujemy wszystkie źródłowo potwierdzone interpretacje: lemma, tag, NAME, LABELS, identyfikatory źródeł. To candidate interpretations, nie ręcznie napisane sense descriptions.
3. Nie tworzymy etykiet fruit/boat/street/surname, jeżeli nie wynikają z przyjętego źródła. Dotyczy to także przykładów wcześniej uznanych intuicyjnie.
4. Ogólny, zamrożony szablon może przedstawić modelowi kategorię źródłową. Nie dodaje per-word wiedzy. Wariant kategorii i porównanie z systemem bez kategorii muszą zostać zapisane przed inferencją.
5. NAME nie musi być niepuste: przymiotnik łódzki ma użyteczny TAG, choć brak klasy NAME. Puste NAME nie oznacza automatycznie nazwy pospolitej. LABELS nie zastępuje NAME.
6. orth analizy po wielkiej literze jest tekstem wejściowym: samo orth nie dowodzi właściwej kapitalizacji leksemu. Powiązanie interpretacja→wariant musi opierać się na lemacie i dowodach źródłowych/polityce, z oddzielnym autocap.
7. Łódź/łódź i Łódzki/łódzki są różnymi kluczami. Nie dopisywać derywacji ani odmiany przez ręczne zgadywanie.
8. Brak danych zachowuje fallback i alternatywy, nie powoduje odrzucania poprawnego słowa.
9. Zachowujemy lexical order oraz engineScore; główne kryterium poprawny klucz i dokładny zapis w top 3, top 1 dodatkowo.
10. Nie wybierać HerBERT tylko dlatego, że wygrał próbę bez metadanych. Kolejny test ma zmierzyć realne wykorzystanie danych źródłowych.

## Walidacja, granice i następny krok

audit_source_metadata.py odtwarza agregaty i dziewięć przykładów z przypiętego artefaktu. SHA256 wejścia, pakietu, dictionary.bin, wordlisty i wybranych TSV zapisane w JSON. Weryfikacje runtime: dokładna wersja/słownik, hash archiwum, liczność manifestu, unikalność kluczy, zgodność CKDT i tekstu, obecność wszystkich dziewięciu przykładów. Powtórny audit wykonano po dodaniu sprawdzenia CKDT. Nie wykonano inferencji AI ani Android CI w tym etapie.

Przed kolejnym pomiarem trzeba wygenerować źródłowe wejście modelu i bezpieczne powiązanie interpretacji z wariantami, oddzielić NAME/POS od niepotwierdzonych znaczeń i zamrozić protokół. Pierwszy test może użyć kategorii już dostępnych; źródła ULIC/PESEL są osobnym rozszerzeniem.

Poprzednie 66 testów i sukcesy CI dotyczą NATURAL, nie są nowym testem tego audytu. Wszystkie historyczne wyniki pozostawiono bez zmian. Kryterium tokenizacji nadal otwarte, ale audyt realnych atrybutów ma teraz pierwszeństwo przed dalszym eksperymentem ręcznych opisów.

## Autorstwo danych

Wybrane interpretacje Morfeusza/SGJP są danymi źródłowymi. Autorzy danych fleksyjnych: Zygmunt Saloni, Włodzimierz Gruszczyński, Marcin Woliński, Robert Wołosz, Danuta Skowrońska. Program: Instytut Podstaw Informatyki PAN, Copyright © 2014–2026. Dane potrzebne do analizy fleksyjnej udostępniane na BSD-2-Clause; nie jest to licencja całej publikacji SGJP. [Oficjalna licencja](https://morfeusz.sgjp.pl/doc/license/), [dokumentacja](https://morfeusz.sgjp.pl/doc/doc/), istniejące docs/PL_MORFEUSZ_SGJP_ATTRIBUTION_2026-09-24.md. Nie publikujemy pełnej bazy ani pełnej wordlisty tego artefaktu.

Warunki BSD-2-Clause dla dołączonych interpretacji:

Redystrybucja i używanie w formie źródłowej lub binarnej, z modyfikacjami lub bez, są dozwolone pod warunkiem zachowania noty copyrightowej, poniższych warunków i oświadczenia: (1) redystrybucja źródeł zachowuje je w źródłach; (2) redystrybucja binarna odtwarza je w dokumentacji lub innych materiałach.

DANE I OPROGRAMOWANIE DOSTARCZANE SĄ „TAK JAK SĄ”, BEZ JAKICHKOLWIEK GWARANCJI, W TYM PRZYDATNOŚCI HANDLOWEJ I PRZYDATNOŚCI DO KONKRETNEGO CELU. WŁAŚCICIELE PRAW I WSPÓŁTWÓRCY NIE ODPOWIADAJĄ ZA SZKODY BEZPOŚREDNIE, POŚREDNIE, PRZYPADKOWE, SZCZEGÓLNE, PRZYKŁADOWE ANI WYNIKOWE (W TYM NABYCIE DÓBR LUB USŁUG ZASTĘPCZYCH, UTRATĘ UŻYTKOWANIA, DANYCH, ZYSKÓW LUB PRZERWĘ W DZIAŁALNOŚCI), BEZ WZGLĘDU NA PRZYCZYNĘ I PODSTAWĘ ODPOWIEDZIALNOŚCI, W TYM UMOWĘ, ODPOWIEDZIALNOŚĆ ŚCISŁĄ LUB DELIKT, NAWET PO UPRZEDZENIU O MOŻLIWOŚCI TAKICH SZKÓD.

