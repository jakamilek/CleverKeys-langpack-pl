# Kamień milowy: warianty źródłowe w Androidzie — etap 1

Data: 2026-10-03. Status: implementacja w draft PR, bez scalenia i bez wydania.

## 1. Zweryfikowany stan main

Snapshot przed zapisem tego dokumentu: CleverKeysPL `d6d70fc778745e55bb2fa39f2bc300c73a4a0f41`,
CleverKeys-langpack-pl `23e6c72656e958d9ae1ad4373b92f62fb0368e83`.
Kod wariantów nie jest na main. Runtime draft PR #1:
https://github.com/jakamilek/CleverKeysPL/pull/1 . Producent draft PR #5:
https://github.com/jakamilek/CleverKeys-langpack-pl/pull/5 .

## 2. Architektura

CKDT i geometric zachowują jeden klucz leksykalny. Opcjonalny sidecar API v1
przenosi politykę pisowni oraz zachowane metadane/proweniencję. Importer sprawdza
deklarację, schemat, SHA, język, unikalność pól/kluczy, zgodność powierzchni i
polityk. Immutable provider ładuje dane poza UI. Po istniejącym rankingu kontekstu
najlepszy klucz daje parę powierzchni z tym samym wynikiem; następny różny klucz
jest trzeci. Pasek i automatyczny commit używają tej samej formy.

## 3. Ustalenia przyjęte

Użytkownik jawnie zwolnił fork z odziedziczonej konsultacji Gemini 3 Pro / PAL;
odstępstwo zapisane w memory/REPO_INSTRUCTIONS.md, commit `d6d70fc`.
Bez Shift/autocap pierwsza jest forma domyślna, chyba że istniejąca preferencja
użytkownika pasuje do wariantu źródłowego. Na początku zdania / ze Shift pierwsza
jest duża litera i pozostaje wybór małej. Oznaczony wybór zachowuje dokładny tekst
przy commicie. Caps Lock utrzymuje dotychczasową listę uppercase bez rozwijania.
Przymiotnik z jedną formą, np. łódzki, pozostaje pojedynczy. Aktualizacja/usunięcie
paczki czyści snapshot; cold start pokazuje dotychczasowe propozycje do zakończenia
ładowania, bez późniejszego nadpisywania już wyświetlonego swipe.

## 4. Odrzucone lub odłożone rozwiązania

Nie dublujemy CKDT jako łódź/Łódź i nie dopisujemy ręcznie znaczeń lub wyjątków.
Nie interpretujemy top-3 z deterministycznej pary jako jakości AI. CTC i nowe AI
pozostają odłożone, ponieważ geometric działa i etap par nie wymaga tych silników.
Nie znosimy pozostałych wymagań testów, bezpieczeństwa importu i publikacji.

## 5. Zaplanowane, niewdrożone

Pełne generowanie źródłowych metadanych dla całego PL; edycja Łódźi→Łodzi/łodzi;
ranking kontekstowy korzystający z kategorii; interpunkcja. Etap 1 nie jest pełną
implementacją wszystkich opcjonalnych pól logicznego API ani nowym rerankerem.

## 6. Nieweryfikowane

Pozostają realne testy IME/Termuksa. Release lint był pominięty po niepowodzeniu lint debug. Testy JVM/MockK nie zastępują InputConnection w prawdziwej
aplikacji ani sprawdzenia Termuksa. Nie zmierzono czasu/heapu pełnego sidecara.
Nie ma dowodu na jakość rozpoznawania znaczenia przez AI, ponieważ AI tu nie działa.

## 7. Gałęzie historyczne i bieżące

`docs/source-variants-integration-v1` w runtime zaczęła jako propozycja, a teraz
zawiera implementację; zachowano historię i dołączono bieżący main bez force push.
Runtime head po aktualizacji dokumentacji: `ba3d6a9054fc404128effa6b906c5a3e6d844e9e`; testowany kod: `a21d9fef3b643ad7a09520f232d9d39f42be1071`. Commit późniejszy zmienia wyłącznie dokumentację. `feature/source-variants-trial-v1` w langpacku,
head po aktualizacji dokumentacji `75a06570cc9eaac72f1e7c4376a4efd068be73fb`; kod/artefakt producenta zweryfikowany na `e970d209ec0c10fe7733cdb80f61a3bc155a1f00`. Jest to trial, nie main.
Wcześniejsze gałęzie eksperymentów kontekstu/metadanych pozostają materiałem
audytowym; nie promowano ich do produkcji.

## 8. Artefakty i integracja

