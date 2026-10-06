# Kamień milowy: ostrożny ranking v4 nie przeszedł nowej walidacji
Data: 2026-10-06, Europe/Warsaw.

## 1. Repozytoria
Main przed zapisem: CleverKeys-langpack-pl 9e1ee283af2bd8309a08b889f06782aee0889261;
CleverKeysPL 628ad6d70a1b7f81610c74579751635e5b52ed7c.
Ten sam dokument na obu main, docs-only. Kod i raw wyniki na isolated branch.

## 2. Architektura
Geometric + importowany pack ze źródłowymi wariantami/default/metadata.
Android SI nadal oddzielny benchmark, live ranking off, default32/max64/4096UTF16.
V4 bada globalny margin-threshold dwóch form jednego źródłowego klucza.
Obie formy zachowane. Model score nie jest kalibrowanym probability.

## 3. Ustalenia
Run37502851581 completed SUCCESS, wszystkie4jobsSUCCESS.
Oba original FP32 modele ukończyły256requests z head7d7d3ec4....
TrzyZIP SHA256, tokenizer/loading/head/parity/trace identities PASS.
Lokalny collector z GITHUB_SHA7d7d3... reprodukuje JSON i Markdown dokładnie.
Safety quality screenFAIL na nowych64/window16. Nie kwalifikować tej reguły
do wdrożenia i nie dostrajać progu na tych samych przykładach.
Słownik ODŁOŻONY przez użytkownika, obowiązek powrotu zachowany.
Licencja odłożona, brak założenia grantu/licencji.

## 4. Odrzucone
Nie zmieniać frozen kryterium utility po wyniku i nie stroić wyjątków dla Kot/Koza/Zając.
Nie traktować poprawy development replay jako nowej walidacji.
Nie anulować v3 historicalFAIL. Nie traktować hostRSS jako phonePSS.
Ten FAIL nie dowodzi nieskuteczności każdego modelu/metody SI.
Brak promotion/merge/release/tag/version bump, bez subagentów.

## 5. Wykonane i planowane
Wykonano niezależną weryfikację artefaktów i odtworzenie kolektora.
14rawfiles zapisano z kontrolą blob SHA; RESULTS i provenance zachowane.
DraftPR12 opis zaktualizowany wynikiemFAIL.
Nowy run/model/metoda/ONNX/phone test nieuruchomione.
Przed kolejną próbą rozstrzygnąć bardziej odpowiednią metodę kontekstowego
wyboru źródłowych form i ewentualnego wykorzystania metadanych,
zamiast utożsamiać marginMLM z pewnością. Osobny protokół/nowe dane potrzebne.

## 6. Wyniki i niewiadome
Primary nowe64/window16:
source default32/64;
HerBERT50/64 repairs19/regressions1;
rawdistil48/64 repairs17/regressions1;
gateddistil46/64 repairs15/regressions1, overrides16.
Utilitygated11 vsraw13 -> utilityAtLeastRawFAIL.
Pozostałe6/7 kryteriówPASS, exploratorySafeCandidate=false.
Gating zatrzymuje poprawne Koza po pan (margin0.0495) i Kot przy nazwisku na
identyfikatorze (margin0.1947), przepuszcza błędne Zając przy zwierzęciu w kapuście
(margin0.4602). Nie zmniejsza liczby błędnych zmian w primary.
Secondary nowe64/window32:
HerBERT48/64 regresje6; rawdistil47/64 regresje2;
gated46/64 repairs16/regresje2/overrides18/utility8.
Default16 niezatwierdzony, default32 aplikacji bez zmian.
Development replay historical64 w obu oknach:
HerBERT50/rawdistil46/gated46; rawdistilrepairs16/regresje2,
gatedrepairs14/regresje0. Stary reference-quality threshold>=49 nadalFAIL.
Nie są to nowe unseen przykłady.
Host peakRSS1427.91MiB HerBERT/950.45MiB distil; parametry124494416/81967184.
Phone distil PSS/latency/energy nadal nieznane.

## 7. Gałęzie
experiment/polish-mlm-safe-rank-v4:
frozen executable7d7d3ec4f7be31476df11f198dfcc2b21d813e5b;
archive commit5339596a801717569a72d1ad847aa1f0131ffe9a.
DraftPR12 base experiment/polish-mlm-v3-loading-fix-v1 nie scalony.
V3 frozen83fa31.../run37500235605 oraz archiveb2c334... zachowane.
V3 failedc1e9d3.../run37363474711 nieprzepisane.
Runtime APK codedb88fd28cca21ba2aa1e99b38e3886f1f147b5d6 bez zmian.

## 8. Artefakty i odtwarzanie
Run https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37502851581
RequestSHA84ec2282a35f0e96b4020c42c6e9bca8376b00b712d7653adf2148f4541a3f60.
Freeze file SHA256 5c16b760927e70d89131a0d2a10a5c5d6bce90d9ac9985f09a68d5afc5705a07.
Artifact11431065594 HerBERT ZIP SHA256
8f61e1eb9466736885e2694c958a7989f1c648609981cdced167598595f43aa8.
Artifact11429599621 distil ZIP SHA256
4cd858fb43cc9f35444d40f0e5506173d1457f30fc5220358fe4962797150a7e.
Artifact11430542426 comparison ZIP SHA256
a1d672c24fb10fe0e0855df36a4ef9521345185f577b1b9cd0124b5827e9814e.
Raw/provenance/RESULTS w experiments/polish_mlm_safe_rank_v4_results
na commit5339596.... Bez wag, expiryZIP2026-11-05; raw zachowane wGit.
Reproduce collector z frozen executable/GITHUB_SHA7d7d3..., nieSHA archiwum.

## 9. Ograniczenia
64nowe autorskie teksty po development, known16keys; context holdout, niekeyholdout,
bez zewnętrznego anotatora/humanblind. Mała próba, nie produkcyjny benchmark.
Próg0.25 dobrany wyłącznie development256 requests, utilityrepairs−4regressions
i siatka ustalone wcześniej. Próg niezmieniony po nowym wyniku.
Top3 dwóch form nasycone bezSI. Brak multi-key replay/interpunkcji/telefonu.
FullHerBERT FP32 phonePSS >2GiB pozostaje przeszkodą.
Słownik9 form swipe i3czasyBS oraz inne locale nadal backlog.

## 10. Następny krok
Omówić ograniczenie prostej margin-reguły; dalszy wybór metody/modelu wymaga
dopasowania do celu kontekstowego rozróżnienia poświadczonych źródłowych form.
Nie uruchamiać kolejnej granicy progu na v4 i nie przedstawiać jej jako walidacji.
Nie zakwalifikowano do eksportu/telefonu na podstawie tegoFAIL.
Monitoring<=60s TOTAL/run; użytkownik podaje zakończenie. Brak kolejnego runa.

## 11. Różnica
PROJECT_MILESTONE_2026-10-06_SAFE_RANK_V4_FROZEN.md miał model/qualityPENDING.
Teraz actual evidence zweryfikowane, techSUCCESS ale new64qualityFAIL:
2trafne poprawki utracone, brak redukcji błędów wprimary.
Wynik zachowany bez strojenia, proweniencja i raw archiwum zapisane.
Ten dokument exact readback w obu main. Main tylko dokumenty.
