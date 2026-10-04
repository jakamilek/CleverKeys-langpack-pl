"""Construct and freeze a controlled diagnostic suite, not a user benchmark."""
import json
from pathlib import Path

from prototype import canonical_bytes, prepare

ROOT = Path(__file__).parent
SPECS = [
    ("łódź", "Łódź", "Fotografia przedstawia polskie miasto znane z fabryk i przemysłu włókienniczego.",
     "Fotografia przedstawia niewielką drewnianą jednostkę pływającą po jeziorze.",
     "Dużym polskim miastem przemysłowym jest ", "Do brzegu przybiła niewielka drewniana "),
    ("malina", "Malina", "Portret przedstawia nauczycielkę. Podpis podaje wyłącznie jej nazwisko.",
     "Fotografia przedstawia czerwony owoc zerwany z krzewu w ogrodzie.",
     "Nowa nauczycielka nosi nazwisko ", "Na krzaku dojrzała czerwona "),
    ("jagoda", "Jagoda", "Portret przedstawia dziewczynę. Podpis podaje wyłącznie jej imię.",
     "Fotografia przedstawia mały ciemny owoc znaleziony w lesie.",
     "Nowa uczennica ma na imię ", "W koszyku została jedna leśna "),
    ("róża", "Róża", "Portret przedstawia kobietę. Podpis podaje wyłącznie jej imię.",
     "Fotografia przedstawia kwiat z kolcami i czerwonymi płatkami.",
     "Nowa lekarka ma na imię ", "W ogrodzie rozkwitła czerwona "),
]
TAIL = "Na zdjęciu widoczna jest "
FILLER = ("Album ma szarą okładkę. Kartki są ponumerowane. "
          "Oglądamy je po kolei i zapisujemy krótkie uwagi w notesie. "
          "Na stole leży ołówek, obok niego mała kartka papieru. ")


def build():
    cases, entries = [], []
    index = 0
    for lower, upper, proper_hint, common_hint, proper_direct, common_direct in SPECS:
        entries.append({"surfaceKey": lower, "commonNoun": True, "properName": True,
                        "capitalization": {"defaultSurface": lower, "variants": [
                            {"surface": lower, "casePolicy": "lowercase"},
                            {"surface": upper, "casePolicy": "capitalized"}]},
                        "metadata": {"source": "constructed diagnostic fixture; no production audit"}})
        for category in ("direct", "previous", "distant_retained", "conflicting", "context_lost"):
            for proper in (True, False):
                hint, opposite = (proper_hint, common_hint) if proper else (common_hint, proper_hint)
                if category == "direct":
                    context = proper_direct if proper else common_direct
                elif category == "previous":
                    context = hint + " " + TAIL
                elif category == "distant_retained":
                    context = hint + " " + FILLER + TAIL
                elif category == "conflicting":
                    context = "Poprzedni opis: " + opposite + " Nowy, aktualny opis: " + hint + " " + TAIL
                else:
                    context = hint + " " + FILLER * 3 + TAIL
                index += 1
                cases.append({"id": f"diag{index:03}", "beforeCursor": context,
                              "candidates": [{"surface": lower, "engineScore": 650},
                                             {"surface": "dom", "engineScore": 100}],
                              "expected": {"languageCode": "pl", "surfaceKey": lower,
                                           "surface": upper if proper else lower},
                              "diagnostic": {"category": category,
                                             "pairId": f"{lower}/{category}"}})
        for category, context in (("ambiguous", TAIL), ("ambiguous_short", "Oto ")):
            index += 1
            cases.append({"id": f"diag{index:03}", "beforeCursor": context,
                          "candidates": [{"surface": lower, "engineScore": 650},
                                         {"surface": "dom", "engineScore": 100}],
                          "diagnostic": {"category": category, "pairId": None}})
    document = {"schemaVersion": 1,
                "fixtureKind": "constructed_controlled_diagnostic_not_independent_quality_benchmark",
                "cases": cases}
    sidecar = {"schemaVersion": 1, "languageCode": "pl", "entries": entries}
    return document, sidecar


if __name__ == "__main__":
    cases, sidecar = build()
    (ROOT / "diagnostic-cases.json").write_bytes(canonical_bytes(cases))
    (ROOT / "diagnostic-sidecar.json").write_bytes(canonical_bytes(sidecar))
    (ROOT / "diagnostic-requests.json").write_bytes(canonical_bytes(prepare(cases, sidecar)))
