# Audyt kontekstu i wariantów powierzchni — 2026-10-02

**Typ:** audyt kodu i wykonalności; rekomendacje do decyzji, bez wdrożenia nowej architektury.
**Repo kanoniczne:** jakamilek/CleverKeys-langpack-pl.
**Rekord cross-repo:** [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-02_CONTEXT_AND_SURFACE_AUDIT.md).
**Data weryfikacji:** 2026-10-02, Europe/Warsaw.

## 1. Snapshot i różnica względem poprzedniego milestone’u

| Repo | Branch | HEAD audytowanego kodu/danych, przed zapisem audytu |
|---|---|---|
| jakamilek/CleverKeysPL | main | 83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69 |
| jakamilek/CleverKeys-langpack-pl | main | 16a6835bdb3ed415667c63ecee6cc6b1a283c1fb |
| tribixbite/CleverKeys | main | 01b6212d92d96dd8943145a7b6cef2be53c9fe3c |

HEAD-y sprawdzono przez GitHub branches API. Są zgodne ze stanem końcowym poprzedniej rekonstrukcji. Drzewa obu forków pobrano z przypiętych SHA; recursive tree nie było ucięte. Ten zapis dodaje dokumentację, nie zmienia kodu, artefaktów ani membership immutable 100k.

Poprzedni dokument: PROJECT_MILESTONE_2026-10-02_STATE_RECONSTRUCTION.md. Nowość: rozdzielenie rzeczywistej ścieżki tap od swipe, ujawnienie ograniczeń casingowych i kontekstowych, wynik wcześniejszego eksperymentu S3, dostępne zewnętrzne źródła i ocena oczekiwania użytkownika.

## 2. Wymaganie użytkownika i werdykt

Użytkownik oczekuje jednego wpisu słownikowego dla klucza łódź, z informacją o dopuszczalnych odczytaniach i zapisach. Dekoder ma zwracać kandydatów po maźnięciu. Warstwa kontekstowa ma oceniać te kandydatury i ich warianty; może wybrać Łódź jako propozycję główną, zachowując łódź jako alternatywę oraz inne słowa z dekodera, np. lód.

**To jest prawidłowy kierunek architektoniczny.** Atrybuty opisują możliwe odczytania; model kontekstowy musi ocenić, które pasuje do aktualnego tekstu. Same atrybuty nie rozpoznają intencji.

Jedna tożsamość w indeksie nie oznacza jednego znaczenia językoznawczego. Łódź jako nazwa miasta i łódź jako rzeczownik pospolity mogą mieć wspólny klucz techniczny, lecz różne odczytania. Nie trzeba dodawać dwóch członkostw CKDT.

„Słowa podstawowe” rozumiemy jako bazowe kandydatury dekodera, nie wyłącznie lematy. Polski dekoder musi nadal móc rozpoznać formy odmienione, np. łodzi, Łodzi, Łodzią. Sam lemat i zestaw tagów nie zapewniają dekodowania dowolnej formy.

## 3. Fakty z kodu

