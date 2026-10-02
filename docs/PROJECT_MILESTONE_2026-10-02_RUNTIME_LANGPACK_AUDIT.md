# Kamień milowy — audyt architektury runtime ↔ langpack

Data: 2026-10-02
Typ: stan przekrojowy projektu
Poprzednia faza: rozdzielenie runtime i pakietu PL oraz audyt gałęzi eksperymentalnych
Następny etap: minimalny kontrakt Language Intelligence Provider; bez implementacji przed zamknięciem kontraktu

## 0. Stan zweryfikowany

CleverKeysPL
- repozytorium: jakamilek/CleverKeysPL
- main HEAD: c6fa9f0b3b8c8976cefa2b0b34e39504f121bec4
- ostatni commit: docs: record runtime/langpack audit conclusions

CleverKeys-langpack-pl
- repozytorium: jakamilek/CleverKeys-langpack-pl
- main HEAD: b7895f4675304f3bfa447c424b76e9ef902379b0

Upstream runtime
- repozytorium: tribixbite/CleverKeys
- audytowane/przypięte źródło runtime: 263bd0abc03dec420f60fa073a9d2c5e25a176b5
- fork projektu runtime: jakamilek/CleverKeysPL

## 1. Zaakceptowana architektura

Docelowy układ pozostaje rozdzielony:

CleverKeysPL
  -> Language Intelligence API
  -> wersjonowany artefakt pakietu językowego
  -> CleverKeys-langpack-pl

Runtime jest uniwersalnym silnikiem. Pakiet językowy jest dostawcą wiedzy językowej. Repozytoria nie są scalane.

## 2. Zaakceptowany podział odpowiedzialności

CleverKeysPL:
- Android runtime;
- wejście i UI;
- swipe i dekodery;
- generowanie kandydatów przez silnik;
- ranking runtime;
- istniejący context reranking;
- konsumpcja Language Intelligence API.

CleverKeys-langpack-pl:
- polski słownik;
- częstotliwości i priorytety;
- morfologia;
- wiedza o kapitalizacji;
- rozróżnienie rzeczownika pospolitego i nazwy własnej;
- nazwy własne i miejsca;
- metadane językowe;
- przyszła polska wiedza kontekstowa/modelowa;
- budowa wersjonowanego artefaktu danych.

## 3. Co już działa w runtime

LanguagePackManager:
- importuje ZIP;
- wymaga manifest.json i dictionary.bin;
- waliduje CKDT V2;
- przechowuje pakiet w files/langpacks/{code}/;
- udostępnia getDictionaryPath(code);
- obsługuje opcjonalne elementy pakietu.

Blob:
src/main/kotlin/tribixbite/cleverkeys/langpack/LanguagePackManager.kt
SHA: afb0b4b4a8525a5f8f147c0e6e7ad4d2dc4e2597

WordPredictor korzysta najpierw z zainstalowanego langpacku, a następnie ładuje dictionary.bin przez BinaryDictionaryLoader.

Bloby:
- WordPredictor.kt: 70b6ffe89c64d971ccb4c6ad2b9f731324340399
- BinaryDictionaryLoader.kt: 2f887680cd9cc913648921c385ea3b9acf67b75a

## 4. Główna luka

Obecny CKDT V2 i Map<String, Int> nie reprezentują jeszcze:
- canonicalForm;
- morfologii;
- kapitalizacji;
- commonNoun;
- properName;
- metadanych źródła/modułu;
- wielu powierzchni tego samego klucza leksykalnego.

Obecny artefakt jest więc przede wszystkim słownikiem i sygnałem częstotliwości, a nie pełnym Language Intelligence Layer.

## 5. Obecne punkty integracji

Predictor jest interfejsem oddzielającym konsumentów od konkretnego WordPredictor.

Blob:
src/main/kotlin/tribixbite/cleverkeys/Predictor.kt
SHA: a1ac6ed0a99b492278ce2f3490d261a186e0d7d1

