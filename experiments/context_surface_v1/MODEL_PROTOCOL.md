# Zamrożony protokół pierwszej inferencji

Ustalony przed wykonaniem pomiaru. Bez dostrajania modelu, promptu, progu ani
metody punktowania na podstawie etykiet tych 14 przykładów.

- Model: `allegro/plt5-small`, rewizja
  `6ab71258c53f77f075fdda380992c0e691703f6b`, licencja CC BY 4.0.
  Gotowy model Polish T5, pretrained przez denoising; nie gotowy klasyfikator
  nazw własnych. Autorzy: Allegro ML Research, Chrabrowa et al. (2022),
  [model card](https://huggingface.co/allegro/plt5-small),
  [paper](https://arxiv.org/abs/2205.08808).
- Input: wyłącznie okno tekstu przed kursorem i `<extra_id_0>`.
- Teacher forcing dla `<extra_id_0> powierzchnia <extra_id_1>`.
  Score to suma log prawdopodobieństw tokenów powierzchni i końca span-u
  `<extra_id_1>`, po wspólnym sentinel0. Nie uwzględnia EOS ani sentinel0,
  nie normalizuje długością. Różna segmentacja wariantów może wprowadzać
  preferencję długości; raport zapisuje tokeny obu form. Żadna alternatywna
  metoda punktowania nie jest wybierana po zobaczeniu wyników.
- Porównywane wyłącznie warianty jednego klucza; engineScore i kolejność
  kluczy bez zmian. Jednowariantowy klucz nie wymaga inferencji.
- Pusty kontekst: słownikowy default, bez preferencji a priori modelu.
- Dwa okna: 2 słowa i do 64 słów / 4096 znaków, oba z zachowaną pisownią.
  To porównanie samej długości, nie wierna emulacja obecnej historii runtime,
  która dodatkowo zamienia litery na małe.
- Osobny budżet 512 tokenów wejścia z suffix-em (mask + EOS); przy nadmiarze
  usuwamy najstarsze tokeny, odnotowując flagę. To budżet eksperymentalny.
- CPU, float32, 2 wątki, eval + inference_mode. Model loading ma odrzucić
  brakujące/dodatkowe/niedopasowane wagi; nie ma losowo inicjalizowanej głowicy.
- Bez gold labels w requests. Hash żądań, rewizja modelu i SHA kodu adaptera
  wiążą wyniki z wejściem. Wynik musi przejść istniejący walidator.
- Raport: paired display top-1, błędy, tokenizacja, latencja w tym środowisku.
  Syntetyczny fixture nie jest benchmarkiem użytkowników ani pomiarem Android.

## Odtworzenie

```bash
python3 -m venv .venv-model
.venv-model/bin/pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
.venv-model/bin/pip install -r experiments/context_surface_v1/requirements-model.txt
python3 experiments/context_surface_v1/prototype.py prepare --cases experiments/context_surface_v1/cases-fixture.json --sidecar experiments/context_surface_v1/sidecar-fixture.json --output build/context-surface/requests.json
.venv-model/bin/python experiments/context_surface_v1/plt5_adapter.py --requests build/context-surface/requests.json --output build/context-surface/plt5-predictions.json
python3 experiments/context_surface_v1/prototype.py evaluate --cases experiments/context_surface_v1/cases-fixture.json --sidecar experiments/context_surface_v1/sidecar-fixture.json --predictions build/context-surface/plt5-predictions.json --output build/context-surface/plt5-report.json
```

Wyniki inferencji nie są odtwarzane w szybkim CI: CI sprawdza kontrakt i kod
stdlib, bez pobierania 381 MB wag. Pełny pomiar jest osobnym artefaktem.
