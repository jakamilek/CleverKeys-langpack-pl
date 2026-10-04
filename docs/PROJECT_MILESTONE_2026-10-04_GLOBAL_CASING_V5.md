# Globalna kapitalizacja i metadane homonimów — langpack v5

## 1. Zweryfikowany stan i data
2026-10-04. Przed dokumentem main CleverKeysPL:
2e70db8b53563c05c39398a436fec4d8e005fdd2; main CleverKeys-langpack-pl:
93ea8fd86a14c8fc9b9f4a869dd426ea61b33521. Oba mainy otrzymują tylko ten dokument.
Producer feature/source-variants-trial-v1 przesunięto fast-forward z
bb55e87f5bfa2c7ce2a3eb2214cf5a7f3031205f do 041b28ae4587c531ef73e62933e9151cadb84c33.
Nowe drzewo: 8129d6d8456b0bf5df4734bf86b2e52e0328f328; wszystkie siedem zmienionych blobów
zgadza się z lokalnymi plikami i zostały odczytane dokładnie z nowego commita.
Runtime trial docs/source-variants-integration-v1 pozostaje na
4e51c3b45285fdbfdc93531bd80e228444601818 był headem zweryfikowanego APK v15.
Po odczycie runów trial przesunięto do 6b3b2580094170384e1e0f9a4b72138546ebd884:
zmieniono wyłącznie workflow CI, aby wykonywał dwa pominięte zestawy regresji.
Draft PR #1 pozostaje otwarty; kod aplikacji i wersja bez zmian.

Wspólny zapis: [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-04_GLOBAL_CASING_V5.md)
i [CleverKeys-langpack-pl](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-04_GLOBAL_CASING_V5.md).

## 2. Architektura
Audyt każdego CKDT key: obie sondy pierwszej litery, wyłącznie dokładne pojedyncze
formy połączone z generatorem tego samego lematu, pełnego tagu i klas NAME.
Zwykła poświadczona mała forma ma pierwszeństwo; nazwa zostaje alternatywą tego samego
wpisu. Wyłącznie nazwy zachowują dużą literę. Brak zgodnej formy zachowuje CKDT.
Skróty/camelcase poza małą/wielką pierwszą literą zachowują wejściową pisownię.

Pełny audyt JSONL zachowuje wszystkie interpretacje, tagi i dowody. Runtime grupuje
identyczne lemat/POS/NAME/kwalifikatory w lexicalReadings z formami; variantCategoryIds
łączy pisownię i klasy źródła. Łącze provenance.fullAudit podaje SHA i klucz surfaceKey.
Dziewięć dotychczasowych wpisów zachowuje wcześniejsze bogate dowody/GUS.
API v1 pozostaje bez zmian: metadata jest opcjonalnym obiektem opaque.
Wspólny resolver przyszłych buildów rozszerza priorytet zwykłej formy na wszystkie
poświadczone POS; reguła funkcyjna pozostaje wcześniejsza dla zgodności raportu v4.

## 3. Zaakceptowane ustalenia i przyczyna
Użytkownik potwierdza działanie aktualizacji v4, lecz odrzuca jej ograniczony zakres
i żąda globalnej obsługi informacji o zwykłym słowie i odmianie nazwy. Zgłasza Tutaj
w środku zdania. V4 nie był listą dwóch wyjątków: obejmował całą kategorię funkcyjną,
lecz nie eksportował metadanych tych homonimów i nie obejmował wszystkich POS.
Przypięte źródło potwierdza tutaj/adv oraz Tutaj/nazwisko, ale/conj/part/interj
i Ale/imię, lub/conj oraz impt od lubić i Lub/imię/nazwisko od Luba:Sf.
Nie dopowiadamy opisów znaczeń ani ulic/miast na podstawie nazwiska.


Aktualizacja po testach telefonu (2026-10-04): użytkownik zgłasza „działa świetnie”.
To ogólna akceptacja użytkowa dostarczonego etapu, nie pomiar RAM/latencji ani
osobne potwierdzenie każdego punktu checklisty/wersji pliku. Nie przypisujemy tej
wypowiedzi wyniku oczekującego CI 6b3b2580. Użytkownik odkłada nowe opcje czasu BS
do następnej zmiany klawiatury i wskazuje wybór SI jako kolejny temat.

