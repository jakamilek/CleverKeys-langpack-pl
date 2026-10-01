# PROMPT DO NOWEGO OKNA — CleverKeys-langpack-pl — 2026-09-30

Kontynuujemy istniejący projekt CleverKeys-langpack-pl. Nie zaczynaj od początku i nie traktuj starych liczb/runów jako aktualnych bez weryfikacji GitHub.

## Oficjalny baseline

Repo: https://github.com/jakamilek/CleverKeys-langpack-pl
Branch roboczy: ops/baseline-sync-2026-09-20
GitHub jest jedynym oficjalnym baseline. Nie wykonuj merge/promote do main. Zapisuj istotne zmiany w małych atomowych commitach.

## Najważniejsza decyzja z 2026-09-30

### Rdzeń 100k
- Członkostwo immutable 100k jest nienaruszalne.
- Każde słowo rdzenia przechodzi niezależny resolver kapitalizacji PRZED modułami.
- Resolver musi działać także dla słów, których nie ma w żadnym module.
- Moduły nie są źródłem decyzji kapitalizacyjnej rdzenia i nie mogą go korygować.
- Morfeusz 2 / SGJP jest podstawowym źródłem lingwistycznym; NKJP1M może być wtórną warstwą lingwistyczną resolvera.
- Zweryfikowana nazwa pospolita ma absolutne pierwszeństwo: lowercase. Przykłady: malina, łódź.

### Moduły
Moduły są wyłącznie dodatkowymi zbiorami słów. Mogą dostarczać słowa nowe albo pokrywać słowa już znajdujące się w rdzeniu. Wspólny klucz case-insensitive nie tworzy drugiego klucza.

### Konflikt rdzeń ↔ moduł
Porównujemy wyniki niezależnego resolvera, a nie surową kapitalizację źródłową. Jeżeli rdzeń i moduł po zastosowaniu wspólnych reguł dają różne kanoniczne powierzchnie, CI ma się zatrzymać. To jest sygnał do naprawy reguły dla całej klasy przypadków, a nie do dopisywania wyjątku dla jednego słowa.

Przykład aktualny:
- warszawa w rdzeniu + niezależny resolver -> warszawa, ponieważ Morfeusz/SGJP potwierdza analizę `nazwa_pospolita`;
- moduł miasta po tym samym resolverze również -> warszawa;
- surowe źródło `Warszawa` nie może przełamać tej reguły.

Nie wolno naprawiać tego przez ręczny wyjątek dla Warszawy.

## Nazwy z łącznikiem — obowiązująca zasada

Nazwa z rozpoznanym projektowym łącznikiem ma być zachowana w dwóch warstwach jednocześnie:
- komponenty: np. kujawsko, pomorskie;
- pełna powierzchnia: kujawsko-pomorskie.

Pełne formy odmienione również muszą być zachowane tam, gdzie model kategorii je przewiduje, np. kujawsko-pomorskiego.

Dla miast: Bielsko i Bielsko-Biała mają być osobnymi kandydatami; prefix bielsko powinien móc znaleźć obie powierzchnie.

Łącznik nie definiuje gramatyki. Nie odmieniać automatycznie każdego komponentu bez modelu kategorii. Dla województw zachować istniejący model: stały pierwszy komponent + odmiana końcowego przymiotnika.

Spacja sama nie uruchamia ścieżki łącznikowej. Oficjalna nazwa może jednak zawierać łącznik i spację; pełna powierzchnia hyphenowana jest zachowywana, natomiast alternatywy rozdzielone przecinkiem nie są jedną nazwą.

## Aktualizacja ciągłości — 2026-09-30 — najnowszy stan HEAD

Najnowszy HEAD branch:
- `c7ad011a1e7631438b263b2c31c98950ee690222` — `test: inspect Morfeusz analysis for Warsaw`.
- dokumentacja została później uzupełniona w commitach `95181170...`, `3709c563...`, `cf07e423...`.

Ostatnie poprawki po checkpointcie:
- `29af2b160787e4879dd952d2e8b57b9d75917701` — komponent nazwy złożonej ma własną analizę; kapitalizacja ze źródła jest tylko fallbackiem, nie wymuszeniem.
- `36374a6d7cb6ae2452e010f675e61587f7667758` — wspólna warstwa NKJP1M została wydzielona do `scripts/nkjp_capitalization.py`; zarówno audyt rdzenia, jak i audyt modułów korzystają z tego samego niezależnego źródła wtórnego.
- Audyt modułów dostaje teraz `--nkjp` i dla kluczy wspólnych z rdzeniem wykonuje niezależne rozstrzygnięcie na tej samej warstwie Morfeusz + NKJP, po czym porównuje wynik z rdzeniem.
- To naprawia klasę konfliktów, w której rdzeń mógł dostać `Warszawa` z niezależnej evidencji NKJP, a moduł bez NKJP nadal rozstrzygał `warszawa`.
- Nazwy z rozpoznanym łącznikiem pozostają podwójne: komponenty + pełna powierzchnia. Pełne formy są objęte walidacją CKDT.
- Dokumentacja starszych polityk została zaktualizowana; obowiązuje `docs/ARCHITECTURE_DECISION_2026-09-30.md`.

