# Protokół source-category-surface-v1 — zapis przed inferencją

Cel: porównać gotowy NLI korzystający z rzeczywistych kategorii źródłowych z tym samym NLI bez kategorii. Polbert i HerBERT WWM są odniesieniami pisowni; nie otrzymują kategorii w tej próbie. Bez treningu, miksowania modeli, strojenia per słowo, zmian produkcyjnego API v1 i Androida.

## Dane źródłowe i generator

Wejście: experiments/source_metadata_v1/source-metadata-audit.json z cd03c3002e7164eac5d972a2a8b502873177ca09, SHA256 83ae7299c4781bd0cb731db6d5653cbc6f6b840c38d4b60a1797f40e894c6a4a.
Morfeusz 1.99.15 / pl.sgjp.sgjp-2026.06.01 / pl.sgjp.morfeusz-0.8.0.
Źródło słów: historyczny udany preview run 36916501466, artifact 11189614575; nie nowy build main.

Dziewięć kluczy: łódź, łodzi, łódzki, malina, jagoda, róża, polska, warszawska, warszawski.
Każda interpretacja zachowuje lemma/tag/NAME/LABELS. Jej ID to hash tych danych. Warianty pochodzą z m.generate(pełny lemma ID), filtrowane na exact lowercase key, POS i te same NAME. Nie opieramy kapitalizacji na orth tekstu wejściowego. Wszystkie raw interpretations muszą mieć generatedFormProofs. Pod kluczem łączymy dane, nie usuwamy dodatkowych analiz np. Malin/Łodzia, imienia/nazwiska/geografii.

Kategoria modelu: każda źródłowa klasa NAME; jeżeli NAME puste — pierwszy człon TAG, czyli POS. To uproszczona projekcja danych do NLI, nie klasyfikator wszystkich szczegółów gramatyki. LABELS i pełne TAG zachowane do audytu, nie występują w hipotezie NLI. Klasy łączone NAME pozostają przy lemacie; projekcja dopuszcza wszystkie wymienione klasy, nie rozstrzyga ich samodzielnie.

Generic PHRASES jest wspólne dla kategorii, nie dla słowa:
NAME:nazwa_pospolita → wyrazem pospolitym;
NAME:nazwa_geograficzna → nazwą geograficzną;
NAME:imię → imieniem osoby;
NAME:nazwisko → nazwiskiem osoby;
POS:adj/adjp → przymiotnikiem.
Nie dodajemy etykiet fruit/boat/street/country, nazwiska Łódzki ani relacji słowotwórczych. Źródło generuje tylko łódzki, więc nie ma hipotetycznej alternatywy Łódzki. Warszawska/Warszawski mają źródłowo potwierdzone nazwisko i przymiotnik.

## Populacja i kontrole

68 main: 60 jawnie powtórzonych kontekstów NATURAL (64 minus 4 konteksty ulicy), plus 8 nowych zdań warszawski/Warszawski (4 małe/4 wielkie). Razem 36 małych/32 wielkie; nie zewnętrzny ślepy benchmark. Ocena main oraz dodatkowo reused60/new8 oddzielnie w raporcie, bez wyboru modeli po podzbiorach.

68 top3_probe powtarza main: właściwy klucz #2 po dwóch wariantach innego klucza. Poprawna preferowana forma jest #3, alternatywa #4; probe top3 mechanicznie odpowiada main top1. Distractor malina, a dla malina jagoda.

8 nowych single-variant łódzki — kontrola, nie main; poprawna pisownia jest dostępna automatycznie. 4 unsupported_street ze starej próby — osobno, bez gold kategorii; dobra wielka litera nie dowodzi rozpoznania ulicy. Źródło ulic nie dołączone. Po 9 sentence_start (jawny caseMode), ambiguous (bez gold), missing_key i slot_limit. Łącznie 184 cases / 368 requests. Część kontroli powtarza main; nie zwiększa niezależnej populacji.

