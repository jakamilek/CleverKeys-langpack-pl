# Kamień milowy: HerBERT FP32 — pamięć i czas etapami v2
Data: 2026-10-05. Status: CI i natywna próba faz v2 PASS; koszt ładowania dominuje pamięć, dalsza diagnoza oczekuje.

## 1. Wersje i zakres
Runtime jakamilek/CleverKeysPL, trial/herbert-fp32-benchmark-v1, code db88fd28cca21ba2aa1e99b38e3886f1f147b5d6, parent 93f5d1c9b314c4bfc43476b6c66ce640749012d0.
https://github.com/jakamilek/CleverKeysPL/actions/runs/37348519387 — completed/success, job 111893158683, zakończony 2026-10-05T17:40:18Z.
Producent/model pozostają zamrożone: d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c, run 37230171787; dokumentacja producenta ebbe16b2cea2a924a7fef4feb635b2cf44ebbed3.
Raport i protokół następnej próby zapisano na branch trial w dokumentacyjnym commicie 1493bd64de2ef798113191d8577c0024149e28c9.
Ten identyczny checkpoint na obu main jest wyłącznie dokumentacją. Bez scalenia kodu, wersji, tagu i wydania.

## 2. Dowód, który zachowujemy
Pierwszy raport nubia NX721J /Android 15 /arm64-v8a potwierdził import i natywne 2471 wektorów/232 batche, max wyświetlony błąd 0.000062 (<0.001), rank parity.
Całość p50/p95: 32=82,2/229,0 ms, 64=81,7/326,9 ms. Load 1256,2 ms, największa próbka PSS procesu 2699,3 MiB.
Ten wynik v1 pozostaje w docs/eval/2026-10-05-herbert-fp32-nubia-phone-v1.md.
Nowy pełny raport: docs/eval/2026-10-05-herbert-fp32-nubia-phase-v2.md. Otrzymano 2026-10-05 19:49:10 Europe/Warsaw; numer 1, PID 10016. Commit/APK/model SHA zgadzają się z CI. Native conformance PASS, max błąd 0,000062. Nie zastępuje niezależnej oceny jakości.

## 3. Cel i kolejność nowej próby
Świeża sesja przy każdym kliknięciu: bazowe PSS po imporcie → load/SHA → pierwsza krótka analiza dwóch form → rozgrzewki/pomiary krótkich, potem długiego kontekstu → obowiązkowa pełna zgodność → zamknięcie → natychmiastowy odczyt PSS.
Udany raport jest zwracany dopiero po przejściu wszystkich dotychczasowych token/feed/score/rank gates i zamknięciu.
To eliminuje wpływ wcześniejszych batchy zgodności na początkowy pomiar intended workload, bez osłabienia bramek. Proces może zachowywać wcześniejsze alokacje z poprzednich uruchomień.

## 4. Pamięć etapami
HerbertMemoryProbe zapisuje baseline/load/first, sześć rozgrzewek i sześć faz timed per kontekst/limit, zgodność oraz close — 17 identyfikatorów etapów po pełnym przebiegu.
Raport: pierwsza/ostatnia/największa próbka, liczba odczytów, różnica max od bazowego PSS całego procesu.
Granice i pierwszy odczyt fazy są wymuszone; powtórzenia danej fazy podlegają globalnemu odstępowi >=250 ms. Wszystko poza timerem inferencji i pomiędzy wywołaniami.
Nie jest to exact peak, model-only memory ani izolowany koszt każdego okna; ciepła sesja zachowuje wcześniejsze rozgrzewki i przypadki. Bazowy punkt obejmuje tokenizer po imporcie.
Telefon v2: baseline 346,2 MiB → loaded 2121,0 (+1774,9 wg raportu) → first 2121,7 → workload max 2132,1 (+1785,9) → zgodność ostatnia 2086,8 → close 1336,8 (+990,7).
Wzrost workload względem load około 11,1 MiB; główny koszt już przed inferencją. Natychmiastowy spadek po close 750,0 MiB względem ostatniej próbki zgodności. Nie dowodzi leak ani udziału map/native/GC. Spadek już na początku zgodności do 1995,1 wskazuje zmienność. Niższy max niż v1 nie jest kontrolowanym dowodem optymalizacji.

