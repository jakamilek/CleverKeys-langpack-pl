# PROMPT MIGRACYJNY — CleverKeys Polish Language Pack + dual-casing — 2026-10-01

Kontynuuj istniejący projekt **CleverKeys Polish Language Pack**. NIE zaczynaj od zera i NIE odtwarzaj projektu na podstawie pamięci modelu.

## 1. Oficjalny stan projektu

Właściwe repozytorium projektu:
`jakamilek/CleverKeys-langpack-pl`

Oficjalny baseline:
`ops/baseline-sync-2026-09-20`

GitHub jest jedynym źródłem prawdy dla kodu i stanu projektu.

Zasady:
- nie zgaduj repozytorium, gałęzi, SHA, ścieżek ani statusu CI;
- przed każdą operacją zależną od tych danych zweryfikuj je na GitHubie;
- przy braku potwierdzenia oznacz informację jako **NIEZNANA** i nie wykonuj zależnej operacji;
- nie traktuj innego repozytorium jako zamiennika;
- nie wykonuj merge/promote do `main`;
- stosuj małe, atomowe commity;
- nie zakładaj istnienia lokalnych zmian.

Obowiązujący dokument:
`docs/PROJECT_RULE_NO_GUESSING_2026-10-01.md`

## 2. Dwie warstwy pracy — nie wolno ich mieszać

### A. Pakiet językowy PL

To jest główny projekt i nadal pozostaje aktywny.

Najważniejsze zasady:
- immutable core = dokładnie 100 000 case-insensitive keys;
- moduły są additive;
- moduł nie może zmieniać membership core;
- rozdzielaj membership, kapitalizację, ranking i zachowanie swipe;
- NKJP1M jest podstawowym wtórnym źródłem częstotliwości dla dodatków;
- wordfreq jest sygnałem pomocniczym;
- nie twórz sztucznego wspólnego score NKJP + wordfreq;
- TERC: 16 województw pełna odmiana, 380 powiatów selektywna według częstotliwości/wag, 2479 gmin tylko mianownik;
- pełna odmiana TERC pozostaje artefaktem audytowym, a selected TERC jest wejściem produkcyjnym;
- nie przywracaj automatycznie starych pilotów `reviewed_proper_nouns` ani `reviewed_morphology`;
- aktywne moduły: 100k core, first names, Polish cities/localities, custom/manual, TERC, countries + capitals;
- ręczne/custom wpisy są w `sources/staging/custom_manual.tsv`.

Kapitalizacja:
- jedna wspólna reguła dla wszystkich aktywnych modułów przez `scripts/capitalization_rules.py`;
- przymiotniki rozstrzygają się na lowercase;
- zwykły rzeczownik pospolity ma ochronę lowercase, ale homonimy leksykalne nie mogą być rozwiązywane przez proste 'proper > common';
- nie dodawaj ręcznych wyjątków dla Warszawy, Łodzi czy Maliny;
- `PN` w NKJP nie jest automatycznym autorytetem uppercase;
- kapitalizacja początku zdania jest osobnym mechanizmem runtime.

Znane poprawione powierzchnie miast:
- Gdynia: Gdynia / Gdyni / Gdynię / Gdynią / Gdynio;
- Toruń: Toruń / Torunia / Toruniowi / Toruń / Toruniem / Toruniu;
- Wrocław: Wrocław / Wrocławia / Wrocławiowi / Wrocław / Wrocławiem / Wrocławiu.

Źródła/piny:
- wordfreq git pin: `912caf64b657478d1dff1138efdc078947d54bb1`
- AOSP Polish dictionary SHA256: `75a7a488e014ec3b9dbdb2527f09bca6bb28c250232d9ba50cb0ee1f8738ea45`
- Morfeusz2 1.99.15
- polish-inflection 0.7.3
- NKJP1M revision: `be02836cf3aa0286ad8961d2e4528cdc2f72d044`
- NKJP1M SHA256: `fee31b1d6a682970b4e8ca68b593aea8dadbc8541e875e2d287480d83601e79c`
- AOSP tree: `2b550379fe38213f9d1dcb75478ef2133682685`

Regresyjna lista swipe zawiera m.in.:
`chopin, chopina, goebbels, goebbelsa, catherine, catalina, cameron, carli, carlo, castillo, cali, celli, casino, calli, carrillo, caroli, cassino, compos, gourami, celastial`

Przykład użytkownika:
swipe `carli` może być zdominowany przez zagraniczne kandydatury; nie wolno utożsamiać UserDictionary z zanieczyszczeniem pakietu.

## 3. Dual-casing — aktualny kierunek architektoniczny

