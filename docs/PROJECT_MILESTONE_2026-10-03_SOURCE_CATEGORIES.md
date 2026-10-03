# Kamień milowy — inferencja na kategoriach źródłowych

Weryfikacja i zapis: 2026-10-03 UTC. Inferencja wykonana 2026-10-02.
Repo: jakamilek/CleverKeys-langpack-pl.
[Kamień milowy drugiego repozytorium](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-03_SOURCE_CATEGORIES.md).
Status: ukończony eksperyment offline; bez wyboru silnika produkcyjnego.

## 1. Zweryfikowane HEAD main i branch

Wspólny snapshot main przed dokumentacyjnymi commitami, sprawdzony ponownie bezpośrednio przed zapisem:
- jakamilek/CleverKeys-langpack-pl: 43c838007f439ec22831d2d233fcaa160c50999e.
- jakamilek/CleverKeysPL: 53f84e62474d0dc2f0833dfde8644b910c7d7012.

Zapis przesuwa main wyłącznie dokumentacją. Eksperyment nadal experiment/context-surface-window-v1 / Draft PR #4.
Poprzedni audyt źródeł: cd03c3002e7164eac5d972a2a8b502873177ca09.
Freeze przed inferencją: e654720e5bcbe9825747b74df2b7d82cdfac4eaa.
Komplet wyników: 90b836adb4970c3fcc1cf44bbbc3a2ea45e2da52. Bez merge/promocji eksperymentu do main.

## 2. Stan architektury

Oddzielne repozytoria, immutable core 100k, CKDT V2, dodatki i fallback w stanie poprzedniego milestone’u. Pakiet ma dostarczać dane/model, wspólny runtime wykonywać ranking. API v1, generator produkcji i Android nie zmienione.

Nowy generator eksperymentalny: dziewięć kluczy, 39 raw interpretacji lemma/tag/NAME/LABELS oraz 83 generatedFormProofs. Warianty syntezowane przez Morfeusz z pełnego lemma ID, filtrowane po lowercase key/POS/NAME. Utrzymano wszystkie interpretacje, również dodatkowe imiona/nazwiska/geografię i formy Malin/Łodzia. NAME lub POS przy pustym NAME projektowane do kategorii modelu; pełne TAG i LABELS pozostają w danych, lecz nie w hipotezie NLI.

Siedem kluczy ma odpowiedniki z wcześniejszego NATURAL, dodano łódzki i warszawski. łódzki ma jedną źródłowo potwierdzoną formę, nie wymyślono nazwiska Łódzki. Źródła ULIC/PESEL nie dołączone. Kategorie i formy pochodzą ze źródeł; konteksty testowe/gold są ręcznie anotowane.

## 3. Zaakceptowane decyzje i wyniki

Dane słownika mają pochodzić z obecnych lub dostępnych baz, bez ręcznych per-word opisów znaczeń. Główny cel nadal poprawny key i dokładny zapis w top3; top1 pomocniczo. Zachować alternatywy, lexical order i engineScore. Długi kontekst zachowuje case/diakrytykę/interpunkcję; tylko offline.

68 main (60 jawnie powtórzonych NATURAL bez czterech ulic + 8 nowych warszawski), 36 małych/32 wielkie litery. Wszystkie modele wykonały nową inferencję na 184 cases / 368 requests.

| System | Main top1 2 słowa | Main top1 długie | Main top3 długie | Probe top3 długie |
|---|---:|---:|---:|---:|
| Neutralny | 36/68 | 36/68 | 68/68 | 36/68 |
| NLI kategorie źródłowe | 37/68 | 33/68 | 68/68 | 33/68 |
| Ten sam NLI bez kategorii | 28/68 | 39/68 | 68/68 | 39/68 |
| Polbert WWM bez kategorii | 47/68 | 54/68 | 68/68 | 54/68 |
| HerBERT WWM bez kategorii | 53/68 | 59/68 | 68/68 | 59/68 |

Main top3 gwarantują dwa warianty pierwszego klucza także bez AI. Probe powtarza te same konteksty z celem #2 po dwóch wariantach innego klucza; jego top3 mechanicznie równa się main top1. Nie prezentować tego jako niezależnej accuracy albo 100% jakości AI.

NLI kategorie: 24/68 szerokich NAME/POS poprawnych, nie pełnych znaczeń. NLI preferował uppercase 65/68, trafił 31/32 wielkie i tylko 2/36 małe. Wobec tego samego NLI bez kategorii 13 napraw/19 regresji, netto -6. Rzeczywiste dane nie poprawiły tego konkretnego modelu/szablonu.

