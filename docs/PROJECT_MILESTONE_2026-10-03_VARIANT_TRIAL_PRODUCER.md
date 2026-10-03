# Kamień milowy — producent pakietu próbnego z wariantami

Repo: jakamilek/CleverKeys-langpack-pl.
[Zapis drugiego repozytorium](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-03_VARIANT_TRIAL_PRODUCER.md).

Data: 2026-10-03 UTC. Status: część langpacka wdrożona na gałęzi i sprawdzona w CI; runtime pozostaje niewdrożony.

## 1. Zweryfikowany baseline
Main przed dokumentacyjnym zapisem:
- CleverKeys-langpack-pl: 9b24a94215bbb6d9fee47f794fac40346bef0c01.
- CleverKeysPL: 0da41d8951f96b9dab4e9fb219da5e4924aa66b6.
Punktem wejścia był GEOMETRIC_IMPLEMENTATION_PATH. Nie promowano kodu ani nie scalono PR-ów.

## 2. Stan architektury
Geometric pozostaje wybraną podstawą PL. Pakiet trial dodaje language-intelligence.json zgodny z polami kapitalizacji API v1. Jeden surfaceKey, canonicalForm i potwierdzone warianty. Raw kategorie/interpretacje/form proofs/source records w metadata.sourceEvidence; proweniencja zachowana na poziomie dokumentu.
Manifest deklaruje lexicon, frequency, capitalization, metadata; nie deklaruje nieeksportowanych neutralnych morphology/features lub pełnego common_noun/proper_name.
Importer/provider/pasek Androida nadal nie konsumują tej warstwy.

## 3. Ustalenia i wykonane prace
Użytkownik autoryzował rozpoczęcie etapu 1. Wdrożono scripts/build_variant_trial.py i 21 testów; istniejący pełny CKDT i unigrams nie zmieniane.
Źródłowa fixture z freeze e654720e5bcbe9825747b74df2b7d82cdfac4eaa, zachowana z wynikiem 90b836adb4970c3fcc1cf44bbbc3a2ea45e2da52. Nie wykonano nowej inferencji ani ręcznych opisów.
Trial: 106363 klucze CKDT, 9 wpisów dodatkowej wiedzy, 8 par i jednowariantowy łódzki, 39 interpretacji i 83 dowody form. Lista obejmuje jagoda, malina, polska, róża, warszawska, warszawski, łodzi, łódzki, łódź.
Zachowano pełne dane źródeł i notę atrybucji. Brak wymyślonego surname Łódzki/street.

## 4. Odrzucone lub odłożone
Nie dodawano kopii uppercase do CKDT. Nie stosowano AI/NLI ani zmian CTC. Nie ogłaszano gotowej funkcji Androida.
Nie zastępowano obecnego production preview małym trialem; producent korzysta z jawnie pinned historycznego artefaktu i fail-closed na zmianie hash.
Nie omijano wymogu Gemini/PAL z runtime REPO_INSTRUCTIONS. Nie zmieniono wykonawczej architektury klawiatury.

## 5. Planowane, niewdrożone
Runtime: walidowana instalacja sidecara, parser/immutable provider, rozwinięcie top lexical key na dwie formy, dokładny wybór powierzchni z zastąpieniem swipe tokenu.
Konkretny zakres i scenariusze: CleverKeysPL docs/plans/source-casing-variants-v1.md na gałęzi docs/source-variants-integration-v1. Propozycje Shift/autocap/Caps Lock pozostają do przeglądu.
Pełny eksport całego słownika, fleksyjna edycja Łódźi→Łodzi, AI/interpunkcja pozostają kolejnymi etapami.

## 6. Niezweryfikowane
Brak Androidowych testów, APK, instalacji na telefonie lub prawdziwych swipe. Nie mierzyć tych wyników jako top3/accuracy. Stary runtime nie włączy wariantów po samym imporcie triala.
Brak konsultacji Gemini/PAL: przeszukano dostępne narzędzia, nie ma takiej zdolności w sesji. Wymagane rozstrzygnięcie użytkownika dotyczy konkretnej integracji, nie ponownej zgody na cały projekt.
To nie nowy build main vocabulary; brak pełnego eksportu wszystkich interpretacji dla 100k.

