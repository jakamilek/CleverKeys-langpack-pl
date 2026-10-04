# Stabilizacja CI po zaakceptowanej wersji v9 — 2026-10-04

## 1. Zweryfikowany stan repozytoriów
Stan sprawdzony 2026-10-04 przed zapisem tego dokumentu: main CleverKeysPL c6e34780d9da3b03026e5ba8b5e214345d18b12d; main CleverKeys-langpack-pl 8ba0fed207f21694bb8e1f0eb73bc71a09cb85ba. Zapis tego kamienia doda osobne commity dokumentacyjne na obu mainach. Kod integracyjny pozostaje na gałęzi docs/source-variants-integration-v1, draft PR #1: 5200f718a0a9f2cf29135d6e8607c171d308f889, rodzic 897edfa3e3e9ea28abaf75a32c99417233e6a6d2. Wszystkie sześć zmienionych plików odczytano z tego commita i porównano z przygotowaną treścią — zgodność.

Wspólny zapis: [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-04_CI_STABILIZATION.md) oraz [CleverKeys-langpack-pl](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-04_CI_STABILIZATION.md).

## 2. Architektura
Polski swipe używa dekodera geometrycznego. Warianty kapitalizacji pozostają atrybutami jednego wpisu słownika. Zaakceptowane ustawienia v9, synchronizacja edytora, dodawanie do słownika bez zmiany tekstu, formatowanie i obsługa Backspace pozostają bez zmian.

SubkeyAssignActivity ładuje mapowanie asynchronicznie przez LaunchedEffect do zapamiętanego obiektu stanu. Stan i efekt są powiązane z managerem, kodem klawisza i kierunkiem. Odczyt jest anulowany po opuszczeniu kompozycji; wyświetlanie czeka również na rozstrzygnięcie pustego slotu. Zastępuje zapis produceState odrzucony przez dotychczasowy lint.

## 3. Zaakceptowane ustalenia
Użytkownik potwierdził działanie zmian v9 na telefonie: „jest tak jak być powinno”. Jest to jakościowa akceptacja, bez dopisywania osobnych wyników każdej kombinacji opcji. Priorytetem pozostaje polskie tłumaczenie; wykryte błędy innych języków należy zapisywać do późniejszej poprawy. Autoryzowano teraz naprawę przyczyn czerwonego CI. Limit monitorowania Actions: 60 sekund łącznie na build.

## 4. Rozwiązania odrzucone
Nie wyciszamy ProduceStateDoesNotAssignValue, nie aktualizujemy baseline lint i nie osłabiamy skanera HIGH/CRITICAL. Nie przeprowadzamy zbiorczej aktualizacji zależności. Nie zmieniamy AI/CTC, słownika, ustawień zaakceptowanych gestów ani wersji aplikacji. Nie ma merge, tagu lub publikacji release.

## 5. Plan niewdrożony
Po stabilizacji: diagnoza niepożądanej kapitalizacji Ale/Lub, dopracowanie faktycznie niejasnych polskich opisów ustawień, następnie ocena kontekstowego rankingu z poprawną formą w pierwszej trójce. Przegląd językowy pozostałych 21 lokalizacji jest odłożony. Backup/import, instrumented/minified/performance pozostają oddzielnymi zadaniami.

## 6. Weryfikacja i jej granice
Lokalnie Bun 1.3.11 wygenerował lockfile; bun install --frozen-lockfile PASS. Zmienił się wyłącznie devalue z 5.8.1 na 5.9.3 oraz identyczny override w package.json i bun.lock. Astro zbudowało 84 strony — PASS. git diff --check PASS. Sprawdzono zainstalowaną wersję devalue 5.9.3.

