# Kamień milowy — HerBERT live v1 i haptyka BS, CI rozpoczęte

Data weryfikacji: 2026-10-06. Dokument wspólny dla jakamilek/CleverKeysPL
oraz jakamilek/CleverKeys-langpack-pl. Najnowszy punkt wejścia przed dalszą pracą:
ten dokument w obu repozytoriach. GitHub jest źródłem prawdy.

## 1. Zweryfikowane HEAD main przed tym zapisem
- Runtime: 8296a5db0058a5e5ba19e1ef8292def949ca7d99.
- Producent: 598b206596fe9e2adf093f2c08b16d4f8dd8ba17.
- Ten zapis jest dokumentacyjny; nie przenosi kodu próbnego do main.
- Poprzedni punkt: docs/PROJECT_MILESTONE_2026-10-06_SAFE_RANK_V4_VALIDATION_FAILED.md.

## 2. Architektura
Geometric pozostaje dekoderem. Jeden klucz słownika ma źródłowe warianty pisowni.
Nowa gałąź runtime trial/herbert-live-v1, kod 1b3f3291ba411e6a7afb727a7b68bf6f6ce27f37,
dodaje test live oryginalnego HerBERT FP32: wyłącznie kolejność dwóch źródłowych
form pierwszego kandydata. Wagi, inne klucze, języki, znaczniki exact case i proweniencja
pozostają zachowane. Wszystko nadal przechodzi jedną ścieżkę SuggestionHandler.

HerbertLiveRuntime: własny ekran testu, import SAF siedmiu przypiętych plików,
trwały prywatny noBackup staging, sumy wszystkich plików, jeden worker i natywna
weryfikacja przed READY. 2471 przykładów tokenizera + 232 paczki / 532 kandydatów
z kontrolą pięciu wejść, wyników i kolejności. Import nie fałszuje benchmarkOnly /
phoneReady w oryginalnym manifeście. Pliki z poprzedniego ekranu pomiarowego były
tymczasowe; nowa próba potrzebuje importu w swoim ekranie.

SI odczytuje bieżące pole przed wstawieniem słowa, z wielkością liter/interpunkcją.
Domyślnie do 32 słów / 4096 jednostek UTF-16, UI 16/32/64. Hasła, incognito,
wyszukiwanie, WWW/e-mail, terminale i zaznaczenie są wykluczone. Brak tekstu
edytora w nowych raportach, logach, plikach lub kopiach zapasowych; same liczniki.
Model jest osobnym plikiem poza APK i kopiami zapasowymi.

Decyzja jest jednorazowa, przed zatwierdzeniem. Domyślnie 350 ms, zakres
100–1000 ms, na podstawie wcześniejszego p95 Nubii 229/329 ms dla dłuższych wejść.
Kolejne dotknięcie klawiatury kończy oczekiwanie bazowym wynikiem przed nowym gestem.
Timeout/błąd/brak modelu/zajęty worker daje dotychczasową kolejność. Powrót do
bazowego wyniku przy niezmienionym edytorze zabezpiecza opóźnione powiadomienia
kursora przed utratą oczekującego słowa. Zmieniony edytor/revision/zaznaczenie/
tekst/pakiet/język/ustawienia/generacja modelu uniemożliwia zastosowanie starego
wyniku. Brak późniejszego przepisywania już zatwierdzonego tekstu. Shift/Caps Lock/
początek zdania oraz preferencja pisowni użytkownika mają pierwszeństwo.

BS: przyjęte zaznaczenie słowa i przyjęte usunięcie emitują dedykowane HapticEvent
przez VibratorCompat. Wspólny przełącznik wibracji, haptic_long_press i własny czas
wibracji. Początek i kolejne słowa, usunięcie timerem albo na puszczenie; bez impulsu
sukcesu przy odmowie/pustym zaznaczeniu/anulowaniu. Błąd haptyki nie przerywa edycji.
Pierwszy podgląd słowa nie dodaje drugiego impulsu TrackPoint; ruch po znakach nadal
korzysta z zaakceptowanego wspólnego ze spacją SliderMotion.

## 3. Zaakceptowane ustalenia
Użytkownik 2026-10-06 wyraźnie polecił przygotować testową klawiaturę HerBERT mimo
znanego kosztu pamięci i mieszanych wcześniejszych wyników. Nowa kolejność pracy:
HerBERT live + haptyka BS, przygotowanie APK, potem globalny słownik swipe.
SI domyślnie wyłączona. Trzy opcje mają Defaults, bezpieczne bounded reads,
typowane defaults/ranges backupu, wyszukiwalne wejście do ekranu i scoped reset.
Polskie/base tłumaczenia 14 nowych zasobów przygotowane; inne języki później.
Gemini/PAL obowiązek pozostaje zniesiony; brak delegacji; monitoring <=60 s/run.
Brak scalania, wydania, tagów i zmiany wersji aplikacji.

