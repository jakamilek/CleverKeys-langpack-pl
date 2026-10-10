# HerBERT: diagnostyka odmiany i kapitalizacji v1

Autoryzacja użytkownika: 2026-10-10, po zgłoszeniu „Gdzie leży wieś ” → Pracą, Praca.
Ta próba ma odtworzyć decyzję modelu, a nie zmieniać ranking klawiatury.

## Tożsamość i zakres

- Oryginalny HerBERT FP32 używany przez telefon, bez ponownego eksportu/treningu.
- Producer d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c, run37230171787,
  artifact11312693984, model SHA f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2.
- Pobranie wewnątrz tego samego repozytorium z uprawnieniem actions:read,
  kontrola wszystkich siedmiu rozmiarów/hashów identycznych z HerbertBenchmarkTrial.
- ORT1.21.1 CPU, wątki2/1; mean whole-word mask jest dotychczasowym kontraktem.
- 24 jawne krótkie konteksty, w tym zgłoszony przykład i wcześniejszy kontekst pracy.
  Gold zapisany przed inferencją. To ręcznie opisany benchmark, nie ręczne dopiski do słownika.
  Pozostałe konteksty są nowe, lecz autorskie, bez ślepej zewnętrznej oceny.
- Source-fixture.json to byte-identical dziewięciowpisowy fixture sourcev5 z runtime
  3f48e456f0d8f411e80be3857f1846e4b2cd139e. Do modelu trafia sam tekst i formy.
  Oba klucze i wszystkie cztery powierzchnie muszą być źródłowo dopuszczone
  i mieć wspólną case-sensitive lemma/POS. Nie dodajemy żadnych form ani opisów.

## Obowiązkowe kontrole

1. Freeze obejmuje nowe pliki, workflow i oryginalny PortableTokenizer.
2. Stare kontrakty mobile/portable pozostają wymagane; nowe testy sprawdzają
   kompletność/source identity, zaufanie do plików, tensor padding/maski, score/ties.
3. Wczytanie oryginalnego graphu dopiero po siedmiu hashach; dokładne pięć nazw,
   typów/rang wejść i dwa wyjścia.
4. Oryginalne 2471 token vectors: fast tokenizer i portable; 232batches/532surfaces:
   dokładne pięć wejść oraz real ONNX score/rank parity z tolerancją0.001.
5. Nowe konteksty/formy mają również dokładną zgodność obu tokenizerów.
   Każdy czteroelementowy wynik porównywany z osobnymi single-row wywołaniami0.001.

Wynik techniczny CI oznacza kompletność i zgodność pomiaru. Błędy językowego Top1
są raportowane, nie ukrywane przez failure/upload-skip. Nie istnieje nowy próg
promocji do produkcji ani zmieniony algorytm wybrany po obejrzeniu wyników.

## Raport i interpretacja

scores.json zawiera każde syntetyczne zdanie, gold, wszystkie cztery mean/sum scores,
liczbę i ID tokenów, komplet pięciu wejść, pełny ranking i osobne wyniki formy
bez wielkości liter oraz kapitalizacji. SUMMARY.md daje porównanie per przykład.

Top3 w tym raporcie to raw ranking wewnątrz grupy czterech form, nie pozycja na
telefonicznym pasku po compact presentation. BaselineOrder jest jawną syntetyczną
kolejnością źródłową, nie odtworzonym rankingiem geometric z telefonu.

Route DIRECT_HOST_ONNX_NO_IME_FALLBACK oznacza, że wynik rzeczywiście pochodzi
z tej bezpośredniej inferencji: nie ma timeoutu/busy/fallbacku IME. Nie dowodzi,
która ścieżka zadziałała podczas zgłoszonego swipe na telefonie. Jeśli host również
wybierze Pracą, odtworzymy błąd preferencji modelu w tym kontekście. Jeśli wybierze
Praca, pozostają do zbadania realny capture, skład grupy i fallback telefonu.

Sum-score ranking jest wyłącznie diagnostyczny: pokaże ewentualną zależność wyniku
od długości tokenizacji. Nie zastępuje live mean i nie ustanawia confidence gate.
Żadna metryka nie dowodzi czasu telefonu, niezależnej trafności ani poprawy wag.

## Kolejny krok

Po wynikach: porównać zgłoszony przypadek z pozostałymi i odmianami wspólnymi.
W razie potrzeby przygotować nietekstową diagnostykę ostatniej ścieżki live oraz
audyt źródłowych tagów przypadku/liczby/rodzaju. Tagi same nie wyznaczają przypadku
w kontekście. Nie dodawać wyjątku „po wieś wybierz Praca”.

Bez zmian APK/model/langpack/rankingu, bez osobistych danych, zapisów edytora,
telemetrii i modelu w raporcie/Git. Bez merge/release/tag/version bump.
Monitorowanie Actions maksymalnie60s total/run; potem użytkownik zgłasza zakończenie.
