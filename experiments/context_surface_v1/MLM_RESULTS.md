# Pierwszy pomiar gotowego modelu — 2026-10-02

Wykonano rzeczywistą inferencję Polbert cased na CPU, bez treningu.
Wynik poprawia neutralny default, ale **nie wykazuje poprawy top-1 od
dłuższego kontekstu** na tych 14 skonstruowanych przykładach.

Model: dkleczek/bert-base-polish-cased-v1,
fed744e81ebd16cf099b5c64c40688bc3e6ace67, 132 775 010 parametrów.
Zamrożony kod/protokół przed inferencją:
098ee26130f38edad1f75f57e5ea25c21e7a98a9.
Adapter SHA256: e1f775981248bb9ff42e33e9ef03c753f1dce9d0d72c352af6c59bc98ad37da8.
Pełny opis score i ograniczeń: [MLM_PROTOCOL.md](MLM_PROTOCOL.md).

## Miary

| Miara | Neutralny default, oba okna | Model, 2 słowa | Model, do 64 słów |
|---|---:|---:|---:|
| Poprawny klucz dostępny | 13/14 | 13/14 | 13/14 |
| Poprawny klucz top-1 | 13/14 | 13/14 | 13/14 |
| Poprawna powierzchnia top-1 | 10/14 | 12/14 | 12/14 |
| Oczekiwana powierzchnia dostępna | 13/14 | 13/14 | 13/14 |

Paired długie vs krótkie: 0 zmienionych top-1, 0 naprawionych, 0 zepsutych.
Przeciw neutralnemu defaultowi model poprawił case004 (Łódź) i case007 (Malina).
Najważniejszy nierozwiązany błąd: case001 nadal proponuje łódź zamiast miasta Łódź.
Case012 celowo nie ma właściwego klucza w kandydaturach; resolver go nie odzyskuje.

| Case | 2 słowa | Dłuższy kontekst | Trafienie w obu |
|---|---|---|---|
| 001 | łódź | łódź | nie |
| 002 | łódź | łódź | tak |
| 003 | łódź | łódź | tak |
| 004 | Łódź | Łódź | tak |
| 005 | lód | lód | tak |
| 006 | mazowiecki | mazowiecki | tak |
| 007 | Malina | Malina | tak |
| 008 | malina | malina | tak |
| 009 | Łódź | Łódź | tak, jawny sentence_start |
| 010 | ŁÓDŹ | ŁÓDŹ | tak, jawny caps_lock |
| 011 | ChatGPT | ChatGPT | tak, brak sidecara |
| 012 | lód | lód | nie, brak klucza |
| 013 | łódź | łódź | tak, pusty kontekst/default |
| 014 | Łódź | Łódź | tak, jawny shift |

Same identyczne top-1 nie oznaczają ignorowania kontekstu przez model.
Dla case001/002 krótkie okno jest identyczne: oba dają log-score Łódź−łódź
= −2.369853. Długie okna dają odpowiednio −0.042233 i −1.807735.
Kontekst zmienia preferencję, ale w case001 nie przekracza decyzji wyboru.
Te różnice nie są skalibrowaną pewnością ani dowodem stabilnej jakości.

## Koszt i tokenizacja

W tym środowisku serwerowym (CPU float32, 2 wątki), dla 10 aktywnych
requests każdego okna, bez wykluczania warmup:

| Okno | Mediana | Min–max |
|---|---:|---:|
| 2 słowa | 77.61 ms | 73.17–88.67 ms |
| Dłuższe | 94.78 ms | 70.13–110.48 ms |

To tokenizacja i scoring grup wielowariantowych, bez ładowania modelu/zapisu
JSON. Nie jest to p95, benchmark telefonu ani pomiar end-to-end swipe.
Load wraz z pobraniem wag w tym uruchomieniu: 26.73 s.
Plik wag: 531 146 786 bajtów; wagi nie są redystrybuowane w repozytorium.
Nie ustalono jawnej licencji redystrybucji Polbert; kwestia produkcyjna otwarta.

łódź i Łódź mają po jednym różnym tokenie, malina i Malina po dwa różne
subwordy. Żaden oceniony wariant nie zawiera unk. W obrębie par tego fixture
liczby tokenów są równe, więc porównanie nie ma tu różnicy długości wariantów.
Żadnego wejścia nie obcięto budżetem 512 pozycji. Fixture nie testuje rzeczywistego
obciążenia 64 słów; 64 pozostaje górnym budżetem, nie zmierzonym optimum.

## Walidacja i proweniencja

- 39/39 testów stdlib PASS lokalnie.
- [Push CI 37046923040](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37046923040)
  dla 098ee26130f38edad1f75f57e5ea25c21e7a98a9: completed/success.
  CI sprawdza kontrakt i baseline; inferencja wykonana lokalnie, nie w CI.
- Model załadowany z pełną głowicą MLM i NSP, bez missing/unexpected/mismatched
  keys. Korzystamy z MLM; nie używamy NSP do wyboru powierzchni.
- Predykcje przeszły walidację request hash oraz kompletności wariantów.
- Gold labels tylko w evaluatorze, żadnych dodatkowych słów ani zmiany lexical rank.
- Źródłowy score zamrożony przed inferencją; bez retestowania alternatywnych score
  na gold labels tego fixture.

Artefakty w [results-2026-10-02](results-2026-10-02): requests, neutralny
baseline, wszystkie scores, report, paired summary, środowisko, manifest
SHA256 wag/tokenizatora oraz dowody dwóch zatrzymanych prób modelu.

| Plik | SHA256 |
|---|---|
| requests.json | f89fab6cb1469f8b847003d22aca7dbff22dc43a0cbb451e7c534a9d98611ceb |
| polbert-predictions.json | fdde06bcc30bfc5513745bd8d496987179f64b123e592e107ff4f1d537c1bbe6 |
| polbert-report.json | acd47864cafd794dd7e03ca4a3a341f9e6cc88a9b4112c9527a145b787e95c8c |

Wcześniejsze próby plT5 (brak standardowych sentinel-i) i Polish RoBERTa v2
(Łódź zawiera unk) nie dały wyników inferencji. Ich przyczyn nie wolno
przedstawiać jako porównania jakości modeli.

## Decyzja

Pierwszy gotowy model potrafi zmienić casing istniejącego kandydata, zachowując
alternatywę. Nie rozwiązał kluczowego przykładu z miastem w poprzednim zdaniu.
Nie ma podstaw do integracji tego modelu z Androidem ani do zmiany rankingu
słów. Kolejny krok to oddzielny większy zbiór sprawdzający wcześniejsze zdania,
inne nazwy własne i kontekst niejednoznaczny, potem porównanie kolejnego
zweryfikowanego modelu/metody. Parametry i kryteria należy zamrozić przed testem.
W późniejszej walidacji konieczne rzeczywiste slates i pomiar urządzenia.
