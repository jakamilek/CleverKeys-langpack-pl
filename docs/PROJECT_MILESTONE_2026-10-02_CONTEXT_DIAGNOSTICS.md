# Kamień milowy — diagnoza kontekstu, modelu i punktowania

**Weryfikacja:** 2026-10-02 UTC.
**Repo:** jakamilek/CleverKeys-langpack-pl.
**Cross-repo:** [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-02_CONTEXT_DIAGNOSTICS.md).
**Status:** ukończony eksperyment offline; bez wyboru rozwiązania produkcyjnego.

## 1. GitHub i HEAD main przed zapisaniem tego milestone’u

| Repo | HEAD main |
|---|---|
| jakamilek/CleverKeys-langpack-pl | 8032c68f78a50bfd3fb892dced41b56dc321b03e |
| jakamilek/CleverKeysPL | a26d11d2fd7350e2dcbebf8c4b7f678fe776dc46 |

HEAD-y sprawdzono na początku i przed zapisem. Zapis milestone’u przesuwa main tylko dokumentacyjnym commitem. Eksperyment nie został promowany.

Branch experiment/context-surface-window-v1 / [Draft PR #4](https://github.com/jakamilek/CleverKeys-langpack-pl/pull/4):
- dane, evaluator i kryteria zamrożone przed inferencją: 98badb06118353a1c504bb47d04733624c63ebff;
- kod ukończonej inferencji po optymalizacji z kontrolą parity: 50e66f77a07ef7a00b3b7e8e27f3695a4c659275;
- kompletne wyniki i raport: df65d22b59a865a77939cb00653ac54e5735fb38.

## 2. Architektura

Oddzielne repozytoria, immutable 100k, CKDT V2 i legacy fallback w stanie poprzedniego milestone’u. Pakiet dostarcza wiedzę/model; wspólny runtime wykonuje ranking.

Eksperyment zachowuje tekst przed kursorem z case/interpunkcją, 64 słowa/4096 znaków oraz osobny limit 512 pozycji modelu. Projekcja wariantów następuje po grupowaniu kluczy, z zachowaniem alternatyw. Lexical rank i engineScore pozostają niezmienne. To nadal narzędzie offline, nie drugi produkcyjny polski ranker.

## 3. Autoryzacja i wykonane ustalenia

Użytkownik zlecił dalszą diagnozę po pytaniu o przyczyny błędów. Zrealizowano kontrolowany zestaw 48 cases / 96 requests: 32 główne, 8 context_lost, 8 ambiguous bez gold labels. Cztery klucze: łódź, malina, jagoda, róża.

Dwa modele bez treningu:
- Polbert fed744e81ebd16cf099b5c64c40688bc3e6ace67;
- HerBERT 50e33e0567be0c0b313832314c586e3df0dc2297.

HerBERT ma pretrained głowicę MLM, co wcześniej było niezweryfikowane. Brakujących/niedopasowanych wag nie ma; ignoruje się tylko jawnie zapisane wagi poolera/SSO, nieużywane przez factory MLM. Modele nie otrzymują gold labels, kategorii, pairId ani semantycznych atrybutów. Wagi nie są redystrybuowane.

Zamrożone metody: wwm (cały wariant masked), pll_variant (pojedyncze subwordy), pll_full_mean (rekonstrukcja całego fragmentu, mean). PLL wykorzystuje istniejącą metodę Salazar et al. (2020); nie budujemy modelu od zera.

## 4. Wynik i diagnoza

| Model / metoda | 2 słowa | Dłuższy kontekst | Naprawione / zepsute |
|---|---:|---:|---:|
| Polbert wwm | 20/32 | 23/32 | 8 / 5 |
| Polbert pll_variant | 19/32 | 22/32 | 6 / 3 |
| Polbert pll_full_mean | 20/32 | 23/32 | 4 / 1 |
| HerBERT wwm | 18/32 | 21/32 | 6 / 3 |
| HerBERT pll_variant | 17/32 | 20/32 | 3 / 0 |
| HerBERT pll_full_mean | 18/32 | 21/32 | 6 / 3 |

Neutralny lowercase default: 16/32. W skonstruowanych parach identyczne dwa ostatnie słowa ograniczają krótki wariant do maksimum 20/32. Długi kontekst przekracza ten limit, ale ma również regresje. Conflicting pozostaje słaby: 4–5/8. To kontrolowana diagnostyka szablonów, nie niezależna jakość dla użytkowników.

Legacy v1 oceniono oddzielnie: Polbert wwm/pll_variant nadal 12/14 dla obu okien; Polbert pll_full_mean 12→13/14. HerBERT wwm/full_mean 12→13/14, pll_variant 11→13/14. W długim oknie HerBERT i Polbert full_mean naprawiają pierwotny case001 Łódź. Case012 nadal nie ma poprawnego klucza.

Potwierdzone przyczyny/wykluczenia:
- case001 nie wynikał z braku formy, utraty kontekstu ani różnej liczby tokenów;
- łódź/Łódź są pojedynczymi tokenami w obu modelach: wwm i pll_variant są tutaj identyczne;
- zmiana modelu lub celu oceny zmienia decyzję na tym samym kontekście;
- naprawa jednego przykładu nie oznacza wyboru najlepszego systemu: HerBERT naprawia legacy, ale jest słabszy na v2;
- utrata informacji przez okno to osobne ograniczenie: context_lost daje 4/8 we wszystkich konfiguracjach;
- margin nie jest skalibrowaną pewnością: modele potrafią mieć znaczną preferencję w tekstach bez rozstrzygającej wskazówki.

Nie ustalono jednej wewnętrznej przyczyny błędów łączenia zdań/nazw własnych. Hipotezy o częstości i możliwościach semantycznych pozostają hipotezami.

## 5. Odrzucone skróty i nieukończone próby

Nie wybrano zwycięzcy do produkcji na szablonach ani jednym przykładzie. Nie dostrajano wag/progów/metod po wynikach. Nie przywrócono dwusłownej historii.

Pierwszą wolniejszą próbę v2 zatrzymano przed zapisem/ewaluacją. Zastąpiono zbędną projekcję vocab na wszystkich pozycjach projekcją tylko ocenianych pozycji, z parity wobec pełnego modelu. Dane, kryteria i funkcje celu pozostały te same. Kod przypięto ponownie przed ukończoną inferencją.

Zablokowane wcześniej plT5 standard sentinel i RoBERTa v2 unknown Łódź pozostają historycznymi kontrolami kontraktu, nie wynikami jakości modeli.

## 6. Artefakty, SHA i walidacja

[DIAGNOSTIC_RESULTS.md i kod](https://github.com/jakamilek/CleverKeys-langpack-pl/tree/df65d22b59a865a77939cb00653ac54e5735fb38/experiments/context_surface_v1).
diagnostic-results-2026-10-02: pełne scores 6 systemów / 2 zestawy, decyzje, summary, wejścia, metadata, environment, models-manifest i artifacts-manifest SHA256.

- Runner SHA256: 715f3d165130b486fb3fb74d42b33e4b783360013e2a68d772c853b89552db6d.
- Requests plik SHA256: f8b0004b48b55154b1a87017cdd85a8ab5cc48422a9dc469444411ad00b15289.
- Summary SHA256: 2489085be07f13b5801bbb9256937ae143975e86f2be0cea739a0d80f7ccfb02.
- 47/47 testów stdlib PASS lokalnie.
- [Push CI 37051613058](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37051613058) dla df65d22b59a865a77939cb00653ac54e5735fb38: completed/success; PR CI 37051622161 success.
- CI dotyczy kontraktu; inferencja realna lokalnie, nie w CI. Nie jest to green Android runtime.
- Wszystkie predykcje przeszły walidator request hash i dopuszczalnych/kompletnych wariantów.
- Parity maksymalnego błędu logitów: 4.292e-6 Polbert / 3.052e-5 HerBERT.
- Replay v1 wwm Polbert: maksymalna różnica score 6.676e-6, te same oceniane tożsamości i decyzje.
- Summary odczytano ponownie z przypiętego GitHub po zapisie.

## 7. Planowane, niewdrożone

Jawne znaczenia przypisane do surface variants i model wykorzystujący te znaczenia w eksperymencie. Niezależna ewaluacja, rzeczywiste slates, kalibracja przy braku pewności i pomiar urządzenia.

Nie ma integracji InputConnection/snapshot freshness, provider/parser v1, commit/tap-to-replace, uczenia casing-u ani produkcyjnego rerankingu. Android nadal ma dotychczasową historię. CKDT, 100k i pakiet ZIP bez zmian.

## 8. Niezweryfikowane i ograniczenia

Szablony powstały po v1; nie są niezależną próbą jakości. Kategorie i pary są skorelowane, nie wolno wnioskować statystycznej istotności. Wybór modelu obejmuje też tokenizer i trening, nie izoluje samych wag/architektury.

Unequal variant token lengths w HerBERT mogą wpływać na sumy; scores nie są wspólną skalą między metodami/modelami ani skalibrowaną pewnością. Brak jawnego wyboru sense z atrybutów słownika.

Licencja dystrybucji Polbert pozostaje nieustalona; HerBERT model card CC BY 4.0. Rozmiar/latencja/energia/RAM/kwantyzacja na telefonie niezweryfikowane; PLL to kosztowna diagnostyka. CTC ł i eligibility rzeczywistego PL ZIP pozostają otwarte, podobnie pl.cklm i niespójność ADR.

## 9. Gałęzie historyczne

experiment/context-surface-window-v1 nadal Draft. Wyniki v1 w 4b585dd286d88069342acb654ad588dfd3a8a7b1 zachowują rolę wcześniejszego baseline’u; niczego nie usunięto.

Branche docs/architecture-runtime-langpack-separation-2026-10-02 oraz docs/architecture-langpack-plugin-model-2026-10-02 zachowują role z STATE_RECONSTRUCTION. Nie przeprowadzano merge ani przepisania historii. FAIL S3 statycznego angielskiego LM nadal jest oddzielnym historycznym wynikiem.

## 10. Następny uzasadniony krok

Przypisać jawne znaczenia do dopuszczalnych wariantów w danych eksperymentu i porównać istniejący model interpretujący te znaczenia z zamrożonym baseline’em. Objąć konflikty i brak rozstrzygającej informacji. Potem niezależna próba z rzeczywistymi slates, kalibracja i koszt telefonu. Brak podstaw do promocji eksperymentu lub wyboru rozwiązania produkcyjnego.

## 11. Delta

Od PROJECT_MILESTONE_2026-10-02_PRETRAINED_SURFACE_INFERENCE:
- dodano kontrolowaną większą diagnozę, drugi gotowy model i trzy metody;
- potwierdzono net +3/32 od dłuższego okna, wcześniej nie było poprawy na 14 przypadkach;
- wyjaśniono wpływ funkcji celu/modelu na pierwotne Łódź i wykluczono długość subwordów;
- ujawniono regresje, słabość sprzecznych opisów i brak kalibracji;
- zweryfikowano pretrained głowicę HerBERT, wcześniej niezweryfikowaną;
- wzrosła liczba testów 39→47; zachowano pełną proweniencję;
- produkcja i jawna interpretacja znaczeń z atrybutów nadal niewdrożone.
