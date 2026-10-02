#!/usr/bin/env python3
"""Frozen offline plT5 denoising-span scorer; no training or lexical reranking."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import time
from pathlib import Path

from prototype import canonical_bytes, digest, validate_predictions

MODEL_ID = "allegro/plt5-small"
MODEL_REVISION = "6ab71258c53f77f075fdda380992c0e691703f6b"
ADAPTER_VERSION = "plt5-span-logprob-v1"
MAX_INPUT_TOKENS = 512  # experiment budget, not a claimed architecture maximum


def check_request(document):
    payload = {k: v for k, v in document.items() if k != "requestSha256"}
    if document.get("schemaVersion") != 1 or digest(payload) != document.get("requestSha256"):
        raise ValueError("request schema or hash mismatch")
    if any("expected" in row for row in document["requests"]):
        raise ValueError("gold labels must not enter inference")


def bounded_input(ids, sentinel_id, eos_id, limit=MAX_INPUT_TOKENS):
    if type(limit) is not int or limit < 3:
        raise ValueError("token budget must leave space for a context token and suffix")
    if ids[-2:] != [sentinel_id, eos_id]:
        raise ValueError("input must end with exactly the mask sentinel and EOS")
    return ids[-limit:], len(ids) > limit


def checked_target(ids, sentinel0, sentinel1, unk_id):
    if len(ids) < 3 or ids[0] != sentinel0 or ids[-1] != sentinel1:
        raise ValueError("target must contain a nonempty sentinel-delimited variant")
    if unk_id in ids or sentinel0 in ids[1:] or sentinel1 in ids[:-1]:
        raise ValueError("unrepresentable variant or injected sentinel")
    return ids


def run(request):
    check_request(request)
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    torch.set_num_threads(2)
    started = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID, revision=MODEL_REVISION, use_fast=False, trust_remote_code=False)
    model, loading_info = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_ID, revision=MODEL_REVISION, trust_remote_code=False,
        use_safetensors=False, output_loading_info=True)
    for field in ("missing_keys", "unexpected_keys", "mismatched_keys", "error_msgs"):
        if loading_info.get(field):
            raise ValueError(f"incomplete pretrained model: {field}: {loading_info[field]}")
    if model.config._commit_hash != MODEL_REVISION:
        raise ValueError("loaded model revision differs from the pinned revision")
    model.eval()
    load_seconds = time.perf_counter() - started
    s0 = tokenizer.convert_tokens_to_ids("<extra_id_0>")
    s1 = tokenizer.convert_tokens_to_ids("<extra_id_1>")
    if s0 == s1 or tokenizer.unk_token_id in (s0, s1):
        raise ValueError("tokenizer has no distinct mask sentinels")
    results, measurements, tokenization = [], [], {}
    for row in request["requests"]:
        began = time.perf_counter()
        context = row["context"]["text"]
        # The model sees only this exact left context and a masked continuation.
        if "<extra_id_" in context:
            raise ValueError("literal sentinel syntax in context is unsupported")
        full_ids = tokenizer.encode(context + "<extra_id_0>", add_special_tokens=True)
        input_ids, truncated = bounded_input(full_ids, s0, tokenizer.eos_token_id)
        scores = []
        decision_groups = 0
        # Without context, preserve dictionary defaults rather than a model prior.
        for group in row["candidates"] if context.strip() else []:
            if len(group["variants"]) < 2:
                continue
            targets = []
            for surface in group["variants"]:
                ids = tokenizer.encode(f"<extra_id_0> {surface} <extra_id_1>",
                                       add_special_tokens=False)
                checked_target(ids, s0, s1, tokenizer.unk_token_id)
                if ids in targets:
                    raise ValueError("distinct surface variants collapse to the same token IDs")
                targets.append(ids)
                tokenization[surface] = {"targetIds": ids,
                                         "tokens": tokenizer.convert_ids_to_tokens(ids)}
            decision_groups += 1
            labels = torch.full((len(targets), max(map(len, targets))), -100, dtype=torch.long)
            for index, ids in enumerate(targets):
                labels[index, :len(ids)] = torch.tensor(ids)
            inputs = torch.tensor([input_ids] * len(targets))
            with torch.inference_mode():
                logits = model(input_ids=inputs, attention_mask=torch.ones_like(inputs),
                               labels=labels).logits
                log_probs = torch.log_softmax(logits, dim=-1)
                for index, (surface, ids) in enumerate(zip(group["variants"], targets)):
                    # Exclude sentinel0 (identical conditioning prefix). Include
                    # all surface tokens AND sentinel1, the end-of-span decision.
                    score = sum(log_probs[index, pos, token].item()
                                for pos, token in enumerate(ids) if pos > 0)
                    scores.append({"languageCode": group["languageCode"],
                                   "surfaceKey": group["surfaceKey"],
                                   "surface": surface, "score": score})
        results.append({"requestId": row["requestId"], "variantScores": scores})
        measurements.append({"requestId": row["requestId"],
                             "inputTokensBeforeBudget": len(full_ids),
                             "inputTokens": len(input_ids), "tokenTruncated": truncated,
                             "decisionGroups": decision_groups,
                             "seconds": time.perf_counter() - began})
        print(f"scored {row['requestId']}: {len(scores)} variants", flush=True)
    output = {"schemaVersion": 1, "requestSha256": request["requestSha256"],
              "source": {"kind": "model", "name": MODEL_ID,
                         "revision": MODEL_REVISION + "/" + ADAPTER_VERSION},
              "protocol": {"adapterVersion": ADAPTER_VERSION,
                           "adapterFileSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                           "score": "sum log P(surface tokens and sentinel1 | left context, sentinel0)",
                           "lengthNormalization": False, "emptyContext": "dictionary_default",
                           "maxInputTokens": MAX_INPUT_TOKENS, "truncationSide": "left",
                           "device": "cpu", "threads": 2, "dtype": "float32"},
              "environment": {"python": platform.python_version(),
                              **{name: importlib.metadata.version(name)
                                 for name in ("torch", "transformers", "sentencepiece", "numpy")}},
              "model": {"parameters": sum(p.numel() for p in model.parameters()),
                        "loadSecondsIncludingDownload": load_seconds},
              "tokenization": tokenization, "measurements": measurements, "results": results}
    validate_predictions(output, request)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requests", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(json.loads(args.requests.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(result))


if __name__ == "__main__":
    main()
