# Wyniki: znaczenia przypisane do wariantów, 2026-10-02

Zrealizowano propozycję użytkownika w izolowanym eksperymencie: jeden klucz
słownikowy, warianty z senseIds i osobne opisy znaczeń. Gotowy model NLI
oceniał zgodność kontekstu z opisami, bez treningu. Dodatkowe atrybuty pomagają
w tym kontrolowanym zestawie, szczególnie gdy wskazówka jest wcześniej.
Słabość przy sprzecznych opisach nie pozwala wybrać tego modelu do produkcji.

## Kryterium użytkownika: poprawna forma w top 3

Użytkownik zaakceptował pierwsze **trzy** miejsca jako dobry wynik. Główną
metryką jest poprawny klucz i dokładna pisownia w top 3; top 1 jest dodatkowy.
Nie wymagamy doskonałego top 1. Zachowanie alternatyw jest częścią resolvera,
więc nie przypisujemy całej dostępności wariantów inteligencji modelu.

Na głównej próbie 32/32 mają właściwą formę w top 3 we **wszystkich** systemach,
także neutralnym: pierwszy klucz ma tylko dwa warianty. To sprawdza zachowanie
alternatyw, a nie przewagę AI. Dlatego osobno dodano top3_probe: właściwy klucz
na drugim miejscu dekodera, poprzedzony dwoma wariantami innego klucza.
Wybrana forma celu zajmuje miejsce 3, jej alternatywa 4. Konteksty są
powtórzeniami głównej próby, nie dodatkową niezależną populacją.

## Wyniki zamrożonej próby

| System | Główne top 1: 2 słowa | Główne top 1: długie | Główne top 3: długie | Osobne probe top 3: długie |
|---|---:|---:|---:|---:|
| Neutralny default | 16/32 | 16/32 | 32/32 | 16/32 |
| NLI, poprawne opisy znaczeń | 18/32 | 24/32 | 32/32 | 24/32 |
| Ten sam NLI, bez opisów znaczeń | 14/32 | 16/32 | 32/32 | 16/32 |
| NLI, opisy zamienione między formami | 14/32 | 8/32 | 32/32 | 8/32 |
| Polbert wwm — replay v2 | 20/32 | 23/32 | 32/32 | 23/32 |
| Polbert pll_variant — replay v2 | 19/32 | 22/32 | 32/32 | 22/32 |
| Polbert pll_full_mean — replay v2 | 20/32 | 23/32 | 32/32 | 23/32 |
| HerBERT wwm — replay v2 | 18/32 | 21/32 | 32/32 | 21/32 |
| HerBERT pll_variant — replay v2 | 17/32 | 20/32 | 32/32 | 20/32 |
| HerBERT pll_full_mean — replay v2 | 18/32 | 21/32 | 32/32 | 21/32 |

MLM to odtworzenie niezmienionych wcześniejszych ocen celu, bez nowej inferencji.
Nowy konkurent w probe pozostaje neutralny w replay MLM; NLI ocenia oba klucze.
Kolejność kluczy i engineScore nie zmieniają się, więc ten eksperyment nadal
nie bada wyboru właściwego słowa spośród różnych kluczy ani rzeczywistych swipe.

W długim oknie dodanie opisów wobec NLI bez opisów naprawia 10 przypadków i
psuje 2 (net +8). Wobec Polbert wwm naprawia 5 i psuje 4 (net +1). Nie ma
podstaw do ogłoszenia zwycięzcy produkcyjnego na tych znanych szablonach.
Praktyczna ablacja zmienia także treść hipotezy; nie izoluje wszystkich
czynników przyczynowych. Opisów ani metody nie strojono po obejrzeniu wyników.

## Kategorie, długi kontekst i źródła pozostałych błędów

| Kategoria | NLI z opisami, top 1 | Polbert wwm v2, top 1 |
|---|---:|---:|
| Bezpośrednia wskazówka | 7/8 | 8/8 |
| Wskazówka w poprzednim zdaniu | 8/8 | 6/8 |
| Wskazówka dalej w zachowanym kontekście | 8/8 | 5/8 |
| Sprzeczne opisy, poprzedni i aktualny | 1/8 | 4/8 |

W pierwszych trzech kategoriach NLI z opisami daje 23/24, lecz w conflicting
7 z 8 preferowanych form jest błędnych. W tej konfiguracji nie rozróżnia
konsekwentnie znaczenia dotyczącego aktualnego opisu. Hipoteza NLI odnosi się
ogólnie do kontekstu; nie sprawdziliśmy osobno wpływu tego sformułowania wobec
możliwości modelu. Nie przypisujemy regresji jednej wewnętrznej przyczynie.
Ósmy błąd top 1 dotyczy jagoda/Jagoda w bezpośrednim opisie owocu (diag026).
We wszystkich tych przypadkach głównej próby poprawna alternatywa jest druga.

