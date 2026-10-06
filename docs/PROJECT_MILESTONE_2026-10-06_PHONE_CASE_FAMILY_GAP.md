# Kamień milowy — próba telefonu pozytywna, luka Malina/Maliną i propozycja małej grupy form

Data weryfikacji: 2026-10-06. Wspólny punkt wejścia dla jakamilek/CleverKeysPL
oraz jakamilek/CleverKeys-langpack-pl. GitHub jest źródłem prawdy.

## 1. Zweryfikowane HEAD main przed tym zapisem
- Runtime: 739aceec629eb2987fcd49fb58b1590f3808466b.
- Producent: 4a5b77adf3a9f484ec55abbfef318592e2bfdda4.
- Trial runtime: aebe6afd82fa0d37fc40d37cd1105ad6c949cc9d.
- Ten zapis jest wyłącznie dokumentacyjny, bez nowego kodu lub scalenia.
- Poprzedni punkt: docs/PROJECT_MILESTONE_2026-10-06_HERBERT_LIVE_APK_READY.md.

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

Nowa PROPOZYCJA do omówienia/implementacji, nie zaakceptowana produkcyjna zmiana:
rozwinąć źródłową pisownię również dla bliskiego dalszego kandydata różniącego się
polskim znakiem, następnie ocenić ograniczoną grupę malina/Malina/maliną/Maliną
z zachowaniem każdej wagi geometrycznej, lexical identity i źródła. Grupowanie
początkowo z wyników już obecnych w slacie; bez generowania odmian z powietrza.
Wspólna pisownia bez diakrytyków pomaga odkryć grupę, nie dowodzi wspólnego znaczenia.
Nie spłaszczać całego słownika, nie dodawać caps do wszystkich słów, nie przepisywać
już zatwierdzonego tekstu po późnym wyniku. Zmiana między różnymi CKDT keys wychodzi
poza dotychczasowy case-pair-v1 i wymaga własnych bramek ranking/latency/fallback.
Cztery formy nie mieszczą się wszystkie w Top3; celem jest poprawna forma w Top3,
z zachowaniem alternatyw. Gdy SI zawiedzie/timeout, bliskie źródłowe formy nadal dostępne.

- Po przygotowaniu APK: globalny audyt pokrycia/fleksji i etapów odrzucenia słownika swipe.
- Trzy preferencje czasów stacjonarnego BS przy przyszłych zmianach.
- SI do interpunkcji/różnych kluczy i ograniczenie pamięci: osobne dalsze projekty.
- Inne locale: 14 kluczy herbert_live.xml i edit_typed_autocorrect_restore_help później.
- Licencje mniejszych modeli nadal odłożone na wyraźną prośbę użytkownika.

## 6. Zweryfikowane i niezweryfikowane

Nowa obserwacja użytkownika z telefonu2026-10-06: „jest całkiem dobrze”.
Jedyna zgłoszona luka: „jutro będę widział się z Malina”, oczekiwane „Maliną”.
Wstawiono Malina; pasek według użytkownika: malina,maliną,mamoną.
To obserwacja użycia, nie niezależny benchmark/pełna lista sprawdzonych guardów.

Sprawdzono lokalnie uprzednio zweryfikowane bytes pakietu v5:
language-intelligence.json ma dla surfaceKey malina kapitalizację malina/Malina,
a dla maliną już maliną/Maliną. Czytania źródłowe maliną zawierają lemma
Malina:Sf z NAME imię/nazwa_geograficzna/nazwisko, Malina:Sm1 z nazwisko,
oraz malina z nazwa_pospolita. Brak tu konieczności ręcznego dopisania Maliną.
Bajty aktualnie zainstalowanego pakietu telefonu nadal nie zostały odczytane.

Kod SwipeSurfaceVariants.expand rozwija kapitalizację tylko primary=words.first().
Pozostałe klucze dekodera trafiają bez rozwinięcia źródłowych form.
HerbertLiveSlate.pair dopuszcza wyłącznie dwie pierwsze exactCase formy jednego
lowercase klucza; HerbertCasePair/worker oceniają tylko tę parę.
Zgłoszenie jest zgodne z tą granicą: maliną jest dalszym kandydatem, ale Maliną
nie jest rozwinięte ani ocenione przez obecny live SI. Nie udowodniono na telefonie,
która forma wygrałaby po przyszłej ocenie czterech kandydatów.

