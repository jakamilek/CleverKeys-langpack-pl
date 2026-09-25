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


def _attrs(tag: str) -> dict[str, str]:
    attrs: dict[str, str] = {}
    for match in re.finditer(r"""([\w:-]+)\s*=\s*["']([^"']*)["']""", tag):
        attrs[match.group(1).lower()] = html.unescape(match.group(2))
    return attrs


class FormCollector(html_parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.forms: list[dict] = []
        self.current: dict | None = None
        self.select: dict | None = None
        self.option: dict | None = None
        self.textarea: dict | None = None

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {k.lower(): (v or "") for k, v in attrs_list}
        if tag.lower() == "form":
            self.current = {
                "attrs": attrs,
                "fields": [],
                "controls": [],
                "textareas": [],
            }
            self.forms.append(self.current)
            return
        if self.current is None:
            return
        if tag.lower() == "input":
            typ = attrs.get("type", "text").lower()
            field = {"name": attrs.get("name", ""), "value": attrs.get("value", ""),
                     "type": typ, "checked": "checked" in attrs}
            self.current["fields"].append(field)
            self.current["controls"].append(field)
        elif tag.lower() == "select":
            self.select = {"name": attrs.get("name", ""), "value": None}
        elif tag.lower() == "option" and self.select is not None:
            self.option = {
                "value": attrs.get("value", ""),
                "selected": "selected" in attrs,
                "text": "",
            }
        elif tag.lower() == "textarea":
            self.textarea = {"name": attrs.get("name", ""), "text": ""}

    def handle_data(self, data: str) -> None:
        if self.option is not None:
            self.option["text"] += data
        elif self.textarea is not None:
            self.textarea["text"] += data

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "option" and self.select is not None and self.option is not None:
            if self.option["selected"] or self.select["value"] is None:
                self.select["value"] = self.option["value"] or self.option["text"].strip()
            self.option = None
        elif tag == "select" and self.select is not None:
            if self.select["name"]:
                self.current["fields"].append({
                    "name": self.select["name"],
                    "value": self.select["value"] or "",
                    "type": "select",
                    "checked": False,
                })
            self.select = None
        elif tag == "textarea" and self.textarea is not None:
            if self.textarea["name"]:
                self.current["fields"].append({
                    "name": self.textarea["name"],
                    "value": self.textarea["text"],
                    "type": "textarea",
                    "checked": False,
                })
            self.textarea = None
        elif tag == "form":
            self.current = None


def _choose_form(page: str, marker: str) -> dict:
    parser = FormCollector()
    parser.feed(page)
    if not parser.forms:
        raise RuntimeError("Official GUS page contained no HTML forms")
    candidates = []
    for form in parser.forms:
        controls = form["controls"]
        combos = []
        for item in controls:
            combos.append(f'{item.get("name","")} {item.get("value","")}'.lower())
        score = sum(1 for combo in combos if marker.lower() in combo)
        if score:
            candidates.append((score, form))
    if not candidates:
        raise RuntimeError(
            "Could not find the TERC form in the official GUS page. "
            f"Forms={len(parser.forms)}"
        )
    return max(candidates, key=lambda x: x[0])[1]


def _form_payload(form: dict, state_date: str, clicked: dict[str, str]) -> dict[str, str]:
    payload: dict[str, str] = {}
    for field in form["fields"]:
        name = field.get("name", "")
        if not name:
            continue
        typ = field.get("type", "text")
        if typ in {"submit", "button", "image", "reset"}:
            continue
        if typ in {"checkbox", "radio"} and not field.get("checked"):
            continue
        payload[name] = field.get("value", "")
    date_name = ""
    for field in form["fields"]:
        combo = f'{field.get("name","")} {field.get("value","")}'.lower()
        if "tbdata" in combo or ("data" in combo and field.get("type") in {"text", "date"}):
            date_name = field.get("name", "")
            break
    if date_name:
        payload[date_name] = pl_date(state_date)
    if clicked["kind"] == "submit":
        payload[clicked["name"]] = clicked.get("value", "")
    else:
        payload["__EVENTTARGET"] = clicked["target"]
        payload["__EVENTARGUMENT"] = ""
    return payload


def _post_control(session: requests.Session, form: dict, clicked: dict[str, str], state_date: str):
    action = form["attrs"].get("action") or DOWNLOAD_URL
    action = requests.compat.urljoin(DOWNLOAD_URL, action)
    payload = _form_payload(form, state_date, clicked)
    return session.post(
        action,
        data=payload,
        timeout=180,
        headers={"Referer": DOWNLOAD_URL},
    )


def _zip_from_response(session: requests.Session, response: requests.Response) -> bytes | None:
    body = response.content
    if body.startswith(b"PK"):
        return body
    page = body.decode("utf-8", errors="replace")
    hrefs = re.findall(
        r"""(?:href|src|action)=["']([^"']+)["']""",
        page,
        flags=re.IGNORECASE,
    )
    hrefs += re.findall(
        r"""(?:window\.open|location(?:\.href)?|window\.location)\s*\(?.*?["']([^"']+\.zip(?:\?[^"']*)?)["']""",
        page,
        flags=re.IGNORECASE,
    )
    for href in hrefs:
        if ".zip" not in href.lower():
            continue
        absolute = requests.compat.urljoin(DOWNLOAD_URL, html.unescape(href))
        candidate = session.get(absolute, timeout=180, headers={"Referer": DOWNLOAD_URL})
        candidate.raise_for_status()
        if candidate.content.startswith(b"PK"):
            return candidate.content
    return None


def download(session: requests.Session, state_date: str) -> tuple[bytes, dict[str, str]]:
    initial = session.get(DOWNLOAD_URL, timeout=180)
    initial.raise_for_status()
    page = initial.text
    form = _choose_form(page, "TERC")

    controls = []
    for item in form["controls"]:
        combo = f'{item.get("name","")} {item.get("value","")}'.lower()
        if "terc" not in combo:
            continue
        if "pobierz" not in combo and "download" not in combo and "generuj" not in combo:
            continue
        if item.get("type") in {"submit", "button"}:
            controls.append({
                "kind": "submit",
                "name": item.get("name", ""),
                "value": item.get("value", ""),
                "combo": combo,
            })

    if not controls:
        raise RuntimeError("No TERC download control discovered in the official GUS form")

    preferred = sorted(
        controls,
        key=lambda c: (
            0 if "urzedowy" in c["combo"] else 1,
            0 if "pobierz" in c["combo"] else 1,
            0 if "terc" in c["combo"] else 1,
        ),
    )
    attempts = []
    for control in preferred:
        response = _post_control(session, form, control, state_date)
        response.raise_for_status()
        data = _zip_from_response(session, response)
        attempts.append(control["name"])
        if data is not None:
            return data, {
                "method": "full-form-submit",
                "control": control["name"],
                "attempted_controls": ",".join(attempts),
                "form_action": form["attrs"].get("action", ""),
            }

    # Expose enough diagnostic state to make the next failure actionable without
    # dumping the full HTML response into the CI log.
    field_names = [
        field.get("name", "")
        for field in form["fields"]
        if field.get("name")
    ]
    raise RuntimeError(
        "Official GUS TERC form returned HTML instead of ZIP for all controls. "
        f"Tried={attempts}; form_fields={field_names[:80]}"
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
