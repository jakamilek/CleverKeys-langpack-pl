# Kategorie źródłowe a wybór pisowni — wyniki

Inferencja: 2026-10-02. Końcowa weryfikacja i zapis po przerwie: 2026-10-03 UTC.
Status: ukończony izolowany eksperyment; bez wyboru silnika produkcyjnego.

**Rzeczywiste kategorie źródłowe nie poprawiły wyniku tego modelu NLI w zamrożonym sposobie ich użycia.** NLI z kategoriami uzyskał 33/68 poprawnych pierwszych propozycji przy długim kontekście, ten sam model bez kategorii 39/68. HerBERT WWM jako odniesienie pisowni uzyskał 59/68, Polbert 54/68. Nie należy z tego wnioskować, że metadane są zbędne albo że HerBERT umie z nich korzystać.

## Co zostało wykonane

Kod, dane i kryteria zamrożone przed inferencją w e654720e5bcbe9825747b74df2b7d82cdfac4eaa. [SOURCE_CATEGORY_PROTOCOL.md](SOURCE_CATEGORY_PROTOCOL.md).
Wejście metadanych: source-metadata-audit.json z cd03c3002e7164eac5d972a2a8b502873177ca09, hash 83ae7299c4781bd0cb731db6d5653cbc6f6b840c38d4b60a1797f40e894c6a4a.

Generator automatycznie zachował 39 interpretacji lemma/tag/NAME/LABELS i 83 generatedFormProofs dla dziewięciu kluczy. Warianty pochodzą z syntezy Morfeusza 1.99.15 / pl.sgjp.sgjp-2026.06.01; dopasowane do klucza, części mowy i tych samych klas NAME. Nie wywnioskowano kapitalizacji z orth uppercase wejścia i nie wpisywano ręcznych opisów fruit/boat/street.

Metadane źródłowe słownika są automatyczne. Konteksty i ich gold labels nadal są ręcznie napisanymi przykładami testowymi. Generic PHRASES renderuje każdą klasę tym samym szablonem, niezależnie od słowa. NLI otrzymał NAME lub POS przy pustym NAME. Pełne tagi/kwalifikatory są zachowane w danych, ale nie użyte w hipotezach. To test tej projekcji danych, nie wszystkich możliwych metod wykorzystania metadanych.

68 main: 60 jawnie powtórzonych zdań z NATURAL, bez czterech przypadków ulicy, plus 8 nowych warszawski/Warszawski. 36 małych i 32 wielkie litery. To mały ręczny zbiór, w większości wcześniej oglądany, nie zewnętrzny ślepy benchmark.

Oddzielnie: 68 powtórzonych top3_probe, 8 single-variant łódzki, 4 unsupported_street, po 9 sentence_start/ambiguous/missing_key/slot_limit. Łącznie 184 cases / 368 requests. Gold, diagnozy i dawny expectedSenseIds nie trafiają do requestów.

## Wyniki zamrożonych warunków

| System | Main top 1: 2 słowa | Main top 1: długie | Main top 3: długie | Osobne probe top 3: długie | Kategoria top 1: długie |
|---|---:|---:|---:|---:|---:|
| Neutralny default | 36/68 | 36/68 | 68/68 | 36/68 | — |
| NLI z kategoriami źródłowymi | 37/68 | 33/68 | 68/68 | 33/68 | 24/68 |
| Ten sam NLI bez kategorii | 28/68 | 39/68 | 68/68 | 39/68 | — |
| Polbert WWM, bez kategorii | 47/68 | 54/68 | 68/68 | 54/68 | — |
| HerBERT WWM, bez kategorii | 53/68 | 59/68 | 68/68 | 59/68 | — |

Główne kryterium pozostaje poprawny lexical key i dokładny zapis w pierwszych trzech propozycjach. Main top 3 jest jednak gwarantowane konstrukcją: właściwy klucz pierwszy, dwa warianty. Wynik 68/68 także neutralnego defaultu nie jest dowodem 100% jakości AI.

Probe powtarza main, ustawiając właściwy klucz drugi po dwóch wariantach innego słowa. Preferowana forma celu jest trzecia, alternatywa czwarta. Probe top3 mechanicznie równa się main top1 i nie zwiększa niezależnej populacji. Rzeczywista kolejność kluczy i presja slotów UI nie były mierzone na maźnięciach.

CategoryTop1 oznacza szeroką kategorię NAME/POS, nie pełne znaczenie, identyfikację osoby/miasta ani wybór konkretnego lematu. Dobra kapitalizacja może towarzyszyć pomyleniu imienia z nazwiskiem. MLM nie ma tu jawnego pomiaru kategorii.

## Podzbiory i poszczególne klucze

