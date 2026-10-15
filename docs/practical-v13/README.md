# Polski langpack v13 — zatwierdzone dodatki

Baza: zaakceptowana na telefonie v11. V12 pominięta. Użytkownik 15.10.2026 zatwierdził 1087 kandydatur, odrzucił 269 i polecił budowę. Zapis decyzji: source/approved-practical-v13/decision.json. Pozostałych rezerw nie dodano.

Pakiet: cleverkeys-pl-practical-v13.zip. Importować jako polski langpack w dotychczasowym APK v11; nowy APK nie jest potrzebny. Import zastępuje poprzednią polską paczkę. Zachowano wszystkie 204463 stare słowa, wagi, 114299 wpisów metadanych oraz wzajemną kolejność starych aliasów.

Wynik: 205550 słów, 115386 wpisów metadanych, 1811515 elementów JSON, 28756734 bajty metadanych. Koszt dodatków z opisem etapu: 160561 bajtów i 10178 elementów JSON. W limicie pozostaje 4614 wpisów, 188485 elementów JSON i 4797698 bajtów.

SHA-256 ZIP: `30a1a296e0478d6ac89af59bbb28410c18d462e39815611e692db85c6238634a`.

Lokalnie wykonano test pełnego odczytu oraz cold/replace/repeat na źródłach czytnika zaakceptowanego APK 0b94e323789e96c44a77f762a6f83fa11e285699. Trzy ostatnie przy stercie 192 MiB i dodatkowej tablicy 16 MiB. To nie jest pomiar RAM telefonu ani test poprawy Top-3. Import na telefonie pozostaje do sprawdzenia przez użytkownika.

Wagi nowych słów: dotychczasowy przelicznik logarytmiczny wordfreq 3.2.0, commit 912caf64b657478d1dff1138efdc078947d54bb1, względem maksimum v11. Żadnej starej wagi nie przeliczono. Częstości dotyczą zapisu, nie konkretnych znaczeń.

Do odtworzenia użyj workflow approved-practical-v13.yml. Pobiera przypięty artefakt v11 z runu 38437507820, kontroluje jego SHA, tworzy pakiet i porównuje raport z reviewed-build-report.json. Lista zatwierdzona i jej SHA są zamrożone; proces nie dobiera kolejnych słów. Dokładne dane źródłowe zostają w metadanych, a historyczny audyt w gałęzi audit/practical-candidates-v11.
