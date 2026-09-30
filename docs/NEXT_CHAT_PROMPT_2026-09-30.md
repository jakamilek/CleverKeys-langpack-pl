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