| Obszar | Potwierdzone zachowanie | Dowód |
|---|---|---|
| Statyczny kontekst | BigramModel ładuje assets/lm/<lang>.cklm; StaticContextLm jest modelem unigram + bigram, nie trigram. Lookup używa lowercase, zachowuje diakrytyki. | [BigramModel, loader](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/BigramModel.kt#L547), [StaticContextLm](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/StaticContextLm.kt#L119) |
| Scoring tap | WordPredictor przekazuje staticContextMultiplier i dynamicContextBoost do UnifiedScore.combine. Domyślne both wybiera max(static, learned), nie iloczyn ani sumę. Przy learned >= 1 statyczne kary poniżej 1 znikają. | [WordPredictor](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/WordPredictor.kt#L2512), [UnifiedScore w SuggestionProvenance.kt](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/SuggestionProvenance.kt#L168) |
| Model użytkownika | ContextModel preferuje pewny trigram i cofa się do bigramu. BigramEntry i TrigramEntry normalizują lowercase + trim. Obserwacje Łódź i łódź nie mają osobnych statystyk kapitalizacji. | [ContextModel](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/contextaware/ContextModel.kt#L286), [BigramEntry](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/contextaware/BigramEntry.kt#L47), [TrigramEntry](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/contextaware/TrigramEntry.kt#L50) |
| Swipe | SuggestionHandler pobiera evidence przez WordPredictor.getSwipeContextEvidence, który odczytuje ContextModel. Nie korzysta tu z StaticContextLm. Domyślny swipe_context_rescoring = false; są dodatkowe bramki nauki/pól i resident stores. | [call site](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/SuggestionHandler.kt#L259), [provider evidence](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/WordPredictor.kt#L1055), [default](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/Config.kt#L354) |
| Matematyka swipe | ln(max(engineScore,1)) + 0.5 ln(boost), boost w [1,5]. Zmiana rank 1 wymaga ratio >= 0.5 oraz progów frequency/probability z NextWordPredictor. Zwracana jest tylko permutacja indeksów. | [SwipeContextRescorer](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/swipe/SwipeContextRescorer.kt#L70) |
| Historia kontekstu | PredictionContextTracker przechowuje najwyżej 2 poprzednie słowa i lowercase. To nie jest pełne zdanie ani historia znaczeń/nazw. | [limity](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/PredictionContextTracker.kt#L33), [commitWord](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/PredictionContextTracker.kt#L381) |
| Deduplikacja | CtcLexiconMerge, CtcRankMerger i geometric CandidateRanker scalają według lowercase. Wstawienie dwóch casingów do zwykłego słownika nie zapewni dwóch sugestii. | [CTC merge](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/swipe/ctc/CtcLexiconMerge.kt#L80), [CTC rank merge](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/swipe/ctc/CtcRankMerger.kt#L48), [geometric](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/swipe/geometric/CandidateRanker.kt#L54) |
| Casing obecnie | User-word casing, Shift/Caps Lock i autocap początku zdania przekształcają istniejące powierzchnie przed rerankingiem swipe. Nie ma tu modelu miasto/rzeczownik. | [SuggestionHandler](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/SuggestionHandler.kt#L892) |
| Pasek sugestii | setSuggestionsWithScores zachowuje listę wejściową bez sortowania czy deduplikacji lowercase. getTopSuggestion wybiera pierwszy element, a swipe automatycznie go wstawia. UI może wyświetlić obie powierzchnie, lecz producent musi je dostarczyć i commit musi je zachować. | [SuggestionBar](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/SuggestionBar.kt#L585), [auto-commit](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/SuggestionHandler.kt#L975) |
| Import pakietu | LanguagePackManager kopiuje konkretne znane człony. Dotychczasowy opcjonalny model.onnx oznacza encoder swipe, a nie model kontekstu. Manifest nie parsuje jeszcze Language Intelligence ani kontekstowego modelu. | [LanguagePackManager](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/langpack/LanguagePackManager.kt#L219) |
| Polski statyczny LM | Nie ma pl.cklm w src/main/assets/lm; builder ma konfiguracje en/es/de/fr/it/pt/sv, bez pl. | [builder](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/scripts/build_static_lm.py#L237) |

Nie wolno używać istniejących progów frequency/probability modelu użytkownika jako automatycznej miary pewności dowolnego transformera. Jego score/logit i liczba obserwacji to inne wielkości. Ogólny scorer wymaga jawnego kontraktu sygnału i osobnej kalibracji.

## 4. Istotny wynik już istniejącego eksperymentu

[Audyt S1/S3 z 2026-09-26](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/docs/eval/2026-09-26-static-lm-replay.md#L11) dokumentuje korzystny wpływ angielskiego statycznego LM na tap, lecz **FAIL S3 dla rerankingu swipe**: najlepsza komórka confirm naprawiła 1 przypadek i zepsuła 3. Builder wprost opisuje ten model jako tap/next-word, NEVER swipe.

To historyczny wynik konkretnego angielskiego modelu i syntetycznego jedno-słownego kontekstu; nie dowodzi, że model polski lub model semantyczny zawiedzie. Dowodzi natomiast, że nie można przedstawiać prostego przeniesienia CKLM do swipe jako już zweryfikowanej poprawy. W poprzedniej odpowiedzi ten istotny warunek został pominięty.

## 5. Dodatkowa luka: ł w dekoderze CTC

[CtcAzProjection.project](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/swipe/ctc/CtcAzProjection.kt#L36) ma jawne rozwinięcia ß, œ, æ, ø, ale brak ł -> l. Unicode NFD nie zamienia ł w l. Po usunięciu combining marks łódź daje łodz, co zostaje odrzucone przez gate a-z. Zatem ten konkretny wpis nie trafia do trie tą projekcją.

[CtcImportedPackSupport](https://github.com/jakamilek/CleverKeysPL/blob/83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69/src/main/kotlin/tribixbite/cleverkeys/swipe/ctc/CtcImportedPackSupport.kt#L78) wprost wskazuje polskie ł jako ograniczenie i mierzy projectability całego importowanego pakietu oraz top 1000. Bez pomiaru rzeczywistego ZIP PL nie podajemy werdyktu eligibility całego pakietu.

AccentNormalizer ma ł -> l, ale CtcAzProjection nie wywołuje tej funkcji. Nie wolno utożsamiać tych dwóch normalizacji. Geometryczny pipeline jest oddzielną ścieżką. Naprawa projekcji CTC wymaga osobnego testu kolizji i coverage, nie tylko dopisania litery.

AI oceniająca wyniki dekodera nie odzyska słowa, którego nie ma w zwróconej liście kandydatów.

## 6. Kontrakt v1: co wystarcza, a czego brakuje

Aktualny kontrakt już przewiduje surfaceKey=łódź, capitalization.variants=[łódź, Łódź], commonNoun=true i properName=true. Jest dokumentacją do implementacji. Bieżące drzewa nie zawierają runtime LanguageIntelligenceProvider ani produkcyjnego language-intelligence.json.

lookup(surface) nie otrzymuje kontekstu. Może dostarczyć metadane, ale sam nie rozstrzyga formy na podstawie zdania.

W v1 commonNoun/properName są flagami całego wpisu, morphology jest pojedynczym opisem, a SurfaceVariant ma tylko surface i casePolicy. To wystarcza do wskazania dwóch zapisów; nie zapewnia strukturalnego powiązania „ten wariant = miasto, tamten = rzeczownik pospolity” ani wielu analiz fleksyjnych. metadata.module=city nie czyni wszystkich odczytań klucza miastem.

**Rekomendacja do dalszego projektu, nie zatwierdzona zmiana v1:** zachować aktualny klucz i dopuszczalne powierzchnie, a dla rzeczywistego użycia semantycznego rozważyć listę analiz/odczytań powiązanych z wariantem, z opcjonalnymi lemma, POS, cechami fleksyjnymi, klasą nazwy własnej i źródłem. Alternatywnie model cased może punktować same tekstowe warianty bez jawnych etykiet znaczeń; wtedy metadata ograniczają dopuszczalne zapisy, a nie stanowią pełnej reprezentacji semantyki.

common noun > proper name powinno określać bezpieczny domyślny zapis przy braku pewnego kontekstu. Nie powinno uniemożliwiać kontekstowego wyboru Łódź. To interpretacja wymagająca doprecyzowania w specyfikacji przed implementacją.

## 7. Proponowany przepływ odpowiadający wymaganiu

1. Dekoder zwraca listę bazowych kandydatów, wraz z niezmienionym score i językiem.
2. Provider odczytuje dopuszczalne warianty i analizy każdego klucza.
3. Wspólny mechanizm runtime ocenia kontekst i warianty wyłącznie tych kandydatur. Model/dane mogą pochodzić z pakietu, ale wykonanie i ranking należą do runtime.
4. Powstaje wynik leksykalny dla wyboru słowa oraz wynik wariantu dla wyboru zapisu. Równoważne zapisy nie dostają dwóch niezależnych bonusów tylko dlatego, że mają wspólny score z dekodera.
5. Po deduplikacji leksykalnej powstaje lista powierzchni: wariant główny, dostępna alternatywa i inne kandydatury. Deduplikacja finalna uwzględnia dokładną powierzchnię i język, aby nie usunąć łódź tylko dlatego, że jest Łódź.
6. Jawny Shift/Caps Lock, autocap początku zdania, wybór użytkownika i commit mają zdefiniowane pierwszeństwo. Na początku zdania zwykłe łódź też daje Łódź; sama wielka litera nie jest dowodem odczytania miasta.
7. Kliknięcie wariantu zachowuje jego konkretny zapis. Personalizacja wariantów, jeżeli dodana, potrzebuje własnej tożsamości/obserwacji; obecne lowercase n-gramy jej nie zapewniają.

To rozszerzanie powierzchni istniejącej kandydatury, zgodne z ideą API bez generowania nowych słów. Nie jest drugą polską wyszukiwarką słów. Langpack może dystrybuować dane/model; nie zyskuje samodzielnego wykonania kodu przy obecnym importerze.

Przykłady oczekiwanego zachowania, **nie wyniki pomiarów**:

| Kontekst przed kandydatem | Główna powierzchnia oczekiwana | Alternatywa |
|---|---|---|
| Moim ulubionym miastem jest | Łódź | łódź |
| Na brzegu stała drewniana | łódź | Łódź |
| W napoju rozpuścił się | lód | inne kandydatury dekodera |
| Brak kontekstu | bezpieczny defaultSurface | drugi potwierdzony wariant |
| Początek zdania | autocap może dać Łódź dla obu odczytań | deduplikacja identycznego wyniku wyświetlania |

Nie należy proponować Lód jako nazwy własnej tylko dlatego, że dowolny rzeczownik można mechanicznie kapitalizować. Wariant taki wymaga podstawy w danych, początku zdania albo jawnego działania użytkownika. Model nie musi jawnie nazywać znaczenia; wystarczy poprawnie ocenić dopuszczalne powierzchnie.

## 8. Gotowe zasoby zamiast treningu od zera

| Zasób | Zweryfikowane informacje | Przydatność i ograniczenie |
|---|---|---|
| [NKJP n-grams](https://zil.ipipan.waw.pl/NKJPNGrams) | Zrównoważony korpus 300M tokenów; n=1..5; zliczenia; lowercase; strona deklaruje CC-BY. | Istniejące dane do lekkiego baseline’u. Nie rozróżnią Łódź/łódź i nie są gotowym CKLM z wygładzaniem/pruningiem. Wymagają konwersji i sprawdzenia tokenizacji. |
| [HerBERT base cased](https://huggingface.co/allegro/herbert-base-cased) | Gotowy polski model BERT, trenowany na kilku korpusach; cased; karta podaje CC BY 4.0. | Kandydat do eksperymentu kontekstowego offline. Nie jest gotowym modelem dla klawiatury ani potwierdzonym resolverem dual-casing. Potrzebny adapter zadania i ocena prefix-only, wielotokenowych słów, rozmiaru i opóźnień. |
| [plT5 small](https://huggingface.co/allegro/plt5-small) | Gotowy polski model T5 z celem denoising; CC BY 4.0; SentencePiece. | Alternatywa do badania; nazwa small nie dowodzi akceptowalnego kosztu Androida ani jakości tego zadania. |
| [PolDeepNer2](https://github.com/CLARIN-PL/PolDeepNer2) | Udostępnia modele rozpoznawania nazw własnych w polskim tekście. | Źródło porównania dla nazw własnych; NER nie zastępuje rankingu wszystkich kandydatów i może polegać na już istniejącym casing-u. |

Nie pobrano wag modeli, nie wykonano inferencji, eksportu ONNX ani pomiaru Androida. Nie potwierdzono gotowego małego modelu, który spełnia całe wymaganie bez adaptacji. Sprawdzone źródła pozwalają rozpocząć od gotowej wiedzy; nie uzasadniają obietnicy „tylko zaimportować i będzie działać”.

N-gramy i schemat słownika nie są alternatywami: pierwsze to możliwy model kontekstu, drugi to reprezentacja dopuszczalnych słów i wariantów. Model cased lub model klas/odczytań może odróżniać warianty bez dwóch wpisów CKDT. Aktualny CKLM i gotowy lowercase NKJP tego nie robią.

## 9. Zalecany następny eksperyment

Najpierw próbka ewaluacyjna: prawdziwe lub odtworzone slates z obu dekoderów, tekst przed kursorem i oczekiwany klucz/wybrany zapis. Zawierać homonimy, odmienione nazwy, zwykłe rzeczowniki, przymiotniki typu warszawski, początek zdania, jawny Shift, brak kontekstu i korektę wariantu przez użytkownika.

Porównać: decoder-only + default casing; metadata + neutralny resolver; gotowy cased model z adapterem. N-gram NKJP opcjonalnie jako baseline wyboru słowa. Bez treningu dużego modelu od zera.

Ewaluować osobno:
- obecność poprawnego słowa w slate (ceiling; przy braku nie ma czego rerankować);
- wybór klucza top-1 i liczby fixed/broken;
- casing top-1 przy poprawnym kluczu, też dla samego lewego kontekstu;
- dostępność alternatywnego wariantu i pozostałych słów;
- zachowanie tap-to-replace i dokładnego commit;
- p50/p95 opóźnienia, pamięć, cold start i rozmiar po eksporcie dopiero dla obiecującego modelu.

Dłuższy kontekst należy pobierać osobno, zachowując case i granice zdań; istniejących dwóch lowercase tokenów nie wystarczy nazwać „kontekstem zdania”. Obliczenia modelu poza wątkiem UI, z snapshotem kursora i odrzucaniem nieaktualnych wyników. Nie wolno opóźniać korekty już wstawionego słowa tak, aby tekst zmieniał się po następnym działaniu użytkownika.

Najpierw izolowany prototyp wyboru powierzchni na istniejących kandydaturach, następnie benchmark gotowego modelu. W przypadku łódź najpierw zapewnić osiągalność kandydatury w wybranym dekoderze; CTC ma opisane ograniczenie ł. Dopiero wyniki uzasadniają wybór modelu i rozszerzenie kontraktu kontekstowego.

## 10. Co pozostaje wiążące i otwarte

**Wiążące z wcześniejszych decyzji:** oddzielne repozytoria, immutable 100k, CKDT V2 i legacy fallback, API jako wiedza o istniejącej kandydaturze, wspólny runtime, bez polskiego drugiego generatora/rankera. Użytkownik doprecyzował oczekiwanie wyboru wariantu na podstawie kontekstu i zachowania alternatywy.

**Odrzucone jako wystarczające rozwiązanie w audycie:** dwie pozycje CKDT różniące się case; same flagi common/proper; sam lowercase CKLM; bezwarunkowe wpięcie statycznego LM do swipe mimo FAIL S3; uznanie istniejącego model.onnx za model semantyczny.

**Nie wdrożono:** parser/provider v1, sidecar, wariantowy resolver, cased context scorer, osobne uczenie casing-u, dłuższy kontekst, nowy człon modelu w ZIP. Wszystkie propozycje z sekcji 6–9 są do decyzji i eksperymentu.

**Znane luki:** brak pl.cklm; ograniczenie CTC ł; agregujący casing modelu użytkownika; dwutokenowy kontekst; API v1 nie wiąże analiz z wariantami; dotychczasowa niespójność dwóch referencji ADR nadal otwarta.

**Historyczne branche:** docs/architecture-runtime-langpack-separation-2026-10-02 (langpack) i docs/architecture-langpack-plugin-model-2026-10-02 (runtime), opisane w poprzednim milestone’ie. Nie analizowano ich ponownie, nie scalano ani promowano.

## 11. Weryfikacja i CI

Przeprowadzono audyt statyczny przypiętych źródeł, przeczytano odpowiednie specyfikacje/testy i raport historyczny S3. Sprawdzono Unicode NFD na przykładach łódź/Łódź/lód: po usunięciu znaków łączących ł pozostaje; to kontrola normalizacji, nie test aplikacji.

Nie uruchamiano pełnego builda, testów Kotlin ani urządzenia; nie zmieniono kodu. Nie przypisuje się obecnemu prototypowi ani modelom nowej skuteczności.

Sprawdzono pełny endpoint Actions runs z head_sha dla obu baseline’ów, nie tylko PR-triggered runs:
- langpack 16a6835bdb3ed415667c63ecee6cc6b1a283c1fb: [push build](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37032314426) — success.
- runtime 83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69: [APK build](https://github.com/jakamilek/CleverKeysPL/actions/runs/37031983557) — success.
- runtime 83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69: [CI](https://github.com/jakamilek/CleverKeysPL/actions/runs/37031983558) — failure. Jobs API wskazuje failure w Security Scan / Gate on fixed HIGH/CRITICAL vulnerabilities oraz Build and Test / Run lint checks; Code Quality Checks success. Nie diagnozowano logów przyczyn ani nie naprawiano tych błędów w ramach audytu.

To aktualizuje poprzedni status „Actions niezweryfikowane”; runtime nie jest globalnie green. Status nowych commitów dokumentacji wymaga osobnego odczytu po ich zapisie.