### Bieżące CI
Najnowszy stan należy sprawdzać bezpośrednio w GitHub, ponieważ kolejne commity diagnostyczne uruchamiają nowe runy i anulują starsze.
- Preview #354 / run `36770384684` uruchomiony dla diagnostyki Warszawy; wynik należy zweryfikować przed kolejnym etapem.
- Size-study #265 / run `36770261873` jest starszym runem na `098bf1f6...`; jego wynik nie jest jeszcze checkpointem.
- Wcześniejsze Preview #344 wykazało, że resolver rdzenia zwraca dla `warszawa` lowercase z powodu analizy `nazwa_pospolita`.
- Wcześniejszy Size-study wykazał dziewięć rozbieżności wynikających z braku niezależnego fallbacku oficjalnej pisowni; dodano `OFFICIAL_CAPITALIZATION_SOURCES` jako późną warstwę ortograficzną.
- Aktualny workflow ma dodatkowy probe surowych analiz Morfeusza dla `warszawa`.
Nie traktuj żadnego z tych runów jako zielonego checkpointu, dopóki GitHub nie poda `success`.


## Aktualny stan po wykonanych zmianach

Ostatnie commity na branchu:
- `7f21f763c8f6f8177819a81b6eb070c3c42a86c4` — niezależna kapitalizacja rdzenia;
- `4f1bc16e57172798040bbeb05479bdacf460e6da` — pełne powierzchnie z łącznikiem;
- `7f31c51c9cbaf949931ae1589859b5aef8ec9271` — pełne formy miast/KSNG;
- `9f5acde2e66d91f299c0d50130afd8e2feebb14d` — poprawa generatorów;
- `f2230fd7933eb927837407e3064c4bef362aec63` — połączenie form rdzenia z evidencją NKJP przez lemata Morfeusza;
- `e6a807b58ec777060fa6983bf804cfc8ccca48c4` — naprawa importu audytu modułów;
- `3e876ce3101ec29845e55650559d9b97a883c8a8` — regresje rdzeń + łączniki;
- `aca90f627c0cc0f610a8e2295383cd51e193028e` — niezależne rozstrzyganie komponentów nazw złożonych;
- `a382f735af0d8ada962d53bfc1ec7258207a9405` — aktualizacja starszej dokumentacji.

Świeże CI należy zawsze sprawdzać względem najnowszego HEAD, a nie względem wcześniejszych runów. Znany wcześniejszy failure ujawnił konflikty `abudży, dżibuti, fidżi, male, mark, mia, nauru, prince, santo, zjednoczone`; była to właśnie pożądana sygnalizacja problemu reguły. Po rozdzieleniu kapitalizacji komponentów należy sprawdzić, które z nich pozostają rzeczywistym konfliktem.

## Stan znany przed bieżącą naprawą

Poprzedni zielony checkpoint:
- Preview #329 / run 36753805242 — success;
- Size-study #248 / run 36753805549 — success;
- First-name audit #121 / run 36753805054 — success;
- final unique keys: 105703.

To jest tylko checkpoint referencyjny. Po zmianach kapitalizacji i nazw z łącznikiem należy uruchomić nowe CI i używać wyłącznie świeżych wyników.

## Następne zadania

1. Zweryfikować najnowszy Preview i Size-study na aktualnym branchu; żaden wcześniejszy failure nie jest checkpointem.
2. Sprawdzić, czy fallback oficjalnej pisowni usuwa wcześniejsze dziewięć rozbieżności `abudży, dżibuti, fidżi, male, mark, mia, nauru, prince, santo`.
3. Potwierdzić w logu surowe analizy Morfeusza dla `warszawa` oraz zgodność z testem lowercase.
4. Po green CI pobrać świeży artefakt, sprawdzić CKDT, 100k membership, kapitalizację oraz wszystkie pełne powierzchnie z rozpoznanym łącznikiem.
5. Dopiero po poprawnym artefakcie przejść do testów runtime/prefix/swipe na przypiętym CleverKeys.
6. Nie zmieniać membership immutable 100k i nie wykonywać merge/promote do `main`.

Przeczytaj także nowy dokument: docs/ARCHITECTURE_DECISION_2026-09-30.md.


## Aktualny wniosek po diagnostyce Warszawy

- `nazwa_pospolita` ma absolutne pierwszeństwo.
- `warszawa` jest obecnie oczekiwane jako lowercase, ponieważ resolver wykrył analizę `nazwa_pospolita`.
- Oficjalna kapitalizacja źródłowa jest fallbackiem ortograficznym, nie sposobem na przełamanie analizy językowej.
- Nie dodawać ręcznego wyjątku dla Warszawy bez dowodu, że zmienia się reguła całej klasy.