Istnieją m.in.:
- predictWordsWithContext;
- getSwipeContextEvidence;
- getNextWordCandidates;
- explainScore.

## 6. Istniejący context reranking — zostaje

SwipeContextRescorer jest już czystym mechanizmem runtime.

Blob:
src/main/kotlin/tribixbite/cleverkeys/swipe/SwipeContextRescorer.kt
SHA: a54bb2d9002a0d634f008e39f999955873c5ccb1

Jego zadanie to zmiana kolejności już wygenerowanych kandydatów na podstawie kontekstu. Nie tworzymy drugiego rerankera dla języka polskiego.

SuggestionHandler.handleSwipePredictionResults() wykonuje obecnie kolejno m.in.:
1. przywrócenie znanej kapitalizacji słów użytkownika;
2. Shift/autocap;
3. istniejący context rescoring;
4. augmentacje;
5. prezentację i automatyczne zatwierdzenie.

Blob:
src/main/kotlin/tribixbite/cleverkeys/SuggestionHandler.kt
SHA: edb9bce20c1b13353e1dc7ad40f4301d9bcb90c0

## 7. Kapitalizacja — ustalenia

Zaakceptowane reguły:
- rzeczownik pospolity ma pierwszeństwo przed sygnałem nazwy własnej;
- przymiotnik nie jest automatycznie kapitalizowany tylko dlatego, że pochodzi z nazwy własnej;
- dual-casing traktujemy jako wariant powierzchni, nie jako dwie niezależne pozycje leksykalne;
- UserDictionary pozostaje osobnym źródłem.

Wniosek z audytu runtime: nie osiągamy dual-casing przez dodanie dwóch kopii tego samego klucza w CKDT.

## 8. Pipeline pakietu PL

Bieżący build_pl_preview.py łączy m.in.:
- ranking wordfreq;
- AOSP LatinIME jako dowód obecności;
- Hunspell;
- filtrowanie błędów i obcych dominacji;
- audyty kapitalizacji;
- moduły nazw, miejsc, TERC, państw i stolic;
- ręcznie zweryfikowane wpisy.

Blob:
scripts/build_pl_preview.py
SHA: 986a02b7dd2a05a21178b38f1b743bab84a7cde7

## 9. Historycznie zweryfikowany artefakt PL

Ostatni zapisany audyt pakietu wskazywał:
- źródłowy commit: a1fa0193fc504e5fe81d9d43c23fd9a1e52ad307;
- preview run: 382;
- artifact: cleverkeys-pl-preview;
- artifact id: 11189614575;
- SHA256 ZIP: 827a20f8489fad51023e1c0d58319dca030d304f7e213ef4973141251c3ad9ff;
- wewnętrzny SHA artefaktu: 301b0b9c7c4c7b96ac7a2545bf27745b6ee38c87f5d04133ede490008d861945;
- wordCount: 106363;
- version: 2;
- hasPrefixBoost: false;
- immutable core: 100000;
- modułowe dodatki: 6363;
- registry conflicts: 0;
- naruszenia kapitalizacji: 0.

To jest stan historycznie zweryfikowany. Przed traktowaniem go jako najnowszego artefaktu publikacyjnego trzeba ponownie sprawdzić najnowszy run.

## 10. Language Intelligence API v1 — obecny stan decyzji

Propozycja API v1 powstała na osobnych gałęziach dokumentacyjnych:
- CleverKeysPL: docs/language-intelligence-api-v1-2026-10-02
  blob: 9d38b251037239c5baef20eb1c1ff8e9368cb4a3
- CleverKeys-langpack-pl: docs/language-intelligence-api-v1-2026-10-02
  blob: e2c0c80d176fa4cbbbd0b5478d6789cf091e4e9b

Ważne: jest to propozycja kontraktu, nie dowód implementacji na main.

