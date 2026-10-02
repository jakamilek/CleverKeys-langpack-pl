# Kamień milowy — nowe konteksty, przymiotniki i wiele znaczeń jednej pisowni

**Weryfikacja:** 2026-10-02 UTC.
**Repo:** jakamilek/CleverKeys-langpack-pl.
**Cross-repo:** [jakamilek/CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-02_NATURAL_CONTEXTS.md).
**Status:** ukończony izolowany eksperyment offline; bez wyboru silnika produkcyjnego.

## 1. Zweryfikowany GitHub i snapshot main przed zapisaniem obu dokumentów

| Repo | HEAD main |
|---|---|
| jakamilek/CleverKeys-langpack-pl | f680305f92afb8e7fd1580aff7de4da5f86651ed |
| jakamilek/CleverKeysPL | 1fe28b6ba86fcf1a2eef4846bda3a109adc2d1aa |

Wspólny snapshot zweryfikowany przed dokumentacyjnymi commitami obu milestone’ów. Ich zapis przesuwa main wyłącznie dokumentacją. Kod eksperymentu pozostaje na experiment/context-surface-window-v1, [Draft PR #4](https://github.com/jakamilek/CleverKeys-langpack-pl/pull/4).

Freeze kodu/danych/kryteriów przed inferencją: 0509a1cc3f222ec6afbcfb08b98a96dfda52824a.
Kompletne nowe wyniki: 37696cd3a4d575daf00beb833cb65b81ac7076c6.
Poprzedni eksperyment znaczeń: 55bb179a1d308cf7a7f7d4049ec6e3f060719e4c.

## 2. Stan architektury

Oddzielne repozytoria, immutable 100k, CKDT V2 i legacy fallback w stanie poprzedniego milestone’u. Pakiet dostarcza wiedzę/model, wspólny runtime wykonuje ranking. Android, produkcyjny generator i kontrakt API v1 nie zmienione w tym etapie.

Eksperymentalny sidecar natural-sense-surface-v2: jeden lowercase surfaceKey, senses (id/kind/descriptionPl), warianty z senseIds; dodano adjective. Wariant Warszawska mapuje na street i surname, warszawska na adjective. Ulica i nazwisko nie wymagają odmiennej kapitalizacji. łodzi/Łodzi jest osobnym kluczem powierzchniowym; nie wdrożono lematyzacji. Przykłady osób fikcyjne, bez deklaracji coverage produkcyjnego słownika.

Okna 2 słów oraz do 64 słów/4096 znaków, zachowany oryginalny case/diakrytyka/interpunkcja; limit modeli 512 tokenów, zero obcięć. Dedupe kluczy, zachowane alternatywy, lexical order i engineScore. Nie wdrożono rankingu pomiędzy różnymi kluczami. Jawny tryb początku zdania zmienia display niezależnie od znaczenia.

## 3. Ustalenia zaakceptowane i wyniki

Użytkownik zlecił kontynuację dla łódź, malina, warszawska (ulica/nazwisko) i podobnych. Głównym kryterium nadal poprawny klucz oraz dokładny zapis w pierwszych trzech sugestiach; top 1 pomocniczo. Interpunkcja pozostaje kryterium przyszłej rozszerzalności.

64 nowe ręcznie napisane główne konteksty: łódź, łodzi, malina, jagoda, róża, polska, warszawska. Po 16 zdań z bezpośrednią wskazówką, wcześniejszym zdaniem, zmianą tematu i zaprzeczeniem; po 8 form małych/wielkich liter w każdej kategorii. Sześć kluczy po 8 przypadków, warszawska 16.

| System | Main top 1: 2 słowa | Main top 1: długie | Main top 3: długie | Probe top 3: długie | Meaning top 1: długie |
|---|---:|---:|---:|---:|---:|
| Neutralny default | 32/64 | 32/64 | 64/64 | 32/64 | — |
| NLI global z opisami | 40/64 | 48/64 | 64/64 | 48/64 | 45/64 |
| NLI current z opisami | 43/64 | 47/64 | 64/64 | 47/64 | 45/64 |
| Ten sam NLI bez opisów | 28/64 | 37/64 | 64/64 | 37/64 | — |
| Polbert WWM | 46/64 | 53/64 | 64/64 | 53/64 | — |
| HerBERT WWM | 50/64 | 56/64 | 64/64 | 56/64 | — |

Main top 3 jest gwarantowane przez dwa warianty pierwszego klucza także bez AI: nie oznacza 100% jakości modelu. Osobne 64 probe powtarzają konteksty i ustawiają właściwy klucz drugi, po dwóch wariantach innego klucza. Wybrany wariant celu zajmuje miejsce 3, alternatywa 4. Probe top 3 jest konstrukcyjnie równe main top 1, nie stanowi niezależnego potwierdzenia.

HerBERT: łódź, łodzi i malina po 8/8 top 1, warszawska 15/16. Pozostałe błędy: cztery owoce jagoda jako Jagoda, trzy kwiaty róża jako Róża, jeden przymiotnik warszawska jako Warszawska. Poprawny wariant zawsze pozostał drugi w głównej próbie.

NLI global dla warszawska: poprawny zapis 11/16, poprawne znaczenie 8/16. Trzy dalsze poprawne wielkie litery ukrywają pomylenie ulicy z nazwiskiem. NLI current: zapis 11/16, znaczenie 9/16. MLM ocenia pisownię, nie deklarujemy jawnego rozpoznawania przez niego znaczeń.

Opisy poprawiają NLI wobec braku opisów o 11 trafień netto (20 napraw/9 regresji), ale nie zapewniają przewagi nad MLM. Hipoteza odnosząca się do aktualnego słowa nie poprawiła całego wyniku (47 zamiast 48; 7 napraw/8 regresji) ani zmiany tematu (9/16 zamiast 10/16). Ranking MLM zmienił się wobec poprzedniej próby: nie wybrano silnika produkcyjnego.

## 4. Rozwiązania odrzucone i powody

Nie dopisywać duplikatów CKDT dla wielkiej/małej litery; wariant i znaczenie są osobnymi atrybutami. Nie traktować ulicy Warszawska i nazwiska Warszawska jako różnych zapisów. Nie utożsamiać autocap z rozpoznaniem nazwy własnej.

Nie stroić scoringu, hipotez, progów, normalizacji ani modelu per słowo po wynikach. Nie wybierać produkcji z jednego ręcznego zbioru, nie uznawać surowych scores za skalibrowaną pewność. Nie rozbudowywać Androida lub scalać branchu eksperymentu na podstawie tej próby.

Historyczne plT5 sentinel i RoBERTa v2 unknown Łódź pozostają kontrolami kontraktu. Nowe modele nie rozwiązują luki CTC ł ani nie dodają brakującego słowa spoza dekodera.

## 5. Planowane, jeszcze niewdrożone

Osobna zamrożona diagnoza wpływu długości tokenizacji; szerszy niezależny zbiór, rzeczywiste slates dekodera oraz rozkład miejsc UI. Pomiary mobilne i osobna ewaluacja interpunkcji przed wyborem silnika.

Generator rzeczywistego sidecara sense→surface, parser/provider API v1, dłuższy odczyt InputConnection i świeżość snapshotów, tap-to-replace oraz uczenie pisowni użytkownika pozostają niewdrożone. Długi kontekst działa wyłącznie offline.

## 6. Niezweryfikowane

Generalizacja poza ręczne zdania, jakość dla użytkowników, coverage znaczeń w 100k, rzeczywiste błędy swipe, interpunkcja, ONNX/kwantyzacja, RAM/energia/latencja na telefonie. Licencja redystrybucji Polbert pozostaje nieustalona według wcześniejszego milestone’u.

Tokenizacja koreluje z częścią błędów: HerBERT jagoda/róża po 2 subwordy, Jagoda/Róża po 1; Polbert warszawska 2, Warszawska 1. WWM sumuje log probabilities, więc długość może wpływać na preferencję. To możliwy czynnik, nie udowodniona przyczyna; nie izolowano go od priorytetów modelu.

## 7. Gałęzie historyczne i role

experiment/context-surface-window-v1: aktywny izolowany eksperyment, Draft PR #4, wcześniejsze wyniki zachowane.

docs/architecture-runtime-langpack-separation-2026-10-02 oraz docs/architecture-langpack-plugin-model-2026-10-02: role z STATE_RECONSTRUCTION, ich HEAD-ów nie sprawdzano ponownie w tym etapie. Nie wykonano merge ani przepisania historii. Poprzednie milestone’y pozostają historią: SENSE_ATTRIBUTES_TOP3, CONTEXT_DIAGNOSTICS, PRETRAINED_SURFACE_INFERENCE, STATE_RECONSTRUCTION.

## 8. Artefakty, SHA, integracja i walidacja

[Raport i komplet wyników](https://github.com/jakamilek/CleverKeys-langpack-pl/tree/37696cd3a4d575daf00beb833cb65b81ac7076c6/experiments/context_surface_v1): NATURAL_PROTOCOL.md, NATURAL_RESULTS.md, natural_cases.py, natural_experiment.py, test_natural_experiment.py, natural-cases.json, natural-sidecar.json, natural-requests.json, natural-results-2026-10-02.

164 cases / 328 requests: 64 main, 64 powtórzone probe, 14 sentence_start, 8 ambiguous bez gold, 7 missing_key, 7 slot_limit. Gold i kategorie nie przekazywane modelom.

Przypięte gotowe modele bez treningu:
- NLI MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli, revision 0a71e92a985b6e1ad1828cf67ce9c459639c1dca.
- Polbert dkleczek/bert-base-polish-cased-v1, revision fed744e81ebd16cf099b5c64c40688bc3e6ace67.
- HerBERT allegro/herbert-base-cased, revision 50e33e0567be0c0b313832314c586e3df0dc2297.

Prawdziwa inferencja wszystkich trzech modeli na nowych danych, bez replay i treningu. Kompletne pretrained głowice, brak missing/mismatched/error keys. HerBERT ma wyłącznie dopuszczone nieużywane wagi poolera/SSO; NLI/Polbert bez unused. MLM tylko uprzednio zapisana metoda WWM; parity max error 4.292e-6 Polbert / 3.052e-5 HerBERT.

- Runner SHA256: f3fd6f76dad2b8770c667c17f8f1b424996ea917aacfc3c5fc26738978bd15e1.
- Cases SHA256: 57669d70d538b58abc65a28910504f7bab81bbac6c543812f7523e517e79f741.
- Sidecar SHA256: 00795b97659a82c0effcb8607fed15267f64bc1c4e15155c32bba5f3f8e796fe.
- Requests plik SHA256: 71091c409e6f38fc983d4c248096efcb91790a356ed8443ac33159e6f8c38bb6.
- Request payload hash: 49016dfa848c5c29f7b24b48daf9d366a7741215ded6647cc28d4d26eed7b92d.
- Summary SHA256: 052a8cb7cf7d73683fe462698e510a8f96ca63350a298f3c84533a18cd7bb305.
- Summary Git blob: 957faf365816b53fd0192caed53f98a69de6f22f.
- Raport Git blob: 77b45bef3f2d0e8e7376b23506977f0c5fe3019c.
- Raport i summary odczytane z przypiętego results SHA, bajty zgodne z lokalnymi.
- 66/66 testów stdlib PASS lokalnie i w kontraktowym CI.
- Freeze push CI 37057347080 oraz PR CI 37057354504 completed/success.
- Results push CI 37058299112 oraz PR CI 37058305692 completed/success.
- CI nie uruchamia modeli ani Androida. Trzy lokalne procesy inferencji exit 0.
- Wszystkie predykcje kompletne/finite/dopuszczalne; NLI senseScores zgodne z inventory i max mapowaniem, engineScore zachowane. Fixture regeneruje się byte-identical; kod i dane zgodne z GitHub freeze.
- CPU float32, 2 wątki/model, batch 8; 456 grup/model, NLI 1776 unikalnych par, MLM po 558 tasks; zero tokenowych obcięć.
- Czas po załadowaniu 14,40 s NLI / 29,70 s Polbert / 28,59 s HerBERT, równoległe procesy i cache: nie benchmark telefonu lub pojedynczego maźnięcia.
- Manifesty zawierają SHA256, loading info, tokenizer lengths i environment; nie opublikowano wag.

Punkt integracji nadal projektowany: pakietowe warianty/znaczenia i wspólny runtime. Brak integracji produkcyjnej w tym etapie.

## 9. Ograniczenia i znane luki

Sztuczne slates, ręczny mały zbiór napisany po wcześniejszej diagnozie: nie zewnętrzny ślepy benchmark. Warianty mogą zajmować kilka slotów, więc nawet dostępne słowo może wypaść poza top 3.

sentence_start: display 14/14 we wszystkich systemach/oknach także bez AI; NLI znaczenie długiego okna 12/14 global i 13/14 current. missing_key: 0/7 osiągalnych; slot_limit: 7/7 osiągalnych, ale 0/7 top 3, prawidłowy klucz najwcześniej czwarty. ambiguous bez accuracy.

CTC ł, eligibility PL ZIP, pl.cklm i niespójność ADR pozostają otwarte według poprzedniego milestone’u; nie sprawdzano ich ponownie. Rzeczywista historia Androida nadal krótka. To eksperyment preferencji form, nie pełny test wyboru słowa przez klawiaturę.

## 10. Następny uzasadniony krok techniczny

Zapisać przed inferencją osobną kontrolę wpływu różnych długości tokenizacji na ocenę wariantów. Następnie niezależne dane i rzeczywiste slates: mierzyć poprawny klucz/zapis w top 3, zachowanie alternatyw i presję slotów. Koszt telefonu i interpunkcja przed decyzją produkcyjną. Nie wybierać reguł/modelu per słowo z obejrzanych przypadków.

## 11. Delta względem SENSE_ATTRIBUTES_TOP3

Dodano 64 nowe konteksty (łącznie 164 cases), siedem kluczy, przymiotniki, explicit łodzi oraz wiele znaczeń wariantu Warszawska. Rozdzielono semantykę od zapisu i autocap. Porównano global/current NLI z ablacją oraz prawdziwą nową inferencją obu MLM. Wykazano brak ogólnej poprawy hipotezy current oraz przewagę HerBERT w tej próbie i możliwy wpływ tokenizacji. Testy 56→66, freeze i komplet wyników/readback/CI utrwalone. Produkcja bez zmian.
