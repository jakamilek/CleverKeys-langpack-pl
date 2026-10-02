# Kamień milowy — rzeczywista inferencja i długość kontekstu

**Data weryfikacji:** 2026-10-02, UTC.
**Status:** eksperyment offline z gotowym modelem; wynik niewystarczający do integracji.
**Repo:** jakamilek/CleverKeys-langpack-pl.
**Cross-repo:** [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-02_PRETRAINED_SURFACE_INFERENCE.md).
**Eksperyment:** [Draft PR #4](https://github.com/jakamilek/CleverKeys-langpack-pl/pull/4).

## 1. Stan GitHub przed zapisem dokumentów

| Repo | Branch | HEAD |
|---|---|---|
| jakamilek/CleverKeys-langpack-pl | main | c5e77a6b9c4f18b0b1a2b2e615d56f1985583e98 |
| jakamilek/CleverKeysPL | main | 9fbc0599beb9d7a8e0bd847e1960c71955c344ab |

Oba HEAD-y zweryfikowano na początku i przed zapisem etapu. Ten milestone przesuwa main wyłącznie dokumentacyjnym commitem. Nie promuje eksperymentu.

Branch experiment/context-surface-window-v1:
- base prototypu: 0832bf6f1353b0a2bc3042dbdd26f330ddc53e33;
- zamrożony adapter/protokół przed inferencją: 098ee26130f38edad1f75f57e5ea25c21e7a98a9;
- wynik i kompletne artefakty: 4b585dd286d88069342acb654ad588dfd3a8a7b1;
- kod i artefakty: [experiments/context_surface_v1](https://github.com/jakamilek/CleverKeys-langpack-pl/tree/4b585dd286d88069342acb654ad588dfd3a8a7b1/experiments/context_surface_v1).

## 2. Stan architektury

Oddzielne repozytoria, immutable 100k, CKDT V2 i legacy fallback pozostają w stanie poprzedniego milestone’u. Pakiet dostarcza wiedzę/model; runtime pozostaje wspólnym wykonawcą i rankerem.

Prototyp offline ma teraz realny adapter pretrained MLM. Ocenia warianty powierzchni istniejącego klucza, zachowuje alternatywy i nie zmienia engineScore ani kolejności kluczy. Dłuższy tekst przed kursorem zachowuje case, diakrytykę i interpunkcję, z budżetami 64 słów / 4096 znaków oraz osobnym limitem modelu 512 pozycji. To parametry eksperymentu, nie zmieniony tracker Android.

## 3. Ustalenia zaakceptowane i wykonane

Użytkownik zlecił dalszą pracę bez potrzeby swojego działania. Wykonano realną inferencję gotowego modelu, bez treningu:
- dkleczek/bert-base-polish-cased-v1;
- model revision fed744e81ebd16cf099b5c64c40688bc3e6ace67;
- pełne AutoModelForPreTraining, używane prediction_logits MLM, bez brakujących/losowych wag;
- whole-word mask wszystkich subwordów wariantu jednocześnie;
- score = suma log prawdopodobieństw tokenów na maskowanych pozycjach, wyłącznie wewnątrz klucza;
- ten sam suffix dla obu wariantów, tylko tekst przed kursorem, żadnych gold labels;
- CPU float32, 2 wątki, eval/inference_mode;
- wybór modelu oraz score zamrożone przed uzyskaniem wyników jakości.

Score MLM nie jest skalibrowanym prawdopodobieństwem całego słowa. Same scores nie upoważniają do zmiany lexical rank.

## 4. Wynik i jego znaczenie

14 ręcznie skonstruowanych przykładów, 28 żądań. Nie są to rzeczywiste slates z telefonu ani reprezentatywny benchmark.

| Miara | Neutralny default | Model, 2 słowa | Model, dłuższe okno |
|---|---:|---:|---:|
| Poprawny klucz top-1 | 13/14 | 13/14 | 13/14 |
| Poprawna powierzchnia top-1 | 10/14 | 12/14 | 12/14 |
| Oczekiwana powierzchnia dostępna | 13/14 | 13/14 | 13/14 |

Model poprawił case004 (Łódź) i case007 (Malina). Długie vs krótkie: 0 zmian top-1, 0 napraw, 0 zepsutych. Case001 z miastem we wcześniejszym zdaniu nadal wybiera łódź. Case012 nie ma właściwego klucza w slate.

Dłuższy kontekst zmienia score: margin Łódź−łódź w case001 wynosi −2.369853 dla 2 słów i −0.042233 dla długiego okna, ale decyzja nadal błędna. Nie wolno interpretować braku zmian top-1 jako braku wpływu kontekstu ani tego małego pomiaru jako dowodu, że dwa słowa wystarczą.

Latencja w tym środowisku dla 10 aktywnych requests/okno: mediana 77.61 ms vs 94.78 ms, bez wykluczenia warmup. Nie jest to pomiar telefonu/p95/end-to-end swipe. Wagi: 531 146 786 bajtów, 132 775 010 parametrów; nie zostały redystrybuowane.

## 5. Odrzucone lub zatrzymane próby

- plT5-small, revision 6ab71258c53f77f075fdda380992c0e691703f6b: opublikowany tokenizer ma extra_ids=0, standardowe sentinel-e nie spełniły kontraktu. Commit próby 39ce8a543a35018e030f6ac769fe3e8a206c4e4e. Zatrzymano przed scoringiem; brak wyników jakości. Nie dodawano losowych tokenów i nie zgadywano sentinel mapping.
- Polish RoBERTa v2, revision 4a0bda6ba39e467e204c913cd642700544fc4d3a: opublikowany tokenizer.json koduje Łódź jako [12,3,4584] z unk=3. Commit próby 175375420189d792b7c413ce01b6edaea2b9f96c. Zatrzymano przed scoringiem; brak wyników jakości.
- HerBERT: odczytano config architecture=BertModel, nie sprawdzono dostępności pretrained MLM w jego wagach; bez inferencji i bez wniosku o jakości.
- Nie zmieniano promptu, progu lub normalizacji po zobaczeniu wyników.
- Nie uznano 12/14 i samego zachowania dłuższego tekstu za gotowość wdrożenia.

Są to kontrole technicznej zgodności, nie porównanie jakości odrzuconych modeli.

## 6. Testy i ważne artefakty

39/39 testów stdlib PASS lokalnie. Pełny [push CI 37047409018](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37047409018) dla 4b585dd286d88069342acb654ad588dfd3a8a7b1: completed/success; PR CI 37047417306 również success. CI sprawdza kontrakt i neutralny baseline; realna inferencja wykonana lokalnie. To green tego eksperymentu, nie całego runtime Android.

MLM_PROTOCOL.md i MLM_RESULTS.md zawierają metodę, ograniczenia i reprodukcję. results-2026-10-02 zawiera wejścia, neutralny baseline, pełne predykcje, report, paired summary, environment-freeze, model-manifest SHA256 i attempts.json.

| Artefakt | SHA256 |
|---|---|
| requests.json | f89fab6cb1469f8b847003d22aca7dbff22dc43a0cbb451e7c534a9d98611ceb |
| polbert-predictions.json | fdde06bcc30bfc5513745bd8d496987179f64b123e592e107ff4f1d537c1bbe6 |
| polbert-report.json | acd47864cafd794dd7e03ca4a3a341f9e6cc88a9b4112c9527a145b787e95c8c |
| mlm_adapter.py | e1f775981248bb9ff42e33e9ef03c753f1dce9d0d72c352af6c59bc98ad37da8 |
| pytorch_model.bin | 79cf0790d5ad0c8343ecd61ad103240dbdaf0410328f8f0ddc9975c2d7ca3655 |

Request payload SHA e6db915401dbff00f0185d938a7bc095d261dc182c4ec44c804eb0b0a8abcda4. Modelowe predykcje przeszły walidator tego żądania. Kod i report odczytano również z GitHub po zapisie.

## 7. Rzeczy w planie, niewdrożone

Większa oddzielna ewaluacja rozróżnień z poprzednich zdań, innych nazw własnych oraz niejednoznacznych wskazówek; porównanie kolejnego poprawnie reprezentującego polskie formy modelu/metody. Następnie rzeczywiste slates, koszt urządzenia i projekt integracji wspólnego runtime.

Nie wdrożono Android InputConnection/snapshot freshness, parsera sidecara, commit/tap-to-replace, uczenia wariantów, nowych providerów ani produkcyjnego rerankingu. CKDT, 100k, manifesty i ZIP-y pozostają bez zmian. Historia Android nadal ma dotychczasowe ograniczenia.

## 8. Niezweryfikowane i ograniczenia

- Jakość na reprezentatywnych danych, koszt telefonu, energia, RAM, kwantyzacja, ONNX i dystrybucja.
- Licencja redystrybucji Polbert nie została jawnie ustalona; musi być wyjaśniona przed produkcją. W repo brak wag.
- Fixture nie osiąga budżetu 64 słów; to górny limit, nie pomiar obciążenia 64 słów.
- Wynik podzbioru gold labels nie generalizuje na użytkowników. Jawny sentence_start/shift/caps i jednoznaczne single-variant przypadki nie testują AI.
- Obcięcie tokenów może przeciąć starszy subword; raportuje truncation, ale nie jest segmentacją zdań.
- CTC ł→l i eligibility realnego PL ZIP pozostają osobnym otwartym warunkiem osiągalności przykładu.
- Brak pl.cklm, provider/parser API v1 i niespójność referencji ADR pozostają otwarte.

## 9. Gałęzie historyczne

experiment/context-surface-window-v1 pozostaje Draft, nie jest scalony. Pierwszy prototyp 2733671896b6d9a13af9907217011fdc20f0066e ma rolę historycznego baseline’u.

Branche docs/architecture-runtime-langpack-separation-2026-10-02 oraz docs/architecture-langpack-plugin-model-2026-10-02 zachowują role z STATE_RECONSTRUCTION; bez merge lub przepisania historii. Wcześniejszy FAIL S3 statycznego angielskiego LM nie został zniesiony tym eksperymentem.

## 10. Następny uzasadniony krok

Zamrozić oddzielny większy zestaw i kryteria poprawy przed testem kolejnego modelu/metody. Objąć rozstrzygające wcześniejsze zdania, przypadki sprzecznego kontekstu, brak pewności oraz inne nazwy własne. Zachować krótki baseline, pełne warianty i niezmieniony slate. Ten etap nie uzasadnia jeszcze promocji do main ani uruchomienia na telefonie.

## 11. Delta względem poprzedniego milestone’u

Od PROJECT_MILESTONE_2026-10-02_CONTEXT_SURFACE_PROTOTYPE:
- wykonano rzeczywistą inferencję gotowego modelu, wcześniej była tylko wymiana JSON;
- zamrożono metodę przed pomiarem i zapisano wszystkie wyniki/proweniencję;
- wykryto dwie istotne niezgodności opublikowanych tokenizerów;
- testy wzrosły z 30 do 39, push i PR CI green;
- potwierdzono poprawę względem defaultu, bez potwierdzonej poprawy od dłuższego okna;
- integracja produkcyjna oraz wymaganie użytkownika dotyczące skutecznego wykorzystania wcześniejszych zdań pozostają niezrealizowane.
