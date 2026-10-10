# HerBERT: zwykłe formy słów i lematy źródłowe — APK gotowe
Data weryfikacji: 2026-10-10.

## 1. HEAD main przed zapisem
Runtime CleverKeysPL: 3442011e6cb2a145114fb39e2616a7393034c720.
Producent CleverKeys-langpack-pl: af0c24dc1462e286f00e4edd42c4a1fd209ce19a.
Dokument identycznie zapisany na obu main wyłącznie dokumentacyjnie. Nie podaje własnego przyszłego SHA jako HEAD. Odpowiedniki:
[runtime](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-10_ORDINARY_WORD_FORMS_APK_READY.md),
[producent](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-10_ORDINARY_WORD_FORMS_APK_READY.md).

## 2. Architektura
Geometric nadal rozpoznaje słowa; SuggestionHandler zachowuje jeden precommit/publish.
word-forms-v3: pierwszy klucz plus jeden z pierwszych pięciu już zdekodowanych polskich kandydatów, maksymalnie cztery pisownie dwóch kluczy. Relacja: identyczna pisownia po usunięciu polskich diakrytyków albo wspólny, case-sensitive lemat/część mowy w źródłowych metadanych.
Zwykłe rozpoznane formy nie potrzebują kapitalizacji w sidecarze. Pisownię wielką/małą literą dodajemy tylko z istniejących deklaracji i przy włączonym pokazywaniu wariantów kapitalizacji.
Slate.formGroupSize oddziela członkostwo grupy od exact-case. Wyłączenie pokazywania wariantów kapitalizacji nie wyłącza rankingu zwykłych form. Każda forma przemieszcza się z własną wagą, językiem i regułą pisowni, reszta listy zachowuje kolejność. Grupa dostępna także bez SI.
SourceLemma to typowany widok istniejących lexicalReadings/generatedFormProofs/interpretations, ograniczony do pasującej pisowni; lemat i POS bez normalizacji znaczenia. Parsowany przy imporcie, nie w geście; zbiór niemutowalny, najwyżej32 identyfikacje na klucz, złożniejsze pole nie daje relacji. Oryginalny metadataJson i schema1 bez zmian; niezgodne przyszłe pola ignorowane w tym opcjonalnym widoku.
Oryginalny zweryfikowany FP32, WWM mean logp, tokenizer, jedna sesja/worker, kontekst32, limit350ms, brak edycji po commit i wszystkie prywatne/editor/model/settings/Shift/timeout/next-touch bramki zachowane.

## 3. Zaakceptowane
Użytkownik potwierdził właściwą kapitalizację Maliną w podpowiedziach, choć SI wstawiła maliną po „Jutro do Łodzi jadę razem z”. Bez dokładnej pozycji/rankingu/liczników nie traktować jako benchmark.
Następnie wyraźnie zlecił dalsze SI przed słownikiem: po „Tak, była w podpowiedziach właściwa” pierwsze kapitalizacją, drugie kapitalizacja. Doprecyzowanie: słowo wprowadzone swipe. Wdrażamy wybór form, nie tylko wielkości liter.

## 4. Odrzucone
Bez reguły dla konkretnego zdania/słowa, ręcznie dopisanych opisów, odmian i zgadywania rdzeni. Bez generowania brakujących kandydatów, skanowania całego słownika lub surowego logp dodanego do geometrii. Dawne nieudane INT8/marginesy modeli pozostają nieudane.
Nie twierdzić, że poprawne przekazanie kandydatów gwarantuje gramatyczną trafność HerBERTa.

## 5. Niewdrożone plany
Globalne pokrycie słownika: wcześniejsze dziewięć dodam/grzeje/kasami/nawilżane/odpowiadam/patrzysz/poczekaj/podpowie/pozdrawiam, dodatkowo sprawdzone luki kapitalizacją/kapitalizacje. Bez punktowych wyjątków. Szersza lematyzacja zwykłych słów wymaga źródłowych danych producenta; nie wszystkie słowa mają takie metadane.
Pełny ranking dowolnych różnych słów, gramatyka wszystkich form, interpunkcja SI, osobne czasy BS i tłumaczenia innych języków pozostają później.