## 4. Odrzucone rozwiązania pozostają odrzucone
Nie zastępujemy geometric przez CTC, nie dodajemy zduplikowanych kluczy dla
kapitalizacji, ręcznych opisów znaczeń, reguł pojedynczych słów ani niekalibrowanego
dodawania surowych MLM log-probabilities do wag geometrycznych.
HerBERT INT8 ma wcześniejszą nieudaną bramkę. distilHerBERT globalny margines .25
v4 nie poprawił użyteczności na nowych 64 kontekstach. Wynik v4 jakości FAIL pozostaje
FAIL, choć workflow zakończył się SUCCESS. Ta nowa decyzja użytkownika pozwala
na izolowany FP32 test live, nie stwierdza gotowości produkcyjnej.

## 5. Nadal planowane
- Po przygotowaniu APK: globalna poprawa źródeł/fleksji/pokrycia słownika swipe.
- Trzy ustawienia czasów stacjonarnego BS przy następnych zmianach.
- Niezależna ocena jakości, ewentualne przyszłe ograniczenie pamięci.
- SI do interpunkcji i różnych kluczy wymaga osobnego projektu/kalibracji.
- Tłumaczenie 14 herbert_live.xml kluczy w innych językach; Polish/base już są.
- Licencje mniejszych modeli nadal odłożone na prośbę użytkownika; bez kontaktu z autorami.

## 6. Co zweryfikowano i co pozostaje niezweryfikowane
Lokalnie PASS: XML manifestu/nowych zasobów, 14 polskich/base formatów, YAML
workflow oraz Python w workflow. Wszystkie 31 wgranych Git blob SHA zgodne
z lokalnymi bajtami przed zamrożeniem kodu. To nie jest wynik kompilacji Androida.
Brak lokalnego SDK/Kotlina/Gradle; nowe testy mają wykonać się w CI.

Nowe testy: jednorazowa decyzja, kolejność obu źródłowych form, zachowane równoległe
tablice, timeout/tie/bad scores/stale identity; rzeczywista ścieżka swipe przed
commit, next-touch fallback i późny wynik, zmieniony edytor, Shift/private; BS
przyjęty podgląd/usunięcie, cykl, puszczenie, odmowa/anulowanie/błąd haptyki;
rzeczywisty dispatch z obiema istniejącymi bramkami wibracji.

Run runtime 37507317429 (Polish SI HerBERT live trial v1) rozpoczęty:
https://github.com/jakamilek/CleverKeysPL/actions/runs/37507317429
Ostatnia obserwacja: in_progress, kompilacja Androida w toku; reszta pending.
Osobny standardowy CI 37507323534 także in_progress w jednorazowym odczycie.
Nie monitorować do końca; użytkownik zgłosi zakończenie.

Wymagane przed APK: compileDebugKotlin, zarejestrowane pure z oryginalnym markerem
2471/232/532, editor/source-variant/BS/pointer/haptic/learning mock regresje,
lintDebug/lintVitalRelease, assembleDebug i audyt APK bez wag/tokenizer fixtures.
Nowy APK/SHA/artifact ID jeszcze nie istnieją w zweryfikowanym stanie.
Próba telefonu, płynność, pamięć, bateria i jakość live NIEZWERYFIKOWANE.

## 7. Gałęzie i historia
- trial/herbert-live-v1: nowa implementacja, draft PR4:
  https://github.com/jakamilek/CleverKeysPL/pull/4
- trial/herbert-fp32-benchmark-v1 0367b334f770d4ad2b1925dc445850e9c19e9b78:
  baza aplikacji z zaakceptowanymi wcześniejszymi poprawkami i pomiarem FP32 v2.
  Nie była scalona do main; PR4 zawiera także tę wcześniejszą bazę i nie służy
  do automatycznego scalania.
- Producent experiment/herbert-fp32-benchmark-v1: zaufany zewnętrzny FP32.
- experiment/polish-mlm-v3-loading-fix-v1: poprawny oryginalny native loading;
  64 nowe przypadki limit16 HerBERT62/distil63, limit32 HerBERT57/distil61.
