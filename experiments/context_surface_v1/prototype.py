#!/usr/bin/env python3
"""Offline surface experiment. No decoder, model inference or production ranking."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

CASE_MODES = {"none", "sentence_start", "shift", "caps_lock"}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def key(surface: str) -> str:
    # API v1: lowercase, preserving diacritics. No accent stripping or lemmatizing.
    return surface.lower()


def text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonblank string")
    return value


@dataclass(frozen=True)
class ContextWindow:
    text: str
    word_count: int
    source_char_count: int
    character_truncated: bool
    word_truncated: bool
    boundary_cues: tuple[int, ...]


def word_spans(value: str) -> list[tuple[int, int]]:
    """Unicode letter runs, including combining marks and internal joiners."""
    spans = []
    index = 0
    while index < len(value):
        if not unicodedata.category(value[index]).startswith("L"):
            index += 1
            continue
        start = index
        index += 1
        while index < len(value):
            category = unicodedata.category(value[index])
            if category.startswith(("L", "M")):
                index += 1
            elif value[index] in "'’-" and index + 1 < len(value) and unicodedata.category(value[index + 1]).startswith("L"):
                index += 1
            else:
                break
        spans.append((start, index))
    return spans


def context_window(before_cursor: str, max_words: int = 64,
                   max_chars: int = 4096) -> ContextWindow:
    """Keep the bounded exact suffix; punctuation offsets are cues, not segmentation.

    Input is only text BEFORE the cursor. Character truncation discards a cut word;
    word truncation starts at a complete Unicode word. Case, joiners, accents and
    line breaks are untouched. Text after the cursor is never an input.
    """
    if not isinstance(before_cursor, str):
        raise ValueError("before_cursor must be text")
    if type(max_words) is not int or type(max_chars) is not int:
        raise ValueError("limits must be integers")
    if max_words < 1 or max_chars < 1:
        raise ValueError("limits must be positive")
    start = max(0, len(before_cursor) - max_chars)
    char_truncated = start > 0
    if start and not before_cursor[start - 1].isspace() and not before_cursor[start].isspace():
        # A token can include a combining mark or a joiner, so use whitespace as
        # a conservative cut boundary. A giant unbroken token yields no context.
        while start < len(before_cursor) and not before_cursor[start].isspace():
            start += 1
    suffix = before_cursor[start:]
    words = word_spans(suffix)
    word_truncated = len(words) > max_words
    if word_truncated:
        suffix = suffix[words[-max_words][0]:]
    cues = tuple(i for i, char in enumerate(suffix) if char in ".!?\n\r")
    return ContextWindow(suffix, len(word_spans(suffix)), len(before_cursor),
                         char_truncated, word_truncated, cues)


def load_sidecar(document: dict[str, Any]) -> tuple[str, dict[str, dict[str, Any]]]:
    """Validate the subset needed by this experiment, not the full future importer."""
    if type(document.get("schemaVersion")) is not int or document["schemaVersion"] != 1:
        raise ValueError("unsupported sidecar schemaVersion")
    language = text(document.get("languageCode"), "languageCode")
    if not isinstance(document.get("entries"), list):
        raise ValueError("entries must be a list")
    entries: dict[str, dict[str, Any]] = {}
    for entry in document["entries"]:
        if not isinstance(entry, dict):
            raise ValueError("entry must be an object")
        surface_key = text(entry.get("surfaceKey"), "surfaceKey")
        if surface_key != key(surface_key) or surface_key in entries:
            raise ValueError("surfaceKey must be lowercase and unique")
        capitalization = entry.get("capitalization")
        if capitalization is not None:
            if not isinstance(capitalization, dict):
                raise ValueError("capitalization must be an object")
            variants = capitalization.get("variants", [])
            if not isinstance(variants, list):
                raise ValueError("variants must be a list")
            surfaces: set[str] = set()
            for variant in variants:
                if not isinstance(variant, dict):
                    raise ValueError("variant must be an object")
                surface = text(variant.get("surface"), "surface")
                if key(surface) != surface_key or surface in surfaces:
                    raise ValueError("variant must belong to its key and be unique")
                policy = variant.get("casePolicy")
                if policy not in {"lowercase", "capitalized"}:
                    raise ValueError("unsupported casePolicy")
                if policy == "lowercase" and surface != key(surface):
                    raise ValueError("lowercase variant has capital letters")
                if policy == "capitalized" and not surface[0].isupper():
                    raise ValueError("capitalized variant must start with uppercase")
                surfaces.add(surface)
            default = capitalization.get("defaultSurface")
            if default is not None and default not in surfaces:
                raise ValueError("defaultSurface must be a declared variant")
        entries[surface_key] = entry
    return language, entries


def candidate_groups(candidates: list[dict[str, Any]], language: str,
                     entries: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Case-insensitive lexical dedupe in input rank order; no new words."""
    if not isinstance(candidates, list):
        raise ValueError("candidates must be a list")
    groups = []
    seen: set[tuple[str, str]] = set()
    for index, candidate in enumerate(candidates):
        surface = text(candidate.get("surface"), "candidate.surface")
        lang = text(candidate.get("languageCode", language), "candidate.languageCode")
        score = candidate.get("engineScore")
        if type(score) not in {int, float} or not math.isfinite(score) or score < 0:
            raise ValueError("engineScore must be finite and nonnegative")
        surface_key = key(surface)
        identity = (lang, surface_key)
        if identity in seen:
            continue
        seen.add(identity)
        entry = entries.get(surface_key, {}) if lang == language else {}
        capitalization = entry.get("capitalization") or {}
        variants = [v["surface"] for v in capitalization.get("variants", [])] or [surface]
        default = capitalization.get("defaultSurface") or variants[0]
        groups.append({"languageCode": lang, "surfaceKey": surface_key,
                       "engineScore": score, "decoderIndex": index,
                       "defaultSurface": default, "variants": variants})
    return groups