Użytkownik zgłosił zakończenie. Oba runy na aebe6afd82fa0d37fc40d37cd1105ad6c949cc9d
zakończone SUCCESS: live37512331919 oraz standard37512337696.
Live android112436390234: compile, pure,9 mock suites, lintDebug, lintVitalRelease,
assemble, APK-content audit i upload SUCCESS.
Standard: build/test/lint, code quality, security fixed HIGH/CRITICAL gate i size PASS.
Bez osłabienia security ani pipeline: wcześniejszy false-green tee jest naprawiony.

Pure2857 PASS w obu runach. Oryginalny marker zgodności2471 token vectors /
232 batches /532 candidates /five inputs PASS w obu logach. To hostowe bramki
fixtures, nie dowód uruchomienia nowej integracji modelu na telefonie.
Live9 mock suites188 PASS (BS45, Pointers26, HapticRouting1, LearningFunnel29
i import/swipe/editor/suggestion pozostałe). Standard18 mock suites293 PASS.
Nie sumować powtórzonych testów jako unikalnych. Source scanners i learning fixture
naprawione w ostatnim kodzie; cała wymagana klasa learning teraz PASS.

Pobrano reports ZIP11436521304,22417B; lokalny SHA256 zgodny z GitHub:
9d0fe3758e2500065584067d4b844dba200b5179278bf2ab35620a96f33426ad.
Odczytano pełne OK(2857 tests), brak FAILURES i mandatory marker. Debug lint XML:
0 Error/Fatal,234 innych issues (nie twierdzić, że brak wszystkich ostrzeżeń).
Release vital lint PASS w jobie/logu.

CI obliczył APK SHA/size i wydrukował identity JSON przed uploadem: codeCommit
aebe6afd82fa0d37fc40d37cd1105ad6c949cc9d, liveAI=true,optInDefault=false,
producer/model/context zgodne z frozen kodem. Audyt APK nie znalazł pakietu
FP32 benchmark/tokenizer fixtures ani giant assets. Lokalny download APK ZIP
odrzucony limitem32MiB; nie przeliczono niezależnie lokalnej sumy APK.
SHA samego APK poniżej pochodzi z obliczenia CI; ZIP digest to osobna suma GitHub.

Gotowy APK jest do próby, nie do release. Phone READY/live accuracy/latency/PSS/
bateria oraz nowe BS/haptyka na urządzeniu nadal NIEZWERYFIKOWANE.

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
Frozen kod aebe6afd82fa0d37fc40d37cd1105ad6c949cc9d, tree2ff6cc69ca5b206aade7018b6605b2c021821914.
APK live artifact11436446299, cleverkeys-herbert-live-trial-arm64:
https://github.com/jakamilek/CleverKeysPL/actions/runs/37512331919/artifacts/11436446299
ZIP35796681B, digestSHA256 b1f8dc0d1ec8697c62fc0bcc88981214d749a8dd574464478ec751ffa9ae5cf7.
APK CleverKeys-v2.0.0-arm64-v8a.apk,35795518B.
APK SHA256 z CI:76f38752684c5502992ecdb5854bbd32d0c643df3efa6e1a35e39c6119f28c6a.
ZIP zawiera też herbert-live-apk.sha256 i herbert-live-apk.json.
Expired=false, expires2026-10-20T18:46:39Z w odczytanej metadata.
Identity diagnosticOnly=false/liveAI=true/optInDefault=false/case-pair-v1,
words32/options16,32,64/wait350ms/BSwordHaptics/nativeConformanceBeforeLive=true.

