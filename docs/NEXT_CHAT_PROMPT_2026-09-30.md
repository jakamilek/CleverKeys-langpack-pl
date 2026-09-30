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

Przykład docelowy:
- warszawa w rdzeniu + niezależny resolver rdzenia -> Warszawa;
- moduł miasta -> Warszawa;
- zgodność.

Kontrprzykład:
- warszawa w rdzeniu -> warszawa;
- moduł po własnym resolverze -> Warszawa;
- CI ma wskazać konflikt i zablokować pipeline.

Nie wolno naprawiać tego przez ręczny wpis dla Warszawa.

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
- `36374a6d7cb6ae2452e010f675e61587f7667758` — `fix: share NKJP evidence across core and module audits`.

Ostatnie poprawki po checkpointcie:
- `29af2b160787e4879dd952d2e8b57b9d75917701` — komponent nazwy złożonej ma własną analizę; kapitalizacja ze źródła jest tylko fallbackiem, nie wymuszeniem.
- `36374a6d7cb6ae2452e010f675e61587f7667758` — wspólna warstwa NKJP1M została wydzielona do `scripts/nkjp_capitalization.py`; zarówno audyt rdzenia, jak i audyt modułów korzystają z tego samego niezależnego źródła wtórnego.
- Audyt modułów dostaje teraz `--nkjp` i dla kluczy wspólnych z rdzeniem wykonuje niezależne rozstrzygnięcie na tej samej warstwie Morfeusz + NKJP, po czym porównuje wynik z rdzeniem.
- To naprawia klasę konfliktów, w której rdzeń mógł dostać `Warszawa` z niezależnej evidencji NKJP, a moduł bez NKJP nadal rozstrzygał `warszawa`.
- Nazwy z rozpoznanym łącznikiem pozostają podwójne: komponenty + pełna powierzchnia. Pełne formy są objęte walidacją CKDT.
- Dokumentacja starszych polityk została zaktualizowana; obowiązuje `docs/ARCHITECTURE_DECISION_2026-09-30.md`.

### Bieżące CI
Dla HEAD `36374a6d7cb6ae2452e010f675e61587f7667758` wystartowały:
- Preview #340, run `36766869572`;
- Size-study #257, run `36766869525`.

Nie zakładaj wyniku. Przed dalszym etapem sprawdź świeże runy i używaj wyłącznie ich wyników. Poprzednie runy #254/#255 zakończyły się błędem w audycie modułów przed aktualną poprawką.


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

1. Poprawić wspólny resolver tak, aby rdzeń samodzielnie potrafił rozstrzygać nazwy własne, w tym przypadki typu Warszawa, bez danych modułowych.
2. Dodać niezależną wtórną evidencję lingwistyczną NKJP1M do resolvera core, tak aby silne niezależne wskazanie kapitalizacji mogło skorygować zbyt szerokie ordinary-lexical -> lowercase, ale nigdy nie przełamało nazwy pospolitej ani reguły przymiotnik -> lowercase.
3. Zmienić audyt modułów: dla kluczy wspólnych z rdzeniem moduł również rozstrzyga się niezależnie przez wspólny resolver, a wynik porównuje z rdzeniem. Różnica ma blokować CI i być traktowana jako problem reguły.
4. Zachować komponenty i pełne powierzchnie z łącznikiem we wszystkich aktywnych modułach, ze szczególnym uwzględnieniem miast, TERC, krajów/stolic oraz custom_manual.
5. Weryfikować pełne formy odmienione według modelu kategorii; nie wprowadzać sztucznych odmian.
6. Dodać regresje dla Warszawa, malina, łódź, przymiotników pochodnych oraz kujawsko-pomorskie / kujawsko-pomorskiego / Bielsko-Biała.
7. Nie zmieniać membership immutable 100k.
8. Po green CI pobrać świeży ZIP, sprawdzić CKDT i dopiero potem przejść do testów runtime/swipe.

Przeczytaj także nowy dokument: docs/ARCHITECTURE_DECISION_2026-09-30.md.
