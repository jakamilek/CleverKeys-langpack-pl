# Backspace: bezpośrednie przeciąganie i kolejne usuwanie słów — v12

## 1. Zweryfikowany stan i data
2026-10-04, przed aktualizacją wyniku CI: main CleverKeysPL
beee16c9f1cf3aecddd4f2c58d2bc435cb6b8c1b; main CleverKeys-langpack-pl
ee026fd2b055579824040ea0f56c295d8a6a5027. Oba mainy otrzymują wyłącznie
aktualizację tego dokumentu ciągłości. Runtime docs/source-variants-integration-v1 przesunięto
fast-forward z 5200f718a0a9f2cf29135d6e8607c171d308f889 do
23b6f6923344f69a11df14e6f01d22f0e8abecd8. Draft PR #1 pozostaje otwarty.
Odczyt wszystkich 18 zmienionych blobów tego commita zgadza się z hashami
przygotowanych plików lokalnych.

Wspólny zapis: [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-04_BACKSPACE_DIRECT_V12.md)
oraz [CleverKeys-langpack-pl](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-04_BACKSPACE_DIRECT_V12.md).

## 2. Architektura
Modern Backspace ma trzy tryby: WORD_PREVIEW, WORD_GAP i DRAG.
Bezpośredni ruch w lewo od BS przejmuje dotyk przed długim naciśnięciem,
zaczyna od pustego zaznaczenia przy kursorze i zaznacza znaki punktami Unicode.
Nieruchome przytrzymanie zaznacza poprzedni wyraz; po 350 ms usuwa zweryfikowane
zaznaczenie, czeka 200 ms i zaznacza następny. Ruch w lewo podczas cyklu przełącza
na DRAG do końca tego dotyku. Hamowanie DRAG nigdy nie wznawia usuwania słów.
Puszczenie kończy gest; podczas przerwy nie usuwa kolejnego wyrazu.

## 3. Zaakceptowane ustalenia
Użytkownik zlecił bezpośrednią aktywację przeciąganiem oraz cykl zaznaczania i
usuwania kolejnych wyrazów bez podnoszenia palca. Zachowujemy separator przed
usuwanym wyrazem, obsługę ruchu poza BS na pozostałych klawiszach oraz hamowanie,
wznowienie i cofanie zaznaczenia. Dotychczasowy krótki BS działa według wybranego
trybu, domyślnie kasuje znak/spację. Polski interfejs ma priorytet.

Pierwszy podgląd używa istniejącego longpress_timeout. Przyjęte 350/200 ms
stanowią stałe prototypu, nie nowe ustawienia; nie są jeszcze zaakceptowane
na telefonie. Ruch startowy korzysta z istniejącego resumeDp (domyślnie 24 dp)
i wymaga przewagi poziomego ruchu nad pionowym większej niż 2:1, zachowując
diagonalne flicki. Suwak dostępny również przy wyłączonym hamowaniu.

## 4. Rozwiązania odrzucone
Nie wymagamy hold przed DRAG. Nie wznawiamy cyklu słów w zatrzymanym DRAG.
Nie wysyłamy niezweryfikowanego DEL po odmowie nowoczesnego edytora.
Nie odczytujemy zmieniających się ustawień w połowie gestu. Nie resetujemy danych
użytkownika. Nie ma merge, tagu, release lub zmiany wersji aplikacji.

## 5. Niewdrożone plany
Osobne suwaki czasu podglądu/przerwy nie zostały dodane. AI/CTC, szersze metadane
oraz kontekstowy ranking top 3 pozostają osobnym planem. Tłumaczenie czterech
zmienionych znaczeniowo zasobów w 20 pozostałych zestawach językowych jest
odłożone w memory/todo.md, zgodnie z priorytetem polskim.

## 6. Weryfikacja i jej granice
Dopisano 13 regresji w już zarejestrowanych BackspaceHoldTest (34 przypadki
po zmianie) oraz PointersBackspaceHoldTest (20). Obejmują bezpośredni start,
density i dystans startowy, cykl dwóch faz, puszczenie podczas przerwy, stare
wiadomości timerów, przejście do DRAG i hamowanie, Unicode, odmowę commitText,
zmianę połączenia/tekstu, synchroniczne callbacki i rzeczywisty przepływ od
Pointers przez timer do KeyEventHandler i bufora edytora. Testy Android/Kotlin
NIE zostały wykonane lokalnie — brak skonfigurowanego toolchaina.

Lokalne kontrole PASS: git diff --check; poprawny XML i unikalne nazwy zasobów
PL/EN; generator wyszukiwarki ustawień (151 wpisów); komplet jawnych metod na
ścieżce pointer→view→Config handler→edytor; Bun 1.3.11 frozen install; Astro
84 strony; 103 odnośniki wewnętrzne na czterech zmienionych stronach rozwiązują
się do plików. Pierwsze wywołanie build:termux nie znalazło bun na PATH;
poprawiono PATH i właściwy build zakończył się sukcesem. Lockfile nie zmienił się.

