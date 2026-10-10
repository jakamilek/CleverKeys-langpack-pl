# HerBERT V3 — przyrost oceny wynikający z kontekstu

Status: eksperyment zamrożony przed inferencją. Nie zmienia aplikacji.

## Uzasadnienie i jedna ustalona metoda

V1: mean wybiera Pracą zamiast Praca po „Gdzie leży wieś ”; sum poprawia cztery
przykłady z Praca. V2: sum naprawia 25, ale psuje 25 wcześniej poprawnych Top1
i raz usuwa poprawny kandydat z raw Top3. Globalna zamiana mean na sum odrzucona.

V3 sprawdza wyłącznie jeden nowy, z góry ustalony wynik:

`gain(surface) = sum_logp(context, surface) − sum_logp(empty_context, same_surface)`.

Oba wywołania używają identycznych target token IDs, masek, słownika, grafu WWM
i modelu FP32. Nie dzielimy różnicy przez liczbę tokenów, nie dobieramy alpha,
progu, reguły dla słowa ani wariantu wzoru po obejrzeniu wyników. Przy remisie
pozostaje dostarczona kolejność kandydatów. Neutralny kontekst to pusty ciąg,
wyłącznie CLS + tyle samo MASK + SEP, bez ręcznego promptu/metadanych.

To różnica ocen MLM, nie skalibrowane prawdopodobieństwo ani dokładny iloraz
wiarygodności zdania. Pusty kontekst zmienia pozycję tokenów i prior początku
zdania; odjęcie może usunąć użyteczną częstość. Nie zakładamy, że usuwa całą
stronniczość tokenizacji ani gwarantuje poprawę.

## Dane i ich rozdzielenie

- History: wszystkie 232 niezmienione żądania / 116 źródłowych przypadków,
  short/long, suite/population/window osobno. 224 labelled, 8 unlabelled; cztery
  labelled gold nie istnieją w dostarczonej paczce i nie są usuwane z oceny.
- Form24: istniejące 24 autorskie przypadki V1, z Praca/Pracą/Pracy,
  Malina/Maliną, Laska/Laską i łaska/łaską. Osobny diagnostyczny wynik;
  to cztery rodziny, nie szeroki niezależny test polskiej odmiany.
- New24: 24 nowe zdania, sześć źródłowych kluczy jagoda, róża, kruk, piła, buk,
  kot; po dwa gold common i dwa proper na klucz. Brak overlap pełnego kontekstu
  ze starszymi próbami. To nowe konteksty znanych słów, nie niewidziane słownictwo
  ani zewnętrzny blind benchmark. Lista pisowni pochodzi automatycznie z istniejącego
  zamrożonego ai_compare_v5/source-snapshot.json, byte-identical na parent commit.
  Ręcznie napisano tylko jawne zdania/gold benchmarku, bez opisów dla modelu.

## Kontrakt inferencji

1. Zewnętrzny freeze całego V3 i transitive V2/V1; gold i kod przed inferencją.
2. Pełny V2 replay: trusted siedem plików, oryginalne 2471 tokenizer vectors,
   232 paczki/532 kandydatów, pięć rzeczywistych feeds i native parity, Form24
   i single/batched. Świeże 232 mean/sum muszą odtworzyć zachowany raport V2:
   identyczne konteksty/surfaces/gold/groups/counts i oba pełne rankingi,
   tolerancja wyników 0.001. Archived outputs nie zastępują nowej inferencji.
3. Oryginalny FP32, ORT1.21.1 CPU 2/1, tokenizer z oryginalnej paczki. Fast vs
   portable parity dla pustego kontekstu i wszystkich nowych ciągów.
4. Baseline neutral dla każdej dokładnej uporządkowanej paczki; deduplikacja tylko
   wewnątrz tego hostowego testu. Zapisane neutral feeds/token IDs/mean/sum.
   Wymagana zgodność token IDs/masek z wejściem kontekstowym oraz neutralne
   single/batched mean i sum w tolerancji 0.001, także nierówne długości targetów.
5. New24: realny kontekstowy batch i single/batched dla każdego kandydata,
   identyczny trust, padding i separator. Gain wyliczany ze świeżych sum.
6. Wszystkie 280 mean/sum/gain i konteksty, baseline IDs, tokeny, pełne rankingi,
   neutral batches i wszystkie sparowane zmiany w scores.json. Nie raportować
   gold z modelu ani przewagi na podstawie samego SUCCESS workflow.

## Osobne metryki i gate

Exact Top1 i raw group Top3 dla labelled. FormTop1 porównuje pisownię po lower(),
bez usuwania ogonków. FormComparable: gold dostępny i co najmniej dwa różne
klucze lower() w paczce. CaseGivenGoldForm: porównanie kapitalizacji wyłącznie
wewnątrz rzeczywistej formy gold; eligible tylko gdy gold dostępny i jest więcej
niż jedna pisownia tego klucza. Duża litera niewłaściwego wyrazu nie zalicza case.
Osobne liczniki eligible, braków gold i unknown; nie zawyżać case jednoelementowymi
grupami ani udawać, że neutralne zdanie ma jedną prawidłową pisownię.

Preservation wymaga ZERO regresji exact Top1, raw Top3, FormTop1 i
CaseGivenGoldForm w KAŻDEJ grupie i każdym zbiorze względem mean. Naprawy nie
równoważą pogorszeń. Quality fail pozostaje wynikiem raportu, upload ma zadziałać.
Brak regresji nie wystarcza do wdrożenia: potrzebna rzeczywista poprawa odmiany,
szersze nowe rodziny form i osobne Android guards/pomiar kosztu na telefonie.

## Granice i dalsza decyzja

Host diagnostyczny, bez edytora użytkownika, śledzenia gestów, logowania kontekstu,
uczenia modelu, nowego eksportu/pakietu słownika, APK ani zmiany live scorer/350ms.
Nie mieszać raw scores z geometrią. Bez nowego współczynnika, wyboru modelu,
przełączenia SI ani reguły produkcyjnej. Jeśli gain regresuje, zachować live mean.
Jeśli test przejdzie, najpierw nowe źródłowe rodziny odmian i timing/cache/privacy
na Androidzie. Cache neutral host nie dowodzi taniego kosztu runtime.
Nie monitorować Actions ponad 60s total/run; zakończenie zgłasza użytkownik.
