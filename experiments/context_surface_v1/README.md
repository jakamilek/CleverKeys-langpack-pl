# Eksperyment: dłuższy kontekst i warianty powierzchni

To działający prototyp offline w Pythonie 3.12. Harness i testy używają
standard library; opcjonalny adapter modelu wymaga torch/transformers.
Aktualna diagnoza: [DIAGNOSTIC_RESULTS.md](DIAGNOSTIC_RESULTS.md),
protokół: [DIAGNOSTIC_PROTOCOL.md](DIAGNOSTIC_PROTOCOL.md).
Pierwszy pomiar zachowano w [MLM_RESULTS.md](MLM_RESULTS.md).
Nie zmienia klawiatury Android ani produkcyjnego rankingu słów.

## Co sprawdza

- Odczyt fragmentu tekstu **przed kursorem**, domyślnie do 64 słów i 4096 znaków.
- Zachowanie wielkości liter, diakrytyki, interpunkcji, nowych linii i joinerów.
- Suffix z pełnymi słowami po obcięciu; flagi pokazujące utratę starszego kontekstu.
- Osobne żądania dla dwóch słów i dłuższego okna, bez gold labels.
- Jedną tożsamość klucza i wiele powierzchni z przykładowego sidecara v1.
- Wybór wariantu na podstawie jawnie dostarczonych wyników modelu lub neutralnego defaultu.
- Zachowanie alternatywnego zapisu oraz innych kandydatur dekodera.
- Dokładną powierzchnię w wyniku; deduplikację po faktycznie wyświetlanym tekście.
- Rozdzielenie casing-u leksykalnego od jawnego Shift/Caps Lock i autocap.
- Spójność danych modelu z request SHA256 i odrzucenie niepełnych/nieważnych wyników.

Okno może obejmować obecne i wcześniejsze zdania w limicie. 64/4096 to
parametry eksperymentu, nie zmierzony optimum ani ustawienie produkcyjnego runtime.
Słowa Unicode nie są tokenami konkretnego transformera: adapter musi osobno
respektować limit modelu. `boundary_cues` to pozycje `. ! ?` i nowych linii;
nie udajemy poprawnej segmentacji skrótów takich jak `dr.`.

## Uruchomienie

Z katalogu głównego repozytorium:

```bash
python3 -m unittest discover -s experiments/context_surface_v1 -p 'test_*.py' -v
python3 experiments/context_surface_v1/prototype.py prepare --cases experiments/context_surface_v1/cases-fixture.json --sidecar experiments/context_surface_v1/sidecar-fixture.json --output build/context-surface/requests.json
python3 experiments/context_surface_v1/prototype.py evaluate --cases experiments/context_surface_v1/cases-fixture.json --sidecar experiments/context_surface_v1/sidecar-fixture.json --output build/context-surface/neutral-baseline.json
```

Obie komendy akceptują `--max-words` i `--max-chars`. Zmiana parametrów
zmienia hash żądania i uniemożliwia przypadkowe użycie wyników innego okna.

`cases-fixture.json` zawiera 14 **ręcznie skonstruowanych przykładów**.
To nie zapis maźnięć telefonu ani reprezentatywny korpus. `sidecar-fixture.json`
jest fixture zgodnym z podzbiorem v1, nie produktem audytu 100k ani produkcyjnym
generatorem inteligencji. Zawiera proweniencję przykładowych danych.

## Wymiana z gotowym modelem

Adapter otrzymuje `requests.json`, ocenia wyłącznie powierzchnie wymienione
w `candidates[].variants` i zapisuje poniższy format. Większy score oznacza
preferowany wariant **tego samego klucza**. Nie porównujemy surowych logitów
między różnymi słowami. Skala modelu i engineScore to odrębne wielkości.

```json
{
  "schemaVersion": 1,
  "requestSha256": "<hash z requests.json>",
  "source": {
    "kind": "model",
    "name": "<dokładne repo/model ID>",
    "revision": "<przypięta rewizja wag i konfiguracji adaptera>"
  },
  "results": [
    {
      "requestId": "case001/long",
      "variantScores": [
        {"languageCode": "pl", "surfaceKey": "łódź", "surface": "łódź", "score": -5.0},
        {"languageCode": "pl", "surfaceKey": "łódź", "surface": "Łódź", "score": -1.0}
      ]
    }
  ]
}
```

Ten fragment ilustruje format, **nie jest wynikiem inferencji**. Pełny plik
musi zawierać dokładnie jeden result dla każdego requestId (28 w fixture).
Pusta lista variantScores oznacza brak sygnału. Jeżeli oceniono jeden wariant
klucza, trzeba dostarczyć oceny wszystkich jego wariantów; częściowe dane są
odrzucane. Zakazane są dodatkowe słowa i warianty spoza żądania, duplikaty,
NaN/Infinity i wyniki dla innego request hash.

```bash
python3 experiments/context_surface_v1/prototype.py evaluate --cases experiments/context_surface_v1/cases-fixture.json --sidecar experiments/context_surface_v1/sidecar-fixture.json --predictions build/context-surface/model-predictions.json --output build/context-surface/model-report.json
```

Wyniki kontrolowane testów używają `source.kind=controlled_test`.
Nazwa modelu i kind w pliku są deklaracją adaptera; walidator nie poświadcza,
że inferencja faktycznie się odbyła. Do raportu jakości potrzebne będą
przypięte wagi, kod adaptera, komenda uruchomienia i prawdziwe pomiary.

## Wyniki i ograniczenia

Raport rozdziela obecność właściwego klucza w slate, lexical top-1,
display top-1 i osiągalność oczekiwanej powierzchni.

Neutralny baseline daje 13/14 poprawnych kluczy top-1, 10/14 poprawnych
powierzchni top-1 i 13/14 osiągalnych powierzchni. Wyniki dla dwóch słów
i dłuższego okna są identyczne: baseline nie interpretuje kontekstu.
Case001/case002 mają te same dwa ostatnie słowa, lecz inne wcześniejsze zdania.
To sprawdza, że krótka historia usuwa potrzebną informację, nie że model już
potrafi ją wykorzystać. Case012 celowo nie ma poprawnego słowa w slate.

Nie wdrożono:
- inferencji HerBERT/plT5 ani treningu; wykonano pretrained Polbert cased;
- nowego rankingu słów: engineScore i kolejność kluczy pozostają niezmienione;
- integracji Android, odczytu InputConnection, tap-to-replace i uczenia wariantów;
- naprawy CTC `ł`, importera sidecara ani zmian CKDT/100k.

Pierwszy pomiar gotowego modelu dał 12/14 poprawnych powierzchni top-1 dla
obu okien, wobec neutralnego 10/14. Dłuższe okno nie naprawiło ani nie
zepsuło top-1 na tym fixture. Kolejny etap: większa oddzielna próba,
zweryfikowane modele o poprawnym kontrakcie tokenizatora i rzeczywiste slates.
Case001 nadal pokazuje porażkę rozróżnienia miasta z poprzedniego zdania.
Integracja wymaga lepszego dowodu jakości i pomiaru urządzenia.