Zewnętrzny zaufany model, ten sam ZIP co do poprzedniego benchmarku:
https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37230171787/artifacts/11312693984
Producentd831e17b6cb99590d6ba036e92a72b6c3fd0cc7c.
Model artifact11312693984 herbert-fp32-benchmark-v1-model,657295441B.
Expired=false,expires2026-10-18T19:57:49Z w ponownym odczycie listy runu.
GitHub ZIP digest36c2183acca3ae6dca4afb54c28fe4d9d4cb37ec26f3230c94b4e007b494587f.
Wewnętrzny model651798883B SHA256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2.
Siedem compiled identities/original manifest zachowane, poza APK/backupem.

Langpack v5 ZIP SHA aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb,
sidecar5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d.
Słownik nieprzebudowany. Instrukcja na frozen branch docs/HERBERT_LIVE_TRIAL_V1.md.
Starszy docs/HERBERT_LIVE_CI_2026-10-06.md zachowuje historię FAIL; ten checkpoint
jest aktualnym rozstrzygnięciem po udanym rerunie.

## 9. Ograniczenia i znane luki
APK do próby gotowy, ale telefon i niezależna jakość live nadal pending.
Nowy ekran SI ma własny trwały prywatny import; poprzedni ekran benchmarku
używał plików tymczasowych. Zaimportować trusted FP32 ZIP w ekranie SI live.
FP32 PSS nadal wysokie: wcześniejszy max2132.1MiB procesu/~1775MiB przyrost po load.
Skrócenie kontekstu nie usuwa kosztu wag; dwie pierwsze formy to konstrukcja listy,
nie wynik jakości SI. Aktualna bramka security PASS po source-map-js1.2.2.
Debug lint ma ostrzeżenia,0 Error/Fatal. Wymagane gates PASS.
Lokalny rehash APK nie wykonany z powodu32MiB transfer limit; CI SHA+identity
są podstawą udostępnienia GitHub ZIP. Bez twierdzenia o lokalnym binary audit.

Bajty zainstalowanego langpacka użytkownika nadal nieodczytane.
Dodam, grzeje, kasami, nawilżane, odpowiadam, patrzysz, poczekaj, podpowie,
pozdrawiam nieobecne w sprawdzonych canonical/normalized v5/base106363 kluczy.
Dokładne etapy odrzucenia każdego słowa i globalna korekta generatora pending.

## 10. Następny krok
Odpowiedzieć użytkownikowi, że źródłowa forma Maliną już jest w sprawdzonym v5,
a obecny ranking SI/presentation obejmuje tylko kapitalizację pierwszego klucza.
Zaproponować ograniczoną grupę4 form z istniejących bliskich kandydatów, rozwinięcie
ich źródłowej kapitalizacji i przed-commit wybór według kontekstu, bez reguły Malina.
Oczekiwany ranking dla zgłoszenia: priorytet Maliną, także maliną oraz formy bazowe
do wyboru. To plan, nie wynik wykonanego testu i nie nowy APK.

Przed wdrożeniem ranking różnych form: skonkretyzować small-group gate i source/
language/case/geometry guards, zweryfikować score comparability (w tym token count),
regresje poza grupą i cztery kandydaty na telefonie w ramach dotychczasowego deadline.
Nie dodawać surowych MLM wartości do wag geometrii. Wersję case-pair-v1 zachować
jako porównanie; wcześniejszy safe-rank-v4 FAIL pozostaje historycznie ważny.
Globalny audyt brakujących form słownika producenta nadal osobnym kolejnym zadaniem.
Nie zmieniono runtime/producers packs/AI modelu/ustawień ani uruchomiono nowego CI.

## 11. Różnica od poprzedniego punktu
Po gotowym APK użytkownik przekazał pozytywną obserwację z telefonu i lukę wyboru
odmienionej kapitalizowanej formy. Audyt wykazał źródłowe Maliną w sprawdzonym v5,
ale presentation/AI rozwijają tylko pierwszy klucz. Zapisano propozycję małej grupy
form oraz jej wymagane ograniczenia. Brak implementacji nowego rankera, zmiany
packa, nowych wyników jakości/latency albo nowego APK. Poprzednie oba CI PASS
i zamrożony runtime aebe6afd pozostają aktualne.
