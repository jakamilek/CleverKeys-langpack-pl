# Kamień milowy: FP32 — APK gotowy do testu na telefonie
Data: 2026-10-04. Status: CI PASS; test natywny na telefonie pozostaje do wykonania.

## 1. Repozytoria i zweryfikowane wersje
Producent: jakamilek/CleverKeys-langpack-pl; źródło zamrożonego modelu d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c, run 37230171787.
Runtime: jakamilek/CleverKeysPL; przetestowany kod 73627fae758bcdf845ed8696be821b7052e326ff, run 37232458354.
Dokumentacja wyników: producent c02f43379da7a4f5e23ec2f6480e6bb24e617e9a; runtime 6e87483a55d2d3be1bf4c5430e25d503b872296d.
Ten checkpoint na obu main jest zmianą wyłącznie dokumentacji. Nie promuje kodu próbnego, nie scala PR, nie zmienia wersji ani nie tworzy wydania.

## 2. Architektura i kontekst
Geometric pozostaje aktywnym dekoderem. SI w codziennym wpisywaniu pozostaje wyłączona; ekran diagnostyczny jest osobny.
HerbertContextWindow ma domyślny limit 32 słów, maksymalnie 64 i ograniczenie 4096 jednostek UTF-16. Zachowuje interpunkcję i kapitalizację. Docelowo kontekst pochodzi z bieżącego pola przed kursorem, a nie z historii pisania między aplikacjami. Obecny benchmark korzysta wyłącznie z przygotowanych przykładów i nie czyta tekstu użytkownika.
Istniejący tracker dwóch słów dla n-gramów pozostaje niezależny.

## 3. Zakres gotowej próby
Ekran „Test polskiej SI” w placu testowym gestów importuje osobny ZIP FP32, sprawdza przypięte rozmiary i SHA-256 plików, uruchamia test zgodności i pomiary, pozwala skopiować raport, zatrzymać próbę oraz usunąć model.
Model jest przechowywany prywatnie, mapowany tylko do odczytu i nie jest dołączony do APK. Zamykanie ekranu usuwa import; kolejne pomiary należy wykonać przed wyjściem z ekranu.
Brak podbicia wersji aplikacji: plik nadal nazywa się CleverKeys-v2.0.0-arm64-v8a.apk.

## 4. Decyzje i odrzucone ścieżki
Nie aktywujemy SI na żywo przed pomiarami na urządzeniu. Próba INT8 nadal ma wynik FAIL: 22 zmiany rankingu, 7 regresji top-1, 3 naprawy i 1 regresję top-3. Kryteria nie zostały poluzowane.
Pierwszy przyszły zakres SI: ranking dwóch udokumentowanych form kapitalizacji najlepszego kandydata geometric, z zachowaniem obu propozycji. Kalibracja między różnymi słowami jest odłożona.

## 5. Prace pozostające
Pomiar natywnego ONNX na Nubia Z60 Ultra LV 12 GB / 512 GB; wersja Androida i ABI mają zostać potwierdzone raportem.
Ocena jakości na niezależnych polskich kontekstach, decyzja o modelu i ewentualnej optymalizacji, bezpieczne opcje włączenia SI i obsługi modelu.
Ustawienia trzech czasów przytrzymania Backspace pozostają na liście dalszych zmian. Polski ma pierwszeństwo; brakujące tłumaczenia pozostałych 18 języków zapisano w osobnym backlogu.

## 6. Zweryfikowany wynik CI
Runtime run 37232458354 zakończył się sukcesem: kompilacja Kotlin, JUnitCore OK (2835 tests), obowiązkowa zgodność oryginalnego tokenizera — 2471 wektorów i 232 batchy / 532 kandydatów / wszystkie pięć wejść — oraz 83 ukierunkowane testy edytora i sugestii.
Debug lint, release vital lint, assembleDebug, audyt zawartości APK i upload artefaktów zakończyły się sukcesem. Nie oznacza to, że wszystkie istniejące opcjonalne testy projektu wykonują swoje ciała; zgodność rzeczywistego tokenizera w tej próbie jest obowiązkowa.
Producent FP32: bez zmian rankingu względem zapisanej referencji, maksymalna tolerancja bezwzględna 0.001. Sprawdzono również 4352 bloki Unicode w referencji przenośnej.

