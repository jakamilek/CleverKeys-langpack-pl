#!/usr/bin/env python3
"""Fetch the official GUS TERYT TERC full-file archive without authentication."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urljoin

import requests

DOWNLOAD_URL = (
    "https://eteryt.stat.gov.pl/eTeryt/rejestr_teryt/"
    "udostepnianie_danych/baza_teryt/uzytkownicy_indywidualni/"
    "pobieranie/pliki_pelne.aspx"
)

MONTHS = {
    1: "stycznia",
    2: "lutego",
    3: "marca",
    4: "kwietnia",
    5: "maja",
    6: "czerwca",
    7: "lipca",
    8: "sierpnia",
    9: "września",
    10: "października",
    11: "listopada",
    12: "grudnia",
}

TERC_CONTROL = "ctl00$body$BTERC"
TERC_ARCHIVED_NAME = "TERC_Urzedowy"


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-date", default="2026-01-01")
    ap.add_argument("--out-zip", type=Path, required=True)
    ap.add_argument("--out-sha256", type=Path, required=True)
    ap.add_argument("--out-provenance", type=Path, required=True)
    return ap.parse_args()


def pl_date(iso_date: str) -> str:
    y, m, d = map(int, iso_date.split("-"))
    return f"{d} {MONTHS[m]} {y}"


def _postback(
    session: requests.Session,
    event_target: str,
    state_date: str,
    *,
    archived_name: str | None = None,
) -> requests.Response:
    """Submit the same WebForms fields used by the public GUS download page."""
    data = {
        "__EVENTTARGET": event_target,
        "ctl00$body$TBData": pl_date(state_date),
    }
    if archived_name is not None:
        data["archived_name"] = archived_name

    response = session.post(
        DOWNLOAD_URL,
        data=data,
        timeout=180,
        headers={"Referer": DOWNLOAD_URL},
    )
    response.raise_for_status()
    return response


def _response_zip(response: requests.Response) -> bytes | None:
    """Return ZIP bytes from a direct response, if present."""
    body = response.content
    if body.startswith(b"PK"):
        return body
    return None


def _extract_zip_link(
    session: requests.Session,
    response: requests.Response,
) -> bytes | None:
    """Follow a ZIP link emitted by the GUS page, if the postback returns HTML."""
    page = response.content.decode(response.encoding or "utf-8", errors="replace")
    hrefs = re.findall(
        r"""(?:href|src)=[\"']([^\"']+\.zip(?:\?[^\"']*)?)[\"']""",
        page,
        flags=re.IGNORECASE,
    )
    for href in hrefs:
        absolute = urljoin(DOWNLOAD_URL, html.unescape(href))
        candidate = session.get(
            absolute,
            timeout=180,
            headers={"Referer": DOWNLOAD_URL},
        )
        candidate.raise_for_status()
        if candidate.content.startswith(b"PK"):
            return candidate.content
    return None


def _fetch_once(
    session: requests.Session,
    event_target: str,
    state_date: str,
    *,
    archived_name: str | None = None,
) -> bytes | None:
    response = _postback(
        session,
        event_target,
        state_date,
        archived_name=archived_name,
    )
    return _response_zip(response) or _extract_zip_link(session, response)


def download(
    session: requests.Session,
    state_date: str,
) -> tuple[bytes, dict[str, str]]:
    attempts: list[str] = []

    # GUS first asks for the TERC file and, when it is not already generated,
    # returns the Generuj control. The latter must carry archived_name=TERC_Urzedowy.
    direct_control = f"{TERC_CONTROL}Pobierz"
    generate_control = f"{TERC_CONTROL}Generuj"

    attempts.append(direct_control)
    data = _fetch_once(session, direct_control, state_date)
    if data is not None:
        return data, {
            "method": "gus-webforms-postback",
            "control": direct_control,
            "state_date": state_date,
        }

    attempts.append(generate_control)
    data = _fetch_once(
        session,
        generate_control,
        state_date,
        archived_name=TERC_ARCHIVED_NAME,
    )
    if data is not None:
        return data, {
            "method": "gus-webforms-postback",
            "control": generate_control,
            "archived_name": TERC_ARCHIVED_NAME,
            "attempted_controls": ",".join(attempts),
            "state_date": state_date,
        }

    raise RuntimeError(
        "Official GUS TERC full-file postback did not return a ZIP archive. "
        f"Tried={attempts}"
    )


def main() -> int:
    args = parse_args()
    for p in (args.out_zip, args.out_sha256, args.out_provenance):
        p.parent.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "CleverKeys-langpack-pl/TERC-audit",
        "Accept": "*/*",
    })

    data, acquisition = download(session, args.state_date)
    digest = hashlib.sha256(data).hexdigest()
    args.out_zip.write_bytes(data)
    args.out_sha256.write_text(digest + "\n", encoding="utf-8")

    provenance = {
        "source": "GUS TERYT / TERC",
        "source_url": DOWNLOAD_URL,
        "state_date_requested": args.state_date,
        "state_date_form": pl_date(args.state_date),
        "archive_sha256": digest,
        "selection_rule": (
            "three-level territorial division: "
            "voivodeships, powiats and gminas"
        ),
        "acquisition": acquisition,
        "expected_current_state": {
            "voivodeships": 16,
            "powiats": 380,
            "gminas": 2479,
            "total": 2875,
        },
    }
    args.out_provenance.write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(provenance, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
