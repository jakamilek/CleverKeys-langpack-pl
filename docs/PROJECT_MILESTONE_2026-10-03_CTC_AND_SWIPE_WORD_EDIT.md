# Kamień milowy — CTC PL i edycja słowa po swipe

Repo: jakamilek/CleverKeys-langpack-pl.
[Zapis w drugim repozytorium](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-03_CTC_AND_SWIPE_WORD_EDIT.md).

Data weryfikacji: 2026-10-03 UTC. Status: audyt wykonalności i wymagania użytkownika; bez implementacji runtime.

## 1. Zweryfikowany baseline
Snapshot main przed dokumentacyjnym zapisem:
- CleverKeysPL: 1e7333fe7ecd8bd0420c642454349af7bd284b70.
- CleverKeys-langpack-pl: 2de3ea96795e4f85d36068c3fa347ee9e0fef39d.
Poprzedni milestone: PROJECT_MILESTONE_2026-10-03_SOURCE_CATEGORIES.md. Code main nie zmieniony w tym etapie.

## 2. Stan architektury
CKDT V2 utrzymuje jeden klucz dla wariantów kapitalizacji. Zaakceptowany kontrakt LANGUAGE_INTELLIGENCE_API_V1_FINAL_2026-10-02.md przewiduje surfaceKey i capitalization.variants w language-intelligence.json. Produkcyjny generator/parser/provider nadal niewdrożony. LanguagePackManager kopiuje wybrane człony, lecz nie instaluje nowego sidecara.

CtcAzProjection wykonuje lowercase/NFD/usunięcie Mn/joinerów, następnie ß/œ/æ/ø i wymaga a–z. Brak ł→l. AccentNormalizer już ma ł→l, ale CTC nie używa tej samej funkcji. To luka implementacji, nie zakaz polskiego wynikający z samego CTC.
CtcScriptProjection.projectLexicon zachowuje tylko zwycięzcę częstotliwościowego kolizji znormalizowanych słów. Warianty diakrytyczne różnych kluczy wymagają osobnego zachowania alternatyw; nie utożsamiać tego z łódź/Łódź.

## 3. Wymagania użytkownika
Jedna pozycja słownikowa z potwierdzonymi wariantami ma umożliwiać dwa pierwsze miejsca paska dla najlepszego klucza: łódź, Łódź, następne słowo. Brak AI jest legalnym samodzielnym etapem. Dostępność wariantów wynikająca z konstrukcji próby nie jest dowodem jakości AI.

Nowe wymaganie: po swipe Łódź użytkownik dopisuje i, uzyskuje Łódźi i otrzymuje Łodzi oraz łodzi na pierwszych miejscach. Wybór zastępuje cały edytowany token. Nie dodawać niepoprawnego Łódźi do słownika.
łódź i łodzi są różnymi powierzchniami fleksyjnymi/kluczami; Łodzi i łodzi są wariantami kapitalizacji klucza łodzi.

## 4. Odrzucone uproszczenia
Nie wystarczy dopisać pl do listy wspieranych języków lub obniżyć progi dopuszczenia. Nie twierdzić, że sama projekcja dowodzi jakości na polskich śladach.
Nie wymagać od razu nowego modelu: standardowe a–z QWERTY może użyć bieżącego modelu po naprawie projekcji, pod warunkiem pomiaru.
Nie doklejać automatycznie każdej litery po swipe: polskie i może rozpoczynać osobny wyraz. Nie hardkodować zamiany Łódźi→Łodzi.

## 5. Planowane, niewdrożone
CTC: dodać jawne ł→l w projekcji, odświeżać cache oceny zainstalowanych pakietów po zmianie polityki, zachować wszystkie kanoniczne klucze kolidujące pod jedną ścieżką, wykonać pomiary na realnych PL śladach i układach.
Edycja: odczytać cały token z InputConnection, powiązać zmianę z edytowanym słowem po swipe, generować słownikowe korekty/fleksję, rozwinąć potwierdzone warianty i zastąpić cały token po wyborze.
Sygnał edycji przy automatycznej spacji pozostaje do rozstrzygnięcia. Możliwe rozwiązania: jawne wejście w edycję/umieszczenie kursora na końcu słowa albo propozycje korekty łączącej poprzedni wyraz z wpisaną końcówką, zatwierdzane dopiero stuknięciem. Nie zmieniać automatycznie zwykłego wpisywania następnego wyrazu.

