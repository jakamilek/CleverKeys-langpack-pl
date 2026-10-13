# Addytywne rozszerzenie zwykłych polskich form — próba v6

## Cel i wynik lokalny

Do zweryfikowanego v5 dodajemy zwykłe słowa i użyteczne odmiany. Nie usuwamy
niczego ze słownika bazowego. Wynik: **106 363 + 75 328 = 181 691 kluczy**.
Wszystkie stare rekordy kanoniczne i ich bajty rang, warianty kapitalizacji,
istniejące wpisy metadanych i unigrams pozostają zachowane. Stare powiązania
accent-map zachowują wzajemną kolejność; nowe formy otrzymują własne indeksy.
Wagi nowych form są wyliczane tą samą logarytmiczną kwantyzacją wordfreq co
w pierwotnym builderze CKDT. Geometria ustala ranking również przy większym
słowniku; zachowanie starych bajtów nie oznacza niezmiennych rang porządkowych.

Wszystkie dziewięć wcześniej publicznie zgłoszonych braków znalazło się w paczce.
To test pokrycia, nie dowód rozpoznawania gestów w Top3. Pierwszy etap nie dodaje
osobno list marek, skrótów, nazw własnych ani prywatnych adresów/ciągów.

## Przyczyna pierwotnych braków

Odtworzono prawdziwy `build_pl_preview.py --base-only` z limitami
top=300000, band=100000, limit=100000 i przypiętymi źródłami.
Native Hunspell potwierdził wszystkie dziewięć form. Filtr ASCII wymagający
jednocześnie Hunspell i AOSP odrzucił dodam, grzeje, odpowiadam, patrzysz,
poczekaj, podpowie i pozdrawiam. Kasami i nawilżane przeszły filtry, lecz zostały
odcięte przez limit wynikowego słownika. Szczegóły: original-nine-rejection-probes.json.
To utrata pokrycia producenta, niezależna od modelu SI. Nie stosujemy wyjątków
dla tych słów: są wyłącznie niezmienną kontrolą regresji.

## Dane i reguła globalna

- Wejściowy wewnętrzny ZIP v5 z udanego runu 37202645255, artifact
  `cleverkeys-pl-global-casing-trial` (11303920512), SHA-256
  `aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb`.
  Dictionary SHA-256: `a32f6a55bce7375e744d3d261d6ec9aad96dc64725ac429d4cb1d7225aed3c2a`.
  Pełny audit v5 jest sprawdzany według hasha z przypiętej paczki i musi
  obejmować dokładnie każdy stary klucz.
- Morfeusz2 1.99.15, SGJP `pl.sgjp.sgjp-2026.06.01`.
- wordfreq 3.2.0 z dokładnego commitu
  `912caf64b657478d1dff1138efdc078947d54bb1`; sprawdzamy instalacyjne direct_url.
  Pierwsze 300000 unikalnych poprawnych kandydatów polskiej listy.
- Kandydat musi mieć analizę całego pojedynczego słowa powiązaną z dokładną
  wygenerowaną formą: tożsamość lematu, pełnego tagu i klas nazwy. Mała litera
  musi być rzeczywiście wygenerowana; samo sondowanie wielką literą nie wystarcza.
- Wymagamy zwykłego odczytania; ignorujemy odczytania wyłącznie nazwowe,
  nieleksykalne oraz oznaczone jako dawne/historyczne/gwarowe. Inne poprawne
  współistniejące odczytania pozostają w dowodach.
- Dopuszczamy formę o Zipf >=2.0, albo formę o Zipf >=1.0, której dokładny
  zwykły lemat ma w obecnej bazie potwierdzoną formę o Zipf >=2.5.
  Nie generujemy masowo niepoświadczonych paradygmatów. 42449 dodatków pochodzi
  z reguły rodziny; 32879 przekracza próg częstości samej formy.
- Każdy nieobecny kandydat ma decyzję i pełne dowody w osobnym JSONL.
  Prywatny słownik nie jest wejściem, wyjątkiem, fixturem ani źródłem częstotliwości.

## Format, metadane i aplikacja

CKDT pozostaje v2, langpack version=6/API=1. Metadane nowych form zachowują
lemma/POS/surfaces/nameClasses/labels. Pomijamy puste tablice, zdublowane
category IDs oraz zbędną deklarację jedynej zwykłej małej pisowni (zapewnia ją
CKDT). Dwie źródłowo poświadczone kapitalizacje pozostają zadeklarowane.
Pełne tagi i dowody analizy/generowania są w audycie. Stary sidecar nie jest
przepisywany ani redukowany. Nie dodajemy ręcznych opisów znaczenia.

Sidecar: 91 527 wpisów, 28 123 935 bajtów, 1 844 963 węzły JSON. Wymagana
aplikacja z **limitem 2 000 000 węzłów** — wcześniejszy limit 1M odrzuci paczkę.
Aktualny kompatybilny kod: CleverKeysPL commit
`455eec6e59f66c2422d6c0a485f9dc1084dc49e6`, `trial/herbert-live-v1`.
Pozostają limity 32 MiB, 120000 wpisów, depth32, string16384, 32 tożsamości
sourceLemma, ścisłe schematy/duplikaty i staging/rollback importu. Nie zmieniamy
modelu, długości kontekstu, gestów, ustawień ani zakresu SI.

## Weryfikacja i dalszy test

Lokalnie: 50 testów producenta PASS; 18 testów prawdziwego konsumenta Kotlin
PASS (w tym dokładna granica 2M/2M+1); jego rzeczywisty czytnik CKDT i sidecaru
akceptuje całą paczkę, potwierdza zachowanie wszystkich starych wpisów oraz
50686 par współdzielących źródłową tożsamość nowych form. Test nie uruchamia
Androida, edytora ani SI. CI odtwarza paczkę, porównuje cały reviewed-report.json
i kompiluje te same przypięte pliki rzeczywistego konsumenta.

Po pomyślnym CI APK i paczki: zaktualizować aplikację, zaimportować wewnętrzny
ZIP langpacka, sprawdzić liczbę słów, wykonać dziewięć gestów regresyjnych,
sprawdzić łódź/Łódź, malina/Malina/maliną/Maliną, zwykłe formy i dłuższą sesję.
Osobno ocenić czas, RAM i ranking; pełniejszy słownik nie gwarantuje poprawy
wszystkich gestów. Import może wymagać ponownego otwarcia klawiatury.

Na końcu porównujemy prywatne wpisy tylko z dokładną pisownią i jawnymi
wariantami kapitalizacji. Nie usuwamy przez folding diakrytyków. Oczyszczony
eksport jest prywatny; obecny import słownika użytkownika scala i sam nie
usuwa wcześniej zapisanych duplikatów z telefonu.

Nie ma merge/tag/release. Monitoring Actions najwyżej 60 sekund łącznie na run;
dalszy stan użytkownik zgłasza sam.
