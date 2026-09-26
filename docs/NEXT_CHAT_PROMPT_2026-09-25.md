# PROMPT DO NOWEGO OKNA — CleverKeys-langpack-pl — 2026-09-25

Kontynuujemy istniejący projekt **CleverKeys-langpack-pl**. Nie zaczynaj od początku.

## Oficjalny baseline

Repo:
https://github.com/jakamilek/CleverKeys-langpack-pl

Branch:
`ops/baseline-sync-2026-09-20`

GitHub jest jedynym oficjalnym baseline. Wcześniejsze zmiany z innych instancji/Codex traktuj jako materiał migracyjny do audytu. **Nie wykonuj automatycznego merge/promote.** Po każdej istotnej zmianie zapisuj atomowy commit do GitHub.

## Cel projektu

Budujemy kontrolowany polski pakiet językowy dla CleverKeys Android, z priorytetami:
1. bezpieczeństwo źródeł językowych,
2. pełna audytowalność provenance,
3. deterministyczne generowanie,
4. poprawa polskiego swipe typing.

Aktualne testy użytkownika:
- CleverKeys 1.5.0 / build 1.5.0,
- QWERTY (Polski),
- geometric swipe,
- swipe=true,
- autocorrect=false,
- inne słowniki wyłączone.

Główny problem praktyczny: krótkie polskie słowa są czasem wypierane przez zagraniczne nazwy/podobne ścieżki swipe.

## Nienaruszalny rdzeń

Production core = dokładnie **100 000 słów**.

Klucz jest case-insensitive. Ten sam klucz w module i core nie zużywa dodatkowego slotu. Moduły są additive.

Finalna wielkość:
**100 000 + union(net-new module keys)**.

Nie zmieniaj immutable 100k core, aby zrobić miejsce dla modułów.

## Obowiązująca polityka TERC

Dokładnie:
- **16 województw — pełna odmiana**,
- **380 powiatów — odmiana selektywna ze względu na częstość i inne wagi**,
- **2479 gmin — tylko mianownik**.

Pełna odmiana jest artefaktem audytowym. Nie wolno jej utożsamiać z warstwą produkcyjną.

Pliki:
- pełna odmiana: `build/pl-terc-inflections.tsv`
- produkcyjnie wybrana odmiana: `build/pl-terc-inflections-selected.tsv`
- raport selekcji: `build/pl-terc-retention-report.json`
- polityka: `docs/PL_TERC_RETENTION_POLICY_2026-09-25.md`

Skrypty:
- `scripts/fetch_teryt_terc.py`
- `scripts/extract_teryt_terc.py`
- `scripts/generate_terc_inflections.py`
- `scripts/select_terc_inflections.py`

TERC source CI już poprawnie raportował:
16 województw / 380 powiatów / 2479 gmin / 2875 rekordów.

## Zasady selekcji powiatów

Nie ustalaj arbitralnego progu przed pomiarem.

Primary:
- NKJP1M frequency.

Secondary:
- wordfreq jako niezależny sygnał.

Dodatkowe wagi:
- użyteczność gramatyczna,
- case priority,
- pewność źródła.

**Nie twórz sztucznego wspólnego score NKJP + wordfreq.**

Wykluczone formy muszą pozostać w audycie z powodem wykluczenia.

## Znany aktualny problem selektora TERC

Ostatnio naprawiono jego schema validation. Obecny skrypt musi wymagać pól:
`category, name, level, terc, number, case, form, case_policy, source, morfeusz_version`.

Ostatnia poprawka:
`83bdbeeb2d3a63ee1e6e9c4e705528e74eb500ca`

Najnowsze workflow uruchomione na tym SHA:
- Polish language pack preview #167 — in progress,
- Polish dictionary size study #143 — in progress.

**Najpierw sprawdź ich faktyczny wynik.**

## Aktualny stan KSNG / GUGiK

Oficjalny główny PDF KSNG/GUGiK:
197 państw + stolice.

Oficjalny update 1/2026:
Gwinea Równikowa -> Ciudad de la Paz.

Piny:
- main PDF SHA256 = `4645f3f84b46920b7e9bb480a265f70a52da5d429977eb650709d84dfabd08eb`
- update PDF SHA256 = `bd4c8b543e4389163de653f5c26d55dd7db37d989c54d7f102104fb5ecff3c75`

Ekstrakcja KSNG jest już rozwiązana:
- parser odczytuje PDF mimo rotated/font-encoded text,
- poprawiono regex `pol.`,
- dodano PyMuPDF,
- wybrano 197 wpisów po schemacie `pol. … stol.`,
- update PDF jest jednopozycyjną poprawką.

