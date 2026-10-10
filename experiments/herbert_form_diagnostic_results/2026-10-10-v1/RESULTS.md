# HerBERT form diagnostic v1 — wynik zweryfikowany 2026-10-10

Run https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38043798307
SUCCESS na91a5986ee51d000107841bf5b1e0c32f5dc8bef3; contract i measure PASS.
Stare testy13+5 i nowe13 PASS. Oryginalny graph/tokenizer/feeds/native rank:
2471 vectors,232batches/532candidates PASS, max abs error0.0000448227;
single/batched różnica0 dla24 nowych czteropowierzchniowych przypadków.

Artifact11667680259 herbert-form-diagnostic-v1-reports,8794B ZIP;
SHA256 cf16f3053bf8ec2355cbb871fd8df7a2b4a995c92212dcb2a4ee93888f79688a.
ZIP pobrano/re-hashowano. scores.json zachowane verbatim; niezależnie przeliczono
kompletność, każdy ranking, średnią/sumę i wszystkie poniższe metryki.

| Metryka w24 jawnych przypadkach | Live mean | Diagnostic sum |
|---|---:|---:|
| Dokładny Top1 |18|22|
| Raw Top3 wewnątrz grupy4 |23|23|
| Poprawna forma bez wielkości liter |20|24|
| Poprawny rodzaj pierwszej litery |22|22|

Naprawy: form-01/02/03/04 (Pracą→Praca). Regresje na tych24:0.
Pozostałe błędy: form-11/12 (Pracy→pracy).

Dla „Gdzie leży wieś ” live mean daje Pracą,Praca,praca,pracą dokładnie jak
zgłoszona pierwsza para na telefonie. Praca ma1 token, wynik -12.620338;
Pracą ma2 tokeny, mean -8.603776, sum -17.207552. Sum wybiera Praca.
To silny trop zależności rankingu od normalizacji/długości tokenizacji, nie
dowód, że sama normalizacja jest jedyną przyczyną błędów językowych.

Direct host bez fallbacku odtwarza model preference; nie ustala przyczyny routing
konkretnego phone swipe. Authored gold i cztery naprawy jednej rodziny nie są
niezależną trafnością produkcyjną. Kolejny krok: V2 paired replay całej historii,
bez zmiany APK/live scorera na podstawie samego V1.
