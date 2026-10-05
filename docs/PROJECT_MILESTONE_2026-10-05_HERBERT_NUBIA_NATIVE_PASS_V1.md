# Kamień milowy: pierwsza zgodność HerBERT FP32 na Nubii
Data: 2026-10-05. Status: import i natywna zgodność PASS na telefonie; pamięć i niezależna jakość wymagają dalszych badań.

## 1. Tożsamość i zakres dowodu
Użytkownik przekazał raport 2026-10-05 18:52:50 Europe/Warsaw: nubia NX721J, Android 15, arm64-v8a; wcześniej podał Z60 Ultra LV 12 GB /512 GB.
Zalecane APK: runtime code 884a29b72e8673ad57e506c3d3d2d174e5cd329f, run 37280833641, artifact 11331993610.
Raport v1 nie zapisuje hash/run; powiązanie z tą instalacją wynika z rozmowy. Importer sprawdza siedem przypiętych tożsamości.
Ten checkpoint zmienia wyłącznie dokumentację na main w obu repozytoriach; nie scala ani promuje kodu próbnego, nie tworzy wydania/tagu i nie zmienia wersji.

## 2. Przyjęta architektura
Geometric jest dekoderem, obie źródłowe formy pozostają dostępne. HerBERT działa na przygotowanych przykładach na osobnym ekranie; nie wpływa jeszcze na podpowiedzi.
Domyślny kontekst 32 słowa, maksimum 64/4096 UTF-16, z zachowaniem case i interpunkcji. Docelowy kontekst pochodzi z bieżącego pola przed kursorem, bez historii między aplikacjami.
Pierwszy zakres live pozostaje kolejnością dwóch form najlepszego klucza, bez dodawania surowego MLM score do geometric i bez zmiany zatwierdzonego tekstu.

## 3. Potwierdzone działanie telefonu
Import po naprawie ZIP i pełny test zakończyły się raportem. 2471 przykładów tokenizacji i 232 batche /532 kandydatów; benchmark przed zwróceniem raportu wymaga identycznych pięciu feeds, zgodności wyników i pełnego rankingu.
Największy wyświetlony błąd 0.000062, poniżej tolerancji 0.001. Wartość jest zaokrąglona do sześciu miejsc.
Natywne ONNX i przenośny tokenizer działają zgodnie z przygotowaną referencją. Nie jest to nowa, niezależna ocena rozumienia zdań czy przewagi jakościowej SI.

## 4. Czas na urządzeniu
Load wraz ze sprawdzeniem SHA: 1256,2 ms; nie jest pełnym czasem startu aplikacji ani udowodnionym cold-start.
180 próbek: 90 dla każdego okna.
32 słowa: token/feed p50/p95 0,5/1,2 ms; inference 81,5/227,8 ms; total 82,2/229,0 ms.
64 słowa: token/feed 0,5/1,6 ms; inference 81,1/325,7 ms; total 81,7/326,9 ms.
Agregat total 82,0/326,6 ms. W tym teście 32 ma p95 niższe o 97,9 ms /około 29,9% względem 64. Pozostawiamy 32 jako domyślne.

## 5. Pamięć i zastrzeżenia pomiaru
Największa próbka PSS całego procesu: 2699,3 MiB /około 2,64 GiB. To istotny koszt wymagający wyjaśnienia przed live SI.
PSS ma odstęp >=250 ms, jest odczytywane pomiędzy wywołaniami i raportowane jako jedno maksimum. Nie ma bazowej wartości ani rozbicia na fazy/okna; nie wyznacza dokładnego szczytu ani pamięci samych wag.
Ten sam scorer/sesja wykonuje najpierw wszystkie testy zgodności, potem warmup i pomiary. Przygotowane feedy zgodności: 49 różnych B/S/T, max B=8/S=21/T=3. Nie przypisujemy pamięci wyłącznie pełnej zgodności.
Dokumentacja ORT opisuje domyślne zatrzymywanie alokacji arena; to możliwa przyczyna, nie diagnoza tego telefonu:
https://onnxruntime.ai/docs/get-started/with-c.html#features
Eksport już wybiera pozycje celu przed głowicą MLM; ta optymalizacja jest wykonana.

