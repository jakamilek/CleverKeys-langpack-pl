# Nowe zdania, przymiotniki i znaczenia tej samej pisowni — 2026-10-02

Dodano 64 nowe ręcznie napisane konteksty oraz osobne kontrole. HerBERT WWM
wypadł najlepiej w tej próbie pisowni: 56/64 top 1 i 56/64 top 3 w osobnym
probe konkurujących podpowiedzi. Polbert uzyskał 53/64, NLI z opisami 48/64.
To wspiera dalsze testy gotowych modeli, ale nie wybór silnika produkcyjnego.
Sama jawna informacja o znaczeniu nie gwarantuje przewagi nad cased MLM.

## Dane i kryterium trzech propozycji

Główne kryterium: poprawny klucz i dokładny zapis w pierwszych trzech
sugestiach. Top 1 pomocniczo. Zachowujemy inne warianty tego samego słowa.

Siedem kluczy: łódź, łodzi, malina, jagoda, róża, polska, warszawska.
64 konteksty główne, po 16 natural_direct/history/switch/negation; w każdej
kategorii po 8 lowercase i capitalized. Żaden nie jest kopią poprzedniego
fixture. Powstały po wcześniejszej diagnozie: nie są zewnętrznym ślepym
benchmarkiem, korpusem użytkowników ani dowodem ogólnej jakości.

Osobno 64 powtórzone top3_probe, 14 sentence_start, 8 ambiguous bez gold,
7 missing_key i 7 slot_limit. Razem 164 cases / 328 requests. Powtórzenia nie
powiększają niezależnej próby. Slates są sztuczne, nie rzeczywiste maźnięcia.

## Co zmienia przykład warszawska

Jeden wariant może mieć kilka znaczeń. W sidecarze:
- warszawska → przymiotnik określający związek z Warszawą;
- Warszawska → nazwa ulicy lub nazwisko.

