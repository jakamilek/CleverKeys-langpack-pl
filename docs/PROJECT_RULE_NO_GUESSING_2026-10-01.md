# ZASADA ZERO DOMYSŁÓW — CleverKeys Polish Language Pack

Data: 2026-10-01

## Cel

Chronić ciągłość projektu przed błędnym odtwarzaniem kontekstu między oknami czatu, instancjami i migracjami.

## Reguła nadrzędna

**NIE WOLNO ZGADYWAĆ.**

Jeżeli informacja potrzebna do wykonania zadania nie jest jednoznacznie potwierdzona w aktualnym stanie GitHub, w obowiązującym promptcie/handoffie albo wprost przez użytkownika, nie wolno jej uzupełniać przez skojarzenie, podobieństwo, pamięć modelu ani prawdopodobieństwo.

Dotyczy to w szczególności:
- nazwy repozytorium;
- właściwego forka;
- gałęzi;
- SHA commitów;
- ścieżek plików;
- wersji runtime;
- statusu CI;
- przeznaczenia repozytorium;
- aktualnych decyzji projektowych;
- źródeł danych;
- założeń dotyczących zmian użytkownika.

## Procedura przy braku pewności

1. **STOP przed działaniem.**
2. Sprawdź informację w GitHubie lub w najnowszym obowiązującym dokumencie projektu.
3. Jeżeli istnieją sprzeczne informacje, nie wybieraj jednej na podstawie podobieństwa. Ustal stan z aktualnego GitHub HEAD i jawnie wskaż konflikt.
4. Jeżeli nie da się potwierdzić informacji, oznacz ją jako **NIEZNANA** i nie wykonuj operacji zależnej od tej informacji.
5. Nie używaj innego repozytorium jako zamiennika tylko dlatego, że ma podobną nazwę, historię albo zawartość.
6. Nie przedstawiaj przypuszczenia jako faktu.

## Źródło prawdy

Dla kodu i stanu projektu obowiązuje GitHub jako oficjalny baseline.

Przed rozpoczęciem pracy należy zweryfikować:
- aktualny HEAD odpowiedniej gałęzi;
- właściwe repozytorium;
- obowiązujące dokumenty handoff/prompt;
- relevantne committy i artefakty, gdy zadanie ich dotyczy.

Pamięć rozmowy może pomóc wskazać, **co sprawdzić**, ale nie może zastąpić weryfikacji.

## Reguła ochronna dla repozytoriów

Nigdy nie wolno przechodzić automatycznie:
- z jednego repozytorium CleverKeys do innego;
- z upstreamu do forka;
- z jednego forka użytkownika do innego;
- z jednej gałęzi do innej;

na podstawie podobieństwa nazwy lub wcześniejszego, niezwiązanego eksperymentu.

**Każde repozytorium robocze musi być jednoznacznie potwierdzone.**

## Reguła ochronna dla niepewności

Preferowany komunikat wewnętrzny decyzji:

> „Nie mam potwierdzenia tej informacji. Najpierw ją sprawdzam.”

Nigdy:

> „Prawdopodobnie chodzi o …”

gdy od tej informacji zależy działanie w repozytorium lub zmiana projektu.

## Migracje

Każdy kolejny prompt migracyjny musi zawierać tę zasadę albo jednoznaczne odwołanie do tego dokumentu.

Zasada obowiązuje również wtedy, gdy wcześniejszy prompt zawiera informację wyglądającą na kompletną, ale aktualny GitHub jej nie potwierdza.

## Wymóg audytowalności

Jeżeli model popełni błąd wynikający z niezweryfikowanego założenia, należy:
- nie maskować błędu;
- nie kontynuować na jego podstawie;
- skorygować stan GitHub, jeżeli został błędnie zapisany;
- pozostawić krótki, jednoznaczny ślad korekty w dokumentacji projektu.