def prepare(cases_document: dict[str, Any], sidecar: dict[str, Any],
            max_words: int = 64, max_chars: int = 4096) -> dict[str, Any]:
    language, entries = load_sidecar(sidecar)
    if type(cases_document.get("schemaVersion")) is not int or cases_document["schemaVersion"] != 1:
        raise ValueError("unsupported cases schemaVersion")
    if not isinstance(cases_document.get("cases"), list):
        raise ValueError("cases must be a list")
    requests = []
    seen = set()
    for case in cases_document["cases"]:
        case_id = text(case.get("id"), "case.id")
        if case_id in seen:
            raise ValueError("duplicate case id")
        seen.add(case_id)
        mode = case.get("caseMode", "none")
        if mode not in CASE_MODES:
            raise ValueError("unsupported caseMode")
        groups = candidate_groups(case["candidates"], language, entries)
        for window_name, word_limit in (("two_words", 2), ("long", max_words)):
            context = context_window(case["beforeCursor"], word_limit, max_chars)
            # Gold labels and descriptive case names never enter model requests.
            requests.append({"requestId": f"{case_id}/{window_name}", "caseMode": mode,
                             "context": asdict(context), "candidates": groups})
    payload = {"schemaVersion": 1, "maxWords": max_words, "maxChars": max_chars,
               "sidecarSha256": digest(sidecar), "requests": requests}
    return {**payload, "requestSha256": digest(payload)}


def validate_predictions(document: dict[str, Any], request: dict[str, Any]) -> dict[str, dict[tuple[str, str, str], float]]:
    if type(document.get("schemaVersion")) is not int or document["schemaVersion"] != 1 or document.get("requestSha256") != request["requestSha256"]:
        raise ValueError("prediction schema or request hash mismatch")
    source = document.get("source", {})
    if source.get("kind") not in {"model", "controlled_test"}:
        raise ValueError("source.kind must distinguish model from controlled_test")
    text(source.get("name"), "source.name")
    text(source.get("revision"), "source.revision")
    requests = {item["requestId"]: item for item in request["requests"]}
    result = {}
    for row in document["results"]:
        request_id = row.get("requestId")
        if request_id not in requests or request_id in result:
            raise ValueError("unknown or duplicate prediction request")
        groups = requests[request_id]["candidates"]
        allowed = {(g["languageCode"], g["surfaceKey"], surface)
                   for g in groups for surface in g["variants"]}
        scores = {}
        for item in row["variantScores"]:
            identity = (item["languageCode"], item["surfaceKey"], item["surface"])
            score = item["score"]
            if identity not in allowed or identity in scores:
                raise ValueError("unknown or duplicate variant score")
            if type(score) not in {int, float} or not math.isfinite(score):
                raise ValueError("variant score must be finite")
            scores[identity] = score
        for group in groups:
            identities = {(group["languageCode"], group["surfaceKey"], surface)
                          for surface in group["variants"]}
            if identities & scores.keys() and not identities <= scores.keys():
                raise ValueError("all variants of a scored candidate are required")
        result[request_id] = scores
    if result.keys() != requests.keys():
        raise ValueError("one prediction result per request is required")
    return result