## 7. Historia napraw i gałęzie
Gałęzie próbne: experiment/herbert-fp32-benchmark-v1 oraz trial/herbert-fp32-benchmark-v1; draft PR producenta #7 i runtime #3.
Run runtime 37230173951 zatrzymał się na brakujących tłumaczeniach nowych zasobów diagnostycznych; zakres wyjątku lint ograniczono do tego pliku i zapisano backlog.
Run 37231774451 miał PASS kompilacji oraz obowiązkowej zgodności, lecz skrypt workflow wymagał niedostępnego rg. Zastąpiono sprawdzenie znacznika Pythonem stdlib, sprawdzając ścieżkę pozytywną i negatywną. Run 37232458354 potwierdza poprawkę; żaden warunek testu nie został usunięty.

## 8. Artefakty i tożsamość
APK ARM64:
https://github.com/jakamilek/CleverKeysPL/actions/runs/37232458354/artifacts/11314463703
Artefakt cleverkeys-herbert-fp32-benchmark-trial-arm64, ZIP 35 697 510 bajtów.
SHA-256 ZIP: a5fda8a6163de65bdd531cd48a88aa3ce14b79cff04dbb630d80a59f1c3109d5
CleverKeys-v2.0.0-arm64-v8a.apk: 35 696 490 bajtów.
SHA-256 APK z CI: 70c3e0e94f10e0a6e7ec4f9b6e043767cd9e41e7e21f14f21586958b07e07958
Raporty runtime: artefakt 11313914852.

Model:
https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37230171787/artifacts/11312693984
ZIP herbert-fp32-benchmark-v1-model: 657 295 441 bajtów, około 657 MB / 627 MiB.
SHA-256 ZIP: 36c2183acca3ae6dca4afb54c28fe4d9d4cb37ec26f3230c94b4e007b494587f
Ważność artefaktu modelu według katalogu GitHub: 2026-10-18T19:57:49Z.
allegro/herbert-base-cased, rewizja 50e33e0567be0c0b313832314c586e3df0dc2297, CC BY 4.0.
model.onnx: 651 798 883 bajtów; SHA-256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2.
Mały artefakt raportów producenta 11312569320 pobrano i niezależnie sprawdzono: rozmiary i SHA plików bez modelu, wszystkie zapisane porównania wyników oraz 2471 wektorów tokenizacji.

## 9. Granice dowodów
Nie wykonano jeszcze próby na telefonie ani skanu antywirusowego. SHA APK policzył CI; archiwum APK jest większe od limitu narzędzia pobierania 32 MiB, a bezpośrednia próba pobrania zwróciła HTTP 403, więc nie ma niezależnej lokalnej weryfikacji tego APK. Pełnego ZIP modelu także nie pobrano lokalnie; jego tożsamość kontroluje producent i importer.
Benchmark 32/64 mierzy opóźnienie, nie dowodzi różnicy jakości: wspólne przykłady jakości mają najwyżej 13 słów. Pomiar PSS dotyczy całego procesu i jest próbkowany między wywołaniami; nie jest dokładnym szczytem pamięci modelu, energii ani temperatury.

## 10. Następny krok
Rozpakować ZIP APK i zainstalować APK ARM64. Osobny ZIP modelu pozostawić nierozpakowany.
Otworzyć plac testowy gestów → „Test polskiej SI” → „Importuj ZIP z modelem” → „Uruchom test”. Przygotowane przykłady uruchamiają się automatycznie.
Pozostać na ekranie, opcjonalnie powtórzyć 2–3 razy, wybrać „Kopiuj raport” i przekazać raport do analizy. Test obejmuje zgodność oraz 90 próbek czasowych dla każdego limitu 32/64.
Nie uruchamiamy nowego CI dla tych zmian dokumentacyjnych. Monitorowanie pojedynczego nowego runu jest ograniczone do 60 sekund łącznie, następnie stan przekazuje użytkownik.

## 11. Zmiana względem poprzedniego kamienia milowego
Obowiązkowa zgodność Kotlin była już potwierdzona; obecnie cały runtime CI zakończył się PASS i dostępny jest konkretny APK ARM64 z tożsamością, instrukcją telefonu i oddzielnym przypiętym modelem FP32.
Po przetestowanym headzie kod się nie zmienił: dodano wyłącznie dokumentację wyników i instrukcję docs/HERBERT_FP32_PHONE_TRIAL_V1.md. Jedynym kolejnym warunkiem decyzji jest teraz raport z urządzenia, a następnie niezależna ocena jakości.
