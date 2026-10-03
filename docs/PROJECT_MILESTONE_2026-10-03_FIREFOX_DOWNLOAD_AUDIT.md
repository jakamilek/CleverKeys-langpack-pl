# Kamień milowy: audyt alarmu pobierania Firefoksa

Data weryfikacji: 2026-10-03. Status: integralność potwierdzona, ClamAV bez detekcji; przyczyna alarmu Firefoksa nierozstrzygnięta.

## 1. Zweryfikowany stan main

Snapshot przed zapisem dokumentu: CleverKeysPL `b8d5cdc2da729330baaeae662e2c67926ba0d573`; CleverKeys-langpack-pl `3e34f8d2c72036cc38ab58342f13bec9fb574ed4`.
Ten etap zmienia wyłącznie dokumentację. Punktem wejścia w architekturę i testy pozostaje [poprzedni milestone](PROJECT_MILESTONE_2026-10-03_ANDROID_SURFACE_VARIANTS_V1.md).

## 2. Architektura

Bez zmian: jeden klucz CKDT/geometric, źródłowe warianty powierzchni w opcjonalnym sidecarze. Producent i runtime pozostają w draft PR; kod wariantów nie został scalony do main.

## 3. Ustalenia przyjęte

Zrzut użytkownika zawiera komunikat „Ten plik zawiera wirusa lub inne złośliwe oprogramowanie”, z przyciskami Usuń/Pozwól. To kategoria malware, nie komunikat o rzadko pobieranym pliku. Zgodność hashy i czysty wynik pojedynczego skanera nie wystarczają do stwierdzenia, że alarm jest fałszywy.

## 4. Rozwiązania odrzucone

Nie rekomendowano przycisku Pozwól, wyłączenia ochrony, zmiany przeglądarki ani przepakowania w celu obejścia blokady. Nie zmieniono paczki. Nie przekazano paczki zewnętrznemu serwisowi skanowania.

## 5. Zaplanowane, niewdrożone

Realna próba IME pozostaje planem. AI, CTC, pełna generacja metadanych, interpunkcja i edycja Łódźi→Łodzi/łodzi pozostają odłożone zgodnie z poprzednim milestone.

## 6. Nieweryfikowane

Nie znamy szczegółowego werdyktu Safe Browsing ani reguły, która wywołała blokadę. Nie rozstrzygnięto, czy dotyczy zawartości, reputacji adresu pobrania czy innego sygnału. Nie wykonano skanu APK ani analizy dynamicznej. Audyt dotyczy wyłącznie ZIP-a langpacka wskazanego przez użytkownika.

## 7. Istotne gałęzie

Runtime: `docs/source-variants-integration-v1`, ostatni zweryfikowany head dokumentacji `ba3d6a9054fc404128effa6b906c5a3e6d844e9e`, testowany kod `a21d9fef3b643ad7a09520f232d9d39f42be1071`.
Producent: `feature/source-variants-trial-v1`, ostatni zweryfikowany head dokumentacji `75a06570cc9eaac72f1e7c4376a4efd068be73fb`, producent badanego artefaktu `e970d209ec0c10fe7733cdb80f61a3bc155a1f00`. Bieżących headów tych gałęzi nie odświeżano w tym audycie.

## 8. Artefakt i wyniki kontroli

GitHub Actions: run [37106034633](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37106034633), artifact [11267842273](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37106034633/artifacts/11267842273).

- Pobrano dokładny ZIP ze wskazanego podpisanego adresu, bez uruchamiania zawartości.
- Archiwum zewnętrzne: 907 721 bajtów; SHA-256 `55b54b7472210baacce823b69c27d4a9f7f88091d4b777031bab58730d5678c9`.
- Jest bajtowo identyczne z pobranym wcześniej artefaktem GitHub Actions i zgodne z digestem GitHub.
- Wewnętrzny `cleverkeys-pl-variants-trial.zip`: SHA-256 `4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7`; identyczny z lokalnie zbudowanym trialem.
- Zewnętrzny ZIP zawiera wewnętrzny ZIP, sumę SHA-256, sidecar i raport. Wewnętrzny ZIP zawiera NOTICE.txt, dictionary.bin, language-intelligence.json, manifest.json i unigrams.txt. Brak zaszyfrowanych wpisów i błędów CRC; brak APK, EXE i skryptów w tych archiwach.
- ClamAV 1.5.3: official main v63, daily v28142, bytecode v339. Daily zbudowano 2026-10-03 06:24 UTC. Wszystkie trzy CVD przeszły `sigtool --info` z wynikiem Verification OK.
- Sygnatury pobrano oficjalnym CVDUpdate 1.2.0. Zwykły DNS był niedostępny; zmieniono tylko transport publicznego rekordu TXT na HTTPS DNS, pozostawiając logikę pobierania/wersji i walidację CVD. Nie obchodzono limitów dostawcy.
- Skan objął archiwum zewnętrzne, wewnętrzne i każdy rozpakowany plik osobno: 10 plików, 3 katalogi, 3 642 799 znanych sygnatur, 21.16 MiB przeskanowanych danych.
- Wynik: **Infected files: 0**, kod wyjścia **0**. Każdy plik otrzymał OK. Brak błędów skanera i alertów limitów.
- Użyto oficjalnych baz, limitu aktualności 2 dni, rekursji archiwów, allmatch, PUA, alertów szyfrowania/przekroczenia limitów i wyłączono cache. Limity: 20M/pliki, 100M/dane kontenera, 100 wpisów, rekursja 10.

Nie zapisujemy podpisanego URL-a z tymczasowym tokenem w repozytorium.

## 9. Ograniczenia i znane luki

Czysty wynik ClamAV nie jest gwarancją bezpieczeństwa ani dowodem fałszywego alarmu Firefoksa. Dotychczasowe problemy lint/security CI opisane w poprzednim milestone nie są dowodem przyczyny tego alarmu. Nie zmieniono ani nie wyłączono żadnych bramek.

## 10. Następny uzasadniony krok

Pozostawić blokadę pobrania do wyjaśnienia werdyktu ochrony. Zgromadzone hashe i wynik skanu umożliwiają dalsze sprawdzenie konkretnego artefaktu i ewentualne zgłoszenie błędnej klasyfikacji po ustaleniu właściwej ścieżki. Wysłanie pliku lub zgłoszenia do zewnętrznej usługi nie zostało autoryzowane ani wykonane. Próba IME, scalenie i wydanie nie zostały wykonane w tym etapie.

## 11. Różnica względem poprzedniego milestone

Dodano weryfikację dokładnego pliku z linku użytkownika, identyczność z artefaktem/buildem, analizę struktury obu ZIP-ów, rozpoznanie dokładnej kategorii komunikatu Firefoksa oraz rzeczywisty skan aktualnym ClamAV. Przyczyna alarmu pozostaje otwarta; nie promowano triala ani nie zmieniono kodu.

## Dokumenty powiązane

- [Runtime — ten audyt](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-03_FIREFOX_DOWNLOAD_AUDIT.md)
- [Langpack — ten audyt](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-03_FIREFOX_DOWNLOAD_AUDIT.md)
- [Poprzedni etap runtime](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-03_ANDROID_SURFACE_VARIANTS_V1.md)
- [Poprzedni etap langpack](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-03_ANDROID_SURFACE_VARIANTS_V1.md)
- [Mozilla — ochrona pobrań](https://support.mozilla.org/en-US/kb/how-does-phishing-and-malware-protection-work)
- [Mozilla — rodzaje komunikatów](https://support.mozilla.org/en-US/kb/where-find-and-manage-downloaded-files-firefox)
