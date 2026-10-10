# Kamień milowy — compact-case-v4: naprawa danych testu i ponowne CI

Data weryfikacji: 2026-10-10 UTC. GitHub jest źródłem prawdy.

## 1. HEAD main przed zapisaniem dokumentu
CleverKeysPL: 62bf81eb8a29e30523d01d2baa65f7ab4ce0c280.
CleverKeys-langpack-pl: b5ff2c2fcc4f23847f054e5a823a705475865d26.
Są to zweryfikowane HEAD przed nowymi commitami dokumentacyjnymi, nie przyszłe SHA.
Ten sam checkpoint jest w obu repozytoriach: [runtime](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-10_COMPACT_CASE_CI_REPAIR.md) i [producer](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-10_COMPACT_CASE_CI_REPAIR.md).

## 2. Architektura
Kod trial/herbert-live-v1: 3f48e456f0d8f411e80be3857f1846e4b2cd139e, parent5646c9157251d80c7ccfe6ceb143a3ca3bf6338b.
Geometric dekoduje. Oryginalny HerBERT FP32 ocenia pełną grupę maksymalnie czterech form z maksymalnie dwóch polskich kluczy: równoważny fold lub potwierdzony wspólny source lemma/POS. Nie generuje form.
Terminalne SwipeSurfaceVariants.present zachowuje pierwszą ocenioną pisownię każdego klucza, uzupełnia pierwsze trzy miejsca kandydatami spoza grupy, a pozostałe kapitalizacje przenosi za nie. Wszystkie propozycje i równoległe score/language/exactCase pozostają; winner i względna kolejność pozostałych słów pozostają. Slate presentationOnly nie może wrócić do modelu.
Publikacja jest wspólna dla SI success/off/no-model/busy/timeout/next-touch oraz chronionego Shift/początku zdania. Jeden dotychczasowy commit i zabezpieczenia edytora/prywatności.

## 3. Zaakceptowane
Globalny budżet prezentacji zamiast punktowych wyjątków praca/Ale/Lub. Przegrywająca kapitalizacja pozostaje dostępna, ale bez gwarancji Top3. SI może wybrać dużą literę jako reprezentanta.
Model, tokenizer, dane langpacka, default32 słowa, opcje16/32/64, limit350ms, opt-in, BS/haptyka/edytor pozostają bez zmian względem v4.

## 4. Odrzucone
Nie rozluźniamy kontroli HerbertLiveSlate.ordered, aby przepuścić nieistniejącą formę w teście.
Nie dopisujemy łódź do historycznego wycinka sourcev5 ani ręcznych opisów/częstości do słownika. Nie wycinamy poprawnych nazw geograficznych.
Brak merge/release/tag/version bump. Debug trial jest autoryzowany przez użytkownika.

## 5. Plan, jeszcze niewdrożony
docs/specs/polish-case-usage-priors.md na branch trial opisuje pomiar użycia case-sensitive reading/lemma/POS z korpusów, z kontrolą początku zdania i wieloznaczności. SIMC/PRNG dla tożsamości miejsca i pomocnicze GUS BDL/NSP2021 dla populacji miejscowości statystycznych wymagają audytowalnego mapowania i proweniencji. Unknown nie oznacza rare/zero. Nie wdrożono wag, progów populacji ani danych o rzadkości.

