#!/usr/bin/env python3
"""Frozen whole-word-mask scorer for existing surfaces; no lexical reranking."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import time
from pathlib import Path

from prototype import canonical_bytes, validate_predictions
from plt5_adapter import check_request

MODEL_ID = "sdadas/polish-roberta-base-v2"
MODEL_REVISION = "4a0bda6ba39e467e204c913cd642700544fc4d3a"
ADAPTER_VERSION = "roberta-whole-word-mask-v1"
MAX_INPUT_TOKENS = 512


def shared_context_suffix(context_ids, variant_lengths, budget=MAX_INPUT_TOKENS):
    """Every variant of a key gets exactly the same suffix of left context."""
    if not variant_lengths or min(variant_lengths) < 1:
        raise ValueError("variants must have at least one token")
    capacity = budget - 2 - max(variant_lengths)  # BOS, EOS and variant masks
    if capacity < 1:
        raise ValueError("variant exhausts context budget")
    return context_ids[-capacity:], len(context_ids) > capacity


def run(request):
    check_request(request)
    import torch
    from transformers import AutoModelForMaskedLM, AutoTokenizer

    torch.set_num_threads(2)
    began = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID, revision=MODEL_REVISION, use_fast=True, trust_remote_code=False)
    model, info = AutoModelForMaskedLM.from_pretrained(
        MODEL_ID, revision=MODEL_REVISION, use_safetensors=True,
        trust_remote_code=False, output_loading_info=True)
    for field in ("missing_keys", "unexpected_keys", "mismatched_keys", "error_msgs"):
        if info.get(field):
            raise ValueError(f"incomplete pretrained MLM: {field}: {info[field]}")
    if model.config._commit_hash != MODEL_REVISION or tokenizer.mask_token_id is None:
        raise ValueError("model revision or mask-token contract mismatch")
    if tokenizer.num_special_tokens_to_add(pair=False) != 2:
        raise ValueError("this protocol requires exactly BOS and EOS")
    model.eval()
    load_seconds = time.perf_counter() - began
    results, measurements, inventory = [], [], {}
    for row in request["requests"]:
        began = time.perf_counter()
        context = row["context"]["text"]
        context_ids = tokenizer.encode(context, add_special_tokens=False)
        if any(i in tokenizer.all_special_ids for i in context_ids):
            raise ValueError("literal model special token in context is unsupported")
        scores, details = [], []
        for group in row["candidates"] if context.strip() else []:
            if len(group["variants"]) < 2:
                continue
            targets = [tokenizer.encode(s, add_special_tokens=False) for s in group["variants"]]
            if len({tuple(ids) for ids in targets}) != len(targets):
                raise ValueError("distinct variants collapse to the same token IDs")
            if any(i in tokenizer.all_special_ids for ids in targets for i in ids):
                raise ValueError("variant contains unknown or special tokens")
            suffix, truncated = shared_context_suffix(context_ids, list(map(len, targets)))
            inputs = [tokenizer.build_inputs_with_special_tokens(
                suffix + [tokenizer.mask_token_id] * len(ids)) for ids in targets]
            padded = torch.full((len(inputs), max(map(len, inputs))),
                                tokenizer.pad_token_id, dtype=torch.long)
            attention = torch.zeros_like(padded)
            for index, ids in enumerate(inputs):
                padded[index, :len(ids)] = torch.tensor(ids)
                attention[index, :len(ids)] = 1
            with torch.inference_mode():
                logits = model(input_ids=padded, attention_mask=attention).logits
                log_probs = torch.log_softmax(logits, dim=-1)
                for index, (surface, ids) in enumerate(zip(group["variants"], targets)):
                    positions = [p for p, token in enumerate(inputs[index])
                                 if token == tokenizer.mask_token_id]
                    if len(positions) != len(ids):
                        raise ValueError("mask positions differ from variant length")
                    # All subword positions are masked simultaneously. This sum
                    # is a compatibility score, NOT a joint word probability.
                    score = sum(log_probs[index, pos, token].item()
                                for pos, token in zip(positions, ids))
                    scores.append({"languageCode": group["languageCode"],
                                   "surfaceKey": group["surfaceKey"],
                                   "surface": surface, "score": score})
                    inventory[surface] = {"ids": ids, "tokens": tokenizer.convert_ids_to_tokens(ids)}
            details.append({"languageCode": group["languageCode"], "surfaceKey": group["surfaceKey"],
                            "contextTokens": len(suffix), "tokenTruncated": truncated,
                            "variantTokens": list(map(len, targets)),
                            "maxInputTokens": max(map(len, inputs))})
        results.append({"requestId": row["requestId"], "variantScores": scores})
        measurements.append({"requestId": row["requestId"], "contextTokensBeforeBudget": len(context_ids),
                             "groups": details, "seconds": time.perf_counter() - began})
        print(f"scored {row['requestId']}: {len(scores)} variants", flush=True)
    output = {"schemaVersion": 1, "requestSha256": request["requestSha256"],
              "source": {"kind": "model", "name": MODEL_ID,
                         "revision": MODEL_REVISION + "/" + ADAPTER_VERSION},
              "protocol": {"adapterVersion": ADAPTER_VERSION,
                           "adapterFileSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                           "score": "sum masked-position token log probabilities; all variant tokens masked",
                           "lengthNormalization": False, "emptyContext": "dictionary_default",
                           "maxInputTokens": MAX_INPUT_TOKENS, "truncationSide": "left",
                           "device": "cpu", "threads": 2, "dtype": "float32"},
              "environment": {"python": platform.python_version(),
                              **{name: importlib.metadata.version(name)
                                 for name in ("torch", "transformers", "tokenizers", "numpy")}},
              "model": {"parameters": sum(p.numel() for p in model.parameters()),
                        "loadSecondsIncludingDownload": load_seconds},
              "tokenization": inventory, "measurements": measurements, "results": results}
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
