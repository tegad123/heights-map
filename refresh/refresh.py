#!/usr/bin/env python3
"""Actives refresh pipeline for the Heights map.

Stage (a) scope: diff a dated pair of HAR actives CSVs against the current
DATA actives, respecting OUT_OF_ZONE and the current reconcile state, and
emit changes/changes_YYYY-MM-DD.json + changes/index.json.

Usage:
  python3 refresh/refresh.py diff --date 2026-08-10 single.csv split.csv
      [--html index.html] [--write]

Without --write it prints the classification and touches nothing.
HUMAN-INVOKED ONLY — never run from cron (CLAUDE.md hard rule).
"""
import argparse, csv, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from norm import key

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANGES_DIR = os.path.join(ROOT, 'changes')


# ---------- index.html extraction ----------

def load_html(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def extract_data(src):
    m = re.search(r'let DATA = (\[.*?\]);\n', src, re.S)
    if not m:
        raise SystemExit('FATAL: DATA block not found')
    return json.loads(m.group(1))


def extract_out_of_zone(src):
    m = re.search(r'const OUT_OF_ZONE=/(.*?)/i;', src)
    if not m:
        raise SystemExit('FATAL: OUT_OF_ZONE regex not found')
    return re.compile(m.group(1), re.I)


def extract_reconcile(src):
    """Read reconcile state from the RECONCILE marker block, or fall back to
    the legacy OFFMKT_727/RELIST_727 constants."""
    m = re.search(r'const RECONCILE=(\{.*?\});', src)
    if m:
        rec = json.loads(m.group(1))
        return rec.get('off', {}), rec.get('relist', {})
    off, rel = {}, {}
    m = re.search(r'const OFFMKT_727=(\{.*?\});', src)
    if m:
        off = {k: {'t': v, 'd': '2026-07-27'} for k, v in json.loads(m.group(1)).items()}
    m = re.search(r'const RELIST_727=(\{.*?\});', src)
    if m:
        rel = {k: {'t': v, 'd': '2026-07-28'} for k, v in json.loads(m.group(1)).items()}
    return off, rel


# ---------- HAR CSV parsing ----------

def parse_har(path):
    """Parse a HAR actives export. Accepts the address-led headerless
    template or the headered variant with an Address column. Anything else
    (e.g. the stats view, which has no Address) is a hard error."""
    with open(path, encoding='utf-8-sig', newline='') as f:
        rows = [r for r in csv.reader(f) if any(c.strip() for c in r)]
    if not rows:
        raise SystemExit(f'FATAL: {path} is empty')
    first = rows[0]
    out = []
    if re.match(r'^\d', (first[0] or '').strip()):
        # address-led, no header row
        for r in rows:
            out.append({'Address': r[0].strip(), '_row': r})
    else:
        hdr = [c.strip() for c in first]
        if 'Address' not in hdr:
            raise SystemExit(f'FATAL: {path} has a header row but no Address '
                             'column — this looks like the stats-view export, which will not parse')
        for r in rows[1:]:
            rec = dict(zip(hdr, r))
            if rec.get('Address', '').strip():
                rec['_row'] = r
                out.append(rec)
    if not out:
        raise SystemExit(f'FATAL: {path} parsed to zero listings')
    return out


def _matched_alt(pattern, a):
    """Which top-level alternative of the OUT_OF_ZONE regex matched (split on
    '|' only at paren depth 0, so grouped alternations stay intact)."""
    alts, depth, cur = [], 0, ''
    for ch in pattern:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == '|' and depth == 0:
            alts.append(cur); cur = ''
        else:
            cur += ch
    alts.append(cur)
    for alt in alts:
        if re.search(alt, a, re.I):
            return alt
    return pattern


# ---------- diff ----------

def run_diff(date, csv_paths, html_path):
    src = load_html(html_path)
    data = extract_data(src)
    ooz = extract_out_of_zone(src)
    off, rel = extract_reconcile(src)

    actives = [d for d in data if d.get('kind') == 'active']
    by_key = {}
    for d in actives:
        by_key.setdefault(key(d['a']), d)

    export, excluded = [], []
    for prod, path in csv_paths:
        for rec in parse_har(path):
            a = rec['Address']
            if ooz.search(a):
                excluded.append({'a': a, 'rule': _matched_alt(ooz.pattern, a)})
                continue
            rec['_prod'] = prod
            export.append(rec)

    exp_keys = {}
    for rec in export:
        exp_keys.setdefault(key(rec['Address']), rec)

    # pass 1: exact key matches
    hits = {k: by_key[k] for k in exp_keys if k in by_key}
    # pass 2: unit-fallback — pair leftover export rows and DATA records that
    # share number+street but differ in unit letter, ONLY when unambiguous
    # (exactly one candidate on each side). Handles "845-A West 23rd" vs
    # "845 West 23rd Street" without conflating true unit twins.
    rem_exp = {k: r for k, r in exp_keys.items() if k not in hits}
    rem_data = {k: d for k, d in by_key.items() if k not in hits}
    def nc(k):
        n, u, c = k.split('|'); return n + '|' + c
    exp_g, dat_g = {}, {}
    for k in rem_exp: exp_g.setdefault(nc(k), []).append(k)
    for k in rem_data: dat_g.setdefault(nc(k), []).append(k)
    for g, eks in exp_g.items():
        dks = dat_g.get(g, [])
        if len(eks) == 1 and len(dks) == 1:
            eu, du = eks[0].split('|')[1], dks[0].split('|')[1]
            if eu and du and eu != du:
                continue    # two different explicit unit letters: never pair
            hits[eks[0]] = by_key[dks[0]]
            rem_data.pop(dks[0], None)

    matched, new, relisted = [], [], []
    matched_ids = set()
    for k, rec in exp_keys.items():
        d = hits.get(k)
        if d is None:
            new.append(rec)
            continue
        matched_ids.add(d['id'])
        if d['id'] in off:
            relisted.append({'id': d['id'], 'a': d['a'], 'ty': d.get('ty'),
                             'offSince': off[d['id']]['d']})
        else:
            matched.append(d['id'])

    dropped = []
    for k, d in by_key.items():
        if d['id'] in matched_ids:
            continue
        if d['id'] in off:      # already off-market; no new event
            continue
        is_split = d.get('ty') == 'active_split' or d.get('prod') == 'Split Lot'
        dropped.append({'id': d['id'], 'a': d['a'],
                        'ty': 'split' if is_split else 'single',
                        'disposition': 'unconfirmed'})

    return {
        'date': date,
        'sources': [os.path.basename(p) for _, p in csv_paths],
        'counts': {'matched': len(matched), 'dropped': len(dropped),
                   'new': len(new), 'relisted': len(relisted),
                   'excluded': len(excluded)},
        'matchedIds': sorted(matched),
        'dropped': sorted(dropped, key=lambda x: x['id']),
        'relisted': sorted(relisted, key=lambda x: x['id']),
        'new': [{'a': r['Address'], 'prod': r['_prod'], 'staged': True,
                 'mergeCandidate': None} for r in new],
        'excluded': excluded,
        'dispositionUpdates': {},
    }


# ---------- changelog io ----------

def write_changelog(chg):
    os.makedirs(CHANGES_DIR, exist_ok=True)
    fn = f"changes_{chg['date']}.json"
    with open(os.path.join(CHANGES_DIR, fn), 'w', encoding='utf-8') as f:
        json.dump(chg, f, ensure_ascii=False, indent=1)
        f.write('\n')
    rebuild_index()
    return fn


def rebuild_index():
    files = sorted(f for f in os.listdir(CHANGES_DIR)
                   if re.fullmatch(r'changes_\d{4}-\d{2}-\d{2}\.json', f))
    idx = {'files': [], 'updated': None}
    for f in files:
        with open(os.path.join(CHANGES_DIR, f), encoding='utf-8') as fh:
            c = json.load(fh)
        idx['files'].append({'file': f, 'date': c['date'], 'counts': c['counts']})
        idx['updated'] = c['date']
    with open(os.path.join(CHANGES_DIR, 'index.json'), 'w', encoding='utf-8') as f:
        json.dump(idx, f, ensure_ascii=False, indent=1)
        f.write('\n')


# ---------- reconcile generation (stage b) ----------

MARK_BEGIN = '/* RECONCILE:BEGIN — machine-generated by refresh/refresh.py. Do not hand-edit. */'
MARK_END = '/* RECONCILE:END */'


def fold_reconcile():
    """Fold the changelog chronologically into latest-state-per-id off/relist."""
    with open(os.path.join(CHANGES_DIR, 'index.json'), encoding='utf-8') as f:
        idx = json.load(f)
    off, rel = {}, {}
    for entry in idx['files']:
        with open(os.path.join(CHANGES_DIR, entry['file']), encoding='utf-8') as f:
            c = json.load(f)
        for d in c.get('dropped', []):
            off[d['id']] = {'t': d['ty'], 'd': c['date']}
            rel.pop(d['id'], None)
        for r in c.get('relisted', []):
            t = 'split' if 'split' in str(r.get('ty')) else 'single'
            rel[r['id']] = {'t': t, 'd': c['date']}
            off.pop(r['id'], None)
    overlap = set(off) & set(rel)
    if overlap:
        raise SystemExit(f'FATAL: off/relist overlap after fold: {overlap}')
    return off, rel


def validate_spliced(src):
    """Full re-parse of a candidate index.html. Raises on any failure."""
    if src.count(MARK_BEGIN) != 1 or src.count(MARK_END) != 1:
        raise SystemExit('FATAL: RECONCILE markers not present exactly once')
    if src.index(MARK_BEGIN) > src.index(MARK_END):
        raise SystemExit('FATAL: RECONCILE markers out of order')
    json.loads(re.search(r'let DATA = (\[.*?\]);\n', src, re.S).group(1))
    json.loads(re.search(r'SEED_POINTS=(\{.*?\});\nif\(Object', src, re.S).group(1))
    json.loads(re.search(r'const LIFE=(\{.*?\});\n', src, re.S).group(1))
    rec = json.loads(re.search(r'const RECONCILE=(\{.*?\});', src, re.S).group(1))
    assert set(rec) == {'off', 'relist'}, 'RECONCILE keys wrong'
    assert not set(rec['off']) & set(rec['relist']), 'RECONCILE off/relist overlap'
    if src.count('applyReconcile(state.points)') < 2:
        raise SystemExit('FATAL: applyReconcile not referenced at both call sites')
    return rec


def cmd_generate(html_path, skip_pull=False):
    if not skip_pull:
        r = os.system('git -C "%s" pull --ff-only -q' % ROOT)
        if r != 0:
            raise SystemExit('FATAL: git pull --ff-only failed — resolve divergence first')
    src = load_html(html_path)
    off, rel = fold_reconcile()
    block = (MARK_BEGIN + '\nconst RECONCILE=' +
             json.dumps({'off': off, 'relist': rel}, ensure_ascii=False,
                        separators=(',', ':')) + ';\n' + MARK_END)
    i, j = src.find(MARK_BEGIN), src.find(MARK_END)
    if i == -1 or j == -1:
        raise SystemExit('FATAL: RECONCILE markers missing — one-time migration must exist first')
    candidate = src[:i] + block + src[j + len(MARK_END):]
    rec = validate_spliced(candidate)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(candidate)
    print(f"spliced RECONCILE: {len(rec['off'])} off, {len(rec['relist'])} relist — validated")


# ---------- cli ----------

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    d = sub.add_parser('diff', help='diff HAR exports against DATA actives')
    d.add_argument('--date', required=True)
    d.add_argument('single_csv')
    d.add_argument('split_csv')
    d.add_argument('--html', default=os.path.join(ROOT, 'index.html'))
    d.add_argument('--write', action='store_true', help='write the changelog (default: dry run)')
    g = sub.add_parser('generate', help='splice RECONCILE block into index.html from the changelog')
    g.add_argument('--html', default=os.path.join(ROOT, 'index.html'))
    g.add_argument('--skip-pull', action='store_true', help='skip git pull --ff-only (tests only)')
    args = ap.parse_args()

    if args.cmd == 'generate':
        cmd_generate(args.html, skip_pull=args.skip_pull)
        return

    if args.cmd == 'diff':
        chg = run_diff(args.date, [('Single Lot', args.single_csv),
                                   ('Split Lot', args.split_csv)], args.html)
        print(json.dumps(chg['counts']))
        for sec in ('dropped', 'relisted', 'new', 'excluded'):
            for e in chg[sec]:
                print(f"  {sec[:4].upper()}  {e.get('id', '-'):34s} {e.get('a', '')}")
        if args.write:
            fn = write_changelog(chg)
            print(f'wrote changes/{fn} + index.json')
        else:
            print('(dry run — nothing written)')


if __name__ == '__main__':
    main()
