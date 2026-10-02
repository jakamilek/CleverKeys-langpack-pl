#!/usr/bin/env python3
"""Audit module surface frequency using a pinned NKJP1M frequency table.

The NKJP-derived frequency table contains one row per word-form/lemma/tag
combination. For keyboard-module retention we report:
  * total NKJP token count for the lowercase surface form;
  * NKJP count for the exact lowercase (surface, lemma) pair when a lemma can
    be inferred from the module source;
  * whether the surface was seen at all in the pinned NKJP1M snapshot;
  * wordfreq Zipf frequency as an independent secondary signal.

This script deliberately does not choose retention thresholds. It produces
auditable measurements and distribution statistics for later threshold
calibration.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from pathlib import Path

from surface_components import component_surfaces


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_nkjp(path: Path) -> tuple[dict[str, int], dict[tuple[str, str], int]]:
    by_form: dict[str, int] = {}
    by_form_lemma: dict[tuple[str, str], int] = {}
    rows = 0
    with path.open(encoding="utf-8", errors="strict") as handle:
        for line in handle:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 4:
                continue
            form, lemma, _tag = fields[:3]
            try:
                frequency = int(fields[3])
            except ValueError:
                continue
            key_form = form.strip().lower()
            key_lemma = lemma.strip().lower()
            if not key_form:
                continue
            by_form[key_form] = by_form.get(key_form, 0) + frequency
            if key_lemma:
                pair = (key_form, key_lemma)
                by_form_lemma[pair] = by_form_lemma.get(pair, 0) + frequency
            rows += 1
    if not by_form:
        raise SystemExit(f"No usable NKJP frequency rows found in {path}")
    return by_form, by_form_lemma


def load_module(path: Path, column: str) -> list[dict[str, str]]:
    if column == "__family_forms__":
        out: list[dict[str, str]] = []
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            fields = line.split("\t")
            start = 2 if path.name == "reviewed_morphology.tsv" else 1
            if len(fields) <= start:
                continue
            lemma = fields[1].strip() if path.name == "reviewed_morphology.tsv" else fields[0].strip()
            for surface in fields[start].split(";"):
                surface = surface.strip()
                if surface:
                    for component in component_surfaces(surface):
                        out.append({
                            "surface": component,
                            "lemma": lemma if len(component_surfaces(surface)) == 1 else "",
                        })
        return out

    with path.open(encoding="utf-8", newline="") as handle:
        rows = (line for line in handle if line.strip() and not line.lstrip().startswith("#"))
        reader = csv.DictReader(rows, delimiter="\t")
        if column not in (reader.fieldnames or []):
            raise SystemExit(
                f"Module source {path} has no column {column!r}; "
                f"available={reader.fieldnames}"
            )
        out = []
        for row in reader:
            value = row[column].strip()
            if value:
                components = component_surfaces(value)
                source_lemma = row.get("name", row.get("lemma", "")).strip()
                for component in components:
                    out.append({
                        "surface": component,
                        "lemma": source_lemma if len(components) == 1 else "",
                    })
        return out


def parse_module(spec: str) -> tuple[str, Path, str]:
    try:
        name, rest = spec.split("=", 1)
        path_text, column = rest.rsplit(":", 1)
    except ValueError as exc:
        raise SystemExit(
            f"Malformed --module {spec!r}; expected NAME=PATH:COLUMN"
        ) from exc
    return name, Path(path_text), column


def percentile(values: list[int], p: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    if len(values) == 1:
        return float(values[0])
    pos = (len(values) - 1) * p
    lo = int(pos)
    hi = min(lo + 1, len(values) - 1)
    frac = pos - lo
    return values[lo] * (1 - frac) + values[hi] * frac


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nkjp", type=Path, required=True)
    ap.add_argument("--module", action="append", default=[])
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    nkjp_form, nkjp_pair = load_nkjp(args.nkjp)

    try:
        from wordfreq import zipf_frequency
    except Exception as exc:
        raise SystemExit("wordfreq is required for the secondary signal") from exc

    records = []
    modules = []
    all_nkjp = []
    all_zipf = []

    for order, spec in enumerate(args.module, 1):
        name, path, column = parse_module(spec)
        entries = load_module(path, column)
        unique = {}
        for entry in entries:
            key = entry["surface"].lower()
            unique.setdefault((key, entry["lemma"].lower()), entry["surface"])

        module_records = []
        for (key, lemma_key), surface in sorted(unique.items()):
            form_count = nkjp_form.get(key, 0)
            pair_count = nkjp_pair.get((key, lemma_key), 0) if lemma_key else None
            z = float(zipf_frequency(surface, "pl"))
            row = {
                "module": name,
                "surface": surface,
                "surface_key": key,
                "lemma": lemma_key,
                "nkjp1m_surface_count": form_count,
                "nkjp1m_surface_seen": form_count > 0,
                "nkjp1m_exact_form_lemma_count": pair_count,
                "wordfreq_zipf": z,
            }
            module_records.append(row)
            records.append(row)
            if form_count > 0:
                all_nkjp.append(form_count)
            if z > 0:
                all_zipf.append(z)

        modules.append({
            "order": order,
            "module": name,
            "source": str(path),
            "column": column,
            "source_surface_records": len(entries),
            "unique_surface_lemma_pairs": len(module_records),
            "nkjp1m_seen_surfaces": sum(1 for r in module_records if r["nkjp1m_surface_seen"]),
        })

    counts = [r["nkjp1m_surface_count"] for r in records if r["nkjp1m_surface_count"] > 0]
    zipfs = [r["wordfreq_zipf"] for r in records if r["wordfreq_zipf"] > 0]

    result = {
        "source": {
            "type": "NKJP1M tagged frequency table",
            "pinned_revision": "be02836cf3aa0286ad8961d2e4528cdc2f72d044",
            "retrieval_url": "https://git.nlp.ipipan.waw.pl/wojciech.jaworski/ENIAM/repository/archive.tar.gz?ref=be02836cf3aa0286ad8961d2e4528cdc2f72d044&path=resources%2FNKJP1M",
            "pinned_file_path": "resources/NKJP1M/NKJP1M-tagged-frequency.tab",
            "acquisition_method": "legacy GitLab repository archive",
            "sha256": sha256(args.nkjp),
            "scope": "manually annotated 1-million-word NKJP subcorpus",
            "note": "This is an NKJP-derived frequency snapshot, not the full 1.5B-word searchable corpus.",
        },
        "modules": modules,
        "distribution": {
            "nkjp1m_surface_counts_nonzero": len(counts),
            "nkjp1m_surface_zero_count": sum(1 for r in records if r["nkjp1m_surface_count"] == 0),
            "nkjp1m_surface_count_percentiles": {
                "p10": percentile(counts, 0.10),
                "p25": percentile(counts, 0.25),
                "p50": percentile(counts, 0.50),
                "p75": percentile(counts, 0.75),
                "p90": percentile(counts, 0.90),
                "p95": percentile(counts, 0.95),
            },
            "wordfreq_zipf_nonzero": len(zipfs),
            "wordfreq_zipf_zero_count": sum(1 for r in records if r["wordfreq_zipf"] == 0),
            "wordfreq_zipf_percentiles": {
                "p10": percentile([int(round(v * 1000)) for v in zipfs], 0.10) / 1000 if zipfs else None,
                "p25": percentile([int(round(v * 1000)) for v in zipfs], 0.25) / 1000 if zipfs else None,
                "p50": percentile([int(round(v * 1000)) for v in zipfs], 0.50) / 1000 if zipfs else None,
                "p75": percentile([int(round(v * 1000)) for v in zipfs], 0.75) / 1000 if zipfs else None,
                "p90": percentile([int(round(v * 1000)) for v in zipfs], 0.90) / 1000 if zipfs else None,
                "p95": percentile([int(round(v * 1000)) for v in zipfs], 0.95) / 1000 if zipfs else None,
            },
        },
        "policy": {
            "nkjp_is_primary_frequency_signal": True,
            "wordfreq_is_secondary_frequency_signal": True,
            "retention_thresholds_status": "not_yet_set",
            "reason": "Thresholds will be calibrated from the observed module-form distribution and keyboard utility, not imposed before measurement.",
        },
        "records": records,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["distribution"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
