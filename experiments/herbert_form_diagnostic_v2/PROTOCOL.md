# HerBERT form v2 — kontrola zachowania wcześniejszych wyników

V1 realny run38043798307 na91a5986e odtworzył zgłoszenie „Gdzie leży wieś ”:
mean wybiera Pracą, potem Praca. Praca to1 token (mean/sum -12.620338), Pracą2
tokeny (mean -8.603776, sum -17.207552). Sum wybiera Praca.
Na24 authored gold cases mean18/24, sum22/24,4 naprawy i0 regresji; rawTop3
23/24 w obu. Ending poprawny20→24/24, kapitalizacja22/24 w obu.
Pozostałe dwa błędy to Pracy→pracy; wszystkie te tokeny mają długość1.
Nie zmieniono aplikacji. To wynik diagnostyczny, nie dowód poprawności ogólnej.

## Pytanie przed zmianą scorera

Czy sum zachowuje wcześniejsze poprawne Top1/Top3 na wszystkich232 oryginalnych
żądaniach? Zbiory/window/population są utrzymywane osobno. Naprawa w jednym
zbiorze nie usprawiedliwia utraty poprawnego wyniku w innym.

## Zasady

- V1 kod, freeze, dataset i workflow pozostają byte-identical. V2 to osobny katalog
  i workflow na tej samej izolowanej gałęzi. Nie dobieramy współczynnika po wynikach.
- Ten sam trusted FP32 artifact/model/tokenizer, ORT1.21.1, threads2/1.
- Najpierw cała ścieżka V1:7 file hashes,2471 vectors,232 pięć-wejść/native-score
  parity i24+96 realnych pomiarów. Ponowne24 muszą odtworzyć zachowany V1 raport
  w tolerancji0.001 i bez zmian obu pełnych rankingów.
- Potem232 realne mean/sum wyjścia. Powiązanie vector/request/case musi być dokładne;
  gold pochodzi ze starego niezmienionego contract_mobile.prepare i frozen source.
- 7 testów kolektora: grupy, regresje niezależnie od napraw, rawTop3, unknown/missing
  gold, kompletność, rank trace i zewnętrzny transitive freeze.
- preservationPassed=true wymaga0 Top1 i0 Top3 regressions w KAŻDEJ historycznej
  suite/population/window. To próg diagnostycznej ochrony, nie production approval.
- Wszystkie232 wyjścia, zmiany i gold dostępne w scores.json; syntetyczne24 osobno.
  Quality FAIL pozostaje wynikiem raportu, nie błędem uploadu. CI success oznacza,
  że udało się kompletnie i zgodnie zmierzyć, a nie że sum jest zatwierdzone.

## Ograniczenia i kolejny krok

Gold historyczny/autorski nie jest zewnętrzną ślepą oceną. Brak phone geometry,
capture/routing potwierdzenia, czasów Android i confidence thresholds.
Sum może preferować krótszą tokenizację; poprawienie V1 nie rozstrzyga ogólnej
metody. Jeśli sum regresuje, zachować live mean i dobrać dalszy ogólny eksperyment.
Jeśli zachowuje wyniki, przed opt-in zmianą sprawdzić nowe różne słowa/odmiany,
szczególnie grupy o różnej długości tokenizacji, i phone guards.
Brak APK/model/langpack/rankingu zmiany, merge/release/tag/version bump.
Nie monitorować Actions dłużej niż60s total/run; użytkownik zgłasza zakończenie.