[CI run 37189695279](https://github.com/jakamilek/CleverKeysPL/actions/runs/37189695279)
zakończył się SUCCESS dla dokładnego head 23b6f692. Logi potwierdzają 2804 testy
pure JVM i 240 testów skupionych (łącznie 3044), w tym 34 BackspaceHoldTest
oraz 20 PointersBackspaceHoldTest. assembleDebug, lint debug i release,
Code Quality Checks, Security Scan (gate fixed HIGH/CRITICAL) i APK Size Analysis
zakończyły się sukcesem. Upload test results zgłosił brak build/reports/tests/:
wynik testów potwierdzają logi JUnit, nie osobny artefakt raportów.
APK i lint-results są dostępne. Odczyt po zgłoszeniu użytkownika zakończył weryfikację;
obowiązuje maksymalnie 60 sekund monitorowania łącznie na build.
Telefon jeszcze nie testował v12.

## 7. Gałęzie i historia
Runtime trial pozostaje na docs/source-variants-integration-v1, draft PR #1.
V9 użytkownik przyjął jakościowo na telefonie. Runtime 5200 ma zielony run
37185565077 (3031 testów, oba lint, dotychczasowy gate fixed HIGH/CRITICAL),
ale ten wynik nie weryfikuje nowego v12. Wcześniejsze v5/v6 problemy drag/release
pozostają bez dowiedzionej przyczyny; nie wnioskujemy jej z tej zmiany UX.
Producer feature/source-variants-trial-v1 pozostaje na bb55e87f5bfa2c7ce2a3eb2214cf5a7f3031205f.

## 8. Artefakty i integracja
Commit runtime 23b6f6923344f69a11df14e6f01d22f0e8abecd8, rodzic 5200f718.
Nowy marker placu testowego: backspace-direct-v12. Nowe metody beginBackspaceDrag,
deleteBackspaceHoldWord i previewPreviousBackspaceWord są jawnie przekazywane
przez oba interfejsy i Keyboard2View. Anulowane identyfikatory timerów są
unieważniane, a kontynuacja wyrazu instalowana przed commitText, by odebrać
synchroniczne potwierdzenie kursora. Przy kolejnym podglądzie sprawdza połączenie,
EditorInfo, pozycję, zaznaczony tekst i pozostający fragment przed kursorem.

Nowy [apk-debug, artifact 11298891131](https://github.com/jakamilek/CleverKeysPL/actions/runs/37189695279/artifacts/11298891131)
ma 97046331 bajtów; GitHub podaje digest ZIP
sha256:d37038a4e1124085809ee09a12ca1c259e876509a7caba5ae3d6f3cbcb010972
oraz wygaśnięcie 2026-10-11T08:51:58Z. To digest artefaktu ZIP, nie pojedynczego APK.
lint-results: artifact 11299075649, 15640 bajtów, digest ZIP
sha256:b9c86d04cf5ffc242cea9dbe23c5953e514392817bab29fab4bce016c8983993.
Ostatni wcześniejszy zielony APK pozostaje opisany w
[poprzedniej stabilizacji](PROJECT_MILESTONE_2026-10-04_CI_STABILIZATION.md).
Langpack i producer nie zmieniły się w tym etapie. Hash lokalnego packa v4
3767c76dbf87589182d6b26b8f8d64d80ec635764cee15d350015b60d41e21af i jego
źródła pozostają opisane w [kamieniu kapitalizacji](PROJECT_MILESTONE_2026-10-04_FUNCTION_WORD_CASING.md).
Nie odczytywano w tym etapie wyników producer CI ani nie potwierdzano jego artefaktu.

## 9. Ograniczenia
Nowa obsługa wymaga edytora z poprawnymi API zaznaczania. Prywatne pola, terminale
i tryby wewnętrzne zachowują fallback. Bounded read i reguła całego poprzedniego
wyrazu zachowują dotychczasowe granice: nie usuwamy obciętego początku długiego
tokenu; trailing spacje/tabulatory należą do podglądu, podgląd na końcu linii
nie przechodzi przez znak nowej linii. Utrata walidacji zatrzymuje nowy cykl.
Puszczenie podczas podglądu respektuje releaseDelete; to ustawienie nie wyłącza
automatycznych usunięć przy dalszym przytrzymaniu. Cancel nie przywraca już
usuniętych słów, ale nie kasuje aktualnego podglądu. Brak nowych kluczy ustawień
i zmian formatu backupu. Pełne phone/instrumented/minified/performance nadal otwarte.

## 10. Następny krok
Zainstalować APK v12 z potwierdzonego artefaktu i przetestować na telefonie:
przeciągnięcie bez hold, trzy kolejne wyrazy przy nieruchomym hold, puszczenie
między wyrazami, przejście od podglądu do DRAG oraz hamowanie i cofanie bez
wznowienia cyklu słów. Sprawdzić zachowanie separatorów i brak aktywacji innych
klawiszy podczas przeciągania. Zachować limit monitorowania kolejnych buildów.

## 11. Różnica wobec poprzedniego kamienia
[Poprzedni etap](PROJECT_MILESTONE_2026-10-04_FUNCTION_WORD_CASING.md) naprawił dane
Ale/Lub w producer i przygotował pack v4. Ten etap zmienia wyłącznie runtime
Backspace zgodnie z nową instrukcją użytkownika, uaktualnia polskie opisy i
specyfikacje oraz dodaje 13 regresji. Lokalne kontrole dokumentacji są zielone;
nowy CI potwierdza kompilację, 3044 testy i oba lint. APK v12 jest dostępne;
akceptacja gestów na telefonie pozostaje otwarta.
