# Backspace: ruch zaznaczenia taki jak na spacji — v13

## 1. Zweryfikowany stan i data
2026-10-04. Przed aktualizacją wyniku CI main CleverKeysPL:
6017f6b2b478ff9c3c8ee2a192c9d85adef5deb3; main CleverKeys-langpack-pl:
a5826b7bf5a8d135ca19f2213fdf5918b7307279. Oba mainy otrzymują wyłącznie
aktualizację tego dokumentu ciągłości. Runtime trial docs/source-variants-integration-v1 przesunięto fast-forward
z 23b6f6923344f69a11df14e6f01d22f0e8abecd8 do
9582257fd7deeb849f0c97550babdd01708799fa; draft PR #1 pozostaje otwarty.
Wszystkie 26 zmienionych blobów nowego drzewa zweryfikowano względem plików lokalnych.

Wspólny zapis: [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-04_BACKSPACE_SLIDER_V13.md)
oraz [CleverKeys-langpack-pl](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-04_BACKSPACE_SLIDER_V13.md).

## 2. Architektura
SliderMotion jest wspólną czystą polityką dla Pointers.Sliding oraz nowoczesnego
Backspace DRAG. Przechowuje ułamkową odległość, prędkość palca i jej wygładzenie.
slide_step_px, slider_speed_smoothing i slider_speed_max są przechwytywane w
ConfigSnapshot przy dotknięciu. Spacja przesuwa kursor, BS granicę zaznaczenia.
DRAG nie ma timera; nieruchomy palec nie przesuwa zaznaczenia.
WORD_PREVIEW / WORD_GAP zachowują cykl v12: 350 ms podglądu i 200 ms przerwy.
Przejście do DRAG unieważnia timer słów do końca tego dotyku.

## 3. Zaakceptowane ustalenia
Użytkownik przyjął v12 na telefonie („działa ekstra”), następnie zlecił taką samą
reakcję BS na ruch jak przy przesuwaniu kursora na spacji. Wolny ruch daje precyzję,
szybki przyspiesza; zatrzymanie palca zatrzymuje zaznaczenie; ruch w prawo je cofa.
Współdzielimy istniejącą czułość i parametry przyspieszenia ze spacją. Zachowujemy
usuwanie kolejnych słów przez nieruchome przytrzymanie, kasowanie zaznaczenia po
puszczeniu według istniejącego ustawienia, własność dotyku poza BS i separatory.
Priorytetem interfejsu jest polski.

## 4. Rozwiązania odrzucone
Dotychczasowy automatyczny repeat DRAG, hamowanie i dystans wznowienia są zastąpione
ruchem palca. Nie pozostawiamy aktywnych suwaków, które niczego nie kontrolują.
Nie kasujemy danych użytkownika, nie odczytujemy nowych ustawień w połowie dotyku,
nie wysyłamy niezweryfikowanego DEL przy odmowie edytora. Nie wznawiamy cyklu słów
po zatrzymaniu DRAG. Nie ma merge/tagu/release ani zmiany wersji aplikacji.

## 5. Niewdrożone plany
Osobne suwaki 350/200 ms dla cyklu słów pozostają planem. AI/CTC i ranking kontekstowy
są osobnym etapem. Sześć zmienionych opisów współdzielonego ruchu w 20 innych zestawach
językowych zapisano w memory/todo.md: cs de es fa fil fr hu in it ja ko lv nl pt ro ru
tr uk vi zh-rCN. Polskie i bazowe angielskie opisy są aktualne.

## 6. Weryfikacja i jej granice
Lokalne PASS: git diff --check; XML PL/EN i unikalne nazwy; generator wyszukiwarki
ustawień — 145 wpisów po usunięciu sześciu kontrolek; frozen Bun 1.3.11 install;
Astro — 84 strony; 104 wewnętrzne odnośniki wiki/spec na czterech zmienionych stronach
rozwiązują się do plików. Skan potwierdza, że stare klucze mają w runtime tylko
klasyfikację deprecated i usuwanie przy resecie własnej grupy. Lockfile bez zmian.
Zdalne drzewo b3a74f7886e83e79e7a0455d057d5a0e0116ff06 ma 26 blobów zgodnych
z przygotowanymi plikami; bazowe bloby zweryfikowano na dokładnym 23b6f692.

Aktualne zarejestrowane zestawy: BackspaceGestureTest 18 przypadków,
PointersBackspaceHoldTest 26, BackspaceHoldTest 36, EditingSettingsPolicyTest 4,
EditingSettingsReadTest 4. Zastąpiono testy starego repeat/brake testami ruchu.
Obejmują zatrzymanie, ułamkową odległość, szybkość palca, cofanie, wspólną czułość,
rzeczywisty Pointers.Sliding vs BS, timer słów i stare wiadomości, edytor/Unicode oraz
deprecację preferencji. Wykonanie jest już potwierdzone poniższym CI.

