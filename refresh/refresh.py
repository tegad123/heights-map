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
        # pending (under contract) ids are still off the market — if one
        # reappears in an export that is a relist, so fold them into off here
        off = dict(rec.get('off', {}))
        off.update(rec.get('pending', {}))
        return off, rec.get('relist', {})
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
    """Latest-state-per-id buckets for the RECONCILE block. Business rule:
    off_market applies to sold/terminated/unconfirmed only — ids whose newest
    disposition is 'under contract' go in the pending bucket instead."""
    off, rel, pend, _, _ = fold_events()
    for a, b in (('off', 'relist'), ('off', 'pending'), ('relist', 'pending')):
        overlap = set({'off': off, 'relist': rel, 'pending': pend}[a]) & \
                  set({'off': off, 'relist': rel, 'pending': pend}[b])
        if overlap:
            raise SystemExit(f'FATAL: {a}/{b} overlap after fold: {overlap}')
    return off, rel, pend


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
    assert set(rec) == {'off', 'relist', 'pending'}, 'RECONCILE keys wrong'
    for a in ('off', 'relist', 'pending'):
        for b in ('off', 'relist', 'pending'):
            if a < b:
                assert not set(rec[a]) & set(rec[b]), f'RECONCILE {a}/{b} overlap'
    if src.count('applyReconcile(state.points)') < 2:
        raise SystemExit('FATAL: applyReconcile not referenced at both call sites')
    return rec


def cmd_generate(html_path, skip_pull=False):
    if not skip_pull:
        r = os.system('git -C "%s" pull --ff-only -q' % ROOT)
        if r != 0:
            raise SystemExit('FATAL: git pull --ff-only failed — resolve divergence first')
    src = load_html(html_path)
    off, rel, pend = fold_reconcile()
    block = (MARK_BEGIN + '\nconst RECONCILE=' +
             json.dumps({'off': off, 'relist': rel, 'pending': pend},
                        ensure_ascii=False, separators=(',', ':')) + ';\n' + MARK_END)
    i, j = src.find(MARK_BEGIN), src.find(MARK_END)
    if i == -1 or j == -1:
        raise SystemExit('FATAL: RECONCILE markers missing — one-time migration must exist first')
    candidate = src[:i] + block + src[j + len(MARK_END):]
    rec = validate_spliced(candidate)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(candidate)
    print(f"spliced RECONCILE: {len(rec['off'])} off, {len(rec['relist'])} relist, "
          f"{len(rec['pending'])} pending — validated")


# ---------- stage (c): generated off-market CSV + LIFE sync ----------

CSV_NAME = 'heights_off_market.csv'
CSV_HDR = ['id', 'address', 'lot_type', 'last_list_price', 'builder', 'agent',
           'lot_sqft', 'building_sqft', 'mls_number', 'date_off_market',
           'disposition', 'lat', 'lng', 'notes']


def fold_events():
    """Full fold: off/relist/pending state plus newest-wins dispositions and
    drop dates. 'under contract' ids move from off to pending (they are not
    Off Market until they resolve to sold or terminated)."""
    with open(os.path.join(CHANGES_DIR, 'index.json'), encoding='utf-8') as f:
        idx = json.load(f)
    off, rel, disp, ddate = {}, {}, {}, {}
    for entry in idx['files']:
        with open(os.path.join(CHANGES_DIR, entry['file']), encoding='utf-8') as f:
            c = json.load(f)
        for d in c.get('dropped', []):
            off[d['id']] = {'t': d['ty'], 'd': c['date']}
            rel.pop(d['id'], None)
            ddate[d['id']] = c['date']
            disp[d['id']] = (d.get('disposition') or 'unconfirmed', c['date'])
        for r in c.get('relisted', []):
            t = 'split' if 'split' in str(r.get('ty')) else 'single'
            rel[r['id']] = {'t': t, 'd': c['date']}
            off.pop(r['id'], None)
        for k, v in c.get('dispositionUpdates', {}).items():
            disp[k] = (v, c['date'])
    pend = {i: off.pop(i) for i in [i for i in off
            if disp.get(i, ('', ''))[0] == 'under contract']}
    return off, rel, pend, disp, ddate