## 4. Rozwiązania odrzucone
Brak blacklisty słów, ręcznych opisów, duplikowania CKDT przez case i nowej listy
ręcznych kategorii. Nie traktujemy sondy z dużą literą jako dowodu nazwy.
Nie zwiększamy limitów Androida ani nie wkładamy pełnego 81 MB audytu do importowanego ZIP.
Pełna nieskompaktowana wersja przekroczyła limit węzłów i została odrzucona.
Nie zmieniamy rangi na podstawie nieistniejących częstotliwości znaczeń.
Bez merge/tagu/release/promocji do main i zmiany wersji aplikacji.

## 5. Niewdrożone plany
Kontekstowe AI, korpusowe wagi poszczególnych interpretacji, pełna morfologia runtime
i szersze źródła dla nierozpoznanych form pozostają osobnymi etapami.
Nie wykonano pełnego głównego preview pipeline. Inne tłumaczenia pozostają w backlogu.
Globalny audyt nie oznacza metadanych wszystkich wyrazów w pamięci klawiatury:
runtime zawiera konflikty/poprawki/kontrole; pełna analiza wszystkich jest w audycie.


Backlog zaakceptowany przez użytkownika — czasy stacjonarnego Backspace:
1. „Czas przytrzymania BS”: od naciśnięcia do podglądu/zaznaczenia pierwszego słowa.
2. „Czas podglądu słowa”: od zaznaczenia do zweryfikowanego usunięcia; obecnie 350 ms.
3. „Przerwa między słowami”: od usunięcia do zaznaczenia kolejnego słowa; obecnie 200 ms.
Cykl 2–3 powtarza się do podniesienia palca; przejście do przesuwania zachowuje
przyjęty gest i jego guards. Dokładne zakresy/krok/default pierwszej opcji ustalić
z istniejącym timeoutem, nie zgadywać. Wdrożyć przy następnej zmianie aplikacji:
typed preferences, polskie tytuły/opisy, wyszukiwarka ustawień, backup/import/export
i właściwy reset. Nie zmieniono teraz kodu, zachowania ani istniejących czasów.

Kolejny etap SI to wybór na podstawie porównania, nie natychmiastowa instalacja:
- Kandydaci: istniejący HerBERT MLM, MiniLM NLI oraz mały generatywny Qwen
  (do kwalifikacji Qwen3-0.6B / nowszy Qwen3.5-0.8B w trybie tekstowym).
  Dokumentacja modeli jest przesłanką do eksperymentu, nie wynikiem polskiej klawiatury.
- Wejście: aktualne interpretacje/formy z v5, zachowana pisownia/interpunkcja
  dłuższego kontekstu, rzeczywiste slates i engineScore. Bez ręcznych opisów słów,
  przywiązania do dawnego dziewięciowpisowego próbnego sidecara czy nowych duplikatów CKDT.
- Przed inferencją zamrozić nowe dane i metryki; porównać ten sam model z metadanymi
  i bez, krótsze/dłuższe okno oraz neutralny baseline v5. Kontrolować wpływ długości
  tokenizacji. Baseline może już umieszczać obie formy w top 3: sam taki wynik nie
  dowodzi przewagi SI. Osobno mierzyć top 1, dokładny klucz/zapis w top 3, regresje,
  alternatywy i przypadki, gdy poprawny klucz dekodera nie jest pierwszy.
- Interpunkcja: oddzielna próba znak/brak znaku; przyszła funkcja może korzystać
  z tego samego interfejsu, ale nie zakładamy, że wymaga tych samych wag/modelu.
- Finalny wybór obejmuje kwantyzację/parity, licencję wag/runtime, opóźnienie p50/p95,
  pamięć/start i energię na docelowym telefonie. Geometric pozostaje dekoderem;
  SI ocenia dopuszczalne kandydatury i nie blokuje wpisania słowa ani nie zmienia
  już zatwierdzonego tekstu spóźnionym wynikiem. CTC nie jest warunkiem tego etapu.
- Nie uruchomiono w tej aktualizacji modeli, nowego benchmarku ani integracji Androida.
  Źródła: https://huggingface.co/allegro/herbert-base-cased,
  https://huggingface.co/MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli,
  https://huggingface.co/Qwen/Qwen3-0.6B, https://huggingface.co/Qwen/Qwen3.5-0.8B.
  Historyczne wyniki: PROJECT_MILESTONE_2026-10-02_NATURAL_CONTEXTS.md oraz
  PROJECT_MILESTONE_2026-10-02_SOURCE_METADATA.md; nie są ewaluacją v5.

