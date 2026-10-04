"""Portable cased Char-BPE tables derived from the pinned fast tokenizer.

No Python Unicode categories: normalizer/pre-tokenizer behaviour is probed from
tokenizers 0.22.2 for every Unicode scalar and encoded as compact ranges.
The reference interpreter is an independent parity check, not a new vocabulary.
"""
import json
import random

VERSION = 'herbert-fp32-benchmark-v1'
FP32_SHA = 'f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2'
MODEL_BYTES = 651798883

def export_tables(tokenizer):
    backend = tokenizer.backend_tokenizer
    data = json.loads(backend.to_str())
    model = data['model']
    expected_normalizer = dict(type='BertNormalizer', clean_text=True,
                               handle_chinese_chars=True, strip_accents=False, lowercase=False)
    if data['normalizer'] != expected_normalizer or data['pre_tokenizer'] != {'type':'BertPreTokenizer'}:
        raise ValueError('unsupported normalizer or pre-tokenizer')
    if (model['type'] != 'BPE' or model.get('dropout') is not None or
        model.get('continuing_subword_prefix') not in (None, '') or
        model.get('end_of_word_suffix') != '</w>' or model.get('fuse_unk') is not False or
        model.get('byte_fallback') is not False or model.get('ignore_merges', False)):
        raise ValueError('unsupported BPE configuration')
    vocab = model['vocab']
    if len(vocab) != 50000 or set(vocab.values()) != set(range(50000)):
        raise ValueError('vocabulary differs')
    tokens = [''] * len(vocab)
    for token, token_id in vocab.items():
        tokens[token_id] = token
    added = data['added_tokens']
    if len(added) != 5 or {t['content'] for t in added} != {'<s>', '</s>', '<mask>', '<pad>', '<unk>'}:
        raise ValueError('unexpected added tokens')
    for t in added:
        if (not t['special'] or any(t[k] for k in ('single_word','lstrip','rstrip','normalized')) or
            vocab.get(t['content']) != t['id']):
            raise ValueError('unsupported added-token attributes')
    merges = []
    for pair in model['merges']:
        a, b = pair.split(' ') if isinstance(pair, str) else pair
        merges.append([vocab[a], vocab[b], vocab[a+b]])
    ranges = []
    start = last = flags = None
    for cp in range(0x110000):
        if 0xd800 <= cp <= 0xdfff:
            continue
        c = chr(cp)
        normalized = backend.normalizer.normalize_str(c)
        if normalized == '':
            value = 1
        elif normalized == ' ':
            value = 2
        elif normalized == ' '+c+' ':
            value = 4
        elif normalized == c:
            split = backend.pre_tokenizer.pre_tokenize_str('a'+c+'a')
            value = 8 if len(split) == 3 and split[1][0] == c else 0
            if not (len(split) == 1 or value == 8):
                raise ValueError(f'unhandled pre-tokenizer scalar U+{cp:04X}')
        else:
            raise ValueError(f'unhandled normalization scalar U+{cp:04X}')
        if value and value == flags and cp == last+1:
            last = cp
        else:
            if flags:
                ranges.append([start, last, flags])
            start = last = cp
            flags = value
    if flags:
        ranges.append([start, last, flags])
    return dict(schemaVersion=1, protocol=VERSION, vocabulary=tokens, merges=merges,
                unicodeRanges=ranges, addedTokens=added,
                specialTokenIds={k:getattr(tokenizer, k+'_token_id') for k in ('cls','sep','mask','pad','unk')})

class PortableTokenizer:
    def __init__(self, data):
        self.vocab = {s:i for i,s in enumerate(data['vocabulary'])}
        self.merges = {(a,b):(rank,c) for rank,(a,b,c) in enumerate(data['merges'])}
        self.special = {t['content']:t['id'] for t in data['addedTokens']}
        self.unk = data['specialTokenIds']['unk']
        self.flags = bytearray(0x110000)
        for start,end,flag in data['unicodeRanges']:
            self.flags[start:end+1] = bytes([flag])*(end-start+1)

    def word(self, word):
        ids = [self.vocab.get(c+('</w>' if i == len(word)-1 else ''), self.unk)
               for i,c in enumerate(word)]
        # Leftmost minimum-rank merge. The reference intentionally uses a simple
        # search; the Android implementation uses a linked priority queue.
        while len(ids) > 1:
            choices = [(self.merges[(a,b)][0],i,self.merges[(a,b)][1])
                       for i,(a,b) in enumerate(zip(ids,ids[1:])) if (a,b) in self.merges]
            if not choices:
                break
            _,pos,new = min(choices)
            ids[pos:pos+2] = [new]
        return ids

    def ordinary(self, text):
        words, current = [], []
        def flush():
            if current:
                words.append(''.join(current))
                current.clear()
        for c in text:
            flag = self.flags[ord(c)]
            if flag == 1:
                continue
            if flag in (2,4,8):
                flush()
                if flag != 2:
                    words.append(c)
            else:
                current.append(c)
        flush()
        return [i for w in words for i in self.word(w)]

    def encode(self, text):
        if any(0xd800 <= ord(c) <= 0xdfff for c in text):
            raise ValueError('unpaired surrogate')
        out, pos = [], 0
        while pos < len(text):
            choices = [(text.find(s,pos),-len(s),s) for s in self.special if text.find(s,pos) >= 0]
            if not choices:
                out.extend(self.ordinary(text[pos:]))
                break
            at,_,token = min(choices)
            out.extend(self.ordinary(text[pos:at]))
            out.append(self.special[token])
            pos = at+len(token)
        return out

def conformance_strings(requests):
    strings = {'', 'łódź', 'Łódź', 'łodzi', 'Łodzi', '3. Ale lub tutaj',
               'zażółć gęślą jaźń', 'a\u0301', 'A\tB\nC', 'a\u00a0b',
               'a\u200bb', '🚤 🏙️', '中 文', 'foo-bar „Łódź”', 'a\x00b',
               '<mask> <s> </s> <unk> <pad>', 'a<mask>b', '<mask><mask>',
               '<ma\u200bsk>', 'a\ufffdb', '\ue000kot\U000F0000', '𠀀Łódź丽'}
    strings.update(r['context'] for r in requests)
    strings.update(c['surface'] for r in requests for c in r['candidates'])
    rng = random.Random(20261004)
    alphabet = list('łŁódźŹąĄęĘńŃóÓśŚżŻabcXYZ 012,.!?-\t\n') + list('🚤中\u0301\u200b\u00a0')
    for _ in range(512):
        strings.add(''.join(rng.choice(alphabet) for _ in range(rng.randrange(1,97))))
    for _ in range(1024):
        cp = rng.randrange(0x110000)
        if not 0xd800 <= cp <= 0xdfff:
            strings.add('a'+chr(cp)+'Ł')
    return sorted(strings)
