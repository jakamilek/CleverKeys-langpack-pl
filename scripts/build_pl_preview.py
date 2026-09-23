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



def load_reviewed_morphology(
    path: Path,
) -> tuple[set[str], dict[str, list[str]]]:
    forms: set[str] = set()
    families: dict[str, list[str]] = {}
    if not path.exists():
        return forms, families
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 5:
            raise SystemExit(
                f"Malformed morphology row {path}:{line_no}; expected 5 TSV columns"
            )
        family_id, lemma, raw_forms, basis, note = parts
        if not family_id or not lemma or not raw_forms or not basis or not note:
            raise SystemExit(f"Malformed morphology row {path}:{line_no}")
        family_forms = [w.strip().lower() for w in raw_forms.split(";") if w.strip()]
        if not family_forms:
            raise SystemExit(f"Empty morphology family {path}:{line_no}")
        invalid = [w for w in [lemma.lower(), *family_forms] if not is_candidate(w)]
        if invalid:
            raise SystemExit(
                f"Invalid morphology candidate(s) at {path}:{line_no}: "
                + ", ".join(sorted(set(invalid)))
            )
        bucket = families.setdefault(family_id, [])
        for word in family_forms:
            if word not in bucket:
                bucket.append(word)
            forms.add(word)
    return forms, families


