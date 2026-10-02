#!/usr/bin/env python3
"""Fetch the official KSNG/GUGiK 2025 country/capital list and 2026 update."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import requests

MAIN_URL = "https://www.gov.pl/attachment/128fd818-7fb0-4528-8d6f-eb59fa53c395"
UPDATE_URL = "https://www.gov.pl/attachment/80df1b7d-dbe5-45c6-ba56-6d43177355fb"

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-main", type=Path, required=True)
    ap.add_argument("--out-main-sha256", type=Path, required=True)
    ap.add_argument("--out-update", type=Path, required=True)
    ap.add_argument("--out-update-sha256", type=Path, required=True)
    ap.add_argument("--out-provenance", type=Path, required=True)
    return ap.parse_args()

def fetch(session: requests.Session, url: str) -> bytes:
    r = session.get(url, timeout=180)
    r.raise_for_status()
    data = r.content
    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"Official KSNG endpoint did not return PDF: {url}")
    return data

def main() -> int:
    args = parse_args()
    for p in (args.out_main, args.out_main_sha256, args.out_update,
              args.out_update_sha256, args.out_provenance):
        p.parent.mkdir(parents=True, exist_ok=True)
    s = requests.Session()
    s.headers.update({"User-Agent": "CleverKeys-langpack-pl/KSNG-audit",
                      "Accept": "application/pdf,*/*"})
    main_pdf = fetch(s, MAIN_URL)
    update_pdf = fetch(s, UPDATE_URL)
    main_sha = hashlib.sha256(main_pdf).hexdigest()
    update_sha = hashlib.sha256(update_pdf).hexdigest()
    args.out_main.write_bytes(main_pdf)
    args.out_update.write_bytes(update_pdf)
    args.out_main_sha256.write_text(main_sha + "\n", encoding="utf-8")
    args.out_update_sha256.write_text(update_sha + "\n", encoding="utf-8")
    provenance = {
        "source": "KSNG / GUGiK",
        "main": {"edition": "Wydanie VIII zaktualizowane, Warszawa 2025",
                 "url": MAIN_URL, "sha256": main_sha},
        "update_1_2026": {"url": UPDATE_URL, "sha256": update_sha,
                          "scope": "Gwinea Równikowa: stolica Ciudad de la Paz"},
        "selection_scope": "197 states recognized by Poland; primary capitals in Part I",
    }
    args.out_provenance.write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(provenance, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
