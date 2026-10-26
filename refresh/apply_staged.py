#!/usr/bin/env python3
"""Append human-approved staged listings to DATA and SEED_POINTS.

Usage:
  python3 refresh/apply_staged.py --file staging/proposed_2026-08-10.json \
      --approve act_id-one act_id-two [--html index.html]

Refuses: geocode FAILED, OUT_OF_ZONE matches, ids already present, any listing
carrying a mergeCandidate (link those with `refresh.py link-staged`), any
listing whose address (street type optional, units significant) is already a
DATA record, and exact lat/lng collisions involving an appended pin unless the
two are split siblings (same street, unit letters or house numbers 2 apart).
Runs the full verification battery on the candidate file before writing, then
marks the listing's `new` entry applied in the same-date changelog.
HUMAN-INVOKED ONLY."""
import argparse, json, os, re, sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refresh
from refresh import (ROOT, MARKETS, load_html, extract_data, extract_out_of_zone,
                     validate_spliced, type_free_key)

DATA_FIELDS = ['id', 'a', 'llc', 'v', 'sd', 'lot', 'kind', 'bb', 'prod', 'f',
               'u', 'lat', 'lng', 'c', 'ty']


def _house(addr):
    w = type_free_key(addr).split()
    return (w[0], w[1:]) if w and w[0].isdigit() else (None, w)


def split_siblings(a, b):
    (na, ra), (nb, rb) = _house(a), _house(b)
    if not na or not nb:
        return False
    if na == nb:
        diff = [x for x in ra if x not in rb] + [x for x in rb if x not in ra]
        return bool(diff) and all(re.fullmatch(r'[a-f]', x) for x in diff)
    return abs(int(na) - int(nb)) == 2 and int(na) % 2 == int(nb) % 2 and ra == rb


def mark_applied(staged_path, html_path, approved):
    """Changelog text with the appended listings' `new` entries flagged applied
    (matched by MLS): returns (path, text, message); path None = untouched."""
    market = next((m for m, mk in MARKETS.items()
                   if Path(html_path).resolve() == Path(ROOT, mk['html']).resolve()), None)
    m = re.search(r'proposed_(\d{4}-\d{2}-\d{2})\.json$', str(staged_path))
    if market is None or m is None:
        return None, None, 'no market/date for this staging file; changelog untouched'
    refresh.set_market(market)
    path = Path(refresh.CHANGES_DIR, f'changes_{m.group(1)}.json')
    if not path.exists():
        return None, None, f'{path.relative_to(ROOT)} absent; changelog untouched'
    raw = path.read_text()
    chg = json.loads(raw)
    if json.dumps(chg, ensure_ascii=False, indent=1) + '\n' != raw:
        raise SystemExit(f'FATAL: {path.relative_to(ROOT)} does not round-trip; refusing to reserialize it')
    hits = 0
    for s in approved:
        news = [n for n in chg.get('new', []) if s.get('mls') and n.get('mls') == s['mls']
                and not n.get('mergeCandidate')]
        if len(news) > 1:
            raise SystemExit(f"FATAL: MLS {s['mls']} has {len(news)} new entries in {path.name}")
        for n in news:
            n.update(staged=False, id=s['id'], applied=True)
            hits += 1
    return (path, json.dumps(chg, ensure_ascii=False, indent=1) + '\n',
            f'marked {hits} new entries applied in {path.relative_to(ROOT)}')


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
    by_key = {}
    for d in data:
        by_key.setdefault(type_free_key(d['a']), []).append(d['id'])

    approved = []
    for i in args.approve:
        s = staged.get(i)
        if s is None:
            raise SystemExit(f'REFUSED: {i} not in {args.file}')
        if s['geocode'] == 'FAILED':
            raise SystemExit(f'REFUSED: {i} has no geocode — resolve coordinates first')
        if s.get('mergeCandidate'):
            raise SystemExit(f"REFUSED: {i} duplicates {s['mergeCandidate']} — "
                             'link it with refresh.py link-staged, do not append')
        if ooz.search(s['a']) or ooz.search(s['data']['a']):
            raise SystemExit(f'REFUSED: {i} matches OUT_OF_ZONE')
        if i in ids or i in sp:
            raise SystemExit(f'REFUSED: {i} already exists in DATA or SEED_POINTS')
        k = type_free_key(s['a'])
        if by_key.get(k):
            raise SystemExit(f"REFUSED: {i} ({s['a']}) is already DATA record(s) {by_key[k]}")
        by_key[k] = [i]
        approved.append(s)

    data_frag = ', '.join(
        json.dumps({k: s['data'][k] for k in DATA_FIELDS}, ensure_ascii=False)
        for s in approved)
    seed_frag = ','.join(
        f'"{s["id"]}":' + json.dumps(s['seed'], ensure_ascii=False, separators=(',', ':'))
        for s in approved)

    m = re.search(r'let DATA = (\[.*?\]);[ \t]*(?://[^\n]*)?\n', src, re.S)
    d_end = m.end(1) - 1
    candidate = src[:d_end] + ', ' + data_frag + src[d_end:]
    m = re.search(r'SEED_POINTS=\{.*?\};\nif\(Object', candidate, re.S)
    s_end = m.end() - len('};\nif(Object')
    candidate = candidate[:s_end] + ',' + seed_frag + candidate[s_end:]

    rec_check = validate_spliced(candidate)
    new_data = extract_data(candidate)
    if new_data[:len(data)] != data or len(new_data) != len(data) + len(approved):
        raise SystemExit('FATAL: existing DATA records changed')
    new_ids = {s['id'] for s in approved}
    at = {}
    for d in new_data:
        if 'lat' in d:
            at.setdefault((d['lat'], d['lng']), []).append(d)
    for ll, group in at.items():
        fresh = [d for d in group if d['id'] in new_ids]
        for x in fresh:
            for y in group:
                if y is not x and not split_siblings(x['a'], y['a']):
                    raise SystemExit(f"REFUSED: exact lat/lng collision {ll}: {x['id']} / {y['id']}")
    by_id = {d['id']: d for d in new_data}
    for s in approved:
        assert list(by_id[s['id']].keys()) == DATA_FIELDS, f'field order broke for {s["id"]}'
    assert rec_check is not None
    chg_path, chg_text, chg_msg = mark_applied(args.file, args.html, approved)

    with open(args.html, 'w', encoding='utf-8') as f:
        f.write(candidate)
    if chg_path:
        chg_path.write_text(chg_text)
    print(f'appended {len(approved)} listings to DATA + SEED_POINTS — validated:')
    for s in approved:
        print(f"  {s['id']}  {s['a']}  ({s['geocode']})")
    print(chg_msg)


if __name__ == '__main__':
    main()