## 6. Weryfikacja i jej granice
42 testy lokalnie PASS: 21 istniejących wariantów, 8 funkcyjnych, 13 nowych.
Nowe obejmują prawdziwe homonimy, adv/czasowniki, nazwy, brak fałszywych wielkich form,
fragmenty, pełne tagi, audyt każdego klucza, CKDT/rangi, korelację source/runtime,
historyczne dane, determinizm, checksum i limit JSON. Python py_compile PASS.
YAML i powiązanie test/build/summary/artifact PASS, 14 kroków workflow.

Niezależny przegląd całego realnego CKDT potwierdza klucze/kolejność/rangi,
nagłówek/lookup/unigrams i niezmienione dziewięć historycznych wpisów.
Dwa buildy mają identyczne ZIP, report, pełny audyt i summary.
Struktura wszystkich 16199 wpisów odpowiada kontraktowi kluczy/case/manifestu
odczytanemu z runtime; to kontrola hostowa, nie wykonany parser Androida.
Sidecar 11542814 bajtów / 751535 węzłów mieści się w
32 MiB / 1 000 000 / 120 000 wpisów bez podnoszenia limitów.
Po zgłoszeniu „Runy zakończone” odczytano wyniki właściwych commitów:
- Runtime v15 4e51c3b4: CI 37201055281 SUCCESS; 2801 pure JVM + 251 focused = 3052
  testy w logach JUnit, assembleDebug, debug lint, lintVitalRelease, Code Quality,
  gate fixed HIGH/CRITICAL i APK Size Analysis PASS. Brak plików raportu testowego
  przy uploadzie jest ostrzeżeniem; liczbę testów potwierdzają logi, nie pusty artifact.
- Luka wykonania: trzy nowe SuggestionStripScrollTest i trzy nowe metody w
  LearningFunnelBookkeepingTest były zarejestrowane w build.gradle, ale oba zestawy
  pominięto w liście wywołań workflow. Zielony v15 ich nie dowodzi. Naprawiono workflow
  w 6b3b2580094170384e1e0f9a4b72138546ebd884: 18 jawnych guarded wywołań zamiast 16.
  Dokładny readback pliku i commit diff są weryfikowane; nowego runu nie monitorujemy.
- Producer v5 041b28ae: push 37202645255 i PR 37202647650 SUCCESS. Log wybranego push
  potwierdza 21+8+13 = 42 testy, audyt 106363 kluczy/736 korekt/16199 wpisów,
  dokładny SHA ZIP i udane cmp summary z zatwierdzonym plikiem.
Import, parser Androida na realnym v5, pamięć/start, SimpleX i telefon v15
pozostają do potwierdzenia. Test hostowy importu nie zastępuje nowej paczki na telefonie.
Limit monitorowania 60 sekund łącznie na build obowiązuje.

## 7. Gałęzie i historia
Producer trial commit 041b28ae4587c531ef73e62933e9151cadb84c33; runtime ma po v15
workflow-only follow-up 6b3b2580094170384e1e0f9a4b72138546ebd884; draft PR #1 zachowany.
V4 ZIP pozostaje identyczny i zaakceptowany na telefonie pod względem korekty,
ale użytkownik żąda szerszego modelu danych. Poprzedni producer run 37188544526
był wcześniej potwierdzony SUCCESS; nie dowodzi nowego v5.
V14 run 37199887090 odczytano jako completed/SUCCESS dla 95f302c1d528bd9d006e5660697f6a307b983ce2.
V15 zawiera jego poprawkę; jej wynik na telefonie w SimpleX pozostaje nieznany.
Nie kasowano ani nie ponawiano istniejących runów.

## 8. Artefakty, hashe i integracja
Pack version 5, 106363 kluczy, 736 korekt (673 na małą,
63 na wielką literę), 16199 wpisów sidecara. Źródłowych par
16117, w tym 15977 zwykłe/nazwa.
Źródłowe pokrycie 102135; bez zgodnej formy 4228.
455 canonical forms poza obsługiwanym wzorcem case
zachowuje wejściową pisownię; liczba par audytu nie jest gwarancją par dla wszystkich skrótów.