[CI run 37192552115](https://github.com/jakamilek/CleverKeysPL/actions/runs/37192552115)
zakończył się SUCCESS dla dokładnego 9582257fd7deeb849f0c97550babdd01708799fa.
Logi JUnit potwierdzają 2801 testów pure JVM i 248 skupionych, łącznie 3049.
BackspaceHoldTest przeszedł 36 przypadków, PointersBackspaceHoldTest — 26.
assembleDebug, lint debug i release, Code Quality Checks, Security Scan (gate fixed
HIGH/CRITICAL) oraz APK Size Analysis zakończyły się sukcesem.
Upload test results nadal zgłasza brak build/reports/tests/: liczby i wynik testów
potwierdzają logi JUnit, nie osobny artefakt raportów. APK i lint-results są dostępne.
Lokalnie brak Android/Kotlin toolchaina. Wcześniejsze monitorowanie zakończono po
około 29 sekundach; wynik odczytano po zgłoszeniu użytkownika. Limit monitorowania
pozostaje 60 sekund łącznie na build. V13 jeszcze nie przyjęto na telefonie.

## 7. Gałęzie i historia
Runtime trial pozostaje na docs/source-variants-integration-v1 i draft PR #1.
V12 przeszedł run 37189695279: 3044 testy, assembly i oba lint; użytkownik zaakceptował
gesty na telefonie. Wynik v12 nie dowodzi działania nowej dynamiki v13.
Producer feature/source-variants-trial-v1 pozostaje na
bb55e87f5bfa2c7ce2a3eb2214cf5a7f3031205f. Nie zmieniono generatora ani langpacka.
Przyczyna wcześniejszych v5/v6 niepowodzeń nadal nie jest dowiedziona.

## 8. Artefakty i integracja
Commit runtime 9582257fd7deeb849f0c97550babdd01708799fa; rodzic 23b6f692.
Marker placu testowego: backspace-slider-v13. Nowa klasa SliderMotion w zwykłym source
set; istniejące zarejestrowane zestawy testowe obejmują jej regresje.
stepBackspaceHold otrzymuje podpisaną liczbę punktów Unicode i wykonuje jeden
zweryfikowany setSelection na ruch, ograniczony buforem i początkowym kursorem.
Brak dodatkowych IPC dla każdego znaku szybkiego ruchu; maksymalnie 256 znaków/ruch.

Nowy [apk-debug v13, artifact 11299851311](https://github.com/jakamilek/CleverKeysPL/actions/runs/37192552115/artifacts/11299851311)
ma 97024300 bajtów; GitHub podaje digest artefaktu ZIP
sha256:07716ecd6f6a8a3ce9974fc324add39d23e52d73de5cd3e304d2e4c406f61e85
i wygaśnięcie 2026-10-11T09:40:40Z. To digest ZIP, nie pojedynczego APK.
lint-results: artifact 11299178794, 16107 bajtów; digest ZIP
sha256:db0d9226150ecec13799982df2355bdfbd832155212196c218fc9d29d4f68b95.
Wcześniejszy v12: artifact 11298891131 / run 37189695279.
Pack v4 i jego pochodzenie pozostają w
[kamieniu kapitalizacji](PROJECT_MILESTONE_2026-10-04_FUNCTION_WORD_CASING.md).
Nie sprawdzano ani nie potwierdzano wyników osobnego producer CI w tym etapie.

## 9. Ograniczenia
Nowoczesna ścieżka wymaga API zaznaczania edytora; pola prywatne, terminale i
nieobsługiwane edytory zachowują fallback. Unicode oznacza punkty kodowe, nie pełne
klastry grafemów. Granica odczytu pozostaje 4096 jednostek UTF-16. Stacjonarny cykl
nie usuwa obciętego początku wyrazu ani nie przechodzi przez końcowy znak nowej linii.
Ruch pionowy nie przyspiesza poziomego BS; diagonalne flicki zachowują drogę subkeys.

Sześć starych kluczy backspace_pause_enabled / pause_dp / resume_dp / speed_percent /
fast_percent / accel_percent jest ignorowanych przy odczycie i imporcie oraz pomijanych
w eksporcie. Reset BS usuwa je wyłącznie w swojej grupie; nie resetuje wspólnych
ustawień spacji. Wspólne klucze zachowują dotychczasowe typy i zakresy backupu.
releaseDelete nadal dotyczy tylko puszczenia, nie automatycznego cyklu przy hold.
Cancel nie przywraca wcześniej skasowanych słów. Phone/instrumented/minified/
performance pozostają otwarte. Hostowe testy CI są PASS; nie zastępują akceptacji
ruchu i wyczucia gestów na telefonie.

## 10. Następny krok
Zainstalować APK v13 z potwierdzonego artefaktu. Na telefonie porównać
spację/BS przy powolnym i szybkim ruchu, zatrzymanie bez cofnięcia, ruch w prawo/lewo,
puszczenie po zaznaczeniu oraz stacjonarny cykl trzech słów i przejście z niego do
DRAG. Sprawdzić wpływ wspólnej czułości na oba gesty i separator po usunięciu.
Zachować limit monitorowania; nie promować trial do main bez odrębnego zlecenia.

## 11. Różnica wobec poprzedniego kamienia
[Poprzedni etap v12](PROJECT_MILESTONE_2026-10-04_BACKSPACE_DIRECT_V12.md) wprowadził
bezpośredni start zaznaczania i cykliczne usuwanie słów. V13 zastępuje dynamikę DRAG
mechanizmem spacji i porządkuje jego ustawienia; zaakceptowany cykl słów pozostaje.
Lokalne kontrole oraz nowy CI są zielone: 3049 testów, assembly i oba lint.
APK v13 jest dostępne; weryfikacja i akceptacja telefonu pozostają otwarte.
