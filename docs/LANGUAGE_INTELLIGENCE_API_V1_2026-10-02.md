# Language Intelligence API v1 — kontrakt danych pakietu językowego

**Status:** propozycja architektoniczna do implementacji po akceptacji kontraktu
**Data:** 2026-10-02

## 1. Rola pakietu
`CleverKeys-langpack-pl` jest dostawcą wiedzy językowej dla uniwersalnego runtime CleverKeys. Pakiet nie implementuje runtime ani drugiego mechanizmu rerankingu.

## 2. Kontrakt wersjonowany
Artefakt deklaruje: kod języka, opcjonalny tag językowy, wersję pakietu, wersję Language Intelligence API, listę capability („obsługiwanych możliwości”) oraz identyfikację/proweniencję artefaktu.

## 3. Minimalne capability v1
- lexicon — słownik
- frequency — częstotliwość/priorytet
- morphology — informacja morfologiczna
- capitalization — wiedza o preferowanej kapitalizacji
- common_noun — wiedza o rzeczownikach pospolitych
- proper_name — wiedza o nazwach własnych
- metadata — metadane językowe

Pakiet deklaruje tylko capability, które rzeczywiście dostarcza.

## 4. Rekord kandydata
Logicznie API musi móc odpowiedzieć na pytanie o już istniejącą formę: surface, canonicalForm, frequency, morphology, capitalization, commonNoun, properName — zależnie od dostępności.
To model logiczny, nie nakaz konkretnego pliku ani formatu serializacji.

## 5. Kapitalizacja — reguły polskie
Dane muszą umożliwiać rozróżnienie form preferowanych małą literą, wielką literą oraz form posiadających równocześnie znaczenie pospolite i własne.
Rzeczownik pospolity ma pierwszeństwo przed sygnałem nazwy własnej. Przymiotnik nie może być automatycznie zapisywany wielką literą wyłącznie dlatego, że występuje w nazwie własnej.

## 6. Morfologia
Pakiet powinien przekazywać wynik zweryfikowanego procesu językowego. Runtime nie powinien być uzależniony od Morfeusza, Hunspell ani innych narzędzi użytych podczas budowania pakietu.

## 7. Context reranking
Pakiet dostarcza wiedzę o kandydacie. Runtime decyduje, jak użyć tej wiedzy w istniejącym context rerankingu. Pakiet nie generuje kandydatów i nie implementuje drugiego rerankera.

## 8. Fallback
Brak capability jest stanem dozwolonym. Brak informacji nie może być automatycznie interpretowany jako false, jeśli semantycznie oznacza „nie wiadomo”.

## 9. Separacja źródeł
Oficjalne dane pakietu muszą być odróżnialne od Android UserDictionary, custom words i innych źródeł runtime.

## 10. Poza zakresem przed audytem
Nie ustalamy jeszcze konkretnego schema plików, nazw plików, wag, scoringu, nowych klas runtime ani formatu binarnego. Najpierw mapujemy istniejące dane i określamy najmniejszą zmianę kompatybilną z obecnym artefaktem.

## 11. Warunek implementacji
Przed zmianą generatora pakietu należy zweryfikować obecny manifest, wszystkie artefakty językowe, źródła morfologii, capitalization/proper-name, proces budowania i deterministyczność ZIP oraz kompatybilność z obecnym runtime.

## 12. Reguły procesu
GitHub jest źródłem prawdy. ZERO DOMYSŁÓW. ACTION FIRST. Repozytoria pozostają oddzielne. Żaden eksperymentalny branch nie staje się źródłem prawdy.