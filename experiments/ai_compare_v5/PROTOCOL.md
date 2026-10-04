# Porównanie SI na metadanych langpacka v5 — protokół przed inferencją

Zlecenie użytkownika: „w takim razie porównuj”, 2026-10-04, Europe/Warsaw.
Wersja protokołu: ai-compare-v5-1. Izolowany eksperyment, nie zmiana klawiatury.
Telefon docelowy zgłoszony przez użytkownika: Nubia Z60 Ultra LV, 12 GB RAM / 512 GB.
Telefon nie jest dostępny w tym wykonaniu; poniższe pomiary odbywają się na hostach CI.

## Źródła i zakres

- Producer: jakamilek/CleverKeys-langpack-pl, commit
  041b28ae4587c531ef73e62933e9151cadb84c33.
- Wewnętrzny ZIP v5 SHA-256:
  aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb.
- Sidecar SHA-256:
  5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d.
- Gotowy udany run producer 37202645255; artifact cleverkeys-pl-global-casing-trial.
  Pipeline sprawdza dokładny ZIP i regeneruje source-snapshot.json byte-for-byte.
- Snapshot zachowuje dokładne runtime entries dla potrzebnych kluczy. Klucze bez
  sidecara dostają tylko rzeczywistą kanoniczną formę z CKDT, bez domyślonych atrybutów.
  Historyczne dziewięć wpisów ma pełne interpretation/proof; nowe mają lexicalReadings.
  Adapter sprowadza oba formaty do lemma/POS/NAME/labels/surfaces, zachowując powiązania.
- Wspólny renderer pól słownika nie dodaje opisów ptaka, owocu, miasta ani osoby.
  Wiedza per-word nie jest ręcznie dopisywana do słownika. Zob. NOTICE.txt.

To kontynuacja wcześniejszych izolowanych prób w experiment/context-surface-window-v1,
lecz ma osobny katalog, nowe konteksty i bieżące v5. Poprzednie wyniki są zachowane.
Wcześniejszy MiniLM z kategoriami był słabszy; nie zakładamy przewagi metadanych.

## Gotowe modele i rewizje

| Preset | Model | Przypięta rewizja | Rola |
|---|---|---|---|
| herbert | allegro/herbert-base-cased | 50e33e0567be0c0b313832314c586e3df0dc2297 | Polski MLM |
| minilm | MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli | 0a71e92a985b6e1ad1828cf67ce9c459639c1dca | NLI |
| qwen | Qwen/Qwen3-0.6B | c1899de289a04d12100db370d81485cdf75e47ca | Model generatywny, ograniczony wybór |

Qwen3.5-0.8B pozostaje przyszłym kandydatem, nie jest modelem tego pomiaru.
Qwen3-0.6B wybrano do pierwszego porównania z uwagi na istniejący format tekstowy
i obsługę we wspólnie przypiętym transformers. Nie deklarujemy przewagi nad 3.5.
Rewizję Qwen potwierdzono z https://huggingface.co/api/models/Qwen/Qwen3-0.6B.
Publiczne karty modeli: https://huggingface.co/allegro/herbert-base-cased,
https://huggingface.co/MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli,
https://huggingface.co/Qwen/Qwen3-0.6B.
Karty deklarują odpowiednio CC BY 4.0, MIT, Apache-2.0; wagi nie są redystrybuowane.
Bez trenowania/dostrajania, trust_remote_code=False, pełne pretrained heads.
Loading musi odrzucić missing/mismatched/error oraz niewyjaśnione unused weights.
HerBERT dopuszcza wyłącznie historyczne cztery nieużywane wagi poolera/SSO.

## Dane i jawne ograniczenia populacji

104 przypadki, 376 żądań na każdy model:

- 64 nowe ręcznie napisane konteksty dla 16 kluczy, po cztery na klucz,
  po 32 przypadki małych i wielkich liter. Klucze: łódź, malina, jagoda, róża,
  warszawska, ale, lub, tutaj, lis, wilk, kruk, sowa, piła, buk, zając, kot.
  Konteksty i gold to anotacja eksperymentu, nie metadane słownika.
