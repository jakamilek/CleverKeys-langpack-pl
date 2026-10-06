# Kamień milowy — compile/BS PASS, naprawione test fixtures i bramka pure, nowe CI

Data weryfikacji: 2026-10-06. Wspólny punkt wejścia dla jakamilek/CleverKeysPL
oraz jakamilek/CleverKeys-langpack-pl. GitHub jest źródłem prawdy.

## 1. Zweryfikowane HEAD main przed tym zapisem
- Runtime: 86fb23fe671c5bc56714c37f6580f5f159fa1931.
- Producent: 153c866d0c7b6b378ef85866cfda89767fa1dc6e.
- Ten zapis w obu main jest wyłącznie dokumentacyjny.
- Poprzedni punkt: docs/PROJECT_MILESTONE_2026-10-06_TYPED_AUTOCORRECT_BS_RESTORE_CI_STARTED.md.

## 2. Architektura i bieżąca implementacja
Geometric pozostaje dekoderem. Jeden klucz CKDT zawiera źródłowe warianty pisowni.
HerBERT FP32 live w trial/herbert-live-v1 pozostaje izolowanym opt-in testem
kolejności dwóch potwierdzonych form pierwszego kandydata przed pojedynczym commit.
SI domyślnie off, osobny zweryfikowany model poza APK, prywatny staging i native
2471 tokenizer / 232 paczki / 532 kandydatów przed READY. Kontekst 32 słowa,
opcje16/32/64, maks4096 UTF-16, oczekiwanie350 ms/100–1000. Brak raw editor text
w nowych raportach/pliku/backupie, bez późnego przepisywania tekstu. Shift/private/
cursor/text/model/settings guards i BS haptics nie zostały usunięte.

Kod źródłowy BS7c651e753ff72b54b8c3ff05bbcc664a0ae7aaf6 dodaje globalny, ograniczony wyjątek
pierwszego krótkiego BS po autokorekcie wyrazu wpisanego literami. Zwraca oryginał
z istniejącą spacją także w domyślnym trybie pojedynczego znaku. Następny BS
wykonuje wybraną akcję. Nie zmienia swipe-undo, timerów przytrzymania ani
zaakceptowanego wspólnego ze spacją SliderMotion/haptyki.

SuggestionHandler przechowuje krótkotrwały, nieutrwalany bookmark: identity
InputConnection/EditorInfo, collapsed absolute caret, token + separator.
Zgodność jest sprawdzana na żywym edytorze. Normalne potwierdzenie kursora
zachowuje prompt; zmiana tekstu/pola/zaznaczenia/kursora, typing, swipe, field exit
unieważnia go. KeyEventHandler używa istniejącego bezpośredniego LearningHooks,
nie dodaje metody wymagającej proxy IReceiver. Udana zamiana nie wywołuje
handle_backspace (to nie usunięcie znaku z trackera).

Przy Show Exact Typed Word nieznany oryginał trafia na pierwsze miejsce jako
ExactAdd. Sprawdzenie słownika wyklucza świeżo uczoną historię wyborów; historia
nie może udawać jawnego wpisu. Zweryfikowany bookmark pozwala dodać słowo za
zachowaną spacją. Kliknięcie dodania jest storage-only, bez usuwania, ponownego
wpisania ani zmiany kursora. Nie dodajemy słowa automatycznie samym cofnięciem.
Zamiana undo wybiera sprawdzony zakres i wykonuje jeden commit; odmowa nie kasuje
wyrazu przed wstawieniem i nie ponawia tej samej próby.

## 3. Zaakceptowane ustalenia
Użytkownik zgłosił ogólny brak cofania autokorekty nowych słów, z grzeje jako
przykładem, i oczekuje zachowania odstępu oraz jawnego dodania do słownika.
Realizacja dotyczy wszystkich wpisanych literami wyrazów, bez wyjątku grzeje.
Nie zmieniono domyślnej wartości backspace_tap_mode=0; dodano wąski wyjątek
opisany w polskim/base tekście ustawień.
Kolejność nadal: przygotowanie testowego APK HerBERT/haptyka/BS, potem słownik.
Gemini/PAL zniesione przez użytkownika; bez delegacji i bez monitoringu >60 s/run.
Nie scalono kodu próbnego do main, nie utworzono wydania/tagu ani zmiany wersji.

