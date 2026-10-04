# Kamień milowy — porównanie SI na langpacku v5

Data weryfikacji: 2026-10-04. Stan: protokół utrwalony, porównanie uruchomione, wyniki modeli oczekujące.

## 1. Zweryfikowany stan repozytoriów

HEAD main przed dodaniem tego dokumentu:
- CleverKeysPL: `ebe319c811f7b37f6a60551dbb38eb74ba20ee60`.
- CleverKeys-langpack-pl: `e1a696cd724df9fc4523702582cbab1ee9388b5d`.

Eksperyment SI jest utrwalony w CleverKeys-langpack-pl, gałąź `experiment/context-surface-window-v1`, commit `00a7bf5999e8f6419a68c1884919e699c744a927`, draft PR #4. Zweryfikowano 13 dodanych plików i ich Git blob SHA. Oba main otrzymują wyłącznie dokumentację.

Dokumenty przekrojowe: [runtime](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-04_AI_COMPARISON_V5.md) i [langpack](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-04_AI_COMPARISON_V5.md). Poprzedni punkt wejścia: `docs/PROJECT_MILESTONE_2026-10-04_GLOBAL_CASING_V5.md` w obu repozytoriach.

## 2. Aktualna architektura

Geometric pozostaje dekoderem gestów. Jeden klucz słownika może mieć kilka dopuszczalnych form zapisanych w metadanych; nie powielamy wpisów CKDT dla samej kapitalizacji. Langpack v5 pochodzi z gałęzi `feature/source-variants-trial-v1`, commit `041b28ae4587c531ef73e62933e9151cadb84c33`.

Nowy eksperyment offline porównuje trzy gotowe modele/adaptacje: HerBERT WWM, MiniLM NLI i Qwen3-0.6B z ograniczonym wyborem etykiety, bez swobodnego generowania. Konteksty zachowują pisownię, diakrytykę i interpunkcję. Porównujemy okno dwóch słów z dłuższym oknem, maksymalnie 64 słowa/4096 znaków, oraz metadane z warunkiem bez metadanych. Runtime nie otrzymał jeszcze dłuższego kontekstu ani SI.

## 3. Ustalenia zaakceptowane

Podstawowe kryterium użytkownika to właściwe słowo i forma dostępne w pierwszej trójce. Oddzielnie liczymy top 1, korekty i regresje, żeby ocenić rzeczywistą korzyść z SI. Metadane pochodzą z dostępnych źródeł; nie dopisujemy ręcznych opisów znaczeń poszczególnych słów.

Telefon użytkownika: Nubia Z60 Ultra LV, 12 GB RAM / 512 GB pamięci. Wersja Androida i układ SoC nie są przyjmowane na podstawie domysłu. Najpierw ocena jakości, potem koszt na telefonie. Priorytet tłumaczeń: polski; błędy pozostałych języków zapisywać do późniejszej poprawy.

Użytkownik akceptuje obecne zmiany klawiatury ogólną informacją „działa świetnie”. Nie oznacza to szczegółowej weryfikacji każdej ścieżki ani pomiaru wydajności.

## 4. Rozwiązania odrzucone lub odłożone

Nie wybieramy silnika wyłącznie z powodu rozmiaru modelu ani pamięci telefonu. Nie uznajemy top 3 dla dwóch dostępnych wariantów za dowód przewagi SI. Nie wdrażamy CTC na tym etapie, ponieważ geometric działa dobrze.

Historyczna agregacja NLI po kategoriach nie potwierdziła korzyści: 33/68 top 1 wobec 39/68 bez kategorii. Nowy adapter ma uprzednio ustaloną projekcję metadanych i identyczną hipotezę pisowni w warunkach sparowanych. Historyczny wynik nie jest wynikiem nowego porównania ani dowodem bezużyteczności metadanych. Qwen3.5-0.8B pozostaje możliwym dalszym kandydatem, poza obecną trójką.

## 5. Zaplanowane, jeszcze niewdrożone

Po wynikach jakości: wybór kandydata do próby mobilnej, format i kwantyzacja, opóźnienie p50/p95, start, RAM, energia oraz płynność pisania na Nubii. Docelowe ważenie wyników SI względem geometrycznego wymaga kalibracji.

Przy kolejnych zmianach aplikacji dodać trzy ustawienia czasów stacjonarnego backspace: przytrzymanie do pierwszego zaznaczenia słowa, zaznaczenie do usunięcia (obecnie 350 ms), usunięcie do zaznaczenia kolejnego słowa (obecnie 200 ms). Cykl działa do podniesienia palca. Zachowanie przeciągania pozostaje zaakceptowane. Potrzebne polskie opisy, wyszukiwanie ustawień, kopia zapasowa i reset.

## 6. Weryfikacja i rzeczy niezweryfikowane

Lokalnie przeszło 15 testów stdlib kontraktu: zgodność źródeł i form, powtarzalność danych, brak etykiet odpowiedzi w wejściach modeli, zachowanie rankingów, kompletność i skończoność ocen, sparowane warunki oraz oddzielne poprawki/regresje. Snapshot odtworzono bajtowo z dokładnej paczki v5. YAML oraz przypięcia akcji sprawdzono.

[Run 37218630239](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37218630239), zdarzenie push: kontrola kontraktu SUCCESS; wszystkie trzy zadania modeli pobrały i zweryfikowały v5. Przy ostatnim odczycie instalowały zależności. Wyniki faktycznej inferencji są oczekujące. Osobny run PR 37218634724 zakończył kontrolę kontraktu SUCCESS; nie uruchamia modeli.