HerBERT nadal bez metadanych: reused60 52/60, new8 7/8; NLI kategorie 29/60 i 4/8, NLI bez 35/60 i 4/8; Polbert 49/60 i 5/8. Dziewięć błędów HerBERT: cztery owoce jagoda jako Jagoda, trzy kwiaty róża jako Róża, przymiotnik warszawska jako Warszawska i surname Warszawski jako warszawski w new006. Prawidłowa forma nadal druga w main.

## 4. Odrzucone lub nieuzasadnione rozwiązania

Nie promować tego małego NLI z ogólnymi hipotezami NAME/POS do rankingu produkcji. Nie odrzucać metadanych na podstawie niepowodzenia jednego sposobu wykorzystania. Zachować generator źródłowych wariantów i dowody.

Nie stroić po wynikach opisów, agregacji, progów, mieszanek ani modelu per słowo. Maksimum po kategoriach może faworyzować wariant z większą liczbą kategorii, ale preferencja uppercase występuje też przy jednej kategorii na wariant. Nie ustalono jednego wewnętrznego mechanizmu błędów. Test zmienia także treść hipotezy, nie izoluje wszystkich przyczyn.

Nie wybierać produkcyjnego HerBERT na małym, w większości powtórzonym zbiorze. Dobra pisownia ulicy może wynikać z wyboru nazwiska; nie deklarować rozumienia street. Nie zmieniać 100k lub CKDT pod wynik.

## 5. Planowane, niewdrożone

Przegląd gotowych silników/adapterów rankingu rzeczywiście korzystających z kategorii i porównanie z uprzednio zapisanym protokołem na szerszym niezależnym zbiorze. Osobno wpływ tokenizacji, rzeczywiste slates i presja UI, telefon, interpunkcja.

Produkcja: pełny generator sidecara dla słownika, parser/provider API v1, dłuższy InputConnection i świeżość snapshotów, tap-to-replace i uczenie pisowni użytkownika nadal niewdrożone. Generator tego etapu działa na dziewięciu zbadanych kluczach, nie jest wdrożeniem pełnego eksportu 100k.

## 6. Niezweryfikowane

Generalizacja, actual swipe beams, RAM/latencja/energia/kwantyzacja/ONNX, interpunkcja i wybór silnika. NLI nie mierzy wszystkich szczegółów TAG/LABELS, MLM nie korzysta z metadanych. Nie zmierzono poprawy źródłowych kategorii we wszystkich możliwych metodach.

Dodatkowa weryfikacja cache-file hashes modeli została przerwana; nie deklarować jej ukończenia. Pinned loading checks oraz realna inferencja zakończone przed przerwą. Po wznowieniu venv był niedostępny; zachowane scores zwalidowano i odtworzono summary standardowym Pythonem. Poprzedni model manifest pozostaje referencją z 37696cd3a4d575daf00beb833cb65b81ac7076c6. Przyczyny przerwy interfejsu nie ustalono.

## 7. Gałęzie i historia

experiment/context-surface-window-v1 aktywny, nadal Draft PR #4. Poprzednie wyniki WINDOW/DIAGNOSTIC/SENSE/NATURAL i SOURCE_METADATA zachowane. docs/architecture-runtime-langpack-separation-2026-10-02 oraz docs/architecture-langpack-plugin-model-2026-10-02: role z STATE_RECONSTRUCTION, HEAD nie sprawdzany ponownie. Nie przepisano historii ani nie scalono repozytoriów.

## 8. Artefakty, SHA i walidacja

