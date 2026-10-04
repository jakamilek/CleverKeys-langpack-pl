# Nowe słowo: początek paska podpowiedzi i dostarczenie poprawki ale/lub — v15

## 1. Zweryfikowany stan i data
2026-10-04. Przed dokumentem main CleverKeysPL:
a019f0f223698ff611bbc5c5e7375102cea01feb; main CleverKeys-langpack-pl:
9158646ff69f0e0885e28ac131da2266708ec728. Oba mainy otrzymują wyłącznie ten zapis ciągłości.
Runtime trial docs/source-variants-integration-v1 przesunięto fast-forward z
95f302c1d528bd9d006e5660697f6a307b983ce2 do 4e51c3b45285fdbfdc93531bd80e228444601818.
Draft PR #1 pozostaje otwarty. Nowe drzewo 8fcb9ef867d1629a2da63d6cbc6b81fa5dd0e982
jest identyczne z przygotowanym lokalnie; dziewięć zmienionych plików.

Wspólny zapis: [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-04_WORD_STRIP_V15.md)
i [CleverKeys-langpack-pl](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-04_WORD_STRIP_V15.md).

## 2. Architektura
SuggestionBar.resetScrollPosition wykonuje post do swojego HorizontalScrollView
i sprawdza, czy w chwili wykonania nadal należy do tego samego rodzica.
SuggestionHandler wywołuje reset przy zaakceptowanym niepustym wyniku swipe,
pierwszym punkcie kodowym wpisywanego prefiksu po synchronizacji z edytorem,
separatorze kończącym słowo oraz Enter/akcji edytora poza trybem hasła.
Reset viewportu jest niezależny od renderowania zawartości: identyczna lista
z kolejnego gestu też wraca do początku. Dalsze litery i aktualizacje cursor-sync
nie wywołują resetu. Wewnętrzne apostrofy/łączniki zachowują dotychczasową gałąź.

## 3. Zaakceptowane ustalenia i diagnoza
Użytkownik zgłosił brak resetu przy następnym słowie oraz nadal tylko Ale/Lub.
Na pytanie o osobny import v4 odpowiedział „Tylko nowe APK”.
Poprawka ale/lub znajduje się w langpacku v4; aktualizacja APK nie zastępuje
wcześniej zaimportowanego słownika. Użytkownik dostał link i instrukcję importu.
To wyjaśnia brak dostarczenia poprawki danych; nie odczytano faktycznych bajtów
z telefonu ani ewentualnej pisowni w słowniku użytkownika.
Nowe słowo ma zawsze pokazywać początek listy. Obecna opcja resetu po BS
pozostaje oddzielną kontrolą dotyczącą wyłącznie kasowania.

## 4. Rozwiązania odrzucone
Brak ręcznej blacklisty Ale/Lub, zdublowanych wpisów CKDT i zmiany wag w runtime.
Pack v4 poprawia kanoniczną pisownię według danych gramatycznych, zachowując rangi.
Nie resetujemy po każdej literze ani z każdej asynchronicznej aktualizacji listy.
Nie dodajemy zbędnej opcji dla początku kolejnego słowa.
Bez merge, tagu, release, zmiany wersji aplikacji i promocji trial do main.

## 5. Niewdrożone plany
Kontekstowy ranking form, szersze metadane i AI/interpunkcja pozostają odrębnym etapem.
Nowych par dla homonimicznych nazw ale/lub w sidecarze nie dodano; dostępne są
ręczny Shift i pisownia użytkownika. Inne tłumaczenia pozostają w backlogu;
w v15 nie zmieniono zasobów ani preferencji. Nie zmieniono dynamiki BS ani czasów słów.

## 6. Weryfikacja i jej granice
Lokalne PASS: git diff --check; generator wyszukiwarki — 145 wpisów;
Astro — 84 strony; 54 odnośniki wiki/spec na dwóch zmienionych stronach;
cztery ścieżki resetu i rejestracja nowej klasy testów. package.json i bun.lock
bez zmian. Budowa korzystała z zależności v14 z wcześniejszego frozen install,
bez zmiany lockfile. GitHub utworzył dokładnie to samo drzewo co lokalne git write-tree.

Dodano sześć regresji w skupionym CI: trzy SuggestionStripScrollTest dotyczą
rzeczywistego posted resetu, powtórzenia i zmiany/odłączenia rodzica; trzy w
LearningFunnelBookkeepingTest prowadzą rzeczywisty tracker/handler przez
tap → separator → tap, dwa identyczne swipe oraz swipe → tap → Enter.
Test tapów wyłącza reset po BS, potwierdzając niezależność zakresów.
Lokalnie brak Android/Kotlin toolchaina: testy nie zostały tu wykonane.
Nowego runtime CI ani bieżącego runu v14 nie odczytywano i nie monitorowano
w tym etapie zgodnie z prośbą użytkownika. Wykonanie testów/build/lint i telefon
v15 pozostają niepotwierdzone. Limit monitorowania 60 sekund łącznie na build trwa.

