# Polski MLM v2 — zweryfikowany wynik, 2026-10-05

**distilHerBERT przechodzi zamrożony wstępny screen dla kolejności par pisowni,
Geotrend Distil go nie przechodzi. Żaden model nie jest zatwierdzony do wdrożenia.**
distilHerBERT ma wynik mieszany: lepszy na nowych naturalnych przykładach,
słabszy na starszych formach i nowej interpunkcji. Licencja wag nadal niewyjaśniona.

## Dowody wykonania

[Run 37359525824](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37359525824)
**SUCCESS**, kod `56b7d0f213fcdda1a8a5c245555bd3307fcc2133`.
Zadania: kontrakt 111930329726, distilHerBERT 111930393764, Geotrend 111930393996,
collector 111930931001 — wszystkie PASS. 11 niezmienionych starych i 8 nowych testów.
Oba modele: oryginalny tokenizer/backend i384requests przed wagami, strict loading_info
bez missing/mismatch/error/unexpected,384/384 ukończonych predictions.
Original full-head projection parity PASS: Geotrend0.0, distilHerBERT max0.0000343323.

Pobrano trzy ZIP, sprawdzono rozmiar/SHA z API, bezpiecznie odczytano członków,
następnie uruchomiono oryginalny frozen collector z GITHUB_SHA kodu próby.
Przeliczony comparison.json **dokładnie równy** archiwalnemu JSON i COMPARISON.md.
Raw predictions/model files/validation/preflight/reference identities również sprawdzone.

| Artefakt | ID | Bajty ZIP | SHA-256 ZIP |
|---|---:|---:|---|
| comparison | 11366575092 | 24229 | 2eb6b871f73985a9145d489536978f244b36199aac02307cad2082414fab0b79 |
| geotrend_distil | 11366302106 | 49965 | 092e51daa590ad63b10a2084e3c6edb61c9ec361170e6b72c71c7860f56c4240 |
| distilherbert | 11365304288 | 48839 | 8491fdb59f4c24c230aabc4a15de51f863aa80889c670a0d6e25d6dfc1271a88 |

Raw wyniki w podkatalogach geotrend_distil/distilherbert, osobne environment.txt;
pełny CI comparison.json/COMPARISON.md obok. Wagi/tokenizer vocab nie redystrybuowane.

## Trafność pierwszej propozycji (osobne populacje, limit32)

| Populacja/zadanie | Źródłowy default | Historyczny HerBERT | Geotrend Distil | distilHerBERT |
|---|---:|---:|---:|---:|
| Nowe naturalne formy | 16/32 | 24/32 | 21/32 | **25/32** |
| Historyczne formy v5 | 32/64 | **50/64** | 40/64 | 46/64 |
| Historyczny wielokluczowy replay | 3/8 | 7/8 | 1/8 | 7/8 |
| Sztuczny dystans wskazówki | 16/32 | 18/32 | 16/32 | 19/32 |
| Nowy przecinek/brak znaku | 12/24 | **20/24** | 11/24 | 16/24 |
| Historyczny przecinek/brak znaku | 8/20 | 15/20 | 10/20 | **17/20** |

Nie sumujemy tych populacji w jeden wynik. Replay obejmuje różne klucze bez kalibracji
z geometrycznymi rangami; nie jest obecnym planowanym wdrożeniem case-only SI.
Jedna forma6/6 jest deterministyczna; brakujący gold2/2 nieosiągalny; ambiguous4 bez gold.

distilHerBERT nowe naturalne: **16/16 małych** i9/16 wielkich,9napraw źródłowego
defaultu i0regresji defaultu. Względem HerBERTa2naprawy,1regresja (Buk), netto+1.
Zamrożony exploratory screen wymagał>=23/32 i<=3regresji defaultu: PASS25/32 i0.
To mały znany diagnostic screen, nie statystyczna noninferiority lub production approval.
Na starszych formach względem HerBERTa3naprawy i7regresji: netto-4, pełny wynik46/64.
Nie ukrywamy starszych regresji dlatego, że screen na nowej populacji przeszedł.

Geotrend nowe naturalne15/16 małych,6/16 wielkich,6napraw defaultu i1regresja:
FAILscreen21/32. Względem HerBERTa5napraw i8regresji. Na starych formach7napraw
i17regresji; replay6regresji bez napraw. Szybkość/rozmiar nie kompensują tu gorszej
trafności w obranej metodzie. Nie retunowano średniej logp/tokenizera po wyniku.

## Konkretne przykłady distilHerBERTa

W nowych naturalnych przypadkach poprawnie wybiera obie znaczeniowe formy
Łódź/łódź,Malina/malina,Warszawska/warszawska oraz małe ale/lub/tutaj.
Są to konkretne konteksty diagnostyczne, nie gwarancja rozpoznania wszystkich użyć.
Nowe pomyłki: Róża,Ale,Tutaj,Kruk,Buk,Zając,Kot proponowane za małą formą.
Żadnej małej gold formy nie zmienił błędnie na wielką w tej nowej32-populacji.

