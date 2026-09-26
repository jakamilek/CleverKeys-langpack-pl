# CHAT HANDOFF — CleverKeys-langpack-pl — 2026-09-26

## Cel dokumentu

Ten dokument jest obowiązkowym punktem synchronizacji przy przechodzeniu do kolejnego okna czatu lub innej instancji SI. Nie wolno rozpoczynać pracy od początku. GitHub pozostaje jedynym źródłem prawdy projektu.

## Projekt

Repozytorium:

`jakamilek/CleverKeys-langpack-pl`

Branch roboczy:

`ops/baseline-sync-2026-09-20`

Założenia nienaruszalne:

- rdzeń CKDT = dokładnie 100 000 słów, case-insensitive (niezależnie od wielkości liter),
- GitHub jest jedynym baseline (punktem odniesienia),
- nie wykonywać automatycznego merge/promote niezweryfikowanych zmian,
- każda istotna decyzja ma być zapisana w GitHub,
- provenance (pochodzenie danych) musi być audytowalne.

## Najważniejsza nowa decyzja architektoniczna: kapitalizacja

### Zasada nadrzędna

CKDT nie jest słownikiem semantycznym ani składniowym. Silnik wybiera powierzchnie słów i nie analizuje części mowy ani kontekstu zdania.

Dlatego do obecnego słownika nie zapisujemy oficjalnej pisowni źródła bez analizy ortograficznej.

Podstawą jest:

**kanoniczna podstawowa forma ortograficzna słowa według zasad języka polskiego, a nie kategoria źródła.**

## Hierarchia decyzji

1. Reguły języka polskiego dotyczące podstawowej formy słowa.
2. Audyt kapitalizacji rdzenia 100 000.
3. Konflikty mała/wielka litera.
4. Moduły źródłowe (imiona, miasta, TERC, państwa itd.).
5. Budowa CKDT.

## Rdzeń jako pierwsza prawda

Jeżeli słowo istnieje w rdzeniu i posiada decyzję kapitalizacji:

- moduł nie może zmienić tej decyzji,
- moduł może jedynie dostarczyć informację kontrolną,
- audyt modułu jest drugą warstwą ochronną.

## Ważna reguła dla przymiotników

Sam fakt występowania słowa w nazwie własnej nie oznacza wielkiej litery.

Przykład:

`Tomaszów Mazowiecki`

Dla CKDT analizujemy słowa:

- Tomaszów — nazwa własna rzeczownikowa → Tomaszów,
- mazowiecki — przymiotnik od Mazowsze → mazowiecki.

Nie zapisujemy automatycznie `Mazowiecki`, tylko dlatego że pochodzi z nazwy miasta.

Ta zasada dotyczy wszystkich modułów.

Przykładowe klasy:

- mazowiecki,
- pomorski,
- śląski,
- krakowski,
- warszawski.

## Nazwy wieloczłonowe

Każdy człon musi być analizowany osobno, ale bez budowania pełnej gramatycznej reprezentacji w obecnym CKDT.

Obecny słownik potrzebuje poprawnej powierzchni słowa.

## Przyszły etap rozwoju (nie obecny CKDT)

Należy zachować jako kierunek rozwoju:

Budowa słownika kontekstowego, który będzie rozróżniał użycie słów zależnie od zdania:

- "Dzisiaj jedziemy do Łodzi" → Łódź jako miasto,
- "Dzisiaj będziemy cumować łódź" → łódź jako rzeczownik pospolity.

Wymagałoby to:

- części mowy,
- analizy składniowej,
- kontekstu,
- modelu predykcyjnego.

Nie jest to część obecnego CKDT.

## Zasada tworzenia kolejnych handoffów

Każdy następny prompt migracyjny musi automatycznie zawierać:

1. aktualny cel projektu,
2. repozytorium i branch,
3. zasadę GitHub jako jedynego źródła prawdy,
4. ostatnie decyzje architektoniczne,
5. nierozwiązane problemy,
6. aktualny etap pipeline,
7. zakaz rozpoczynania pracy od początku,
8. informację, że wcześniejsze ustalenia muszą zostać zachowane i rozszerzane, a nie zastępowane.

---

# Prompt do następnego okna czatu

Kontynuujemy istniejący projekt CleverKeys-langpack-pl.

GitHub jest jedynym źródłem prawdy.

Repo:
`https://github.com/jakamilek/CleverKeys-langpack-pl`

Branch:
`ops/baseline-sync-2026-09-20`

Najpierw sprawdź aktualny HEAD branch, dokumenty handoff oraz GitHub Actions. Nie zaczynaj projektu od początku i nie zakładaj zmian poza GitHub.

Przeczytaj:
- `docs/CHAT_HANDOFF_2026-09-25.md`
- `docs/NEXT_CHAT_PROMPT_2026-09-25.md`
- `docs/CHAT_HANDOFF_2026-09-26_CAPITALIZATION_POLICY.md`

Kontynuujemy budowę polskiego pakietu językowego CleverKeys.

Aktualne nienaruszalne zasady:

- CKDT core = dokładnie 100 000 słów,
- provenance musi być audytowalne,
- nie wykonujemy automatycznych merge/promote,
- każdą istotną zmianę zapisujemy w GitHub.

Najważniejsza decyzja:

Kapitalizacja w CKDT wynika z podstawowej formy ortograficznej słowa, a nie z tego, czy źródłem była nazwa miasta, imię lub inna nazwa własna.

Rdzeń 100k jest pierwszą prawdą kapitalizacji. Moduły są drugą warstwą ochronną.

Przymiotniki i inne części mowy muszą być normalizowane zgodnie z zasadami polskiej ortografii.

Przykład:

Tomaszów Mazowiecki:
- Tomaszów → Tomaszów,
- mazowiecki → mazowiecki.

Nie zapisujemy automatycznie członu wielką literą tylko dlatego, że pochodzi z nazwy własnej.

Kontynuuj od aktualnego stanu kodu i pipeline. Najpierw audytuj stan, potem wykonuj zmiany. Każdą istotną zmianę zapisuj od razu w GitHub.


## Aktualizacja ciągłości — 2026-09-26 18:36 UTC

Stan po wznowieniu migracji kapitalizacji:
- bieżący HEAD branch: `ac169ba3c3d2b591f5f8c29ecea0bdbffaa7a191`;
- commit `3d583b45ad6d401729ece1644dcb25591c136eb3`: usunięto pozostały odwołujący się do nieistniejącej polityki imion parametr `special_policy/name_policy` z `scripts/audit_core_capitalization.py`;
- commit `8de68ba49f0b8ebdd69f6320a850c3adc3b9dddd`: `scripts/build_additive_phone_test.py` stał się resolver-only — nie czyta registry kapitalizacji i nie ma własnego fallbacku lowercase/capitalized; dla klucza module-only wymaga decyzji z `module_capitalization_audit`;
- commit `ac169ba3c3d2b591f5f8c29ecea0bdbffaa7a191`: poprawiono wiring workflow, tak aby registry pozostało wejściem do audytów core/module, ale nie do phone-test buildera.

Stan CI:
- preview #258 na `fb9ce...`: failure; bezpośrednia przyczyna: `NameError: name_policy is not defined` w `audit_core_capitalization.py:154`;
- preview #260 na `8de68...`: cancelled;
- preview #261 na `ac169...`: in_progress;
- size-study #200 na `3d583...`: in_progress.

Nie uznawać projektu za green przed rzeczywistym `conclusion=success` nowych runów. Po green CI sprawdzić świeże artefakty, CKDT, net-new union i kapitalizację regresji. Nie wykonuj merge/promote.
