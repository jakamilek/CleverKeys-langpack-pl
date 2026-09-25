#!/usr/bin/env python3
"""
Build a report-only/preview Polish word list for CleverKeys.

The script combines:
  * wordfreq Polish ranking (candidate universe)
  * AOSP LatinIME Polish headwords (mobile-keyboard evidence)
  * Hunspell pl_PL acceptance (Polish spelling/inflection evidence)
  * edit-distance-1 typo detection against high-frequency known-good forms
  * foreign-language dominance filtering
  * Polish diacritic-alias suppression when the accented canonical form is
    positively evidenced

It does NOT modify source/ and does NOT promote any source.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path

POLISH_ALPHABET = set("aąbcćdeęfghijklłmnńoóprsśtuwyzźż")
WORD_RE = re.compile(r"^[a-ząćęłńóśźż]+$", re.IGNORECASE)
DIACRITICS = set("ąęćłńóśźż")
EXPECTED_WORDFREQ_COMMIT = "912caf64b657478d1dff1138efdc078947d54bb1"


def normalize_accents(word: str) -> str:
    special = {"ł": "l", "Ł": "l"}
    value = word.lower()
    for src, dst in special.items():
        value = value.replace(src, dst)
    value = unicodedata.normalize("NFD", value)
    return "".join(c for c in value if unicodedata.category(c) != "Mn")


def is_candidate(word: str) -> bool:
    return (
        1 <= len(word) <= 25
        and word.isalpha()
        and WORD_RE.fullmatch(word) is not None
        and all(ch.lower() in POLISH_ALPHABET for ch in word)
    )


def load_aosp(path: Path) -> set[str]:
    out: set[str] = set()
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            match = re.search(r"(?:^|[\t ,])word=([^\t ,]+)", line)
            if not match:
                continue
            word = match.group(1).strip().strip('"').lower()
            if is_candidate(word):
                out.add(word)
    return out


def hunspell_accepts(words: list[str]) -> set[str]:
    binary = shutil.which("hunspell")
    if not binary:
        raise SystemExit("hunspell is required but was not found")
    proc = subprocess.run(
        [binary, "-d", "pl_PL", "-G", "-i", "UTF-8"],
        input="\n".join(words) + "\n",
        text=True,
        capture_output=True,
        timeout=900,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(
            f"hunspell failed with exit {proc.returncode}: {proc.stderr[-1000:]}"
        )
    return {
        line.strip().lower()
        for line in proc.stdout.splitlines()
        if is_candidate(line.strip().lower())
    }


def edit_distance_leq_one(a: str, b: str) -> bool:
    if a == b:
        return False
    if abs(len(a) - len(b)) > 1:
        return False

    if len(a) == len(b):
        mismatches = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        if len(mismatches) == 1:
            return True
        if len(mismatches) == 2:
            i, j = mismatches
            return j == i + 1 and a[i] == b[j] and a[j] == b[i]
        return False

    if len(a) > len(b):
        a, b = b, a
    # a is shorter by one
    i = j = 0
    mismatches = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            i += 1
            j += 1
        else:
            mismatches += 1
            j += 1
            if mismatches > 1:
                return False
    return True


def build_delete_index(words: set[str]) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}
    for word in words:
        for i in range(len(word)):
            key = word[:i] + word[i + 1 :]
            index.setdefault(key, set()).add(word)
    return index


def typo_matches(
    candidates: list[str],
    known_good: set[str],
    zipf: dict[str, float],
) -> dict[str, tuple[str, str, float]]:
    index = build_delete_index(known_good)
    result: dict[str, tuple[str, str, float]] = {}
    for word in candidates:
        if len(word) < 3 or word in known_good:
            continue
        if zipf[word] >= 3.5:
            continue
        nearby: set[str] = set()
        for i in range(len(word)):
            key = word[:i] + word[i + 1 :]
            nearby.update(index.get(key, set()))
        best: tuple[str, str, float] | None = None
        for other in nearby:
            if not edit_distance_leq_one(word, other):
                continue
            gap = zipf.get(other, 0.0) - zipf[word]
            if gap <= 0:
                continue
            if len(word) == 3:
                threshold = 3.0
            elif len(word) <= 5:
                threshold = 2.5
            else:
                threshold = 2.0
            if gap >= threshold and (best is None or gap > best[2]):
                # Classify the edit for review.
                if len(word) == len(other):
                    diffs = [i for i, (x, y) in enumerate(zip(word, other)) if x != y]
                    if len(diffs) == 2 and diffs[1] == diffs[0] + 1 and word[diffs[0]] == other[diffs[1]]:
                        rule = "transposition"
                    else:
                        rule = "substitution"
                elif len(word) > len(other):
                    rule = "deletion"
                else:
                    rule = "insertion"
                best = (other, rule, gap)
        if best:
            result[word] = best
    return result


def load_blocked_errors(path: Path) -> tuple[set[str], list[dict[str, str]]]:
    blocked: set[str] = set()
    rows: list[dict[str, str]] = []
    if not path.exists():
        return blocked, rows
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            raise SystemExit(f"Malformed autocorrect row {path}:{line_no}")
        wrong, canonical, error_class = parts[:3]
        blocked.add(wrong.strip().lower())
        rows.append({
            "wrong": wrong.strip().lower(),
            "canonical": canonical.strip(),
            "error_class": error_class.strip(),
        })
    return blocked, rows



def load_custom_words(
    path: Path,
) -> tuple[set[str], dict[str, str], dict[str, str]]:
    """Load explicit hand-reviewed dictionary surfaces with an explicit casing policy."""
    forms: set[str] = set()
    surface_map: dict[str, str] = {}
    case_policy_map: dict[str, str] = {}
    if not path.exists():
        return forms, surface_map, case_policy_map
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        expected_fields = {"surface", "case_policy", "basis", "source"}
        if set(reader.fieldnames or ()) != expected_fields:
            raise SystemExit(
                f"Malformed custom category header {path}: expected {sorted(expected_fields)}"
            )
        for line_no, row in enumerate(reader, 2):
            surface = row["surface"].strip()
            policy = row["case_policy"].strip()
            if not surface or policy not in {"lowercase", "capitalized"}:
                raise SystemExit(f"Malformed custom category row {path}:{line_no}")
            if not is_inflection_surface(surface):
                raise SystemExit(
                    f"Invalid custom category surface {path}:{line_no}: {surface!r}"
                )
            lower = surface.lower()
            prior = surface_map.get(lower)
            if prior is not None and prior != surface:
                raise SystemExit(
                    f"Conflicting custom category surface {path}:{line_no}: "
                    f"{prior!r} vs {surface!r}"
                )
            prior_policy = case_policy_map.get(lower)
            if prior_policy is not None and prior_policy != policy:
                raise SystemExit(
                    f"Conflicting custom category case policy {path}:{line_no}: "
                    f"{prior_policy!r} vs {policy!r}"
                )
            forms.add(lower)
            surface_map[lower] = surface
            case_policy_map[lower] = policy
    return forms, surface_map, case_policy_map


def load_city_source(
    path: Path,
) -> tuple[set[str], dict[str, str]]:
    forms: set[str] = set()
    surface_map: dict[str, str] = {}
    if not path.exists():
        return forms, surface_map
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"name", "simc", "rm", "stan_na", "source"}
        if set(reader.fieldnames or ()) != required:
            raise SystemExit(
                f"Malformed city source header {path}: expected {sorted(required)}"
            )
        for line_no, row in enumerate(reader, 2):
            name = row["name"].strip()
            if not name or row["rm"].strip() != "96":
                raise SystemExit(f"Malformed city source row {path}:{line_no}")
            if not is_candidate(name.lower()):
                raise SystemExit(
                    f"City source contains non-single-token form {path}:{line_no}: {name!r}"
                )
            lower = name.lower()
            forms.add(lower)
            prior = surface_map.get(lower)
            if prior is not None and prior != name:
                raise SystemExit(
                    f"Conflicting city capitalization {path}:{line_no}: {prior!r} vs {name!r}"
                )
            surface_map[lower] = name
    return forms, surface_map


def is_inflection_surface(word: str) -> bool:
    """Validate explicit proper-name/city inflection surfaces.

    The ordinary vocabulary gate is intentionally stricter and Polish-only. Explicitly
    audited proper names may legitimately use additional basic Latin letters (e.g. Alex),
    so this layer accepts ASCII A-Z plus Polish diacritics while still requiring one token.
    """
    return bool(re.fullmatch(r"^[A-Za-ząćęłńóśźżĄĆĘŁŃÓŚŹŻ]+$", word))


def validate_capitalization(
    surface: str,
    *,
    expected: str,
    context: str,
) -> None:
    """Enforce the canonical capitalization policy before a surface enters the dictionary.

    expected="lowercase" is the default lexical-vocabulary policy.
    expected="adjective" is the explicit lowercase policy for adjectives derived from
    proper names or geographic/administrative names (e.g. "warszawski").
    expected="capitalized" is reserved for source-backed proper-name/city surfaces.
    The exact expected surface is supplied by the audited source mapping, so this is
    deliberately a gate rather than a heuristic capitalization guess.
    """
    if expected in {"lowercase", "adjective"}:
        if surface != surface.lower():
            label = "adjective" if expected == "adjective" else "lowercase"
            raise SystemExit(
                f"Capitalization gate rejected {context}: expected {label} surface, got {surface!r}"
            )
        return
    if expected == "capitalized":
        if not surface or not surface[0].isupper():
            raise SystemExit(
                f"Capitalization gate rejected {context}: expected capitalized surface, got {surface!r}"
            )
        return
    raise SystemExit(f"Unknown capitalization policy {expected!r} for {context}")


def load_lowercase_inflection_surfaces(
    path: Path,
    lowercase_names: set[str],
) -> set[str]:
    """Return generated inflection surfaces belonging to lowercase name homonyms."""
    if not path.exists() or not lowercase_names:
        return set()
    forms: set[str] = set()
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            name = row.get("name", "").strip().lower()
            form = row.get("form", "").strip()
            if name in lowercase_names and form:
                forms.add(form.lower())
    return forms


def load_first_name_inflections(
    path: Path,
) -> tuple[set[str], dict[str, str]]:
    forms: set[str] = set()
    surface_map: dict[str, str] = {}
    if not path.exists():
        return forms, surface_map
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        expected_fields = {"name", "gender", "layer", "case", "form", "source", "morfeusz_version"}
        if set(reader.fieldnames or ()) != expected_fields:
            raise SystemExit(
                f"Malformed first-name inflection header {path}: expected {sorted(expected_fields)}"
            )
        for line_no, row in enumerate(reader, 2):
            form = row["form"].strip()
            case_tag = row["case"].strip()
            if case_tag not in {"nom", "gen", "dat", "acc", "inst", "loc", "voc"} or not form:
                raise SystemExit(f"Malformed first-name inflection row {path}:{line_no}")
            if not is_inflection_surface(form):
                raise SystemExit(f"Invalid first-name inflection form {path}:{line_no}: {form!r}")
            lower = form.lower()
            prior = surface_map.get(lower)
            if prior is not None and prior != form:
                # One CKDT lowercase key can have only one canonical surface. Prefer the
                # explicitly-capitalized proper-name surface when the same lowercase key
                # is encountered through multiple name paradigms.
                if prior[:1].isupper() and form[:1].islower():
                    form = prior
                elif form[:1].isupper() and prior[:1].islower():
                    surface_map[lower] = form
                elif prior != form:
                    raise SystemExit(
                        f"Conflicting first-name inflection surface {path}:{line_no}: {prior!r} vs {form!r}"
                    )
            else:
                surface_map[lower] = form
            forms.add(lower)
    return forms, surface_map


def load_terc_inflections(
    path: Path,
) -> tuple[set[str], dict[str, str], dict[str, str]]:
    forms: set[str] = set()
    surface_map: dict[str, str] = {}
    case_policy_map: dict[str, str] = {}
    if not path.exists():
        return forms, surface_map, case_policy_map
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        expected_fields = {"name", "level", "terc", "case", "form", "case_policy", "source", "morfeusz_version"}
        if set(reader.fieldnames or ()) != expected_fields:
            raise SystemExit(
                f"Malformed TERC inflection header {path}: expected {sorted(expected_fields)}"
            )
        for line_no, row in enumerate(reader, 2):
            form = row["form"].strip()
            case_tag = row["case"].strip()
            if case_tag not in {"nom", "gen", "dat", "acc", "inst", "loc", "voc"} or not form:
                raise SystemExit(f"Malformed TERC inflection row {path}:{line_no}")
            if not is_inflection_surface(form):
                raise SystemExit(f"Invalid TERC inflection form {path}:{line_no}: {form!r}")
            lower = form.lower()
            prior = surface_map.get(lower)
            if prior is not None and prior != form:
                raise SystemExit(
                    f"Conflicting TERC inflection surface {path}:{line_no}: {prior!r} vs {form!r}"
                )
            surface_map[lower] = form
            policy = row["case_policy"].strip()
            if policy not in {"lowercase", "capitalized"}:
                raise SystemExit(f"Invalid TERC inflection case policy {path}:{line_no}: {policy!r}")
            prior_policy = case_policy_map.get(lower)
            if prior_policy is not None and prior_policy != policy:
                raise SystemExit(f"Conflicting TERC inflection case policy {path}:{line_no}: {prior_policy!r} vs {policy!r}")
            case_policy_map[lower] = policy
            forms.add(lower)
    return forms, surface_map, case_policy_map


def load_geo_source(
    path: Path,
    expected_category: str,
) -> tuple[set[str], dict[str, str], dict[str, str]]:
    forms: set[str] = set()
    surface_map: dict[str, str] = {}
    case_policy_map: dict[str, str] = {}
    if not path.exists():
        return forms, surface_map, case_policy_map
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"name", "case_policy", "source"}
        if not required.issubset(set(reader.fieldnames or ())):
            raise SystemExit(
                f"Malformed {expected_category} source header {path}: missing {sorted(required - set(reader.fieldnames or ()))}"
            )
        for line_no, row in enumerate(reader, 2):
            name = row["name"].strip()
            policy = row["case_policy"].strip()
            if not name or policy not in {"lowercase", "capitalized"}:
                raise SystemExit(f"Malformed {expected_category} source row {path}:{line_no}")
            if not is_inflection_surface(name):
                raise SystemExit(f"Non-single-token {expected_category} source surface {path}:{line_no}: {name!r}")
            lower = name.lower()
            prior = surface_map.get(lower)
            if prior is not None and prior != name:
                raise SystemExit(
                    f"Conflicting {expected_category} source casing {path}:{line_no}: {prior!r} vs {name!r}"
                )
            prior_policy = case_policy_map.get(lower)
            if prior_policy is not None and prior_policy != policy:
                raise SystemExit(
                    f"Conflicting {expected_category} case policy {path}:{line_no}: {prior_policy!r} vs {policy!r}"
                )
            forms.add(lower)
            surface_map[lower] = name
            case_policy_map[lower] = policy
    return forms, surface_map, case_policy_map


def load_geo_inflections(
    path: Path,
) -> tuple[set[str], dict[str, str], dict[str, str]]:
    forms: set[str] = set()
    surface_map: dict[str, str] = {}
    case_policy_map: dict[str, str] = {}
    if not path.exists():
        return forms, surface_map, case_policy_map
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"category", "name", "number", "case", "form", "case_policy", "source", "morfeusz_version"}
        if set(reader.fieldnames or ()) != required:
            raise SystemExit(
                f"Malformed geo inflection header {path}: expected {sorted(required)}"
            )
        for line_no, row in enumerate(reader, 2):
            form = row["form"].strip()
            policy = row["case_policy"].strip()
            if row["case"] not in {"nom", "gen", "dat", "acc", "inst", "loc", "voc"}:
                raise SystemExit(f"Malformed geo inflection case {path}:{line_no}")
            if row["number"] not in {"sg", "pl", "source"}:
                raise SystemExit(f"Malformed geo inflection number {path}:{line_no}")
            if not form or policy not in {"lowercase", "capitalized"}:
                raise SystemExit(f"Malformed geo inflection row {path}:{line_no}")
            if not is_inflection_surface(form):
                raise SystemExit(f"Invalid geo inflection surface {path}:{line_no}: {form!r}")
            lower = form.lower()
            prior = surface_map.get(lower)
            if prior is not None and prior != form:
                raise SystemExit(
                    f"Conflicting geo inflection surface {path}:{line_no}: {prior!r} vs {form!r}"
                )
            prior_policy = case_policy_map.get(lower)
            if prior_policy is not None and prior_policy != policy:
                raise SystemExit(
                    f"Conflicting geo inflection case policy {path}:{line_no}: {prior_policy!r} vs {policy!r}"
                )
            forms.add(lower)
            surface_map[lower] = form
            case_policy_map[lower] = policy
    return forms, surface_map, case_policy_map


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=300000)
    ap.add_argument("--band", type=int, default=150000)
    ap.add_argument("--limit", type=int, default=150000)
    ap.add_argument(
        "--base-only",
        action="store_true",
        help="Build the 100k frequency core without names or cities.",
    )
    ap.add_argument("--aosp", type=Path, required=True)
    ap.add_argument(
        "--errors",
        type=Path,
        default=Path("sources/staging/autocorrect_errors.tsv"),
    )
    ap.add_argument(
        "--first-name-history",
        type=Path,
        default=None,
        help="Official 2006-2025 name-history report; injects the audited top 215 names per gender as explicit candidates.",
    )
    ap.add_argument(
        "--historical-first-names",
        type=Path,
        default=None,
        help="Reviewed historical name staging TSV; injects 20 female + 20 male historical candidates.",
    )
    ap.add_argument(
        "--first-name-surface-policy",
        type=Path,
        default=None,
        help="Explicit user-reviewed surface policy for first names.",
    )
    ap.add_argument(
        "--first-name-inflections",
        type=Path,
        default=None,
        help="Generated singular inflections for the already-selected first names.",
    )
    ap.add_argument(
        "--countries",
        type=Path,
        default=None,
        help="Official KSNG/GUGiK one-token country source.",
    )
    ap.add_argument(
        "--country-inflections",
        type=Path,
        default=None,
        help="Generated country inflections from KSNG/GUGiK names.",
    )
    ap.add_argument(
        "--capitals",
        type=Path,
        default=None,
        help="Official KSNG/GUGiK one-token capital source.",
    )
    ap.add_argument(
        "--capital-inflections",
        type=Path,
        default=None,
        help="Generated capital inflections from KSNG/GUGiK names.",
    )
    ap.add_argument(
        "--terc",
        type=Path,
        default=None,
        help="Current official GUS TERYT TERC three-level administrative source.",
    )
    ap.add_argument(
        "--terc-inflections",
        type=Path,
        default=None,
        help="Generated singular inflections for one-token TERC names.",
    )
    ap.add_argument(
        "--custom",
        type=Path,
        default=Path("sources/staging/custom_manual.tsv"),
        help="Explicit hand-reviewed manual/custom dictionary surfaces.",
    )
    ap.add_argument(
        "--cities",
        type=Path,
        default=None,
        help="Current official TERYT one-token city source.",
    )
    ap.add_argument(
        "--city-inflections",
        type=Path,
        default=None,
        help="Selected city inflections generated from the current TERYT source.",
    )
    ap.add_argument("--out-wordlist", type=Path, required=True)
    ap.add_argument("--out-report", type=Path, required=True)
    args = ap.parse_args()

    if args.base_only:
        # The base core is intentionally built only from frequency-ranked candidates
        # plus the normal linguistic evidence/quality gates. All additive category
        # inputs are excluded from this pass so its 100k membership remains immutable.
        args.first_name_history = None
        args.historical_first_names = None
        args.first_name_surface_policy = None
        args.first_name_inflections = None
        args.cities = None
        args.city_inflections = None
        args.terc = None
        args.terc_inflections = None
        args.countries = None
        args.country_inflections = None
        args.capitals = None
        args.capital_inflections = None
        args.custom = None

    from wordfreq import iter_wordlist, zipf_frequency
    try:
        from importlib.metadata import version as package_version
        wordfreq_version = package_version("wordfreq")
    except Exception:
        wordfreq_version = "unknown"

    ranked: list[str] = []
    seen: set[str] = set()
    non_polish = 0
    for raw in iter_wordlist("pl"):
        word = raw.lower()
        if word in seen:
            continue
        if is_candidate(word):
            seen.add(word)
            ranked.append(word)
            if len(ranked) >= args.top:
                break
        else:
            non_polish += 1

    # Snapshot the original wordfreq candidate universe before any explicit first-name,
    # city or morphology additions are appended. This is the baseline for the
    # later capacity-displacement audit.
    base_candidate_words = set(ranked)

    first_name_surface_policy: dict[str, str] = {}
    if args.first_name_surface_policy:
        with args.first_name_surface_policy.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row in reader:
                name = row["name"].strip()
                policy = row["policy"].strip()
                if not is_candidate(name):
                    raise SystemExit(f"Invalid first-name surface policy entry: {name!r}")
                if policy not in {"lowercase_common_noun", "exclude"}:
                    raise SystemExit(f"Invalid first-name surface policy for {name!r}: {policy!r}")
                first_name_surface_policy[name.lower()] = policy

    lowercase_first_name_exceptions = {
        name for name, policy in first_name_surface_policy.items()
        if policy == "lowercase_common_noun"
    }
    excluded_first_names = {
        name for name, policy in first_name_surface_policy.items()
        if policy == "exclude"
    }

    first_name_inflection_forms: set[str] = set()
    first_name_inflection_surface_map: dict[str, str] = {}
    lowercase_first_name_inflection_surfaces: set[str] = set()
    if args.first_name_inflections:
        first_name_inflection_forms, first_name_inflection_surface_map = load_first_name_inflections(
            args.first_name_inflections
        )
        lowercase_first_name_inflection_surfaces = load_lowercase_inflection_surfaces(
            args.first_name_inflections,
            lowercase_first_name_exceptions,
        )

    city_forms: set[str] = set()
    city_surface_map: dict[str, str] = {}
    if args.cities:
        city_forms, city_surface_map = load_city_source(args.cities)

    city_inflection_forms: set[str] = set()
    city_inflection_surface_map: dict[str, str] = {}
    if args.city_inflections:
        city_inflection_forms, city_inflection_surface_map = load_first_name_inflections(args.city_inflections)

    terc_forms: set[str] = set()
    terc_surface_map: dict[str, str] = {}
    terc_case_policy_map: dict[str, str] = {}
    if args.terc:
        with args.terc.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            required = {"level", "terc", "woj", "pow", "gmi", "rodz", "name", "nazdod", "stan_na", "eligible_single_token", "case_policy", "source_name", "source"}
            if set(reader.fieldnames or ()) != required:
                raise SystemExit(f"Malformed TERC source header {args.terc}: expected {sorted(required)}")
            terc_surface_map = {}
            for line_no, row in enumerate(reader, 2):
                name = row["name"].strip()
                if row["eligible_single_token"] != "yes":
                    continue
                if not is_inflection_surface(name):
                    raise SystemExit(f"Invalid TERC source surface {args.terc}:{line_no}: {name!r}")
                lower = name.lower()
                prior = terc_surface_map.get(lower)
                if prior is not None and prior != name:
                    raise SystemExit(f"Conflicting TERC source casing {args.terc}:{line_no}: {prior!r} vs {name!r}")
                terc_surface_map[lower] = name
                policy = row["case_policy"].strip()
                if policy not in {"lowercase", "capitalized"}:
                    raise SystemExit(f"Invalid TERC case policy {args.terc}:{line_no}: {policy!r}")
                terc_case_policy_map[lower] = policy
                terc_forms.add(lower)
    terc_inflection_forms: set[str] = set()
    terc_inflection_surface_map: dict[str, str] = {}
    terc_inflection_case_policy_map: dict[str, str] = {}
    if args.terc_inflections:
        terc_inflection_forms, terc_inflection_surface_map, terc_inflection_case_policy_map = load_terc_inflections(args.terc_inflections)

    country_forms: set[str] = set()
    country_surface_map: dict[str, str] = {}
    country_case_policy_map: dict[str, str] = {}
    capital_forms: set[str] = set()
    capital_surface_map: dict[str, str] = {}
    capital_case_policy_map: dict[str, str] = {}
    if args.countries:
        country_forms, country_surface_map, country_case_policy_map = load_geo_source(args.countries, "country")
    if args.capitals:
        capital_forms, capital_surface_map, capital_case_policy_map = load_geo_source(args.capitals, "capital")

    country_inflection_forms: set[str] = set()
    country_inflection_surface_map: dict[str, str] = {}
    country_inflection_case_policy_map: dict[str, str] = {}
    capital_inflection_forms: set[str] = set()
    capital_inflection_surface_map: dict[str, str] = {}
    capital_inflection_case_policy_map: dict[str, str] = {}
    if args.country_inflections:
        country_inflection_forms, country_inflection_surface_map, country_inflection_case_policy_map = load_geo_inflections(args.country_inflections)
    if args.capital_inflections:
        capital_inflection_forms, capital_inflection_surface_map, capital_inflection_case_policy_map = load_geo_inflections(args.capital_inflections)

    custom_forms: set[str] = set()
    custom_surface_map: dict[str, str] = {}
    custom_case_policy_map: dict[str, str] = {}
    if args.custom:
        custom_forms, custom_surface_map, custom_case_policy_map = load_custom_words(args.custom)

    first_name_case_map: dict[str, str] = {}
    reviewed_first_names: set[str] = set()
    first_name_meta: list[dict] = []
    if args.first_name_history:
        history = json.loads(args.first_name_history.read_text(encoding="utf-8"))
        for gender, key in (("F", "top_female"), ("M", "top_male")):
            selected = history[key][:215]
            if len(selected) != 215:
                raise SystemExit(f"First-name history {key} must contain at least 215 rows")
            for row in selected:
                canonical = str(row["name"]).strip()
                lower = canonical.lower()
                surface_policy = first_name_surface_policy.get(lower)
                first_name_meta.append({
                    "gender": gender,
                    "name": canonical,
                    "rank_20y": row["cumulative_rank_20y"],
                    "count_20y": row["cumulative_count_20y"],
                    "surface_policy": surface_policy or "capitalized_name",
                })
                if surface_policy == "exclude":
                    continue
                reviewed_first_names.add(lower)
                prior = first_name_case_map.get(lower)
                if prior is not None and prior != canonical:
                    raise SystemExit(f"Conflicting first-name casing: {prior!r} vs {canonical!r}")
                first_name_case_map[lower] = canonical
                if lower not in seen:
                    ranked.append(lower)
                    seen.add(lower)

    historical_first_names: set[str] = set()
    historical_first_name_meta: list[dict] = []
    if args.historical_first_names:
        with args.historical_first_names.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            rows = list(reader)
        if len(rows) != 40 or {row["gender"] for row in rows} != {"F", "M"}:
            raise SystemExit("Historical first-name staging must contain exactly 40 rows (20 F + 20 M)")
        if sum(row["gender"] == "F" for row in rows) != 20 or sum(row["gender"] == "M" for row in rows) != 20:
            raise SystemExit("Historical first-name staging must contain 20 F + 20 M rows")
        for row in rows:
            canonical = row["name"].strip()
            lower = canonical.lower()
            surface_policy = first_name_surface_policy.get(lower)
            historical_first_name_meta.append({
                "gender": row["gender"],
                "name": canonical,
                "basis": row["basis"],
                "source": row["source"],
                "status": row["status"],
                "surface_policy": surface_policy or "capitalized_name",
            })
            if surface_policy == "exclude":
                continue
            historical_first_names.add(lower)
            prior = first_name_case_map.get(lower)
            if prior is not None and prior != canonical:
                raise SystemExit(f"Conflicting first-name casing: {prior!r} vs {canonical!r}")
            first_name_case_map[lower] = canonical
            if lower not in seen:
                ranked.append(lower)
                seen.add(lower)

    for word in sorted(lowercase_first_name_exceptions):
        if word not in seen:
            ranked.append(word)
            seen.add(word)

    # Official TERYT city names are explicit candidates. Multiword/hyphenated names are
    # intentionally kept out of this one-token CKDT layer and are tracked by the extractor.
    for word in sorted(city_forms):
        if word not in seen:
            ranked.append(word)
            seen.add(word)

    # Generated city inflections are explicit candidates for the selected city subset.
    for word in sorted(city_inflection_forms):
        if word not in seen:
            ranked.append(word)
            seen.add(word)

    # Generated name inflections are explicit candidates. Lowercase homonym exceptions
    # are intentionally excluded from this layer because they are ordinary-word surfaces
    # and must remain governed by the normal Polish vocabulary/morphology pipeline.
    for word in sorted(first_name_inflection_forms - lowercase_first_name_exceptions):
        if word not in seen:
            ranked.append(word)
            seen.add(word)

    # Official three-level TERC names are explicit candidates. Lower-level TERC rows are
    # retained in the source audit but are not mixed into this flat administrative layer.
    for word in sorted(terc_forms | terc_inflection_forms):
        if word not in seen:
            ranked.append(word)
            seen.add(word)

    # Official countries and capitals are explicit audited candidates.
    for word in sorted(country_forms | country_inflection_forms | capital_forms | capital_inflection_forms):
        if word not in seen:
            ranked.append(word)
            seen.add(word)

    # Explicit manual/custom surfaces are added as audited candidates.
    for word in sorted(custom_forms):
        if word not in seen:
            ranked.append(word)
            seen.add(word)

    # Capture the candidate universe before the explicit first-name/city layers are
    # appended. This lets the final capacity audit identify words displaced specifically
    # by those additions.
    zipf = {word: float(zipf_frequency(word, "pl")) for word in ranked}
    aosp = load_aosp(args.aosp)
    spell = hunspell_accepts(ranked)
    blocked_errors, error_rows = load_blocked_errors(args.errors)
    reviewed_first_names |= historical_first_names
    positive = spell | aosp

    # High-confidence known-good set for typo detection.
    known_good = {
        word for word in positive
        if word in seen and zipf[word] >= 3.5
    }
    known_good |= set(ranked[:5000])

    at_risk = [
        word for word in ranked
        if word not in positive and zipf[word] < 3.5
    ]
    typo = typo_matches(at_risk, known_good, zipf)

    # Hard regression blocklist for foreign/proper-name surfaces observed in real Polish swipe tests.
    # These are blocked at source-generation time so the CKDT artifact cannot reintroduce them.
    regression_blocklist = {
        "chopin", "chopina", "goebbels", "goebbelsa",
        "catherine", "catalina", "cameron", "carli", "carlo",
        "castillo", "cali", "celli", "casino", "calli",
        "carrillo", "caroli", "cassino", "compos", "gourami",
        "celastial",
    }

    foreign_langs = ("en", "cs", "sk", "ru", "uk", "de", "es", "it", "fr", "pt", "nl")
    foreign: dict[str, tuple[str, float]] = {}
    for word in ranked:
        if zipf[word] >= 3.5:
            continue
        best_lang = ""
        best_z = 0.0
        for lang in foreign_langs:
            z = float(zipf_frequency(word, lang))
            if z > best_z:
                best_lang, best_z = lang, z
        if best_z >= 3.0 and best_z > zipf[word] + 1.0:
            foreign[word] = (best_lang, best_z)

    # Explicit project guards: high-value Polish forms and the known regression words.
    guards = {
        # Polish function words, including one-letter words that keyboard corpora may omit.
        "a", "i", "o", "u", "w", "z",
        "nie", "na", "się", "to", "jest", "że", "jak", "ale", "co",
        "tak", "może", "można", "który", "która", "które", "być",
        "mieć", "wziąć", "włączać", "rzeczywiście", "właśnie",
        "naprawdę", "spoko", "super",
    }

    keep: dict[str, str] = {}
    drop: dict[str, str] = {}

    rank_of = {word: rank for rank, word in enumerate(ranked)}

    for rank, word in enumerate(ranked):
        if word in blocked_errors:
            drop[word] = "reviewed-typo-blocklist"
            continue
        if word in regression_blocklist:
            drop[word] = "swipe-regression-blocklist"
            continue
        if word in excluded_first_names:
            drop[word] = "user-excluded-first-name"
            continue
        if word in lowercase_first_name_exceptions:
            keep[word] = "user-lowercase-common-noun"
            continue
        if word in guards:
            keep[word] = "guard"
            continue
        if word in terc_inflection_forms:
            keep[word] = "reviewed-terc-inflection"
            continue
        if word in terc_forms:
            keep[word] = "reviewed-terc"
            continue
        if word in country_inflection_forms:
            keep[word] = "reviewed-country-inflection"
            continue
        if word in country_forms:
            keep[word] = "reviewed-country"
            continue
        if word in capital_inflection_forms:
            keep[word] = "reviewed-capital-inflection"
            continue
        if word in capital_forms:
            keep[word] = "reviewed-capital"
            continue
        if word in custom_forms:
            keep[word] = "custom-manual"
            continue
        if word in first_name_inflection_forms and word not in lowercase_first_name_exceptions:
            keep[word] = "reviewed-first-name-inflection"
            continue
        if word in city_inflection_forms:
            keep[word] = "reviewed-city-inflection"
            continue
        if word in city_forms:
            keep[word] = "reviewed-city"
            continue
        if word in reviewed_first_names:
            # Explicitly selected first names are source-backed candidates.
            # Their inclusion must not depend on corpus/foreign-language evidence;
            # otherwise the audited 215+215 + 20+20 selection would be silently lost.
            keep[word] = (
                "reviewed-historical-first-name"
                if word in historical_first_names
                else "reviewed-first-name"
            )
            continue
        if word in foreign and word not in guards:
            drop[word] = f"foreign:{foreign[word][0]}"
            continue
        # Bare ASCII forms are especially prone to imported/proper-name noise.
        # For non-guard vocabulary, require both Polish spelling acceptance and
        # mobile-keyboard evidence from AOSP. This is intentionally stricter for
        # unaccented forms because proper names and foreign words are concentrated there.
        if word.isascii() and (word not in spell or word not in aosp):
            drop[word] = "ascii-without-dual-evidence"
            continue
        if word not in positive:
            if word in typo:
                drop[word] = f"typo->{typo[word][0]}"
            else:
                drop[word] = "no-positive-evidence"
            continue
        keep[word] = "spell-evidence"

    # Suppress bare-ASCII aliases when an accented canonical form is positively evidenced.
    normalized_groups: dict[str, list[str]] = {}
    for word in keep:
        normalized_groups.setdefault(normalize_accents(word), []).append(word)

    for normalized, words in normalized_groups.items():
        accented = [w for w in words if any(ch in DIACRITICS for ch in w)]
        if not accented:
            continue
        for word in list(words):
            if any(ch in DIACRITICS for ch in word):
                continue
            if (
                word in positive
                or word in guards
                or word in first_name_inflection_forms
                or word in city_inflection_forms
            ):
                continue
            best = max(accented, key=lambda w: zipf.get(w, 0.0))
            if best != word and best in positive:
                del keep[word]
                drop[word] = f"diacritic-alias->{best}"

    # Explicit first-name/city additions are protected. Track only additions that were
    # genuinely absent from the pre-augmentation candidate universe; a city/name that was
    # already present in the base corpus does not consume an extra dictionary slot.
    name_city_augmented_words = (
        (reviewed_first_names - lowercase_first_name_exceptions)
        | (first_name_inflection_forms - lowercase_first_name_exceptions)
        | city_forms
        | city_inflection_forms
    )
    new_name_city_words = {
        w for w in name_city_augmented_words
        if w not in base_candidate_words and w in keep
    }
    pre_limit_keep = set(keep)

    # Enforce hard size cap by wordfreq rank while protecting guards and oracle-backed top words.
    if len(keep) > args.limit:
        protected = {
            w for w in keep
            if w in guards or w in custom_forms or w in reviewed_first_names or w in first_name_inflection_forms or w in city_forms or w in city_inflection_forms or w in terc_forms or w in terc_inflection_forms or w in country_forms or w in country_inflection_forms or w in capital_forms or w in capital_inflection_forms
        }
        if len(protected) > args.limit:
            raise SystemExit(
                "Protected first-name/city morphology layers exceed dictionary limit: "
                + f"{len(protected)} > {args.limit}"
            )
        rest = sorted(
            (w for w in keep if w not in protected),
            key=lambda w: (rank_of[w], -zipf[w], w),
        )
        for word in rest[max(0, args.limit - len(protected)):]:
            del keep[word]
            drop[word] = "limit-cut"

    # Reconstruct the counterfactual final dictionary without the genuinely new
    # name/city layer so capacity displacement caused by those additions can be measured.
    baseline_without_new_name_city = pre_limit_keep - new_name_city_words
    baseline_protected = {
        w for w in baseline_without_new_name_city
        if w in guards
    }
    if len(baseline_without_new_name_city) <= args.limit:
        baseline_final_without_new_name_city = baseline_without_new_name_city
    else:
        baseline_rest = sorted(
            (w for w in baseline_without_new_name_city if w not in baseline_protected),
            key=lambda w: (rank_of[w], -zipf[w], w),
        )
        baseline_final_without_new_name_city = set(baseline_protected)
        baseline_final_without_new_name_city.update(
            baseline_rest[: max(0, args.limit - len(baseline_protected))]
        )
    capacity_displaced_by_name_city = sorted(
        baseline_final_without_new_name_city - set(keep)
    )

    missing_guards = sorted(guards - set(keep))
    if missing_guards:
        raise SystemExit("Guard words lost: " + ", ".join(missing_guards))

    # Final capitalization gate: every retained word is checked immediately before it
    # becomes a dictionary surface. Ordinary vocabulary stays lowercase; only audited
    # proper-name/city mappings may intentionally restore an initial capital.
    surface_keep = {}
    capitalization_audit = {
        "checked": 0,
        "lowercase_surfaces": 0,
        "adjective_surfaces": 0,
        "capitalized_surfaces": 0,
        "lowercase_first_name_inflection_surfaces": len(lowercase_first_name_inflection_surfaces),
        "violations": [],
    }
    for word, reason in keep.items():
        expected_surface = word
        capitalization_policy = "lowercase"
        context = f"{reason}:{word}"

        # Derived adjectives are ordinary lexical surfaces. The current pipeline does not
        # generate them in the proper-name/city inflection maps, so they stay lowercase.
        # Future category generators should tag their adjective outputs as "adjective"
        # rather than routing them through proper-name capitalization.

        if word in lowercase_first_name_exceptions:
            expected_surface = word
            capitalization_policy = "lowercase"
        elif word in lowercase_first_name_inflection_surfaces:
            expected_surface = word
            capitalization_policy = "lowercase"
        elif word in terc_surface_map:
            expected_surface = terc_surface_map[word]
            capitalization_policy = terc_case_policy_map[word]
        elif word in terc_inflection_surface_map:
            expected_surface = terc_inflection_surface_map[word]
            capitalization_policy = terc_inflection_case_policy_map[word]
        elif word in country_surface_map:
            expected_surface = country_surface_map[word]
            capitalization_policy = country_case_policy_map[word]
        elif word in capital_surface_map:
            expected_surface = capital_surface_map[word]
            capitalization_policy = capital_case_policy_map[word]
        elif word in country_inflection_surface_map:
            expected_surface = country_inflection_surface_map[word]
            capitalization_policy = country_inflection_case_policy_map[word]
        elif word in capital_inflection_surface_map:
            expected_surface = capital_inflection_surface_map[word]
            capitalization_policy = capital_inflection_case_policy_map[word]
        elif word in custom_surface_map:
            expected_surface = custom_surface_map[word]
            capitalization_policy = custom_case_policy_map[word]
        elif word in city_surface_map:
            expected_surface = city_surface_map[word]
            capitalization_policy = "capitalized"
        elif word in city_inflection_surface_map:
            expected_surface = city_inflection_surface_map[word]
            capitalization_policy = "capitalized"
        elif word in first_name_inflection_surface_map:
            expected_surface = first_name_inflection_surface_map[word]
            capitalization_policy = "capitalized"
        elif word in first_name_case_map:
            expected_surface = first_name_case_map[word]
            capitalization_policy = "capitalized"

        try:
            validate_capitalization(
                expected_surface,
                expected=capitalization_policy,
                context=context,
            )
            if capitalization_policy == "lowercase":
                capitalization_audit["lowercase_surfaces"] += 1
            elif capitalization_policy == "adjective":
                capitalization_audit["adjective_surfaces"] += 1
            else:
                capitalization_audit["capitalized_surfaces"] += 1
        except SystemExit as exc:
            capitalization_audit["violations"].append(str(exc))
            raise
        capitalization_audit["checked"] += 1

        surface_keep[expected_surface] = reason

    if capitalization_audit["checked"] != len(keep):
        raise SystemExit(
            "Capitalization gate did not inspect every retained dictionary word"
        )
    if capitalization_audit["violations"]:
        raise SystemExit(
            "Capitalization gate violations: "
            + "; ".join(capitalization_audit["violations"])
        )

    words_sorted = sorted(surface_keep)
    args.out_wordlist.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_wordlist.write_text(
        "# CleverKeys Polish preview word list\n"
        f"# wordfreq={wordfreq_version} ref={EXPECTED_WORDFREQ_COMMIT}\n"
        f"# candidates={len(ranked)} band={args.band} limit={args.limit} keep={len(words_sorted)}\n"
        + "\n".join(words_sorted)
        + "\n",
        encoding="utf-8",
    )

    report = {
        "mode": "preview",
        "wordfreq_version": wordfreq_version,
        "wordfreq_ref": EXPECTED_WORDFREQ_COMMIT,
        "candidate_count": len(ranked),
        "non_polish_tokens_seen": non_polish,
        "aosp_count": len(aosp),
        "hunspell_count": len(spell),
        "positive_union": len(positive),
        "aosp_overlap": len(set(ranked) & aosp),
        "hunspell_overlap": len(set(ranked) & spell),
        "diacritic_candidate_count": sum(
            1 for w in ranked if any(ch in DIACRITICS for ch in w)
        ),
        "typo_candidates": len(typo),
        "foreign_candidates": len(foreign),
        "reviewed_error_rows": len(error_rows),
        "reviewed_error_forms_present_in_candidates": sorted(blocked_errors & set(ranked)),
        "kept": len(keep),
        "capitalization_audit": capitalization_audit,
        "kept_reasons": {
            "spell_evidence": sum(1 for r in keep.values() if r == "spell-evidence"),
            "guard": sum(1 for r in keep.values() if r == "guard"),
            "reviewed_first_name": sum(1 for r in keep.values() if r == "reviewed-first-name"),
            "reviewed_historical_first_name": sum(1 for r in keep.values() if r == "reviewed-historical-first-name"),
            "reviewed_terc": sum(1 for r in keep.values() if r == "reviewed-terc"),
            "reviewed_terc_inflection": sum(1 for r in keep.values() if r == "reviewed-terc-inflection"),
            "reviewed_country": sum(1 for r in keep.values() if r == "reviewed-country"),
            "reviewed_country_inflection": sum(1 for r in keep.values() if r == "reviewed-country-inflection"),
            "reviewed_capital": sum(1 for r in keep.values() if r == "reviewed-capital"),
            "reviewed_capital_inflection": sum(1 for r in keep.values() if r == "reviewed-capital-inflection"),
            "custom_manual": sum(1 for r in keep.values() if r == "custom-manual"),
            "reviewed_first_name_inflection": sum(1 for r in keep.values() if r == "reviewed-first-name-inflection"),
            "reviewed_city": sum(1 for r in keep.values() if r == "reviewed-city"),
            "reviewed_city_inflection": sum(1 for r in keep.values() if r == "reviewed-city-inflection"),
        },
        "reviewed_first_names": {
            "enabled": args.first_name_history is not None,
            "selected_total": len(first_name_meta) + len(historical_first_name_meta),
            "lowercase_common_noun_exceptions": sorted(lowercase_first_name_exceptions),
            "excluded_first_names": sorted(excluded_first_names),
            "count": len(reviewed_first_names),
            "selected_per_gender": 215 if args.first_name_history else 0,
            "provenance": "official dane.gov.pl first-name statistics, 2006-2025" if args.first_name_history else None,
            "selection": first_name_meta,
            "historical_count": len(historical_first_names),
            "historical_selection": historical_first_name_meta,
            "missing_from_keep": sorted(reviewed_first_names - set(keep)),
            "inflection_forms": len(first_name_inflection_forms),
            "city_names": len(city_forms),
            "city_inflection_forms": len(city_inflection_forms),
        },
        "reviewed_first_name_evidence_gates": {
            "requires_positive_source": True,
            "ascii_requires_hunspell_and_aosp": True,
            "foreign_dominant_is_not_overridden": True,
        },
        "dropped": len(drop),
        "drop_reasons": {},
        "name_city_capacity_audit": {
            "new_name_city_words": len(new_name_city_words),
            "pre_limit_keep": len(pre_limit_keep),
            "baseline_without_new_name_city": len(baseline_without_new_name_city),
            "baseline_final_without_new_name_city": len(baseline_final_without_new_name_city),
            "final_keep": len(keep),
            "capacity_displaced_count": len(capacity_displaced_by_name_city),
            "capacity_displaced_words": capacity_displaced_by_name_city,
        },
        "samples": {
            "name_city_capacity_displaced": capacity_displaced_by_name_city,
            "typo": sorted(
                [{"word": w, "target": v[0], "rule": v[1], "gap": round(v[2], 2)}
                 for w, v in typo.items()],
                key=lambda x: (-x["gap"], x["word"]),
            )[:100],
            "foreign": sorted(
                [{"word": w, "language": v[0], "foreign_zipf": round(v[1], 2),
                  "polish_zipf": round(zipf[w], 2)}
                 for w, v in foreign.items()],
                key=lambda x: (-x["foreign_zipf"], x["word"]),
            )[:100],
            "kept_tail": [
                {"word": w, "zipf": round(zipf[w], 2), "reason": surface_keep.get(w, keep[w])}
                for w in sorted(keep, key=lambda x: (-zipf[x], x))[:100]
            ],
        },
        "promotion": {
            "approved": False,
            "source": "preview only; not written to source/",
            "next_step": "manual review + CKDT V2 build + app smoke test",
        },
    }
    from collections import Counter
    report["drop_reasons"] = dict(Counter(
        value.split("->")[0].split(":")[0] for value in drop.values()
    ))

    args.out_report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "kept": report["kept"],
        "new_name_city_words": report["name_city_capacity_audit"]["new_name_city_words"],
        "capacity_displaced_count": report["name_city_capacity_audit"]["capacity_displaced_count"],
        "capacity_displaced_words": report["name_city_capacity_audit"]["capacity_displaced_words"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
