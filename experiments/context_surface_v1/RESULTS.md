# Wynik eksperymentu lokalnego — 2026-10-02

Baseline main: `0832bf6f1353b0a2bc3042dbdd26f330ddc53e33`.
Runtime main: `56e7e90d3a669f2eb28e65257ce6851aa7b5d925`.
Gałąź: `experiment/context-surface-window-v1`.
Środowisko: Python 3.12.14, standard library; bez pobierania modeli.

## Wykonane sprawdzenia

- `python3 -m unittest discover -s experiments/context_surface_v1 -p 'test_*.py' -v`: **30/30 PASS**.
- CLI `prepare` i `evaluate`: zakończone sukcesem.
- Powtórne przygotowanie żądań i raportu: identyczne bajty i SHA256.
- Testy objęły pełne słowa przy obcięciu, Unicode z combining marks, casing, diakrytykę,
  interpunkcję, nowe linie, wspólny klucz, alternatywy, Shift/Caps Lock, brak metadanych,
  język secondary, brak właściwego słowa w slate, nieważne/stare wyniki oraz brak gold labels.
- Wyniki kontrolowane są oznaczone jako `controlled_test`; nie są inferencją AI.

## Baseline neutralny na 14 przykładach skonstruowanych

| Miara | 2 słowa | Okno do 64 słów / 4096 znaków |
|---|---:|---:|
| Poprawny klucz dostępny w slate | 13/14 | 13/14 |
| Poprawny klucz top-1 | 13/14 | 13/14 |
| Poprawna powierzchnia top-1 | 10/14 | 10/14 |
| Oczekiwana powierzchnia dostępna w sugestiach | 13/14 | 13/14 |

Neutralny baseline nie używa znaczenia kontekstu, dlatego nie poprawia się od wydłużenia okna.
To kontrola mechaniki i osiągalności, nie ocena jakości klawiatury ani gotowego modelu.

## Deterministyczne artefakty

| Artefakt | Bajty | SHA256 pliku UTF-8 |
|---|---:|---|
| requests.json | 11970 | f89fab6cb1469f8b847003d22aca7dbff22dc43a0cbb451e7c534a9d98611ceb |
| neutral-baseline.json | 17953 | 8e4af8bf1ae64649b3817f45f97666d22b1e8d4892b77459bd16d47cdf15af69 |

`requestSha256=e6db915401dbff00f0185d938a7bc095d261dc182c4ec44c804eb0b0a8abcda4`
jest hashem kanonicznego payloadu przed dodaniem samego pola requestSha256.
`sidecarSha256` jest hashem kanonicznego JSON fixture, nie hashem pliku instalowanego ZIP-a.
Artefakty można odtworzyć komendami z README; nie są danymi produkcyjnymi.

## Zakres dalszej pracy

Gotowy model cased z przypiętą rewizją i rzeczywisty adapter oceny wariantów.
Następnie większy zbiór, rzeczywiste slates, koszt telefonu i integracja runtime.
Nie zmieniono kolejności słów, engineScore, dictionary.bin ani membership 100k.
Nie naprawiono w tym eksperymencie CTC ł i nie podłączono prototypu do aplikacji.
Status CI gałęzi należy sprawdzić po push; ten raport opisuje wykonane testy lokalne.
# Aktualizacja — rzeczywista inferencja

Ten plik opisuje historyczny neutralny baseline. Wykonany pomiar Polbert,
porównanie długości okna i kompletne artefakty są w [MLM_RESULTS.md](MLM_RESULTS.md).

