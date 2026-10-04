# Metadane v5: objaśnienie schematu i instrukcja — protokół przed inferencją

Zlecenie użytkownika: „ok, działaj”, 2026-10-04. Wersja: ai-metadata-v5-1.
Izolowane porównanie offline. Nie zmienia klawiatury ani langpacka.

## Pytanie badawcze

Poprzednia próba wykazała, że tekstowe dołączenie surowych metadanych nie poprawiało
globalnie wyboru pisowni. Nie potwierdziła znajomości schematu przez modele. Sprawdzamy
osobno rozwinięcie kodów/powiązań w zrozumiałe opisy oraz podanie reguł ich użycia.
Kontrola instrukcji bez opisów pozwala ocenić, czy korzyść dotyczy metadanych, czy
samego dodatkowego polecenia. Wyniku nie nazywamy dowodem rozumienia modelu.

## Zamrożone źródła, modele i scoring

Dziedziczymy dokładny source-snapshot v5 oraz oryginalne funkcje modeli z
`experiments/ai_compare_v5`, zamrożonego wcześniej w
`00a7bf5999e8f6419a68c1884919e699c744a927`. Manifest wiąże hashe rzeczywistych zależności.
Poprzednie wyniki pozostają w `experiments/ai_compare_v5_results`, commit
`6c468719da474408b8ebadfcb03ebc184c32afda`. Dane/model/metody nowej próby utrwalamy
przed inferencją w osobnym katalogu; poprzednich plików nie edytujemy.

- ZIP v5 SHA256: aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb.
- Snapshot SHA256: 05270f8ae2c6d88bb8209cb00c83ff3d66ba788544f524ed27fbb5e0b4666794.
- CI ponownie weryfikuje pack/source byte-for-byte z udanego producer run 37202645255.
- HerBERT `allegro/herbert-base-cased`, rewizja
  `50e33e0567be0c0b313832314c586e3df0dc2297`: WWM średnia logp tokenów.
- MiniLM `MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli`, rewizja
  `0a71e92a985b6e1ad1828cf67ce9c459639c1dca`: NLI entailment literalnej pisowni.
- Qwen `Qwen/Qwen3-0.6B`, rewizja
  `c1899de289a04d12100db370d81485cdf75e47ca`: non-thinking, ocena jednoto­kenowych
  etykiet, uśrednienie forward/reverse.
- Scoring, ładowanie, parytet projekcji, CPU float32/dwa wątki i zależności zachowujemy.
  Nie uczymy modeli. Nie dobieramy nowych modeli lub scoringu po wynikach.

## Metadane i wspólny renderer

Zachowujemy każdy rzeczywisty związek lemma/POS/NAME/labels/surfaces, w tym stare
interpretation/proof i nowe lexicalReadings. Ten sam renderer działa dla wszystkich
kluczy. `glossary.json` zawiera tylko rozwinięcia kodów klasy gramatycznej i nazw
kategorii. Źródło kodów: oficjalna dokumentacja Morfeusz 2 z 2026-01-22, tabela 1:
https://download.sgjp.pl/morfeusz/Morfeusz2.pdf . Rozróżnienie analizy i wyboru interpretacji:
https://morfeusz.sgjp.pl/doc/about/ . Mapowania nie zawierają nazw testowanych słów.

Przykładowo subst rozwijamy do rzeczownika, nazwisko do nazwiska osoby,
nazwa_geograficzna do nazwy geograficznej. Nie zawężamy tej ostatniej do miasta.
Brak klasy NAME oznacza brak podanej klasy, nie dowód znaczenia pospolitego.
Kwalifikatory pozostają dosłowne, również nierozpoznane. Pełny lemat z rozróżnieniami
po dwukropku jest zachowany. Nie dopisujemy owocu, pojazdu, gatunku ptaka ani ulicy.

## Pięć kontrolowanych warunków

| Warunek | Opis metadanych | Dodatkowe reguły |
|---|---|---|
| plain | brak | brak |
| raw | identyczny zapis jak w poprzedniej próbie | brak |
| explained | opisy generowane z tych samych pól i globalnego glosariusza | brak |
| guided | identyczny opis jak explained | wspólna instrukcja |
| plain_guided | brak | ta sama instrukcja co guided |

Instrukcja wyjaśnia rolę alternatywnych interpretacji, lematu, wariantu i klas nazw;
nakazuje porównać je z kontekstem. Sama obecność nazwy własnej nie uzasadnia wielkiej
litery. Nieznane informacje nie są dopisywane. Dokładny tekst jest w `render_metadata.py`
i jest częścią zamrożonego payloadu. Nie dodajemy przykładów z poprawnymi odpowiedziami
ani opisów per słowo. Gold i oznaczenie nowego/powtórzonego przypadku nie trafiają do
wejścia modeli. Opcje i engineScore są identyczne między warunkami.

