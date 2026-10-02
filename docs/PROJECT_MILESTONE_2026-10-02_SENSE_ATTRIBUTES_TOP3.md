# Kamień milowy — znaczenia wariantów i kryterium top 3

**Weryfikacja:** 2026-10-02 UTC.
**Repo:** jakamilek/CleverKeys-langpack-pl.
**Cross-repo:** [jakamilek/CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-02_SENSE_ATTRIBUTES_TOP3.md).
**Status:** ukończony izolowany eksperyment offline; bez wyboru silnika produkcyjnego.

## 1. Zweryfikowany GitHub i snapshot main przed zapisaniem obu dokumentów

| Repo | HEAD main |
|---|---|
| jakamilek/CleverKeys-langpack-pl | 99f87aed2a80f0b4db2d1f85953f9e5d83ebd4f3 |
| jakamilek/CleverKeysPL | 2552adc8223677d698ce7d5d5b08931e5d154e00 |

To wspólny snapshot przed dokumentacyjnymi commitami obu milestone’ów, sprawdzony ponownie przed zapisem. Zapis przesuwa main wyłącznie dokumentacją. Eksperyment nie został promowany.

Branch experiment/context-surface-window-v1 / [Draft PR #4](https://github.com/jakamilek/CleverKeys-langpack-pl/pull/4):
- poprzednie wyniki diagnostyki v2: df65d22b59a865a77939cb00653ac54e5735fb38;
- freeze kodu, danych i kryteriów przed inferencją: 23544abd04fcb540f4df91bd170cad5707e67070;
- kompletne wyniki znaczeń i top 3: 55bb179a1d308cf7a7f7d4049ec6e3f060719e4c.

## 2. Stan architektury

Oddzielne repozytoria, immutable 100k, CKDT V2 i legacy fallback w stanie poprzedniego milestone’u. Pakiet dostarcza wiedzę/model, wspólny runtime wykonuje ranking. Eksperyment pozostaje offline; nie dodano drugiego produkcyjnego polskiego rankera.

Do ręcznego sidecara eksperymentu dodano senses (id/kind/descriptionPl) oraz senseIds przy wariantach. Jeden lowercase surfaceKey nadal grupuje łódź/Łódź. Znaczenie boat powiązano z łódź, city z Łódź. Dopiero ten eksperyment ma jawne powiązanie znaczenie–wariant; produkcyjny kontrakt API v1 nie został zmieniony.

Okna 2 i do 64 słów/4096 znaków, zachowany case/diakrytyka/interpunkcja; dodatkowy limit NLI 512 pozycji. Warianty po dedupe kluczy, alternatywy zachowane. Lexical order i engineScore bez zmian.

## 3. Ustalenia i autoryzacja użytkownika

Użytkownik zlecił rozpoczęcie punktu 1: test słownika ze znaczeniami. Uściślił, że poprawna forma w pierwszych trzech miejscach jest bardzo dobrym wynikiem.

Główny cel: poprawny klucz i dokładny zapis w top 3; top 1 dodatkowo. To zastępuje wcześniejsze robocze kryterium dwóch propozycji. Nie wymagamy perfekcyjnego top 1. Interpunkcję należy brać pod uwagę przy przyszłym wyborze silnika, ale nie była zadaniem tej inferencji.

Gotowy model NLI bez treningu: MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli, revision 0a71e92a985b6e1ad1828cf67ce9c459639c1dca. Factory AutoModelForSequenceClassification; kompletne pretrained wagi bez missing/unexpected/mismatched/error keys. Karta autora deklaruje MIT. Polski nie ma opublikowanego wyniku XNLI w karcie; wykonano własną próbę diagnostyczną.

## 4. Wyniki i interpretacja

48 niezmienionych cases v2 (32 główne, 8 context_lost, 8 ambiguous bez gold labels) plus 32 osobne top3_probe z powtórzonymi kontekstami. Łącznie 80 cases / 160 requests. Probe to sztuczne slates, nie maźnięcia: właściwy klucz drugi, pierwszy ma dwa warianty; wybrana forma celu zajmuje miejsce 3, alternatywa 4.

| System | Główne top 1: 2 słowa | Główne top 1: długie | Główne top 3: długie | Osobne probe top 3: długie |
|---|---:|---:|---:|---:|
| Neutralny default | 16/32 | 16/32 | 32/32 | 16/32 |
| NLI z opisami znaczeń | 18/32 | 24/32 | 32/32 | 24/32 |
| Ten sam NLI bez opisów | 14/32 | 16/32 | 32/32 | 16/32 |
| NLI z zamienionymi opisami | 14/32 | 8/32 | 32/32 | 8/32 |
| Polbert wwm, replay v2 | 20/32 | 23/32 | 32/32 | 23/32 |

Pełne pozostałe metody w SENSE_RESULTS.md. Na głównej próbie top 3 jest gwarantowane przez dwa warianty pierwszego klucza, również bez AI. Nie przedstawiać 32/32 jako jakości modelu. Osobny probe ujawnia presję limitu UI, ale powtarza konteksty i nie zwiększa niezależnej populacji.

NLI z opisami, długie okno: direct 7/8, previous 8/8, distant_retained 8/8, conflicting 1/8. Zatem 23/24 bez konfliktów; sprzeczne opisy pozostają wyraźną regresją względem Polbert wwm 4/8. Wobec NLI bez opisów naprawiono 10, zepsuto 2; wobec Polbert wwm naprawiono 5, zepsuto 4. Net +1 względem Polbert nie rozstrzyga wyboru modelu.

Kontrola swap zmienia preferowaną formę w 32/32 głównych przypadków obu okien. To mechaniczne przeniesienie tych samych ocen na przeciwny wariant, nie samodzielny dowód rozumienia kontekstu. Ablacja bez opisów zmienia też treść hipotezy, nie izoluje wszystkich przyczyn.

context_lost 4/8 top 1 we wszystkich systemach; ambiguous bez accuracy. Nie ustalono jednej wewnętrznej przyczyny błędów konfliktów. Hipoteza NLI ogólnie opisuje kontekst; nie zmierzono osobno wpływu odniesienia do aktualnego dopisywanego słowa.

## 5. Odrzucone skróty i wcześniejsze próby

Nie wybrano silnika produkcyjnego na jednym wyniku albo przykładzie Łódź. Nie strojono opisów, progów ani scoringu po wyniku. Nie traktujemy surowego NLI score jako skalibrowanej pewności. Nie dodano duplikatów CKDT ani nowego lexical rankingu.

Zablokowane historycznie plT5 sentinel i RoBERTa v2 unknown Łódź pozostają kontrolami kontraktu, nie wynikami jakości. NLI nie naprawia historycznej luki CTC ł.

## 6. Planowane, jeszcze niewdrożone

Nowy niezależny zestaw zwykłych zdań z aktualnym znaczeniem i sprzecznymi wskazówkami; rzeczywiste slates dekodera, kalibracja i koszt telefonu. Osobna ewaluacja interpunkcji przy wyborze silnika.

Generator rzeczywistych danych sense→surface, parser/provider API v1, odczyt InputConnection i świeżość snapshotów, tap-to-replace, uczenie pisowni i Android integration nadal niewdrożone. Android ma dotychczasową historię; długie okno działa wyłącznie offline.

## 7. Niezweryfikowane

Jakość dla użytkowników, coverage znaczeń w 100k, generalizacja poza cztery klucze, polska interpunkcja, wieloznaczność z wieloma znaczeniami na formę (obsługiwana strukturalnie, nie zmierzona jakościowo), ONNX/kwantyzacja, RAM/energia/latencja na telefonie.

Wagi NLI mają 106 995 075 parametrów i 427 997 022 bajty safetensors. 4,09 s całej inferencji na tym CPU z cache/powtórzeniami nie jest pomiarem jednego maźnięcia ani urządzenia. Licencja redystrybucji Polbert pozostaje nieustalona w poprzednim milestone’u.

## 8. Artefakty, SHA i walidacja

[Raport, kod i pełne wyniki](https://github.com/jakamilek/CleverKeys-langpack-pl/tree/55bb179a1d308cf7a7f7d4049ec6e3f060719e4c/experiments/context_surface_v1).
SENSE_PROTOCOL.md, SENSE_RESULTS.md, sense_experiment.py, sense-cases.json, sense-sidecar.json, sense-requests.json oraz sense-results-2026-10-02.

- Runner SHA256: 3bcf4b92c6cccd7aaefd4db77fde8cb4d39780682bc6adbd73569810af3f0394.
- Requests plik SHA256: e2f1f254a313ee237d19b8f23d91ca1bbb672853f4c40ae41aa1386e7c7c4b42.
- Request payload hash: 11d068c9a9c6779e61cdb664a531992f71c6c0a0879358e57e36ade4ec1cc833.
- Summary SHA256: a122b35c3489e643c235ed922a7f725cad1c8b7f451e58b7f77c7cc5c58d36e3.
- Summary Git blob: 3d7fc2bf1d2dad2b2f324d44b851db459d1cca15; odczytano z przypiętego GitHub, bajty zgodne.
- 56/56 testów stdlib PASS lokalnie. Freeze push CI 37054460796 i PR CI 37054468868 completed/success.
- Results push CI 37055044234 i PR CI 37055052356 completed/success dla 55bb179a1d308cf7a7f7d4049ec6e3f060719e4c.
- Inferencja realna lokalnie, exit 0; CI sprawdza kontrakt, nie modele ani Androida.
- 224 grupy / 380 unikalnych par; zero obcięć tokenowych, max premise 121 tokenów.
- Wszystkie warianty dopuszczalne/kompletne/finite i zgodne z request hash; engineScore zachowane.
- 6 wcześniejszych systemów MLM replay bez zmiany scores celu; nowy konkurent w probe neutralny, bez udawania nowej inferencji.
- Manifest modelu i artefaktów zawiera SHA256; wag nie opublikowano.

## 9. Gałęzie historyczne i ograniczenia

experiment/context-surface-window-v1 nadal Draft PR #4. Poprzednie v1/v2 i ich immutable wyniki zachowano. Branche docs/architecture-runtime-langpack-separation-2026-10-02 i docs/architecture-langpack-plugin-model-2026-10-02 zachowują role opisane w STATE_RECONSTRUCTION; ich HEAD-ów nie sprawdzano ponownie w tym etapie. Nie wykonywano merge ani przepisania historii.

Znane luki CTC ł, eligibility PL ZIP, pl.cklm i niespójność ADR pozostają otwarte według poprzedniego milestone’u. Ten etap nie weryfikował ich ponownie. Modele nie porównują różnych kluczy; konkurencja słów i rozkład slotów UI wymagają odrębnego testu.

## 10. Następny uzasadniony krok techniczny

Przygotować nowe dane i zamrożone kryteria sprawdzające znaczenie aktualnie dopisywanego słowa w zwykłych zdaniach oraz przy sprzecznych informacjach. Porównać gotowe rozwiązania z baseline’em bez strojenia na dotychczasowych przypadkach. Następnie rzeczywiste slates, koszt telefonu i interpunkcja. Główne kryterium nadal top 3, top 1 pomocniczo.

## 11. Delta względem CONTEXT_DIAGNOSTICS

Dodano jawne senseIds i opisy znaczeń, prawdziwą inferencję gotowego NLI, kontrolę bez opisów/swap, ocenę top 3 i osobny probe limitu UI. Utrwalono korektę użytkownika z dwóch do trzech propozycji oraz wymóg przyszłej rozszerzalności o interpunkcję. Wykazano poprawę przy wcześniejszej wskazówce i regresję przy sprzecznych opisach. Testy 47→56; pełne wyniki i readback w GitHub. Produkcja, generator i API v1 bez zmian.