def display(surface: str, mode: str) -> str:
    if mode == "caps_lock":
        return surface.upper()
    if mode in {"shift", "sentence_start"}:
        return surface[0].upper() + surface[1:]
    return surface


def resolve(groups: list[dict[str, Any]], scores: dict[tuple[str, str, str], float] | None = None,
            case_mode: str = "none") -> list[dict[str, Any]]:
    """Choose spelling within each key, preserving the decoder's lexical order/scores.

    Scores are comparable ONLY among variants of the same key. This deliberately
    avoids treating transformer logits as evidence for existing swipe top-1 guards.
    First place belongs to the top decoder key's preferred surface. Its alternates
    follow; other keys' preferred surfaces precede their own alternates.
    """
    if case_mode not in CASE_MODES:
        raise ValueError("unsupported case mode")
    scores = scores or {}
    ranked = []
    for group in groups:
        lang, surface_key = group["languageCode"], group["surfaceKey"]
        variants = sorted(enumerate(group["variants"]), key=lambda item: (
            -scores.get((lang, surface_key, item[1]), 0.0),
            item[1] != group["defaultSurface"], item[0]))
        ranked.append([{**{k: group[k] for k in ("languageCode", "surfaceKey", "engineScore", "decoderIndex")},
                        "variantSurface": surface, "surface": display(surface, case_mode),
                        "variantScore": scores.get((lang, surface_key, surface))}
                       for _, surface in variants])
    if not ranked:
        return []
    ordered = ranked[0] + [row[0] for row in ranked[1:]] + [item for row in ranked[1:] for item in row[1:]]
    seen = set()
    out = []
    for row in ordered:
        identity = (row["languageCode"], row["surface"])
        if identity not in seen:
            seen.add(identity)
            out.append(row)
    return out


def evaluate(cases_document: dict[str, Any], request: dict[str, Any],
             predictions: dict[str, Any] | None = None) -> dict[str, Any]:
    evidence = validate_predictions(predictions, request) if predictions else {}
    cases = {case["id"]: case for case in cases_document["cases"]}
    rows = []
    for item in request["requests"]:
        case_id, window = item["requestId"].rsplit("/", 1)
        expected = cases[case_id]["expected"]
        suggestions = resolve(item["candidates"], evidence.get(item["requestId"]), item["caseMode"])
        top = suggestions[0] if suggestions else None
        expected_identity = (expected["languageCode"], expected["surfaceKey"])
        available = {(g["languageCode"], g["surfaceKey"]) for g in item["candidates"]}
        lexical_correct = bool(top and (top["languageCode"], top["surfaceKey"]) == expected_identity)
        rows.append({"caseId": case_id, "window": window, "context": item["context"],
                     "expectedKeyReachable": expected_identity in available,
                     "lexicalTop1Correct": lexical_correct,
                     "displayTop1Correct": bool(lexical_correct and top["surface"] == expected["surface"]),
                     "expectedSurfaceReachable": any((s["languageCode"], s["surfaceKey"]) == expected_identity
                                                     and s["surface"] == expected["surface"] for s in suggestions),
                     "suggestions": suggestions})
    metrics = {}
    for window in ("two_words", "long"):
        subset = [r for r in rows if r["window"] == window]
        metrics[window] = {"cases": len(subset), **{
            field: sum(row[field] for row in subset)
            for field in ("expectedKeyReachable", "lexicalTop1Correct", "displayTop1Correct", "expectedSurfaceReachable")}}
    return {"schemaVersion": 1, "requestSha256": request["requestSha256"],
            "fixtureKind": cases_document.get("fixtureKind", "unspecified"),
            "source": predictions["source"] if predictions else {"kind": "neutral_baseline"},
            "lexicalRankingChanged": False, "metrics": metrics, "rows": rows}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "evaluate"))
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--sidecar", type=Path, required=True)
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--max-words", type=int, default=64)
    parser.add_argument("--max-chars", type=int, default=4096)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare" and args.predictions:
        parser.error("prepare does not consume predictions")
    cases, sidecar = read_json(args.cases), read_json(args.sidecar)
    request = prepare(cases, sidecar, args.max_words, args.max_chars)
    output = request if args.command == "prepare" else evaluate(
        cases, request, read_json(args.predictions) if args.predictions else None)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(output))
    print(json.dumps({"output": str(args.output), "sha256": digest(output),
                      "metrics": output.get("metrics")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
