# Kamień milowy: HerBERT FP32 — pamięć i czas etapami v2
Data: 2026-10-05. Status: CI PASS i diagnostyczny APK dostępny; nowe wyniki telefonu oczekują.

## 1. Wersje i zakres
Runtime jakamilek/CleverKeysPL, trial/herbert-fp32-benchmark-v1, code db88fd28cca21ba2aa1e99b38e3886f1f147b5d6, parent 93f5d1c9b314c4bfc43476b6c66ce640749012d0.
https://github.com/jakamilek/CleverKeysPL/actions/runs/37348519387 — completed/success, job 111893158683, zakończony 2026-10-05T17:40:18Z.
Producent/model pozostają zamrożone: d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c, run 37230171787; dokumentacja producenta ebbe16b2cea2a924a7fef4feb635b2cf44ebbed3.
Ten identyczny checkpoint na obu main jest wyłącznie dokumentacją. Bez scalenia kodu, wersji, tagu i wydania.

## 2. Dowód, który zachowujemy
Pierwszy raport nubia NX721J /Android 15 /arm64-v8a potwierdził import i natywne 2471 wektorów/232 batche, max wyświetlony błąd 0.000062 (<0.001), rank parity.
Całość p50/p95: 32=82,2/229,0 ms, 64=81,7/326,9 ms. Load 1256,2 ms, największa próbka PSS procesu 2699,3 MiB.
Ten wynik v1 pozostaje w docs/eval/2026-10-05-herbert-fp32-nubia-phone-v1.md. Nie zastępujemy go nowym niezmierzonym wynikiem ani niezależną oceną jakości.

## 3. Cel i kolejność nowej próby
Świeża sesja przy każdym kliknięciu: bazowe PSS po imporcie → load/SHA → pierwsza krótka analiza dwóch form → rozgrzewki/pomiary krótkich, potem długiego kontekstu → obowiązkowa pełna zgodność → zamknięcie → natychmiastowy odczyt PSS.
Udany raport jest zwracany dopiero po przejściu wszystkich dotychczasowych token/feed/score/rank gates i zamknięciu.
To eliminuje wpływ wcześniejszych batchy zgodności na początkowy pomiar intended workload, bez osłabienia bramek. Proces może zachowywać wcześniejsze alokacje z poprzednich uruchomień.

## 4. Pamięć etapami
HerbertMemoryProbe zapisuje baseline/load/first, sześć rozgrzewek i sześć faz timed per kontekst/limit, zgodność oraz close — 17 identyfikatorów etapów po pełnym przebiegu.
Raport: pierwsza/ostatnia/największa próbka, liczba odczytów, różnica max od bazowego PSS całego procesu.
Granice i pierwszy odczyt fazy są wymuszone; powtórzenia danej fazy podlegają globalnemu odstępowi >=250 ms. Wszystko poza timerem inferencji i pomiędzy wywołaniami.
Nie jest to exact peak, model-only memory ani izolowany koszt każdego okna; ciepła sesja zachowuje wcześniejsze rozgrzewki i przypadki. Bazowy punkt obejmuje tokenizer po imporcie.

## 5. Czas i geometria wejścia
Pierwsza krótka analiza ma osobny czas przed rozgrzewką. Sześć zestawów (konteksty 7/8/48 słów, limity 32/64) ma po 30 próbek, liczby zachowanych słów i B/S/T oraz token/feed, inference, total p50/p95.
Okna agregują po 90, ogółem 180; trzy warmupy per zestaw i naprzemienny limit pierwszy w 30 rundach. Pierwszy warmup long-32 jest przed long-64; późniejsze timed samples mogą już korzystać z pamięci obu rozgrzewek.
Dodatkowo całkowity czas testu obejmuje load, przygotowanie, warmupy, pełną zgodność i odczyty PSS. 431 wywołań score: 1 pierwsze +18 warmup +180 timed +232 referencje.

## 6. Zasoby i anulowanie
HerbertBenchmarkLifecycle zawsze zamyka sesję po jej otwarciu, również przy błędzie obowiązkowej zgodności, anulowaniu pracy lub obserwacji load. Odczyt closed jest po native close; failed open nie ma sesji do zamknięcia.
HerbertOnnxScorer po udanym close zwalnia własne silne odwołanie do mapped buffer. Nie usuwa go podczas używania sesji; nie wymusza unmap ani GC. System/alokator może dalej zachowywać strony pamięci.
Worker pozostaje pojedynczym właścicielem import/inference/close/delete. Model i jego pliki usuwa istniejący lifecycle ekranu; bez zmian backup/network/editor context.