ExpectedCategoryIds to ręczna anotacja testowego kontekstu przekształcona do klas źródłowych, nie metadane słownika. CategoryTop1 mierzy wybraną szeroką kategorię NAME/POS, nie pełne ujednoznacznienie lematu lub sensu. Gold, sense IDs ze starych danych, diagnozy i sourceId nie trafiają do requestów modelu.

## Zamrożone warunki i scoring

Premise: exact left context + lowercase candidate. Okna 2 słów oraz do 64 słów/4096 znaków, oryginalny case/diakrytyka/interpunkcja. Model 512 tokenów; wszystkie warunki tego samego klucza dostają ten sam suffix.

source_categories: „W tym kontekście ostatnie dopisywane słowo «{key}» jest {generic category phrase}.”
no_attributes: dokładnie poprzednia hipoteza „W tym kontekście poprawną pisownią dopisywanego słowa jest «{surface}».”
Rzeczywisty kod używa polskich cudzysłowów. Porównanie zmienia treść hipotezy oraz daje kategorie; nie izoluje wszystkich możliwych przyczyn różnicy.

Model NLI: MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli, revision 0a71e92a985b6e1ad1828cf67ce9c459639c1dca. Kompletny pretrained sequence-classification head, log-softmax entailment. Wariant otrzymuje maksimum scores swoich kategorii. Surowe categoryScores zapisane i sprawdzane dla wszystkich grup requestu. Większa liczba kategorii przy wielkiej literze może faworyzować ten wariant; nie stroić agregacji po wyniku. Scores nie są skalibrowaną pewnością.

MLM odniesienia: dkleczek/bert-base-polish-cased-v1 fed744e81ebd16cf099b5c64c40688bc3e6ace67; allegro/herbert-base-cased 50e33e0567be0c0b313832314c586e3df0dc2297. Prawdziwa inferencja na nowych requests, bez replay. Wyłącznie wcześniejsza metoda WWM (maskowanie wszystkich subwordów celu, suma log probabilities), z dotychczasowym sprawdzonym loaderem/projekcją. natural_experiment.run_mlm jest shared runner; jego source revision string natural-sense-surface-v2 opisuje historyczny adapter WWM, dane wiąże nowy request hash. Nie zmieniamy tych funkcji tylko dla etykiety. MLM nie korzysta z NAME/POS w tej próbie. Wpływ długości tokenizacji pozostaje niewyizolowany.

CPU float32, 2 threads/model, batch8, eval/inference_mode, local_files_only. Przypięte cached wagi, brak treningu i redystrybucji wag. Można uruchomić procesy równolegle; czas nie jest porównaniem kontrolowanej latencji telefonu.

## Kryteria i zabezpieczenia

Pierwszorzędne: poprawny key i dokładny surface w top3. Top1 pomocniczo. W main pierwszy klucz ma dwa warianty, więc top3 jest gwarantowane także bez AI; nie przedstawiać go jako 100% jakości modelu.

Nie zmieniamy kolejności lexical keys ani engineScore, nie dopisujemy słów spoza dekodera. Zachowujemy alternatywy. Slot_limit oraz missing_key muszą pozostać jawnymi ograniczeniami.

Walidacja generatora i powiązań: hash źródła, exact wersja/słownik, wszystkie raw interpretation IDs powiązane z wygenerowanym form proof, kategorie przypisane zgodnie z proof; unsupported classes fail zamiast ręcznego zgadywania. 76 testów stdlib mają przejść przed freeze. Fixture regeneruje się byte-identical. Check request hash, pełność i finite predykcji, category inventory oraz exact max mapping dla wszystkich grup, invariants kolejności/engineScore, loading info i trace obcięć.

Dane/kod/protokół trafiają do GitHub przed inferencją. Bez zmian hipotez, danych, normalizacji, reguł lub model selection po wyniku. Poprzednie eksperymenty zachowane. Bez merge do main; Draft PR #4. Po pomiarze raport i 11-punktowe milestone’y obu repos. Dalej: szerszy niezależny zbiór, rzeczywiste slates, telefon i interpunkcja przed wyborem silnika.

