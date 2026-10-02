# Reguła ciągłości projektu — kamienie milowe dla kolejnych instancji

Data ustanowienia: 2026-10-02
Obowiązuje: natychmiast
Zasada nadrzędna: GitHub jest jedynym źródłem prawdy.

## 1. Cel
Kolejna instancja projektu nie ma odtwarzać całej historii z poprzednich rozmów, analizować wszystkich historycznych gałęzi ani polegać na pamięci rozmowy. Stan projektu ma być utrwalany w GitHub jako kamienie milowe.

Kamień milowy jest zatwierdzonym zapisem stanu projektu na konkretny dzień. Ma pozwolić kolejnej instancji wejść w projekt przez lekturę kilku wskazanych dokumentów, zamiast wykonywać ponownie pełny audyt historyczny.

## 2. Obowiązek zapisu w obu repozytoriach
Każdy znaczący etap architektoniczny, audyt, ważna decyzja integracyjna albo zmiana stanu projektu musi otrzymać kamień milowy:
- jakamilek/CleverKeysPL
- jakamilek/CleverKeys-langpack-pl

Dokumenty mogą mieć różne części repozytoryjne, ale muszą wskazywać na siebie i zawierać wspólny stan przekrojowy. Powód: kolejna instancja może rozpocząć pracę od dowolnego z dwóch repozytoriów.

## 3. Co musi zawierać każdy kamień milowy
Każdy dokument musi jednoznacznie podawać:
1. aktualny HEAD main danego repozytorium i datę weryfikacji;
2. aktualny stan architektury;
3. ustalenia zaakceptowane;
4. rozwiązania odrzucone lub porzucone oraz powód;
5. rzeczy będące w planie, ale jeszcze niewdrożone;
6. rzeczy niezweryfikowane;
7. istotne gałęzie historyczne i ich rolę;
8. ważne artefakty, SHA i punkty integracji;
9. aktualne ograniczenia i znane luki;
10. następny uzasadniony krok techniczny;
11. różnicę względem poprzedniego kamienia milowego.

Nie wolno wpisywać przypuszczeń jako faktów. Każda informacja o bieżącym stanie musi być zweryfikowana w GitHub albo wyraźnie oznaczona jako niezweryfikowana.

## 4. Reguła dla kolejnych promptów migracyjnych
Każdy kolejny prompt migracyjny generowany dla nowej instancji musi wskazywać:
- najnowszy kamień milowy w CleverKeysPL;
- najnowszy kamień milowy w CleverKeys-langpack-pl;
- obowiązek przeczytania tych dokumentów przed wykonywaniem nowej analizy.

Prompt ma przekazywać stan, a nie całą historię. Historię należy odtwarzać tylko wtedy, gdy kamień milowy wskazuje konflikt lub wymaga tego nowy etap.

## 5. Reguła tworzenia kolejnego kamienia milowego
Po zakończeniu kolejnego znaczącego etapu instancja ma:
1. zweryfikować stan obu repozytoriów;
2. dopisać nowy kamień milowy w obu repozytoriach;
3. podać zmianę względem poprzedniego;
4. używać nowego kamienia jako pierwszego dokumentu wejściowego w następnym promptcie migracyjnym.

## 6. Kolejność ważności informacji
Przy konflikcie informacji stosować kolejno:
bieżący GitHub -> najnowszy kamień milowy -> aktualne ADR/specyfikacje -> kod i testy bieżącego HEAD -> starsza dokumentacja -> pamięć rozmowy.

Pamięć rozmowy nigdy nie może nadpisać zweryfikowanego stanu GitHub.

## 7. Zasady operacyjne
Obowiązują równolegle:
- ZERO DOMYSŁÓW;
- ACTION FIRST po autoryzacji użytkownika;
- nie scalać repozytoriów;
- nie promować eksperymentalnych gałęzi do main bez osobnej autoryzacji;
- nie usuwać ani nie przepisywać historii bez osobnej autoryzacji;
- zachowywać proweniencję i audyty;
- znaczące zmiany zapisywać w atomowych commitach.

## 8. Trwałość reguły
Niniejszy dokument jest trwałą regułą procesu projektu. Kolejne instancje mają stosować go automatycznie przy tworzeniu i czytaniu promptów migracyjnych.