#!/usr/bin/env python3
"""Fetch the current official GUS TERYT TERC archive without authentication."""
from __future__ import annotations

import argparse
import hashlib
import json
import html
import re
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


def _attrs(tag: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for match in re.finditer(r"""([\w:-]+)\s*=\s*["']([^"']*)["']""", tag):
        attrs[match.group(1).lower()] = html.unescape(match.group(2))
    return attrs


def _form_fields(page: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for tag in re.findall(r"<input\b[^>]*>", page, flags=re.IGNORECASE):
        attrs = _attrs(tag)
        name = attrs.get("name")
        if not name:
            continue
        input_type = attrs.get("type", "text").lower()
        if input_type == "hidden":
            fields[name] = attrs.get("value", "")
    return fields


def _controls(page: str) -> list[dict[str, str]]:
    controls: list[dict[str, str]] = []
    for tag in re.findall(r"<input\b[^>]*>", page, flags=re.IGNORECASE):
        attrs = _attrs(tag)
        name = attrs.get("name", "")
        value = attrs.get("value", "")
        combo = f"{name} {attrs.get('id', '')} {value}".lower()
        if name and attrs.get("type", "").lower() in {"submit", "button"}:
            controls.append({"kind": "submit", "name": name, "value": value, "combo": combo})
    for match in re.finditer(
        r"<a\b[^>]*href=[\"']([^\"']*__doPostBack\([^)]*\)[^\"']*)[\"'][^>]*>(.*?)</a>",
        page,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        href = html.unescape(match.group(1))
        text_value = re.sub(r"<[^>]+>", " ", match.group(2))
        combo = f"{href} {text_value}".lower()
        m = re.search(r"__doPostBack\(\s*['\"]([^'\"]+)['\"]", href, flags=re.IGNORECASE)
        if m:
            controls.append({"kind": "eventtarget", "target": m.group(1), "value": text_value.strip(), "combo": combo})
    return controls


def _find_date_field(page: str) -> str:
    for tag in re.findall(r"<input\b[^>]*>", page, flags=re.IGNORECASE):
        attrs = _attrs(tag)
        name = attrs.get("name", "")
        combo = f"{name} {attrs.get('id', '')} {attrs.get('value', '')}".lower()
        if "tbdata" in combo or ("data" in combo and attrs.get("type", "").lower() in {"text", "date"}):
            return name
    return "ctl00$body$TBData"


def _post_control(session: requests.Session, page: str, control: dict[str, str], state_date: str):
    data = _form_fields(page)
    data[_find_date_field(page)] = pl_date(state_date)
    if control["kind"] == "eventtarget":
        data["__EVENTTARGET"] = control["target"]
    else:
        data[control["name"]] = control["value"]
    return session.post(DOWNLOAD_URL, data=data, timeout=180)


def _zip_from_response(session: requests.Session, response: requests.Response) -> bytes | None:
    body = response.content
    if body.startswith(b"PK"):
        return body
    page = body.decode("utf-8", errors="replace")
    for href in re.findall(r"""(?:href|src)=["']([^"']+\.zip(?:\?[^"']*)?)["']""", page, flags=re.IGNORECASE):
        absolute = requests.compat.urljoin(DOWNLOAD_URL, html.unescape(href))
        candidate = session.get(absolute, timeout=180)
        candidate.raise_for_status()
        if candidate.content.startswith(b"PK"):
            return candidate.content
    return None


def download(session: requests.Session, state_date: str) -> tuple[bytes, dict[str, str]]:
    initial = session.get(DOWNLOAD_URL, timeout=180)
    initial.raise_for_status()
    page = initial.text

    controls = _controls(page)
    terc_controls = [
        c for c in controls
        if "terc" in c["combo"]
        and ("pobierz" in c["combo"] or "download" in c["combo"] or "generuj" in c["combo"])
    ]
    if not terc_controls:
        raise RuntimeError(
            "Could not discover a TERC download/generate control on the official GUS form. "
            f"Discovered controls: {[c.get('name', c.get('target', '')) for c in controls if 'teryt' in c.get('combo', '')][:30]}"
        )

    preferred = sorted(
        terc_controls,
        key=lambda c: (
            0 if "pobierz" in c["combo"] else 1,
            0 if "podstaw" in c["combo"] else 1,
            0 if "terc" in c["combo"] else 1,
        ),
    )

    attempts = []
    for control in preferred:
        response = _post_control(session, page, control, state_date)
        response.raise_for_status()
        data = _zip_from_response(session, response)
        attempts.append(control.get("name", control.get("target", "")))
        if data is not None:
            return data, {
                "method": control["kind"],
                "control": control.get("name", control.get("target", "")),
                "attempted_controls": ",".join(attempts),
            }

    raise RuntimeError(
        "Official GUS TERC form returned HTML instead of ZIP for all discovered TERC controls. "
        f"Tried: {attempts}"
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
