#!/usr/bin/env python3
"""Append human-approved staged listings to DATA and SEED_POINTS.

Usage:
  python3 refresh/apply_staged.py --file staging/proposed_2026-08-10.json \
      --approve act_id-one act_id-two [--html index.html]

Refuses: geocode FAILED, OUT_OF_ZONE matches, ids already present, and any
listing carrying a mergeCandidate (merges stay hand-reviewed anchored edits).
Runs the full verification battery on the candidate file before writing.
HUMAN-INVOKED ONLY."""
import argparse, json, os, re, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from refresh import (ROOT, load_html, extract_data, extract_out_of_zone,
                     validate_spliced)

DATA_FIELDS = ['id', 'a', 'llc', 'v', 'sd', 'lot', 'kind', 'bb', 'prod', 'f',
               'u', 'lat', 'lng', 'c', 'ty']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--file', required=True)
    ap.add_argument('--approve', nargs='+', required=True)
    ap.add_argument('--html', default=os.path.join(ROOT, 'index.html'))
    args = ap.parse_args()

    with open(args.file, encoding='utf-8') as f:
        staged = {s['id']: s for s in json.load(f)}
    src = load_html(args.html)
    data = extract_data(src)
    ids = {d['id'] for d in data}
    sp = json.loads(re.search(r'SEED_POINTS=(\{.*?\});\nif\(Object', src, re.S).group(1))
    ooz = extract_out_of_zone(src)

    approved = []
    for i in args.approve:
        s = staged.get(i)
        if s is None:
            raise SystemExit(f'REFUSED: {i} not in {args.file}')
        if s['geocode'] == 'FAILED':
            raise SystemExit(f'REFUSED: {i} has no geocode — resolve coordinates first')
        if s.get('mergeCandidate'):
            raise SystemExit(f"REFUSED: {i} duplicates {s['mergeCandidate']} — "
                             'merge by hand per convention, do not append')
        if ooz.search(s['a']) or ooz.search(s['data']['a']):
            raise SystemExit(f'REFUSED: {i} matches OUT_OF_ZONE')
        if i in ids or i in sp:
            raise SystemExit(f'REFUSED: {i} already exists in DATA or SEED_POINTS')
        approved.append(s)

    data_frag = ', '.join(
        json.dumps({k: s['data'][k] for k in DATA_FIELDS}, ensure_ascii=False)
        for s in approved)
    seed_frag = ','.join(
        f'"{s["id"]}":' + json.dumps(s['seed'], ensure_ascii=False, separators=(',', ':'))
        for s in approved)

    m = re.search(r'let DATA = \[.*?\];\n', src, re.S)
    d_end = m.end() - len('];\n')
    candidate = src[:d_end] + ', ' + data_frag + src[d_end:]
    m = re.search(r'SEED_POINTS=\{.*?\};\nif\(Object', candidate, re.S)
    s_end = m.end() - len('};\nif(Object')
    candidate = candidate[:s_end] + ',' + seed_frag + candidate[s_end:]

    rec_check = validate_spliced(candidate)
    new_data = extract_data(candidate)
    cc = Counter((d['lat'], d['lng']) for d in new_data if 'lat' in d)
    dup = [k for k, v in cc.items() if v > 1]
    if dup:
        raise SystemExit(f'REFUSED: exact lat/lng collision(s): {dup}')
    by_id = {d['id']: d for d in new_data}
    for s in approved:
        assert list(by_id[s['id']].keys()) == DATA_FIELDS, f'field order broke for {s["id"]}'
    assert rec_check is not None

    with open(args.html, 'w', encoding='utf-8') as f:
        f.write(candidate)
    print(f'appended {len(approved)} listings to DATA + SEED_POINTS — validated:')
    for s in approved:
        print(f"  {s['id']}  {s['a']}  ({s['geocode']})")


if __name__ == '__main__':
    main()
