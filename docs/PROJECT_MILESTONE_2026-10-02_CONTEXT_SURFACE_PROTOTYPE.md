# Kamień milowy — prototyp dłuższego kontekstu i wariantów powierzchni

**Data:** 2026-10-02, Europe/Warsaw.
**Repo kanoniczne:** jakamilek/CleverKeys-langpack-pl.
**Cross-repo:** [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-02_CONTEXT_SURFACE_PROTOTYPE.md).
**Status:** działający eksperyment offline; bez integracji runtime i bez inferencji modelu.

## 1. Zweryfikowany baseline GitHub

| Repo | Branch | HEAD przed zapisaniem tego milestone’u |
|---|---|---|
| jakamilek/CleverKeys-langpack-pl | main | 0832bf6f1353b0a2bc3042dbdd26f330ddc53e33 |
| jakamilek/CleverKeysPL | main | 56e7e90d3a669f2eb28e65257ce6851aa7b5d925 |

HEAD-y sprawdzono na początku i przed zapisem tego etapu. Zapis dokumentów przesuwa main o dokumentacyjny commit; nie promuje eksperymentu.

Eksperyment:
- branch: experiment/context-surface-window-v1;
- base: 0832bf6f1353b0a2bc3042dbdd26f330ddc53e33;
- commit: 2733671896b6d9a13af9907217011fdc20f0066e;
- tree: 904a8eba6243a4504a4cec873c97469e4cb841c6;
- [Draft PR #4](https://github.com/jakamilek/CleverKeys-langpack-pl/pull/4).

## 2. Doprecyzowanie zaakceptowane przez użytkownika

Użytkownik potwierdził kierunek wariantów powierzchni i uznał dwa poprzednie słowa zapisane małymi literami za zdecydowanie zbyt krótki kontekst. Zlecił dalszą pracę.

Przyjęto do eksperymentu dłuższy tekst przed kursorem z zachowaniem case, interpunkcji i nowych linii. Domyślnie 64 słowa Unicode oraz 4096 znaków, oba limity konfigurowalne. **Użytkownik zatwierdził potrzebę dłuższego kontekstu, nie konkretne optimum 64/4096.** To punkt startowy pomiarów, nie zmiana ustawień klawiatury.

## 3. Co zaimplementowano

W experiments/context_surface_v1:
- prototype.py — kontekst jako dokładny ograniczony suffix, walidacja używanego podzbioru sidecara v1, grupowanie bazowych kandydatów i projekcja dopuszczalnych wariantów;
- deterministyczny request/response JSON do późniejszego podłączenia modelu, z hashem żądania i identyfikacją źródła;
- porównanie dwóch słów z dłuższym oknem na tych samych przykładach, bez gold labels w żądaniu modelu;
- wybór wariantu według zewnętrznego score wewnątrz jednego klucza; bez zmiany lexical rank i engineScore;
- dostępna alternatywa łódź/Łódź oraz pozostałe kandydatury;
- jawne rozdzielenie caseMode none/sentence_start/shift/caps_lock i deduplikacja dokładnie wyświetlanej powierzchni;
- neutralny evaluator mierzący osobno poprawny klucz, poprawny zapis i osiągalność;
- 30 testów regresyjnych;
- 14 skonstruowanych przykładów oraz fixture podzbioru sidecara v1;
- README.md i RESULTS.md z instrukcjami, ograniczeniami i reprodukcją;
- workflow Context surface prototype.

[Kod i instrukcje na przypiętym SHA](https://github.com/jakamilek/CleverKeys-langpack-pl/tree/2733671896b6d9a13af9907217011fdc20f0066e/experiments/context_surface_v1).

Przykłady case001/case002 mają identyczne ostatnie dwa słowa, lecz różny wcześniejszy tekst o mieście i jednostce pływającej. Test potwierdza zachowanie tej informacji w dłuższym oknie. Nie potwierdza rozumienia jej przez AI.

## 4. Walidacja i wynik

Lokalnie Python 3.12.14, standard library:
- 30/30 unittest PASS;
- komendy prepare/evaluate PASS;
- ponowne uruchomienie: identyczne bajty i SHA256.

Pełny push run dla commitu 2733671896b6d9a13af9907217011fdc20f0066e:
[Context surface prototype / 37044611353](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37044611353) — completed, success.

To green konkretnego eksperymentu, nie całego Android runtime. Nowy push milestone’u jest dokumentacyjny; jego CI należy odczytać oddzielnie.

Neutralny baseline na ręcznie skonstruowanych przykładach:

| Miara | 2 słowa | Dłuższe okno |
|---|---:|---:|
| Poprawny klucz dostępny | 13/14 | 13/14 |
| Poprawny klucz top-1 | 13/14 | 13/14 |
| Poprawna powierzchnia top-1 | 10/14 | 10/14 |
| Oczekiwana powierzchnia dostępna | 13/14 | 13/14 |

Brak różnicy jest oczekiwany: baseline używa defaultSurface i **nie interpretuje kontekstu**. Wyniki kontrolowane testów mają kind=controlled_test; nie wolno cytować ich jako jakości AI. Case012 bez właściwego klucza w slate pokazuje ograniczenie samego resolvera.

Hash UTF-8 requests.json: f89fab6cb1469f8b847003d22aca7dbff22dc43a0cbb451e7c534a9d98611ceb.
Hash UTF-8 neutral-baseline.json: 8e4af8bf1ae64649b3817f45f97666d22b1e8d4892b77459bd16d47cdf15af69.
Request payload hash: e6db915401dbff00f0185d938a7bc095d261dc182c4ec44c804eb0b0a8abcda4.
Artefakty generuje CLI; szczegóły w RESULTS.md.

## 5. Architektura i zakres

Nadal oddzielne repozytoria, immutable 100k, CKDT V2 i legacy fallback. Runtime pozostaje wspólnym wykonawcą i rankerem, pakiet dostarcza wiedzę/model. Prototyp jest narzędziem eksperymentu offline, nie drugim produkcyjnym polskim rerankerem.

Nie zmieniono:
- API v1 na main;
- generatora preview i membership 100k;
- dictionary.bin, manifestu instalowanego ZIP-a ani produkcyjnych artefaktów;
- kodu Android, obecnego dwutokenowego trackera czy scoringu;
- obsługi CTC ł.

Fixture sidecara jest przykładowym wejściem testów, nie wygenerowanym wynikiem zweryfikowanego audytu 100k.

## 6. Odrzucone skróty

- Zwiększenie tylko liczby tokenów w istniejącym lowercase trackerze: nie zachowuje case i pełnego tekstu.
- Przedstawianie metadanych lub neutralnego baseline’u jako AI.
- Dopisywanie dwóch casingów do CKDT.
- Wymyślanie keyword heurystyk dla miasta/łodzi jako substytutu gotowego modelu.
- Używanie surowych logitów między kluczami jako skalibrowanej pewności zmiany rank 1.
- Przeniesienie eksperymentu do main lub runtime bez osobnego etapu.

## 7. Niewdrożone i niezweryfikowane

Nie ma inferencji HerBERT/plT5 ani innego modelu; środowisko tego etapu nie zawiera transformers/torch/onnxruntime ani wag. Nie pobierano modeli. Rzeczywisty adapter, przegląd rewizji i rozmiaru, wyniki jakości AI oraz koszt telefonu pozostają do wykonania.

Nie wdrożono odczytu InputConnection, obsługi aktualności snapshotu kursora, tap-to-replace/commit ani uczenia casing-u. Hash żądania chroni spójność offline; nie jest pełnym mechanizmem ochrony przed wyścigami edytora.

Ograniczenia:
- boundary_cues zachowują znaki interpunkcji, nie są poprawnym segmenterem zdań ze skrótami;
- słowa Unicode != subword tokens konkretnego modelu;
- zestaw 14 przykładów nie jest reprezentatywną ewaluacją;
- modele liczą tylko ocenę wariantu w tym etapie; lexical reranking pozostaje istniejącą odpowiedzialnością runtime;
- CTC ł i eligibility rzeczywistego polskiego ZIP nadal wymagają osobnego testu;
- wcześniejszy FAIL S3 statycznego angielskiego LM pozostaje dowodem przeciw obietnicy bezwarunkowego wpięcia tego modelu do swipe.

## 8. Historyczne branche i istniejące luki

Branche dokumentacyjne docs/architecture-runtime-langpack-separation-2026-10-02 i docs/architecture-langpack-plugin-model-2026-10-02 zachowują rolę opisaną w STATE_RECONSTRUCTION; bez ponownego audytu lub merge. Niespójność referencji do dwóch ADR pozostaje otwarta. Brak pl.cklm i produkcyjnego provider/parser v1 pozostaje otwarty.

## 9. Delta od poprzedniego milestone’u

Od PROJECT_MILESTONE_2026-10-02_CONTEXT_AND_SURFACE_AUDIT:
- dodano wymaganie użytkownika dotyczące dłuższego kontekstu;
- zrealizowano izolowany wykonywalny prototyp i neutralny baseline;
- sprawdzono 30 testów lokalnie i green push workflow;
- utworzono branch i Draft PR;
- kod produkcyjny i artefakty pozostają w stanie audytu.

## 10. Następny uzasadniony krok

Podłączyć rzeczywisty adapter gotowego modelu cased do przygotowanych żądań, z przypiętą rewizją wag i kodu adaptera. Mierzyć osobno efekt długości kontekstu, casing i dostępność alternatywy; nie ujawniać modelowi gold labels ani tekstu po kursorem. Obsłużyć słowa wielotokenowe.

Jeśli wynik daje uzasadnioną poprawę, rozszerzyć zestaw o rzeczywiste slates i oddzielną próbę walidacyjną; dopiero potem koszty Androida, projekt integracji wspólnego runtime, aktualność snapshotu, commit i testy na urządzeniu. Równolegle zachować CTC ł jako warunek osiągalności przykładu.

Eksperyment nie został scalony. Nie traktować go jako działającej funkcji telefonu ani gotowego langpacku.