## 4. Odrzucone rozwiązania
Bez ręcznego dopisywania pojedynczych słów/reguł i duplikowania kluczy słownika.
Nie zastępujemy geometric przez CTC, nie dodajemy surowych wag MLM do geometrii.
Cofnięcie BS nie oznacza automatycznego dodania oryginału do słownika.
Nie odtwarzamy dodawanego wyrazu przez delete/recommit ani ze starych długości
trackera po wycięciu/wklejeniu. Stara podpowiedź nie ma edytować nowego tekstu.
Wcześniejsze INT8 / distilHerBERT safe-rank v4 FAIL nie stają się PASS.

## 5. Nadal planowane
- Po przygotowaniu APK: globalny audyt pokrycia/fleksji i etapów odrzucenia słownika swipe.
- Trzy preferencje czasów stacjonarnego BS przy przyszłych zmianach.
- SI do interpunkcji/różnych kluczy i ograniczenie pamięci: osobne dalsze projekty.
- Inne locale: 14 kluczy herbert_live.xml i edit_typed_autocorrect_restore_help później.
- Licencje mniejszych modeli nadal odłożone na wyraźną prośbę użytkownika.

## 6. Zweryfikowane i niezweryfikowane
Odczytane zakończone runy na kodzie7c651e753ff72b54b8c3ff05bbcc664a0ae7aaf6:
live37510369362 FAILURE, standard37510378362 FAILURE. Android compileDebugKotlin
PASS, standard assembleDebug PASS, oryginalny native conformance2471/232/532 PASS.
Brak zweryfikowanego udostępnionego APK: live artifact11434523202 zawiera raporty,
standard upload APK i dalsze bramki pominięte. Debug/release vital lint pending.

Pure2857 prób /2 FAIL: stare źródłowe skanery wymagały bezparametrowej sygnatury
handleBackspaceUndoAutocorrect, zamiast początku deklaracji z aktualnym parametrem.
W workflow live pipeline Gradle|tee MASKOWAŁ nonzero exit: etap zgłosił success
mimo dwóch FAIL. Poprawiono jawne set -euo pipefail, nie usuwa się bramki ani testów.
Działanie propagation sprawdzone lokalnym failing producer przez tee: PASS.

Osiem mock suites PASS159 testów: import45, SwipeAutocap20, EditorPrediction8,
SuggestionTapPartialReplace11, StripScroll3, BackspaceHold45, PointersBackspace26,
HapticRouting1. BS45 zawiera nowe default restore/next-BS/stale/refused-commit.
LearningFunnel29 prób/19 FAIL:18 null primary_language w fixture,1 stara oczekiwana
spacja w haśle. Ustawiono fixture primary_language=en i oczekiwanie hunter bez spacji,
z zachowaną kontrolą zakazu uczenia. Dwa nowe restored ExactAdd/storage-only/cut-paste
testy nie były na liście failures, ale całej klasy nie deklarować PASS.

Standardowy Trivy gate FAIL: site/bun.lock source-map-js1.2.1,
CVE-2026-93749 HIGH, fixed1.2.2 w logu. Zmiana ograniczona do resolved1.2.2/integrity
w lock; istniejące ranges obejmują wersję, package.json bez zmian. Oficjalny npm
registry i pobrany archive36349B zweryfikowane SHA1+SHA512, package metadata1.2.2.
Lokalny mapping SourceMapGenerator/Consumer round-trip/source content PASS.
To nie jest świeży wynik Trivy PASS ani pełny build strony. Bramka nadal blokująca.

Nowy kod aebe6afd82fa0d37fc40d37cd1105ad6c949cc9d zmienia6 plików: workflow pure,
dwa test fixtures, site/bun.lock, dokument wyniku, memory/todo. Kod produkcyjny
BS/HerBERT bez zmian w tej poprawce. Wszystkie6 Git blob SHA zgodne z lokalnymi
bajtami. Lokalnie YAML/shell/exit propagation/source anchors/Bun JSON/API smoke PASS.
Nie uruchomiono lokalnych Kotlin/Android prób: brak toolchain.

Nowy live run37512331919:
https://github.com/jakamilek/CleverKeysPL/actions/runs/37512331919
Standard37512337696:
https://github.com/jakamilek/CleverKeysPL/actions/runs/37512337696
Jednorazowy odczyt obu: in_progress, conclusion null. Monitoring zakończony.
Pełne pure/mock, lint, security i zweryfikowany APK/SHA oraz phone check pending.
Dokładny raport w gałęzi: docs/HERBERT_LIVE_CI_2026-10-06.md.

