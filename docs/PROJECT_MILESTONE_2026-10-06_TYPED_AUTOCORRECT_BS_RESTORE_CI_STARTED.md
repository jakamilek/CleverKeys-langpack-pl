# Kamień milowy — BS przywraca wpisany oryginał, zachowuje spację i opcję dodania

Data weryfikacji: 2026-10-06. Wspólny punkt wejścia dla jakamilek/CleverKeysPL
oraz jakamilek/CleverKeys-langpack-pl. GitHub jest źródłem prawdy.

## 1. Zweryfikowane HEAD main przed tym zapisem
- Runtime: 400ac1bb86aeed7dec45bcf0ee6591428b62f824.
- Producent: 30ca127906dd6190b67a7682fe31897a29e82f9b.
- Ten zapis w obu main jest wyłącznie dokumentacyjny.
- Poprzedni punkt: docs/PROJECT_MILESTONE_2026-10-06_HERBERT_LIVE_V1_CI_STARTED.md.

## 2. Architektura i bieżąca implementacja
Geometric pozostaje dekoderem. Jeden klucz CKDT zawiera źródłowe warianty pisowni.
HerBERT FP32 live w trial/herbert-live-v1 pozostaje izolowanym opt-in testem
kolejności dwóch potwierdzonych form pierwszego kandydata przed pojedynczym commit.
SI domyślnie off, osobny zweryfikowany model poza APK, prywatny staging i native
2471 tokenizer / 232 paczki / 532 kandydatów przed READY. Kontekst 32 słowa,
opcje16/32/64, maks4096 UTF-16, oczekiwanie350 ms/100–1000. Brak raw editor text
w nowych raportach/pliku/backupie, bez późnego przepisywania tekstu. Shift/private/
cursor/text/model/settings guards i BS haptics nie zostały usunięte.

Nowy kod 7c651e753ff72b54b8c3ff05bbcc664a0ae7aaf6 dodaje globalny, ograniczony wyjątek
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
Poprzedni live run37507317429 FAILED na compileDebugKotlin:
enabled property setter i metoda setEnabled miały JVM signature setEnabled(Z)V.
Nie powstał zweryfikowany APK; pure/mock/lint/assemble zostały pominięte.
Metoda ekranu została przemianowana na setLiveEnabled, jej wszystkie wywołania
zaktualizowane. Nie oznacza to jeszcze nowego wyniku kompilacji PASS.

Lokalnie PASS: XML nowego zasobu base/Polish oraz wszystkie 11 wgranych Git blob
SHA zgodne z lokalnymi bajtami przed commit. Brak lokalnego SDK/Gradle/Kotlina.
Siedem nowych zarejestrowanych mock testów: restore+drugi BS, stale eligibility,
odmowa bez podwójnego restore, normalny cursor ack, field/text/caret/selection
invalidation, restore/add bez text mutation i stare chipy po cut/paste.
To przygotowane testy; ich wykonanie w Android CI nadal pending.

Nowy live run37510369362:
https://github.com/jakamilek/CleverKeysPL/actions/runs/37510369362
Ostatni jednorazowy odczyt: in_progress, conclusion null.
Osobny CI37510378362:
https://github.com/jakamilek/CleverKeysPL/actions/runs/37510378362
Ostatni odczyt: in_progress, conclusion null. Nie czekać do końca.

Wymagane bramki: Android compile, registered pure z oryginalnym native fixture
markerem, editor/source/swipe/BS/pointer/haptic/learning mock, debug i release
vital lint, assemble i audyt zawartości APK. Nowe APK/SHA i phone check pending.

## 7. Gałęzie i historia
- trial/herbert-live-v1 HEAD 7c651e753ff72b54b8c3ff05bbcc664a0ae7aaf6, parent1b3f3291ba411e6a7afb727a7b68bf6f6ce27f37.
- Draft PR4: https://github.com/jakamilek/CleverKeysPL/pull/4
  Zawiera także wcześniejszą nieprzeniesioną do main bazę benchmark/editor.
  Nie jest automatyczną prośbą scalenia całej historii.
- trial/herbert-fp32-benchmark-v1 bazowy0367b334f770d4ad2b1925dc445850e9c19e9b78.
- Producent: źródłowy FP32 experiment/herbert-fp32-benchmark-v1, langpack v5
  feature/source-variants-trial-v1 i wcześniejsze gałęzie ocen pozostają bez zmian.
- Szczegółowa historia ocen v3/v4: poprzedni wspólny checkpoint.

## 8. Artefakty, SHA i punkty integracji
Kod 7c651e753ff72b54b8c3ff05bbcc664a0ae7aaf6, Git tree025f90163afaf1ee537293ceb5768146e90955b9.
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
Nowe zachowanie nie zostało jeszcze sprawdzone natywnie ani na telefonie.
Edytor odmawiający read/selection/commit lub nieraportujący caret bezpiecznie
degraduje do zwykłego BS; nie zakładamy zgodności wszystkich implementacji.
FP32 wysokie PSS pozostaje: wcześniejszy telefon max2132.1MiB procesu, ~1775MiB
przyrost po load. Zmniejszenie liczby słów nie usuwa kosztu wag/modelu.
Dwie formy na początku paska nie są dowodem jakości SI.
Zainstalowane bajty langpacka użytkownika nie zostały odczytane.
Dodam, grzeje, kasami, nawilżane, odpowiadam, patrzysz, poczekaj, podpowie,
pozdrawiam nie występują w sprawdzonych canonical/normalized v5/base indeksach.
Porównane słowniki miały identyczne106363 klucze/rangi; nie dowodzi to uboższego
specjalnego słownika AI. Dokładne etapy odrzucenia każdego słowa nadal pending.

## 10. Następny krok
Po informacji użytkownika o zakończeniu runów odczytać wyniki, poprawić konkretne
błędy jeśli wystąpiły, zweryfikować wszystkie wymagane bramki i SHA APK, udostępnić
testową aktualizację z zachowaniem danych. Próba BS: typed unknown + space →
autocorrection → pierwszy BS original + space + ExactAdd → add bez edycji;
powtórka i drugi BS zwykłe usunięcie spacji; cursor/field/cut-paste stale checks.
Następnie wrócić do GLOBALNEGO producenta słownika.

## 11. Różnica od poprzedniego punktu
Poprzedni punkt miał uruchomiony niezakończony live run. Teraz ustalono jego
konkretną porażkę kompilacji, poprawiono kolizję setter/metoda i dodano żądany
ogólny mechanizm cofnięcia typed-autocorrect z zachowaniem spacji/jawnym
storage-only dodawaniem. Nowy kod i siedem mock przypadków wgałęzi, CI rozpoczęte;
bez deklaracji APK gotowego, testów PASS lub zmiany harmonogramu słownika.
