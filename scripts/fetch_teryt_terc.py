#!/usr/bin/env python3
"""Fetch the current official GUS TERYT TERC archive without authentication."""
from __future__ import annotations

import argparse
import hashlib
import json
import html
import re
from html import parser as html_parser
from datetime import date
from pathlib import Path

import requests

DOWNLOAD_URL = (
    "https://eteryt.stat.gov.pl/eTeryt/rejestr_teryt/"
    "udostepnianie_danych/baza_teryt/uzytkownicy_indywidualni/"
    "pobieranie/pliki_pelne.aspx"
)

MONTHS = {
    1: "stycznia", 2: "lutego", 3: "marca", 4: "kwietnia",
    5: "maja", 6: "czerwca", 7: "lipca", 8: "sierpnia",
    9: "września", 10: "października", 11: "listopada", 12: "grudnia",
}


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



def _postback(session: requests.Session, event_target: str, state_date: str) -> requests.Response:
    """Use the documented GUS WebForms postback controls for the TERC full file."""
    response = session.post(
        DOWNLOAD_URL,
        data={
            "__EVENTTARGET": event_target,
            "ctl00$body$TBData": pl_date(state_date),
        },
        timeout=180,
        headers={"Referer": DOWNLOAD_URL},
    )
    response.raise_for_status()
    return response


def _extract_zip_link(session: requests.Session, response: requests.Response) -> bytes | None:
    body = response.content
    if body.startswith(b"PK"):
        return body
    page = body.decode("utf-8", errors="replace")
    hrefs = re.findall(r"""(?:href|src)=["']([^"']+\.zip(?:\?[^"']*)?)["']""", page, flags=re.IGNORECASE)
    for href in hrefs:
        absolute = requests.compat.urljoin(DOWNLOAD_URL, html.unescape(href))
        candidate = session.get(absolute, timeout=180, headers={"Referer": DOWNLOAD_URL})
        candidate.raise_for_status()
        if candidate.content.startswith(b"PK"):
            return candidate.content
    return None


def download(session: requests.Session, state_date: str) -> tuple[bytes, dict[str, str]]:
    attempts: list[str] = []
    for event_target in ("ctl00$body$BTERCPobierz", "ctl00$body$BTERCGeneruj"):
        attempts.append(event_target)
        response = _postback(session, event_target, state_date)
        data = _extract_zip_link(session, response)
        if data is not None:
            return data, {
                "method": "documented-gus-webforms-postback",
                "control": event_target,
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
        "selection_rule": "three-level territorial division: voivodeships, powiats and gminas",
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
