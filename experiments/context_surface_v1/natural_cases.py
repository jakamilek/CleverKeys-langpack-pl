"""Fresh authored Polish continuations, not corpus samples or phone traces."""
from __future__ import annotations

import copy
from prototype import canonical_bytes

VERSION = "natural-sense-surface-v2"
SPECS = {
    "łódź": [("boat", "common_noun", "jednostkę pływającą"), ("city", "proper_name", "miasto")],
    "łodzi": [("boat", "common_noun", "jednostkę pływającą"), ("city", "proper_name", "miasto")],
    "malina": [("fruit", "common_noun", "owoc maliny"), ("surname", "proper_name", "nazwisko osoby")],
    "jagoda": [("fruit", "common_noun", "owoc jagody"), ("given_name", "proper_name", "imię osoby")],
    "róża": [("flower", "common_noun", "kwiat róży"), ("given_name", "proper_name", "imię osoby")],
    "polska": [("adjective", "adjective", "cechę związaną z Polską"), ("country", "proper_name", "państwo")],
    "warszawska": [("adjective", "adjective", "cechę związaną z Warszawą"),
                   ("street", "proper_name", "nazwę ulicy"),
                   ("surname", "proper_name", "nazwisko osoby")],
}

# Four categories, each 16 main cases with 8 lowercase and 8 capitalized forms.
# Each tuple: key, intended sense, exact text BEFORE the cursor.
ROWS = {
    "natural_direct": [
        ("łódź", "boat", "Przy pomoście kołysze się niewielka drewniana "),
        ("łódź", "city", "Miastem słynącym z ulicy Piotrkowskiej jest "),
        ("łodzi", "boat", "Rybak wymienia uszkodzone wiosło w swojej "),
        ("łodzi", "city", "Na weekend kupiłem bilet kolejowy do "),
        ("malina", "fruit", "Na krzaku przy płocie została ostatnia dojrzała "),
        ("malina", "surname", "Na liście nauczycieli widnieje pan Adam "),
        ("jagoda", "fruit", "Na dnie koszyka leży mała granatowa "),
        ("jagoda", "given_name", "Moja młodsza siostra ma na imię "),
        ("róża", "flower", "Z bukietu wypadła jedna czerwona "),
        ("róża", "given_name", "Babcia mówi, że jej siostra miała na imię "),
        ("polska", "adjective", "W radiu rozbrzmiewa tradycyjna muzyka "),
        ("polska", "country", "Krajem leżącym między Niemcami a Litwą jest "),
        ("warszawska", "adjective", "Za remont odpowiada niewielka firma "),
        ("warszawska", "adjective", "Przetarg wygrała spółka z Warszawy, czyli spółka "),
        ("warszawska", "street", "Wpisz w adresie nazwę ulicy: ulica "),
        ("warszawska", "surname", "Nowa klientka nazywa się Anna "),
    ],
    "natural_history": [
        ("łódź", "boat", "Kupiliśmy wiosła i kamizelki ratunkowe. W sobotę ruszamy na jezioro. Przy brzegu czeka nasza "),
        ("łódź", "city", "Chcemy zobaczyć dawne fabryki i ulicę Piotrkowską. Nocleg już zarezerwowany. Celem wycieczki jest "),
        ("łodzi", "boat", "Kadłub zaczął przeciekać, a silnik nie chce zapalić. Mechanik przyjedzie rano. Nie możemy teraz używać tej "),
        ("łodzi", "city", "Wybieramy się do miasta z Manufakturą i Piotrkowską. Pociąg odjeżdża o ósmej. Jutro będziemy w "),
        ("malina", "fruit", "Zerwaliśmy czerwone owoce z krzewów. Większość trafiła do słoików. Na talerzyku została jedna "),
        ("malina", "surname", "Zatrudniliśmy nowego nauczyciela, pana Adama. Dziś dostaliśmy dokumenty. Na końcu jest podpis: Adam "),
        ("jagoda", "fruit", "W lesie zbieraliśmy drobne granatowe owoce. Koszyk jest prawie pusty. Została w nim tylko jedna "),
        ("jagoda", "given_name", "W klasie pojawiła się nowa dziewczynka. Wychowawczyni przedstawiła ją wszystkim. Jej imię to "),
        ("róża", "flower", "Ogrodnik przyciął kolczasty krzew z czerwonymi kwiatami. Jeden kwiat zachował dla nas. To piękna "),
        ("róża", "given_name", "Przyszła nowa koleżanka mojej mamy. Przedstawiła się przy wejściu. Zapamiętałem jej imię: "),
        ("polska", "adjective", "Koncert dotyczy tradycji naszego kraju. W programie są utwory rodzimych kompozytorów. Będzie to muzyka "),
        ("polska", "country", "Rozmawiamy o państwie, którego stolicą jest Warszawa. W atlasie leży nad Bałtykiem. To "),
        ("warszawska", "adjective", "Wybieramy wykonawcę z Warszawy, a nie z Krakowa. Biuro ma w stolicy. To firma "),
        ("warszawska", "adjective", "Ta uczelnia działa w Warszawie i uczy mieszkańców stolicy. Porównujemy ją z gdańską. To uczelnia "),
        ("warszawska", "street", "Kurier potrzebuje adresu dostawy. Numer domu już podałem. Brakuje nazwy: ulica "),
        ("warszawska", "surname", "Przyjmujemy nową pacjentkę, panią Annę. Wypełnia formularz osobowy. Obok imienia wpisuje nazwisko: "),
    ],
    "natural_switch": [
        ("łódź", "boat", "Rano planowaliśmy wycieczkę do miasta z Piotrkowską. Jednak po południu wolimy popływać po jeziorze. Potrzebna nam będzie "),
        ("łódź", "city", "Najpierw rozmawialiśmy o remoncie jednostki pływającej. Teraz wybieramy miasto na wycieczkę do Manufaktury. Będzie to "),
        ("łodzi", "boat", "O podróży do miasta z Manufakturą porozmawiamy później. Teraz zdejmujemy silnik z jednostki pływającej. Pomóż mi przy tej "),
        ("łodzi", "city", "Wiosła zostawiamy w garażu, a rejs odwołujemy. Zamiast na jezioro pojedziemy pociągiem zwiedzać Piotrkowską. Ruszamy do "),
        ("malina", "fruit", "Skończyliśmy rozmowę o nauczycielu, panu Adamie. Teraz oglądamy owoce z ogrodu. Ten czerwony owoc to "),
        ("malina", "surname", "Owoce na dżem są już w garnku. Teraz sprawdzam listę pracowników szkoły. Widnieje na niej pan Adam "),
        ("jagoda", "fruit", "Moja siostra już poszła do domu. Teraz przebieramy leśne owoce w koszyku. Ten mały granatowy owoc to "),
        ("jagoda", "given_name", "Leśne owoce schowałem do lodówki. Teraz opowiem o nowej uczennicy. Ma na imię "),
        ("róża", "flower", "Moja koleżanka już wyszła. Teraz chcę opisać czerwony kwiat z kolcami. W wazonie stoi "),
        ("róża", "given_name", "Kwiaty zostały w ogrodzie. Teraz zapisujemy imiona uczestniczek spotkania. Pierwsza dziewczyna ma na imię "),
        ("polska", "adjective", "Listę państw skończyliśmy przed chwilą. Teraz rozmawiamy o muzyce tworzonej w naszym kraju. Interesuje nas muzyka "),
        ("polska", "country", "O rodzimych piosenkach porozmawiamy później. Teraz wskazujemy na mapie państwo ze stolicą w Warszawie. To "),
        ("warszawska", "adjective", "Nazwisko klientki już zapisane. Teraz wybieramy wykonawcę z Warszawy. Najlepsza będzie firma "),
        ("warszawska", "adjective", "Adres dostawy mamy gotowy. Teraz opisujemy komunikację w stolicy. Chodzi o komunikację miejską, czyli komunikację "),
        ("warszawska", "street", "Rozmowa z panią Anną skończona. Teraz wypełniamy adres koperty. W rubryce jest: ulica "),
        ("warszawska", "surname", "Nazwę ulicy już znamy. Teraz przedstawia się nowa właścicielka mieszkania. Nazywa się Anna "),
    ],
    "natural_negation": [
        ("łódź", "boat", "Nie pytam o miasto ani o ulicę Piotrkowską. Chodzi o drewnianą jednostkę pływającą. Czy jest tu wolna "),
        ("łódź", "city", "Nie chodzi mi o statek ani o jezioro. Pytam o miasto z ulicą Piotrkowską. Odpowiedzią jest "),
        ("łodzi", "boat", "Nie piszę o mieście. Opisuję jednostkę z kadłubem i wiosłami. Szukam nowego silnika do mojej "),
        ("łodzi", "city", "Nie wybieramy się na rejs. Chcemy zobaczyć Manufakturę i ulicę Piotrkowską. Kupiliśmy bilety do "),
        ("malina", "fruit", "To nie nazwisko nauczyciela, tylko nazwa czerwonego owocu z krzewu. W ręce leży dojrzała "),
        ("malina", "surname", "Nie zamawiam owoców. Szukam nazwiska pana Adama z listy nauczycieli. Pan Adam nazywa się "),
        ("jagoda", "fruit", "Nie wymieniam imienia dziewczynki. Opisuję drobny owoc znaleziony w lesie. To leśna "),
        ("jagoda", "given_name", "Nie chodzi o owoc ani o koszyk. Wpisujemy imię mojej siostry. Ma na imię "),
        ("róża", "flower", "Nie przedstawiam kobiety. Mówię o kwiecie z kolczastego krzewu. Ten czerwony kwiat to "),
        ("róża", "given_name", "Nie chodzi o bukiet. Zapisuję imię mojej babci. Nazywa się "),
        ("polska", "adjective", "Nie podaję nazwy państwa. Określam pochodzenie tych utworów. To tradycyjna muzyka "),
        ("polska", "country", "Nie opisuję stylu muzyki. Wymieniam państwo ze stolicą w Warszawie. Tym państwem jest "),
        ("warszawska", "adjective", "To nie nazwisko ani nazwa ulicy. Określam położenie siedziby firmy w Warszawie. Jest to firma "),
        ("warszawska", "adjective", "Nie podaję nazwy ulicy. Mówię o zwykłej ulicy położonej w Warszawie. To ulica stołeczna, czyli ulica "),
        ("warszawska", "street", "Nie opisuję ulicy położonej w Warszawie. Podaję jej oficjalną nazwę w adresie. To ulica "),
        ("warszawska", "surname", "Nie podaję adresu. Wpisuję nazwisko nowej pacjentki, pani Anny. W formularzu jest: Anna "),
    ],
}