[Raport i komplet wyników](https://github.com/jakamilek/CleverKeys-langpack-pl/tree/90b836adb4970c3fcc1cf44bbbc3a2ea45e2da52/experiments/context_surface_v1).
SOURCE_CATEGORY_PROTOCOL.md / SOURCE_CATEGORY_RESULTS.md; source_category_cases.py, source_category_experiment.py, test_source_category_experiment.py; source-category-cases/sidecar/requests.json; source-category-results-2026-10-02.

- Runner SHA256: 18b8b2249a003e8d6863bc56f3845c3a5add7d1f8d6a6d207923edfb4028a969.
- Cases SHA256: cc1be705a36fc3af50e8c0c1977268afbc2af0a70c534cb016ce8c90617c09d9.
- Sidecar SHA256: 6bbdf928c338d44ab3eddb76f8a1fe9f0b4a789cb1d51f55740f55826a21e2e2.
- Requests file SHA256: 264657153743e4f0b098ea011866efc1be5bb9c2511822853ef4a7e4de001d77.
- Request payload hash: bb5cec6e089aa18f04406c4a3a66f157e0325539f056a856a679894d3921ca2f.
- Summary SHA256: 4c43746730e5e80c1853267aa7d9b0bd2d35965a2a1724d91f79b8d62033ef15.
- Raport SHA256: f639753e035164a06746d9219669e2c05080cdcf75e059a1f3866430532e148d.
- Raport Git blob fd2581bcee52975286166507136274344af4c6af i summary Git blob 99caa3d73ec74b90409f2b2188e851d273e2fcc4; pinned readback zgodny.
- 76/76 testów stdlib PASS przed freeze i po wznowieniu. Fixture regeneruje się byte-identical. Wszystkie siedem frozen files zgodne z Git blob przed inferencją i po wznowieniu.
- Freeze CI push 37062857614 / PR 37062863016 success. Results CI push 37102657115 / PR 37102660333 success.
- CI testuje kontrakt, nie modele/Android. Trzy procesy inferencji exit0; 4 pliki predictions zwalidowane, pełne/finite/allowed. category inventory i max mapping dla wszystkich grup, lexical order i engineScore zachowane.
- NLI 1543 unique pairs/504 grupy; MLM po 578 tasks/482 grupy. Brak obcięć tokenowych. CPU float32, 2 threads/model, batch8.
- LoadingInfo kompletne; NLI/Polbert bez unexpected; HerBERT tylko wcześniej dopuszczone pooler/SSO. WWM selected-position parity 4.292e-6 Polbert / 3.052e-5 HerBERT.
- Czas po ładowaniu 15,31 s NLI / 31,37 s Polbert / 29,60 s HerBERT, procesy równoległe/cache: nie benchmark telefonu.
- environment, execution checks, previous model reference i artifacts-manifest zapisane. Nie redystrybuowano wag/full SGJP. Atrybucja wybranych danych z SOURCE_METADATA_AUDIT pozostaje obowiązująca.

Modele/revisions: NLI MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli 0a71e92a985b6e1ad1828cf67ce9c459639c1dca; Polbert dkleczek/bert-base-polish-cased-v1 fed744e81ebd16cf099b5c64c40688bc3e6ace67; HerBERT allegro/herbert-base-cased 50e33e0567be0c0b313832314c586e3df0dc2297. Shared MLM runner nadal ma historyczny suffix natural-sense-surface-v2, dane wiąże nowy request hash.

## 9. Ograniczenia i luki

Mały ręczny zbiór, większość kontekstów powtórzona, sztuczne slates. Łódzki jako nazwisko i Warszawska jako ulica nadal bez źródłowego potwierdzenia w tym dataset.

Single łódzki 8/8 i sentence_start 9/9 pisowni automatyczne także bez AI; unsupported_street 4/4 NLI kategorii/MLM to zapis, nie semantyka. missing_key 0/9 reachable, slot_limit 9/9 reachable i 0/9 top3, wszystkie systemy/okna. Ambiguous9 bez gold. Długi NLI: kategoria sentence_start tylko 1/9.

Historyczne CTC ł, eligibility PL ZIP, pl.cklm, niespójność ADR i licencja dystrybucji Polbert pozostają otwarte według poprzedniego milestone’u; nie sprawdzono ich ponownie. Długi kontekst wyłącznie offline, brak cross-key rerankingu.

## 10. Następny uzasadniony krok

Zachować źródłowy generator i poszukać gotowego rozwiązania/rankera potrafiącego wykorzystać szerokie klasy, z osobnym zamrożonym pomiarem i niezależnymi kontekstami. Nie kontynuować ręcznych opisów ani adaptować scoringu do obejrzanych błędów. Rzeczywisty dekoder, telefon i interpunkcja przed wyborem produkcji.

## 11. Delta względem SOURCE_METADATA

Wdrożono offline generator źródłowych interpretacji→warianty, ogólną projekcję NAME/POS, nowy protokół i realną inferencję NLI z/bez kategorii oraz obu MLM. Ujawniono regresję rankingu i silną preferencję nazw przez NLI. Testy 76 zamiast 66, 184 cases/368 requests, pełne wyniki i pinned readback/CI zachowane mimo przerwy. Nie zmieniono wcześniejszych wyników, produkcji ani wyboru silnika.