Lokalny cleverkeys-pl-global-casing-trial.zip: 1713402 bajty.
ZIP SHA aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb
CKDT SHA a32f6a55bce7375e744d3d261d6ec9aad96dc64725ac429d4cb1d7225aed3c2a
sidecar SHA 5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d
pełny audyt SHA 06031fee57cc32b6c795cc36f0a728449e7bc7bd841b09bb23d0fb33012c7454
lista zmian SHA 50215963bff5ed9ab0332202309181b26ff7257b51ea51c2e267c6c323c1de3d
Audyt JSONL ma 81566499 bajtów, jest osobnym plikiem artefaktu.
CI v5 wydrukowało identyczny wewnętrzny ZIP SHA; cmp reviewed summary PASS.
[Artifact v5 11303920512](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37202645255/artifacts/11303920512):
cleverkeys-pl-global-casing-trial, 10341499 bajtów, expired=false,
wygaśnięcie 2027-01-02T12:35:39Z. Digest zewnętrznego ZIP artifact:
sha256:66e0480ea158385bb3cdb5bd2e4efda7c3d16ae5b5ae5ec6f114b0f6454ba740.
[APK v15 artifact 11303261365](https://github.com/jakamilek/CleverKeysPL/actions/runs/37201055281/artifacts/11303261365):
apk-debug, 97027740 bajtów, expired=false, wygaśnięcie 2026-10-11T12:17:11Z.
Digest zewnętrznego ZIP artifact:
sha256:ba43c19a3644dc6ccc962a4344b439d5b30b2ba6e8ed5a3352f15cac6ecd644b.
Metadane API i upload log potwierdzają oba ID/digesty. Binarnych artefaktów ponownie
nie pobierano; outer SHA nie jest SHA pojedynczego APK ani inner langpack ZIP.

Workflow wydał artifact cleverkeys-pl-global-casing-trial z wewnętrznym ZIP,
raportem, audytem i summary. Raport v4 zmienił tylko fingerprint resolvera;
jego ZIP SHA 3767c76dbf87589182d6b26b8f8d64d80ec635764cee15d350015b60d41e21af
pozostaje identyczny. CI v5 porównuje summary z zatwierdzonym wynikiem i hashem pełnej listy.
[Specyfikacja v5](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/041b28ae4587c531ef73e62933e9151cadb84c33/docs/GLOBAL_CASING_TRIAL_V1.md).

## 9. Ograniczenia
Źródło Morfeusz 1.99.15 / SGJP 2026.06.01 jest przypięte, nie zastępuje wszystkich baz.
Nierozpoznane i nieprzedstawialne formy nie są zgadywane. Domyślna mała forma jest
polityką użytkową, nie zmierzoną przewagą częstotliwości interpretacji.
Metadane przygotowują przyszły kontekst; obecnie AI ich nie konsumuje.
Większy sidecar wymaga testu importu, startu i płynności na telefonie; zgodność limitów
nie dowodzi kosztu pamięci ani akceptacji UX. Pisownia użytkownika może mieć pierwszeństwo.
Nie kasujemy jego danych. Osiem dawnych par i kontrola łódzki zostają.

## 10. Następny krok
Priorytet po ogólnej akceptacji telefonu: protokół i porównanie SI na rzeczywistych
metadanych v5. Opcje czasów BS pozostają zapisanym backlogiem kolejnej zmiany aplikacji.
Dostarczono linki do zweryfikowanych artifacts v15 APK i v5 langpack.
Po kolejnym zgłoszeniu zakończenia runu sprawdzić 6b3b2580 i wykonanie obu nowych
zestawów; nie oczekiwać na Actions w aktywnej sesji.
Dla producer v5 importować wewnętrzny cleverkeys-pl-global-casing-trial.zip,
nie zewnętrzny wrapper z audytem. Sprawdzić w środku zdania ale/lub/tutaj:
mała forma domyślna i nazwa obok, a następnie Jan, Łódź/łódź, Shift/kropkę,
restart i płynność po większym imporcie. Jeżeli nadal dominuje pisownia użytkownika,
zbadać ją bez automatycznego kasowania słownika.
Dokończyć oczekujące testy SimpleX i resetu paska na runtime v15.

## 11. Różnica względem poprzedniego kamienia
[Poprzedni v15 runtime](PROJECT_MILESTONE_2026-10-04_WORD_STRIP_V15.md)
dotyczył resetu paska i dostarczenia v4. Ten etap zmienia wyłącznie producer:
audyt wszystkich kluczy, ogólną politykę POS oraz automatyczny eksport interpretacji
i wariantów dla konfliktów. Zastępuje ograniczony zakres
[korekty funkcyjnej](PROJECT_MILESTONE_2026-10-04_FUNCTION_WORD_CASING.md)
nowym packiem v5; runtime/API, rangi i klucze pozostają. Lokalnie i CI 42 PASS;
CI runtime v15 3052 PASS. Odczyt ujawnił niewykonywane nowe testy paska; workflow
naprawiono osobnym commitem. Użytkownik zgłasza ogólną akceptację telefonu; pomiary i wynik follow-up CI nadal oczekują.
Zapisano odłożone ustawienia czasów BS i plan porównania SI; bez zmiany aplikacji.