## 5. Czas i geometria wejścia
Pierwsza krótka analiza ma osobny czas przed rozgrzewką. Sześć zestawów (konteksty 7/8/48 słów, limity 32/64) ma po 30 próbek, liczby zachowanych słów i B/S/T oraz token/feed, inference, total p50/p95.
Okna agregują po 90, ogółem 180; trzy warmupy per zestaw i naprzemienny limit pierwszy w 30 rundach. Pierwszy warmup long-32 jest przed long-64; późniejsze timed samples mogą już korzystać z pamięci obu rozgrzewek.
Dodatkowo całkowity czas testu obejmuje load, przygotowanie, warmupy, pełną zgodność i odczyty PSS. 431 wywołań score: 1 pierwsze +18 warmup +180 timed +232 referencje.
Telefon v2 total p50/p95: krótkie 7 słów 66,5/69,4 ms (limit32), 66,7/69,0 (limit64); 8 słów 82,4/84,2 i 82,8/84,2; długi 32 słowa 228,0/229,7 versus 48 słów pod limitem64 327,5/329,2. P95 długiego krótszy około30,2%, bez oceny jakości skrócenia. Load+hash1544,7 ms, pierwsza para70,8 ms, cały test52528,5 ms; nie jest to czas jednej podpowiedzi.

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
Nie ma lokalnego Kotlin/Android SDK. Log job 111893158683 potwierdza compile PASS, JUnitCore OK (2851 tests), obowiązkowy marker 2471-token/232-batch/532-candidate/five inputs PASS, 83 testy edytora (45+16+8+11+3), debug/vital lint, assembly i audyt ARM64 APK PASS. Dziewięć nowych testów jest w zarejestrowanym zestawie. Telefon v2 natywnie przeszedł wszystkie obowiązkowe gates. Jeden raport z dopasowanymi SHA jest zachowany; niezależna jakość, energia i izolacja kosztów pamięci nadal niezweryfikowane.

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
CI i pierwsza próba telefonu v2 PASS; nie trzeba powtarzać dotychczasowej próby teraz. Następny zaplanowany eksperyment: osobne procesy dla obecnego mapped buffer i ładowania z prywatnej ścieżki pliku; SHA strumieniowo małym buforem, te same bajty/options/threads i wszystkie token/feed/score/rank gates.
Odczyty przed hash, po hash, po session creation, pair i close; Java/native/file PSS i czasy, powtórzenia, bez wymuszania GC. Nie łączyć eksperymentu z arena/model zmianą. Nie wdrożono go jeszcze ani nie obiecujemy oszczędności. Jeśli koszt pozostaje, porównać mniejszy model na niezależnych polskich kontekstach; INT8 nadal FAIL. Najbardziej użyteczna pierwsza próba po aktualizacji; raport ujawnia jej numer i PID.
Instrukcja docs/HERBERT_FP32_PHASE_TRIAL_V2.md. Raport z fazami i sześcioma czasami już przekazany i zarchiwizowany. Osobno rozważamy allocator experiments, lżejszy model i niezależne konteksty; polskie „1 próbek” odłożono do najbliższej zmiany UI.
Nie czekamy na CI w pętli. Maksymalnie 60 sekund łącznie monitorowania/build, potem zakończenie zgłasza użytkownik.
Ustawienia trzech czasów Backspace, dispatcher opt-in i jakość są dalszymi etapami.

## 11. Różnica względem poprzedniego checkpointu
Po natywnym PASS v1 mieliśmy duży PSS bez bazowego punktu/faz oraz agregat czasu. Teraz implementacja daje pomiar intended workload przed szerszą zgodnością, szczegółowe fazy i konteksty, cleanup oraz tożsamość raportu.
Kod i CI oraz nowy natywny raport v2 przeszły. Koszt około1,77 GiB ponad baseline występuje już po load; analiza wskazuje etap, ale nie rozdziela mapowania/parsowania/optymalizacji/alokatora. Skrócenie kontekstu nie usuwa tego stałego kosztu. Potrzebny kontrolowany eksperyment ładowania i niezależna jakość. Nie twierdzimy jeszcze, że pamięć spadła ani że model jest gotowy do produkcji.
