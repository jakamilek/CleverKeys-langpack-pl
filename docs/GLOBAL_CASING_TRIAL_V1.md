# Globalna pisownia i interpretacje źródłowe — pakiet trial v5

## Cel i zakres
Audyt obejmuje wszystkie 106363 klucze przypiętego polskiego CKDT, bez listy
wyjątków słów ani ograniczenia do części mowy conj/comp/part/prep.
Morfeusz 2 1.99.15, SGJP pl.sgjp.sgjp-2026.06.01 analizuje małą i wielką
pierwszą literę. Dokładna forma wygenerowana z tego samego lematu, pełnego tagu
i klas NAME potwierdza dopuszczalną pisownię. Sam wynik sondy wielką literą
nie jest dowodem takiej pisowni: mogła to być tylko zwykła kapitalizacja początku zdania.

Kategoria nazwy i zwykłe użycie są niezależnymi interpretacjami jednego klucza:
- ale: conj/part/interj; Ale: odmiany imion Al/Ali/Alo/Ala;
- lub: conj i impt od lubić; Lub: odmiana Luba:Sf, NAME imię/nazwisko;
- tutaj: adv; Tutaj: nazwisko.
Nie przypisujemy ręcznych opisów znaczeń ani nie dopowiadamy ulicy/miasta z samego nazwiska.
Dokumentacja źródła: https://morfeusz.sgjp.pl/doc/about/.

## Domyślna forma i warianty
Dokładnie poświadczone zwykłe użycie małymi literami ma pierwszeństwo.
Wariant nazwy pozostaje w capitalization.variants tego samego wpisu.
Gdy źródło potwierdza tylko nazwę pisaną wielką literą, domyślna forma pozostaje
nazwą. Gdy nie potwierdzono żadnej zgodnej formy, zachowujemy wejściową pisownię.
Skróty z inną kapitalizacją niż mała/wielka pierwsza litera zachowują CKDT;
nie wymuszamy formy niedającej się przedstawić w obecnym API.
To deterministyczna polityka domyślna, nie waga korpusowa poszczególnych znaczeń.
Kontekstowe AI i częstotliwości interpretacji nie zostały wdrożone.

W pakiecie:
- 106363 kluczy poddanych audytowi;
- 102135 z co najmniej jedną potwierdzoną formą;
- 16117 par źródłowych, w tym 15977 zwykłe użycie/nazwa;
- 736 zmian domyślnej pisowni;
- 16199 wpisów runtime, obejmujących konflikty, poprawione formy i historyczne kontrole;
- 4228 kluczy bez zgodnej formy z tego źródła — zachowana pisownia;
- 455 wejściowych form poza wzorcem mała/wielka pierwsza litera.
Liczba par źródłowych nie jest deklaracją liczby par dostępnych dla wszystkich skrótów w API.

## Dane dla przyszłego rankingu
Pełny global-casing-audit.jsonl zachowuje każdy klucz, interpretacje (lemat, tag,
NAME, kwalifikatory), ich stabilne identyfikatory oraz dokładne formy wygenerowane.
Sidecar runtime zawiera zwięzłe sourceEvidence.lexicalReadings:
lemma, partOfSpeech (pierwsze pole TAG), nameClasses, labels, surfaces.
Różne tagi fleksyjne o tej samej tożsamości lemat/POS/NAME/kwalifikatory są grupowane
wyłącznie w kopii runtime. variantCategoryIds łączy pisownię z kategoriami NAME/POS.
Pełne tagi pozostają w audycie: provenance.fullAudit wskazuje plik, SHA i surfaceKey
jako klucz powiązania. Audyt jest obok packa w artefakcie CI, nie wewnątrz importowanego ZIP.
Dziewięć wcześniejszych wpisów zachowuje bogatsze dane i pierwotne rekordy GUS bez zmian.

Nie eksportujemy wszystkich analiz wszystkich wyrazów do pamięci klawiatury.
Cały słownik jest audytowany, natomiast runtime zawiera tylko potrzebne konflikty
pisowni/poprawki i kontrole. Metadane nie są jeszcze używane przez AI.
API v1 pozostaje: lexicon/frequency/capitalization/metadata; nie deklarujemy pełnej morfologii.

