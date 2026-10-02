#!/usr/bin/env python3
"""Frozen comparison of two pretrained MLMs and three surface scoring methods."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import time
from pathlib import Path

from mlm_adapter import shared_context_suffix
from plt5_adapter import check_request
from prototype import canonical_bytes, validate_predictions

PRESETS = {
    "polbert": {"id": "dkleczek/bert-base-polish-cased-v1",
                "revision": "fed744e81ebd16cf099b5c64c40688bc3e6ace67", "unused": set()},
    "herbert": {"id": "allegro/herbert-base-cased",
                "revision": "50e33e0567be0c0b313832314c586e3df0dc2297",
                "unused": {"bert.pooler.dense.bias", "bert.pooler.dense.weight",
                           "cls.sso.sso_relationship.bias", "cls.sso.sso_relationship.weight"}},
}
METHODS = ("wwm", "pll_variant", "pll_full_mean")
VERSION = "context-surface-diagnostic-v2"
BATCH_SIZE = 8


def masked_tasks(context_ids, target_ids, cls_id, sep_id, mask_id):
    """Mask every text position once; additionally mask the whole variant.

    Every task is (input IDs, positions to score, gold token IDs, contribution).
    Here 'gold' means the observed token being reconstructed, never eval labels.
    """
    sequence = [cls_id] + context_ids + target_ids + [sep_id]
    tasks = []
    for position in range(1, len(sequence) - 1):
        masked = sequence.copy()
        masked[position] = mask_id
        part = "context" if position <= len(context_ids) else "variant"
        tasks.append((masked, [position], [sequence[position]], part))
    if len(target_ids) > 1:
        positions = list(range(len(context_ids) + 1, len(sequence) - 1))
        masked = sequence.copy()
        for position in positions:
            masked[position] = mask_id
        tasks.append((masked, positions, target_ids, "wwm"))
    return tasks


def aggregate(contributions, context_count, target_count):
    context = sum(value for part, value in contributions if part == "context")
    variant = sum(value for part, value in contributions if part == "variant")
    wwm = variant if target_count == 1 else sum(value for part, value in contributions if part == "wwm")
    return {"wwm": wwm, "pll_variant": variant,
            "pll_full_mean": (context + variant) / (context_count + target_count)}, context


def score_tasks(model, tokenizer, tasks, torch):
    contributions = []
    for start in range(0, len(tasks), BATCH_SIZE):
        batch = tasks[start:start + BATCH_SIZE]
        inputs = torch.full((len(batch), max(len(t[0]) for t in batch)),
                            tokenizer.pad_token_id, dtype=torch.long)
        attention = torch.zeros_like(inputs)
        for i, task in enumerate(batch):
            inputs[i, :len(task[0])] = torch.tensor(task[0])
            attention[i, :len(task[0])] = 1
        with torch.inference_mode():
            output = model(input_ids=inputs, attention_mask=attention)
            logits = output.prediction_logits if hasattr(output, "prediction_logits") else output.logits
            for i, (_, positions, target_ids, part) in enumerate(batch):
                selected = torch.log_softmax(logits[i, positions, :], dim=-1)
                value = sum(selected[j, token].item() for j, token in enumerate(target_ids))
                contributions.append((part, value))
    return contributions


def load_model(preset):
    import torch
    from transformers import AutoModelForMaskedLM, AutoModelForPreTraining, AutoTokenizer
    torch.set_num_threads(2)
    tokenizer = AutoTokenizer.from_pretrained(preset["id"], revision=preset["revision"],
                                            use_fast=True, trust_remote_code=False)
    factory = AutoModelForPreTraining if preset["id"].startswith("dkleczek/") else AutoModelForMaskedLM
    model, info = factory.from_pretrained(preset["id"], revision=preset["revision"],
                                         use_safetensors=False, trust_remote_code=False,
                                         output_loading_info=True)
    for field in ("missing_keys", "mismatched_keys", "error_msgs"):
        if info.get(field):
            raise ValueError(f"untrained/incomplete head: {field}: {info[field]}")
    if set(info.get("unexpected_keys", [])) != preset["unused"]:
        raise ValueError(f"unexplained unused weights: {info}")
    if model.config._commit_hash != preset["revision"]:
        raise ValueError("model revision mismatch")
    if any(v is None for v in (tokenizer.cls_token_id, tokenizer.sep_token_id, tokenizer.mask_token_id)):
        raise ValueError("required special token missing")
    model.eval()
    return model, tokenizer, torch, info


def run_requests(request, model, tokenizer, torch, preset, info):
    check_request(request)
    results = {method: [] for method in METHODS}
    trace, inventory = [], {}
    for row in request["requests"]:
        began = time.perf_counter()
        context = row["context"]["text"]
        context_ids = tokenizer.encode(context, add_special_tokens=False)
        if any(i in tokenizer.all_special_ids for i in context_ids):
            raise ValueError("unknown/special token in context")
        scores, detail = {m: [] for m in METHODS}, []
        for group in row["candidates"] if context.strip() else []:
            if len(group["variants"]) < 2:
                continue
            targets = [tokenizer.encode(s, add_special_tokens=False) for s in group["variants"]]
            if len({tuple(ids) for ids in targets}) != len(targets):
                raise ValueError("variant tokenization collapsed")
            if any(i in tokenizer.all_special_ids for ids in targets for i in ids):
                raise ValueError("unknown/special token in variant")
            suffix, truncated = shared_context_suffix(context_ids, list(map(len, targets)))
            for surface, ids in zip(group["variants"], targets):
                tasks = masked_tasks(suffix, ids, tokenizer.cls_token_id,
                                     tokenizer.sep_token_id, tokenizer.mask_token_id)
                values, context_score = aggregate(score_tasks(model, tokenizer, tasks, torch), len(suffix), len(ids))
                for method, value in values.items():
                    scores[method].append({"languageCode": group["languageCode"],
                                          "surfaceKey": group["surfaceKey"], "surface": surface, "score": value})
                detail.append({"surfaceKey": group["surfaceKey"], "surface": surface,
                               "contextTokens": len(suffix), "variantTokens": len(ids),
                               "tokenTruncated": truncated, "contextPllSum": context_score})
                inventory[surface] = {"ids": ids, "tokens": tokenizer.convert_ids_to_tokens(ids)}
        for method in METHODS:
            results[method].append({"requestId": row["requestId"], "variantScores": scores[method]})
        trace.append({"requestId": row["requestId"], "contextTokensBeforeBudget": len(context_ids),
                      "groups": detail, "secondsAllMethods": time.perf_counter() - began})
        print(f"{preset['id']} {row['requestId']}", flush=True)
    outputs = {}
    for method in METHODS:
        outputs[method] = {"schemaVersion": 1, "requestSha256": request["requestSha256"],
                           "source": {"kind": "model", "name": preset["id"],
                                      "revision": preset["revision"] + "/" + VERSION + "/" + method},
                           "method": method, "results": results[method]}
        validate_predictions(outputs[method], request)
    metadata = {"schemaVersion": 1, "requestSha256": request["requestSha256"],
                "modelId": preset["id"], "modelRevision": preset["revision"],
                "runnerSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "loadingInfo": info, "parameters": sum(p.numel() for p in model.parameters()),
                "environment": {n: importlib.metadata.version(n) for n in
                                ("torch", "transformers", "tokenizers", "numpy", "sacremoses")},
                "device": "cpu", "threads": 2, "batchSize": BATCH_SIZE,
                "maxInputTokens": 512, "tokenization": inventory, "trace": trace}
    return outputs, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=PRESETS, required=True)
    parser.add_argument("--requests", type=Path, required=True)
    parser.add_argument("--legacy-requests", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    preset = PRESETS[args.model]
    model, tokenizer, torch, info = load_model(preset)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, path in (("diagnostic", args.requests), ("legacy", args.legacy_requests)):
        request = json.loads(path.read_text(encoding="utf-8"))
        outputs, metadata = run_requests(request, model, tokenizer, torch, preset, info)
        for method, result in outputs.items():
            (args.output_dir / f"{name}-{args.model}-{method}.json").write_bytes(canonical_bytes(result))
        (args.output_dir / f"{name}-{args.model}-metadata.json").write_bytes(canonical_bytes(metadata))


if __name__ == "__main__":
    main()