## 7. Gałęzie i historia
Runtime trial i draft PR #1 zachowane. V13 przeszedł 3049 testów, build i oba lint;
użytkownik zaakceptował ruch, zgłaszając wyjątek SimpleX. V14 porządkuje trzy
zakresy zaznaczenia edytora; wynik runu 37199887090 i telefon nadal nieodczytane tutaj.
V15 zawiera v14, lecz nie stanowi potwierdzenia naprawy SimpleX.
Producer feature/source-variants-trial-v1 pozostaje na
bb55e87f5bfa2c7ce2a3eb2214cf5a7f3031205f — kod producenta bez zmian.

## 8. Artefakty i integracja
Runtime commit 4e51c3b45285fdbfdc93531bd80e228444601818, rodzic 95f302c1d528bd9d006e5660697f6a307b983ce2;
marker placu testowego word-strip-v15. Dziewięć plików obejmuje handler, bar,
dwa zestawy testów, rejestrację w build.gradle, przewodnik/spec, TOC i todo.
Nowy APK v15 nie został jeszcze potwierdzony.

Odczytano wcześniej zakończony producer run
[37188544526](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37188544526):
completed/SUCCESS dla dokładnego bb55e87f5bfa2c7ce2a3eb2214cf5a7f3031205f.
[Artifact 11297484236](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37188544526/artifacts/11297484236) ma nazwę
cleverkeys-pl-function-words-trial, 906578 bajtów, expired=false, wygaśnięcie
2027-01-02T08:19:32Z. GitHub podaje digest zewnętrznego archiwum artefaktu:
sha256:b7344ed0185cf26feea9409316a5a9d4d04c7ff7b73f7d8afcb7ccf3a280802f.
Nie jest to hash wewnętrznego ZIP langpacka ani APK.

Wewnętrzny pack cleverkeys-pl-function-words-trial.zip ma wersję 4.
Lokalne, uprzednio zweryfikowane hashe: ZIP
3767c76dbf87589182d6b26b8f8d64d80ec635764cee15d350015b60d41e21af,
CKDT 868548d23415d22d04a6f0c5580e5c26ae1a72d64a68359288aa4a1d761b4bd9.
W tym etapie nie pobierano ani ponownie nie hashowano binarnego artefaktu GitHuba.
[Specyfikacja packa](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/bb55e87f5bfa2c7ce2a3eb2214cf5a7f3031205f/docs/FUNCTION_WORD_CASING_TRIAL_V1.md)
potwierdza nazwę ZIP i oddzielny import.

## 9. Ograniczenia
Import v4 i sprawdzenie na telefonie wymagają działania użytkownika; nie potwierdzono
jeszcze jego wykonania. Środek zdania sprawdza małe ale/lub, a początek po kropce
i Shift nadal mogą dawać dużą literę. Własna pisownia użytkownika może mieć
pierwszeństwo; danych użytkownika nie kasujemy. Rangi/klucze i dziewięciowpisowy
sidecar w v4 pozostają bez zmian; poprawiono 18 domyślnych pisowni.
Regresje viewportu są hostowe, nie zastępują sprawdzenia rzeczywistego scroll/fling,
motywu i edytora. Istniejące guards i granice BS pozostają.

## 10. Następny krok
Po zgłoszeniu zakończenia runów odczytać wyniki dla właściwych commitów,
zweryfikować APK v15 i oddzielnie status v14. Nie prowadzić bieżącego monitorowania.
Importować wewnętrzny ZIP packa v4 przez menedżer pakietów.
Sprawdzić „chcę ale nie mogę” i „kawa lub herbata”, następnie kropkę/Shift i istniejące
pary Łódź/łódź. Dla paska: przewinąć, wpisać następne słowo, wykonać kolejny swipe
również z tym samym rankingiem i sprawdzić początek listy; dalsze litery nie powinny
resetować pozycji. Powtórzyć z wyłączonym resetem BS.
Przeprowadzić oczekujący test SimpleX z v14 także na APK v15.

## 11. Różnica względem poprzedniego kamienia
[Poprzedni v14](PROJECT_MILESTONE_2026-10-04_BACKSPACE_ORDERED_V14.md)
dotyczył zgodności zaznaczenia w SimpleX. V15 dodaje reset viewportu nowego słowa,
sześć regresji i diagnozę niedostarczonego na telefon packa.
[Kamień funkcji słów](PROJECT_MILESTONE_2026-10-04_FUNCTION_WORD_CASING.md)
zawiera już poprawkę producer; ten etap potwierdza jej wcześniejszy CI/artefakt
i kieruje do importu, bez ponownej zmiany danych. Runtime CI i telefon v15 oczekują.