Ostatni poprawny raport:
- country_records = 197
- capital_records = 197
- country_flat_unique = 165
- capital_flat_unique = 164

Nie wracaj do wcześniejszego błędu 0 markerów jako aktualnego.

## Ostatni błąd generatora KSNG

Była wadliwa forma:
`Barbadosie ang. Barbados`

Źródłowa adnotacja została pomyłkowo potraktowana jako jedna forma słownikowa.

To zostało naprawione:
- formy produkcyjne muszą być pojedynczym tokenem,
- nieprawidłowe źródłowe „formy” są wykluczane z warstwy produkcyjnej,
- pozostają w raporcie audytowym.

## Aktywne moduły

1. immutable 100k base,
2. first names,
3. Polish cities/localities,
4. custom/manual,
5. TERC administrative division,
6. countries + capitals.

Plan późniejszy:
controlled brands/trade names.

Nie przywracaj automatycznie wycofanych pilotów:
- `reviewed_proper_nouns`
- `reviewed_morphology`

75 form z dawnego morphology pilot zostało świadomie przeniesionych do:
`sources/staging/custom_manual.tsv`

`custom_manual.tsv` zaczyna się od komentarza:
`# Manual/custom Polish dictionary category.`

Loadery muszą ignorować komentarze przed TSV header.

## First names

Workflow:
`First-name 235-per-gender selection audit`

Docelowy wybór:
- 215 F + 215 M z historii 20-letniej,
- dodatkowo audyt selected-core.

Ostatni znany sukces first-name audit:
run #76 był success przed kolejnymi zmianami.

Nie zakładaj, że historyczny sukces jest nadal aktualny — sprawdzaj najnowszy run.

## Regresje swipe

Chroniona lista obejmuje m.in.:
`chopin, chopina, goebbels, goebbelsa, catherine, catalina, cameron, carli, carlo, castillo, cali, celli, casino, calli, carrillo, caroli, cassino, compos, gourami, celastial`

Przykład z playground:
swipe -> `carli`
ranking był zdominowany przez zagraniczne nazwy.

Nie dodawaj śmieciowych nazw tylko po to, aby zwiększyć recall.

## Źródła/piny

- wordfreq git pin: `912caf64b657478d1ff1138efdc078947d54bb1`
- AOSP Polish dictionary SHA256:
`75a7a488e014ec3b9dbdb2527f09bca6bb28c250232d9ba50cb0ee1f8738ea45`
- Morfeusz2 1.99.15
- polish-inflection 0.7.3
- NKJP1M revision `be02836cf3aa0286ad8961d2e4528cdc2f72d044`
- NKJP1M SHA256 `fee31b1d6a682970b4e8ca68b593aea8dadbc8541e875e2d287480d83601e79c`
- TERC SHA256 `82224d982c965b7f6d20e33e4dbfefbc64af57bcb6c559c7119070a96dc50798`
- SIMC SHA256 `678444fbdcfc631738d8280f78d2edf4b29c489d9e61c28b368907b9e0cab15a`

## Ostatnie problemy CI i ich interpretacja

Poprzednie błędy, już zdiagnozowane:
- KSNG parser: rfind/find sekcji było niewłaściwe — naprawione,
- KSNG update PDF miał tylko 1 wpis — validator dostosowany,
- syntax separator po edycji parsera — naprawione,
- KSNG source annotation typu `Barbadosie ang. Barbados` — naprawione,
- custom_manual komentarz przed headerem — loader został poprawiony,
- CI sprawdzało pełną odmianę krajów zamiast warstwy po retencji — zdiagnozowane i poprawiane,
- size-study miał chwilowo brak pliku NKJP po pobraniu — rozróżniaj awarię infrastruktury od błędu kodu.

Najnowszy stan z 2026-09-25:
- preview #165 / size-study #141 miały problemy związane z dostępnością/pobieraniem NKJP,
- preview #166 / size-study #142 doszły do walidacji i wykazały brak spójności z selected TERC schema,
- poprawka schema jest w SHA `83bdbeeb2d3a63ee1e6e9c4e705528e74eb500ca`,
- najnowsze #167/#143 uruchomiły się ponownie na tym SHA.

## Co zrobić po otwarciu nowego czatu

Nie pytaj użytkownika o historię projektu.

Wykonaj kolejno:
1. Odczytaj ten prompt i `docs/CHAT_HANDOFF_2026-09-25.md`.
2. Sprawdź aktualny stan branch `ops/baseline-sync-2026-09-20`.
3. Sprawdź najnowsze runy #167 i #143 oraz wynik każdego kroku.
4. Zweryfikuj `scripts/select_terc_inflections.py` i jego output.
5. Zwróć szczególną uwagę na to, czy:
   - województwa mają pełną odmianę,
   - gminy tylko nom,
   - powiaty mają selektywną odmianę zgodną z pomiarem.