Zaakceptowane założenia logiczne:
- API nie generuje nowych kandydatów;
- runtime generuje kandydatów;
- langpack dostarcza wiedzę o kandydacie;
- logiczne pola mogą obejmować surface, canonicalForm, frequency, morphology, capitalization, commonNoun, properName, metadata;
- capability są deklarowane przez pakiet;
- brak capability jest dozwolony;
- starszy pakiet ma działać przez fallback;
- UserDictionary nie jest częścią oficjalnej wiedzy langpacku.

Nadal NIE ustalono: konkretnego schema JSON, formatu binarnego, nazw klas Kotlin, nazw plików nowego formatu, wag scoringowych i szczegółów serializacji.

## 11. Z czego zrezygnowaliśmy

Monorepo / scalanie projektów:
- exp/unified-pl-project-2026-10-01 pozostaje proweniencją historyczną;
- nie kopiować trwale drzewa langpack-pl, źródeł danych i workflowów językowych do runtime.

Hurtowe przeniesienie exp/context-reranking-runtime-2026-10-01:
- gałąź jest eksperymentem;
- jest rozbieżna z bieżącym main;
- nie kopiować ani nie scalać jej w całości;
- jej wartością jest potwierdzenie punktu integracji, który obecny main już posiada.

Drugi polski reranker:
- nie budujemy osobnego polskiego rerankera;
- istniejący SwipeContextRescorer pozostaje mechanizmem runtime.

Nieograniczony generator z API:
- Language Intelligence API nie staje się drugim generatorem słów.

Mieszanie UserDictionary z pakietem:
- oficjalne dane langpacku i dane użytkownika pozostają osobnymi źródłami.

## 12. Co zaakceptowane, ale jeszcze niewdrożone

Docelowo potrzebujemy dostawcy wiedzy językowej odpowiadającego dla już istniejącego kandydata m.in. o:
surface, canonicalForm, frequency, morphology, capitalization, commonNoun, properName, metadata.

Docelowy przepływ:
decoder -> kandydaci -> wzbogacenie wiedzą językową -> istniejący context reranking -> prezentacja/commit

## 13. Plan

1. Zdefiniować minimalny LanguageIntelligenceProvider po stronie runtime.
2. Zmapować, które informacje są już rzeczywiście dostępne w artefakcie PL, a których jeszcze nie ma.
3. Ustalić minimalne rozszerzenie artefaktu bez łamania obecnego CKDT i fallbacku.
4. Dodać model wariantów powierzchni dla dual-casing bez duplikowania tożsamości leksykalnej.
5. Włączyć metadata do przepływu kandydatów.
6. Dodać testy kontraktu, fallbacku i zgodności starszego pakietu.
7. Dopiero potem implementować zmiany.

## 14. Znane ograniczenia

- runtime nie ma jeszcze pełnego Language Intelligence Layer;
- manifest runtime nie deklaruje jeszcze apiVersion ani capability nowego kontraktu;
- obecny loader zna przede wszystkim słowo i częstotliwość;
- dokładny format wielowariantowych powierzchni nie jest ustalony;
- bieżący main runtime nie ma w tym audycie potwierdzonego statusu CI green;
- historyczny run 382 nie jest automatycznie uznany za najnowszy artefakt.

## 15. Reguła wejścia dla następnej instancji

Przed nowym audytem:
1. przeczytaj najnowszy PROJECT_MILESTONE_*.md w obu repozytoriach;
2. przeczytaj PROJECT_CONTINUITY_RULE_MILESTONES.md w obu repozytoriach;
3. zweryfikuj bieżące HEAD-y main;
4. nie rozpoczynaj od analizy wszystkich historycznych branchy;
5. historyczne branche analizuj tylko wtedy, gdy kamień milowy wskazuje konflikt lub nowy etap tego wymaga.

## 16. Relacja z wcześniejszą dokumentacją

Kamień milowy nie zastępuje wcześniejszych ADR i audytów. Ma być pierwszym dokumentem wejściowym dla kolejnej instancji.