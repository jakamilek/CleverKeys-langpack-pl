# Kamień milowy — compact-case-v4: oba CI PASS, APK gotowe do testu

Data weryfikacji: 2026-10-10 UTC (Europe/Warsaw: 10 października). GitHub jest źródłem prawdy.

## 1. Zweryfikowane HEAD main przed zapisem
- CleverKeysPL: 4877da5504d8ed683e43d096a4336aa9efcfcce9.
- CleverKeys-langpack-pl: 000dc212e4663cdb2dfb3be17708f50df5b42816.
Są to odczytane HEAD przed nowymi commitami dokumentacyjnymi.
Ten sam stan przekrojowy zapisano w [runtime](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-10_COMPACT_CASE_APK_READY.md) i [producer](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-10_COMPACT_CASE_APK_READY.md).

## 2. Architektura bieżącego trial
Kod trial/herbert-live-v1: 3f48e456f0d8f411e80be3857f1846e4b2cd139e, parent 5646c9157251d80c7ccfe6ceb143a3ca3bf6338b.
Geometric dekoduje. HerBERT ocenia przed pojedynczym zatwierdzeniem pełną ograniczoną grupę maksymalnie czterech powierzchni z dwóch polskich kluczy: wspólny fold lub potwierdzony source lemma/POS.
SwipeSurfaceVariants.present jest terminalnym krokiem wspólnej publikacji. Pierwsza oceniona pisownia każdego klucza zostaje reprezentantem; kandydaci dekodera spoza grupy uzupełniają pierwsze trzy miejsca, a dodatkowe kapitalizacje pozostają za nimi. Nie giną powierzchnie ani score/language/exactCase. Winner i względna kolejność innych dekodowanych słów są zachowane. Slate presentationOnly nie może ponownie trafić do modelu.
Ten sam publish obejmuje SI success/off/no-model/busy/timeout/next-touch i chronione Shift/początek zdania.

## 3. Zaakceptowane ustalenia
Globalny budżet prezentacji, bez wyjątków dla konkretnych słów i bez duplikowania kluczy słownika. Przegrywająca kapitalizacja nadal jest wybieralna, lecz nie ma zarezerwowanego Top3. SI może nadal wybrać dużą literę jako pierwszą, kiedy nada jej wyższy wynik.
Model/tokenizer/scorer, dane packa, default 32 słowa, opcje 16/32/64, limit 350ms i opt-in pozostają. Zachowane BS/haptyka, autokorekta, Shift, autospace, editor/privacy/one-shot guards.

## 4. Odrzucone rozwiązania
Nie wycinamy poprawnych nazw miejscowości ani nie nadajemy ręcznych wag/opisów. Nie mieszamy raw logp z geometrycznym score. Mała miejscowość nie oznacza automatycznie małego użycia nazwy.
Nie rozluźniono zabezpieczeń ordered dla poprzedniego błędu testu.
Nie scalono kodu do main, nie ma release/tag/version bump. Debug trial jest autoryzowany w sesji.

## 5. W planie, jeszcze niewdrożone
Źródłowe priory użycia opisuje docs/specs/polish-case-usage-priors.md na trial: case-sensitive reading/lemma/POS z korpusów z kontrolą początku zdania i wieloznaczności; identyfikacja SIMC/PRNG; pomocnicze dane populacji GUS BDL/NSP2021 wymagające mapowania miejscowości statystycznych i proweniencji. Unknown nie oznacza zero/rare. Brak wdrożonych częstości, progów populacji i wag rzadkości.
Pokrycie swipe słownika pozostaje osobnym odłożonym zadaniem.

