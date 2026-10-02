# Kamień milowy — metadane wyłącznie ze źródeł

Weryfikacja: 2026-10-02 UTC. Repo: jakamilek/CleverKeys-langpack-pl.
[Stan drugiego repozytorium](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-02_SOURCE_METADATA.md).
Status: ukończony audyt źródeł i pokrycia, bez nowej inferencji AI lub integracji Android.

## 1. Zweryfikowane HEAD main przed zapisaniem obu dokumentów

- CleverKeys-langpack-pl: ab99eb7b287932f78620d57782662333e1297c2a.
- CleverKeysPL: 3af5f796524d77a91d1c5c316fc61ea955770f58.

Wspólny snapshot przed dokumentacyjnymi commitami, sprawdzony ponownie bezpośrednio przed zapisem. Main przesuwa się wyłącznie dokumentacją. Nowy audyt: cd03c3002e7164eac5d972a2a8b502873177ca09 na experiment/context-surface-window-v1, Draft PR #4. Poprzednie wyniki NATURAL: 37696cd3a4d575daf00beb833cb65b81ac7076c6.

## 2. Stan architektury

Dwa repozytoria, rdzeń 100k, CKDT V2, dodatki i fallback pozostają w stanie poprzedniego milestone’u. Pakiet dostarcza dane/model, wspólny runtime wykonuje ranking. Brak produkcyjnego generatora inteligencji i parsera/provider API v1. Nie zmieniono Androida, ZIP-a, 100k ani generatora produkcji.

Zweryfikowany main pipeline posiada metadane w raportach budowy. capitalization_rules.py zachowuje lemma/tag/NAME, ale pomija piąte pole LABELS. Pobrany ostatni udany ZIP preview ma tylko dictionary.bin, manifest.json, unigrams.txt. Metadane nie są jeszcze eksportowane do klawiatury.

## 3. Ustalenia zaakceptowane

Użytkownik odrzucił ręczne dopisywanie opisów dla każdego słowa. AI ma korzystać z danych istniejącego słownika albo dostępnych baz możliwych do automatycznego dołączenia. Ogólny szablon wejścia może przekładać kategorię na tekst, lecz nie może dodawać niepotwierdzonej wiedzy o konkretnym słowie.

Morfeusz: orth, lemma, TAG, NAME, LABELS to odrębne pola. NAME nie jest pełnym opisem znaczenia; TAG nie zastępuje NAME. Zachowujemy wszystkie potwierdzone interpretacje i ich powiązania, również dodatkowe nazwy/imiona/fleksje. Jeden klucz lowercase, warianty i autocap oddzielnie. Główne kryterium nadal dokładny zapis i klucz w top 3; lexical order i engineScore bez zmian.

Audyt 106363 rzeczywistych surfaces historycznego pakietu: 102203 rozpoznane pełne analizy (96,09%), 4160 bez pełnej analizy, 56497 z NAME, 8813 z LABELS, 12459 z nazwa_pospolita oraz dodatkową klasą NAME. To pokrycie morfologiczne, nie skuteczność AI.

## 4. Odrzucone podejścia

Ręczne fruit/boat/street nie mogą stać się produkcyjną wiedzą bez źródła. Nie zawężać malina do owocu i nazwiska: źródło daje też imię, geograficzne analizy i formę od Malin. Nie dopisywać nazwiska Łódzki: przypięty Morfeusz ma tylko przymiotnik. Warszawska ma nazwisko/przymiotnik; ulicę trzeba potwierdzić osobną bazą.

Nie traktować orth po uppercase probe jako dowodu wielkiej litery; common analyses zwracają również uppercase tekst wejściowy. Nie utożsamiać członu nazwy z całą nazwą, pustego NAME z nazwa_pospolita ani nazwy geograficznej z miastem. Nie wybierać HerBERT na podstawie przewagi testu bez metadanych.

## 5. Planowane, niewdrożone

Źródłowy generator interpretacji→warianty z proweniencją, zamrożone wejście AI oparte na rzeczywistych klasach i test z kategoriami/bez kategorii. Wszystkie dodatkowe klasy i analizowane formy muszą pozostać widoczne. Pierwszy test może użyć dostępnych danych bez pełnych definicji semantycznych.

ULIC dla nazw ulic i statystyki nazwisk PESEL to zweryfikowane kierunki źródeł, jeszcze nie pobrane/połączone. Poszczególnych wpisów Warszawska/Łódzki z tych baz nie potwierdzono. Diagnostyka tokenizacji nadal planowana, ale audyt realnych danych ma pierwszeństwo. Dłuższy InputConnection, świeżość snapshotów, tap-to-replace, uczenie użytkownika i interpunkcja pozostają niewdrożone.

## 6. Niezweryfikowane

Brak nowego pomiaru AI na źródłowych metadanych, generalizacji i kosztu telefonu. Nieznane pokrycie poza ostatnim udanym artefaktem; nie wyznaczono osobnego pokrycia rdzenia 100k. Nie pobrano aktualnych danych ULIC/PESEL ani nie ustalono licencji konkretnego pliku nazwisk. Brak semantycznych definicji owocu/kwiatu/przedmiotu w zbadanych interpretacjach.

