# Świeże konteksty polskiej kapitalizacji — próba v3

Zamrożone przed pierwszą inferencją. Autorskie teksty diagnostyczne przygotowane
przez asystenta po odczytaniu v2, **nie niezależny zewnętrzny benchmark**. Gold nie
pochodzi od osobnego anotatora. Nie przedstawiać tych wyników jako dowodu produkcyjnej
noninferiority. Użytkownik 2026-10-05 odłożył sprawdzanie licencji; ta decyzja pozwala
kontynuować obecne próby, nie ustanawia licencji ani praw redystrybucji modelu.

## Dane i sposób oceny

128 przypadków, po dwa okna = 256 zapytań na każdy z dwóch oryginalnych FP32 MLM:
- 64 świeże konteksty: 16 kluczy, każdy ma krótki/dłuższy kontekst dla małej/wielkiej formy.
- Osobno po 16 przypadków fresh_short_known_key, fresh_short_new_key,
  fresh_long_known_key, fresh_long_new_key. W każdym osiem małych i osiem wielkich.
- Znane klucze: łódź, malina, warszawska, buk, kruk, zając, kot, wilk.
- Klucze spoza wcześniejszej populacji new_natural: koza, wrona, sikora, kula,
  mucha, wierzba, orzeł, ryś. Żaden nie był w dotychczasowym v1/v2 forms gold.
- Krótkie teksty 4–6 słów; dłuższe 21–26. To ciągłe teksty o sytuacji, bez
  mechanicznego paddingu/filleru. Okno16 rzeczywiście ucina początek dłuższych tekstów,
  32 zachowuje całość. Nie testujemy jeszcze realnych prywatnych rozmów ani >32 słów.
- Zachowane 64 oryginalne historyczne forms v5, włącznie ze wszystkimi znanymi regresjami.
  Osobna populacja, bez mieszania z nowymi przypadkami. Brak interpunkcji/multi-key replay.

Źródłowe wpisy dla nowych kluczy skopiowane dokładnie z authenticated full v5 sidecar,
pack SHA aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb,
sidecar SHA 5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d.
Nie dodajemy kluczy ani znaczeń do słownika. Wszystkie pary/gold źródłowo poświadczone.
Metadane ograniczają dozwolone powierzchnie/default, nie są promptem/tekstem modelu.

Wspólny niezmieniony mlm.py v1: maskowanie wszystkich subtokenów całego dopisanego
słowa, oryginalny pełny vocab softmax, średnia logp. Tie-break przez źródłowy default.
Oryginalny AutoTokenizer i oryginalna wytrenowana głowica, bez instrukcji, nowych wag
ani kalibracji po zobaczeniu wyników. Kandydaci odwracani deterministycznie według ID,
oba okna naprzemiennie pierwsze. Bez ucasing adapterów lub wykluczania trudnych słów.

## Modele i bramki

HerBERT allegro/herbert-base-cased rev50e33e0567be0c0b313832314c586e3df0dc2297,
12 warstw; distilHerBERT BartekK/distilHerBERT-base-cased
rev7276461b7a8fd668aaf30313c03a68bd11aad642, 6 warstw. Oba oryginalne BERT MLM.
PyTorch2.8.0 CPU FP32, Transformers4.57.6, wątki2/1, trzy rozgrzewki pierwszej pary.
Tokenizer/source pairs i wszystkie targets sprawdzone przed ładowaniem wag.
Strict loading_info bez missing/mismatch/error oraz z dokładnym zbiorem nieużywanych
kluczy checkpointu: cztery znane pooler/SSO HerBERT, zero dla distilHerBERT;
pinned config/layers768;
trzy full-forward parity probes allclose atol1e-4/rtol1e-5, maxabs <=0.001 w collectorze.
Pełny trace mean/sum/target IDs/positions. Manifest wiąże dane, kod, workflow i stare
zależności. Collector wymaga obu kompletnych modeli z tego samego bieżącego commitu,
preflight/validation/result identities, hashy wag i dokładnego recomputation report.

Zamrożony **wstępny diagnostyczny** screen: dla każdej z czterech świeżych populacji
limit32 distil top1>=bieżącyHerBERT-1, regresje źródłowego defaultu<=HerBERT+1;
dodatkowo stare64 forms top1>=HerBERT-1. Poprzednie v2 stare46/64 vs50/64 sugeruje,
że ta część może FAIL — nie luzujemy jej. Screen FAIL jest wynikiem, nie powodem
zmiany metody lub niearchiwizowania wyników. Techniczne wykonanie może być SUCCESS
przy jakości FAIL. Nie deklarować statystycznego progu wdrożenia.

16/32: pełne decyzje, naprawy/regresje i liczba identycznych/różnych wejść osobno.
Bez automatycznej decyzji o default16: mała diagnoza nie wystarcza. Top3 par nasycone
z konstrukcji, nie dowód dodatkowej jakości SI. Koszty hosta z osobnych jobs nie są
kontrolowanym pomiarem Nubii. Oba modele rerun — referencja nie historyczna.

## Wykonanie i dalszy etap

Branch experiment/polish-mlm-fresh-v3, workflow polish-mlm-fresh-v3.yml.
PR wykonuje tylko kontrakty; push/manual uruchamia oba modele i collector.
ZIP wyników zawierają tylko raporty/predictions/validation/environment, bez wag.
Nie zmieniamy Androida/APK, default32/max64, live SI, interpunkcji i wcześniejszego
INT8 FAIL. Eksport/native fixtures/telefon dopiero po odczytaniu i ocenie tego wyniku.
Sprawdzanie licencji odłożone na prośbę użytkownika; brak kontaktu z autorami.
Monitorowanie Actions <=60 sekund TOTAL/run; potem użytkownik informuje o zakończeniu.

## Korekta wykonania loading-fix-v1 — 2026-10-06

Pierwotny zamrożony kod c1e9d3a7895f2a380bc75772985c88a53db32a4b i run
37363474711 pozostają historyczne. HerBERT zatrzymał się przed oceną jakości:
v3 odrzucał również znane nieużywane wagi pooler/SSO, które oryginalny test v1
sprawdzał jawnie. DistilHerBERT ukończył część runa; starego wyniku nie mieszamy
z nową referencją. Oba modele uruchamiane ponownie z nowego zamrożonego commitu.

Branch experiment/polish-mlm-v3-loading-fix-v1. Wspólny loading.py sprawdza przed
inferencją i w collectorze dokładnie bert.pooler.dense.bias/weight oraz
cls.sso.sso_relationship.bias/weight dla przypiętego HerBERT. Dla distilHerBERT
oczekuje pustego zbioru. Brakujące/mismatched/error, dodatkowe nieznane,
niepełne/zdublowane klucze lub brak dowodów loading_info są odrzucane.
Pełna głowica MLM i encoder nadal podlegają kontroli ładowania, hashom wag,
tożsamości config/revision oraz trzem full-forward parity probes.

Dane/gold/kandydaci/okna, metoda scoringu i bramki jakości są identyczne.
Niezmieniony request SHA256:
a20cad29b09554a9718f1d520d68c4e695c9274aac0b708801463f498097f53d.
Nowy manifest wykonania wiąże poprawiony kod i testy przed inferencją.
Protocol ID v3 opisuje te same dane; commit i SHA manifestu odróżniają rewizje.
Nie jest to ponowienie starego commitu ani poprawa jakości na podstawie gold.
