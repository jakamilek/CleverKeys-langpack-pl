# Ostrożny ranking polskiej kapitalizacji — v4

Nowy protokół celu: ograniczyć błędne nadpisania poprawnego źródłowego defaultu,
kosztem możliwego pominięcia trafnej poprawki. Nie zmieniamy bramek starego v3;
jego distil historical quality FAIL pozostaje wynikiem i nie zostaje anulowany.
Brak produkcyjnej kwalifikacji, interpunkcji, live SI, APK i eksportu.

## Polityka i development

Jeden globalny próg przewagi mean-logp alternatywy nad defaultem. Gdy przewaga
jest dodatnia i >=progu, zamieniamy kolejność. W innym przypadku zostaje default.
Obie źródłowe formy zawsze pozostają w rankingu; brak wyjątków dla słów lub nazw.
To wynik punktowy modelu, nie kalibrowane prawdopodobieństwo ani „pewność %”.

Przed kalibracją ustalono siatkę0/.25/.5/1/2/3/4/6/8/abstain-all i cel
repairs - 4*regressions. Tie-break: mniej regresji, mniej zmian, większy próg.
Development: wszystkie256 requests poprzedniego v3, oba okna16/32, ze zweryfikowanego
archiwum b2c3342643a77ef01a04323034465acae8609c27, frozen code83fa31fd....
Kalibracja wybrała0.25 PRZED napisaniem64 nowych kontekstów i przed ich inferencją.
Development: raw216/256, repairs96/regressions8; gated214/256, repairs90/regressions4.
Nie przedstawiać tych wyników jako nowych wyników walidacyjnych.
calibration.json wiąże dokładne wejścia SHA; obliczenie odtwarzane przed testem.
Próg nie zmienia się po odczytaniu wyników holdout.

## Walidacja i zakres danych

64 nowe autorskie konteksty, rozłączne tekstowo z v1/v2/v3, po4 dla16 źródłowych
kluczy: short/long i lower/upper. Te klucze były już w development; jest to
holdout kontekstów, NIE holdout słów. Znane/new_key oznaczają historyczny podział
v1 natural, nie nieznajomość kluczy w kalibracji. Każda z4 grup ma16 przypadków,
po8 formlower/upper. Short<=16 słów; long17–32, okna16/32 zachowują różne wejścia.
Źródłowe wpisy/metadata identyczne jak w v3, bez ręcznie dopisanych opisów.
Konteksty/gold przygotował asystent po zobaczeniu v3; brak zewnętrznego anotatora
i brak niezależnego zewnętrznego benchmarku. Nie twierdzić humanblind walidacji.

Osobno64 historical forms v5 jako DEVELOPMENT REPLAY, obliczane ponownie dla
kontroli tożsamości i porównania raw/gated; nie kwalifikują nowej polityki.
128 cases *2 windows =256 requests/model. Nie mieszać populacji w screenie.
Top3 par jest zawsze nasycone i nie dowodzi korzyści SI.

## Zamrożony wstępny screen nowego celu

Primary: nowe64, okno16. Gated distil musi:
- mieć <=2 regresje źródłowego poprawnego defaultu na64;
- mieć nie więcej takich regresji niż raw distil;
- mieć utility repairs-4*regressions >=raw distil;
- poprawić top1 względem defaultu i rzeczywiście nadpisać >=8/64 przypadków;
- w każdej4 grupie top1>=baseline i regresje<=1.
Zero zmian lub abstain-all nie oznacza przejścia. Wszystkie warunki wymagane.
Okno32, rawHerBERT i replay opisowe, bez dobierania progu/okna po holdout.
Raport zawiera też stary historyczny próg distil>=HerBERT-1 jako development
referenceQualityGate, z jawnym FAIL/PASS. Nowy safety screen nie zastępuje go.
Wstępny PASS pozwala omówić dalszy etap, nie oznacza gotowości produkcyjnej.

## Modele i dowody

Te same oryginalne modele/tokenizery/revisions, CPUFP32 wątki2/1 co v3.
Nie zmieniamy mlm.py ani projection.py, celu maskowania i pełnego vocab softmax.
Oryginalna wytrenowana głowica. Dokładna znana unused-key bramka HerBERT,
brak missing/mismatch/error,3 original-forward parity probes i trace mean/sum.
Tokenizer preflight wszystkich targetów przed wagami w CI. Nie ma lokalnego
tokenizer preflight nowych tekstów; starego preflight v3 nie używamy jako dowodu.
Freeze wiąże policy/calibration/cases/code/workflow oraz wszystkie stare zależności.
Collector wymaga dwóch kompletnych modeli z tego samego frozen commitu i odtwarza
raw oraz gated reports. Fixture scores służą tylko testom kontraktów.

## Wykonanie

Branch experiment/polish-mlm-safe-rank-v4; workflow polish-mlm-safe-rank-v4.yml.
Inference push/manual, PR tylko kontrakty. ZIP bez wag. License review odłożony
przez użytkownika, brak przypisania domyślnej licencji/brak kontaktu z autorami.
Monitorowanie<=60s TOTAL/run. Telefon i pamięć distil nadal niezmierzone.
Słownik i czasy stacjonarnegoBS backlog. Nie zmieniać default32 aplikacji.
