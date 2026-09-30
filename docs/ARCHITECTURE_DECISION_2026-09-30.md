# Decyzja architektoniczna — 2026-09-30

## Rdzeń 100k i kapitalizacja

Immutable 100k core oznacza niezmienność członkostwa, nie niezmienność powierzchni znakowej. Każdy z 100 000 kluczy rdzenia musi przejść samodzielny proces ustalenia kanonicznej kapitalizacji przed dołączeniem jakiegokolwiek modułu.

Resolver rdzenia nie może wymagać obecności słowa w module. Musi poprawnie rozstrzygać również nazwy własne i inne powierzchnie wymagające wielkiej litery, których nie ma w żadnym aktywnym module. Podstawowym źródłem pozostaje Morfeusz 2 / SGJP, a niezależne dane NKJP1M mogą być wtórną warstwą lingwistyczną resolvera. Moduły nie są źródłem kapitalizacji rdzenia.

Twarda reguła: zweryfikowana nazwa pospolita ma absolutne pierwszeństwo i pozostaje lowercase. Przykłady: malina, łódź. Nie wolno przełamywać tej zasady dlatego, że w module istnieje Malina albo Łódź jako nazwa własna.

## Moduły

Aktywne moduły są dodatkowymi zbiorami słów. Każdy moduł może zawierać słowo:
- którego nie ma w rdzeniu — wtedy jest dodatkiem;
- które już jest w rdzeniu — wtedy nie powstaje drugi klucz case-insensitive;
- które występuje w rdzeniu z inną powierzchnią znakową — wtedy nie wolno automatycznie poprawiać rdzenia danymi modułu.

Wspólny klucz w rdzeniu i module jest okazją do kontroli spójności reguły, a nie do sterowania rdzeniem przez moduł.

## Konflikt rdzeń ↔ moduł

Jeżeli ta sama powierzchnia po niezależnym rozstrzygnięciu daje w rdzeniu i module różne kanoniczne postacie, CI ma zatrzymać pipeline i wskazać konflikt.

Taki konflikt jest sygnałem: naprawić regułę obowiązującą dla całej klasy przypadków, a nie dopisywać ręczny wyjątek dla pojedynczego słowa.

Przypadki świadomie rozstrzygane wspólną regułą, np. common-noun -> lowercase, muszą zostać ocenione przez ten sam resolver po obu stronach. Nie wolno traktować surowej kapitalizacji źródłowej modułu jako konfliktu, jeżeli wspólny resolver prawidłowo sprowadza obie strony do tej samej kanonicznej powierzchni.

## Nazwy z łącznikiem

Nazwy zawierające projektowy łącznik są reprezentowane równolegle:
1. przez komponenty leksykalne — np. kujawsko, pomorskie;
2. przez pełną nazwę z zachowanym łącznikiem — np. kujawsko-pomorskie.

Pełna powierzchnia nie jest zastępowana przez komponenty. Dotyczy to również pełnych form odmienionych, np. kujawsko-pomorskiego, gdy dana kategoria i model gramatyczny przewidują tę formę.

Dla nazw miejscowości analogicznie: Bielsko oraz Bielsko-Biała muszą być dostępne jako osobne klucze. Dzięki temu prefix bielsko może prowadzić do obu powierzchni.

Łącznik sam w sobie nie definiuje gramatyki. Odmiana pełnej nazwy jest generowana według modelu właściwego dla kategorii, a nie przez bezrefleksyjne odmienianie każdego komponentu. Dla województw zachowujemy dotychczasowy model stały pierwszy komponent + odmiana końcowego przymiotnika, np. kujawsko-pomorskiego.

Spacje nie uruchamiają ścieżki hyphenowanej. Jednak jeżeli oficjalna nazwa zawiera zarówno rozpoznany łącznik, jak i spację, pełna oficjalna powierzchnia hyphenowana może być zachowana jako jedna powierzchnia źródłowa; alternatywy rozdzielane przecinkiem nie są automatycznie traktowane jako jedna nazwa.

## Zasada budowania

Kolejność jest twarda:

100k membership → niezależna kapitalizacja rdzenia → niezależna walidacja modułowa → additive union → CKDT

Żaden moduł nie może zmieniać członkostwa 100k ani jego kanonicznej powierzchni. Pełna historia źródeł i audytów pozostaje zachowana.

## Status przed wdrożeniem

Na branchu ops/baseline-sync-2026-09-20 poprzedni zielony checkpoint miał 105703 unikalne klucze, ale ujawnił architektonicznie błędne założenie: obecny core resolver mógł rozstrzygnąć warszawa lowercase, mimo że aktywne źródła modułowe zawierały Warszawa. To nie może być naprawiane wpisem dla Warszawa; trzeba poprawić niezależną regułę resolvera, aby rdzeń sam potrafił skorygować powierzchnię.

Ten dokument supersedes wcześniejsze interpretacje, w których moduły były traktowane jako potencjalne źródło decyzji kapitalizacyjnej rdzenia albo w których pełna nazwa z łącznikiem była zastępowana samymi komponentami.
