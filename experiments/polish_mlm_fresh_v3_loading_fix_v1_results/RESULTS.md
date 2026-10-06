# Wyniki MLM v3 — loading-fix-v1
Data: 2026-10-06, Europe/Warsaw. Run37500235605 SUCCESS:
https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37500235605
Frozen code83fa31fd6071ba48b8e7828c58bb28ff2d49f2f1, draftPR11.
Oba oryginalne FP32 MLM ukończyły256 zapytań. Wszystkie jobs SUCCESS.
Kontrola SHA256 trzech ZIPów, identities/preflight/validation i niezależne
przeliczenie collector PASS; comparison.json oraz COMPARISON.md identyczne z CI.

## Trafność pierwszej propozycji
| Zbiór | Limit słów | HerBERT | distilHerBERT |
|---|---:|---:|---:|
| Świeże autorskie konteksty |16|62/64|63/64|
| Świeże autorskie konteksty |32|57/64|61/64|
| Historyczne forms v5 |16|50/64|46/64|
| Historyczne forms v5 |32|50/64|46/64|

Każda z4 świeżych populacji32 przechodzi wcześniej ustalony screen distil vs HerBERT:
short_known16vs15, short_new16vs16, long_known15vs13, long_new14vs13;
również warunek regresji źródłowego defaultu dla tych populacji PASS.
Historyczne64 FAIL: wymagane >=HerBERT-1 =49, uzyskano46.
exploratoryCaseCandidate=false. Nie obniżamy progu po wynikach.
Wniosek: distil obiecujący na nowych tekstach, lecz nie przechodzi całości
ustalonej kwalifikacji do kolejnego etapu. Nie produkcyjny wybór.

## Różnice i długość kontekstu
W historical32 distil traci7 poprawnych decyzji HerBERT i naprawia3 jego błędy.
Straty: nazwisko Warszawska po „pani”, Lub jako forma imienia Luba,
wilk jako zwierzę, Kruk po „doktor”, Buk po „nazwisko brzmi”,
dwa konteksty nazwiska Zając po „pan”.
Naprawy: imię Jagoda, pospolite lub, zając jako zwierzę.
To diagnoza błędów w tych tekstach, nie globalna reguła słownikowa.

W historical32 małe formy: HerBERT29/32, distil30/32;
wielkie formy: HerBERT21/32, distil16/32.
Na świeżych32 wielkie formy: HerBERT31/32, distil32/32.
Problem wielkich form w historical nie jest więc globalnym brakiem obsługi kapitalizacji.

96 par okien ma identyczny kontekst,32 dłuższe świeże pary różnią się rzeczywiście.
Zmiana16->32: HerBERT5 pogorszeń/0 napraw, distil2 pogorszenia/0 napraw.
Nie ustalamy default16 na tej małej autorskiej diagnozie.
Nie przeprowadzono >32-word ani reprezentatywnego prywatnego testu.

## Koszty i zakres
Parametry: HerBERT124494416; distil81967184 (około34% mniej).
Peak host RSS HerBERT1380.54MiB, distil952.75MiB, osobne jobs.
Host RAM i czasy nie są pomiarem Nubii ani porównaniem na kontrolowanym urządzeniu.
Brak pomiaru telefonu distil, eksportu ONNX/INT8, nowego APK/live SI i wag w repo.
HerBERT FP32 na Nubii wcześniej PSS całego procesu >2GiB; nie rekomendowany
do codziennego IME na podstawie tych kosztów.

## Metoda i ograniczenia
Te same128 przypadków,256 label-free requests:
a20cad29b09554a9718f1d520d68c4e695c9274aac0b708801463f498097f53d.
Ten sam scoring v1, modele/tokenizery/revisions, okna16/32, gold i kryteria.
Jedyna korekta wykonania: dokładne known-unused HerBERT loading keys,
wspólna bramka runner/collector; MLM encoder/head i parity nadal kontrolowane.
Świeże teksty napisane przez asystenta po v2, bez niezależnego anotatora.
Top3 dwóch form nasycone bez SI; nie przedstawiać jako poprawy SI.
Metadane ograniczają poświadczone formy/default, nie są semantic promptem.
Test nie ocenia jeszcze interpunkcji ani rankingu wielu różnych słów.

## Następny krok
Przeanalizować niezgodne przypadki i zasadność ostrożnego przestawiania propozycji.
Nie dopisywać wyjątków dla nazw ani stroić progu na tym zbiorze i przedstawiać
tego samego zbioru jako nowej niezależnej walidacji.
Jeśli zmieni się metoda rankingu/kwalifikacji, wymaga nowego protokołu i
odrębnej walidacji zamrożonej przed oceną. Obecne quality FAIL zachować.
Eksport i test Nubii wstrzymane według dotychczasowej warunkowej kolejności.
Słownik nadal odłożony. Licencja odłożona na prośbę użytkownika.

## Odtwarzanie
Uruchomić collector z frozen code83fa31... i GITHUB_SHA=83fa31... na katalogu
z oboma modelami. Nowy commit archiwum wyników nie jest commitem inferencji.
Source ZIP digests/ID/expiry w artifact-provenance.json.
Nie przepisywać failed run37363474711 ani mieszać jego wyników z tym runem.