- experiment/polish-mlm-safe-rank-v4: kod 7d7d3ec4f7be31476df11f198dfcc2b21d813e5b,
  wyniki 5339596a801717569a72d1ad847aa1f0131ffe9a, run37502851581 SUCCESS,
  jakość FAIL. Nie stroić marginesu po tym wyniku.
- feature/source-variants-trial-v1 041b28ae4587c531ef73e62933e9151cadb84c33:
  źródłowe warianty i bieżący v5 langpack; runtime AI nie przebudowuje słownika.

## 8. Artefakty, SHA i punkty integracji
Kod nowej próby: 1b3f3291ba411e6a7afb727a7b68bf6f6ce27f37.
Nowe APK ma zostać artefaktem cleverkeys-herbert-live-trial-arm64 po wszystkich
kontrolach; status i SHA należy odczytać po zakończeniu runu, nie zakładać.

Zaufany model oryginalnego HerBERT:
- 651798883 bajtów, SHA256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2.
- Producent d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c, run37230171787,
  artifact11312693984. Siedem stałych tożsamości w HerbertBenchmarkTrial.
- Tokenizer portable SHA ee9b13d7732fb22dc7b28d51751daebbe5caaac484ba69d7104b80b52b32681b.
- Model nie trafia do Git/APK; manifest i scoring WWM oryginalne.

Wcześniejszy pomiar telefonu, kod db88fd28cca21ba2aa1e99b38e3886f1f147b5d6,
APK SHA c3d15aaf1ba26b8f2534199dda5a6b8835cb72e5233038f4e6f1292b57ed3dd9:
PSS346.2 przed /2121.0 po wczytaniu /max2132.1 /1336.8 zaraz po zamknięciu,
MiB całego procesu. Limit16 nie został wówczas zmierzony natywnie. Skrócenie
kontekstu nie usuwa zaobserwowanego stałego kosztu wczytywania.

Słownik v5 ZIP SHA aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb,
sidecar SHA 5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d.
Aktualnie zainstalowane bajty pakietu użytkownika pozostają nieodczytane.
Instrukcja próby: runtime docs/HERBERT_LIVE_TRIAL_V1.md.

## 9. Ograniczenia i znane luki
Wysokie FP32 PSS; brak dowodu gotowości produkcyjnej ani niezależnej jakości live.
Dwie formy w pierwszych miejscach są konstrukcją listy, nie dowodem jakości SI.
Przy czasie/busy/loading używany jest bazowy wynik; brak analizy bez potwierdzonej
pary. Nowy test wymaga dalszej kompilacji i próby telefonu, bez twierdzenia że już działa.
Pamięć natywna/mapowania mogą pozostawać po zamknięciu; zamknięcie nie obiecuje GC.
Import wymaga wolnego miejsca także na tymczasowy kontener i rozpakowane pliki.

Dziewięć zgłoszonych słów nie występuje w zweryfikowanych canonical/normalized
indeksach v5 ani porównywanej bazie 106363 kluczy: dodam, grzeje, kasami, nawilżane,
odpowiadam, patrzysz, poczekaj, podpowie, pozdrawiam. Nie jest to dowód ubogiego
wariantu „AI”: porównane słowniki miały identyczne klucze/rangi. Globalny generator
ma AND Hunspell/AOSP oraz inne filtry; dokładny etap odrzucenia KAŻDEGO słowa
pozostaje do śledzenia. Audyt producenta: docs/audits/swipe-coverage-2026-10-06.json
i docs/PROJECT_MILESTONE_2026-10-06_SWIPE_DICTIONARY_COVERAGE.md.

## 10. Następny krok
Gdy użytkownik poda zakończenie CI, odczytać oba runy, poprawić konkretne błędy
jeśli są, zweryfikować obowiązkowe testy/lint i SHA artefaktu, udostępnić testowy APK.
Nie czekać aktywnie na cały run. Następnie globalny audyt odrzucenia/fleksji/pokrycia
słownika producenta; równolegle użytkownik może sprawdzić HerBERT/haptykę na telefonie.

## 11. Różnica od poprzedniego punktu
Poprzedni etap zakończył weryfikację jakości safe-rank v4 jako FAIL. Użytkownik
teraz wybrał HerBERT FP32 do izolowanego live testu. Kod integration/settings/
persistent import/guards/BS haptics i testy zapisane w nowej gałęzi; CI uruchomione,
niezakończone przy zapisie. Słownik pozostaje następny; stare wyniki nienadpisane.