Problem:
CKDT/ranker ma jedną tożsamość case-insensitive, natomiast prawdziwe homonimy leksykalne mogą potrzebować dwóch powierzchni:
- `malina` / `Malina`
- `łódź` / `Łódź`
- `warszawa` / `Warszawa`

Założenie:
1. jedna tożsamość leksykalna;
2. dwa audytowane warianty powierzchni;
3. ranking wybiera tylko jeden klucz;
4. dopiero po rankingu resolver prezentacji wybiera primary + alternate;
5. lokalne uczenie może zmienić primary;
6. oba warianty pozostają osiągalne.

Nie należy:
- tworzyć dwóch niezależnych kandydatów rankera;
- zmieniać immutable 100k tylko dla dual-casing;
- wprowadzać ręcznego wyjątku tylko dla Warszawy;
- łączyć dual-casing z sentence-start autocap.

## 4. Audyt 1702 kandydatur

Ścisły audyt core wykazał **1702** kandydatur dual-casing:
- common side: `subst:sg:nom` + `nazwa_pospolita` / `nazwa pospolita`;
- proper side: `subst:sg:nom` + dowolna niepospolita klasa NAME;
- formy fleksyjne wykluczone;
- moduły nie były używane.

Podział:
- 1173 tylko `nazwisko`;
- 254 `nazwisko` + inna klasa;
- 253 bez surname, z bezpośrednią klasą leksykalną;
- 22 tylko `człon_*`.

Przykłady:
- `warszawa`: common + `nazwa_geograficzna | nazwisko`;
- `łódź`: common + `nazwa_geograficzna`;
- `malina`: common + `imię | nazwa_geograficzna | nazwisko`;
- `bardo` nie należy do ścisłego zbioru, bo konkurencyjne proper evidence jest tylko surname-only.

Nie wdrażaj automatycznie wszystkich 1702. Pierwszy eksperyment obejmuje kontrolowane przypadki nie-surname-only.

Dokument:
`docs/CORE_DUAL_CASING_CLASS_AUDIT_2026-10-01.md`

## 5. Audyt przypiętego runtime

Runtime reference:
repo `tribixbite/CleverKeys`
SHA:
`263bd0abc03dec420f60fa073a9d2c5e25a176b5`

Dokładnie zweryfikowane ścieżki:

### CandidateRanker
`src/main/kotlin/tribixbite/cleverkeys/swipe/geometric/CandidateRanker.kt`
blob:
`9d4c6fdf53536a25c3ab9ed0ad120a9d12a93cb4`

Ranker sortuje, a następnie deduplikuje po:
`c.word.lowercase()`

Wniosek: dwa warianty nie mogą zostać dodane jako zwykli równorzędni kandydaci.

### PredictionResult
`src/main/kotlin/tribixbite/cleverkeys/PredictionResult.kt`
blob:
`3584ee89b0e0f9ebeb55dceb8a6112eae244e117`

Kontrakt zawiera:
- `words`
- `scores`
- opcjonalne `languages`

Brak dedykowanego pola wariantów powierzchni.

### WordPredictor
`src/main/kotlin/tribixbite/cleverkeys/WordPredictor.kt`
blob:
`dcb88266857b56003b4c7c1f3f1e763708718e33`

Istnieje mechanizm `userWordOriginalCase`, ale dla jednego klucza przechowuje tylko jedną powierzchnię. To nie rozwiązuje prawdziwego dual-casing.

### SuggestionHandler
`src/main/kotlin/tribixbite/cleverkeys/SuggestionHandler.kt`
blob:
`896bba5c7996fff21705129196f06a2e6dc9848b`

Potwierdzony swipe flow:
- 748–758: `handleSwipePredictionResults()`;
- 779–795: przywrócenie case + sentence-start autocap;
- 799–815: context rescoring;
- 816–835: possessive augment;
- 852–855: zapis do suggestion bar;
- 857+ : auto-insert top prediction;
- 964–975: końcowe ponowne wyświetlenie + next-word append.

### SuggestionBar
`src/main/kotlin/tribixbite/cleverkeys/SuggestionBar.kt`

Może przechowywać listę wyświetlanych Stringów/scores/metas. Kliknięcie sugestii idzie zwykłą ścieżką wyboru sugestii. To czyni bar możliwym miejscem prezentacji alternate.

Pełny audyt:
`docs/CLEVERKEYS_RUNTIME_DUAL_CASING_AUDIT_2026-10-01.md`

## 6. Resolver — etap 1

Istnieje pure resolver:
`docs/runtime-patches/DUAL_CASING_RUNTIME_PATCH_2026-10-01.patch`

