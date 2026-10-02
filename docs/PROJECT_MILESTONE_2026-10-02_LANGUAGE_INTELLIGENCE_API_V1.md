# Kamień milowy — finalizacja Language Intelligence API v1

**Data:** 2026-10-02  
**Typ:** decyzja architektoniczna + audyt danych  
**Poprzedni kamień:** `docs/PROJECT_MILESTONE_2026-10-02_RUNTIME_LANGPACK_AUDIT.md`  
**Następny etap:** implementacja producenta danych inteligencji

## 0. Zweryfikowany stan

Po zapisaniu finalnego kontraktu bieżący `main`:

- `jakamilek/CleverKeysPL`: HEAD `e26d70da385e20a175ecf9e1884233746587ca3d`
- `jakamilek/CleverKeys-langpack-pl`: HEAD `168f1f83a7df49e572518f1c87037485bc5bee5d`

W tym etapie zmieniono wyłącznie dokumentację.

## 1. Potwierdzone źródła danych

Pipeline PL rzeczywiście posiada dane potrzebne do przyszłego sidecara:

- Morfeusz 2 / SGJP;
- NKJP1M;
- AOSP LatinIME;
- Hunspell;
- TERYT SIMC/TERC;
- KSNG;
- audyty kapitalizacji;
- audyty nazw własnych;
- ręcznie zweryfikowane wpisy.

Ważne rozróżnienie:

**źródło referencyjne („oracle”) nie jest automatycznie danymi runtime.**

Runtime otrzymuje dopiero zweryfikowany wynik.

## 2. Co dziś przechodzi do CKDT

Do CKDT V2 trafia finalna powierzchnia słownikowa oraz ranga częstotliwości.

Nie przechodzą jako osobne rekordy:

- canonicalForm;
- morfologia;
- commonNoun;
- properName;
- lista wariantów casingowych;
- metadata/proweniencja.

## 3. Finalny kontrakt danych

Dokument:

`docs/LANGUAGE_INTELLIGENCE_API_V1_FINAL_2026-10-02.md`

Nowy opcjonalny plik:

`language-intelligence.json`

Minimalny rekord obejmuje:

- `surfaceKey`;
- opcjonalny `canonicalForm`;
- opcjonalną `capitalization` z wariantami;
- opcjonalne `commonNoun`;
- opcjonalne `properName`;
- opcjonalną `morphology`;
- opcjonalne `metadata`.

Frequency pozostaje logicznie częścią API, ale może być pobierane z CKDT zamiast duplikowane w sidecarze.

## 4. Reguły PL

Utrwalono jako dane wynikowe:

- common noun > proper name;
- przymiotniki lowercase;
- dual-casing jako wiele powierzchni jednego klucza;
- `Łódź` / `łódź` jako jedna tożsamość powierzchniowa dla warstwy casingowej;
- `Tomaszów` jako powierzchnia kapitalizowana;
- formy typu `mazowiecki`, `warszawski` jako lowercase.

To są reguły produkcyjne wynikające z audytów, a nie heurystyka runtime.

## 5. Manifest

Nowy pakiet PL ma docelowo deklarować:

- `apiVersion=1`;
- capability;
- plik inteligencji;
- schemaVersion;
- SHA256.

Istniejąca wersja pakietu nadal opisuje dane pakietu.

## 6. Deterministyczność

Sidecar musi być:

- deterministyczny;
- UTF-8;
- stabilnie uporządkowany;
- hashowalny;
- dołączany do deterministycznego ZIP-a.

## 7. Coverage

Capability oznacza, że typ informacji jest obsługiwany; nie oznacza automatycznie pełnego pokrycia całego słownika.

Build powinien raportować co najmniej:

- liczbę rekordów sidecara;
- liczbę rekordów z canonicalForm;
- liczbę rekordów z morphology;
- liczbę rekordów z capitalization;
- liczbę commonNoun/properName;
- liczbę dual-casing;
- konflikty;
- wpisy bez rozstrzygnięcia.

## 8. Legacy i fallback

Nie zmieniamy CKDT V2.

Pakiet legacy nadal jest prawidłowy.

Nowe capability są dodatkiem. Brak capability nie oznacza fałszu.

## 9. Odrzucone kierunki

Nie:

- pakujemy Morfeusza/Hunspell do aplikacji;
- nie przenosimy źródeł referencyjnych jako zależności runtime;
- nie duplikujemy całych 100k słów wyłącznie dla sidecara;
- nie mieszamy UserDictionary;
- nie zmieniamy jeszcze wag scoringowych.

## 10. Niezaimplementowane

Do wykonania:

1. generator sidecara z istniejących wyników audytów;
2. walidator sidecara;
3. rozszerzenie manifestu generowanego przez `build_langpack.py`;
4. testy deterministyczności;
5. testy kompletności i konfliktów;
6. dopiero później integracja z runtime.

## 11. Różnica względem poprzedniego kamienia

Wcześniej wiedzieliśmy, że brakuje warstwy inteligencji.

Teraz dokładnie wiemy:

- które dane istnieją;
- gdzie powstają;
- które trafiają do CKDT;
- które są dziś tracone;
- jak będą przenoszone bez naruszania CKDT.

## 12. Następny etap

Najbliższy etap jest po stronie producenta danych:

**zbudować pierwszy deterministyczny `language-intelligence.json` z bieżących, zweryfikowanych wyników audytów — bez zmiany reguł selekcji 100k core.**

Po jego zbudowaniu utworzyć kolejny kamień milowy w obu repozytoriach.
