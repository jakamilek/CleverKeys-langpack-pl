# HerBERT FP32 benchmark package v1 — wyniki

[Run 37230171787](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37230171787),
commit d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c: contract/package SUCCESS.
FP32 odtworzony byte-identical: 651798883 B, SHA256
f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2.
232 requests / 532 candidate evaluations; zero zmian pełnego rankingu,
max bezwzględny błąd względem archived FP32 <=0.001. Pełny raport grup w float-comparison.json.

Portable reference vs oryginalny HerbertTokenizerFast: 2471 zapisanych vectors PASS,
4352 exhaustive scalar blocks PASS. Oryginalne 50000 tokenów / 48016 merges / 198
skompresowanych Unicode ranges; bez ręcznie budowanego słownika i bez zależności
od kategorii Unicode danej wersji Androida. Model/tokenizer versions w benchmark-report.json.

Metadata artifact 11312569320, 1299643 B, ZIP SHA256
2310649ba6e8c9b72e40952687d88a50940a71d6cfadb186ca055138bdea91d6:
lokalnie pobrany i zweryfikowany (ZIP i każdy nie-modelowy member zgodnie z manifestem).
Pełny float-comparison przeliczony z android-score-vectors scores i archived requests;
dokładnie zgodny z CI. Portable reference ponownie sprawdzony na wszystkich 2471 vectors.

Model artifact 11312693984, 657295441 B, GitHub ZIP digest
36c2183acca3ae6dca4afb54c28fe4d9d4cb37ec26f3230c94b4e007b494587f,
ważny do 2026-10-18T19:57:49Z. Duży ZIP wag nie był pobierany do lokalnego workspace.
CI wymagało dokładnego model SHA przed uploadem; app importer zweryfikuje każdy plik
z własnym kompletem pinned identities. Manifest SHA256
667bd4fee413a13ca8edca75f5b7defff2c58d0450d8d87ab8e9ccef948026b0, 1243 B.

To paczka diagnostyczna: phoneReady=false, independentQualityValidated=false,
bez live IME. Dotychczasowy INT8 preservation FAIL pozostaje FAIL. Nie ma nowych
niezależnych wyników trafności ani pomiarów telefonu. Runtime Kotlin token/feed parity potwierdzono w run 37231774451 (90615f0):
2471 token vectors, wszystkie pięć feeds /232 batches/532 candidates PASS, JUnitCore
OK(2835), compile PASS. Workflow zatrzymał potem nieobecny rg (exit127), nie test.
Android JNI scores, finalny APK i rzeczywiste Nubia timings nadal nieweryfikowane.

Konteksty archived mają najwyżej 13 słów; nie rozstrzygają trafności okien 32 vs 64.
Przygotowany runtime wybiera 32 jako default i porównuje czas obu limitów na syntetycznym
benchmarku. To porównanie wydajności, nie dowód równej trafności.

Android workflow repair run 37232458354 at 73627fa SUCCESS: compile, JUnitCore
OK(2835), mandatory original conformance, 83 focused regressions, debug/vital lint,
assembly, APK ZIP audit i upload ARM64 PASS. APK artifact 11314463703 /35697510 B,
raw APK 35696490 B, SHA256
70c3e0e94f10e0a6e7ec4f9b6e043767cd9e41e7e21f14f21586958b07e07958.
APK verified przez CI logs/audit, nie lokalny download/scan. Phone JNI/timing/accuracy
nadal pending; live SI wyłączone. Instrukcja w runtime docs/HERBERT_FP32_PHONE_TRIAL_V1.md.