## Bezpieczeństwo kontraktu i odtwarzalność
Wejście to wyłącznie przypięty pack v4 SHA 3767c76dbf87589182d6b26b8f8d64d80ec635764cee15d350015b60d41e21af.
Jednakowa długość UTF-8 poprawianych form zachowuje nagłówek, sekcje lookup,
kolejność/klucze/rangi i unigrams. Sidecar defaultSurface i canonicalForm muszą
zgadzać się z nowym CKDT. ZIP ma deterministyczne członki, daty i kompresję.
Porównanie identycznych buildów dotyczy tego samego środowiska Python/zlib.

Androidowe limity nie zostały zwiększone:
11542814 bajtów sidecara, 751535 węzłów JSON, 16199 wpisów,
wobec limitów 32 MiB / 1 000 000 / 120 000. Pełna nieskompaktowana wersja przekraczała
limit węzłów i została odrzucona. Rzeczywisty parse Android, import, pamięć i start
na telefonie wymagają osobnej kontroli; hostowa zgodność struktury ich nie zastępuje.

## Testy i CI
42 testy lokalnie PASS: 21 istniejących wariantów, 8 funkcyjnych, 13 nowych globalnych.
Nowe obejmują prawdziwe homonimy, adv/czasowniki, właściwe nazwy, brak fałszywych
wielkich wariantów, fragmenty, pełne tagi, każdorazowy audyt klucza, CKDT/rangi,
powiązanie danych runtime ze źródłem, historyczne dane, hash/determinizm i limit JSON.
Niezależny od buildera przegląd realnego CKDT potwierdza 106363 klucze/rangi,
nagłówek/lookup/unigrams i niezmienione dziewięć wcześniejszych wpisów.
Dwa pełne buildy dają identyczne ZIP, raport, audyt i summary.

Workflow variant-trial.yml odtwarza v3 i v4, wykonuje nowe testy, buduje v5 i porównuje
global-casing-reviewed-summary.json z zatwierdzonym wynikiem. Pełna lista zmian ma
SHA w summary, a jej treść i pełny audyt trafiają do artefaktu.
Raport v4 ma uaktualniony wyłącznie fingerprint wspólnego resolvera; ZIP v4 pozostaje
identyczny. Przyszłe pełne buildy używają szerszej reguły attested_ordinary_matches.
Nie wykonano pełnego głównego preview pipeline.

## Budowa, import i telefon
```sh
python3 -m unittest discover -s tests -p 'test_*trial.py' -v
python3 scripts/build_global_casing_trial.py \
  --base-pack build/function-word-trial/cleverkeys-pl-function-words-trial.zip \
  --out-dir build/global-casing-trial
```

Nowy artifact CI: cleverkeys-pl-global-casing-trial.
Po potwierdzeniu runu rozpakować zewnętrzny artefakt i importować tylko
cleverkeys-pl-global-casing-trial.zip jako aktualizację polskiego langpacka.
APK nie wymaga zmiany tej reguły/danych; bieżący runtime trial v15 obsługuje API v1,
lecz jego run i akceptacja pozostają osobną weryfikacją.
W środku zdania sprawdzić ale/lub/tutaj oraz wariant nazwy obok zwykłej formy.
Sprawdzić też Jan, istniejące Łódź/łódź i inne pary, Shift/początek zdania,
restart klawiatury i płynność po imporcie. Pisownia użytkownika może mieć pierwszeństwo;
nie usuwamy jego słownika.

Lokalne hashe (nie potwierdzony artefakt GitHuba):
- ZIP aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb
- CKDT a32f6a55bce7375e744d3d261d6ec9aad96dc64725ac429d4cb1d7225aed3c2a
- sidecar 5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d
- pełny audyt 06031fee57cc32b6c795cc36f0a728449e7bc7bd841b09bb23d0fb33012c7454
- lista zmian 50215963bff5ed9ab0332202309181b26ff7257b51ea51c2e267c6c323c1de3d

Status: kod i lokalny pack przygotowane; nowy CI/artefakt/import/telefon wymagają
potwierdzenia. Bez release, tagu, zmiany wersji APK i promocji do main.