def cmd_csv(html_path):
    src = load_html(html_path)
    data = {d['id']: d for d in extract_data(src)}
    sp = json.loads(re.search(r'SEED_POINTS=(\{.*?\});\nif\(Object', src, re.S).group(1))
    off, rel, pend, disp, ddate = fold_events()
    # carry enrichment fields + row order from the previous CSV
    prev, order = {}, []
    path = os.path.join(ROOT, CSV_NAME)
    if os.path.exists(path):
        with open(path, encoding='utf-8', newline='') as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            prev[r['id']] = r
            order.append(r['id'])
    ordered = [i for i in order if i in off] + sorted(i for i in off if i not in order)
    out = []
    for i in ordered:
        d, p = data.get(i, {}), prev.get(i, {})
        out.append({
            'id': i,
            'address': p.get('address') or d.get('a', ''),
            'lot_type': p.get('lot_type') or ('Split Lot' if off[i]['t'] == 'split' else 'Single Lot'),
            'last_list_price': d.get('v') or p.get('last_list_price', ''),
            'builder': p.get('builder') or d.get('llc', ''),
            'agent': p.get('agent') or (d.get('c') or [{}])[0].get('n', ''),
            'lot_sqft': p.get('lot_sqft', ''),
            'building_sqft': p.get('building_sqft', ''),
            'mls_number': p.get('mls_number', ''),
            'date_off_market': ddate.get(i) or p.get('date_off_market', ''),
            'disposition': disp.get(i, ('unconfirmed', ''))[0],
            'lat': p.get('lat') or d.get('lat', ''),
            'lng': p.get('lng') or d.get('lng', ''),
            'notes': (sp.get(i) or {}).get('notes') or p.get('notes', ''),
        })
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=CSV_HDR, lineterminator='\n')
        w.writeheader()
        w.writerows(out)
    print(f'wrote {CSV_NAME}: {len(out)} rows')


LIFE_NOTES = {
    'unconfirmed': 'Lifecycle: Off market as of {d} — was active MLS listing',
    'sold': 'Lifecycle: Sold as of {d} — was active MLS listing',
    'under contract': 'Lifecycle: Under contract as of {d} — was active MLS listing',
    'terminated': 'Lifecycle: Listing terminated as of {d} — was active MLS listing',
}


def cmd_life_sync(html_path):
    """Rewrite LIFE entries for changelog-event ids from dispositions.
    Owns s + note only; ty/fin (and every non-event entry) preserved."""
    src = load_html(html_path)
    m = re.search(r'const LIFE=(\{.*?\});\n', src, re.S)
    raw = m.group(1)
    life = json.loads(raw)
    assert json.dumps(life, ensure_ascii=False, separators=(',', ':')) == raw, \
        'LIFE does not round-trip — aborting'
    off, rel, pend, disp, ddate = fold_events()
    changed = 0
    for i in list(off) + list(rel) + list(pend):
        e = life.get(i)
        if e is None:
            continue
        if i in rel:
            want_s, want_note = 'ready', 'Lifecycle: Ready for market — active MLS listing'
        else:
            dsp, ddt = disp.get(i, ('unconfirmed', ddate.get(i, '')))
            date = ddt if dsp != 'unconfirmed' else ddate.get(i, ddt)
            want_s, want_note = 'sold', LIFE_NOTES[dsp].format(d=date)
        if e.get('s') != want_s or e.get('note') != want_note:
            e['s'], e['note'] = want_s, want_note
            changed += 1
    new_raw = json.dumps(life, ensure_ascii=False, separators=(',', ':'))
    candidate = src.replace('const LIFE=' + raw, 'const LIFE=' + new_raw)
    validate_spliced(candidate)
    if changed:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(candidate)
    print(f'life-sync: {changed} entries changed')


# ---------- stage (d): staging of new listings ----------

STAGING_DIR = os.path.join(ROOT, 'staging')


def slug_id(addr):
    return 'act_' + re.sub(r'[^a-z0-9]+', '-', str(addr).lower().split(',')[0]).strip('-')