## 6. Weryfikacja bieżącego HEAD
Oba zakończone runy na dokładnie 3f48e456f0d8f411e80be3857f1846e4b2cd139e:
- [live 38040432033](https://github.com/jakamilek/CleverKeysPL/actions/runs/38040432033): SUCCESS, android job 114179413305; wszystkie wymagane steps success;
- [standard CI 38040436247](https://github.com/jakamilek/CleverKeysPL/actions/runs/38040436247): SUCCESS; Build and Test 114179424992, Security Scan 114179425071, Code Quality 114179425082, APK Size 114181877052 success.

Odczyt logów:
- kompilacja rzeczywistych źródeł Android PASS;
- 2881 pure tests PASS w obu runach;
- obowiązkowy marker HerBERT original conformance: 2471 token vectors; 232 batches / 532 candidates / five inputs PASS;
- dziewięć live handler/editor/source suites: 195 testów PASS;
- standard integration suites: 300 testów PASS. Zestawy się nakładają, nie sumować;
- debug lint i release vital lint PASS, assembly oraz kontrola ARM64 bez FP32/test fixtures PASS;
- standard security/code-quality/APK-size gates PASS.

Live reports ZIP pobrano i ponownie policzono SHA-256; niezależnie odczytano pure marker/OK (2881 tests) oraz lint XML: 0 Error/Fatal, 234 Warning.
Conformance jest kontrolą oryginalnych tokenizer/feed/reference fixtures, nie nowym dowodem JNI inferencji na Androidzie ani oceną trafności językowej.
Bieżący test telefonu i niezależna jakość/performance v4 pozostają NIEZWERYFIKOWANE.

## 7. Gałęzie i historia
trial/herbert-live-v1, draft [PR4](https://github.com/jakamilek/CleverKeysPL/pull/4): jedyne miejsce nowych zmian runtime.
main obu repo: tylko dokumentacyjny checkpoint.
Poprzedni checkpoint docs/PROJECT_MILESTONE_2026-10-10_COMPACT_CASE_CI_REPAIR.md opisuje wspólną porażkę jednego testu na 5646c915: użyto nieobecnej łódź w dziewięciowpisowym fixture sourcev5. Naprawa tylko tej metody używa obecnej laska/Laska i dodatkowo sprawdza grupę wejściową, zachowując kontrolę prezentacji i metadanych. Nie zmieniono danych ani gates.
Historyczny 0acb647606cb52f0a3263b098704745306b5d6b7 (word-forms-v3) miał PASS i pozytywną opinię użytkownika. Nie przenosić tej opinii na bieżący APK.

## 8. Artefakty i tożsamość
Nowy [ARM64 live trial artifact 11665712630](https://github.com/jakamilek/CleverKeysPL/actions/runs/38040432033/artifacts/11665712630), ważny według API do 2026-10-24:
- ZIP 35808273B, digest GitHub/API i logu uploadu: 9064c0a0190404e9c7edfb00ceffd6ef832f5988a56bec296210783010a4aa52;
- APK CleverKeys-v2.0.0-arm64-v8a.apk, 35806926B;
- APK SHA-256 z wymaganej kontroli CI: b9c063b3f6bea4c7549f2574e8841f4f0751ea751b291fa920074fafaeeb481f;
- CI identity: codeCommit 3f48e456f0d8f411e80be3857f1846e4b2cd139e, liveRevision compact-case-v4, liveAI true, optInDefault false, compactCasePresentation true, distinctLeadingTarget 3, maxLiveSurfaces 4, familySearchCandidates 5, ordinaryDecodedForms/sharedSourceLemma true;
- contextDefaultWords 32, availableWordLimits 16/32/64, waitDefaultMs 350, backspaceWordHaptics/nativeConformanceBeforeLive true.
APK bytes nie pobrano/re-hashowano lokalnie; jego tożsamość i hash odczytano z successful CI audit/upload i powiązania artifact/run/SHA.

[Live reports artifact 11665622785](https://github.com/jakamilek/CleverKeysPL/actions/runs/38040432033/artifacts/11665622785): 22692B, SHA-256 b915bf4e6314ca2505ec36040032ca51f9a85faa9611e14a9020db96cde2ba6c; pobrano, re-hash i treść zweryfikowano.
Standard artifacts: apk-debug 11666380425, lint-results 11666201137. Dla telefonu wskazujemy ARM64 live artifact, nie zbiorczy standard ZIP.

Oryginalny model: producer d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c, run 37230171787, artifact 11312693984; 651798883B, SHA f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2. Oddzielny prywatny import, 7 plików z kontrolą tożsamości i pełna native zgodność przed READY; aktualizacja APK nie wymaga nowych wag.
Pack v5 ZIP SHA aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb; sidecar SHA 5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d. Dane producenta nie zmieniły się tym etapem.

## 9. Ograniczenia i znane luki
Budżet prezentacji nie jest klasyfikatorem małych wsi. Wagi użycia wymagają audytu źródeł i niezależnej kalibracji. Nie twierdzić, że SI porównuje pełny ranking wszystkich słów.
Historyczny PSS procesu na telefonie około 2132MiB; brak nowego pomiaru v4.
Odłożone zgłoszenia swipe: dodam, grzeje, kasami, nawilżane, odpowiadam, patrzysz, poczekaj, podpowie, pozdrawiam; kapitalizacją/kapitalizacje poza badanym CKDT, kapitalizacja/kapitalizacji obecne. Installed pack/user dictionary/native swipe traces pozostają nieodczytane.
Pozostaje 234 warnings debug lint, nie oznacza pełnej naprawy historycznego backlogu.

## 10. Następny uzasadniony krok
Test nowego ARM64 APK na Nubia NX721J z SI gotowa: po „To jest bardzo ważna” sprawdzić, czy praca/pracą pozostają, a Praca/Pracą nie rezerwują pierwszych miejsc; sprawdzić Malina/Maliną i Łódź/łódź oraz ręczny Shift/początek zdania. Pierwsze trzy są celem różnorodności, jeżeli dekoder dostarczył inne klucze; alternatywy wielkiej/małej litery mogą być dalej.
Po feedbacku przejść do audytu danych case-use i odłożonego pokrycia słownika. Nie pollować Actions dłużej niż 60s total/run; użytkownik zgłasza zakończenie.

## 11. Różnica względem poprzedniego checkpointu
Stan repair/pending zastąpiono potwierdzonym PASS obu CI na identycznym poprawionym HEAD, konkretną bieżącą tożsamością ARM64 APK oraz niezależnym odczytem report ZIP. Test telefonu v4 nadal pending. Bez nowych zmian runtime/model/langpack.