## 7. Gałęzie i PR-y
- Langpack feature/source-variants-trial-v1, commit e970d209ec0c10fe7733cdb80f61a3bc155a1f00, tree 8cfdf41b73d2b07e86b44526a8a3263a6c6be280: [Draft PR #5](https://github.com/jakamilek/CleverKeys-langpack-pl/pull/5), implementacja producenta.
- Runtime docs/source-variants-integration-v1, commit c40798d2042baf4db6edc63a3944376775e85243: [Draft PR #1](https://github.com/jakamilek/CleverKeysPL/pull/1), tylko propozycja integracji.
- Experiment/context-surface-window-v1 / Draft PR #4 nadal historyczny eksperyment offline, bez merge. Inne historyczne role wg wcześniejszych milestone'ów.

## 8. Artefakty, SHA i walidacja
Trial oparty na preview run36916501466/artifact11189614575/source a1fa0193fc504e5fe81d9d43c23fd9a1e52ad307.
- Input source fixture SHA256: 6bbdf928c338d44ab3eddb76f8a1fe9f0b4a789cb1d51f55740f55826a21e2e2.
- Base ZIP: 301b0b9c7c4c7b96ac7a2545bf27745b6ee38c87f5d04133ede490008d861945.
- Trial ZIP: 4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7.
- Sidecar SHA256: e0a878249f021eff00eeb11165f600720f9d5fe24f383c9063e1b91c2a589a54, 24683 bajty.
- Dictionary SHA256: 087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20, identyczny bazowy/trial.
- Unigrams SHA256: de64baefedba0f4da8a4f50e41fa431a92dd3241133cd5825d965fe84e5818c0, identyczny bazowy/trial.
ZIP zawiera NOTICE.txt, dictionary.bin, language-intelligence.json, manifest.json i unigrams.txt. Trial package version3, API1, nie release.
21/21 testów stdlib PASS lokalnie. Realny build i odczyt ZIP PASS. Testowane source associations/hash/dedup/missing key/unsupported schema/duplicate JSON/invalid archive/truncated CKDT/deterministic rebuild.
CI push37106034633 i PR37106069627 completed/success. [Artefakt11267842273](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37106034633/artifacts/11267842273), cleverkeys-pl-variants-trial.
Artefakt CI pobrany i sprawdzony: report CI dokładnie zgodny z lokalnym, ZIP/sidecar/dictionary/unigrams hashes sprawdzone, sidecar wewnątrz pakietu równy osobnemu plikowi.
Wszystkie 9 plików commitowego producenta odczytane z pinned Git i zgodne z lokalnymi; dokument propozycji runtime także readback zgodny.
Raport i sidecar zapisane w docs/variant-trial-v1 na gałęzi producenta. Powtarzalność ZIP sprawdzona w tym samym środowisku Python/zlib, nie deklarować cross-version compression identity.

## 9. Granice i blokada runtime
memory/REPO_INSTRUCTIONS.md mówi: "Make architectural changes" — NEVER "without consulting Gemini 3 Pro via PAL MCP first" oraz wymaga konsultacji przy security-sensitive changes. Walidacja importera i nowa warstwa danych dotyczą tego wymogu.
[Dokładny obowiązujący plik](https://github.com/jakamilek/CleverKeysPL/blob/0da41d8951f96b9dab4e9fb219da5e4924aa66b6/memory/REPO_INSTRUCTIONS.md).
Nie otrzymano automatycznego rejection; problemem jest brak wymaganego narzędzia konsultacyjnego. Przygotowano samodzielnie wykonalny producent i konkretny zakres Androida przed pytaniem o odstępstwo. Brak zgody na odstępstwo w chwili tego zapisu.
Pozostałe luki i wymagania wg GEOMETRIC_IMPLEMENTATION_PATH pozostają obowiązujące. Nie usuwać geometric/CTC ani nie zmieniać defaultów jako część triala.

## 10. Następny krok
Uzyskać wymaganą konsultację PAL lub jawne odstępstwo użytkownika dla tej integracji. Następnie wdrożyć przedstawiony importer/provider/wybór powierzchni na osobnej gałęzi runtime, uruchomić właściwe testy pure/mock i real InputConnection. Nie kończyć etapu 1 na samym JSON — całość wymaga działającej klawiatury.

## 11. Delta
Wcześniej istniał kontrakt i plan. Teraz istnieje sprawdzony producent realnego pakietu trial, manifest/SHA/atrybucja, 21 testów, automatyczny build/artifact, dwa draft PR-y i konkretna propozycja Androida. Integracja runtime jawnie oczekuje spełnienia instrukcji repozytorium, nie jest uznana za wykonaną.