## 6. Zweryfikowane i niewiadome
Kod poprzedniej bramki: provider.lookup(primary)?.capitalization ?: unchanged. To wykluczało pierwsze słowo bez metadanych kapitalizacji przed SI.
Autentyczny v5: CKDT106363, sidecar16199. kapitalizacja obecna, rank196; kapitalizacji obecna, rank194; kapitalizacją/kapitalizacje nieobecne. Kapitalizacja/kapitalizacją nie mają wierszy sidecaru. Brak unigrams nie oznacza braku CKDT. Oba podstawowe ZIP mają tę samą obserwację.
Zainstalowany pakiet, własne słowa i natywne wyniki/czas na telefonie nie są sprawdzone, więc to nie dowód dokładnej przyczyny rankingu urządzenia.
Nowy kod:17 blobów zweryfikowanych przed commitem. Lokalnie XML, YAML/osadzony Python i dziewięć verbatim wpisów v5/proweniencja PASS. Brak lokalnego toolchain Android/Kotlin.
Dodano11 zarejestrowanych regresji: zwykłe formy bez metadanych, lemat/POS/immutability, przełącznik pisowni, języki/granice/decoded-only, kolejność/score/rozmiary, staleness/timeout, dokładne wejścia oryginalnego tokenizera i rzeczywisty handler precommit dla zdania użytkownika. Oba runy dla dokładnego 0acb647606cb52f0a3263b098704745306b5d6b7 zakończone SUCCESS. Logi:2874 pure wraz z obowiązkowym oryginalnym conformance2471/232/532/five inputs,193 live integration w dziewięciu suites,298 standard integration. Nie sumować powtórzeń między runami. Brak FAILURES!!!; diagnostyka refleksji MockK w logach nie jest nieudaną asercją. Kompilacja Android, debug lint, release vital lint, assemble i audyt APK PASS. Standard także security/code quality/size PASS. Lokalny rehash ZIP raportów oraz odczyt pure/lint XML PASS:0 Error/Fatal,234 innych issues.
Trafność i wydajność nowych grup na telefonie nieweryfikowane. Testy callbacków nie są pomiarem modelu.

## 7. Gałęzie
Runtime trial/herbert-live-v1: 0acb647606cb52f0a3263b098704745306b5d6b7, rodzic1f32967362917ae60c42f9e116f96fd47ed9b097, drzewo1984d5baaf448e64655342a7f62a566942873f13.
Draft PR4: https://github.com/jakamilek/CleverKeysPL/pull/4 ; obejmuje wcześniejszą bazę, nie tylko tę zmianę. Bez merge/release/tag/bump. Producent bez zmian kodu danych/wag/langpacka; wyłącznie dokumentacja main.
Polskie/bazowe opisy i instrukcja docs/HERBERT_LIVE_TRIAL_V1.md aktualne; inne locale backlog. Todo477 linii, poniżej500.