Starsze7regresji względem HerBERTa: Warszawska w form-warszawska-2,Lub w form-lub-4,
wilk w form-wilk-3,Kruk w form-kruk-4,Buk w form-buk-4,Zając w form-zając-2 i-4.
Obie formy pozostają na liście case-pair; top3 jest zatem z definicji nasycone także
bez SI i nie stanowi dowodu dodatkowej trafności. Nie dodawano zdublowanych kluczy.

## 16 versus32 słowa i interpunkcja

Wszystkie naturalne6–14 słów,stare1–13 i nowe punctuation2–3: wejście16/32 identyczne.
Równe wyniki nie uzasadniają zmiany defaultu ani deklaracji, że16 zachowuje jakość długiego tekstu.
Tylko sztuczny dystans23–25 słów zmienia wejście. distilHerBERT16=16/32,32=19/32;
3naprawy,0regresji32 względem16. Geotrend16=16/32,32=16/32;1naprawa i1regresja.
To autorski stress test znanych kluczy z usuniętą/zachowaną wskazówką, nie realne niezależne rozmowy.

Nowy przecinek: distilHerBERT10/12 przecinków i6/12 braku znaku;6pogorszeń względem
defaultu, a względem HerBERTa1naprawa/5regresji. Starsza interpunkcja17/20 jest lepsza,
co dodatkowo wskazuje na zmienność populacji. Geotrend1/12 przecinków,10/12 bez znaku.
Żaden wynik nie zatwierdza automatycznej interpunkcji; nie ogólne generowanie/koniec zdania.

## Rozmiar i koszt hosta — nie pomiar telefonu

| Model | Rzeczywiste parametry | Peak RSS całego procesu hosta MiB | Naturalne total p50/p95 ms |
|---|---:|---:|---:|
| Historyczny HerBERT v1 | 124494416 | 1426.48 | 84.3/96.5 |
| Geotrend Distil v2 | 60737405 | 605.48 | 50.0/54.8 |
| distilHerBERT v2 | 81967184 | 984.55 | 54.1/63.3 |

Osobne jobs/uruchomienia i historyczny host, bez identycznego sprzętu/control;
nie paired test szybkości, nie model-only RAM, nie PSS/energia/latencja Androida.
distilHerBERT ma około34% mniej parametrów od HerBERTa. Host984.55MiB nie dowodzi,
że na Nubii zużyje984MiB ani że problem~2.1GiB procesu zostanie rozwiązany.

Oryginalne pobrane weight-file identities (nie opublikowane):
- distilHerBERT pytorch_model.bin327906539B, SHA256
  1c5ee904a62f92b249c427a1d542f8934295b1bff435914217b3c80aae60f36b;
  modelrevision7276461b7a8fd668aaf30313c03a68bd11aad642.
- Geotrend model.safetensors242962316B, SHA256
  d58e76039a2d6664bf0f5b4bfdbb8227ffdcb0d498f3f054743572010a981574;
  modelrevision9002d311e35aac14575bf53ad4fa3d8f8b853c2b.
To nie rozmiary przyszłego ONNX/ZIP/APK; eksport może mieć inne powielone stałe/format.

## Decyzja i następny krok

distilHerBERT jest **kandydatem do dalszej weryfikacji case-only**, przy zachowaniu obu
źródłowych form i wszystkich dotychczasowych reguł Shift/sentences/editor/privacy/stale fallback.
Geotrend nie przechodzi tej próby jakości w niezmienionej metodzie. Żadnego modelu nie aktywowano.
Naturalny PASS nie kasuje historycznych regresji; interpunkcja pozostaje osobnym przyszłym zadaniem.

Przed uzasadnioną próbą telefonu: niezależny nowy zbiór kontekstów o realnych długościach
przy16/32, rozpisane małe/wielkie formy i zachowane regresje; wyjaśnienie praw użycia/
redystrybucji distilHerBERT. W publicznej karcie/listach plików i root repo nie znaleziono
deklaracji licencji; nie przyjmujemy licencji nauczyciela za licencję wag ucznia.
Nie wysłano wiadomości do autorów ani nie redystrybuowano wag. Dostępny obecnie import
HerBERTa na telefonie nadal akceptuje tylko wcześniej przypięty model, nie ten nowy plik.

Następnie oryginalny export FP32/parity/tokenizerconformance i rzeczywisty pomiar load,
latency/PSS/energii na Nubii; ewentualna kwantyzacja dopiero jako nowa próba ze swoimi
nieosłabionymi score/rank gates. Wcześniejsze INT8HerBERT nadal FAIL.
Bez nowego APK,liveAI/default32/max64 zmiany,merge/release/tag/version bump.