Monitorowanie zakończono po 29 sekundach. Limit użytkownika to maksymalnie 60 sekund łącznie na build; nie odpytywać dalej bez informacji o zakończeniu. Nie wykonano nowej inferencji lokalnej: środowisko bibliotek jest uszkodzone, a pobieranie wag było niedostępne. Nie ma pomiarów Androida, kwantyzacji ani zwycięzcy tego porównania.

## 7. Gałęzie historyczne i ich role

- Runtime `docs/source-variants-integration-v1`, draft PR #1: zaakceptowane testy klawiatury; kod v15 `4e51c3b45285fdbfdc93531bd80e228444601818`; późniejszy workflow-only HEAD `6b3b2580094170384e1e0f9a4b72138546ebd884`.
- Producer `feature/source-variants-trial-v1`: langpack v5 i globalna kapitalizacja źródłowa.
- `experiment/context-surface-window-v1`: wcześniejsze eksperymenty zachowane jako historia; nowy podkatalog `experiments/ai_compare_v5` nie nadpisuje ich wyników.
- Historyczne wyniki kategorii: commit `90b836adb4970c3fcc1cf44bbbc3a2ea45e2da52`; historyczna zamrożona próba `e654720e5bcbe9825747b74df2b7d82cdfac4eaa`.

Żadnej gałęzi eksperymentalnej nie scalono, nie wydano wersji ani nie promowano kodu na main.

## 8. Artefakty, SHA i punkty integracji

[Frozen protocol](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/00a7bf5999e8f6419a68c1884919e699c744a927/experiments/ai_compare_v5/PROTOCOL.md), `cases.json`, `source-snapshot.json`, `freeze-manifest.json`, adaptery i workflow są przypięte do commitu przed inferencją.

SHA256:
- manifest zamrożenia: `c96cf08e5ffcb240bdbf39df5ed9c902eab1b65575031e52f139debba5b14996`;
- kanoniczne wejścia 376 zapytań: `1af08d48369a7179f39e214f5147f34c5a9c05029c0572f09b8f51995bbca991`;
- snapshot źródeł: `05270f8ae2c6d88bb8209cb00c83ff3d66ba788544f524ed27fbb5e0b4666794`;
- wewnętrzny ZIP v5: `aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb`.

Paczka źródłowa pochodzi z zakończonego sukcesem runu producenta 37202645255, artefakt 11303920512. Obecny workflow zapisze przewidywania, środowisko, hashe pobranych plików modeli i porównanie; nie publikuje wag. Model revisions: HerBERT `50e33e0567be0c0b313832314c586e3df0dc2297`, MiniLM `0a71e92a985b6e1ad1828cf67ce9c459639c1dca`, Qwen `c1899de289a04d12100db370d81485cdf75e47ca`.

## 9. Ograniczenia i znane luki

104 przypadki / 376 zapytań na model: 64 przypadki form, osiem historycznych rankingów top 5, sześć kontroli jednej formy, cztery przypadki niejednoznaczne, dwie kontrole brakującego klucza i 20 przypadków przecinka/braku znaku przed znanym kolejnym słowem.

Konteksty są nowo napisanymi próbami diagnostycznymi, nie ślepym korpusem zewnętrznym. Część kluczy była wcześniej badana. Baseline dla głównej próby form ma top 1 = 32/64, top 3 = 64/64 z konstrukcji dwóch wariantów. Historyczne rankingi pochodzą z logu użytkownika, nie z nowego dekodowania gestów v5; brak surowych punktów. Sortowanie ocen SI nie jest skalibrowanym połączeniem z geometrią.

Test interpunkcji nie obejmuje końca zdania ani wspólnego przewidywania słowa i znaku. Brak źródła ulic nie jest naprawiany ręcznie. CPU float32, opóźnienia i RSS hostów GitHub nie są pomiarami telefonu. Pełne metadane mogą wymagać skrócenia najstarszego kontekstu do budżetu tokenów; skrócenie jest logowane i jednakowe w sparowanych warunkach danego modelu.

## 10. Następny uzasadniony krok

Po zgłoszeniu zakończenia runu sprawdzić status i logi wszystkich modeli, rzeczywiste przewidywania, kompletność 376 zapytań, hashe kodu/źródeł/manifestu oraz raport porównawczy. Brak jednego modelu oznacza niepełne porównanie. Błędy infrastruktury oddzielić od jakości. Nie dostrajać zamrożonych kryteriów po wynikach.

Ocenę przedstawić oddzielnie dla dłuższego kontekstu, metadanych, rankingów i interpunkcji; dopiero potem zaproponować próbę mobilną. Jeżeli run nie przejdzie, utrwalić poprawkę oraz nowy freeze przed ponowną inferencją.

## 11. Różnica względem poprzedniego kamienia milowego

Poprzedni dokument dotyczył globalnej kapitalizacji v5 i odbioru zmian klawiatury. Ten etap dodaje izolowane, odtwarzalne porównanie trzech modeli z prawdziwym źródłem v5, dłuższym kontekstem, sparowanym wpływem metadanych i pierwszą próbą przecinka. Zapisał parametry telefonu, kolejny backlog ustawień backspace i limit monitorowania. Nie zmienia aplikacji ani paczki v5; wyniki i wybór SI pozostają oczekujące.