- 8 odtworzeń historycznych rankingów. Zachowane dokładne top 5 i scores czterech
  gestów z logu użytkownika: olej, mleko, karton, łódź. Każdy ma dwa nowe konteksty.
  Nie posiadamy surowych punktów gestów ani nowego decoder replay v5.
- 6 kontroli jednowariantowych (Jan, Maria, łódzki), 4 niejednoznaczne bez gold,
  2 kontrole poprawnego klucza nieobecnego w dekoderze.
- 20 ręcznych prób przecinek/brak znaku PRZED znanym kolejnym słowem.
  Nie mierzymy całej interpunkcji, znaków końca zdania ani wspólnej skuteczności
  jednoczesnego wyboru słowa i znaku. Nie jest to test gotowej głowicy interpunkcji.

Konteksty powstały przed nową inferencją, ale po wcześniejszych wynikach projektu;
część kluczy jest wcześniej znana. To rozszerzona diagnostyka, nie ślepy zewnętrzny
benchmark i nie dowód generalizacji. Nie optymalizujemy tekstów/promptów po wyniku.

## Warunki wejścia i bezpieczeństwo interpretacji wyniku

Dwa okna: ostatnie 2 słowa vs oryginalny lewy tekst do 64 słów/4096 znaków.
Zachowane case, diakrytyka i interpunkcja. Bez tekstu po kursorze.
Dla każdej próby słowa porównujemy plain vs rzeczywiste metadata; w interpunkcji
tylko plain. Gold, contextType, diagnozy i sourceSlate nie trafiają do wejścia modelu.
Każdy model dostaje te same kandydatury; sourceText to wspólne etykiety pól i źródło.

Żądania zachowują engineScore, kandydatury i źródłowe alternatywy. Kolejność opcji
jest deterministycznie odwracana na podstawie caseId, bez użycia etykiety gold.
Qwen dodatkowo ocenia oba kierunki kolejności, uśredniając odpowiadające scores.

Token budget: HerBERT/NLI 512, Qwen 1536. Najstarsze słowa kontekstu można usuwać,
ale metadata nie jest obcinane. Plain/metadata tego samego przypadku mają ten sam
retained context w danym modelu. Logujemy obcięcia i długości; nie twierdzimy, że
modele z różnymi tokenizerami zawsze zachowają identyczne okno. Przekroczenie
budżetu samymi opcjami/metadanymi blokuje scoring; nie pomijamy trudnego przypadku.

## Zamrożone metody

- HerBERT: WWM, wszystkie tokeny całego dopisywanego wariantu maskowane.
  Score = średnia log prawdopodobieństw tokenów celu; suma i token IDs w trace.
  Średnia jest ustalona przed wynikami, aby ograniczyć czystą preferencję krótszej
  segmentacji. Nie izoluje wszystkich skutków tokenizacji. Metadata jest wspólnym
  tekstem pól źródła przed kontekstem; nie jest nową trenowaną głowicą interpretacji.
- MiniLM: istniejący NLI, log-softmax entailment, hipoteza poprawnej pisowni.
  Te same hipotezy w plain/metadata; metadata dopisane do premise. Nie powtarzamy
  dawnej agregacji max po kategoriach, która mogła faworyzować liczne klasy nazw.
  To inne, z góry zapisane użycie NLI; nie gwarantuje rozumienia pól źródłowych.
- Qwen: oficjalny chat template, enable_thinking=False. Nie generuje swobodnej
  odpowiedzi: oceniamy prawdopodobieństwa jednoto­kenowych liter opcji.
  Wynik wariantu to średnia logp w kolejności forward/reverse. Każda litera musi
  być jednym tokenem, inaczej pomiar się zatrzymuje. To model+adapter, nie porównanie
  samych architektur przy identycznym treningu lub głowicy.
- Interpunkcja: HerBERT WWM dla „słowo” vs „, słowo”; MiniLM hipoteza wstawienia
  przecinka/braku znaku; Qwen ograniczony wybór tych dwóch opcji. Takie adaptery
  są próbą rozszerzalności, nie dostrojonym produkcyjnym modułem.

## Ranking i metryki

