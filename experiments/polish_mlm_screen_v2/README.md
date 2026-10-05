# Screening oryginalnych tokenizerów polskiej SI — 2026-10-05

Tani test PRZED wagami: źródłowy pack v5 (106363 klucze CKDT),16199 sidecar entries,
16117 wpisów wielowariantowych i122480 form, plus niezmienne384requests/836targetspans v1.
Exact pack/dictionary/sidecar SHA, modele/revisions i hash każdego pobranego pliku
zapisane w skrypcie/wynikach. Oryginalny AutoTokenizer, bez trust_remote_code/Torch.
Nie podrabiamy tokenizerów, nie dopisujemy słów/tokenów/opisów ani nie usuwamy błędów.

| Kandydat | Źródłowe formy unknown | Unknown/collapsed pary | Pełne384requests | Status |
|---|---:|---:|---|---|
| Geotrend/distilbert-base-pl-cased | 2 (`ą`,`ę`) | 0/0 | PASS | do diagnostycznej próby,6warstw |
| BartekK/distilHerBERT-base-cased | 0 | 0/0 | PASS | do próby,6warstw; licencja wag niewyjaśniona |
| Geotrend/bert-base-pl-cased | 2 (`ą`,`ę`) | 0/0 | PASS | rezerwa12warstw |

Brak pełnego100%coverage Geotrend wyraźnie zachowany jako `fullSourceCoveragePass:false`.
Nie ma unknown na16117par ani na836maskowanych celach próby. Dwa samodzielne wpisy
nie podlegają testowanej SI porządkującej pary; nie zmieniamy gates dla bieżących żądań.
Pojedyncze znaki ąęńĄĘŃ również unknown; pełne źródłowe słowa nie są pojedynczymi literami.
`Łódź`/`łódź`,Malina/malina,Warszawska/warszawska i wszystkie źródłowe pary rozróżnione.
Geotrend tokenizuje `łódź` na3tokeny,`Łódź` na1; mean-logp może mieć własne uprzedzenia
tokenizacji, dlatego same IDs nie dowodzą trafności. DistilHerBERT obie formy po1tokenie.

Metadata Geotrend Distil safetensors:60737405F32params; BERT103266173F32 +512I64buffer.
`*-safetensors-header.json` to bounded Range metadata (8B length+12688/23888B JSON),
nie pełne wagi. Widać oryginalną głowicę/tied embeddings; poprawność head/weights/parity
dopiero wymaga faktycznego model load. APIparams nie są PSS telefonu ani gwarancją jakości.
DistilHerBERT ma6warstw hidden768/vocab50000, actualparamcount pending inference.

Licencje wg kart:Geotrend Apache-2.0; distilHerBERT nie deklaruje licencji w karcie/API,
plikach modelu ani root repo kodu. Brak redystrybucji/deployment approval; nie zakładamy
dziedziczenia licencji nauczyciela. Treningu/finetune ani zmian głowicy nie wykonano.

ORIS-Bert-Small-C: aktualna karta podaje25.41M/6layers/384hidden, customMLM Polish;
research gated,custom_code i własna architektura. GET API zwrócił401 bez logowania,
nie pobrano config/tokenizera/wag. Tylko rezerwa do osobnej oceny dostępności/licencji
i audytu kodu; nie porównywalna karta GPU z Androidem. Nie zaakceptowano warunków
ani nie skontaktowano się z autorem. Źródło:https://huggingface.co/OrisTeam/ORIS-Bert-Small-C.

Pozostałe primary źródła:
https://huggingface.co/Geotrend/distilbert-base-pl-cased
https://huggingface.co/Geotrend/bert-base-pl-cased
https://aclanthology.org/2020.sustainlp-1.16/
https://huggingface.co/BartekK/distilHerBERT-base-cased
https://github.com/BartekKrzepkowski/DistilHerBERT-base_vol2
Pobrane2026-10-05 przed inference nowych modeli. Konfiguracje,rewizje i fileSHA w JSON.
Pełne pliki tokenizerów i wagi nie redystrybuowane; backend hash wiąże pipeline.

Odtworzenie z oryginalnych metadata files we wskazanych rewizjach:
`USE_TORCH=0 USE_TF=0 python screen_tokenizers.py --metadata METADATA_ROOT --pack EXACT_V5.zip --out OUTPUT`.
Transformers4.57.6/tokenizers0.22.2, environment recorded in results.
Original model subdir is repo_id with slash replaced by `--` and contains original
config/tokenizer assets plus metadata.json listing exact downloaded sizes/SHA.
Screen is coverage only, no quality/RAM/latency evidence; v2 protocol elsewhere.