Przykłady pisowni: ulica Warszawska, Anna Warszawska, warszawska firma,
warszawska ulica w znaczeniu ulicy położonej w Warszawie. Początek zdania
jest osobnym display mode, więc wielka litera nie dowodzi znaczenia nazwy.
Źródło reguł: [aktualne zasady RJP](https://rjp.pan.pl/app/uploads/2026/03/Zalacznik-do-komunikatu-11-25-wersja-ostateczna-jednolita.pdf),
rozdz. 8.1.1, 8.1.2 pkt 1 i 16, 8.2 pkt 4. Osoby/przykłady są fikcyjne;
nie poświadczamy tych nazwisk w rejestrach ani coverage rzeczywistego 100k.
łodzi/Łodzi to jawny kolejny surfaceKey, nie wdrożona lematyzacja.

## Wyniki wszystkich zamrożonych warunków

| System | Główne top 1: 2 słowa | Główne top 1: długie | Osobne probe top 3: długie | Główne meaning top 1: długie |
|---|---:|---:|---:|---:|
| Neutralny default | 32/64 | 32/64 | 32/64 | — |
| NLI global_attributes, opisy jak wcześniej | 40/64 | 48/64 | 48/64 | 45/64 |
| NLI current_attributes, aktualne dopisywane słowo | 43/64 | 47/64 | 47/64 | 45/64 |
| Ten sam NLI bez opisów znaczeń | 28/64 | 37/64 | 37/64 | — |
| Polbert WWM | 46/64 | 53/64 | 53/64 | — |
| HerBERT WWM | 50/64 | 56/64 | 56/64 | — |

Na głównej próbie top 3 = 64/64 **we wszystkich systemach**, również neutralnym,
ponieważ pierwszy klucz ma tylko dwa warianty. To wynik zachowania alternatyw,
nie 100% jakości AI. W probe prawidłowy klucz jest drugi, po dwóch wariantach
innego klucza; wybrana forma zajmuje pozycję 3, alternatywa 4. Dlatego liczba
trafień probe top 3 jest konstrukcyjnie równa main top 1 przy tych samych
kontekstach. Nie jest osobnym niezależnym potwierdzeniem jakości.

Wszystkie modele wykonano naprawdę na nowych danych, nie replay starych
scores. Nie zmieniano lexical order ani engineScore, więc nie jest to test
wybierania właściwego słowa spośród konkurujących kluczy.

NLI global z opisami wobec tego samego modelu bez opisów naprawił 20 i zepsuł
9 (net +11). Wobec Polbert naprawił 4 i zepsuł 9; wobec HerBERT naprawił 7
i zepsuł 15. Zyski opisu znaczeń dla jednego modelu nie oznaczają wyboru tego
modelu jako najlepszego dla pisowni. Nie dobierano blendu modeli lub reguł per
słowo po wyniku. Rankingi modeli zmieniły się wobec poprzedniej diagnozy,
co przemawia za szerszą niezależną ewaluacją przed decyzją produkcyjną.

## Kategorie i poszczególne klucze

Długi kontekst, poprawna pisownia na miejscu 1:

| Kategoria | NLI global | NLI current | Polbert | HerBERT |
|---|---:|---:|---:|---:|
| Bezpośrednia wskazówka | 11/16 | 11/16 | 13/16 | 15/16 |
| Informacja z wcześniejszego zdania | 13/16 | 15/16 | 13/16 | 14/16 |
| Zmiana tematu | 10/16 | 9/16 | 13/16 | 14/16 |
| Zaprzeczenie innego znaczenia | 14/16 | 12/16 | 14/16 | 13/16 |

Samo sformułowanie hipotezy o aktualnie dopisywanym słowie nie poprawiło
wyniku ogólnego NLI: 47 zamiast 48, mimo lokalnych popraw/regresji (wobec
global zmieniło 15 przypadków, 7 popraw na 8 regresji). Nie rozwiązało problemu
zmiany tematu. Opisów/hipotez/metod nie poprawiano po obejrzeniu wyników.

| Klucz | Liczba | NLI global: pisownia / znaczenie | Polbert: pisownia | HerBERT: pisownia |
|---|---:|---:|---:|---:|
| łódź | 8 | 5 / 5 | 6 | 8 |
| łodzi | 8 | 6 / 6 | 8 | 8 |
| malina | 8 | 5 / 5 | 8 | 8 |
| jagoda | 8 | 8 / 8 | 8 | 4 |
| róża | 8 | 8 / 8 | 8 | 5 |
| polska | 8 | 5 / 5 | 7 | 8 |
| warszawska | 16 | 11 / 8 | 8 | 15 |

Warszawska: NLI global ma 11/16 poprawnej pisowni, ale tylko 8/16 poprawnego
znaczenia. Trzy dalsze przypadki mają dobrą wielką literę przy pomyleniu
nazwiska z ulicą. NLI current: pisownia również 11/16, znaczenie 9/16.
HerBERT/Polbert wybierają zapis; nie udajemy ich jawnej klasyfikacji znaczenia.

## Pozostałe błędy i kontrola granic

HerBERT ma 8 błędów main top 1: cztery owoce jagoda jako Jagoda, trzy kwiaty
róża jako Róża i jeden przymiotnik warszawska jako Warszawska (nat062).
Polbert ma 11 błędów: wszystkie osiem przymiotnikowych warszawska jako
Warszawska, dwa konteksty miasta łódź oraz jeden przymiotnik polska.

Tokenizacja wyjaśnia możliwy czynnik, ale nie dowodzi jednej przyczyny:
HerBERT jagoda/róża mają po 2 subwordy, Jagoda/Róża po 1; Polbert warszawska
ma 2, Warszawska 1. Sumy log probabilities w WWM mogą preferować krótszy
wariant. Nie izolowano tego wpływu od priorytetów modelu i nie dostrajano
normalizacji po wyniku. Inne warianty (np. warszawska w HerBERT) mają po jednym
tokenie i również potrafią mieć błędną preferencję.

W głównej próbie poprawna forma przy tych błędach nadal jest drugą sugestią.
W probe drugi wariant drugiego klucza jest czwarty: poza przyjętym top 3,
ale nadal osiągalny. Rozkład miejsc UI będzie istotny w późniejszej integracji.

Kontrole pisowni: wszystkie systemy i oba okna. Wyniki znaczeń poniżej dotyczą
długiego okna:
- sentence_start: pisownia 14/14 top 1 po jawnym autocap, także bez AI.
  NLI global wybiera właściwe znaczenie 12/14, current 13/14; rozdzielamy
  poprawny display od semantyki i nie wdrażamy detektora granic zdań;
- missing_key: 0/7 osiągalnych form — model nie dopisuje słowa spoza dekodera;
- slot_limit: 7/7 form osiągalnych, lecz 0/7 top 3 przy stałej kolejności
  kluczy — poprawny klucz zaczyna się najwcześniej na miejscu 4;
- ambiguous: 8 bez gold, bez sztucznej accuracy.

## Walidacja i proweniencja

[NATURAL_PROTOCOL.md](NATURAL_PROTOCOL.md), kod i dane zamrożono przed inferencją
w 0509a1cc3f222ec6afbcfb08b98a96dfda52824a. Baseline poprzedniego etapu:
55bb179a1d308cf7a7f7d4049ec6e3f060719e4c. Żadne wcześniejsze wyniki nie zmienione.

Przypięte gotowe modele, bez treningu:
- NLI MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli:
  0a71e92a985b6e1ad1828cf67ce9c459639c1dca;
- Polbert: fed744e81ebd16cf099b5c64c40688bc3e6ace67;
- HerBERT: 50e33e0567be0c0b313832314c586e3df0dc2297.

Wagi/głowice kompletne. Brak missing/mismatched/error; NLI i Polbert również
bez unused weights. HerBERT ma tylko wcześniej dopuszczone wagi poolera/SSO,
nieużywane przez MLM. Parity oryginalnego forward i projekcji ocenianych
pozycji: max error 4.292e-6 Polbert, 3.052e-5 HerBERT.

- 66/66 testów stdlib PASS lokalnie.
- Freeze [push CI 37057347080](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37057347080)
  i PR CI 37057354504 completed/success. CI testuje kontrakt, nie modele/Android.
- Trzy procesy realnej inferencji exit 0; predykcje kompletne/dopuszczalne/finite,
  zgodne z request hash. Sense scores zgodne z inventory i max przypisanych znaczeń.
- Fixture regeneruje się byte-identical; kod/dane zgodne z freeze w GitHub;
  engineScore sugestii zachowane.
- CPU float32, 2 wątki na proces, batch 8, eval/inference_mode; inferencje niezależne.
- NLI 1776 unikalnych par, MLM po 558 unikalnych tasks; 456 grup/każdy model.
  Wszystkie wejścia mieszczą się w 512 pozycjach, bez tokenowych obcięć.
- Czas całej inferencji po ładowaniu: NLI 14,40 s, Polbert 29,70 s, HerBERT
  28,59 s przy równoległych procesach/cache. To nie kontrolowany benchmark
  telefonu ani porównanie latencji jednego maźnięcia.
- Runner SHA256: f3fd6f76dad2b8770c667c17f8f1b424996ea917aacfc3c5fc26738978bd15e1.
- Cases SHA256: 57669d70d538b58abc65a28910504f7bab81bbac6c543812f7523e517e79f741.
- Requests plik SHA256: 71091c409e6f38fc983d4c248096efcb91790a356ed8443ac33159e6f8c38bb6.
- Request payload hash: 49016dfa848c5c29f7b24b48daf9d366a7741215ded6647cc28d4d26eed7b92d.
- Summary SHA256: 052a8cb7cf7d73683fe462698e510a8f96ca63350a298f3c84533a18cd7bb305.

[natural-results-2026-10-02](natural-results-2026-10-02): pełne scores,
sense scores, decisions, summary, trace, loading info, environment i SHA256.
Manifest modeli zawiera również nowe tokenIds oraz zweryfikowane pliki wag
i tokenizerów. Żadnych wag nie redystrybuowano. Scores nie są skalibrowaną
pewnością. Licencja dystrybucji Polbert pozostaje nieustalona; dokumentacja
licencji pozostałych modeli w poprzednich milestone’ach, bez nowych deklaracji.

## Dalszy krok

Zachować jeden klucz z wariantami i możliwością wielu znaczeń na formę.
Potrzebna osobna, uprzednio zapisana kontrola wpływu różnych długości
tokenizacji, bez wyboru reguł/modelu per słowo na obejrzanych przykładach.
Następnie szersze dane i rzeczywiste slates: top 3 zależy również od kolejności
kluczy i miejsc zajmowanych przez alternatywy. Koszt telefonu i interpunkcja
nadal przed wyborem silnika. Nie zmieniono Androida, CKDT, generatora, API v1,
100k ani ZIP-a; wszystko pozostaje eksperymentem w Draft PR #4.