HerBERT otrzymuje opis/polecenie jako prefiks przed kontekstem; MiniLM w premise
przy niezmienionej hipotezie; Qwen w komunikacie użytkownika przy niezmienionym
system task i chat template. Instrukcja jest przeznaczona przede wszystkim dla modelu
dialogowego. Guided dla MLM/NLI to kontrolowana próba tekstowa, nie założenie, że
modele były uczone wykonywania poleceń.

Testy porównują wejścia plain/raw dla wszystkich powtórzonych przypadków z oryginalnymi
funkcjami w trzech adapterach. Dzięki temu nie zmieniamy równocześnie scoringu lub
hipotez. Warunek plain_guided izoluje wpływ polecenia od dopisanych danych.

## Populacje: 116 przypadków, 1160 zapytań na model

84 przypadki z poprzedniej próby słów: 64 formy, osiem historycznych rankingów,
sześć kontroli jednej formy, cztery niejednoznaczne i dwie kontrole brakującego klucza.
Ich wyniki i błędy były już widziane. To populacja `reused`, nie świeża walidacja.

32 nowe ręcznie napisane konteksty: po małej i wielkiej literze dla tych samych 16
kluczy, 16/16. To populacja `new`, raportowana oddzielnie. Nie powtarzają tekstów
poprzedniej próby, ale powstały po analizie jej wyników i mają znane klucze. To nowa
diagnostyka, nie ślepy korpus i nie niezależny dowód generalizacji. Nie optymalizujemy
nowych tekstów lub metadanych po bieżącej inferencji.

Dwa okna (dwa ostatnie słowa vs pełny lewy kontekst do 64 słów/4096 znaków) i pięć
warunków daje 116 × 2 × 5 = 1160 zapytań każdego z trzech modeli.
Interpunkcja z poprzedniej próby jest poza zakresem tej zmiany reprezentacji.

## Budżety i ranking

512 tokenów MLM/NLI, 1536 Qwen. Wszystkie pięć warunków pary case/window dostaje ten
sam zachowany kontekst. W razie potrzeby usuwamy wyłącznie najstarsze słowa kontekstu;
opisy i polecenie nie są obcinane. Usunięcia logujemy. Jeżeli same dane przekraczają
budżet, zadanie się zatrzymuje, nie pomija przypadku. Wszystkie budżety sprawdzamy
przed pierwszym scoringiem. Różne tokenizery mogą zachować różny kontekst między modelami.

Remisy zachowują default v5 i kolejność kluczy. Warianty nadal należą do jednego wpisu,
bez duplikowania CKDT. W obu populacjach form top 3 jest nasycone dwoma wariantami,
także bez SI; top 1 defaultu 32/64 reused i 16/32 new. Nie deklarujemy przewagi z top 3.
Historyczny replay pozostaje sortowaniem samych ocen modelu, bez kalibracji z geometrią.

## Metryki i uprzednio ustalone wnioski

Oddzielnie raportujemy suite/population/window/condition: exact top 1/top 3, lexical key
top 1/top 3, dostępność poprawnej formy, naprawy i regresje wobec defaultu.
Bezpośrednie pary: plain→raw, raw→explained, explained→guided, plain→plain_guided,
plain_guided→guided; liczymy zmiany, naprawy/regresje, bez łączenia nowych i reused.
Pełne rankingi, scores i ślady tokenizacji pozostają dostępne.

Lepszy guided niż explained wskazuje korzyść z dodatkowego polecenia w tej konfiguracji;
lepszy guided niż plain_guided wskazuje korzyść z podania danych przy tej samej instrukcji.
Nie dowodzi to mechanistycznego rozumienia pól. Korzyść globalna wymaga dodatniego bilansu
napraw/regresji na nowych formach i raportowania ryzyka replay, nie punktowych przykładów.
Nie wybieramy metody per słowo, nie stroimy progów lub blendu na tych wynikach.

## Wykonanie i trwałość

GitHub Actions: PR uruchamia tylko kontrakt; push/dispatch uruchamia trzy rzeczywiste
modele na oddzielnych hostach i collector. Pinned dependencies/actions odziedziczone
z poprzedniej próby. Zamrożony manifest wiąże nowe pliki, rzeczywiste stare zależności,
workflow, rewizje modeli i payload. Collector weryfikuje tożsamość commit/source/freeze,
kompletność finite predictions i odtwarza raporty. Brak modelu blokuje pełne porównanie.
Wagi nie są publikowane. Hostowe czasy/RSS nie są pomiarem Nubii Z60 Ultra LV 12/512 GB.

Przed inferencją zapisujemy atomowy commit. Poprawki błędów wykonania wymagają jawnej
przyczyny i nowego freeze; nie zmieniamy kryteriów po wyniku. Raporty poprzedniej próby
pozostają historią. Monitorowanie asystenta maksymalnie 60 sekund łącznie na build,
potem użytkownik zgłasza zakończenie. Checkpoint ma trafić do main obu repozytoriów,
wyłącznie jako dokumentacja. Bez merge/release, APK, zmiany paczki lub wyboru produkcyjnego.