Bun audit nie raportuje już devalue, ale zwraca kod 1 z powodu innych zgłoszeń — nie jest to czysty audyt. Lokalnie nie uruchomiono Android Gradle/Kotlin/lint: brak skonfigurowanego SDK. Nowy [CI run 37185565077](https://github.com/jakamilek/CleverKeysPL/actions/runs/37185565077) był in_progress podczas jedynego sprawdzenia około 12 sekund po push; monitorowanie zakończono. Kompilacja, pure/focused tests, debug/release vital lint oraz Trivy są PENDING. Nie przypisujemy temu commitowi wcześniejszych 3031 zaliczonych testów.

## 7. Gałęzie i historia
docs/source-variants-integration-v1 jest gałęzią integracyjną trial; main nie zawiera promowanego kodu trial. V9 897edfa3e3e9ea28abaf75a32c99417233e6a6d2: run 37183355586, assembleDebug i 2804 pure + 227 focused PASS (3031), jakościowa akceptacja telefonu. Run ten nadal miał błąd lint i cztery HIGH devalue. Starsze v5/v6 przyczyny problemów telefonu nie zostały dowiedzione.

## 8. Artefakty i punkty integracji
Nowy commit 5200f718a0a9f2cf29135d6e8607c171d308f889, sześć plików: SubkeyAssignActivity.kt, site/package.json, site/bun.lock, docs/specs/subkey-popover.md, memory/todo.md, memory/REPO_INSTRUCTIONS.md. Aktualizacje dokumentacyjne zapisują akceptację v9 i priorytet języka polskiego.

Zaakceptowany APK v9: [artifact 11295888906](https://github.com/jakamilek/CleverKeysPL/actions/runs/37183355586/artifacts/11295888906), ZIP 97039723 bajty; wygasa 2026-10-11T06:46:09Z. SHA-256 archiwum według metadanych GitHub: ad6d4aa8522bec864e3c78215e75cacd7ae57e3918f0c4bd2e8e7b2b59874784; nie jest to lokalnie policzony hash APK. Nowy run nie ma jeszcze zweryfikowanego APK.

devalue 5.9.3 — integralność lockfile z rejestru npm: sha512-xRumYOCUZN/EesqHEU3WOXanOZNvfZFZ/o1AHVFDX1yI0UAkZkOgDXt341CzKoBVIkgQba55/+DjGBKrIoKcHw==. [Upstream opis poprawek](https://github.com/sveltejs/devalue/releases/tag/v5.9.3). Compose: [cykl życia LaunchedEffect](https://developer.android.com/develop/ui/compose/side-effects#launchedeffect).

Producer kod 75a06570cc9eaac72f1e7c4376a4efd068be73fb bez zmian. Pack SHA-256 4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7; CKDT 087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20 (proweniencja z poprzedniego kamienia; nie pobierano ich ponownie w tym etapie).

## 9. Ograniczenia i znane zgłoszenia
Bun audit po aktualizacji zgłasza http-cache-semantics 4.2.0, HIGH GHSA-ch52-4w7c-c8xp/CVE-2026-93748. [GitHub Advisory](https://github.com/advisories/GHSA-ch52-4w7c-c8xp) podaje brak patched version podczas sprawdzenia. npm udostępnia już 4.3.0, ale naprawa tego konkretnego zgłoszenia nie została tu potwierdzona; nie wprowadzono niezweryfikowanej aktualizacji. Nie jest to zgłoszenie czterech wcześniej blokujących błędów devalue.

Pozostałe lokalne zgłoszenia: Svelte 5.55.4 — moderate GHSA-f3cj-j4f6-wq85, GHSA-rcqx-6q8c-2c42, GHSA-9rmh-mm8f-r9h6, GHSA-pr6f-5x2q-rwfp; esbuild 0.28.0 — low GHSA-g7r4-m6w7-qqqr. Zachowano dotychczasową politykę CI: fixed HIGH/CRITICAL blokują, unfixed oraz niższe poziomy są raportowane. Dokładny wynik Trivy dla nowego commita jest nieznany.

## 10. Następny krok
Gdy użytkownik zgłosi zakończenie runu 37185565077, odczytać wszystkie joby i logi, potwierdzić wynik debug lint i release vital lint oraz skanera, a także dostępność APK. Nie monitorować w tle. Ewentualne nowe błędy rozwiązać na podstawie logu; dopiero po zielonym CI przejść do Ale/Lub. Zachować zaakceptowaną wersję v9 jako punkt odniesienia.

## 11. Różnica wobec poprzedniego kamienia
[Poprzedni kamień v9](PROJECT_MILESTONE_2026-10-04_SETTINGS_V9.md) zapisał akceptację obsługi telefonu i otwarte przyczyny czerwonego CI. Ten etap dodaje naprawę zapisu Compose, pojedynczą aktualizację bezpieczeństwa zależności z wygenerowanym lockfile, zaliczoną lokalną budowę witryny i nowy run do sprawdzenia. Nie ogłasza jeszcze usunięcia wszystkich błędów CI ani nowej akceptacji APK.
