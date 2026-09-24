#!/usr/bin/env python3
"""Fetch the current official GUS TERYT SIMC archive without authentication.

The TERYT public download endpoint is a WebForms application. The exact
download flow is the same public flow documented by GUS: select a reference
date and request the SIMC official full file. The resulting ZIP is stored with
an SHA256 and a provenance JSON record.

This script does not use a third-party mirror as the language-data source.
"""
from __future__ import annotations

import argparse
import hashlib
import json
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
    5: "maja", 6: "czerwca", 7: "sierpnia", 8: "sierpnia",
    9: "września", 10: "października", 11: "listopada", 12: "grudnia",
}
# Corrected month table kept explicit to make the request string auditable.
MONTHS[6] = "czerwca"


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-date", default=str(date.today()))
    ap.add_argument("--out-zip", type=Path, required=True)
    ap.add_argument("--out-sha256", type=Path, required=True)
    ap.add_argument("--out-provenance", type=Path, required=True)
    return ap.parse_args()


def pl_date(iso_date: str) -> str:
    y, m, d = map(int, iso_date.split("-"))
    return f"{d} {MONTHS[m]} {y}"


def download(session: requests.Session, state_date: str) -> bytes:
    form = {
        "__EVENTTARGET": "ctl00$body$BSIMCUrzedowyPobierz",
        "ctl00$body$TBData": pl_date(state_date),
    }
    response = session.post(DOWNLOAD_URL, data=form, timeout=180)
    response.raise_for_status()
    body = response.content

    if body.startswith(b"PK"):
        return body

    # The public site can require a generation request before returning ZIP bytes.
    if b"body_BSIMCUrzedowyGeneruj" in body:
        form = {
            "__EVENTTARGET": "ctl00$body$BSIMCUrzedowyGeneruj",
            "ctl00$body$TBData": pl_date(state_date),
        }
        response = session.post(DOWNLOAD_URL, data=form, timeout=180)
        response.raise_for_status()
        body = response.content
        if body.startswith(b"PK"):
            return body

    preview = body[:1200].decode("utf-8", errors="replace")
    raise RuntimeError(
        "GUS TERYT SIMC endpoint did not return a ZIP archive. "
        f"Response preview: {preview!r}"
    )


def main() -> int:
    args = parse_args()
    args.out_zip.parent.mkdir(parents=True, exist_ok=True)
    args.out_sha256.parent.mkdir(parents=True, exist_ok=True)
    args.out_provenance.parent.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "CleverKeys-langpack-pl/TERYT-audit",
        "Accept": "*/*",
    })

    data = download(session, args.state_date)
    digest = hashlib.sha256(data).hexdigest()
    args.out_zip.write_bytes(data)
    args.out_sha256.write_text(digest + "\n", encoding="utf-8")

    provenance = {
        "source": "GUS TERYT / SIMC",
        "source_url": DOWNLOAD_URL,
        "state_date_requested": args.state_date,
        "state_date_form": pl_date(args.state_date),
        "archive_sha256": digest,
        "selection_rule": "RM == 96 (miasto)",
        "official_catalog_note": (
            "SIMC current catalog state follows the official GUS catalog; "
            "the catalog currently published for 2026 begins 2026-01-01."
        ),
    }
    args.out_provenance.write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(provenance, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
