"""Read-only CKDT V2 coverage comparison. Run with two inner langpack ZIPs."""
import argparse
import hashlib
import json
import struct
import unicodedata
import zipfile


def normalize(word):
    return ''.join(c for c in unicodedata.normalize('NFD', word.lower().replace('ł', 'l'))
                   if unicodedata.category(c) != 'Mn')


def read_pack(path, probes):
    with zipfile.ZipFile(path) as archive:
        data = archive.read('dictionary.bin')
        manifest = json.loads(archive.read('manifest.json'))
        unigrams = set(archive.read('unigrams.txt').decode('utf-8').splitlines())
    magic, version, language, count, canonical, normalized, accent = struct.unpack_from('<4sI4sIIII', data)
    assert magic == b'CKDT' and version == 2 and language == b'pl\0\0'
    def string_at(pos):
        size, = struct.unpack_from('<H', data, pos)
        end = pos + 2 + size
        return data[pos + 2:end].decode('utf-8'), end
    words, ranks, pos = [], {}, canonical
    for _ in range(count):
        word, pos = string_at(pos)
        rank = data[pos]
        pos += 1
        words.append(word)
        assert word.lower() not in ranks
        ranks[word.lower()] = rank
    assert pos == normalized
    normalized_count, = struct.unpack_from('<I', data, normalized)
    pos = normalized + 4
    keys = []
    for _ in range(normalized_count):
        key, pos = string_at(pos)
        keys.append(key)
    assert pos == accent
    aliases, pos = {}, accent
    for key in keys:
        n = data[pos]
        pos += 1
        indexes = struct.unpack_from('<' + 'I' * n, data, pos)
        pos += 4 * n
        assert all(i < count for i in indexes)
        aliases[key] = [words[i] for i in indexes]
    assert pos == len(data)
    return {
        'manifest': manifest, 'pack_sha256': hashlib.sha256(open(path, 'rb').read()).hexdigest(),
        'dictionary_sha256': hashlib.sha256(data).hexdigest(), 'canonical_count': count,
        'normalized_count': normalized_count,
        'probes': {w: {'canonical_present': w.lower() in ranks,
                       'rank': ranks.get(w.lower()), 'normalized_key': normalize(w),
                       'normalized_candidates': aliases.get(normalize(w), []),
                       'unigram_present': w in unigrams} for w in probes},
    }, ranks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', required=True)
    parser.add_argument('--current', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('words', nargs='+')
    args = parser.parse_args()
    base, base_ranks = read_pack(args.base, args.words)
    current, current_ranks = read_pack(args.current, args.words)
    report = {'base': base, 'current': current,
              'removed_keys': sorted(base_ranks.keys() - current_ranks.keys()),
              'added_keys': sorted(current_ranks.keys() - base_ranks.keys()),
              'changed_ranks': {w: [base_ranks[w], current_ranks[w]]
                                for w in base_ranks.keys() & current_ranks.keys()
                                if base_ranks[w] != current_ranks[w]}}
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({'base_count': base['canonical_count'], 'current_count': current['canonical_count'],
                      'removed': len(report['removed_keys']), 'added': len(report['added_keys']),
                      'changed_ranks': len(report['changed_ranks']),
                      'probes': current['probes']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