| System | Powtórzone 60: top 1 długie | Nowe warszawski, 8: top 1 długie |
|---|---:|---:|
| Neutralny | 32/60 | 4/8 |
| NLI z kategoriami | 29/60 | 4/8 |
| NLI bez kategorii | 35/60 | 4/8 |
| Polbert WWM | 49/60 | 5/8 |
| HerBERT WWM | 52/60 | 7/8 |

| Klucz | Cases | NLI z kategoriami: zapis / kategoria | Polbert: zapis | HerBERT: zapis |
|---|---:|---:|---:|---:|
| łódź | 8 | 4 / 4 | 6 | 8 |
| łodzi | 8 | 4 / 4 | 8 | 8 |
| malina | 8 | 4 / 4 | 8 | 8 |
| jagoda | 8 | 4 / 1 | 8 | 4 |
| róża | 8 | 4 / 1 | 8 | 5 |
| polska | 8 | 4 / 1 | 7 | 8 |
| warszawska | 12 | 5 / 5 | 4 | 11 |
| warszawski | 8 | 4 / 4 | 5 | 7 |

Wobec NLI bez kategorii naprawiono 13 przypadków i zepsuto 19: netto -6. Wobec neutralnego defaultu 31 napraw / 34 regresje; wobec Polbert 3 / 24, wobec HerBERT 2 / 28. Nie dobrano miksu lub modelu per słowo po wyniku.

## Obserwowane błędy

NLI z kategoriami wybierał wielką literę w 65/68 głównych długich kontekstów. Trafił w 31/32 oczekiwanych wielkich liter, ale tylko 2/36 małych. Wybrane kategorie: nazwisko 44, geograficzna 16, imię 5, pospolita 2, przymiotnik 1. To wyraźna preferencja kategorii nazwowych, a nie poprawne rozstrzyganie bieżącego użycia.

Maksimum po kilku kategoriach górnego wariantu może faworyzować wielką literę — ograniczenie zapisano przed pomiarem. Jednak preferencja występuje też np. dla łódź i warszawski, gdzie każdy wariant ma jedną kategorię; sama liczba kategorii nie wyjaśnia wszystkich błędów. Nie izolowano wpływu sformułowania hipotez, wiedzy gramatycznej modelu, jego priorytetów ani agregacji. Nie stroimy ich po obejrzeniu tych przypadków. Porównanie z/bez kategorii zmienia też treść hipotezy, więc nie jest izolacją jednego czynnika.

Dłuższy kontekst w tym NLI nie pomógł: 33 wobec 37 z dwóch słów; kategoria 24 wobec 32. Nie oznacza to, że krótki kontekst powinien być docelowym rozwiązaniem.

HerBERT ma dziewięć błędów main: cztery zwykłe jagoda→Jagoda, trzy róża→Róża, jeden przymiotnik warszawska→Warszawska oraz nazwisko Warszawski→warszawski w new006. Prawidłowy wariant jest w tych przypadkach drugim w main, lecz czwartym w probe. Dotychczasowe ograniczenia WWM przy różnej liczbie subwordów pozostają otwarte. Warianty warszawski/Warszawski mają po jednym tokenie w obu MLM, więc ten jeden błąd również nie wynika wyłącznie z różnicy długości.

## Kontrole i zakres metadanych

- single-variant łódzki: 8/8 pisowni we wszystkich systemach/oknach, automatycznie. Źródło nie potwierdza nazwiska Łódzki. NLI ma tu jedną kategorię, więc jej 8/8 również mechaniczne.
- unsupported_street: zapis 4/4 top1 NLI z kategoriami i obu MLM, 2/4 NLI bez kategorii, 0/4 neutralnie w długim oknie. Nie mierzymy rozpoznania ulicy: model ma tylko przymiotnik/nazwisko. Poprawna wielka litera może wynikać z wybrania nazwiska.
- sentence_start: 9/9 display top1 we wszystkich systemach/oknach po jawnym autocap. Długi NLI kategorię wybiera poprawnie 1/9; nie utożsamiać autocap z semantyką.
- missing_key: 0/9 form osiągalnych, wszystkie systemy/okna. Model nie dopisuje klucza spoza dekodera.
- slot_limit: 9/9 osiągalnych, ale 0/9 top3, wszystkie systemy/okna. Cel najwcześniej na miejscu 4.
- ambiguous: 9 bez gold, bez sztucznej accuracy.

Wiedza o mieście, nazwisku lub imieniu jest dostępna źródłowo na różnych poziomach. NLI w tej próbie nie dostaje per-word opisów, pełnych definicji, źródła ULIC ani PESEL nazwisk. Generator zachowuje źródła w sidecarze; nie jest produkcyjnym generatorem całego 100k ani loaderem Androida. M.generate pozwala powiązać formę i lemat; nie wprowadza automatycznego ujednoznaczniania w kontekście.