## 6. Granice interpretacji czasu i jakości
Trzy konteksty benchmarku mają 7, 8 i 48 słów. Dwa krótkie są identyczne dla obu limitów; trzeci przycina tylko 32. Próba 64 nie wypełnia całego limitu 64 słów.
Agregat po trzech długościach nie jest rozkładem realnego pisania; brakuje czasu per kontekst. Zbliżone mediany nie oznaczają jednakowego kosztu długiego kontekstu.
Jedno zgłoszone wykonanie, bez temperatury, obciążenia tła, stanu cache, energii i throttlingu. PSS po zamknięciu i retencja nie zostały zmierzone.

## 7. Decyzje pozostające w mocy
Nie aktywujemy domyślnie FP32 w podpowiedziach po jednym raporcie. Najpierw pomiar rzeczywistego małego workloadu i pamięci, następnie niezależna jakość.
INT8 nadal FAIL: 22 zmiany rankingu, 7 regresji top-1 i 1 regresja top-3. Nie poluzowano bramek.
Bez zmiany modelu/tokenizera, edytora, Source variants, ustawień i wersji w tym etapie. SI ma być opcjonalna, lokalna, z ograniczonym czasem oczekiwania i fallbackiem.

## 8. Następny etap
Dodać pomiar PSS bazowego po imporcie, po wczytaniu, przy dwóch formach w krótkim/32-słownym kontekście, po pełnej zgodności i po zamknięciu.
Mierzyć intended workload przed szeroką zgodnością w świeżej sesji; zachować osobną obowiązkową bramkę zgodności. Raportować długość/tokeny/B/T i p50/p95 per kontekst oraz hash/run modelu i APK.
Polityki alokacji porównywać jako jawne oddzielne eksperymenty z tą samą tolerancją i rank parity, z pomiarem czasu. Implementacja tego kolejnego etapu nie jest zawarta w obecnych commitach dokumentacyjnych.

## 9. Artefakty i wyniki
Pełny raport użytkownika i analiza:
https://github.com/jakamilek/CleverKeysPL/blob/93f5d1c9b314c4bfc43476b6c66ce640749012d0/docs/eval/2026-10-05-herbert-fp32-nubia-phone-v1.md
APK:
https://github.com/jakamilek/CleverKeysPL/actions/runs/37280833641/artifacts/11331993610
Raw APK SHA-256 z CI: ce65d548cd8b82fa5dd8d71f8b68cbf764ec0a48223a1e880b76ee913223e80b; nie sprawdzano lokalnie ani antywirusowo.
Ten sam model:
https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37230171787/artifacts/11312693984
Model 651798883 bajty, SHA-256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2; rev 50e33e0567be0c0b313832314c586e3df0dc2297, CC BY 4.0.

## 10. Dokumentacja i dalszy backlog
Runtime docs commit 93f5d1c9b314c4bfc43476b6c66ce640749012d0: raw report, spec, todo, index.
Producer docs commit ebbe16b2cea2a924a7fef4feb635b2cf44ebbed3: RESULTS.md z odsyłaczem i ograniczeniami.
Brak nowego CI/exportu w tym etapie; kod/model bez zmian. Limit monitorowania <=60 sekund łącznie/run nadal obowiązuje.
Polskie tłumaczenie pierwsze; 18 innych języków w backlogu. Trzy czasy Backspace, opt-in dispatcher/settings, mniejszy model lub inne optymalizacje i niezależne konteksty pozostają dalszymi etapami.

## 11. Różnica względem poprzedniego kamienia milowego
Wcześniej mieliśmy poprawiony importer i PASS CI/APK, lecz nie natywne wyniki urządzenia. Teraz użytkownik potwierdza import i cały test na Android 15 ARM64 wraz z konkretnymi czasami i PSS.
Ustępuje blokada przeniesienia tokenizacji/obliczeń na Android. Nowym głównym zagadnieniem jest koszt pamięci i dłuższych kontekstów, a nie sama możliwość uruchomienia modelu. Akceptacja produkcyjna i semantyczna jakość pozostają otwarte.