def geocode_batch(addrs):
    """Census batch geocode. Returns {input_addr: (lat, lng, quality)} with
    quality Exact/Non_Exact/FAILED. Local-only per CLAUDE.md."""
    import io, urllib.request, uuid
    lines = []
    for n, a in enumerate(addrs, 1):
        street = str(a).split(',')[0].replace('"', '')
        street = re.sub(r'\bunit\s*#?\s*[a-z0-9]+\b', '', street, flags=re.I).strip()
        lines.append(f'{n},{street},Houston,TX,')
    body = '\n'.join(lines).encode()
    boundary = uuid.uuid4().hex
    parts = []
    for name, val, fn in (('benchmark', b'Public_AR_Current', None),
                          ('addressFile', body, 'batch.csv')):
        h = f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"'
        h += f'; filename="{fn}"\r\nContent-Type: text/csv' if fn else ''
        parts.append(h.encode() + b'\r\n\r\n' + (val if isinstance(val, bytes) else val) + b'\r\n')
    payload = b''.join(parts) + f'--{boundary}--\r\n'.encode()
    req = urllib.request.Request(
        'https://geocoding.geo.census.gov/geocoder/locations/addressbatch',
        data=payload, headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
    rows = list(csv.reader(io.StringIO(urllib.request.urlopen(req, timeout=120).read().decode())))
    out = {}
    for r in rows:
        idx = int(r[0]) - 1
        if len(r) >= 6 and r[2] == 'Match':
            lng, lat = r[5].split(',')
            out[addrs[idx]] = (round(float(lat), 7), round(float(lng), 7), r[3])
        else:
            out[addrs[idx]] = (None, None, 'FAILED')
    return out


def fmt_price(v):
    try:
        return '${:,.0f}'.format(float(str(v).replace('$', '').replace(',', '')))
    except ValueError:
        return str(v)


def stage_new(chg, csv_paths, html_path):
    """Build staging/proposed_<date>.json for the diff's new listings."""
    from datetime import date as _date, timedelta
    src = load_html(html_path)
    data = extract_data(src)
    all_by_key = {}
    for d in data:
        all_by_key.setdefault(key(d['a']), d['id'])
    rows = {}
    for prod, path in csv_paths:
        for rec in parse_har(path):
            rec['_prod'] = prod
            rows[key(rec['Address'])] = rec
    new_addrs = [e['a'] for e in chg['new']]
    geo = geocode_batch(new_addrs) if new_addrs else {}
    y, m, dd = map(int, chg['date'].split('-'))
    staged = []
    for e in chg['new']:
        rec = rows.get(key(e['a']), {})
        lat, lng, q = geo.get(e['a'], (None, None, 'FAILED'))
        pid = slug_id(e['a'])
        prod = rec.get('_prod', e.get('prod', ''))
        subdiv = (rec.get('Subdivision') or '').strip()
        f_val = f'{prod}, {subdiv}' if subdiv and subdiv.upper() != 'NA' else prod
        sd = ''
        if rec.get('DOM', '').isdigit():
            sd = str(_date(y, m, dd) - timedelta(days=int(rec['DOM'])))
        agent = rec.get('List Agent Full Name', '')
        builder = rec.get('Builder Name', '')
        ty = 'active_split' if prod == 'Split Lot' else 'active_single'
        drec = {'id': pid, 'a': e['a'], 'llc': builder,
                'v': fmt_price(rec.get('Original List Price', '')),
                'sd': sd, 'lot': rec.get('Building SqFt', ''), 'kind': 'active',
                'bb': '', 'prod': prod, 'f': f_val, 'u': '', 'lat': lat, 'lng': lng,
                'c': [{'n': agent, 'p': [], 'e': []}], 'ty': ty}
        note = f'Active inventory — {prod}.'
        if builder:
            note += f' Builder: {builder}.'
        if agent:
            note += f' Agent: {agent}.'
        if q == 'Non_Exact':
            note += ' (location approximate).'
        staged.append({'id': pid, 'a': e['a'], 'geocode': q,
                       'mergeCandidate': all_by_key.get(key(e['a'])),
                       'data': drec,
                       'seed': {'notes': note, 'tags': [ty]}})
    os.makedirs(STAGING_DIR, exist_ok=True)
    fn = os.path.join(STAGING_DIR, f"proposed_{chg['date']}.json")
    with open(fn, 'w', encoding='utf-8') as f:
        json.dump(staged, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(f'staged {len(staged)} new listings -> staging/proposed_{chg["date"]}.json')
    for s in staged:
        flag = f" MERGE-CANDIDATE:{s['mergeCandidate']}" if s['mergeCandidate'] else ''
        print(f"  {s['id']:38s} geocode={s['geocode']}{flag}")


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
    c = sub.add_parser('csv', help='regenerate heights_off_market.csv from changelog + DATA')
    c.add_argument('--html', default=os.path.join(ROOT, 'index.html'))
    l = sub.add_parser('life-sync', help='sync LIFE s/note from changelog dispositions')
    l.add_argument('--html', default=os.path.join(ROOT, 'index.html'))
    args = ap.parse_args()

    if args.cmd == 'generate':
        cmd_generate(args.html, skip_pull=args.skip_pull)
        return
    if args.cmd == 'csv':
        cmd_csv(args.html)
        return
    if args.cmd == 'life-sync':
        cmd_life_sync(args.html)
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
            if chg['new']:
                stage_new(chg, [('Single Lot', args.single_csv),
                                ('Split Lot', args.split_csv)], args.html)
        else:
            print('(dry run — nothing written)')


if __name__ == '__main__':
    main()
