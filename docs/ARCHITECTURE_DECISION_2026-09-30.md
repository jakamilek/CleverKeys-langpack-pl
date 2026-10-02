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

## Status bieżący

Poprzedni zielony checkpoint miał 105703 unikalne klucze. Późniejsza diagnostyka ujawniła dwa rozłączne problemy: brak wspólnej warstwy NKJP1M w audycie modułów oraz nadmiernie optymistyczne oczekiwanie kapitalizacji `warszawa`.

Aktualne zasady są następujące:
- jeśli Morfeusz/SGJP potwierdza `nazwa_pospolita`, wynik pozostaje lowercase bez względu na źródło modułowe;
- dla luk lingwistycznych oficjalna pisownia źródłowa może dostarczyć późny fallback ortograficzny;
- rdzeń i moduł korzystają z tego samego niezależnego resolvera, więc wspólny klucz nie powinien generować konfliktu tylko dlatego, że surowe źródła mają różne wielkości liter;
- pełne powierzchnie z rozpoznanym łącznikiem pozostają równolegle z komponentami.

Przypadek `warszawa` jest obecnie testowany jako lowercase, ponieważ bieżący resolver wykrywa analizę `nazwa_pospolita`.

Ten dokument zastępuje wcześniejsze interpretacje, w których moduły były traktowane jako potencjalne źródło decyzji kapitalizacyjnej rdzenia albo pełna nazwa z łącznikiem była zastępowana samymi komponentami.


## Doprecyzowanie po diagnostyce CI — 2026-09-30

Najnowsza diagnostyka resolvera potwierdziła, że dla klucza `warszawa` Morfeusz/SGJP znajduje analizę oznaczoną `nazwa_pospolita`. Zgodnie z twardą regułą projektu daje to kanoniczną powierzchnię `warszawa`, nawet jeżeli źródła miejskie zawierają nazwę własną `Warszawa`. Nie jest to wyjątek dla Warszawy, lecz konsekwencja ogólnej reguły pierwszeństwa zweryfikowanej nazwy pospolitej.

Wniosek architektoniczny:
- nazwa własna w module nie może przełamać zweryfikowanej analizy `nazwa_pospolita`;
- `official_source_policies` są wyłącznie późnym fallbackiem ortograficznym dla luk lingwistycznych;
- wspólny klucz rdzeń/moduł musi po zastosowaniu tych samych reguł dawać tę samą powierzchnię;
- regresja dla `warszawa` powinna więc wymuszać lowercase, a nie kapitalizację.

Ta decyzja zastępuje wcześniejszy przykład zakładający `warszawa -> Warszawa` bez uwzględnienia nadrzędnej analizy `nazwa_pospolita`.


## Nowy kierunek analizy homonimii kapitalizacyjnej — 2026-10-01

Rozmowa o `Warszawa` ujawniła, że sama reguła „istnieje analiza `nazwa_pospolita` -> lowercase” jest zbyt uboga semantycznie dla powierzchni, dla której Morfeusz równocześnie pokazuje konkurencyjny leksem własny. Dla `warszawa` CI wykazało zarówno analizę `warszawa + nazwa_pospolita`, jak i `Warszawa:Sf + nazwa_geograficzna`.

Priorytetem staje się minimalizacja obciążenia użytkownika, ponieważ słownik nie zna pełnego kontekstu zdania. Rozważany jest więc model przechowywania obu wariantów kapitalizacji dla rzeczywistych homonimów, tak aby użytkownik mógł wybrać właściwą powierzchnię z podpowiedzi bez ręcznej edycji już wpisanej pierwszej litery.

Pomiar musi być wykonywany wyłącznie na immutable 100k core i niezależnym Morfeuszu/SGJP, bez używania modułów jako źródła kwalifikacji. Pierwszy poprawiony audyt definiuje kandydata wąsko: rzeczownik `subst:sg:nom` z analizą `nazwa_pospolita` oraz równoległą analizą rzeczownikową `subst:sg:nom` z nie-pospolitą klasą własną. Odmiana i przypadki inne niż mianownik są wyłączone.

Uwaga korekcyjna: wcześniejszy wynik 11 499 nie pochodził jeszcze z tego zawężonego audytu mianownika; był wynikiem szerszej diagnostyki opartej na dowolnych analizach rzeczownikowych Morfeusza i obejmował także liczne formy/klasy własne. Nie jest to liczba kandydatów do dwóch powierzchni. Ścisły audyt opisany powyżej został dodany do CI i jego wynik należy pobrać z nowego runu Preview #369.

Nie wolno zakładać, że samo zapisanie `Malina` + `malina` albo `Łódź` + `łódź` rozwiąże problem. W przypiętym runtime CleverKeys istnieją mechanizmy case-insensitive „bez rozróżniania wielkości liter” i testy deduplikujące równoważne kandydaty, więc możliwość pokazania obu powierzchni jednocześnie musi zostać zweryfikowana na rzeczywistym CKDT/runtime.

Do czasu zakończenia tego pomiaru i testu runtime nie należy zmieniać ogólnej reguły kapitalizacji rdzenia ani dodawać ręcznych wyjątków dla `Warszawa`, `Łódź` lub `Malina`.