Baseline to rzeczywisty default v5, po nim pozostałe dopuszczalne formy, z zachowaną
kolejnością kluczy dekodera. Dokładne remisy SI zachowują ten baseline.
W głównych 64 przypadkach obie formy pierwszego klucza mieszczą się w top 3 także
bez SI (32/64 top 1 i 64/64 top 3). Top 3 jest tu nasycone konstrukcją: raport
musi to zaznaczyć zamiast przedstawiać jako jakość SI. Top 1 pokazuje wpływ wyboru formy.

Historyczne replays mierzą osobno dokładny key/surface top 1 i top 3, z uwzględnieniem
presji slotów. Surowe modelowe scores porządkują tu wszystkie kandydatury bez
kalibrowanego blendu z geometr­ią. To eksperyment pomiędzy kluczami, nie propozycja
wdrożenia takiego sortowania do klawiatury. Nie stroimy wag engine/AI na tych danych.
Alternatywy pozostają w pełnym rankingu; brakujący klucz musi zostać nieosiągalny.
Kontrole jednowariantowe nie dowodzą rozpoznania znaczenia, ambiguous nie ma accuracy.

Raport: top 1/top 3, baseline, naprawy/regresje, paired metadata vs plain,
krótkie/długie okno, dostępność poprawnej formy, pełne rankingi/scores/gaps/tokenizacje.
Surowe scores/gaps nie są skalibrowaną pewnością ani wspólną skalą między modelami.
Porównanie jest podstawą shortlisty do niezależnego testu i telefonu, nie automatycznym
wyborem silnika produkcyjnego. Nie wybieramy modeli per słowo ani opisów po błędach.

## Wykonanie i weryfikacja

PyTorch CPU 2.8.0, transformers 4.57.6, numpy 2.2.6, sentencepiece 0.2.1,
sacremoses 0.1.1, float32, 2 wątki, eval/inference_mode, bez dropout/treningu.
Trzy oddzielne hosty CI (matrix); brak walki procesów o ten sam CPU, ale różnice
hostów ograniczają porównywanie opóźnień. Żadnych twierdzeń o mobilnej wydajności.
Hashy wszystkich faktycznie pobranych plików modelu i środowiska zapisujemy w wyniku.
Żadne wagi ani osobisty tekst telefonu nie są uploadowane w artifacts.

Zanim ruszy scoring: sprawdzenie wszystkich input budgets i complete head/revision,
parity zoptymalizowanego projection z pełnym forward dla HerBERT/Qwen.
Predykcje muszą obejmować 376 requests, być finite i dotyczyć tylko dopuszczalnych form.
Collector odtwarza raporty z raw scores, nie ufa gotowemu raportowi model job.
Niepełne trzy modele blokują uznanie porównania za ukończone.

Kod/dane/protokół/freeze-manifest trafiają atomowo do GitHuba PRZED inferencją.
freeze-manifest wiąże pliki SHA-256 i payload requests. Zmiany naprawiające wyłącznie
błąd wykonania wymagają osobnego commita, jawnej przyczyny i ponownego freeze;
nie wolno zmieniać danych/metody po obejrzeniu jakości i udawać tej samej próby.
Workflow odpala prawdziwe modele na push/dispatch, PR wykonuje tylko kontrakt stdlib.
Limit monitorowania przez asystenta: 60 sekund łącznie na build, potem użytkownik
zgłasza zakończenie. Runu nie mylimy z Androidem, APK ani releasem.

## Następny etap po wynikach

Zweryfikować komplet i ograniczenia przed wskazaniem shortlisty. Kolejny niezależny
zbiór i świeże slates rzeczywistych maźnięć poprzedzą decyzję produkcyjną.
Na Nubii: kwantyzacja z kontrolą zmiany jakości, zimny start, p50/p95 pojedynczej
podpowiedzi, pamięć ustalona/szczytowa, energia i płynność szybkiego pisania.
Geometric pozostaje dekoderem; spóźnione SI nie może blokować wejścia ani zmieniać
już zatwierdzonego tekstu. CTC nie jest warunkiem tego etapu. Opcje czasów BS
pozostają odłożonym backlogiem; ta próba nie zmienia APK/langpacka v5.
