# Kamień milowy — ścieżka wdrożenia z geometric

Repo: jakamilek/CleverKeys-langpack-pl.
[Zapis drugiego repozytorium](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-03_GEOMETRIC_IMPLEMENTATION_PATH.md).

Data: 2026-10-03 UTC. Status: utrwalone decyzje rozmowy oraz proponowana kolejność implementacji. To dokumentacja; kod produkcyjny nadal nie zmieniony.

## 1. Zweryfikowany baseline
Main przed tym zapisem:
- CleverKeys-langpack-pl: 07f4c5a9337a543eda468c673d0b362de99b5591.
- CleverKeysPL: e7c213273e257389d949d02ce1092cb74f98c5da.
W obu repozytoriach przeczytano najnowszy PROJECT_MILESTONE_2026-10-03_CTC_AND_SWIPE_WORD_EDIT.md. Historyczne wyniki AI: SOURCE_CATEGORIES.

## 2. Architektura
Wybrana podstawa dalszych prac PL: istniejący geometric. Langpack dostarcza źródłowo potwierdzone dane; wspólny runtime interpretuje je po rozpoznaniu/rankingu słowa. Jeden lowercase surfaceKey, potwierdzone warianty w sidecarze zgodnym z LANGUAGE_INTELLIGENCE_API_V1_FINAL_2026-10-02.md.
Warstwa prezentacji wariantów nie zależy od CTC ani od modelu kontekstowego.

## 3. Ustalone w rozmowie
Użytkownik ocenia geometric jako działający bardzo dobrze i zaakceptował skupienie dalszych prac na langpacku, wariantach i edycji słów z tym silnikiem. CTC nie jest wymagane dla tych funkcji.
Bez duplikatów CKDT ze względu na case. Dane pochodzą ze źródeł, nie z ręcznych per-word opisów.
Cel użytkowy: poprawne słowo i zapis w top3, top1 drugorzędny. Dla najlepszego klucza z dwoma wariantami pokazać oba na pierwszych dwóch miejscach; zachować kolejne słowa dekodera.
Nowe wymaganie edycji: Łódź+i→Łódźi→propozycje Łodzi/łodzi i zastąpienie całego tokenu po wyborze. Automatyczna spacja i znaczenie i jako osobnego wyrazu wymagają osobnego rozstrzygnięcia UX.

## 4. Rezygnacje i odłożenie
Wykluczone: duplikaty case w CKDT, ręczne znaczenia, reguły per-word dopasowane do wyników i prezentowanie konstrukcyjnego top3 jako sukcesu AI.
CTC PL odłożone; nie usuwać silnika z klawiatury. Trening nowego modelu nie jest częścią obecnego etapu.
Nie wdrażać badanego NLI z kategoriami do produkcji: wykazana regresja. Nie odrzucać samych metadanych ani przyszłego AI.
Wybór/uruchamianie modelu kontekstowego oraz interpunkcja odłożone do ukończenia podstawowego mechanizmu i pomiarów.

## 5. Proponowana kolejność, niewdrożona
1. Małe kompletne wdrożenie wariantów: deterministyczny eksport źródłowych form do sidecara, manifest/SHA, instalacja i parser/provider, rozwinięcie najlepszego klucza geometric na pasku, dokładny wybór/zastąpienie. Dane generowane z dowodów, początkowa próba ograniczona; nie ręczna lista wyjątków w runtime.
2. Po walidacji rozszerzyć automatyczny eksport na kwalifikujące się słowa pakietu z coverage/conflict report. Nie obiecywać wariantów tam, gdzie nie ma źródłowego dowodu.
3. Edycja/fleksja po swipe: świeży token z edytora, korekty słownikowe i źródłowe powiązania fleksyjne, warianty wyniku, zastąpienie całego tokenu. Zdecydować zachowanie auto-space przed integracją, bez automatycznego sklejania każdego następnego słowa.
4. Pomiar na realnym geometric: osobno poprawny klucz w top3 i dostępność poprawnej powierzchni, auto-insert, korekta stuknięciem, opóźnienie.
5. Dopiero potem porównanie gotowych modeli/metod kontekstowych z działającym wariantem bez AI na szerszym niezależnym zbiorze. Dłuższy kontekst i interpunkcja mają pozostać możliwe do dołączenia.

## 6. Niezweryfikowane
Brak rzeczywistego wdrożenia sidecara, Androidowego testu wariantów lub edycji Łódźi. Brak polskiego head-to-head geometric/CTC. Ocena geometric od użytkownika nie jest ilościowym benchmarkiem.
Nie wybrano modelu produkcyjnego ani szczegółów sygnału edycji przy auto-space. Przejście z JSON na format zwarty nie jest teraz wymagane; rozmiar/RAM eksportu mierzyć.

## 7. Gałęzie i historia
Experiment/context-surface-window-v1 / Draft PR #4 pozostają eksperymentem offline, bez merge/promocji. Ostatni znany wynik 90b836adb4970c3fcc1cf44bbbc3a2ea45e2da52. Role historyczne według poprzednich milestone'ów, HEAD gałęzi historycznych nie sprawdzono ponownie.
Kod wykonawczy rozwijać w osobnych gałęziach/PR-ach w odpowiednich repozytoriach.

## 8. Artefakty i integracja
Nie powstał APK, nowy langpack lub model w tym etapie. Zachować dotychczasowe protokoły/źródłowe interpretacje i dowody generatora.
Audyt CTC i statyczny pomiar historycznego preview pozostają w CTC_AND_SWIPE_WORD_EDIT; nie przepisywać ich jako wyniku geometric.
Minimalne próby integracyjne: łódź/Łódź, malina/Malina, warszawska/Warszawska na dowodach źródłowych, jednowariantowy łódzki, słowo bez sidecara i pakiet legacy.

## 9. Granice i kryteria odbioru
Warianty nie tworzą podwójnego członkostwa słownika. Dla najlepszego kwalifikującego się klucza oba warianty zajmują dwa pierwsze sloty; następny odmienny klucz zajmuje trzeci, jeżeli istnieje. To polityka UI, nie dowód trafności rozpoznania.
Jawny wybór lowercase nie może zostać ponownie skapitalizowany podczas zatwierdzania. Początek zdania, Shift/Caps Lock, user casing oraz ordinary next-word typing wymagają określonych reguł i regresji.
Parser/import musi sprawdzać deklarację wersji, hash i limity, zachować fallback dla pakietów legacy.
Nie gwarantować wszystkich wariantów każdego klucza w top3; dwa sloty pierwszego słowa zmniejszają liczbę różnych słów w widocznej trójce.
Pozostałe luki wg poprzednich milestone'ów pozostają bez nowej weryfikacji. Przed zmianami runtime stosować AGENTS/CLAUDE/REPO_INSTRUCTIONS i wymagane przeglądy; ten zapis nie jest zmianą kodu architektury.

## 10. Następny konkretny krok
Przygotować najmniejszą kompletną integrację źródłowego sidecara i wyboru dwóch wariantów z geometric, z testami importer→provider→pasek→InputConnection. Nie rozpoczynać teraz kolejnej kampanii AI ani treningu CTC. Pełny eksport i edycja fleksji w kolejnych etapach po sprawdzeniu podstawy.

## 11. Delta
Ustalono geometric jako podstawę PL i odłożono CTC. Uporządkowano kolejność: warianty w działającej klawiaturze, skalowanie eksportu, edycja/fleksja, realny pomiar, potem kontekstowe AI. Wymagania zachowane; propozycje szczegółów UX i modelu oznaczone jako nieustalone.