Łódź/łódź w kategorii previous i distant_retained wybrane poprawnie dla obu
znaczeń. To wspiera dalszy test podejścia z atrybutami, a nie gwarantuje
rozumienia nazw własnych w dowolnym tekście.

context_lost: 4/8 top 1 dla obu okien we wszystkich systemach; wskazówka poza
64 słowami daje identyczne wejścia w parach. Raportowane osobno od głównej próby.
8 ambiguous/ambiguous_short nadal bez gold labels i bez sztucznej accuracy.
Opisy zamienione między wariantami zmieniają preferowaną formę w 32/32 głównych
przypadków obu okien. To mechaniczna kontrola mapowania: te same oceny trafiają
do przeciwnego wariantu, nie niezależny dowód zrozumienia tekstu.

## Proweniencja i weryfikacja

Protokół: [SENSE_PROTOCOL.md](SENSE_PROTOCOL.md).
Kod, dane i kryteria zamrożono przed inferencją:
23544abd04fcb540f4df91bd170cad5707e67070.
Źródłowa diagnostyka v2: df65d22b59a865a77939cb00653ac54e5735fb38.

Gotowy model: MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli,
revision 0a71e92a985b6e1ad1828cf67ce9c459639c1dca.
[Karta autora](https://huggingface.co/MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli)
deklaruje MIT i transfer wielojęzyczny; nie zawiera wyniku XNLI dla polskiego.
106 995 075 parametrów, model.safetensors 427 997 022 bajty; kompletne wagi NLI,
bez missing/unexpected/mismatched/error keys. Wag nie opublikowano.

CPU float32, 2 wątki, batch 8, eval/inference_mode. 80 cases / 160 requests,
224 oceniane grupy i 380 unikalnych par po cache identycznych wejść.
Nie obcięto żadnego wejścia limitem 512 pozycji; najdłuższy premise 121 tokenów.
Zachowano dokładny suffix tekstu sprzed kursora, bez gold/category/sourceId.
Scores to log softmax entailment, nie skalibrowana pewność poprawnej pisowni.
4,09 s całej inferencji po załadowaniu modelu na tym CPU, z cache i powtórzeniami;
to **nie benchmark telefonu ani latencja jednego maźnięcia**.

- 56/56 testów stdlib PASS lokalnie.
- [Push CI 37054460796](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37054460796)
  oraz PR CI 37054468868 dla freeze: completed/success.
- CI sprawdza kontrakt, nie uruchamia modeli ani Androida.
- Inferencja exit 0, wszystkie warianty kompletne/dopuszczalne i finite,
  wszystkie predykcje zgodne z request hash.
- Regeneracja fixtures daje identyczne bajty, engineScore zachowane.
- Runner SHA256: 3bcf4b92c6cccd7aaefd4db77fde8cb4d39780682bc6adbd73569810af3f0394.
- Requests plik SHA256: e2f1f254a313ee237d19b8f23d91ca1bbb672853f4c40ae41aa1386e7c7c4b42.
- Request payload hash: 11d068c9a9c6779e61cdb664a531992f71c6c0a0879358e57e36ade4ec1cc833.
- Summary SHA256: a122b35c3489e643c235ed922a7f725cad1c8b7f451e58b7f77c7cc5c58d36e3.

[sense-results-2026-10-02](sense-results-2026-10-02) zawiera pełne scores,
odtworzone baseline’y, decyzje, summary, trace, environment, manifest plików
modelu i SHA256 artefaktów. Fixture i sidecar są przypięte obok kodu.

## Decyzja i dalszy krok

Zachować kierunek słownika z jawnymi znaczeniami i alternatywami oraz główną
ocenę top 3. Ten test wspiera sens wykonania kolejnego eksperymentu, ale nie
wybór NLI do klawiatury. Top3_probe pokazuje też koszt zajmowania dwóch miejsc
przez warianty pierwszego klucza, gdy właściwe słowo jest kolejnym kandydatem.

Następny test powinien mieć nowe zwykłe zdania i sprzeczne wskazówki dotyczące
aktualnego dopisywanego słowa, z kryteriami zamrożonymi przed wynikiem. Dane
niezależne od dotychczasowych szablonów i rzeczywiste slates są potrzebne przed
wnioskami o jakości dla użytkowników. Dalej: koszt telefonu i osobna próba
interpunkcji przy wyborze silnika. Nie zmieniono Androida, API produkcyjnego,
generatora, CKDT, 100k ani ZIP-a; eksperyment pozostaje w Draft PR #4.
