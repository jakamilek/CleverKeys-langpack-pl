#!/usr/bin/env python3
"""Isolated sense-to-surface experiment using a frozen pretrained NLI model.

No training, lexical reranking, Android integration or production schema change.
Gold labels are consumed only by evaluate(), never by infer().
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
import time
from pathlib import Path

from prototype import (canonical_bytes, digest, load_sidecar, prepare, resolve,
                       validate_predictions)
from plt5_adapter import check_request

ROOT = Path(__file__).parent
MODEL_ID = "MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli"
MODEL_REVISION = "0a71e92a985b6e1ad1828cf67ce9c459639c1dca"
VERSION = "sense-surface-nli-v1"
CONDITIONS = ("attributes", "no_attributes", "swapped_attributes")
MAIN = {"direct", "previous", "distant_retained", "conflicting"}
SENSES = {
    "łódź": (("boat", "common_noun", "jednostkę pływającą"),
             ("city", "proper_name", "miasto")),
    "malina": (("raspberry", "common_noun", "owoc maliny"),
               ("surname", "proper_name", "nazwisko osoby")),
    "jagoda": (("berry", "common_noun", "owoc jagody"),
               ("given_name", "proper_name", "imię osoby")),
    "róża": (("rose", "common_noun", "kwiat róży"),
             ("given_name", "proper_name", "imię osoby")),
}


def build_fixture():
    cases = json.loads((ROOT / "diagnostic-cases.json").read_text(encoding="utf-8"))
    sidecar = json.loads((ROOT / "diagnostic-sidecar.json").read_text(encoding="utf-8"))
    sidecar["experimentExtension"] = VERSION
    for entry in sidecar["entries"]:
        meanings = SENSES[entry["surfaceKey"]]
        entry["senses"] = [{"id": sid, "kind": kind, "descriptionPl": description}
                           for sid, kind, description in meanings]
        for variant, (sid, _, _) in zip(entry["capitalization"]["variants"], meanings):
            variant["senseIds"] = [sid]
    # A separate, deliberately adverse synthetic slate: the correct key is #2.
    # The first key has two variants, so the target's preferred form is #3 and
    # its alternative is #4. These repeat contexts, not independent quality data.
    originals = list(cases["cases"])
    keys = list(SENSES)
    for case in originals:
        if case["diagnostic"]["category"] not in MAIN:
            continue
        probe = copy.deepcopy(case)
        target = case["expected"]["surfaceKey"]
        distractor = keys[(keys.index(target) + 1) % len(keys)]
        probe["id"] = "probe" + case["id"][4:]
        probe["candidates"] = [{"surface": distractor, "engineScore": 700},
                               {"surface": target, "engineScore": 650}]
        probe["diagnostic"] = {"category": "top3_probe", "sourceId": case["id"],
                               "sourceCategory": case["diagnostic"]["category"]}
        cases["cases"].append(probe)
    cases["fixtureKind"] = "constructed_sense_diagnostic_with_repeated_top3_probes"
    return cases, sidecar


def validate_senses(sidecar):
    _, entries = load_sidecar(sidecar)
    if sidecar.get("experimentExtension") != VERSION:
        raise ValueError("experimental sense extension must be explicit")
    for entry in entries.values():
        senses = entry.get("senses")
        if not isinstance(senses, list) or not senses:
            raise ValueError("sense inventory required")
        ids = set()
        for sense in senses:
            if not isinstance(sense, dict):
                raise ValueError("sense must be an object")
            sid, description = sense.get("id"), sense.get("descriptionPl")
            if not isinstance(sid, str) or not sid.strip() or sid in ids:
                raise ValueError("sense id must be nonblank and unique within key")
            if not isinstance(description, str) or not description.strip():
                raise ValueError("sense description required")
            if sense.get("kind") not in {"common_noun", "proper_name"}:
                raise ValueError("unsupported experimental sense kind")
            ids.add(sid)
        referenced = set()
        for variant in entry["capitalization"]["variants"]:
            refs = variant.get("senseIds")
            if not isinstance(refs, list) or not refs or any(not isinstance(r, str) for r in refs):
                raise ValueError("variant requires sense ids")
            if len(set(refs)) != len(refs) or not set(refs) <= ids:
                raise ValueError("duplicate or dangling sense association")
            referenced.update(refs)
        if referenced != ids:
            raise ValueError("unassociated sense")
    return entries


def prepare_senses(cases, sidecar):
    entries = validate_senses(sidecar)
    request = prepare(cases, sidecar)
    for row in request["requests"]:
        for group in row["candidates"]:
            entry = entries.get(group["surfaceKey"]) if group["languageCode"] == sidecar["languageCode"] else None
            if entry:
                group["senses"] = copy.deepcopy(entry["senses"])
                group["variantSenseIds"] = {v["surface"]: list(v["senseIds"])
                                           for v in entry["capitalization"]["variants"]}
    request["experimentExtension"] = VERSION
    del request["requestSha256"]
    request["requestSha256"] = digest(request)
    return request


def hypotheses(group, condition):
    if condition not in CONDITIONS:
        raise ValueError("unknown condition")
    variants = group["variants"]
    if condition == "no_attributes":
        return {surface: [f'W tym kontekście poprawną pisownią dopisywanego słowa jest „{surface}”.']
                for surface in variants}
    associations = group["variantSenseIds"]
    senses = {s["id"]: s["descriptionPl"] for s in group["senses"]}
    if condition == "swapped_attributes":
        if len(variants) != 2:
            raise ValueError("swap control requires exactly two variants")
        associations = {variants[0]: associations[variants[1]], variants[1]: associations[variants[0]]}
    return {surface: [f'W tym kontekście słowo „{group["surfaceKey"]}” oznacza {senses[sid]}.'
                      for sid in associations[surface]] for surface in variants}


def budget_pairs(context, group, tokenizer, max_tokens=512):
    # All three conditions receive the SAME context suffix for this key. The
    # candidate is lowercase in the premise, so it cannot reveal selected case.
    premise = context + ("" if not context or context[-1].isspace() else " ") + group["surfaceKey"]
    premise_ids = tokenizer.encode(premise, add_special_tokens=False)
    encoded = {}
    for condition in CONDITIONS:
        for surface, texts in hypotheses(group, condition).items():
            encoded[condition, surface] = [tokenizer.encode(t, add_special_tokens=False) for t in texts]
    all_hypotheses = [ids for rows in encoded.values() for ids in rows]
    if any(tokenizer.unk_token_id in ids for ids in [premise_ids] + all_hypotheses):
        raise ValueError("unknown token in premise/hypothesis")
    budget = max_tokens - tokenizer.num_special_tokens_to_add(pair=True) - max(map(len, all_hypotheses))
    if budget < 1:
        raise ValueError("hypothesis exceeds token budget")
    suffix = premise_ids[-budget:]
    pairs = {identity: [tokenizer.build_inputs_with_special_tokens(suffix, ids) for ids in rows]
             for identity, rows in encoded.items()}
    if any(len(ids) > max_tokens for rows in pairs.values() for ids in rows):
        raise ValueError("pair budget failure")
    return pairs, {"premiseTokensBeforeBudget": len(premise_ids), "premiseTokens": len(suffix),
                   "tokenTruncated": len(suffix) != len(premise_ids),
                   "premiseTokenSha256": digest(suffix)}


def preflight():
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    torch.set_num_threads(2)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION,
                                             local_files_only=True, trust_remote_code=False)
    model, info = AutoModelForSequenceClassification.from_pretrained(
        MODEL_ID, revision=MODEL_REVISION, local_files_only=True, trust_remote_code=False,
        use_safetensors=True, output_loading_info=True)
    for field in ("missing_keys", "unexpected_keys", "mismatched_keys", "error_msgs"):
        if info.get(field):
            raise ValueError(f"incomplete/unexplained weights: {field}: {info[field]}")
    if model.config._commit_hash != MODEL_REVISION:
        raise ValueError("model revision mismatch")
    if model.config.id2label != {0: "entailment", 1: "neutral", 2: "contradiction"}:
        raise ValueError("NLI label mapping mismatch")
    model.eval()
    # Structural loading check only; it does not measure or tune quality.
    inputs = tokenizer("To jest tekst po polsku.", "To jest tekst.", return_tensors="pt")
    with torch.inference_mode():
        logits = model(**inputs).logits
    if logits.shape != (1, 3) or not torch.isfinite(logits).all():
        raise ValueError("invalid NLI output")
    return model, tokenizer, torch, info


def infer(request, output_dir):
    # Validate request integrity without touching labels/cases.
    check_request(request)
    model, tokenizer, torch, info = preflight()
    cache, trace = {}, []
    results = {condition: [] for condition in CONDITIONS}
    began = time.perf_counter()
    for index, row in enumerate(request["requests"]):
        scores = {condition: [] for condition in CONDITIONS}
        for group in row["candidates"]:
            if not group.get("senses") or len(group["variants"]) < 2:
                continue
            pairs, detail = budget_pairs(row["context"]["text"], group, tokenizer)
            # Deduplicate identical pair inputs (including the swapped control).
            missing = list(dict.fromkeys(tuple(ids) for rows in pairs.values()
                                        for ids in rows if tuple(ids) not in cache))
            for start in range(0, len(missing), 8):
                batch = missing[start:start + 8]
                inputs = torch.full((len(batch), max(map(len, batch))), tokenizer.pad_token_id,
                                    dtype=torch.long)
                attention = torch.zeros_like(inputs)
                for i, ids in enumerate(batch):
                    inputs[i, :len(ids)] = torch.tensor(ids)
                    attention[i, :len(ids)] = 1
                with torch.inference_mode():
                    logits = model(input_ids=inputs, attention_mask=attention).logits
                    probabilities = torch.log_softmax(logits, dim=-1)
                if not torch.isfinite(probabilities).all():
                    raise ValueError("nonfinite NLI score")
                for i, ids in enumerate(batch):
                    cache[ids] = probabilities[i].tolist()
            for (condition, surface), inputs in pairs.items():
                value = max(cache[tuple(ids)][0] for ids in inputs)
                scores[condition].append({"languageCode": group["languageCode"],
                                          "surfaceKey": group["surfaceKey"],
                                          "surface": surface, "score": value})
            trace.append({"requestId": row["requestId"], "surfaceKey": group["surfaceKey"], **detail})
        for condition in CONDITIONS:
            results[condition].append({"requestId": row["requestId"], "variantScores": scores[condition]})
        if index % 16 == 0:
            print(f"NLI {index + 1}/{len(request['requests'])}", flush=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    for condition, rows in results.items():
        prediction = {"schemaVersion": 1, "requestSha256": request["requestSha256"],
                      "source": {"kind": "model", "name": MODEL_ID,
                                 "revision": MODEL_REVISION + "/" + VERSION + "/" + condition},
                      "condition": condition, "results": rows}
        validate_predictions(prediction, request)
        (output_dir / f"nli-{condition}.json").write_bytes(canonical_bytes(prediction))
    metadata = {"modelId": MODEL_ID, "modelRevision": MODEL_REVISION, "loadingInfo": info,
                "parameters": sum(p.numel() for p in model.parameters()),
                "requestSha256": request["requestSha256"],
                "runnerSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "device": "cpu", "dtype": "float32", "threads": 2, "batchSize": 8,
                "uniquePairs": len(cache), "inferenceSeconds": time.perf_counter() - began,
                "timingIsPhoneBenchmark": False,
                "environment": {n: importlib.metadata.version(n) for n in
                                ("torch", "transformers", "tokenizers", "numpy", "safetensors")},
                "trace": trace}
    (output_dir / "nli-metadata.json").write_bytes(canonical_bytes(metadata))


def evaluate(cases, request, predictions=None):
    evidence = validate_predictions(predictions, request) if predictions else {}
    by_id = {case["id"]: case for case in cases["cases"]}
    rows = []
    for row in request["requests"]:
        cid, window = row["requestId"].rsplit("/", 1)
        case = by_id[cid]
        suggestions = resolve(row["candidates"], evidence.get(row["requestId"]), row["caseMode"])
        expected = case.get("expected")
        rank = None
        if expected:
            rank = next((i + 1 for i, s in enumerate(suggestions)
                         if (s["languageCode"], s["surfaceKey"], s["surface"]) ==
                         (expected["languageCode"], expected["surfaceKey"], expected["surface"])), None)
        rows.append({"caseId": cid, "window": window,
                     "category": case["diagnostic"]["category"],
                     "expected": expected, "expectedRank": rank,
                     "displayTop1Correct": rank == 1 if expected else None,
                     "displayTop3Correct": rank is not None and rank <= 3 if expected else None,
                     "expectedSurfaceReachable": rank is not None if expected else None,
                     "suggestions": suggestions})
    metrics = {}
    for window in ("two_words", "long"):
        subset = [r for r in rows if r["window"] == window]
        metrics[window] = {}
        sections = {"main": [r for r in subset if r["category"] in MAIN],
                    **{cat: [r for r in subset if r["category"] == cat]
                       for cat in sorted({r["category"] for r in subset})}}
        for section, items in sections.items():
            labelled = all(r["expected"] is not None for r in items)
            metrics[window][section] = {"cases": len(items), **{
                field: sum(r[field] for r in items) if labelled else None
                for field in ("displayTop1Correct", "displayTop3Correct", "expectedSurfaceReachable")}}
    return {"schemaVersion": 1, "requestSha256": request["requestSha256"],
            "source": predictions["source"] if predictions else {"kind": "neutral_baseline"},
            "primaryMetric": "displayTop3Correct", "lexicalRankingChanged": False,
            "metrics": metrics, "rows": rows}


def archived_prediction(request, archived, cases):
    """Replay old target scores unchanged; distractor spelling stays neutral.

    Not a new model inference. Contexts, target keys and surfaces are validated
    against the archived request. Unscored competitors are explicitly disclosed.
    """
    old_request = json.loads((ROOT / "diagnostic-requests.json").read_text(encoding="utf-8"))
    old_scores = validate_predictions(archived, old_request)
    old_rows = {r["requestId"]: r for r in old_request["requests"]}
    by_id = {c["id"]: c for c in cases["cases"]}
    rows = []
    for row in request["requests"]:
        cid, window = row["requestId"].rsplit("/", 1)
        source_id = by_id[cid]["diagnostic"].get("sourceId", cid)
        old_id = source_id + "/" + window
        old_row = old_rows[old_id]
        if canonical_bytes(row["context"]) != canonical_bytes(old_row["context"]):
            raise ValueError("archived context differs")
        target = old_row["candidates"][0]
        group = next(g for g in row["candidates"] if g["surfaceKey"] == target["surfaceKey"])
        if group["variants"] != target["variants"] or group["languageCode"] != target["languageCode"]:
            raise ValueError("archived target differs")
        rows.append({"requestId": row["requestId"], "variantScores": [
            {"languageCode": lang, "surfaceKey": key, "surface": surface, "score": value}
            for (lang, key, surface), value in old_scores[old_id].items()]})
    output = {"schemaVersion": 1, "requestSha256": request["requestSha256"],
              "source": {**archived["source"], "name": archived["source"]["name"] + " (archived target replay)"},
              "archivedRequestSha256": old_request["requestSha256"],
              "unscoredCompetitorsUseNeutralDefault": True, "results": rows}
    validate_predictions(output, request)
    return output


def evaluate_all(cases, request, output_dir):
    systems = {"neutral": evaluate(cases, request)}
    for condition in CONDITIONS:
        prediction = json.loads((output_dir / f"nli-{condition}.json").read_text(encoding="utf-8"))
        systems["nli-" + condition] = evaluate(cases, request, prediction)
    for model in ("polbert", "herbert"):
        for method in ("wwm", "pll_variant", "pll_full_mean"):
            name = model + "-" + method
            archived = json.loads((ROOT / "diagnostic-results-2026-10-02" /
                                   f"diagnostic-{name}.json").read_text(encoding="utf-8"))
            prediction = archived_prediction(request, archived, cases)
            (output_dir / f"replay-{name}.json").write_bytes(canonical_bytes(prediction))
            systems[name] = evaluate(cases, request, prediction)
    summary = {"schemaVersion": 1, "requestSha256": request["requestSha256"],
               "primaryMetric": "displayTop3Correct", "fixtureKind": cases["fixtureKind"],
               "systems": {name: system["metrics"] for name, system in systems.items()}}
    for name, system in systems.items():
        (output_dir / f"decisions-{name}.json").write_bytes(canonical_bytes(system))
    # Swapping descriptors reassigns identical scores to the opposite surface:
    # it is a mechanical mapping check, not independent proof of comprehension.
    intact = {r["caseId"] + "/" + r["window"]: r for r in systems["nli-attributes"]["rows"]}
    swapped = systems["nli-swapped_attributes"]["rows"]
    summary["swapControl"] = {window: {"mainCases": 32, "changedPreferredTarget": sum(
        next(s["surface"] for s in r["suggestions"] if s["surfaceKey"] == r["expected"]["surfaceKey"]) !=
        next(s["surface"] for s in intact[r["caseId"] + "/" + r["window"]]["suggestions"]
             if s["surfaceKey"] == r["expected"]["surfaceKey"])
        for r in swapped if r["window"] == window and r["category"] in MAIN)}
        for window in ("two_words", "long")}
    (output_dir / "summary.json").write_bytes(canonical_bytes(summary))
    print(json.dumps({name: data["long"] for name, data in summary["systems"].items()},
                     ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "preflight", "infer", "evaluate"))
    parser.add_argument("--output-dir", type=Path, default=ROOT / "sense-results-2026-10-02")
    args = parser.parse_args()
    if args.command == "preflight":
        model, tokenizer, _, info = preflight()
        print(json.dumps({"modelId": MODEL_ID, "revision": MODEL_REVISION,
                          "parameters": sum(p.numel() for p in model.parameters()),
                          "loadingInfo": info, "labels": model.config.id2label,
                          "polishTokens": tokenizer.tokenize("łódź Łódź róża Róża")}, ensure_ascii=False))
        return
    if args.command == "prepare":
        cases, sidecar = build_fixture()
        request = prepare_senses(cases, sidecar)
        for name, document in (("sense-cases.json", cases), ("sense-sidecar.json", sidecar),
                               ("sense-requests.json", request)):
            (ROOT / name).write_bytes(canonical_bytes(document))
        print(json.dumps({"cases": len(cases["cases"]), "requests": len(request["requests"]),
                          "requestSha256": request["requestSha256"]}))
        return
    request = json.loads((ROOT / "sense-requests.json").read_text(encoding="utf-8"))
    if args.command == "infer":
        infer(request, args.output_dir)
    else:
        cases = json.loads((ROOT / "sense-cases.json").read_text(encoding="utf-8"))
        evaluate_all(cases, request, args.output_dir)


if __name__ == "__main__":
    main()
