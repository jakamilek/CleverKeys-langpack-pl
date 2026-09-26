# Kapitalizacja rdzenia i nazw wieloczłonowych — polityka 2026-09-26

## Cel

Kapitalizacja jest właściwością leksykalnej powierzchni słowa, a nie skutkiem przynależności do modułu ani obecności klucza w niezmiennym rdzeniu 100 000.

Przyjęty przepływ:

source -> pełna powierzchnia -> człony -> analiza leksykalna -> rejestr powierzchni -> CKDT

## 1. Rdzeń 100 000

Rdzeń pozostaje niezmienny pod względem członkostwa: dokładnie 100 000 kluczy case-insensitive („niezależnych od wielkości liter”).

Po zbudowaniu rdzenia, a przed złożeniem modułów, uruchamiany jest `scripts/audit_core_capitalization.py`.

Audyt nie zmienia członkostwa rdzenia. Może jednak ustalić poprawną kanoniczną powierzchnię istniejącego klucza, jeśli niezależne źródła wskazują kapitalizację.

Najważniejsza reguła: obecność klucza w rdzeniu nie jest dowodem na małą literę.

## 2. Rzeczownik pospolity jest sprawdzany niezależnie od rdzenia

Każdy kandydat do kapitalizacji jest sprawdzany niezależnie pod kątem zwykłego użycia leksykalnego przez Morfeusz 2 / SGJP.

Przykłady:

- `Łódź` oraz `łódź`: wspólny klucz, ale rzeczownik pospolity wymusza rozstrzygnięcie na rzecz `łódź` w słowniku słów.
- `Malina` oraz `malina`: analogiczny konflikt nazwa własna / rzeczownik pospolity.
- `Tomaszów`: brak wykrytego rzeczownika pospolitego; nazwa własna może więc być przechowywana jako `Tomaszów`.

Jeśli konflikt nie jest jednoznaczny, CI („ciągła integracja”) blokuje promocję zamiast zgadywać.

## 3. Nazwy wieloczłonowe

Pełne nazwy wieloczłonowe i nazwy z łącznikiem nie są odrzucane tylko dlatego, że nie są pojedynczym słowem.

Warstwa źródłowa przechowuje pełną nazwę oraz jej pochodzenie. `scripts/surface_components.py` rozbija ją następnie na człony słowne do analizy.

Każdy człon jest rozpatrywany osobno pod kątem:

- powierzchni źródłowej i jej kapitalizacji;
- funkcji leksykalnej;
- rzeczownika pospolitego lub innej zwykłej funkcji językowej;
- konfliktu z innymi źródłami;
- jawnej polityki powierzchniowej, jeżeli automatyczne rozstrzygnięcie nie jest bezpieczne.

Przykład `Tomaszów Mazowiecki`: pełna nazwa pozostaje w źródle, a `Tomaszów` i `Mazowiecki` są osobno analizowane. Pozwala to wykryć błąd `tomaszów` w rdzeniu nawet wtedy, gdy osobny moduł nie zostałby nigdy dodany do finalnego słownika.

## 4. Wszystkie moduły korzystają z tej samej zasady

Dotyczy to imion, miast, TERC, państw, stolic i przyszłych modułów.

Moduł może wnosić pełne nazwy wieloczłonowe jako dowód i pochodzenie, ale CKDT pozostaje słownikiem powierzchni słów. Dlatego jego finalny klucz jest tworzony na poziomie członu, a nie pełnej frazy.

Nie wolno używać faktu, że dany moduł nie został dodany, jako powodu do rezygnacji z jego informacji ortograficznej na etapie audytu rdzenia.

## 5. Test telefonu jest próbką, nie mechanizmem odkrywania zasad

Każdy błąd znaleziony na telefonie traktujemy jako sygnał klasy problemów.

Przykład `Łódź` nie oznacza tylko poprawki dla jednego klucza. Uruchamia analizę całego wzorca nazwa własna <-> rzeczownik pospolity w rdzeniu oraz we wszystkich źródłach modułowych.

Testowanie ręczne służy do wykrywania zachowania silnika swipe („pisania gestem”), ale nie może być jedynym mechanizmem wykrywania błędów danych.

## 6. Nazwy z końcowym apostrofowym \'s

Tokenizer komponentów usuwa końcowe angielskie \'s z nazw międzynarodowych przed utworzeniem powierzchni słownikowych. Dzięki temu np. `John's` daje komponent `John`, a nie spurious token `s`. Pełna nazwa źródłowa nadal pozostaje zachowana dla pochodzenia i audytu. Apostrofy wewnętrzne pozostają separatorami komponentów.

## 6. Ograniczenie modelu CKDT

CKDT przechowuje jedną kanoniczną powierzchnię dla jednego klucza case-insensitive.

Nie można więc jednocześnie przechować `Łódź` i `łódź` jako dwóch niezależnych wpisów.

Jeżeli jeden klucz ma jednocześnie użycie pospolite i własne, końcową powierzchnię ustalamy jako decyzję leksykalną, zachowując pełne dowody i kontekst w rejestrze oraz artefaktach audytowych.

## 7. Źródła

Oficjalne źródła geograficzne są traktowane jako dowód nazwy własnej i jej oficjalnej postaci. RJP publikuje zasady pisowni nazw własnych, w tym wielowyrazowych nazw geograficznych, których kapitalizacja zależy od rodzaju konstrukcji; dlatego nie stosujemy mechanicznej reguły „każdy człon wielką literą”.