## 6. Niezweryfikowane
Nie uruchomiono ONNX, Androida ani realnych swipe. Nie zmierzono accuracy/RAM/latencji PL. Pełny słownik bazowy 100k jako osobny artefakt nie był częścią pomiaru; pomiar dotyczy dokładnie preview 106363.
Nie dowiedziono pozycji Łodzi w istniejącym fuzzy rankingu ani automatycznej obsługi tego scenariusza. Nowy model/trening może być potrzebny dla innej geometrii z osobnymi polskimi klawiszami lub po negatywnej ewaluacji; nie jest dziś warunkiem naprawy ł.

## 7. Gałęzie i historia
Experiment/context-surface-window-v1 i Draft PR #4 pozostają bez promocji/merge; ostatni znany wynik 90b836adb4970c3fcc1cf44bbbc3a2ea45e2da52. Gałęzie historyczne według SOURCE_CATEGORIES, ich HEAD nie sprawdzano ponownie.

## 8. Pomiar i dowody
Pakiet z udanego run 36916501466, artifact 11189614575, source a1fa0193fc504e5fe81d9d43c23fd9a1e52ad307. Historyczny preview, nie nowy build main.
- ZIP pakietu SHA256: 301b0b9c7c4c7b96ac7a2545bf27745b6ee38c87f5d04133ede490008d861945.
- dictionary.bin SHA256: 087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20.
- Zgodność z zachowanym SOURCE_METADATA audytem i z ZIP-em wewnątrz pobranego archiwum potwierdzona.
Statyczne odtworzenie polityki projekcji Pythonem (Unicode NFD, Mn, joinery i te same ekspansje), bez Kotlin/ONNX:
| Polityka | Projectable/106363 | Top1000 według rank/file order | Kolizje rekordów / grupy |
|---|---:|---:|---:|
| Obecna | 88341 (83,056%) | 905/1000 | 4821 / 4792 |
| Z ł→l | 106362 (99,99906%) | 1000/1000 | 5523 / 5434 |
Obecne progi CtcImportedPackSupport: min1000, całość98%, head99%. Pierwszy wariant nie przechodzi, drugi spełnia kryteria projekcji. Ostatni nieprojektowalny wpis: Papua-Nowa Gwinea (spacja). Nie usuwano go z pakietu.
Żadne z projektowalnych słów nie przekracza 32 ramek przy budżecie długość+liczba powtórzonych sąsiednich liter.
łódź→lodz, łodzi→lodzi, żółć→zolc po naprawie. Pomiar reachability projekcji, nie accuracy i nie gwarancja zachowania przegranych kolizji.
Sprawdzone aktualne pliki: CtcAzProjection, CtcImportedPackSupport, CtcCkdtLexicon, CtcScriptProjection, CtcInstalledPacks, CkdtDictionaryReader, CtcEngineAdapter, AccentNormalizer, WordPredictor, FuzzyPrefixMatcher, PredictionContextTracker, KeyEventHandler, SuggestionHandler, SuggestionBar.

## 9. Ograniczenia i luki
Domyślne zatwierdzenie swipe dodaje spację. KeyEventHandler obsługuje jej pochłanianie dla interpunkcji; zwykła litera unieważnia pending auto-space. SuggestionHandler.handleRegularTyping dopisuje literę do currentWord i przy pierwszej literze czyści lastAutoInsertedWord. Nie jest to gotowy tryb edycji wcześniejszego słowa.
Istnieje fuzzy prefix matching i obsługa zastępowania słowa. Zwykłe dopasowanie prefiksu nie wystarczy, bo łódźi nie jest prefiksem łodzi. Można wykorzystać korektę podobieństwa i źródłowe relacje fleksyjne. Kapitalizacja wszystkich kandydatów od uppercase prefix wymaga obejścia dla jawnie wybranego wariantu lowercase.
Historyczne pl.cklm/ADR, long-context, licencje modeli i inne luki według poprzedniego milestone’u pozostają bez nowej weryfikacji.
Zapis nie zmienia architektury wykonawczej. Przed implementacją respektować instrukcje runtime i wymagane przeglądy zmian.

## 10. Następny krok techniczny
Dwa osobne zakresy: testowane ł→l+cache+zachowanie kolizji dla CTC PL oraz testowany tryb edycji słowa po swipe z fleksją i wariantami. Najpierw regresje/pomiar projekcji i scenariusze InputConnection; następnie realne polskie ślady i telefon. Generowanie końcówek z danych źródłowych, bez ręcznych wyjątków.

## 11. Delta
Ponownie zweryfikowano historyczny bloker CTC na aktualnym kodzie; zmierzono skalę i symulowaną naprawę na rzeczywistym artefakcie. Utrwalono deterministyczne dwa warianty pierwszego klucza oraz nowe wymaganie edycji/fleksji. Poprzednie wyniki AI pozostają bez zmian; produkcja niewdrożona.
