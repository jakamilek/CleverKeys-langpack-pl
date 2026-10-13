# Addytywne wznowienie odłożonych nazw i odmian v10

## Zaakceptowana baza

Użytkownik zaakceptował import i działanie paczki v9 na telefonie Nubia Z60 Ultra:
„działa bardzo dobrze. może nawet troszke szybciej”. Przyspieszenie jest obserwacją
użytkownika; nie mamy pomiaru PSS ani porównania czasów Androida.

Baza: wewnętrzny ZIP `cleverkeys-pl-shared-metadata-trial.zip` z udanego
[runu 38173087935](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38173087935),
SHA-256 `c1ffdac5ef607f183996abf6a4804490a0b5c43c39b6d4215975936062ba8677`.
APK: `jakamilek/CleverKeysPL@64943d82e4480c3e2afb5e3618a5e4e47fa4c6ff`,
runy 38173067500 i 38173069844 SUCCESS; APK SHA-256
`a9b226445fee81098d3fd278448fceba67a22c55731c4503e6de265590f69e39`.
V9 zachowuje 190 813 słów i 100 649 wpisów metadanych.

V10 działa na tym samym APK. Nie zmieniamy modelu SI, gestów, ustawień,
polityk kapitalizacji ani limitów importera. Nie ma merge, tagu, release ani
podniesienia wersji aplikacji. Prywatny eksport nie jest źródłem ani listą
wyjątków; końcowe usuwanie jego duplikatów nadal pozostaje osobnym zadaniem.

## Źródło i dobór

Wracamy do pełnego audytu nazw v8, potwierdzonego w udanym
[runie 38167348861](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38167348861).
`name-forms-audit.jsonl`, SHA-256
`18af9ce13103aeb969c6079729574ec327e8e4326daf9c5b5f5f3753b4c33177`.
Audyt ma 128 934 wiersze: 2511 już przyjętych nazw, 2206 kolizji z dominującymi
wyrazami obcymi i 124 217 form odłożonych ze względu na pojemność.
Najpierw mierzymy całą odłożoną pulę, następnie dobieramy wpisy według wcześniej
ustalonej kolejności grup i częstości polskiego wordfreq. Nie dopisujemy słów,
znaczeń ani końcówek ręcznie. Odrzucenie samego fragmentu nazwy i wykluczenia
źródłowe imion pozostają w mocy.

Źródła: Morfeusz2 1.99.15 / `pl.sgjp.sgjp-2026.06.01`, wordfreq 3.2.0,
commit `912caf64b657478d1dff1138efdc078947d54bb1`. Każdy instalowany dodatek
przechodzi ponowną analizę i generację w przypiętym natywnym SGJP. Kompletny
dowód musi być identyczny z audytem. Wagi nowych słów pochodzą z wordfreq;
rangi i rekordy wcześniejszych słów zachowujemy bajtowo. Reguła kolizji
nazwisk z dominującymi słowami obcymi jest niezmieniona.

## Współdzielenie i zgodność

Tablice `sourceAttributes` i `sourceLexemes` oraz ich indeksy pozostają
identyczne jak w v9. Nowe odczytania odwołują się do istniejącego rekordu tylko
przy dokładnym dopasowaniu wszystkich pól. Pozostałe nowe nagłówki źródłowe
zostają lokalne; mogą współdzielić identyczne istniejące atrybuty. To zachowuje
współdzielenie starych niezmiennych wpisów podczas podmiany na aktualnym APK.
Brak pola, pusta lista, wielkość liter, sufiks lematu, POS, NAME i LABELS
pozostają rozróżnione. Każdy nowy zakodowany wpis odtwarza się dokładnie.

## Wynik

Dodano 13 650 różnych kluczy. Razem 204 463 słowa i 114 299 wpisów metadanych.
Klasy źródłowe mogą się nakładać; poniższych liczb nie sumujemy:

| Klasa dodatków | Liczba kluczy |
|---|---:|
| Nazwiska | 9305 |
| Imiona | 1897 |
| Nazwy geograficzne | 4117 |
| Pseudonimy | 30 |
| Organizacje | 23 |

Są również inne drobne klasy nazw, wymienione w [raporcie](reviewed-report.json).
Przykłady: Eleonora, Gajewska, Gajewski, Gombrowicz, Jasio, Joela, Kasprowicza,
Nosowska, Odessa, Piotrkowa, Ronalda, Rudolfa, Rutkowskiego, Skierniewicach, Sudety.
To przykłady z wyniku źródłowego, nie ręczna lista włączeń.

Metadane: 30 387 503 bajty i 1 999 999 węzłów; pozostaje 1 węzeł do limitu 2M
oraz 5701 miejsc do limitu 120K wpisów. 110 567 potwierdzonych form pozostaje
odłożonych. Paczka zamyka bieżący budżet węzłów. Dalsza rozbudowa wymaga
osobnego etapu reprezentacji i pomiaru pamięci; nie usuwamy starszych słów
ani nie podnosimy tutaj żadnego limitu.

Paczka: `cleverkeys-pl-deferred-names-trial.zip`, 4 495 676 bajtów, SHA-256
`11dee57bc161bd18f1f8e0e6bbee80099a039a5240b70419f971fc297e4e78b7`.

## Weryfikacja i dostarczenie

Lokalne 79 testów producenta PASS. Rzeczywisty Kotlin konsument sprawdza
wszystkie wcześniejsze rekordy, wagi, widoki metadanych i zachowanie referencji
starych wpisów; osobno porównuje każdy dodatek z niezakodowaną oczekiwaną
postacią po potwierdzeniu natywnym. Obejmuje również prezentację powierzchni
i kapitalizacji oraz 28 testów parsera. Zimny odczyt, podmiana v9→v10 i ponowny
v10 mają osobne bramki 192 MiB z 16 MiB balastu. Wszystkie wymienione lokalne bramki rzeczywistego konsumenta PASS.
CI, tożsamość pobranych artefaktów i test telefonu pozostają do potwierdzenia.

CI pobiera oba przypięte wejścia, wymaga identycznego `reviewed-report.json`
i testuje niezmieniony commit konsumenta przed udostępnieniem artefaktu.
Audyt i oczekiwane rozwinięte nowe wpisy pozostają poza importowanym ZIP-em.
Po CI przekazujemy tylko wewnętrzną paczkę do importu na obecnym APK.
Monitorowanie Actions trwa najwyżej 60 sekund łącznie na run; potem użytkownik
informuje o zakończeniu. Native PSS i niezależna trafność swipe/SI nie są
wywnioskowane z testów hosta.