### Stan po wykryciu błędu `-Bielska`

- Size-study #265 wykrył w `build/pl-city-inflections.tsv` wadliwą formę `-Bielska`.
- Commit `25b4aa79d8db2d8448f12c42b9287548fe7d7557` naprawił pierwotną przyczynę w `build_hyphenated_city_forms()`: `products` musi startować od `()`, nie `("",)`.
- Commit `7af161c9fa1b639b8f0cb08843178eb8aa07f3e3` dodatkowo wyłącza zwykłą ścieżkę `Morfeusz.generate()` dla nazw z łącznikiem; takie nazwy są obsługiwane wyłącznie przez model hyphenowany kategorii miast.
- Świeże CI na `7af161c...`: Preview #357 / run `36770877395`; Size-study #268 / run `36770877795`.
- Nie uznawać jeszcze wyniku za zielony checkpoint.


## Migracja 2026-10-01 — najnowszy stan i nowe zadanie

Ostatni istotny commit diagnostyczny:
- `e70bc404b95659dd3ed94e5c84e6962683b05895` — dodał skrypt niezależnego audytu kandydatów dwóch kapitalizacji;
- `34164d869fc4e90c651129d9fd9e413121bfabdd` — dodał ten audyt do Preview CI.

Nowy skrypt:
`scripts/audit_core_dual_casing_candidates.py`

Definicja pomiaru:
- tylko immutable 100k core;
- moduły nie są używane do kwalifikacji;
- Morfeusz 2 / SGJP jest jedynym źródłem;
- kandydat = jednocześnie `subst:sg:nom + nazwa_pospolita` oraz konkurencyjna `subst:sg:nom` z nie-pospolitą klasą własną;
- formy odmiany inne niż mianownik są wykluczone.

Uwaga: liczba **11 499** z wcześniejszego runu NIE jest wynikiem tego ścisłego kryterium. Była wynikiem szerszej diagnostyki i obejmowała również liczne formy/klasy własne. Ścisły audyt mianownika został dopiero dodany do Preview #369. Jego rzeczywisty wynik trzeba odczytać z logu kroku „Audit immutable-core dual-casing candidates without modules”.

Kluczowa zmiana podejścia:
- problem `Warszawa` nie powinien być rozwiązywany przez ręczny wyjątek;
- trzeba rozważyć możliwość przechowywania dwóch powierzchni kapitalizacyjnych dla rzeczywistego homonimu, np. `łódź` + `Łódź`, `malina` + `Malina`;
- użytkownik trafiając na niewłaściwy wariant powinien móc wybrać drugi z paska podpowiedzi bez edycji pierwszej litery;
- mała/wielka litera ma być częścią powierzchni, ale członkostwo klucza case-insensitive pozostaje jednym kluczem.

BARDZO WAŻNE:
Aktualny CleverKeys ma ścieżki, które deduplikują kandydatów case-insensitive. Nie wolno zakładać, że dwa wpisy różniące się tylko wielką literą automatycznie pokażą się jako dwa osobne przyciski. Trzeba sprawdzić rzeczywisty runtime/CKDT. Generator naszego packa obecnie również wymusza unikalność kluczy case-insensitive.

Następny etap:
1. Pobierz wynik audytu 11 499 i pogrupuj kandydatów według klas Morfeusza.
2. Ustal osobno grupę „rzeczywiście sensowne dwie powierzchnie” oraz przypadki, dla których jedna powierzchnia jest wystarczająca.
3. Sprawdź na przypiętym CleverKeys SHA `263bd0abc03dec420f60fa073a9d2c5e25a176b5`, czy CKDT może zwrócić jednocześnie `łódź` i `Łódź` jako dwa używalne warianty, jeżeli oba są fizycznie zapisane.
4. Dopiero po tym zaprojektować ewentualną zmianę formatu/lookupu. Nie zmieniać jeszcze immutable 100k.
5. Nadal nie wykonywać merge/promote do `main`.

Najnowszy CI:
- Preview #369 / run `36829489035` dla commitu `34164d869fc4e90c651129d9fd9e413121bfabdd` był podczas migracji uruchomiony i w ostatnim sprawdzeniu pozostawał `in_progress`.
- Poprzedni Size-study #272 / run `36775273277` dla `424b8b1811dfb9d791d4380b049d8711e9f335a2` zakończył się `success`.
- Preview #364 / run `36775273327` dla `424b8b...` zakończył się `failure` dopiero na końcowym kroku weryfikacji CKDT; wcześniejsze etapy kapitalizacji przechodziły.

Nie uznawać obecnego Preview za checkpoint, dopóki GitHub nie poda świeżego wyniku.