6. Zachowaj pełny TERC jako audit artifact i selected TERC jako production input.
7. Zmierz rzeczywisty net-new union po wszystkich aktywnych modułach.
8. Dopiero po pomiarze kalibruj selekcję powiatów.
9. Każdą istotną zmianę od razu zapisz na GitHub.
10. Nie wykonuj automatycznego merge/promote.

Najważniejsza zasada:
**kontynuuj od rzeczywistego stanu GitHub, nie od starej pamięci z poprzedniego czatu.**


## Aktualizacja 2026-09-26

Kontynuacja po synchronizacji schematu TERC:
- `2c7c22eb136ec323525cd4e3ad1ccf3d21d7887b`: selector wymaga teraz pełnego 10-polowego schematu TERC.
- `c5cd8b9cf74331ec2e7c24eb2859e495acc7af2d`: preview builder został dostosowany do selected TERC.
- `a5ff83b0a522293aec68c47f74a13277f624e2d4`: generator TERC przestał deduplikować jednostki po nazwie; tożsamość opiera się na `level + terc`.
- preview #170 i size-study #146 działają/oczekują na SHA `a5ff83b0...`; sprawdź ich rzeczywisty wynik przed dalszą decyzją.
- Nie używaj historycznego 2,611 jako aktualnego kosztu modułów.
- Po green CI odczytaj aktualny `module-study-report.json`, `module-frequency-report.json` i artefakty TERC.


## Aktualizacja 2026-09-26 — ostatnie decyzje kapitalizacji i pipeline

Branch roboczy: ops/baseline-sync-2026-09-20
Ostatni commit zmieniający kod: 52aa2abe5d6a7c48cc98288ffe2a382a083c0c5e
Aktualny HEAD branch zawiera późniejsze commity dokumentacyjne; przed pracą sprawdź rzeczywisty HEAD.

Naprawione problemy architektoniczne:
1. surface_components.py usuwa angielski possessive 's / ’s / ＇s jako niefaktyczny komponent CKDT.
2. build_pl_preview.py dodaje source-backed module forms do ranked przed wyliczeniem zipf, spell i rank_of, więc nie ma już KeyError dla prawidłowych nazw modułowych spoza wordfreq.
3. size-study używa tych samych audytów kapitalizacji core/module co production-shaped additive path.
4. audyty kapitalizacji zachowują jawnie audytowaną kapitalizację first-name-inflection przed ogólną regułą common-noun -> lowercase; lowercase_common_noun pozostaje jawnie zdefiniowanym wyjątkiem.

Najważniejszy ostatni błąd:
preview #236 wykazał, że 48 capitalized_homonym_names było obecnych w audycie imion, ale generic capitalization audit obniżał je do lowercase. Nie wolno naprawiać tego 48 ręcznymi wyjątkami. Prawidłowa zasada to pierwszeństwo źródła first-name-inflection przy polityce wyłącznie capitalized.

Nowe CI na bieżącym SHA 52aa2a...:
- preview #238 — in progress;
- size-study #184 — in progress.

First-name audit #96 na poprzednim SHA cc073e... — success.
Size-study #182 na cc073e... — success; net_additions_over_100k_base = 5688. Nie jest to jednak ostateczny wynik kapitalizacji po poprawce imion.

Po otwarciu nowego czatu:
- sprawdź rzeczywisty HEAD branch;
- sprawdź najnowsze CI na 52aa2a...;
- jeżeli którykolwiek run jest failed, analizuj przyczynę architektonicznie;
- jeżeli preview i size-study są green, pobierz/odczytaj aktualne raporty i artefakty;
- następnie zweryfikuj CKDT, net-new union oraz przygotuj dopiero wtedy paczkę do testu swipe;
- nie wykonuj merge/promote.


## Aktualizacja 2026-09-26 — poprawka `Gdynia`

Preview #238 na SHA 52aa2a... zatrzymał się na końcowej asercji `Gdynia`. Diagnoza: ogólny audyt kapitalizacji używał `common_lexical` zbyt szeroko jako podstawy lowercase override.

Naprawa w commit `ae7563140232d7e091d4c95a67288822b9c10ae7`:
- core audit obniża powierzchnię tylko przy rzeczywistej analizie rzeczownikowej z klasą `nazwa_pospolita`;
- module audit analogicznie używa `common_noun` jako podstawy decyzji;
- `common_lexical_matches` pozostaje w raporcie, ale nie jest samodzielnym autorytetem kapitalizacji;
- bez ręcznego wpisu dla Gdynia.