Historyczny build nie jest regeneracją dzisiejszego main; nie utożsamiać go ze wszystkimi obecnymi politykami. Wcześniejsze 66 testów i wyniki AI dotyczą NATURAL, nie stanowią nowej walidacji tego audytu.

## 7. Gałęzie historyczne

experiment/context-surface-window-v1 nadal Draft PR #4, obecnie zawiera nowy audyt i wszystkie historyczne eksperymenty. Bez merge/promocji do main. docs/architecture-runtime-langpack-separation-2026-10-02 i docs/architecture-langpack-plugin-model-2026-10-02 zachowują role z STATE_RECONSTRUCTION; ich HEAD nie sprawdzony ponownie.

## 8. Artefakty, SHA i walidacja

[Pełny audyt, kod i wybrane dane](https://github.com/jakamilek/CleverKeys-langpack-pl/tree/cd03c3002e7164eac5d972a2a8b502873177ca09/experiments/source_metadata_v1).
SOURCE_METADATA_AUDIT.md, audit_source_metadata.py, source-metadata-audit.json.

Źródło pomiaru: ostatni udany preview run 36916501466, commit a1fa0193fc504e5fe81d9d43c23fd9a1e52ad307, artifact 11189614575 cleverkeys-pl-preview. SHA256 archiwum: 827a20f8489fad51023e1c0d58319dca030d304f7e213ef4973141251c3ad9ff. Hash porównany z API GitHub.

Morfeusz 1.99.15 / pl.sgjp.sgjp-2026.06.01 / pl.sgjp.morfeusz-0.8.0; CONDITIONALLY_CASE_SENSITIVE; lowercase i capitalized probe każdego klucza. Tylko znane pełne single-token analyses, bez ign/częściowych segmentacji. Zachowano raw analyses dziewięciu przykładów, wybrane rekordy SIMC/imion; pełnego słownika nie opublikowano.

- Parser CKDT V2 potwierdził dokładną równość surfaces z tekstem, manifest wordCount 106363 i unikalność lowercase.
- Wersja/słownik i hash wejścia sprawdzane przez runner; wszystkie dziewięć przykładów obecne.
- Powtórzenie finalnego runnera dało byte-identical JSON; oba procesy exit 0.
- Runner SHA256: 08c086dd1b19d6f903862b23128b1e5f417e316738461f6cc14aa8e214601b41.
- Wynik SHA256: 83ae7299c4781bd0cb731db6d5653cbc6f6b840c38d4b60a1797f40e894c6a4a.
- Raport SHA256: 08a14c95cb5f8accd12ecf24666ec8e76d580f7e761016c7da875b2b28f7deeb.
- Raport odczytany z pinned commit; zgodny z wysłanym plikiem, Git blob da2dc57037aa05ed9af9ab0be4f26b33dad4e686.
- Manifest wyniku zawiera SHA256 pakietu/wordlisty/binary/TSV; brak w tym etapie inferencji AI lub Android testów.

Dokumentacja i źródła: Morfeusz https://morfeusz.sgjp.pl/doc/doc/ oraz https://morfeusz.sgjp.pl/doc/license/; dostępne dane fleksyjne BSD-2-Clause nie oznaczają licencji całej publikacji SGJP. Autorstwo/warunki wybranych danych zachowano w raporcie. ULIC i dane.gov.pl opisano z oficjalnych stron; nie promowano nowych baz.

## 9. Znane luki

Metadane są w pipeline, jeszcze nie w pakiecie/runtime. 4160 kluczy bez pełnej analizy wymaga fallbacku, nie usunięcia słów. Nie zgadywać formy z samego modułu. Pokrycie analizy nie dowodzi poprawności interpretacji w zdaniu.

CTC ł, PL ZIP eligibility, pl.cklm, niespójność ADR, licencja dystrybucji Polbert i koszt mobilny pozostają otwarte według poprzedniego milestone’u; nie sprawdzono ich ponownie. Długi kontekst nadal tylko offline. Brak rankingu między różnymi kluczami.

## 10. Następny krok

Wygenerować wejście AI z surowych kategorii i form faktycznie potwierdzonych przez źródła. Ustalić i zamrozić powiązanie interpretacja→wariant oraz porównanie z/bez kategorii przed nową inferencją. Nie kontynuować strojenia na ręcznych opisach. Potem rzeczywiste slates, koszt telefonu i interpunkcja.

## 11. Delta względem NATURAL_CONTEXTS

Przyjęto korektę użytkownika: data-first, automatyczne źródła zamiast ręcznych opisów. Zweryfikowano generator, pozyskano pinned udany artefakt i policzono całe 106363, dodano automatyczny raport i dziewięć przykładów. Ujawniono dodatkowe klasy malina/jagoda/róża/polska oraz brak dowodu street dla Warszawska i surname dla Łódzki. Wcześniejsze wyniki pozostają historyczną diagnostyką ręcznych danych. Produkcja i silnik AI bez zmian.