## 8. Runy i artefakty
[Live38032850945](https://github.com/jakamilek/CleverKeysPL/actions/runs/38032850945) i [CI38032853742](https://github.com/jakamilek/CleverKeysPL/actions/runs/38032853742): completed/SUCCESS, dokładny commit0acb647606cb52f0a3263b098704745306b5d6b7. Sprawdzono wszystkie obowiązkowe kroki i logi, nie tylko zbiorczy status.
Nowy [APK ZIP11662738564](https://github.com/jakamilek/CleverKeysPL/actions/runs/38032850945/artifacts/11662738564), cleverkeys-herbert-live-trial-arm64,35806410B, SHA256 a9e41c38ae60f5dda97bc9196c1afc4da3ecd92d2cffe3de54af0afe5bd54376, wygasa2026-10-24. Wewnątrz CleverKeys-v2.0.0-arm64-v8a.apk,35805130B, SHA256 z audytu CI fc79a7eca9b06b9fa2d2b5796d07d85482a6c444ba024bb060e91ccd91ed353d. APK nie został lokalnie pobrany/rehashowany; tożsamość i hash z CI, zgodne z artefaktem i head.
Tożsamość w wykonanym audycie:word-forms-v3,ordinaryDecodedForms=true,sharedSourceLemma=true,maxLiveSurfaces4,familySearchCandidates5,liveAI=true,optInDefault=false,contextDefault32,opcje16/32/64,wait350ms,nativeConformanceBeforeLive=true,backspaceWordHaptics=true. Audyt obecności wag FP32 i testowych tokenizer/score fixtures w APK PASS (brak).
Raporty11662678682,22421B,SHA256 c119fe2c323814b4278e6ec1004d477a4dbe63d8de9b004c2d1ce3842f203547. Pobrano mały ZIP, lokalnie zweryfikowano hash i XML/pure. Debug lint0 Error/Fatal,234 innych issues.
Poprzedni case-family-v2 APK11441445238 i walidacja pozostają historyczne w PROJECT_MILESTONE_2026-10-10_HERBERT_FORM_GROUP_APK_READY.md; nie używać jako nowej paczki.
Model d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c /run37230171787 /artefakt11312693984 niezmieniony, SHA modelu f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2. Dotychczasowy import może pozostać; aktualizować APK bez odinstalowania.
Źródłowy v5 ZIP SHA aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb; sidecar SHA5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d. Dziewięć autentycznych wpisów w fixture, nie nowy słownik.

## 9. Ograniczenia
Brak źródłowego lematu dla form o innych literach oznacza brak tego połączenia. To nie pełne generowanie odmian ani ranking całego paska. Provider snapshot/aktualny językpl nadal wymagane; brak sidecaru daje geometrię. Przy4 pisowniach nie każda zmieści się w Top3.
Wysoki poprzedni PSS procesu ~2132MiB pozostaje; nowe zbiory źródłowe/lematy, grupy i czas modelu nie mają pomiaru pamięci/energii na telefonie. Mean logp przy różnych liczbach tokenów nie gwarantuje poprawnego rankingu. Limit350ms może dać bazową kolejność.

## 10. Następny krok
Próba na telefonie nowego APK: SI gotowa, domyślnie32 słowa/350ms; porównać on/off, swipując ostatnie słowo po „Tak, była w podpowiedziach właściwa” /„Zajmuję się” oraz po „To jest bardzo ważna” /„Nie mogę znaleźć”. Oczekiwane kapitalizacja/kapitalizacją/praca/pracy tylko jeśli rozpoznane i dostępne. Raportować wstawienie i pierwszą trójkę, case-toggle/timeout/wytnij-wklej/private oraz czas. To pomiar trafności dopiero do wykonania; CI nie gwarantuje zwycięstwa oczekiwanej formy.
Nie podnosić arbitralnie limitu ani nie patchować zdania pod pojedynczy wynik. Po ocenie SI wrócić do globalnej naprawy pokrycia; dotychczasowe zaakceptowane BS/spacing/kapitalizacja niezmienione. Monitoring runów nadal maks60s TOTAL/run, potem użytkownik zgłasza zakończenie; ten etap był odczytem już zakończonych runów.

## 11. Delta
Względem PROJECT_MILESTONE_2026-10-10_ORDINARY_WORD_FORMS_CI_STARTED.md: oba runy zakończone i sprawdzone wszystkie obowiązkowe gates/logi;2874 pure/193 live/298 standard integration PASS. Nowa paczka word-forms-v3 i jej SHA/commit zweryfikowane w CI, mały ZIP raportów lokalnie rehashowany. PR4 walidacja uaktualniona. Nie dodano kodu, danych, modelu, nowych reguł słów ani sukcesu telefonicznego. Zapis tego checkpointu na obu main wyłącznie dokumentacyjny.