Trial producenta ma 9 kluczy, 39 interpretacji i 83 dowody wygenerowanych form.
Sidecar: 24 683 bajty, SHA-256 `e0a878249f021eff00eeb11165f600720f9d5fe24f383c9063e1b91c2a589a54`.
ZIP trial: SHA-256 `4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7`.
Dictionary SHA-256 `087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20`,
unigrams SHA-256 `de64baefedba0f4da8a4f50e41fa431a92dd3241133cd5825d965fe84e5818c0`.
Dictionary/unigrams byte-identyczne z preview; nie regenerowano core 100k.
Producent CI run 37106034633 / artifact 11267842273:
https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37106034633/artifacts/11267842273 .
Wszystkie 13 plików implementacji runtime odczytano ponownie z przypiętego commita i porównano
1:1 z lokalnym zapisem. Testy korzystają z identycznego sidecara producenta.
Runtime CI run 37108165202 na `a21d9fef3b643ad7a09520f232d9d39f42be1071`:
kompilacja debug PASS; runPureTests 2742 PASS; LanguagePackImportTest 45 PASS;
SwipeAutocapCommitTest 7 PASS; SuggestionTapPartialReplaceTest 5 PASS — razem
2799 testów Androida. Producent: 21 testów PASS. Guard na runnerze ma jawny limit
heap 2 GiB i metaspace 512 MiB, bez zmiany domyślnych limitów telefonu.

Debug APK artifact ID 11268244117, 96 857 664 bajty:
https://github.com/jakamilek/CleverKeysPL/actions/runs/37108165202/artifacts/11268244117 .
Digest ZIP zgłoszony przez GitHub: `sha256:36b41351c6e92ea4abefab78fd7af36abad88222f33f1532a42c58f5d67a1763`.
Archiwum APK nie zostało pobrane ani niezależnie przeliczone w tej sesji.

## 9. Ograniczenia i luki

Trial obejmuje 9 kluczy, choć słownik pozostaje pełnym preview 106 363 kluczy.
Parser obsługuje source lowercase/capitalized i najwyżej dwie powierzchnie;
zmiana tego kontraktu wymaga jawnego rozszerzenia. Granice ekstrakcji: manifest
256 KiB, sidecar 32 MiB, inne pliki 64 MiB, suma 128 MiB i 64 wpisy; istniejący
limit modelu pozostaje. Kopiowanie jest strumieniowe. Odrzucane są ścieżki i
duplikaty ZIP. Backup daje rollback przy błędzie rename, nie odzyskiwanie po
nagłym zakończeniu procesu. Przy nieudanym rollback backup jest zachowany.
Baseline CI main, run 37106833856, już przed implementacją miał błąd lint
ProduceStateDoesNotAssignValue w SubkeyAssignActivity.kt:148 i 4 findings HIGH
z devalue 5.8.1 w site/bun.lock. Nie wyłączono bramek. Aktualny run 37108165202 zakończył się FAILURE przez te same dwa problemy: lint nadal 1 error / 210 warnings i security nadal 4 HIGH z devalue. Brak nowego błędu lint w kodzie wariantów. Bramki nie zostały wyłączone.

## 10. Następny krok

Wykonać realny test z udostępnionym debug APK i ZIP-em trial producenta: pary,
wyboru małej litery i zastąpienia tokenu. Przed promocją naprawić lub jawnie
rozstrzygnąć istniejące blokady CI. Potem rozszerzać źródłowe generowanie danych;
edycja po dopisaniu litery jest oddzielnym etapem. Scalenie i wydanie nadal
wymagają osobnej decyzji.

## 11. Zmiana względem poprzedniego kamienia milowego

Poprzedni milestone VARIANT_TRIAL_PRODUCER miał gotowy producent i propozycję
runtime z blokadą konsultacji. Teraz użytkownik zwolnił konsultację, importer /
provider / pasek / commit są zaimplementowane w draft PR, debug build i 2799 testów przeszły, a APK jest dostępne do realnej próby. AI, CTC,
pełne metadane packa oraz poprawka Łódźi nie zostały przy tym wdrożone.

## Dokumenty powiązane

Runtime: https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-03_ANDROID_SURFACE_VARIANTS_V1.md
Langpack: https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-03_ANDROID_SURFACE_VARIANTS_V1.md
Poprzedni: docs/PROJECT_MILESTONE_2026-10-03_VARIANT_TRIAL_PRODUCER.md.

W trakcie CI poprawiono przesłonięcie zmiennej języka w projekcji wariantów i
ustawiono jawny limit pamięci runnera po GC-overhead OOM przy domyślnym 1 GiB.
Poprawki są objęte końcowym zielonym buildem i testami wskazanego commita.