Model:
`CaseVariantSet(key, defaultPrimary, alternate)`

Obsługiwane są obecnie tylko:
- lowercase;
- first-letter-capitalized.

Eksperymentalna polityka:
- minimum 5 obserwacji;
- minimum 2 przewagi nad drugim wariantem;
- przy równych danych wracamy do audytowanego default;
- oba warianty pozostają dostępne.

Test host-JVM:
`CASE_VARIANT_RESOLVER_SELFTEST=PASS`

## 7. Aktualny patch integracyjny V2

Obowiązujący patch:
`docs/runtime-patches/DUAL_CASING_RUNTIME_INTEGRATION_V2_PATCH_2026-10-01.patch`

Blob SHA:
`a771440c28d235c08256fa72f2d237521502bbd4`

Poprzedni patch:
`docs/runtime-patches/DUAL_CASING_RUNTIME_INTEGRATION_PATCH_2026-10-01.patch`

jest **SUPERSEDED ("zastąpiony")** i NIE należy go nakładać.

V2 zawiera:
- `CaseVariantExperiment` z trzema przypadkami;
- `CaseVariantCatalog`;
- `CaseVariantPreferenceTracker` (in-memory);
- `CaseVariantProjector`;
- `CaseVariantIntegrationTest`;
- proponowane wpięcie do `SuggestionHandler`.

Projektowana kolejność:
1. ranking silnika;
2. przygotowanie ML;
3. projekcja dual-casing;
4. auto-insert aktualnego primary;
5. ten sam stan pozostaje na pasku sugestii.

Wariant alternate jest prezentacyjny, nie leksykalny.

Uczenie:
- ręczny wybór wariantu jest sygnałem;
- auto-insert primary może być obserwacją tylko bez Shift/Caps/autocap;
- stosowane są istniejące bramki uczenia;
- pierwszy eksperyment ma tracker in-memory;
- trwałe przechowywanie dopiero po walidacji.

### Ważna korekta kolejności

Patch V2 został opisany jako projekcja przed auto-insert. Nie wracaj do starszej wersji, która projektowała dopiero po auto-insert.

## 8. Co zostało faktycznie zweryfikowane

Dla V2:
- dokładny runtime plik `SuggestionHandler.kt` został odnaleziony w drzewie SHA `263bd0...`;
- wszystkie 7 kontekstów hunków V2 zostało porównanych z tym dokładnym plikiem;
- nie wykryto błędnych markerów patcha typu `+@@`;
- nie wykryto `++import`;
- sekcje Add File nie mają nieprefiksowanych linii.

**Nie wykonano:**
- rzeczywistego `git apply` na checkoutcie runtime;
- `./gradlew runPureTests` w runtime;
- kompilacji Android runtime;
- testu instrumentowanego paska;
- budowy APK z dual-casing.

Nie nazywaj testu host-JVM testem pełnego runtime.

## 9. Stan repozytoriów — bardzo ważne

Zweryfikowane repozytoria właściciela `jakamilek`:
- `jakamilek/CleverKeys-langpack-pl` — właściwe repo projektu;
- `jakamilek/CleverKeys-animated-gif` — osobny eksperyment GIF, NIE repo runtime dual-casing.

Nie wolno używać `CleverKeys-animated-gif` jako zastępnika.

Weryfikacja wykonana w tym oknie (2026-10-01):
- nie znaleziono potwierdzonego forka/gałęzi runtime użytkownika z prawem zapisu;
- połączenie dostępne dla `tribixbite/CleverKeys` pozostaje reference-only;
- wyszukiwanie repozytoriów właściciela `jakamilek` znalazło `CleverKeys-langpack-pl` oraz `CleverKeys-animated-gif`; drugie repozytorium pozostaje odrębnym eksperymentem GIF i nie jest zamiennikiem runtime.

To ograniczenie należy zweryfikować ponownie w nowym oknie przed wykonaniem jakiejkolwiek operacji zapisu.

## 10. Aktualne gałęzie i SHA projektu — zweryfikowany checkpoint

Checkpoint zweryfikowany bezpośrednio przed zmianą tej dokumentacji:
- oficjalny branch: `ops/baseline-sync-2026-09-20`;
- HEAD baseline: `7665aa1968082ec19068ba2dd30e8e1b58dd5ad5`;
- gałąź eksperymentalna: `exp/dual-casing-runtime-2026-10-01`;
- HEAD eksperymentalny: `3dade89c47814b5226ac4c28ea329cae1da5b038`;
- eksperymentalna gałąź: 9 commitów ahead względem baseline, 0 behind.