Commit `c9078c6e007e91a768c7f7e7813661c3b6dc2c9c` uruchomił CI na tej zmianie.

Bieżące runy:
- preview #240 na c9078c... — pending;
- preview #239 na ae7563... — in progress;
- size-study #186 na c9078c... — in progress;
- size-study #185 na ae7563... — in progress.

Po green CI koniecznie sprawdź `Gdynia`, `Łódź`, `Tomaszów`, 48 capitalized first-name homonyms oraz 5 lowercase exceptions. Nie traktuj starego #238 jako aktualnego wyniku.


## Aktualizacja 2026-09-26 — przymiotnikowe konflikty kapitalizacji

Najnowszy błąd core audit na `c9078c...` obejmował 17 kluczy przymiotnikowych: `brzeski, chełmiński, gdański, jasielski, lubelski, lubelskie, lubuskie, mazowieckie, mazurskie, opolski, opolskie, pomorskie, sandomierski, wschodni, ząbkowicki, łukowski, łódzki`.

Nie rozwiązywać ich przez 17 ręcznych wpisów. Została dodana architektoniczna reguła `verified-adjective-orthography-lowercase` w obu audytach kapitalizacji:
- core: `adj:` zwykłej analizy Morfeusza może rozstrzygnąć lowercase, z ochroną przed innymi POS;
- module: analogiczna reguła i raportowanie `common_adjective_matches`;
- jawny surface registry pozostaje miejscem dla rzeczywistych konfliktów leksykalnych, nie dla systemowej reguły gramatycznej.

Commity:
- `9f0b45755289c260650c7d4cc2d2f67b4195e9d2` — core audit;
- `88320090cb42cc38ba235c380566f160092925ef` — module audit;
- `20078a8f7deb8246194b336cbc50df1332a55d7e` — handoff update.

Po tych commitach sprawdź nowe CI i oczekuj `unresolved_count = 0` bez ręcznego dopisywania 17 nazw.


## Aktualizacja 2026-09-26 — poprawka błędnej bramki TERC

Preview #242 na `88320090cb42cc38ba235c380566f160092925ef` nie ujawnił nowego błędu CKDT. Wszystkie wcześniejsze etapy przeszły, a końcowa weryfikacja zatrzymała się na asercji wymagającej wszystkich nazw TERC w oryginalnej kapitalizacji.

To był błąd testu: źródłowe `pl-terc-flat.tsv` zawiera jawne `case_policy`, więc nazwy przymiotnikowe/powiatowe mogą poprawnie występować lowercase. Poprawka jest w `345becc1fb2478a0d9a0273136ba0d033a277c3f`: końcowy test wylicza oczekiwaną powierzchnię z `case_policy`, zamiast zakładać kapitalizację każdej nazwy.

Size-study #188 na `8832009...` jest green. Po commitcie `345becc...` trzeba sprawdzić nowy preview na bieżącym HEAD. Nie wolno uznawać projektu za gotowy tylko dlatego, że size-study jest green.

Po green preview odczytaj świeże artefakty, zwłaszcza audyty kapitalizacji, raport modułów, raport TERC i finalny ZIP. Następnie przygotuj dopiero paczkę do testu swipe. Nie wykonuj automatycznego merge/promote.


## Stan ciągłości po ponownym odczycie historii — 2026-09-26

Przed kontynuacją kolejna instancja ma zachować pełną ciągłość z wcześniejszych rozmów: nie zaczynać od zera, nie wracać do starych liczb/runów i najpierw czytać aktualny GitHub. Wcześniejsze materiały potwierdzają m.in. pinned runtime CleverKeys `263bd0abc03dec420f60fa073a9d2c5e25a176b5`, CKDT V2, immutable core 100k, audytowane źródła, morphology/proper nouns, politykę 48 capitalized homonyms + 5 lowercase exceptions, rozdzielenie membership/casing/ranking/swipe oraz test swipe #187.

Najświeższy stan:
- poprawka błędnej asercji TERC: `345becc1fb2478a0d9a0273136ba0d033a277c3f`;
- run size-study #188: success na `88320090...`;
- preview #242: failure wyłącznie w końcowej bramce weryfikacyjnej, ponieważ test ignorował `case_policy` TERC;
- preview #243: działa na `345becc...` i w chwili zapisu nie miał jeszcze konkluzji;
- `8374dae9...` jest późniejszym technicznym commitem workflow, bez zmiany merytorycznej reguły TERC.

Po zakończeniu #243 sprawdź najpierw rzeczywisty wynik i failing step, jeśli wystąpi. Następnie świeże artefakty. Nie traktuj żadnego starego ZIP-a jako finalnego po późniejszych zmianach. Nie wykonuj merge/promote.