## 7. Raport i polski ekran
Nagłówek „pomiar etapów v2”, postęp etapu i liczba próbek/batchy. Kopiuj raport jest aktywne dopiero z raportem.
Anulowanie lub błąd daje raport częściowy z dotychczasowym PSS, wyraźnie bez potwierdzonej zgodności tej próby.
Identyfikatory: zweryfikowany GITHUB_SHA w BuildConfig (40 hex lub local-unidentified), SHA zainstalowanego bazowego APK i przypięty SHA modelu, PID/numer próby, ORT 1.21.1 CPU 2/1.
Nie zapisujemy surowego wyjątku, ścieżki, URI, wybranego filename ani tekstu z aplikacji. Tylko przygotowane przypadki. Base/Polish 47 kluczy, w tym 20 nowych; pozostałe 18 locale odłożone w backlogu.

## 8. Weryfikacja
Dziewięć nowych zarejestrowanych testów: kolejność workload→verify→close, odmowa PASS przy błędzie zgodności, cancel/failed load/close observation, PSS throttle i wymuszone punkty, snapshot/delta/max, kwantyle i granice słów Unicode.
Lokalnie 47 zasobów i zgodność formatów/referencji PASS; build.gradle ma wyłącznie provenance oraz rejestrację testu, scorer wyłącznie zmianę retencji po close. Dziewięć źródłowych blob SHA sprawdzono po uploadzie.
Nie ma lokalnego Kotlin/Android SDK. Log job 111893158683 potwierdza compile PASS, JUnitCore OK (2851 tests), obowiązkowy marker 2471-token/232-batch/532-candidate/five inputs PASS, 83 testy edytora (45+16+8+11+3), debug/vital lint, assembly i audyt ARM64 APK PASS. Dziewięć nowych testów jest w zarejestrowanym zestawie. Nowe natywne wyniki/PSS telefonu nadal oczekują; host conformance nie zastępuje ich.

## 9. Niezmienione decyzje i artefakty
Geometric, podpowiedzi oraz live SI pozostają bez zmian/wyłączone. Kontekst domyślny 32, max 64/4096 UTF16.
Model ZIP ten sam:
https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37230171787/artifacts/11312693984
model.onnx 651798883 bajty; SHA f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2, CC BY 4.0.
Nie zmieniono grafu, wag, tokenizerów, CPU threads, optymalizacji ani arena. INT8 pozostaje FAIL; nie rozluźniamy tolerancji/rank gates. Audyt CI potwierdził brak FP32 i test fixtures w APK.
Nowy APK phase-v2: https://github.com/jakamilek/CleverKeysPL/actions/runs/37348519387/artifacts/11361288863
CleverKeys-v2.0.0-arm64-v8a.apk: 35742138 bajtów; SHA256 c3d15aaf1ba26b8f2534199dda5a6b8835cb72e5233038f4e6f1292b57ed3dd9.
ZIP 35743280 bajtów, SHA256 05883670b94c815be141f98c993eed7f337dc4407daeb66b419693bd8305ed70, ważny do 2026-10-19T17:40:07Z.
Raporty CI artifact 11362182090: 22355 bajtów; SHA256 e9006a2add28f93d9bd0a7b67dfba23ec89976dd9e773c860669e663334847f7.
Tożsamość APK pochodzi z logu CI, ZIP z metadanych GitHub; APK nie pobierano/skanowano lokalnie.

## 10. Następny krok
CI PASS; dostarczamy APK z benchmarkRevision phase-v2. Rozpakować ZIP z APK, zainstalować aktualizację i wykonać pierwszą próbę z istniejącym ZIP modelu. Najbardziej użyteczna pierwsza próba po aktualizacji; raport ujawnia jej numer i PID.
Instrukcja docs/HERBERT_FP32_PHASE_TRIAL_V2.md. Użytkownik przekazuje cały raport z fazami i sześcioma czasami; osobno rozważamy allocator experiments, lżejszy model i niezależne konteksty.
Nie czekamy na CI w pętli. Maksymalnie 60 sekund łącznie monitorowania/build, potem zakończenie zgłasza użytkownik.
Ustawienia trzech czasów Backspace, dispatcher opt-in i jakość są dalszymi etapami.

## 11. Różnica względem poprzedniego checkpointu
Po natywnym PASS v1 mieliśmy duży PSS bez bazowego punktu/faz oraz agregat czasu. Teraz implementacja daje pomiar intended workload przed szerszą zgodnością, szczegółowe fazy i konteksty, cleanup oraz tożsamość raportu.
Kod i wymagane bramki CI przeszły, diagnostyczny APK jest dostępny, a przyczyna 2,64 GiB i koszt normalnego użycia wymagają nowego raportu telefonu. Nie twierdzimy jeszcze, że pamięć spadła ani że model jest gotowy do produkcji.
