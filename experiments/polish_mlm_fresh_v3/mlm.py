"""Whole appended span, original vocabulary softmax, full-head parity. No random head."""
import math


def target_positions(text, start, offsets):
    positions = []
    for i, (begin, end) in enumerate(offsets):
        if end <= start or begin == end:
            continue
        if begin < start and text[begin:start].strip():
            raise ValueError('token crosses non-whitespace target boundary')
        if begin >= len(text) or end > len(text):
            raise ValueError('invalid tokenizer offset')
        positions.append(i)
    if not positions or positions != list(range(positions[0], positions[-1] + 1)):
        raise ValueError('empty/discontiguous target')
    return positions


def encode(context, surface, tokenizer):
    text = context + ' ' + surface
    start = len(context) + 1
    encoding = tokenizer(text, add_special_tokens=True, return_offsets_mapping=True,
                         return_special_tokens_mask=True, truncation=False)
    ids = list(encoding['input_ids'])
    positions = target_positions(text, start, encoding['offset_mapping'])
    if len(ids) > 512 or any(encoding['special_tokens_mask'][p] for p in positions):
        raise ValueError('unsupported target/budget')
    target = [ids[p] for p in positions]
    if any(x == tokenizer.unk_token_id for x in target):
        raise ValueError('unknown target token')
    for p in positions:
        ids[p] = tokenizer.mask_token_id
    return {'ids': ids, 'positions': positions, 'target': target}


def tensors(encoded, tokenizer, torch):
    length = max(len(e['ids']) for e in encoded)
    ids = torch.full((len(encoded), length), tokenizer.pad_token_id, dtype=torch.long)
    attention = torch.zeros_like(ids)
    for i, e in enumerate(encoded):
        ids[i, :len(e['ids'])] = torch.tensor(e['ids'])
        attention[i, :len(e['ids'])] = 1
    return ids, attention


def base_and_head(model, architecture):
    if architecture == 'bert':
        return model.bert, model.cls.predictions
    if architecture == 'roberta':
        return model.roberta, model.lm_head
    raise ValueError('unsupported pretrained architecture')


def score(encoded, model, tokenizer, architecture, torch):
    ids, attention = tensors(encoded, tokenizer, torch)
    base, head = base_and_head(model, architecture)
    with torch.inference_mode():
        hidden = base(input_ids=ids, attention_mask=attention).last_hidden_state
        batches, positions, targets = [], [], []
        for i, e in enumerate(encoded):
            batches.extend([i] * len(e['target']))
            positions.extend(e['positions'])
            targets.extend(e['target'])
        # Full vocabulary normalization only at all selected target positions.
        logits = head(hidden[batches, positions, :])
        values = torch.log_softmax(logits.float(), dim=-1)[torch.arange(len(targets)), targets].tolist()
    scores, traces, cursor = [], [], 0
    for e in encoded:
        total = sum(values[cursor:cursor + len(e['target'])])
        mean = total / len(e['target'])
        if not math.isfinite(mean):
            raise ValueError('nonfinite MLM output')
        scores.append(mean)
        traces.append({'targetTokenIds': e['target'], 'targetPositions': e['positions'],
                       'inputTokens': len(e['ids']), 'sumLogProbability': total, 'meanLogProbability': mean})
        cursor += len(e['target'])
    return scores, traces


def check_projection(encoded, model, tokenizer, architecture, torch):
    ids, attention = tensors(encoded, tokenizer, torch)
    base, head = base_and_head(model, architecture)
    with torch.inference_mode():
        original = model(input_ids=ids, attention_mask=attention).logits
        hidden = base(input_ids=ids, attention_mask=attention).last_hidden_state
        batch, pos = [], []
        for i, e in enumerate(encoded):
            batch.extend([i] * len(e['target']))
            pos.extend(e['positions'])
        selected = head(hidden[batch, pos, :])
        expected = original[batch, pos, :]
        error = (selected - expected).abs().max().item()
        if not torch.allclose(selected, expected, atol=1e-4, rtol=1e-5):
            raise ValueError('full pretrained head projection differs')
    return error