## Walidacja i proweniencja

Przypięte modele:
- MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli, 0a71e92a985b6e1ad1828cf67ce9c459639c1dca.
- dkleczek/bert-base-polish-cased-v1, fed744e81ebd16cf099b5c64c40688bc3e6ace67.
- allegro/herbert-base-cased, 50e33e0567be0c0b313832314c586e3df0dc2297.

Realna inferencja wszystkich modeli, exit 0, bez replay i treningu. Kompletne pretrained głowice i zapisane loadingInfo; NLI/Polbert bez missing/unexpected/mismatched/error. HerBERT tylko cztery dopuszczone nieużywane wagi poolera/SSO, bez brakujących MLM weights. Selected-position projection parity max error 4.292e-6 Polbert, 3.052e-5 HerBERT. Shared WWM adapter zachowuje historyczny revision suffix natural-sense-surface-v2, a nowy request hash jednoznacznie identyfikuje dane.

76/76 testów stdlib PASS przed freeze i ponownie po wznowieniu. Freeze push CI 37062857614 oraz PR CI 37062863016 completed/success. CI jest kontraktowe, nie wykonuje modeli ani Androida.

Fixture regeneruje się byte-identical; wszystkie siedem plików kodu/danych/protokołu porównano z Git blobs freeze przed inferencją i ponownie po wznowieniu. Predykcje kompletne/finite/dopuszczalne dla 368 requests, category inventory i max association sprawdzone dla każdej grupy. Eval sprawdza lexical order i engineScore. Po przerwie zwalidowano zapisane scores i odtworzono identyczny summary bez ponownej inferencji.

NLI 1543 unikalne pary, 504 grupy; MLM po 578 unikalnych tasks, 482 grupy. Zero tokenowych obcięć. CPU float32, 2 threads/proces, batch8, cached weights. Po ładowaniu 15,31 s NLI / 31,37 s Polbert / 29,60 s HerBERT przy równoległych procesach. To nie kontrolowany benchmark telefonu lub jednego maźnięcia.

model-manifest-reference.json wskazuje wcześniej zweryfikowane pliki modeli z NATURAL i ich hashe. Dodatkowa weryfikacja cache-file hashes w tym etapie została przerwana; nie deklarujemy jej ukończenia. Loading checks i realna inferencja zakończyły się przed przerwą. Środowisko venv nie było dostępne po wznowieniu; zachowane wyniki i kod zweryfikowano standardowym Pythonem. Wagi nie redystrybuowane; licencja dystrybucji Polbert nadal nieustalona.

- Runner SHA256: 18b8b2249a003e8d6863bc56f3845c3a5add7d1f8d6a6d207923edfb4028a969.
- Cases SHA256: cc1be705a36fc3af50e8c0c1977268afbc2af0a70c534cb016ce8c90617c09d9.
- Sidecar SHA256: 6bbdf928c338d44ab3eddb76f8a1fe9f0b4a789cb1d51f55740f55826a21e2e2.
- Requests plik SHA256: 264657153743e4f0b098ea011866efc1be5bb9c2511822853ef4a7e4de001d77.
- Request payload hash: bb5cec6e089aa18f04406c4a3a66f157e0325539f056a856a679894d3921ca2f.
- Summary SHA256: 4c43746730e5e80c1853267aa7d9b0bd2d35965a2a1724d91f79b8d62033ef15.

[source-category-results-2026-10-02](source-category-results-2026-10-02): raw predictions, categoryScores, decisions, summary, traces, loading info, execution checks, environment i manifest hashy. Atrybucja wybranych danych Morfeusza/SGJP pozostaje w experiments/source_metadata_v1/SOURCE_METADATA_AUDIT.md; nie publikujemy pełnego słownika ani wag.

## Wniosek i dalszy krok

Zachować automatyczne źródła i powiązania form: są potrzebne do dopuszczalnych wariantów, proweniencji i kontroli braków. Ten mały model NLI z ogólnymi hipotezami NAME/POS nie jest obecnie uzasadnionym produkcyjnym sposobem rankingu.

Następny krok powinien porównać gotowe rozwiązania lub sposoby rankingu rzeczywiście korzystające z kategorii, z protokołem zapisanym przed kolejną inferencją i szerszym niezależnym zbiorem. Nie poprawiać opisów per słowo, nie wybierać reguł z tych samych przykładów. HerBERT pozostaje odniesieniem pisowni, a nie dowodem działania metadanych ani wybranym silnikiem. Rzeczywiste slates, koszt telefonu i interpunkcja nadal przed decyzją produkcyjną. Nie zmieniono Androida, CKDT, 100k, generatora produkcji lub API v1; eksperyment pozostaje w Draft PR #4.
