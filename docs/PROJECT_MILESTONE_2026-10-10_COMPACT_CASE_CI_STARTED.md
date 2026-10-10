# HerBERT: kapitalizacja bez blokowania pierwszych podpowiedzi — CI rozpoczęte
Data weryfikacji: 2026-10-10.

## 1. HEAD main przed zapisem
Runtime CleverKeysPL: 6d4db017be9ba36ce11b612fc98a294b24ff5581.
Producent CleverKeys-langpack-pl: cfee0ec03ce8a4f85b9e1e3a94baa3fef93b122b.
Zapis obu main wyłącznie dokumentacyjny. HEAD powyżej jest stanem przed tym atomowym zapisem, nie zgadywanym własnym SHA. Odpowiedniki:
[runtime](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-10_COMPACT_CASE_CI_STARTED.md),
[producent](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-10_COMPACT_CASE_CI_STARTED.md).

## 2. Architektura
Geometric dekoduje; HerBERT nadal analizuje pełną grupę najwyżej4 pisowni dwóch kluczy spośród pierwszych5 kandydatów. Klucze łączy polski fold lub rzeczywisty wspólny lemat/POS w sourceEvidence; zwykłe formy nie wymagają kapitalizacji sidecaru.
compact-case-v4 dodaje terminalne SwipeSurfaceVariants.present w jedynym publishSwipeSlate: pierwsza oceniona pisownia każdego klucza, inne kandydatury dekodera do wypełnienia3 pozycji, dodatkowe pisownie kapitalizacji, następnie reszta dekodera. Wszystkie słowa, własne wagi, języki i exact-case przemieszczają się razem, obce duplikaty nie są usuwane. Zwycięzca i kolejność pozostałych różnych kandydatów zachowane.
Prezentacja następuje po SI lub fallback; grupa wejściowa modelu nie jest skracana. Finalny slate ma formGroupSize=0 i presentationOnly=true; live group i pair odrzucają ponowne użycie. Bez dostatecznej liczby innych kandydatów warianty nadal mogą być w Top3. Złe kształty/obce języki i grupy zwykłych form bez dodatkowej kapitalizacji przechodzą bez zmian.
SI off/no-model/busy, timeout/next-touch, Shift/początek zdania korzystają z tej samej prezentacji. Zaufany model/scorer/tokenizer,32 słowa/350ms, jeden worker, editor/privacy/one-shot i BS bez zmian.

## 3. Zaakceptowane
Użytkownik potwierdził, że v3 działa bardzo dobrze; po „to jest bardzo ważna” podał kolejność praca/Praca/Pracą/pracą i wskazał wypieranie innych słów. Dokładnych wyników/czasu/modelowych liczników nie podał.
Sprawdzony wpis v5 ma jedno surfaceKey praca, canonical/default praca i sourceEvidence common praca + geographic Praca. Wariant pochodzi z automatycznej globalnej analizy Morfeusz2/SGJP, nie ręcznego importu konkretnej wsi ani duplikacji CKDT. Metadane nie identyfikują konkretnej miejscowości ani nie podają częstości.
Po omówieniu użytkownik zlecił ograniczenie automatycznej ekspozycji, a następnie źródłowe priorytety użycia. Wdrożono pierwszy etap; priorytety oparte na danych są wyraźnie planem. W v4 przegrana pisownia kapitalizacji nie ma sztywno zarezerwowanego Top3; wszystkie alternatywy pozostają dostępne.

## 4. Odrzucone
Bez wyjątków dla praca/Łódź/Malina, ręcznych opisów, zgadywania rdzeni, usuwania prawdziwych nazw, duplikowania kluczy czy skanowania całego słownika. Nie interpretować nazwa_geograficzna jako rzadkość. Brak populacji/liczników nie jest zerem.
Nie ustalać sztywnego progu mieszkańców ani arbitralnego progu różnicy logp. Model nie porównuje pozostałych słów i mean logp nie jest skalibrowanym prawdopodobieństwem. Historyczne INT8 i mniejsze-modelowe FAIL pozostają FAIL.