## 6. Weryfikacja oraz rzeczy niezweryfikowane
Na5646c915 oba zakończone runy FAILURE:
- [live38037428188](https://github.com/jakamilek/CleverKeysPL/actions/runs/38037428188), job114170687927;
- [CI38037431013](https://github.com/jakamilek/CleverKeysPL/actions/runs/38037431013), Build and Test job114170698243.
Oba skompilowały aplikację. Oba uruchomiły2881 pure tests, jedna wspólna porażka: loneCasePairLeavesTwoOtherDecoderChoicesBeforeItsAlternate, IllegalArgumentException w HerbertLiveSlate.ordered:37. Test użył sourceProvider dla polish-surface-family-v5.json, który nie zawiera łódź, i próbował rankować nieistniejącą w tej grupie parę Łódź/łódź.
Naprawa zmienia tylko ten test: rzeczywista para laska/Laska z niezmienionego fixture; dodatkowo wymaga formGroupSize2 i dokładnie dwóch uprawnionych powierzchni SI. Wynik prezentacji nadal Laska,kosz,luz,laska,licz z zachowaniem score/exactCase.
Lokalnie zweryfikowano brak łódź, obecność/default/obie powierzchnie laska, brak powiązanych wpisów kosz/luz/licz oraz że poza jedną metodą plik testowy jest identyczny z parentem. Git blob testu643e6dfc8d0194a3f6a6f274f62a98c8e886e322 zweryfikowano w utworzonym tree przed commit/ref.
Brak lokalnego Android SDK/Kotlin. Nowe [live38040432033](https://github.com/jakamilek/CleverKeysPL/actions/runs/38040432033) i [CI38040436247](https://github.com/jakamilek/CleverKeysPL/actions/runs/38040436247) wystartowały na 3f48e456f0d8f411e80be3857f1846e4b2cd139e; odczyt: in_progress. Wyniki bieżącego HEAD, integration/lint/APK i test telefonu są pending. Nie czekać na zakończenie Actions; cap60s total/run.
Standard Security Scan i Code Quality poprzedniej próby sukces. Integration/lint/APK gates poprzedniej próby były skipped po pure failure; nie wolno uznać ich za PASS.

## 7. Gałęzie historyczne
trial/herbert-live-v1 i draft[PR4](https://github.com/jakamilek/CleverKeysPL/pull/4) są miejscem kodu; main obu repo dostają wyłącznie checkpoint.
0acb647606cb52f0a3263b098704745306b5d6b7 (word-forms-v3): live38032850945/standard38032853742 SUCCESS,2874 pure/193 live/298 standard integration (zestawy się nakładają, nie sumować). Pozytywna jakościowa opinia użytkownika, bez niezależnego benchmarku trafności.
Poprzedni checkpoint: docs/PROJECT_MILESTONE_2026-10-10_COMPACT_CASE_CI_STARTED.md. Poprzedni APK-ready: docs/PROJECT_MILESTONE_2026-10-10_ORDINARY_WORD_FORMS_APK_READY.md. Nie przepisywać historii.

## 8. Artefakty i punkty integracji
Nie ma zweryfikowanego APK compact-case-v4. Failed live report artifact11664975098:7258B; digest API sha256409468d40ccdee9cd20c95a4e248d0a818b7ff94bbbeea8988344ffe32ce513e; nie pobrano/re-hashowano tutaj.
Historyczny v3 APKartifact11662738564, ZIP digest a9e41c38ae60f5dda97bc9196c1afc4da3ecd92d2cffe3de54af0afe5bd54376; APK CI SHA fc79a7eca9b06b9fa2d2b5796d07d85482a6c444ba024bb060e91ccd91ed353d. Nie udostępniać jako nowej wersji.
Oryginalny model651798883B SHA f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2; producerd831e17b6cb99590d6ba036e92a72b6c3fd0cc7c/artifact11312693984.
Packv5 ZIP SHA aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb; sidecar5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d.
Mandatory original conformance marker pozostaje2471 token vectors/232batches/532candidates/fiveinputs PASS. Jest kontrolą tokenizer/feed/reference; nie nowym dowodem JNI inferencji na Androidzie ani trafności językowej.

## 9. Ograniczenia i luki
Budżet prezentacji nie dowodzi, że nazwa miejsca jest rzadka. Brak źródłowych wag case-use i populacji. Nie kalibrujemy raw logp przeciw geometrycznym score.
PSS procesu na telefonie historycznie około2132MiB; brak nowego pomiaru v4. Nie zmieniono oryginalnego modelu.
Pokrycie swipe odłożone: dodam,grzeje,kasami,nawilżane,odpowiadam,patrzysz,poczekaj,podpowie,pozdrawiam; kapitalizacją/kapitalizacje poza badanym CKDT. kapitalizacja/kapitalizacji istnieją. Nie naprawiono danych tym etapem.

## 10. Następny krok
Po informacji użytkownika o zakończeniu sprawdzić oba runy dokładnie na nowym SHA, wszystkie obowiązkowe gates, raporty i tożsamość APK. Dopiero po PASS dać bieżącą paczkę do telefonu; zweryfikować praca/pracą, Malina/Maliną i zachowanie SI/Shift. Następnie audyt źródeł case-use i odłożonego pokrycia słownika.

## 11. Różnica
Poprzedni checkpoint opisywał pierwsze CI jako pending. Teraz potwierdzono wspólną porażkę danych jednego testu, naprawiono ją bez zmian runtime/fixture/gates i uruchomiono nową parę CI. To nie jest jeszcze etap APK-ready.