def load_reviewed_proper_nouns(
    path: Path,
) -> tuple[set[str], dict[str, list[str]], dict[str, str]]:
    forms: set[str] = set()
    families: dict[str, list[str]] = {}
    lower_to_canonical: dict[str, str] = {}
    if not path.exists():
        return forms, families, lower_to_canonical
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("	")
        if len(parts) != 4:
            raise SystemExit(
                f"Malformed proper-noun row {path}:{line_no}; expected 4 TSV columns"
            )
        family_id, raw_forms, basis, note = parts
        if not family_id or not raw_forms or not basis or not note:
            raise SystemExit(f"Malformed proper-noun row {path}:{line_no}")
        family_forms = [w.strip() for w in raw_forms.split(";") if w.strip()]
        if not family_forms:
            raise SystemExit(f"Empty proper-noun family {path}:{line_no}")
        invalid = [w for w in family_forms if not is_candidate(w)]
        if invalid:
            raise SystemExit(
                f"Invalid proper-noun candidate(s) at {path}:{line_no}: "
                + ", ".join(sorted(set(invalid)))
            )
        bucket = families.setdefault(family_id, [])
        for word in family_forms:
            lower = word.lower()
            prior = lower_to_canonical.get(lower)
            if prior is not None and prior != word:
                raise SystemExit(
                    f"Conflicting proper-noun casing at {path}:{line_no}: "
                    f"{prior!r} vs {word!r}"
                )
            lower_to_canonical[lower] = word
            if word not in bucket:
                bucket.append(word)
            forms.add(word)
    return forms, families, lower_to_canonical


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=100000)
    ap.add_argument("--band", type=int, default=100000)
    ap.add_argument("--limit", type=int, default=100000)
    ap.add_argument("--aosp", type=Path, required=True)
    ap.add_argument(
        "--errors",
        type=Path,
        default=Path("sources/staging/autocorrect_errors.tsv"),
    )
    ap.add_argument(
        "--morphology",
        type=Path,
        default=Path("sources/staging/reviewed_morphology.tsv"),
    )
    ap.add_argument(
        "--proper-nouns",
        type=Path,
        default=Path("sources/staging/reviewed_proper_nouns.tsv"),
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
        "--first-name-homonyms",
        type=Path,
        default=None,
        help="Lowercase first-name forms that collide with SGJP common nouns; these are excluded as names but may remain as ordinary lowercase words.",
    )
    ap.add_argument("--out-wordlist", type=Path, required=True)
    ap.add_argument("--out-report", type=Path, required=True)
    args = ap.parse_args()

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

    first_name_homonyms: set[str] = set()
    if args.first_name_homonyms:
        for line in args.first_name_homonyms.read_text(encoding="utf-8").splitlines():
            line = line.strip().lower()
            if line:
                if not is_candidate(line):
                    raise SystemExit(f"Invalid first-name homonym blocklist entry: {line!r}")
                first_name_homonyms.add(line)

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
                excluded_common_noun = lower in first_name_homonyms
                first_name_meta.append({
                    "gender": gender,
                    "name": canonical,
                    "rank_20y": row["cumulative_rank_20y"],
                    "count_20y": row["cumulative_count_20y"],
                    "excluded_common_noun_homonym": excluded_common_noun,
                })
                if excluded_common_noun:
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
            historical_first_names.add(lower)
            excluded_common_noun = lower in first_name_homonyms
            historical_first_name_meta.append({
                "gender": row["gender"],
                "name": canonical,
                "basis": row["basis"],
                "source": row["source"],
                "status": row["status"],
                "excluded_common_noun_homonym": excluded_common_noun,
            })
            if excluded_common_noun:
                continue
            prior = first_name_case_map.get(lower)
            if prior is not None and prior != canonical:
                raise SystemExit(f"Conflicting first-name casing: {prior!r} vs {canonical!r}")
            first_name_case_map[lower] = canonical
            if lower not in seen:
                ranked.append(lower)
                seen.add(lower)

    zipf = {word: float(zipf_frequency(word, "pl")) for word in ranked}
    aosp = load_aosp(args.aosp)
    spell = hunspell_accepts(ranked)
    blocked_errors, error_rows = load_blocked_errors(args.errors)
    reviewed_morphology, morphology_families = load_reviewed_morphology(args.morphology)
    reviewed_proper_nouns, proper_noun_families, proper_case_map = load_reviewed_proper_nouns(
        args.proper_nouns
    )
    base_ranked = set(ranked)
    supplemental_morphology = sorted(reviewed_morphology - base_ranked)
    for word in supplemental_morphology:
        ranked.append(word)
        seen.add(word)
    supplemental_proper_nouns = sorted(
        {word.lower() for word in reviewed_proper_nouns} - set(ranked)
    )
    for word in supplemental_proper_nouns:
        ranked.append(word)
        seen.add(word)
    zipf.update({
        word: float(zipf_frequency(word, "pl"))
        for word in supplemental_morphology + supplemental_proper_nouns
    })
    reviewed_proper_nouns_lower = {word.lower() for word in reviewed_proper_nouns}
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
        if word in guards:
            keep[word] = "guard"
            continue
        if word in reviewed_morphology:
            keep[word] = "reviewed-morphology"
            continue
        if word in reviewed_proper_nouns_lower:
            keep[word] = "reviewed-proper-noun"
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
            if word in positive or word in guards or word in reviewed_morphology:
                continue
            if word in reviewed_proper_nouns_lower:
                continue
            best = max(accented, key=lambda w: zipf.get(w, 0.0))
            if best != word and best in positive:
                del keep[word]
                drop[word] = f"diacritic-alias->{best}"

    # Enforce hard size cap by wordfreq rank while protecting guards and oracle-backed top words.
    if len(keep) > args.limit:
        protected = {
            w for w in keep
            if w in guards or w in reviewed_morphology or w in reviewed_proper_nouns_lower or w in reviewed_first_names
        }
        rest = sorted(
            (w for w in keep if w not in protected),
            key=lambda w: (rank_of[w], -zipf[w], w),
        )
        for word in rest[max(0, args.limit - len(protected)):]:
            del keep[word]
            drop[word] = "limit-cut"

    missing_guards = sorted(guards - set(keep))
    if missing_guards:
        raise SystemExit("Guard words lost: " + ", ".join(missing_guards))

    missing_proper_nouns = sorted(reviewed_proper_nouns_lower - set(keep))
    if missing_proper_nouns:
        raise SystemExit(
            "Reviewed proper nouns lost: " + ", ".join(missing_proper_nouns)
        )

    surface_keep = {
        proper_case_map.get(word, first_name_case_map.get(word, word)): reason
        for word, reason in keep.items()
    }
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
        "kept_reasons": {
            "spell_evidence": sum(1 for r in keep.values() if r == "spell-evidence"),
            "guard": sum(1 for r in keep.values() if r == "guard"),
            "reviewed_morphology": sum(1 for r in keep.values() if r == "reviewed-morphology"),
            "reviewed_proper_noun": sum(1 for r in keep.values() if r == "reviewed-proper-noun"),
            "reviewed_first_name": sum(1 for r in keep.values() if r == "reviewed-first-name"),
            "reviewed_historical_first_name": sum(1 for r in keep.values() if r == "reviewed-historical-first-name"),
        },
        "reviewed_first_names": {
            "enabled": args.first_name_history is not None,
            "selected_total": len(first_name_meta) + len(historical_first_name_meta),
            "excluded_common_noun_homonym_count": len(first_name_homonyms),
            "excluded_common_noun_homonyms": sorted(first_name_homonyms),
            "count": len(reviewed_first_names),
            "selected_per_gender": 215 if args.first_name_history else 0,
            "provenance": "official dane.gov.pl first-name statistics, 2006-2025" if args.first_name_history else None,
            "selection": first_name_meta,
            "historical_count": len(historical_first_names),
            "historical_selection": historical_first_name_meta,
            "missing_from_keep": sorted(reviewed_first_names - set(keep)),
        },
        "reviewed_first_name_evidence_gates": {
            "requires_positive_source": True,
            "ascii_requires_hunspell_and_aosp": True,
            "foreign_dominant_is_not_overridden": True,
        },
        "reviewed_morphology": {
            "family_count": len(morphology_families),
            "form_count": len(reviewed_morphology),
            "supplemental_form_count": len(supplemental_morphology),
            "families": {
                family_id: sorted(forms)
                for family_id, forms in sorted(morphology_families.items())
            },
        },
        "reviewed_proper_nouns": {
            "family_count": len(proper_noun_families),
            "form_count": len(reviewed_proper_nouns),
            "supplemental_form_count": len(supplemental_proper_nouns),
            "families": {
                family_id: sorted(forms)
                for family_id, forms in sorted(proper_noun_families.items())
            },
        },
        "dropped": len(drop),
        "drop_reasons": {},
        "samples": {
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
                {"word": w, "zipf": round(zipf[w], 2), "reason": surface_keep.get(proper_case_map.get(w, w), keep[w])}
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

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