## 5. Plany niewdrożone
[Plan priorytetów użycia](https://github.com/jakamilek/CleverKeysPL/blob/5646c9157251d80c7ccfe6ceb143a3ca3bf6338b/docs/specs/polish-case-usage-priors.md): audyt obecnego korpusu producenta i lematów/odczytań, kontrola początku zdania, SIMC/PRNG identyfikatory, pomocnicze GUS BDL NSP2021 P4182 z weryfikacją SIMC-STAT i wielomiejscowych nazw. Proponowany kontrakt ma proweniencję, zakres/rok/mianowniki i unknown; konkretny JSON i współczynniki dopiero po audycie. Osobny dev/held-out i stratyfikowane regresje przed nowym pakietem.
Globalne pokrycie: dodam/grzeje/kasami/nawilżane/odpowiadam/patrzysz/poczekaj/podpowie/pozdrawiam oraz kapitalizacją/kapitalizacje. Źródłowa lematyzacja szerszego słownika, pełny ranking różnych słów, interpunkcja SI, czasy BS i inne locale później.

## 6. Weryfikacja i niewiadome
14 Git blobów sprawdzonych według lokalnego Git SHA przed commitem. Lokalnie XML obu opisów, YAML/osadzony Python, pipefail/oryginalny mandatory conformance marker, limit todo474 i rejestracja istniejących klas testów PASS. Brak lokalnego SDK/Kotlin.
7 nowych pure regresji (w tym wszystkie24 rankingi, rzeczywisty v5, wspólne/wybrane wielkie pisownie, krótkie listy, języki/kształty/immutability przez niezmieniony input, aligned weights/exact-case, idempotence i zakaz reuse) oraz2 rzeczywiste handler regresje full inputs/precommit/single commit/strip/Shift. Istniejące nazwy testów, SI-off/timeout/late/editor i pozostałe gates zachowane.
Aktualne compile/Kotlin/native conformance/mock/lint/APK pending. Strukturalne i callback testy nie dowodzą trafności modelu. Nowe priorytety/populacja/liczniki nie są implementowane ani mierzone. Źródła GUS/NKJP przeglądnięte informacyjnie; pełnych tabel nie pobrano.
Trafność pozycji wariantów, szybkość/PSS/energia i zachowanie telefoniczne v4 nieweryfikowane.

## 7. Gałęzie i integracja
Runtime trial/herbert-live-v1: 5646c9157251d80c7ccfe6ceb143a3ca3bf6338b; rodzic0acb647606cb52f0a3263b098704745306b5d6b7; drzewod461bd05678788520498fc7303c433d8a6209fb7.
[Draft PR4](https://github.com/jakamilek/CleverKeysPL/pull/4) obejmuje także wcześniejszą zaakceptowaną bazę; opis dostosowany do v4. Bez merge/release/tag/version bump. Producent: tylko ten dokument main, bez zmian danych/kodu/wag.
AGENTS/spec/Polish+base explanation/instrukcja/ToC/todo i workflow identity aktualne. Pozostałe locale nadal backlog.

## 8. Runy i artefakty
Nowe [live38037428188](https://github.com/jakamilek/CleverKeysPL/actions/runs/38037428188) i [CI38037431013](https://github.com/jakamilek/CleverKeysPL/actions/runs/38037431013): in_progress przy pierwszym odczycie, dokładny commit5646c9157251d80c7ccfe6ceb143a3ca3bf6338b. Nie potwierdzono nowego APK. Oczekiwana tożsamość compact-case-v4,compactCasePresentation=true,distinctLeadingTarget3; previous ordinaryDecodedForms/sharedSourceLemma/max4/first5 nadal.
Poprzednie v3 oba SUCCESS i dowody w PROJECT_MILESTONE_2026-10-10_ORDINARY_WORD_FORMS_APK_READY.md:2874 pure/193 live/298 standard (nie sumować duplikatów), debug lint0 Error/Fatal/234 innych, wszystkie compile/lint/security/quality/size/APK gates PASS.
Poprzedni APK11662738564: ZIP SHA a9e41c38ae60f5dda97bc9196c1afc4da3ecd92d2cffe3de54af0afe5bd54376; APK CI SHA fc79a7eca9b06b9fa2d2b5796d07d85482a6c444ba024bb060e91ccd91ed353d. Nie jest v4. Raport11662678682 SHA c119fe2c323814b4278e6ec1004d477a4dbe63d8de9b004c2d1ce3842f203547 lokalnie rehashowany/odczytany; APK raw nie rehashowany lokalnie.
Model niezmieniony: producentd831e17b6cb99590d6ba036e92a72b6c3fd0cc7c /run37230171787 /artefakt11312693984 /SHA f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2. Ten sam import i pakiet można zachować.
v5 ZIP SHA aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb; sidecar SHA5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d, dane/fixture niezmienione.

## 9. Ograniczenia
Ekspozycja v4 uwalnia początek paska, lecz nie udaje priorytetu rzadkości. SI może preferować Pracą dla drugiego klucza; nie nadpisujemy tej oceny arbitralną regułą. Wariant przegranej kapitalizacji może wymagać przewinięcia i wypaść poza Top3 — świadomy kompromis zamiast stałej rezerwacji.
Model nadal ocenia tylko małą grupę, nie całe słownictwo. Bez rozpoznanej formy lub dowodu lematu nie generuje końcówek. Historyczny PSS procesu~2132MiB pozostaje, bez nowych pomiarów. W SI timeout zachowuje bazowego zwycięzcę, ale prezentacja wariantów jest kompaktowa.

## 10. Następny krok
Po zgłoszeniu zakończenia obu runów sprawdzić wszystkie obowiązkowe jobs/logi/current SHA, mandatory original-tokenizer/native marker i artefakty. Nie podawać poprzedniego APK jako nowego.
Po udanym CI próbować praca/pracą/Praca/Pracą i inne słowa, Łódź/łódź i Maliną/maliną (SI on/off/timeout, Shift/początek zdania), przewinięcie i wybór alternatywy bez utraty tekstu; osobno wstawienie i Top3. Bez wymuszenia numeru miejsca przegranej kapitalizacji.
Potem audyt danych producenta według planu priorytetów; nie retunować progu na jednym zdaniu. Monitoring Actions maks60s TOTAL/run; po pierwszym odczycie przerwany, użytkownik zgłasza zakończenie. Nie czekamy w pętli do końca.

## 11. Delta
Względem PROJECT_MILESTONE_2026-10-10_ORDINARY_WORD_FORMS_APK_READY.md: jakościowe przyjęcie v3 i nowy problem przesadnej ekspozycji; rozdzielenie pełnego wejścia modelu od końcowego paska,14 plików,9 nowych regresji i nowy guard prezentacji. Aktualne dwa CI rozpoczęte, brak nowego APK/telefonu PASS. Źródłowe priorytety mają osobny plan; model/pakiet/dane/BS/defaulty bez zmian.