START_CONTEXTS = {
    "łódź": ("Kadłub jest drewniany, a wiosła nowe. ", "Chcę zwiedzić miasto z Manufakturą. "),
    "łodzi": ("Mówię o jednostce pływającej, nie o mieście. ", "Rozmawiamy o podróży do miasta z Piotrkowską. "),
    "malina": ("Wszystkie owoce pochodzą z czerwonego krzewu. ", "Nauczyciel podał swoje imię i nazwisko. "),
    "jagoda": ("To był mały granatowy owoc leśny. ", "Nowa uczennica przedstawiła się klasie. "),
    "róża": ("Opisujemy czerwony kwiat z kolcami. ", "Moja babcia właśnie podała swoje imię. "),
    "polska": ("Opisujemy pochodzenie rodzimej muzyki. ", "Państwo nad Bałtykiem ma stolicę w Warszawie. "),
    "warszawska": ("Opisujemy pochodzenie firmy ze stolicy. ", "Nowa klientka przedstawiła się jako pani Anna. "),
}


def build():
    entries = []
    for key, specs in SPECS.items():
        common = [s[0] for s in specs if s[1] != "proper_name"]
        proper = [s[0] for s in specs if s[1] == "proper_name"]
        entries.append({"surfaceKey": key, "capitalization": {"defaultSurface": key, "variants": [
            {"surface": key, "casePolicy": "lowercase", "senseIds": common},
            {"surface": key[0].upper() + key[1:], "casePolicy": "capitalized", "senseIds": proper}]},
            "senses": [{"id": sid, "kind": kind, "descriptionPl": description} for sid, kind, description in specs],
            "metadata": {"source": "manual synthetic experiment; no production coverage claim"}})
    sidecar = {"schemaVersion": 1, "languageCode": "pl", "experimentExtension": VERSION, "entries": entries}
    cases = []
    for category, rows in ROWS.items():
        for key, sense, context in rows:
            kind = next(s[1] for s in SPECS[key] if s[0] == sense)
            surface = key[0].upper() + key[1:] if kind == "proper_name" else key
            cases.append({"id": f"nat{len(cases)+1:03}", "beforeCursor": context,
                          "candidates": [{"surface": key, "engineScore": 650}, {"surface": "dom", "engineScore": 100}],
                          "expected": {"languageCode": "pl", "surfaceKey": key, "surface": surface},
                          "expectedSenseIds": [sense], "diagnostic": {"category": category}})
    originals = list(cases)
    keys = list(SPECS)
    for original in originals:
        probe = copy.deepcopy(original)
        key = original["expected"]["surfaceKey"]
        distractor = keys[(keys.index(key) + 2) % len(keys)]
        probe["id"] = "probe" + original["id"][3:]
        probe["candidates"] = [{"surface": distractor, "engineScore": 700}, {"surface": key, "engineScore": 650}]
        probe["diagnostic"] = {"category": "top3_probe", "sourceId": original["id"],
                               "sourceCategory": original["diagnostic"]["category"]}
        cases.append(probe)
    for key, contexts in START_CONTEXTS.items():
        for proper, context in enumerate(contexts):
            sense = SPECS[key][-1 if proper else 0][0]
            cases.append({"id": f"start{len(cases)-127:03}", "caseMode": "sentence_start", "beforeCursor": context,
                          "candidates": [{"surface": key, "engineScore": 650}, {"surface": "dom", "engineScore": 100}],
                          "expected": {"languageCode": "pl", "surfaceKey": key, "surface": key[0].upper()+key[1:]},
                          "expectedSenseIds": [sense], "diagnostic": {"category": "sentence_start"}})
    for i, key in enumerate(keys + ["warszawska"]):
        cases.append({"id": f"amb{i+1:03}", "beforeCursor": "Oto ",
                      "candidates": [{"surface": key, "engineScore": 650}, {"surface": "dom", "engineScore": 100}],
                      "diagnostic": {"category": "ambiguous"}})
    for i, key in enumerate(keys):
        source = next(c for c in originals if c["expected"]["surfaceKey"] == key)
        missing = copy.deepcopy(source)
        missing["id"] = f"missing{i+1:03}"
        missing["candidates"] = [{"surface": "dom", "engineScore": 650}, {"surface": "lód", "engineScore": 100}]
        missing["diagnostic"] = {"category": "missing_key", "sourceId": source["id"]}
        cases.append(missing)
        limited = copy.deepcopy(source)
        limited["id"] = f"limit{i+1:03}"
        distractor = keys[(keys.index(key) + 2) % len(keys)]
        limited["candidates"] = [{"surface": distractor, "engineScore": 700},
                                 {"surface": "dom", "engineScore": 680}, {"surface": key, "engineScore": 650}]
        limited["diagnostic"] = {"category": "slot_limit", "sourceId": source["id"]}
        cases.append(limited)
    return {"schemaVersion": 1, "fixtureKind": "fresh_authored_natural_continuations_with_separate_repeated_controls",
            "cases": cases}, sidecar


if __name__ == "__main__":
    from pathlib import Path
    root = Path(__file__).parent
    cases, sidecar = build()
    (root / "natural-cases.json").write_bytes(canonical_bytes(cases))
    (root / "natural-sidecar.json").write_bytes(canonical_bytes(sidecar))