**Uwaga:** zapis tej aktualizacji dokumentacji tworzy nowy commit, więc powyższy SHA jest checkpointem poprzedzającym ten commit. Następne okno ma obowiązek zweryfikować rzeczywisty HEAD ponownie.

Jej commity dotyczą zapisanej dokumentacji/patchy eksperymentu dual-casing i nie są zmianą aplikacji runtime.

## 11. Najnowsze dokumenty ciągłości

Czytaj w nowym oknie:
- `docs/PROJECT_RULE_NO_GUESSING_2026-10-01.md`
- `docs/CHAT_HANDOFF_2026-09-25.md`
- `docs/NEXT_CHAT_PROMPT_2026-09-25.md`
- `docs/CORE_DUAL_CASING_CLASS_AUDIT_2026-10-01.md`
- `docs/DUAL_CASING_RUNTIME_DESIGN_2026-10-01.md`
- `docs/CLEVERKEYS_RUNTIME_DUAL_CASING_AUDIT_2026-10-01.md`
- `docs/runtime-patches/DUAL_CASING_RUNTIME_PATCH_2026-10-01.md`
- `docs/runtime-patches/DUAL_CASING_RUNTIME_INTEGRATION_2026-10-01.md`
- `docs/runtime-patches/DUAL_CASING_RUNTIME_INTEGRATION_V2_PATCH_2026-10-01.patch`

## 12. Zadanie dla nowego okna

Najpierw:
1. potwierdź aktualny HEAD `ops/baseline-sync-2026-09-20`;
2. potwierdź aktualny HEAD `exp/dual-casing-runtime-2026-10-01`;
3. sprawdź, czy istnieje teraz właściwy fork/branch runtime użytkownika z prawem zapisu — NIE zgaduj nazwy;
4. jeżeli nie istnieje/prawo zapisu jest nieznane, nie próbuj modyfikować żadnego podobnego repo.

Jeżeli prawidłowy runtime fork z zapisem NIE jest dostępny:
- nie wdrażaj dual-casing do aplikacji;
- kontynuuj tylko dokumentację/analizę/pure-test przygotowanie w `CleverKeys-langpack-pl`.

Jeżeli prawidłowy runtime fork z zapisem JEST potwierdzony:
1. utwórz/zweryfikuj branch dokładnie od `263bd0abc03dec420f60fa073a9d2c5e25a176b5`;
2. zastosuj WYŁĄCZNIE V2;
3. uruchom pure tests;
4. naprawiaj wyłącznie problemy potwierdzone buildem/testem;
5. dopiero po green testach przejdź do minimalnego testu suggestion bar;
6. dopiero potem rozważ CKDT metadata/catalog delivery.

## 13. Nie wolno robić

- nie modyfikować immutable 100k tylko dla dual-casing;
- nie dodawać 1702 przypadków naraz;
- nie tworzyć dwóch kandydatów rankera różniących się tylko case;
- nie zmieniać geometrii swipe;
- nie dodawać ręcznych wyjątków typu `Warszawa`, `Łódź`, `Malina`;
- nie mieszać sentence-start autocap z preferencją leksykalną;
- nie zapisywać trwałych preferencji przed walidacją eksperymentu;
- nie zmieniać `main`;
- nie używać innego repo jako zamiennika.

## 14. Kluczowa odpowiedź na pytanie "czy zmieniamy już aplikację?"

Na obecnym stanie: **NIE.**

Budowa pakietu językowego nadal jest głównym projektem. Dual-casing ujawnił ograniczenie runtime, dlatego przygotowaliśmy eksperymentalny patch aplikacji, ale **kod aplikacji CleverKeys nie został jeszcze zmodyfikowany**.

Do tej chwili:
- pakiet PL jest rozwijany w `jakamilek/CleverKeys-langpack-pl`;
- patch runtime jest przechowywany jako dokumentacja/patch w tym repo;
- `tribixbite/CleverKeys` pozostaje niezmieniony;
- nie ma APK zawierającego dual-casing.

## 15. Styl pracy

Odpowiadaj po polsku.

Gdy używasz nazwy/terminu/zwrotu w innym języku, podawaj polskie tłumaczenie w nawiasie, najlepiej w cudzysłowie, np.:
- runtime ("kod aplikacji wykonywany na urządzeniu"),
- patch ("łatka"),
- ranking ("szeregowanie"),
- surface ("powierzchnia tekstowa"),
- alternate ("wariant alternatywny"),
- primary ("wariant główny"),
- baseline ("stan bazowy").

Najważniejsze:
**NIE ZGADUJ. ZAWSZE KONTYNUUJ OD RZECZYWISTEGO STANU GITHUB.**