## 7. Gałęzie i historia
- trial/herbert-live-v1 HEAD aebe6afd82fa0d37fc40d37cd1105ad6c949cc9d,
  parent7c651e753ff72b54b8c3ff05bbcc664a0ae7aaf6.
- Draft PR4: https://github.com/jakamilek/CleverKeysPL/pull/4
  Zawiera wcześniejszą nieprzeniesioną bazę benchmark/editor, bez automatycznego merge.
- Runtime base trial/herbert-fp32-benchmark-v1:0367b334f770d4ad2b1925dc445850e9c19e9b78.
- Producent FP32/source variants oraz historyczne oceny niezmienione.
- Poprzedni brak-kompilacji run37507317429 naprawiony w7c651e7;
  kolejne runy37510369362/37510378362 miały konkretne błędy bramek opisane wyżej.
- Pełna historia jakości SI/dictionary i zaufanych plików: wcześniejsze wspólne checkpointy.

## 8. Artefakty, SHA i punkty integracji
Kod aebe6afd82fa0d37fc40d37cd1105ad6c949cc9d, Git tree2ff6cc69ca5b206aade7018b6605b2c021821914.
Planowany APK artifact cleverkeys-herbert-live-trial-arm64; nie istnieje jeszcze
w zweryfikowanym stanie tego etapu. SHA odczytać dopiero po udanym CI.
Model FP32651798883B SHA256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2.
Producentd831e17b6cb99590d6ba036e92a72b6c3fd0cc7c/run37230171787/artifact11312693984;
siedem compiled file identities i oryginalny manifest zachowane.
Langpack v5 ZIP SHA aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb,
sidecar5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d.
Instrukcja próby runtime docs/HERBERT_LIVE_TRIAL_V1.md, spec Input Behavior.
Nie przesyłano nowych wag ani nie przebudowano słownika.

## 9. Ograniczenia i znane luki
Nie ma jeszcze zweryfikowanego APK ani nowego pełnego CI PASS; telefon nadal pending.
Kompilacja i159 wybranych mock PASS nie oznaczają całej próby. Stary false-green
etap pure naprawiono, nie należy cytować jego success jako wyniku jakości.
Edytor odmawiający read/selection/commit lub nieraportujący caret degraduje do
zwykłego BS; nie zakładać zgodności wszystkich implementacji.
FP32 PSS pozostaje wysoki: wcześniejszy max2132.1MiB całego procesu, ~1775MiB przyrost
po load. Skrócenie kontekstu nie usuwa stałego kosztu modelu. Dwie formy na początku
paska nie dowodzą jakości SI. Nowa zależność strony wymaga świeżego Trivy.
Bajty aktualnie zainstalowanego langpacka użytkownika nie zostały odczytane.
Dodam, grzeje, kasami, nawilżane, odpowiadam, patrzysz, poczekaj, podpowie,
pozdrawiam są nieobecne w sprawdzonych canonical/normalized v5/base indeksach
106363 identycznych kluczy/rang. Dokładne etapy odrzucenia w generatorze pending.

## 10. Następny krok
Po informacji użytkownika o zakończeniu runów odczytać wyniki, poprawić konkretne
błędy jeśli wystąpiły, zweryfikować wszystkie wymagane bramki i SHA APK, udostępnić
testową aktualizację z zachowaniem danych. Próba BS: typed unknown + space →
autocorrection → pierwszy BS original + space + ExactAdd → add bez edycji;
powtórka i drugi BS zwykłe usunięcie spacji; cursor/field/cut-paste stale checks.
Następnie wrócić do GLOBALNEGO producenta słownika.

## 11. Różnica od poprzedniego punktu
Poprzedni checkpoint miał oczekujące nowe CI po zmianie BS. Teraz odczytano failure
obu runów, potwierdzono Android/native/BS/pointer/haptic PASS, naprawiono stare
source scanners i learning fixtures oraz false-green pipeline, zaktualizowano
konkretną podatną resolved zależność strony z weryfikacją jej paczki. Nowe CI
rozpoczęte, brak całego PASS/zweryfikowanego APK/phone check. Słownik nadal następny.
