# HerBERT mobile v1 — zgodny FP32, regresje INT8

2026-10-04. Run 37227484110 SUCCESS na zamrożonym f4f994d3fd890402d6f4106ae4f75f4ebab76838.
SUCCESS oznacza poprawne wykonanie próby: bramka FP32 PASS, bramka zachowania jakości INT8 FAIL.
Nie utworzono ani nie opublikowano paczki modelu do telefonu. Android przygotowany w osobnym PR #2;
jego CI 37227497872 przy ostatnim odczycie trwało. Żaden model nie jest włączony w klawiaturze.

## Co rzeczywiście sprawdzono

Rzeczywista inferencja 232 plain wejść z obu okien, 532 ocen kandydatów. Ten sam przypięty HerBERT
i źródła. Batch niezależnych wierszy: whole-word masking, BERT, projekcja MLM wybranych pozycji,
log-softmax całego słownika i średnia/suma. ONNX 1.17.0, ORT 1.21.1, opset 17, CPU dwa wątki.
INT8 dynamiczny per-channel dla stałych MatMul/Gemm, zgodnie z protokołem sprzed wyników.

ZIP artefaktu 11313090360 sprawdzono SHA256 względem GitHub, bezpiecznie rozpakowano. Wszystkie trzy
porównania (batched Torch, ONNX FP32, ONNX INT8) ponownie obliczono lokalnie z surowych scores.json:
są identyczne z pełnymi obiektami raportu CI. Zweryfikowano commit/freeze/model/payload/kompletność.
Nie zmieniano kryteriów, danych ani parametrów po wynikach; nie powtarzano inferencji.

## Zgodność i jakość konwersji

| Wariant | Maks. różnica oceny względem archiwum | Zmienione pełne rankingi | Bramka |
|---|---:|---:|---|
| Torch eager z batchem | 0,0000882 | 0/232 | PASS |
| ONNX FP32 | 0,0001030 | 0/232 | PASS |
| ONNX INT8 | 5,6111660 | 22/232 | FAIL |

Wymóg FP32: błąd <=0,001 i brak zmian pełnego rankingu. INT8: brak regresji oznaczonego top 1
i top 3 w każdej populacji/oknie/suite; naprawy nie kompensują regresji.

Poprawna forma na pierwszym miejscu przy długim kontekście:

| Populacja | Archiwum / FP32 | INT8 |
|---|---:|---:|
| Nowe 32 konteksty | 25/32 | 24/32 |
| Powtórzone 64 konteksty | 50/64 | 47/64 |
| Historyczne osiem rankingów | 7/8 | 7/8 |

W obu oknach łącznie INT8 daje 7 regresji top 1, trzy naprawy i jedną regresję top 3.
Ta ostatnia dotyczy krótkiego replay-6: poprawny Karsin przesuwa się z drugiej na czwartą pozycję.
Na nowych długich kontekstach Wilk spada za wilk. Na powtórzonych długich kontekstach regresje
dotyczą Jagoda, Lub, Kruk i Zając; Lis jest naprawą. Nie wprowadzamy wyjątków dla tych słów.

Top 3 nowych form nadal 32/32 ze względu na dwie formy jednego klucza, także bez SI. Nie traktujemy
tego jako samodzielnego dowodu jakości. Populacje diagnostyczne używają znanych kluczy, brak nowego
niezależnego korpusu i kalibracji z geometrią. Ta próba sprawdza konwersję, nie generalizację.

## Rozmiar i pomiar hosta

| Model | Rozmiar | Host p50 / p95 na całym zestawie |
|---|---:|---:|
| ONNX FP32 | 621,6 MiB | 24,8 / 44,3 ms |
| ONNX INT8 | 267,9 MiB | 13,7 / 23,6 ms |

Torch batched: 46,0 / 69,9 ms. Czas obejmuje run grafu, bez przygotowania feedu/tokenizacji.
Sekwencyjne pomiary na jednym hoście; nie są idealnym izolowanym porównaniem ani pomiarem telefonu.
Szczyt RSS 3171 MiB dotyczy procesu z Torch i obiema sesjami, nie samego INT8.
Nubia Z60 Ultra LV 12/512 GB nadal nie była mierzona; nie znamy startu/RAM/energii/płynności.

## Przygotowanie Androida

Runtime b1c829cf28886391cdc98a7b8d7b0bd16bf6b65e przygotowuje rzeczywisty ONNX scorer,
defensywne WWM feeds, kontekst 64 słów/4096 jednostek UTF-16 i politykę kolejności jednej pary.
17 testów JVM jest zarejestrowanych. Kod nie jest podłączony do IME. Brak tokenizera/importu,
modelu w APK, aktywnych ustawień, dispatcherów lub pomiaru telefonu. Nie przedstawiać go jako
ukończonego wdrożenia. Pełny spec: docs/specs/polish-context-ai.md w CleverKeysPL PR #2.

## Decyzja i następny krok

Zachować FP32 jako zgodny punkt odniesienia do kolejnego jawnego etapu przygotowania paczki
benchmarkowej i pomiaru telefonu. Obecnego INT8 nie promować pod pozorem PASS całego workflow.
Mniejsza reprezentacja modelu wymaga nowej jawnej próby i niezależnej kontroli jakości;
nie stroić parametrów na tych samych pomyłkach ani nie zmieniać tego freeze.

Najpierw dokładna tokenizacja zgodna z wyeksportowanymi conformance vectors, bezpieczny import
i pomiar shadow na telefonie. Potem niezależne konteksty i opt-in kolejność wariantów najlepszego
klucza geometric. Nie mieszać nieskalibrowanych ocen SI z punktami geometrii. Obie formy pozostają.

## Trwałe dowody

conversion-report.json, scores.json, android-score-vectors.json, tokenizer-conformance.json,
SUMMARY.md i artifact-manifest.json zachowane obok raportu. Wagi pozostały tymczasowe w CI.
Model FP32 SHA256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2;
INT8 295bce14c649bdd1549f710f19d8b59d13e3cbcec6275c80de2bf6cb6909025b.
Bez merge/release/tag/version bump, nowego APK i zmian zaakceptowanej obsługi klawiatury.
