#!/usr/bin/env python3
"""Actives refresh pipeline for the CQ Houston market maps.

Services all 7 markets via --market (default: heights). Heights keeps its
changelog at changes/ and staging at staging/ (pre-generalization layout);
every other market uses changes/<market>/ and staging/<market>/.

Stage (a) scope: diff a dated pair of HAR actives CSVs against the current
DATA actives, respecting OUT_OF_ZONE and the current reconcile state, and
emit changes/changes_YYYY-MM-DD.json + changes/index.json.

Usage:
  python3 refresh/refresh.py diff --date 2026-08-10 single.csv split.csv
      [--html index.html] [--write]
  python3 refresh/refresh.py pull-edits [--html index.html] [--apply]

pull-edits fetches the browser-side offMarketEdits overlay (manual
disposition/note corrections made in the Off Market table) from the shared
edits store. Dry run stages a proposal; --apply folds disposition rulings
into changes/ (the changelog stays the single source of truth — the overlay
is an inbox, not a second writer). Overlay notes are applied by `csv` from
the staged snapshot; they never enter the changelog.

Without --write it prints the classification and touches nothing.

  python3 refresh/refresh.py har --market heights --date 2026-10-25 \
      --active A.csv --pending P.csv --sold S.csv --terminated T.csv \
      --runtime runtime.json [--apply]

har takes the four headered HAR status exports for one market (names from
market_config.py). Each row is zone-guarded by that market's own OUT_OF_ZONE
regex, east cutoff and boundary ring, and every exclusion
is ledgered. Matched = still listed; pending is never off market; terminal
statuses drop only on current evidence (or a true disappearance of the prior
MLS); new listings and never-listed pins are staged, not appended. Heights
also refreshes SOLD_* (rolling new-construction comps), the market-status
snapshot and heights_active.data.json; markets without SOLD_* get a staged
review file instead. The dry run writes only to pulls/har_<market>_<date>/.

  python3 refresh/refresh.py har-split --date 2026-11-01 \
      --active A.csv --pending P.csv --sold S.csv --terminated T.csv

har-split takes zip-wide exports covering several markets and cuts one slice
set per enabled market into pulls/har_split_<date>/<market>/, routed by each
row's coordinates through that market's own zone guard (never the HAR
Subdivision text). Overlapping rows go to every market that accepts them;
unplaced rows are ledgered in unplaced.csv. A market with no active rows is
held. Feed each slice set to `har`; its split_manifest.json lets a header-only
pending/sold/terminated slice through and replaces the cross-market hash guard.

  python3 refresh/refresh.py link-staged --market montrose --date 2026-10-26 \
      --file staging/montrose/proposed_2026-10-26.json --approve act_a act_b [--apply]
  python3 refresh/refresh.py archive-duplicates --market montrose --date 2026-10-26 \
      --archive acq_x pmt_x [--archive DUP [market:]CANONICAL ...] --reason TEXT [--apply]

link-staged records approved staged rows whose mergeCandidate is an existing
never-listed pin as listing events on that pin in the same-date changelog
(active -> relisted, pending -> 'under contract'); nothing is appended.
archive-duplicates retires a DATA record that repeats another pin's property
(precedent: changes_2026-09-28 archived_duplicates); the record moves into the
changelog. Both re-fold, splice RECONCILE, regenerate the CSV and validate;
dry run unless --apply.

  python3 refresh/refresh.py archive-out-of-zone --market springbranch --date 2026-10-26 \
      --ids acq_x acq_y --reason TEXT [--apply]

archive-out-of-zone retires DATA records whose coordinates fail the market's
own zone guard (market_config boundary) and that
carry no listing state; the record moves into the changelog's
archived_out_of_zone. Same fold/splice/validate path as archive-duplicates.

HUMAN-INVOKED ONLY — never run from cron (CLAUDE.md hard rule).
"""
import argparse, csv, hashlib, io, json, os, re, subprocess, sys
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from norm import key

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,ROOT)

# Per-market file layout. Heights predates the generalization and keeps the
# root-level changes/ + staging/ dirs (no history churn); other markets nest.
MARKETS = {
    'heights':      {'html': 'index.html',        'csv': 'heights_off_market.csv',      'sub': None},
    'montrose':     {'html': 'montrose.html',     'csv': 'montrose_off_market.csv',     'sub': 'montrose'},
    'springbranch': {'html': 'springbranch.html', 'csv': 'springbranch_off_market.csv', 'sub': 'springbranch'},
    'springvalley': {'html': 'springvalley.html', 'csv': 'springvalley_off_market.csv', 'sub': 'springvalley'},
    'timbergrove':  {'html': 'timbergrove.html',  'csv': 'timbergrove_off_market.csv',  'sub': 'timbergrove'},
    'westu':        {'html': 'westu.html',        'csv': 'westu_off_market.csv',        'sub': 'westu'},
    'riveroaks':    {'html': 'riveroaks.html',    'csv': 'riveroaks_off_market.csv',    'sub': 'riveroaks'},
    'gardenoaksoakforest': {'html': 'gardenoaksoakforest.html', 'csv': 'gardenoaksoakforest_off_market.csv', 'sub': 'gardenoaksoakforest'},
}

# Resolved per-run by set_market(); heights defaults keep every pre-existing
# invocation byte-identical.
CHANGES_DIR = os.path.join(ROOT, 'changes')
STAGING_DIR = os.path.join(ROOT, 'staging')
CSV_NAME = 'heights_off_market.csv'
DEFAULT_HTML = os.path.join(ROOT, 'index.html')


def set_market(name):
    global CHANGES_DIR, STAGING_DIR, CSV_NAME, DEFAULT_HTML
    mk = MARKETS[name]
    sub = mk['sub']
    CHANGES_DIR = os.path.join(ROOT, 'changes', sub) if sub else os.path.join(ROOT, 'changes')
    STAGING_DIR = os.path.join(ROOT, 'staging', sub) if sub else os.path.join(ROOT, 'staging')
    CSV_NAME = mk['csv']
    DEFAULT_HTML = os.path.join(ROOT, mk['html'])


# ---------- index.html extraction ----------

def load_html(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def extract_data(src):
    # some market files carry a trailing // comment after the DATA literal
    m = re.search(r'let DATA = (\[.*?\]);[ \t]*(?://[^\n]*)?\n', src, re.S)
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
    json.loads(re.search(r'let DATA = (\[.*?\]);[ \t]*(?://[^\n]*)?\n', src, re.S).group(1))
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

CSV_HDR = ['id', 'address', 'lot_type', 'last_list_price', 'builder', 'agent',
           'lot_sqft', 'building_sqft', 'mls_number', 'date_off_market',
           'disposition', 'lat', 'lng', 'notes']


def fold_events(changes=None):
    """Full fold: off/relist/pending state plus newest-wins dispositions and
    drop dates. 'under contract' ids move from off to pending (they are not
    Off Market until they resolve to sold or terminated)."""
    idx_path = os.path.join(CHANGES_DIR, 'index.json')
    if changes is None and not os.path.exists(idx_path):
        # a market with no changelog yet (pre-first-refresh port) folds to empty
        print(f'note: {os.path.relpath(idx_path, ROOT)} absent — empty reconcile state')
        return {}, {}, {}, {}, {}
    if changes is None:
        with open(idx_path, encoding='utf-8') as f:
            idx=json.load(f)
        changes=[]
        for entry in idx['files']:
            with open(os.path.join(CHANGES_DIR,entry['file']),encoding='utf-8') as f:
                changes.append(json.load(f))
    off, rel, disp, ddate = {}, {}, {}, {}
    for c in changes:
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
        # Archived duplicate identities retain history but must not create a second
        # reconciliation/CSV row for the canonical property.
        for archived in c.get('archived_duplicates', []) + c.get('archived_out_of_zone', []):
            old_id = archived['record']['id']
            if old_id == archived.get('canonical'):
                raise ValueError('Duplicate archive cannot retire its canonical id')
            for bucket in (off, rel, disp, ddate):
                bucket.pop(old_id, None)
    pend = {i: off.pop(i) for i in [i for i in off
            if disp.get(i, ('', ''))[0] == 'under contract']}
    return off, rel, pend, disp, ddate


def cmd_csv(html_path, folded=None, write=True):
    src = load_html(html_path)
    data = {d['id']: d for d in extract_data(src)}
    sp = json.loads(re.search(r'SEED_POINTS=(\{.*?\});\nif\(Object', src, re.S).group(1))
    off, rel, pend, disp, ddate = (
        fold_events() if folded is None else folded)
    # manual note corrections from the Off Market table (pull-edits snapshot):
    # an overlay note, when present, outranks seed/carried notes — it is the
    # newest explicit human statement about the row
    om = load_overlay_snapshot()
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
        if CSV_NAME=='heights_off_market.csv' and p.get('disposition')=='unconfirmed':
            out.append(dict(p))
            continue
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
            'notes': ((om.get(i) or {}).get('note')
                      if (om.get(i) or {}).get('note') is not None
                      else ((sp.get(i) or {}).get('notes') or p.get('notes', ''))),
        })
    buffer=io.StringIO(newline='')
    w=csv.DictWriter(buffer,fieldnames=CSV_HDR,lineterminator='\n')
    w.writeheader()
    w.writerows(out)
    text=buffer.getvalue()
    if write:
        Path(path).write_text(text)
        print(f'wrote {CSV_NAME}: {len(out)} rows')
    return text


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


# ---------- pull-edits: fold browser off-market corrections into the changelog ----------

SNAPSHOT_NAME = 'remote_edits_snapshot.json'


def _extract_remote_url(src):
    m = re.search(r"const REMOTE_EDITS_URL='([^']*)'", src)
    return m.group(1) if m else ''


def load_overlay_snapshot():
    """offMarketEdits from the last pull-edits run, or {} if never pulled."""
    path = os.path.join(STAGING_DIR, SNAPSHOT_NAME)
    if not os.path.exists(path):
        return {}
    with open(path, encoding='utf-8') as f:
        return json.load(f).get('offMarketEdits', {})


def cmd_pull_edits(html_path, apply_=False):
    """Fetch offMarketEdits from the shared edits store. The changelog stays
    canonical: overlay dispositions newer than the newest changelog ruling are
    folded into changes/ (with --apply); stale or unknown entries are skipped.
    Overlay notes are snapshotted for cmd_csv and never enter the changelog."""
    from datetime import date as _date
    today = str(_date.today())
    src = load_html(html_path)
    url = _extract_remote_url(src)
    if not url:
        raise SystemExit('FATAL: REMOTE_EDITS_URL is empty in %s — nothing to pull'
                         % os.path.basename(html_path))
    import urllib.request
    raw = urllib.request.urlopen(url, timeout=60).read().decode('utf-8')
    try:
        blob = json.loads(raw)
    except ValueError:
        raise SystemExit('FATAL: remote edits store returned non-JSON')
    om = blob.get('offMarketEdits') or {}
    if not isinstance(om, dict):
        raise SystemExit('FATAL: offMarketEdits is not an object')
    os.makedirs(STAGING_DIR, exist_ok=True)
    with open(os.path.join(STAGING_DIR, SNAPSHOT_NAME), 'w', encoding='utf-8') as f:
        json.dump({'fetched': today, 'offMarketEdits': om}, f, ensure_ascii=False, indent=1)
        f.write('\n')
    off, rel, pend, disp, ddate = fold_events()
    known = set(off) | set(pend)
    proposed = {}
    for i in sorted(om):
        e = om[i] if isinstance(om[i], dict) else {}
        dv = e.get('disposition')
        if not dv:
            continue
        if dv not in LIFE_NOTES:
            print(f'  SKIP  {i}: unknown disposition {dv!r}')
            continue
        if i not in known:
            print(f'  SKIP  {i}: not an off-market/pending id in the changelog')
            continue
        cur, curdate = disp.get(i, ('', ''))
        if dv == cur:
            continue
        odate = str(e.get('updated') or '')[:10]
        if odate and curdate and odate < curdate:
            print(f'  STALE {i}: overlay {dv} ({odate}) older than changelog {cur} ({curdate})')
            continue
        proposed[i] = dv
        print(f'  {i:38s} {cur or "-"} -> {dv} (edited {odate or "?"})')
    n_notes = sum(1 for e in om.values() if isinstance(e, dict) and e.get('note') is not None)
    print(f'pull-edits: {len(om)} overlay entries, {len(proposed)} disposition updates, '
          f'{n_notes} notes (notes apply at csv regen)')
    if not apply_:
        prop = os.path.join(STAGING_DIR, f'pull_edits_proposed_{today}.json')
        with open(prop, 'w', encoding='utf-8') as f:
            json.dump({'date': today, 'dispositionUpdates': proposed},
                      f, ensure_ascii=False, indent=1)
            f.write('\n')
        print(f'(dry run) proposal -> staging/pull_edits_proposed_{today}.json '
              '— rerun with --apply to fold into changes/')
        return
    if not proposed:
        print('nothing to apply')
        return
    r = os.system('git -C "%s" pull --ff-only -q' % ROOT)
    if r != 0:
        raise SystemExit('FATAL: git pull --ff-only failed — resolve divergence first')
    fn = os.path.join(CHANGES_DIR, f'changes_{today}.json')
    if os.path.exists(fn):
        with open(fn, encoding='utf-8') as f:
            chg = json.load(f)
        chg.setdefault('dispositionUpdates', {}).update(proposed)
    else:
        chg = {'date': today, 'sources': ['pull-edits'],
               'counts': {'matched': 0, 'dropped': 0, 'new': 0,
                          'relisted': 0, 'excluded': 0},
               'matchedIds': [], 'dropped': [], 'relisted': [], 'new': [],
               'excluded': [], 'dispositionUpdates': proposed}
    with open(fn, 'w', encoding='utf-8') as f:
        json.dump(chg, f, ensure_ascii=False, indent=1)
        f.write('\n')
    rebuild_index()
    print(f'applied {len(proposed)} disposition updates -> changes/{os.path.basename(fn)}; '
          'run generate + csv + life-sync next')


# ---------- stage (d): staging of new listings ----------


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


def csv_record_bytes(text):
    lines=text.splitlines(keepends=True)
    reader=csv.DictReader(io.StringIO(text))
    if reader.fieldnames!=CSV_HDR:
        raise ValueError('Unexpected off-market CSV header')
    start=reader.line_num
    result={}
    for row in reader:
        if row['id'] in result:
            raise ValueError('Duplicate off-market CSV id')
        result[row['id']]=(row,''.join(lines[start:reader.line_num]).encode())
        start=reader.line_num
    return result


def cmd_dispositions(args,html_path):
    from combined_market_ingest import load_many
    from market_address import address_key
    from market_linkage import resolve
    from deed_ingest import span
    from market_status_ingest import csvtxt

    if args.market!='heights' or Path(html_path).resolve()!=Path(ROOT,'index.html'):
        raise ValueError('This disposition refresh is Heights only')
    date.fromisoformat(args.date)
    if args.apply:
        subprocess.run(
            ['git','-C',ROOT,'pull','--ff-only','-q'],
            check=True,stdout=sys.stderr)

    html=Path(html_path).read_text()
    index_path=Path(CHANGES_DIR,'index.json')
    index=json.loads(index_path.read_text())
    if any(e['date']>args.date for e in index['files']):
        raise ValueError('Later changelog exists; refusing historical overwrite')
    filename=f'changes_{args.date}.json'
    event_path=Path(CHANGES_DIR,filename)
    if event_path.exists():
        prior=json.loads(event_path.read_text())
        if prior.get('kind')!='pending_disposition_refresh':
            raise ValueError('Run-date changelog belongs to another operation')

    # Always compare against the pre-run history, including on pass two.
    earlier=[
        json.loads(Path(CHANGES_DIR,e['file']).read_text())
        for e in index['files'] if e['date']<args.date]
    baseline=fold_events(earlier)
    pending=baseline[2]
    data={r['id']:r for r in extract_data(html)}
    targets={}
    for rid in pending:
        if rid not in data:
            raise ValueError('Pending identity absent from DATA: '+rid)
        key_=address_key(data[rid]['a'])
        if key_ in targets:
            raise ValueError('Ambiguous pending address: '+key_)
        targets[key_]=rid

    incoming,excluded,profile=load_many(args.input,html,args.date)
    groups={}
    for rec in incoming:
        if not rec['exclusion'] and rec['address_key'] in targets:
            groups.setdefault(targets[rec['address_key']],[]).append(rec)

    chg=dict(
        date=args.date,kind='pending_disposition_refresh',
        sources=[str(Path(p)) for p in args.input],
        source_hashes={
            str(Path(p)):hashlib.sha256(Path(p).read_bytes()).hexdigest()
            for p in args.input},
        matchedIds=[],dropped=[],relisted=[],new=[],excluded=[],
        dispositionUpdates={})
    transitions=[];holds=[];chosen={}
    for rid in sorted(pending):
        if rid not in groups:
            holds.append(dict(id=rid,address=data[rid]['a'],reason='NO_SOURCE_EVIDENCE'))
            continue
        result=resolve(groups[rid])
        if result['ordering_issue']:
            raise ValueError('Unresolved listing order: '+data[rid]['a'])
        current=result['current']
        chosen[rid]=current['mls']
        status=current['status']
        if status=='pending':
            chg['matchedIds'].append(rid)
            holds.append(dict(id=rid,address=data[rid]['a'],reason='STILL_PENDING'))
        elif status=='active':
            chg['relisted'].append(dict(
                id=rid,a=data[rid]['a'],ty=pending[rid]['t'],
                mls=current['mls']))
            transitions.append(dict(id=rid,address=data[rid]['a'],
                                    before='pending',after='active'))
        elif status in ('sold','terminated'):
            chg['dropped'].append(dict(
                id=rid,a=data[rid]['a'],ty=pending[rid]['t'],
                disposition=status,mls=current['mls'],
                close_date=current['close_date']))
            transitions.append(dict(id=rid,address=data[rid]['a'],
                                    before='pending',after=status))
        else:
            raise ValueError('Unsupported disposition: '+status)

    audit=[]
    for rec in incoming:
        rid=targets.get(rec['address_key'])
        decision=rec['exclusion']
        if not decision:
            decision=(
                'OUTSIDE_PENDING_REFRESH_SCOPE' if rid is None else
                'SELECTED_CURRENT_STATUS' if chosen.get(rid)==rec['mls'] else
                'RETAINED_LISTING_HISTORY')
        audit.append(dict(
            FILE=rec['source_file'],SHA256=rec['source_sha256'],
            ROW=rec['source_row'],MLS=rec['mls'],ADDRESS=rec['address'],
            REASON=decision,RAW_JSON=json.dumps(rec['raw'],sort_keys=True)))
    chg['excluded']=excluded
    chg['counts']=dict(
        matched=len(chg['matchedIds']),dropped=len(chg['dropped']),
        relisted=len(chg['relisted']),new=0,excluded=len(excluded))
    folded=fold_events(earlier+[chg])
    off,rel,pend=folded[:3]
    rec=dict(off=off,relist=rel,pending=pend)
    block=(
        MARK_BEGIN+'\nconst RECONCILE='+
        json.dumps(rec,ensure_ascii=False,separators=(',',':'))+
        ';\n'+MARK_END)
    if html.count(MARK_BEGIN)!=1 or html.count(MARK_END)!=1:
        raise ValueError('RECONCILE markers missing or ambiguous')
    a=html.index(MARK_BEGIN);b=html.index(MARK_END)+len(MARK_END)
    candidate=html[:a]+block+html[b:]

    # Clear pending only for authoritative off/relist state.
    a=candidate.index('function applyReconcile(pts){')
    b=candidate.index('applyReconcile(state.points);',a)
    function=candidate[a:b]
    for old,new in [
        ("t!=='active_single'&&t!=='active_split'",
         "t!=='active_single'&&t!=='active_split'&&t!=='pending'"),
        ("t!=='off_market_single'&&t!=='off_market_split'",
         "t!=='off_market_single'&&t!=='off_market_split'&&t!=='pending'")]:
        # Only the first off-market filter is the relist branch.
        if new not in function:
            if old not in function:
                raise ValueError('Reconcile tag-filter anchor missing')
            function=function.replace(old,new,1)
    candidate=candidate[:a]+function+candidate[b:]
    validate_spliced(candidate)
    a,b,_=span(html,'DATA');c,d,_=span(candidate,'DATA')
    if html[a:b].encode()!=candidate[c:d].encode():
        raise ValueError('DATA bytes changed')

    csv_path=Path(ROOT,CSV_NAME)
    old_csv=csv_record_bytes(csv_path.read_text())
    csv_text=cmd_csv(html_path,folded=folded,write=False)
    new_csv=csv_record_bytes(csv_text)
    protected={
        rid:raw for rid,(row,raw) in old_csv.items()
        if row['disposition']=='unconfirmed'}
    for rid,raw in protected.items():
        if rid not in new_csv or new_csv[rid][1]!=raw:
            raise ValueError('Unconfirmed CSV row changed: '+rid)
    if set(pend)&set(new_csv):
        raise ValueError('Pending record present in off-market CSV')

    entries=[e for e in index['files'] if e['file']!=filename]
    entries.append(dict(file=filename,date=args.date,counts=chg['counts']))
    entries.sort(key=lambda e:(e['date'],e['file']))
    encode_json=lambda value:json.dumps(value,ensure_ascii=False,indent=1)+'\n'
    outputs={
        event_path:encode_json(chg),
        index_path:encode_json(dict(files=entries,updated=entries[-1]['date'])),
        Path(html_path):candidate,
        csv_path:csv_text,
        Path(ROOT,f'pulls/dispositions_{args.date}.csv'):csvtxt(
            audit,['FILE','SHA256','ROW','MLS','ADDRESS','REASON','RAW_JSON'])}
    changed=[
        str(p.relative_to(ROOT)) for p,text in outputs.items()
        if not p.exists() or p.read_bytes()!=text.encode()]
    report=dict(
        profile=profile,transitions=transitions,holds=holds,
        preserved_unconfirmed=len(protected),ledger_rows=len(audit),
        changed_files=changed)
    if args.apply:
        for path,text in outputs.items():
            if str(path.relative_to(ROOT)) in changed:
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(text.encode())
    print(json.dumps(report,indent=2))


# ---------- har: four-file HAR status refresh (active, pending, sold, terminated) ----------

HAR_ROLES = ('active', 'pending', 'sold', 'terminated')
HAR_LEDGER = ['FILE', 'SHA256', 'ROW', 'MLS', 'ADDRESS', 'REASON', 'RAW_JSON']
HAR_AUDIT = ['FILE', 'SHA256', 'ROW', 'MLS', 'ADDRESS', 'HAR_STATUS', 'MEMBER', 'METHOD', 'DECISION']
SPLIT_MANIFEST = 'split_manifest.json'


def split_manifest(paths, hashes, market):
    """The har-split manifest vouching for these four slices, or None for direct exports.
    A slice set must be complete, cut for this market, and byte-identical to the cut."""
    found = {p.parent / SPLIT_MANIFEST for p in paths.values() if (p.parent / SPLIT_MANIFEST).is_file()}
    if not found:
        return None
    if len(found) != 1 or any(p.parent / SPLIT_MANIFEST not in found for p in paths.values()):
        raise SystemExit('FATAL: har-split slices must all come from one split directory')
    manifest = json.loads(next(iter(found)).read_text())
    if manifest.get('market') != market:
        raise SystemExit(f"FATAL: these slices were cut for {manifest.get('market')}, not {market}")
    for role, p in paths.items():
        cut = manifest['slices'].get(role) or {}
        if cut.get('file') != p.name or cut.get('sha256') != hashes[role]:
            raise SystemExit(f'FATAL: --{role} {p.name} does not match the split manifest; re-run har-split')
        if not manifest['sources'][role]['rows']:
            raise SystemExit(f'FATAL: the zip-wide {role} export behind this slice was empty')
    return manifest


def cmd_har_split(args):
    """Cut zip-wide HAR exports into per-market slices for `har`. Writes pulls/ only.

    Each enabled market receives every row its own zone guard accepts (OUT_OF_ZONE regex,
    Heights east cutoff, boundary ring) — the same rows a
    market-specific export would hold. Rows inside two markets go to both: sending a
    shared listing to only one would make the other read its pin as a disappearance.
    Rows no enabled market accepts are ledgered with every market's reason."""
    from collections import Counter
    import market_config
    from combined_market_ingest import zone_guard, STATUS, REQUIRED, READ
    from sold_ingest import money
    from market_status_ingest import csvtxt

    run_date = date.fromisoformat(args.date).isoformat()
    markets = [m for m in market_config.INGEST_ORDER if market_config.MARKETS[m]['enabled']]
    guards = {m: zone_guard(Path(ROOT, market_config.MARKETS[m]['html']).read_text(), m) for m in markets}
    out_dir = Path(args.out) if args.out else Path(ROOT, 'pulls', f'har_split_{run_date}')
    if out_dir.resolve().is_relative_to(Path(ROOT).resolve()) and \
            not out_dir.resolve().is_relative_to(Path(ROOT, 'pulls').resolve()):
        raise SystemExit(f'FATAL: --out {out_dir} sits in the deployed tree; use pulls/')
    if out_dir.is_dir():
        import shutil
        for stale in out_dir.glob('*/' + SPLIT_MANIFEST):
            shutil.rmtree(stale.parent)

    sources, slices, unplaced, owners_of = {}, {m: {} for m in markets}, [], {}
    for role in HAR_ROLES:
        p = Path(getattr(args, role))
        if not p.is_file() or p.stat().st_size == 0:
            raise SystemExit(f'FATAL: --{role} {p} is missing or empty — refusing to split')
        if p.resolve().is_relative_to(Path(ROOT).resolve()) and \
                not p.resolve().is_relative_to(Path(ROOT, 'pulls').resolve()):
            raise SystemExit(f'FATAL: --{role} {p} sits in the deployed tree; read exports from outside the repo or pulls/')
        payload = p.read_bytes()
        reader = csv.DictReader(io.StringIO(payload.decode('utf-8-sig'), newline=''))
        rows = list(reader)
        if not rows:
            raise SystemExit(f'FATAL: --{role} {p} has a header but no rows — refusing to split')
        missing = [c for c in REQUIRED + READ if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f'FATAL: --{role} {p.name} is missing columns {missing}')
        digest = hashlib.sha256(payload).hexdigest()
        sources[role] = dict(file=str(p), sha256=digest, rows=len(rows),
                             statuses=dict(Counter(r['Status'].strip() for r in rows)))
        unknown = sorted({s for s in sources[role]['statuses'] if s not in STATUS})
        if unknown:
            raise SystemExit(f'FATAL: --{role} {p.name} has unknown statuses {unknown}')
        for m in markets:
            slices[m][role] = dict(fieldnames=reader.fieldnames, rows=[], source=p.name)
        for line, raw in enumerate(rows, 2):
            address = (raw.get('Address') or '').strip()
            lat, lng = money(raw.get('Latitude')), money(raw.get('Longitude'))
            entry = dict(FILE=p.name, SHA256=digest, ROW=line, MLS=raw.get('MLS Number', '').strip(),
                         ADDRESS=address, RAW_JSON=json.dumps(raw, sort_keys=True))
            if not address or lat is None or lng is None or not (-90 <= lat <= 90 and -180 <= lng <= 180):
                unplaced.append(dict(entry, REASON='INVALID_ADDRESS_OR_COORDINATES'))
                continue
            reasons = {m: guards[m](address, lng, lat) for m in markets}
            owners = [m for m in markets if reasons[m] is None]
            for m in owners:
                slices[m][role]['rows'].append(raw)
            owners_of[(role, line)] = owners
            if not owners:
                unplaced.append(dict(entry, REASON='NO_MARKET ' + ' '.join(f'{m}:{r}' for m, r in reasons.items())))

    report = dict(date=run_date, out=str(out_dir), sources=sources, markets={}, held={},
                  shared=dict(Counter('+'.join(o) for o in owners_of.values() if len(o) > 1)),
                  unplaced=dict(Counter(e['REASON'].split(' ')[0] for e in unplaced)),
                  unplaced_rows=[f"{e['MLS']} {e['ADDRESS']} [{e['FILE']}] {e['REASON']}" for e in unplaced])
    writes = {out_dir / 'unplaced.csv': csvtxt(unplaced, HAR_LEDGER)}
    for m in markets:
        counts = {role: len(slices[m][role]['rows']) for role in HAR_ROLES}
        if not counts['active']:
            report['held'][m] = dict(counts, reason='no active rows inside this market — an empty actives '
                                                    'slice would read every listed pin as gone')
            continue
        mdir = out_dir / m
        manifest = dict(market=m, date=run_date, sources=sources, slices={})
        for role in HAR_ROLES:
            s = slices[m][role]
            buf = io.StringIO(newline='')
            w = csv.DictWriter(buf, fieldnames=s['fieldnames'], quoting=csv.QUOTE_ALL, lineterminator='\n')
            w.writeheader()
            w.writerows(s['rows'])
            name = f"{role}_{s['source']}"
            writes[mdir / name] = buf.getvalue()
            manifest['slices'][role] = dict(file=name, rows=counts[role],
                                            sha256=hashlib.sha256(buf.getvalue().encode()).hexdigest())
        writes[mdir / SPLIT_MANIFEST] = json.dumps(manifest, indent=2) + '\n'
        flags = ' '.join(f'--{role} {mdir / manifest["slices"][role]["file"]}' for role in HAR_ROLES)
        runtime = ' --runtime <timeline_browser capture>' if m == 'heights' else ''
        report['markets'][m] = dict(counts, command=f'python3 refresh/refresh.py har --market {m} '
                                                    f'--date {run_date} {flags}{runtime}')
    for p, text in writes.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.encode())
    (out_dir / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return report


# Street-type words are optional in listing addresses ("1202 W Drew" is
# "1202 W Drew St"); house numbers, directionals and unit letters stay significant.
STREET_TYPES = frozenset({'st', 'ave', 'ln', 'dr', 'rd', 'ct', 'pl', 'blvd', 'way', 'cir',
                          'pkwy', 'trl', 'ter', 'hwy', 'speedway'})
LOOSE_LINK_METERS = 150
EXACT_LINK_METERS = 500


def type_free_key(addr):
    from market_address import address_key
    return ' '.join(w for w in address_key(addr).split() if w not in STREET_TYPES)


def is_deed_pin(d):
    return d.get('prod') == 'Deed Transfer' or str(d.get('id', '')).startswith('acq_')


def har_link(matcher, data, rec):
    """Matcher.match plus two identity fallbacks for one HAR row. A corporate-deed
    pin (acq_) sharing the address of a permit/listing pin is the same parcel, so
    the non-deed pin takes the row instead of the whole address going ambiguous.
    With no exact address hit, an address equal once street types are dropped
    links when exactly one such pin sits within LOOSE_LINK_METERS."""
    from market_linkage import distance
    m = matcher.match(rec)
    target = type_free_key(rec['address'])
    if m['issue'] == 'AMBIGUOUS_IDENTITY':
        cands = [data[i] for i in m['candidates'] if i in data]
        live = [d for d in cands if not is_deed_pin(d)]
        if (len(cands) == len(m['candidates']) and len(live) == 1
                and all(type_free_key(d['a']) == target for d in cands)):
            return dict(method='address_deed_twin', member=live[0]['id'], pin=live[0]['id'],
                        issue=None, candidates=m['candidates'])
    elif m['issue'] in ('NOT_TRACKED', 'AMBIGUOUS_COORDINATE', 'COORDINATE_IDENTITY_CONFLICT'):
        near = [d for d in data.values() if type_free_key(d['a']) == target and d.get('lat')
                and d.get('lng') and distance(rec, d) <= LOOSE_LINK_METERS]
        live = [d for d in near if not is_deed_pin(d)] or near
        if len(live) == 1:
            return dict(method='address_loose', member=live[0]['id'], pin=live[0]['id'],
                        issue=None, candidates=[d['id'] for d in near])
    return m


def har_state(src, folded):
    """Displayed listing state per DATA id: (bucket, disposition, t), bucket in
    listed/pending/off. Bucketed ids follow the fold; the rest follow their seed
    tags, or kind=='active' when the pin has no seed entry."""
    off, rel, pend, disp, _ = folded
    data = {d['id']: d for d in extract_data(src)}
    sp = json.loads(re.search(r'SEED_POINTS=(\{.*?\});\nif\(Object', src, re.S).group(1))
    state = {}
    for i, d in data.items():
        if i in off:
            state[i] = ('off', disp.get(i, ('unconfirmed', ''))[0], off[i]['t'], off[i]['d'])
        elif i in pend:
            state[i] = ('pending', 'under contract', pend[i]['t'], pend[i]['d'])
        elif i in rel:
            state[i] = ('listed', None, rel[i]['t'], rel[i]['d'])
        else:
            tags = (sp.get(i) or {}).get('tags', [])
            t = ('split' if any(x.endswith('_split') for x in tags) else
                 'single' if any(x.endswith('_single') for x in tags) else None)
            if any(x in ('active_single', 'active_split') for x in tags) or (i not in sp and d.get('kind') == 'active'):
                state[i] = ('listed', None, t, None)
            elif 'pending' in tags:
                state[i] = ('pending', 'under contract', t, None)
            elif any(x.startswith('off_market') for x in tags):
                state[i] = ('off', 'unconfirmed', t, None)
    return data, state


def har_classify(data, state, groups, prior, seen_mls, prior_as_of, reviews=None):
    """Listing diff for one four-file refresh.

    groups: id -> linked in-zone rows; prior: id -> prior current HAR record
    (mls, status); seen_mls: every MLS observed before this run. Active/pending
    rows are current by definition; a sold/terminated row is current evidence
    only for the prior current MLS, a sale closed after prior_as_of, an MLS never
    seen before, or a pin with no prior observation. Pending never goes off market:
    it is dropped as 'under contract' and folds into RECONCILE.pending."""
    from market_linkage import resolve
    reviews = reviews or {}
    out = dict(matchedIds=[], pending=[], dropped=[], relisted=[], dispositionUpdates={},
               transitions=[], unresolved=[], staged=[], evidence=[], observed={}, decisions={})
    before_label = lambda st: {'listed': 'active', 'pending': 'pending'}.get(st[0], st[1])
    for i in sorted(set(state) | set(groups)):
        d, st, pc, rows = data[i], state.get(i), prior.get(i), groups.get(i, [])
        def current(r):
            return (r['status'] in ('active', 'pending') or pc is None or r['mls'] == pc['mls']
                    or r['mls'] not in seen_mls
                    or (r['status'] == 'sold' and (r['close_date'] or '') > prior_as_of))
        live = [r for r in rows if current(r)]
        res = resolve(live)['current'] if live else None
        status = res['status'] if res else None
        ty = (st[2] if st and st[2] else
              'split' if d.get('ty') == 'active_split' or d.get('prod') == 'Split Lot' else 'single')
        def transition(before, after, mls):
            out['transitions'].append(dict(member=i, address=d['a'], before=before, after=after,
                                           mls=mls, previous_mls=pc['mls'] if pc else None))
        def drop(status, rec):
            disposition = 'under contract' if status == 'pending' else status
            out['dropped'].append(dict(id=i, a=d['a'], ty=ty, disposition=disposition,
                                       har_status=rec['har_status'] if rec else None,
                                       mls=rec['mls'] if rec else pc['mls'],
                                       close_date=rec['close_date'] if rec else None))
            transition(before_label(st), 'unconfirmed' if rec is None else status,
                       rec['mls'] if rec else pc['mls'])
            out['decisions'][i] = ('DROPPED_' + disposition.upper().replace(' ', '_'), rec and rec['mls'])
        if st is None:
            if status in ('active', 'pending'):
                out['staged'].append((i, res))
                out['decisions'][i] = ('STAGED_MERGE_CANDIDATE', res['mls'])
            elif rows:
                out['evidence'].append(i)
                out['decisions'][i] = ('EVIDENCE_ONLY', res and res['mls'])
            continue
        bucket = st[0]
        if bucket == 'listed':
            if status == 'active':
                out['matchedIds'].append(i); out['observed'][i] = res['mls']
                out['decisions'][i] = ('MATCHED', res['mls'])
                if pc and pc['mls'] != res['mls']:
                    transition('active', 'active', res['mls'])
            elif status:
                drop(status, res)
            elif pc:
                drop('unconfirmed', None)   # prior current MLS absent from all four exports
            else:
                out['unresolved'].append(dict(id=i, mls=None, address=d['a'], reason=reviews.get(
                    i, 'Absent from all exports and never observed in HAR; status unverified')))
                out['decisions'][i] = ('HOLD', None)
        elif bucket == 'pending':
            if status == 'pending':
                out['matchedIds'].append(i); out['pending'].append(i); out['observed'][i] = res['mls']
                out['decisions'][i] = ('STILL_PENDING', res['mls'])
                if pc and pc['mls'] != res['mls']:
                    transition('pending', 'pending', res['mls'])
            elif status == 'active':
                out['relisted'].append(dict(id=i, a=d['a'], ty=ty, mls=res['mls']))
                transition('pending', 'active', res['mls'])
                out['decisions'][i] = ('RELISTED', res['mls'])
            elif status:
                drop(status, res)
            else:
                out['unresolved'].append(dict(id=i, mls=pc and pc['mls'], address=d['a'], reason=reviews.get(
                    i, 'Pending listing absent from all exports; kept pending')))
                out['decisions'][i] = ('HOLD', None)
        else:
            disposition = st[1]
            if status == 'active':
                out['relisted'].append(dict(id=i, a=d['a'], ty=ty, mls=res['mls'],
                                            **({'offSince': st[3]} if st[3] else {})))
                transition(disposition, 'active', res['mls'])
                out['decisions'][i] = ('RELISTED', res['mls'])
            elif status == 'pending':
                out['dispositionUpdates'][i] = 'under contract'
                transition(disposition, 'pending', res['mls'])
                out['decisions'][i] = ('DISPOSITION_UNDER_CONTRACT', res['mls'])
            elif status in ('sold', 'terminated') and status != disposition and (
                    disposition == 'unconfirmed' or (status == 'sold' and res['close_date'] >= (st[3] or ''))):
                out['dispositionUpdates'][i] = status
                transition(disposition, status, res['mls'])
                out['decisions'][i] = ('DISPOSITION_' + status.upper(), res['mls'])
            elif rows:
                out['decisions'][i] = ('NO_CHANGE', res and res['mls'])
    return out


def _skeleton(text, names):
    cuts = [(text.index(MARK_BEGIN), text.index(MARK_END) + len(MARK_END))]
    from deed_ingest import span
    cuts += [span(text, n)[:2] for n in names]
    pieces, pos = [], 0
    for a, b in sorted(cuts):
        pieces.append(text[pos:a]); pos = b
    return pieces + [text[pos:]]


def _prior_observations(earlier, snapshot):
    """MLS -> member continuity and per-member prior current record, from the
    market-status snapshot (Heights) and the mls fields of earlier changelogs."""
    links, prior, seen = {}, {}, set()
    for c in earlier:
        for e in c.get('dropped', []):
            if e.get('mls'):
                links.setdefault(e['mls'], set()).add(e['id'])
                prior[e['id']] = dict(mls=e['mls'], status={'under contract': 'pending'}.get(
                    e.get('disposition'), e.get('disposition')))
        for e in c.get('relisted', []):
            if e.get('mls'):
                links.setdefault(e['mls'], set()).add(e['id']); prior[e['id']] = dict(mls=e['mls'], status='active')
        for i, m in c.get('observed', {}).items():
            links.setdefault(m, set()).add(i); prior[i] = dict(mls=m, status='observed')
        for t in c.get('transitions', []):
            for k in ('mls', 'previous_mls'):
                if t.get(k):
                    links.setdefault(t[k], set()).add(t['member'])
    if snapshot:
        seen |= {r['mls'] for r in snapshot['records']}
        for k, p in snapshot['properties'].items():
            if k.startswith('address:'):
                continue
            prior[k] = p['current']
            for r in [p['current']] + p['history']:
                links.setdefault(r['mls'], set()).add(k)
    seen |= set(links)
    single = {m: next(iter(v)) for m, v in links.items() if len(v) == 1}
    ambiguous = {m: sorted(v) for m, v in links.items() if len(v) > 1}
    return single, ambiguous, prior, seen


def cmd_har(args, html_path):
    """Four-file HAR refresh for one market; dry run unless --apply."""
    from collections import Counter
    from datetime import timedelta
    import market_config
    import sold_comp_refresh
    from combined_market_ingest import load_many, zone_guard, snapshot, merge_evidence
    from market_linkage import Matcher
    from deed_ingest import span, encode
    from market_status_ingest import csvtxt, jsontxt

    cfg = market_config.MARKETS.get(args.market)
    if not cfg or not cfg['enabled']:
        raise SystemExit(f'FATAL: {args.market} is not an enabled market in market_config.py')
    if Path(html_path).resolve() != Path(ROOT, cfg['html']).resolve():
        raise SystemExit(f"FATAL: har writes {cfg['html']} only; --html {html_path} refused")
    html_path = os.path.join(ROOT, cfg['html'])
    run_date = date.fromisoformat(args.date).isoformat()
    heights = args.market == 'heights'
    paths = {role: Path(getattr(args, role)) for role in HAR_ROLES}
    for role, p in paths.items():
        if not p.is_file() or p.stat().st_size == 0:
            raise SystemExit(f'FATAL: --{role} {p} is missing or empty — refusing to refresh')
        inside = p.resolve().is_relative_to(Path(ROOT).resolve())
        if inside and not p.resolve().is_relative_to(Path(ROOT, 'pulls').resolve()):
            raise SystemExit(f'FATAL: --{role} {p} sits in the deployed tree; read exports from outside the repo or pulls/')
    if len({p.resolve() for p in paths.values()}) != len(paths):
        raise SystemExit('FATAL: the four exports must be distinct files')
    hashes = {role: hashlib.sha256(p.read_bytes()).hexdigest() for role, p in paths.items()}
    split = split_manifest(paths, hashes, args.market)
    for other, mk in MARKETS.items():
        if split:
            break
        cdir = Path(ROOT, 'changes', mk['sub']) if mk['sub'] else Path(ROOT, 'changes')
        if other == args.market or not cdir.is_dir():
            continue
        for f in cdir.glob('changes_*.json'):
            used = set(json.loads(f.read_text()).get('source_hashes', {}).values()) & set(hashes.values())
            if used:
                raise SystemExit(f'FATAL: these exports were already applied to {other} '
                                 f'({f.relative_to(ROOT)}); refusing to run them for {args.market}')
    if args.apply:
        try:
            subprocess.run(['git', '-C', ROOT, 'pull', '--ff-only', '-q'], check=True, stdout=sys.stderr)
        except subprocess.CalledProcessError:
            raise SystemExit('FATAL: git pull --ff-only failed — resolve divergence first')

    html = Path(html_path).read_text()
    if html.count(MARK_BEGIN) != 1 or html.count(MARK_END) != 1:
        raise SystemExit('FATAL: RECONCILE markers missing or ambiguous')
    index_path = Path(CHANGES_DIR, 'index.json')
    index = json.loads(index_path.read_text()) if index_path.exists() else dict(files=[], updated=None)
    if any(e['date'] > run_date for e in index['files']):
        raise SystemExit('FATAL: a later changelog exists; refusing historical overwrite')
    filename = f'changes_{run_date}.json'
    event_path = Path(CHANGES_DIR, filename)
    if event_path.exists():
        raise SystemExit(f'FATAL: {event_path.relative_to(ROOT)} already exists; refusing to overwrite')
    earlier = [json.loads(Path(CHANGES_DIR, e['file']).read_text()) for e in index['files']]
    baseline = fold_events(earlier)
    current = json.loads(re.search(r'const RECONCILE=(\{.*?\});', html, re.S).group(1))
    if current != dict(off=baseline[0], relist=baseline[1], pending=baseline[2]):
        raise SystemExit('FATAL: RECONCILE block differs from the changelog fold — run generate first')

    try:
        incoming, ledger, profile = load_many([paths[r] for r in HAR_ROLES], html, run_date,
                                              zone=zone_guard(html, args.market),
                                              allow_empty=[paths[r] for r in HAR_ROLES if split and r != 'active'])
    except ValueError as e:
        raise SystemExit(f'FATAL: {e}')
    role_of = {hashes[r]: r for r in HAR_ROLES}
    for rec in incoming:
        role = role_of[rec['source_sha256']]
        if not rec['exclusion'] and rec['status'] != role:
            rec['exclusion'] = 'NOT_' + role.upper()
            ledger.append(dict(FILE=rec['source_file'], SHA256=rec['source_sha256'], ROW=rec['source_row'],
                               MLS=rec['mls'], ADDRESS=rec['address'], REASON=rec['exclusion'],
                               RAW_JSON=json.dumps(rec['raw'], sort_keys=True)))
    inzone = [r for r in incoming if not r['exclusion']]
    if not inzone:
        raise SystemExit(f'FATAL: no row in these exports is inside {args.market}; wrong market export?')

    data, state = har_state(html, baseline)
    old_snapshot = None
    if heights:
        old_snapshot = json.loads(Path(ROOT, 'heights_market_status.data.json').read_text())
        if old_snapshot['as_of'] >= run_date:
            raise SystemExit('FATAL: heights_market_status.data.json is already at or after ' + run_date)
    links, ambiguous_links, prior, seen_mls = _prior_observations(earlier, old_snapshot)
    prior_as_of = old_snapshot['as_of'] if old_snapshot else max([c['date'] for c in earlier], default='')
    links = {m: i for m, i in links.items() if i in data}
    matcher = Matcher(list(data.values()), {'raw': list(data.values())})
    groups, unlinked, reviews, linkinfo = {}, [], {}, {}
    for r in inzone:
        m = har_link(matcher, data, r)
        member, method = links.get(r['mls']), 'prior_mls'
        if member is None and not m['issue']:
            member, method = m['member'], m['method']
        if member and m['member'] and m['member'] != member and not m['issue']:
            reviews[m['member']] = (f"Identity review: MLS {r['mls']} ({r['address']}) matches this pin by "
                                    f"{m['method']} but continues listing {member} by prior MLS")
        linkinfo[(r['source_sha256'], r['source_row'])] = (member, method if member else m['issue'])
        if member:
            groups.setdefault(member, []).append(r)
        else:
            unlinked.append(r)
    diff = har_classify(data, state, groups, prior, seen_mls, prior_as_of, reviews)

    day = date.fromisoformat(run_date)
    label = day.strftime('%B ') + str(day.day)
    staged, new_entries = [], []
    def stage(rec, candidate):
        prod = rec['product'] if rec['product'] != 'Unknown' else ''
        subdiv = (rec['raw'].get('Subdivision') or '').strip()
        agent = rec['raw'].get('List Agent Full Name', '')
        ty = 'active_split' if prod == 'Split Lot' else 'active_single'
        sd = str(day - timedelta(days=int(rec['dom']))) if rec['dom'] is not None else ''
        pid = slug_id(rec['address'])
        drec = {'id': pid, 'a': rec['address'], 'llc': rec['builder'],
                'v': fmt_price(rec['raw'].get('Current Price') or rec['raw'].get('Original List Price', '')),
                'sd': sd, 'lot': rec['raw'].get('Building SqFt', ''), 'kind': 'active', 'bb': '',
                'prod': prod, 'f': f'{prod}, {subdiv}' if subdiv and subdiv.upper() != 'NA' else prod,
                'u': '', 'lat': rec['lat'], 'lng': rec['lng'],
                'c': [{'n': agent, 'p': [], 'e': []}], 'ty': ty}
        tag = 'pending' if rec['status'] == 'pending' else ty
        note = f"{'Pending' if rec['status'] == 'pending' else 'Active'} inventory — {prod or 'lot size unknown'}."
        if rec['builder']:
            note += f" Builder: {rec['builder']}."
        if agent:
            note += f' Agent: {agent}.'
        note += ' (location from HAR export coordinates).'
        staged.append({'id': pid, 'a': rec['address'], 'geocode': 'HAR', 'mergeCandidate': candidate,
                       'mls': rec['mls'], 'har_status': rec['har_status'], 'data': drec,
                       'seed': {'notes': note, 'tags': [tag]}})
        new_entries.append({'a': rec['address'], 'prod': prod, 'mls': rec['mls'], 'har_status': rec['har_status'],
                            'staged': True, 'mergeCandidate': candidate})
    for i, rec in diff['staged']:
        stage(rec, i)
    for rec in unlinked:
        if rec['status'] in ('active', 'pending'):
            stage(rec, None)

    chg = dict(date=run_date, kind='har_incremental_refresh',
               sources=[paths[r].name for r in HAR_ROLES],
               source_hashes={paths[r].name: hashes[r] for r in HAR_ROLES})
    chg['counts'] = dict(matched=len(diff['matchedIds']), dropped=len(diff['dropped']),
                         relisted=len(diff['relisted']), new=len(new_entries), excluded=len(ledger))
    chg.update(matchedIds=sorted(diff['matchedIds']), dropped=diff['dropped'], relisted=diff['relisted'],
               new=new_entries, excluded=[{k: v for k, v in e.items() if k != 'RAW_JSON'} for e in ledger],
               dispositionUpdates=diff['dispositionUpdates'], unresolved=diff['unresolved'],
               transitions=diff['transitions'], observed=diff['observed'])
    folded = fold_events(earlier + [chg])
    off, rel, pend = folded[:3]
    for a, b in (('off', 'relist'), ('off', 'pending'), ('relist', 'pending')):
        overlap = set(dict(off=off, relist=rel, pending=pend)[a]) & set(dict(off=off, relist=rel, pending=pend)[b])
        if overlap:
            raise SystemExit(f'FATAL: {a}/{b} overlap after fold: {sorted(overlap)}')
    if any(folded[3].get(i, ('',))[0] == 'under contract' for i in off):
        raise SystemExit('FATAL: an under-contract id folded into off')
    block = (MARK_BEGIN + '\nconst RECONCILE=' +
             json.dumps(dict(off=off, relist=rel, pending=pend), ensure_ascii=False, separators=(',', ':')) +
             ';\n' + MARK_END)
    a, b = html.index(MARK_BEGIN), html.index(MARK_END) + len(MARK_END)
    candidate = html[:a] + block + html[b:]

    sold_names, sold_report, comp, review = [], None, None, None
    sold_recs = [r for r in incoming if role_of[r['source_sha256']] == 'sold']
    sold_profile = next(f for f in profile['files'] if Path(f['file']) == paths['sold'])
    if 'const SOLD_COMP_POLICY=' in html and 'const SOLD_EVIDENCE=' in html:
        sold_names = ['SOLD_EVIDENCE', 'SOLD_COMP_POLICY', 'SOLD_DATA', 'SOLD_METRICS']
        evidence0 = span(html, 'SOLD_EVIDENCE')[2]
        evidence1, merge_report = merge_evidence(evidence0, sold_recs)
        scope = sold_comp_refresh.window_scope(sold_profile['close_min'], run_date)
        try:
            comp = sold_comp_refresh.rolling(html, sold_recs, run_date, evidence1, scope)
        except ValueError as e:
            raise SystemExit(f'FATAL: {e}')
        for name, value in [('SOLD_EVIDENCE', comp['evidence']), ('SOLD_COMP_POLICY', comp['policy']),
                            ('SOLD_DATA', comp['comps']), ('SOLD_METRICS', comp['metrics'])]:
            s, e, prior_value = span(candidate, name)
            if prior_value != value:
                candidate = candidate[:s] + encode(value) + candidate[e:]
        held = {r['id'] for r in evidence0}
        sold_report = dict({k: v for k, v in comp['report'].items() if k != 'evidence'},
                           restored_from_evidence=[m for m in comp['report']['added'] if 's' + m in held],
                           evidence_before=len(evidence0), evidence_after=len(comp['evidence']),
                           evidence_added=merge_report['added'], evidence_updated=merge_report['updated'])
        chg['sold_refresh'] = {k: sold_report[k] for k in ('before', 'after', 'added', 'updated',
                               'retired_outside_window', 'start', 'coverage')}
        chg['sold_refresh'].update(scope=sold_report['scope'], restored_from_evidence=sold_report['restored_from_evidence'])
    else:
        review = dict(date=run_date, market=args.market, html=cfg['html'],
                      note=f"{cfg['html']} has no SOLD_DATA/SOLD_COMP_POLICY block; in-zone sold rows staged for review only",
                      close_range=[sold_profile['close_min'], sold_profile['close_max']],
                      sold=[{k: r[k] for k in ('mls', 'address', 'close_date', 'close_price', 'lot_sqft', 'product',
                                                'year_built', 'building_sqft', 'builder', 'lat', 'lng')}
                            for r in sold_recs if not r['exclusion']])

    validate_spliced(candidate)
    s1, e1, _ = span(html, 'DATA'); s2, e2, _ = span(candidate, 'DATA')
    if html[s1:e1].encode() != candidate[s2:e2].encode():
        raise SystemExit('FATAL: DATA bytes changed')
    if _skeleton(html, sold_names) != _skeleton(candidate, sold_names):
        raise SystemExit('FATAL: bytes outside RECONCILE/SOLD_* changed')
    rec_block = json.loads(re.search(r'const RECONCILE=(\{.*?\});', candidate, re.S).group(1))
    if any(i in rec_block['off'] for i in diff['pending']):
        raise SystemExit('FATAL: a pending id landed in RECONCILE.off')

    csv_path = Path(ROOT, CSV_NAME)
    old_csv = csv_record_bytes(csv_path.read_text()) if csv_path.exists() else {}
    csv_text = cmd_csv(html_path, folded=folded, write=False)
    new_csv = csv_record_bytes(csv_text)
    if CSV_NAME == 'heights_off_market.csv':
        for rid, (row, raw) in old_csv.items():
            if row['disposition'] == 'unconfirmed' and (rid not in new_csv or new_csv[rid][1] != raw):
                raise SystemExit('FATAL: unconfirmed CSV row changed: ' + rid)
    if set(pend) & set(new_csv):
        raise SystemExit('FATAL: pending record present in off-market CSV')
    csv_drift = sorted(i for i, (row, _) in new_csv.items()
                       if row['disposition'] != folded[3].get(i, ('unconfirmed',))[0])

    entries = [e for e in index['files'] if e['file'] != filename]
    entries.append(dict(file=filename, date=run_date, counts=chg['counts']))
    entries.sort(key=lambda e: (e['date'], e['file']))
    as_json = lambda value: json.dumps(value, ensure_ascii=False, indent=1) + '\n'
    outputs = {event_path: as_json(chg), index_path: as_json(dict(files=entries, updated=entries[-1]['date'])),
               Path(html_path): candidate, csv_path: csv_text}
    if staged:
        outputs[Path(STAGING_DIR, f'proposed_{run_date}.json')] = as_json(staged)
    if review:
        outputs[Path(STAGING_DIR, f'har_review_{run_date}.json')] = as_json(review)

    snap_report = None
    if heights:
        if not args.runtime:
            raise SystemExit('FATAL: heights needs --runtime (browser runtime capture) for the market-status snapshot')
        runtime_file = json.loads(Path(args.runtime).read_text())
        runtime = runtime_file.get('index', runtime_file)
        if not runtime.get('raw') or runtime_file.get('errors'):
            raise SystemExit('FATAL: runtime capture is empty or recorded page errors')
        records = {r['mls']: r for r in old_snapshot['records']}
        address_changes = []
        for r in inzone:
            o = records.get(r['mls'])
            if o and o['address_key'] != r['address_key']:
                address_changes.append(dict(mls=r['mls'], address=r['address'], previous_address=o['address'],
                                            method='prior_mls', member=links.get(r['mls']), pin=None,
                                            issue='MLS_ADDRESS_CHANGED', candidates=[]))
            records[r['mls']] = r
        snap_links = {m: k for m, k in _prior_observations([], old_snapshot)[0].items()}
        snap = snapshot([records[k] for k in sorted(records)], comp['evidence'] if comp else [],
                        list(data.values()), runtime, run_date, links=snap_links, retain=old_snapshot['properties'],
                        chronology=(f'{label} active/pending snapshots establish current availability; superseded '
                                    'MLS statuses retained as history. Non-sold event dates not supplied.'),
                        price_basis='Current Price where supplied; Original List Price retained separately')
        snap['conflicts'].extend(address_changes)
        snap['refresh_scope'] = (f'{label} active, pending, sold and terminated exports. Missing records retain '
                                 'prior observations and are not automatically retired.')
        fixture = snap['properties']['act_715-merrill']
        assert fixture['status'] == 'active' and any(r['mls'] == '50361472' for r in fixture['history'])
        outputs[Path(ROOT, 'heights_market_status.data.json')] = jsontxt(snap)
        old_active = json.loads(Path(ROOT, 'heights_active.data.json').read_text())
        listings = [dict(mls=r['mls'], address=r['address'], address_key=r['address_key'],
                         original_list_price=r['original_list_price'], current_list_price=r['current_list_price'],
                         dom=r['dom'], lot_sqft=r['lot_sqft'], product=r['product'], builder=r['builder'],
                         list_agent=r['raw'].get('List Agent Full Name', ''), year_built=r['year_built'],
                         lat=r['lat'], lng=r['lng'], status=r['status'], as_of=run_date,
                         source_file=r['source_file'], source_row=r['source_row'], source_sha256=r['source_sha256'])
                    for r in inzone if r['status'] == 'active']
        outputs[Path(ROOT, 'heights_active.data.json')] = jsontxt(dict(as_of=run_date, scope=old_active['scope'],
                                                                        listings=listings))
        snap_report = dict(records=len(snap['records']), properties=len(snap['properties']),
                           tracked=len(snap['tracked']), complete=len(snap['complete']),
                           conflicts=len(snap['conflicts']), address_changes=address_changes,
                           tracked_status=dict(Counter(r['status'] for r in snap['tracked'])))

    audit = []
    for r in incoming:
        member, method = linkinfo.get((r['source_sha256'], r['source_row']), (None, None))
        if r['exclusion']:
            decision = r['exclusion']
        elif member:
            event, mls = diff['decisions'].get(member, ('NO_EVENT', None))
            decision = event if mls == r['mls'] else 'HISTORY'
        else:
            decision = 'STAGED_NEW' if r['status'] in ('active', 'pending') else 'EVIDENCE_ONLY'
        audit.append(dict(FILE=r['source_file'], SHA256=r['source_sha256'], ROW=r['source_row'], MLS=r['mls'],
                          ADDRESS=r['address'], HAR_STATUS=r['har_status'], MEMBER=member or '',
                          METHOD=method or '', DECISION=decision))
    out_dir = Path(args.out) if args.out else Path(ROOT, 'pulls', f'har_{args.market}_{run_date}')
    scratch = {out_dir / 'dropped.csv': csvtxt(ledger, HAR_LEDGER), out_dir / 'audit.csv': csvtxt(audit, HAR_AUDIT)}
    if comp:
        scratch[out_dir / 'sold_comp_dropped.csv'] = csvtxt(comp['ledger'], HAR_LEDGER)
        scratch[out_dir / 'retired_sold_comps.csv'] = csvtxt(comp['retired'], sold_comp_refresh.RETIREMENT_FIELDS)
    changed = [str(p.relative_to(ROOT)) for p, text in outputs.items()
               if not p.exists() or p.read_bytes() != text.encode()]
    if not args.apply:
        for p, text in outputs.items():
            scratch[out_dir / 'candidate' / p.relative_to(ROOT)] = text
    by_reason = {}
    for e in ledger:
        by_reason.setdefault(e['REASON'], []).append(f"{e['MLS']} {e['ADDRESS']} [{e['FILE']}]")
    report = dict(
        market=args.market, date=run_date, applied=bool(args.apply),
        files={role: dict(file=str(paths[role]), rows=f['rows'], statuses=f['statuses'],
                          close_min=f['close_min'], close_max=f['close_max'],
                          in_zone=sum(1 for r in inzone if role_of[r['source_sha256']] == role))
               for role, f in zip(HAR_ROLES, profile['files'])},
        exclusions=by_reason,
        counts=dict(chg['counts'], pending=len(diff['pending']), dispositionUpdates=len(diff['dispositionUpdates']),
                    unresolved=len(diff['unresolved']), staged=len(staged), evidence_only_pins=len(diff['evidence']),
                    unlinked_rows=len(unlinked)),
        dropped=[f"{e['id']} -> {e['disposition']} ({e['har_status'] or 'absent'} {e['mls']})" for e in diff['dropped']],
        relisted=[f"{e['id']} ({e['mls']})" for e in diff['relisted']],
        dispositionUpdates=diff['dispositionUpdates'], unresolved=diff['unresolved'],
        staged=[f"{s['id']} {s['har_status']} {s['mls']} mergeCandidate={s['mergeCandidate']}" for s in staged],
        identity_reviews=reviews, ambiguous_prior_links=ambiguous_links,
        reconcile=dict(off=len(off), relist=len(rel), pending=len(pend)),
        csv_disposition_drift=csv_drift, sold=sold_report, sold_review=bool(review), snapshot=snap_report,
        changed_files=changed, scratch_dir=str(out_dir))
    scratch[out_dir / 'report.json'] = json.dumps(report, indent=2) + '\n'
    if args.apply:
        for p, text in outputs.items():
            if str(p.relative_to(ROOT)) in changed:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(text.encode())
    for p, text in scratch.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.encode())
    print(json.dumps(report, indent=2))
    return report


# ---------- identity follow-ups to a har run: link-staged / archive-duplicates ----------

def _as_json(value):
    return json.dumps(value, ensure_ascii=False, indent=1) + '\n'


def _data_elements(text):
    """(id, start, end) of every DATA element, read in place."""
    from deed_ingest import span
    s, _, _ = span(text, 'DATA')
    dec, out, i = json.JSONDecoder(), [], s + 1
    while True:
        while text[i] in ' \t\r\n,':
            i += 1
        if text[i] == ']':
            return out
        value, j = dec.raw_decode(text, i)
        out.append((value['id'], i, j))
        i = j


def _remove_data_record(text, rid):
    """Cut one DATA element with its leading separator; every other byte stays."""
    els = _data_elements(text)
    hits = [k for k, (i, _, _) in enumerate(els) if i == rid]
    if len(hits) != 1:
        raise SystemExit(f'FATAL: {rid} appears {len(hits)} times in DATA')
    k = hits[0]
    if k:
        a, b = els[k - 1][2], els[k][2]
    elif len(els) > 1:
        a, b = els[0][1], els[1][1]
    else:
        a, b = els[0][1], els[0][2]
    return text[:a] + text[b:]


def _changelog_edit(args, html_path, label, edit):
    """Fold a human-approved identity edit into the same-date changelog, splice
    RECONCILE from the full fold, regenerate the off-market CSV and re-validate.
    `edit(html, data, state, chg, earlier)` mutates chg and returns
    (html, removed_data_ids, report_lines). Dry run unless --apply."""
    from deed_ingest import span
    run_date = date.fromisoformat(args.date).isoformat()
    if args.apply and not args.skip_pull:
        try:
            subprocess.run(['git', '-C', ROOT, 'pull', '--ff-only', '-q'], check=True, stdout=sys.stderr)
        except subprocess.CalledProcessError:
            raise SystemExit('FATAL: git pull --ff-only failed — resolve divergence first')
    html = Path(html_path).read_text()
    if html.count(MARK_BEGIN) != 1 or html.count(MARK_END) != 1:
        raise SystemExit('FATAL: RECONCILE markers missing or ambiguous')
    index_path = Path(CHANGES_DIR, 'index.json')
    index = json.loads(index_path.read_text()) if index_path.exists() else dict(files=[], updated=None)
    if any(e['date'] > run_date for e in index['files']):
        raise SystemExit('FATAL: a later changelog exists; refusing historical edit')
    filename = f'changes_{run_date}.json'
    event_path = Path(CHANGES_DIR, filename)
    if event_path.exists() != any(e['file'] == filename for e in index['files']):
        raise SystemExit(f'FATAL: {filename} and changes index disagree — rebuild the index first')
    earlier = [json.loads(Path(CHANGES_DIR, e['file']).read_text())
               for e in index['files'] if e['file'] != filename]
    if event_path.exists():
        raw = event_path.read_text()
        if _as_json(json.loads(raw)) != raw:
            raise SystemExit(f'FATAL: {filename} does not round-trip; refusing to reserialize it')
        chg = json.loads(raw)
        baseline = fold_events(earlier + [json.loads(raw)])
    else:
        chg = dict(date=run_date, kind=label, sources=[label],
                   counts=dict(matched=0, dropped=0, new=0, relisted=0, excluded=0),
                   matchedIds=[], dropped=[], relisted=[], new=[], excluded=[], dispositionUpdates={})
        baseline = fold_events(earlier)
    current = json.loads(re.search(r'const RECONCILE=(\{.*?\});', html, re.S).group(1))
    if current != dict(off=baseline[0], relist=baseline[1], pending=baseline[2]):
        raise SystemExit('FATAL: RECONCILE block differs from the changelog fold — run generate first')
    data, state = har_state(html, baseline)
    edited, removed, lines = edit(html, data, state, chg, earlier)

    folded = fold_events(earlier + [chg])
    off, rel, pend = folded[:3]
    for a, b in (('off', 'relist'), ('off', 'pending'), ('relist', 'pending')):
        overlap = set(dict(off=off, relist=rel, pending=pend)[a]) & set(dict(off=off, relist=rel, pending=pend)[b])
        if overlap:
            raise SystemExit(f'FATAL: {a}/{b} overlap after fold: {sorted(overlap)}')
    if any(folded[3].get(i, ('',))[0] == 'under contract' for i in off):
        raise SystemExit('FATAL: an under-contract id folded into off')
    block = (MARK_BEGIN + '\nconst RECONCILE=' +
             json.dumps(dict(off=off, relist=rel, pending=pend), ensure_ascii=False, separators=(',', ':')) +
             ';\n' + MARK_END)
    a, b = edited.index(MARK_BEGIN), edited.index(MARK_END) + len(MARK_END)
    candidate = edited[:a] + block + edited[b:]
    validate_spliced(candidate)
    if _skeleton(html, ['DATA']) != _skeleton(candidate, ['DATA']):
        raise SystemExit('FATAL: bytes outside DATA/RECONCILE changed')
    kept = [(i, html[x:y]) for i, x, y in _data_elements(html) if i not in removed]
    if kept != [(i, candidate[x:y]) for i, x, y in _data_elements(candidate)]:
        raise SystemExit('FATAL: a DATA record other than the archived ones changed')
    s1, e1, _ = span(html, 'DATA'); s2, e2, _ = span(candidate, 'DATA')
    if not removed and html[s1:e1] != candidate[s2:e2]:
        raise SystemExit('FATAL: DATA bytes changed')
    rec_block = json.loads(re.search(r'const RECONCILE=(\{.*?\});', candidate, re.S).group(1))
    if set(rec_block['pending']) & set(rec_block['off']):
        raise SystemExit('FATAL: a pending id landed in RECONCILE.off')

    csv_path = Path(ROOT, CSV_NAME)
    old_csv = csv_record_bytes(csv_path.read_text()) if csv_path.exists() else {}
    csv_text = cmd_csv(html_path, folded=folded, write=False)
    new_csv = csv_record_bytes(csv_text)
    if CSV_NAME == 'heights_off_market.csv':
        for rid, (row, raw) in old_csv.items():
            if row['disposition'] == 'unconfirmed' and (rid not in new_csv or new_csv[rid][1] != raw):
                raise SystemExit('FATAL: unconfirmed CSV row changed: ' + rid)
    if set(pend) & set(new_csv):
        raise SystemExit('FATAL: pending record present in off-market CSV')

    entries = [e for e in index['files'] if e['file'] != filename]
    entries.append(dict(file=filename, date=run_date, counts=chg['counts']))
    entries.sort(key=lambda e: (e['date'], e['file']))
    outputs = {event_path: _as_json(chg), index_path: _as_json(dict(files=entries, updated=entries[-1]['date'])),
               Path(html_path): candidate, csv_path: csv_text}
    changed = [str(p.relative_to(ROOT)) for p, text in outputs.items()
               if not p.exists() or p.read_bytes() != text.encode()]
    out_dir = Path(ROOT, 'pulls', f'{label}_{args.market}_{run_date}')
    if args.apply:
        for p, text in outputs.items():
            if str(p.relative_to(ROOT)) in changed:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(text.encode())
    else:
        for p, text in outputs.items():
            dest = out_dir / 'candidate' / p.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(text.encode())
    report = dict(market=args.market, date=run_date, applied=bool(args.apply), actions=lines,
                  removed_data_ids=sorted(removed),
                  reconcile=dict(off=len(off), relist=len(rel), pending=len(pend)),
                  csv_rows=len(new_csv), changed_files=changed,
                  scratch_dir=None if args.apply else str(out_dir))
    print(json.dumps(report, indent=2))
    return report


def cmd_link_staged(args, html_path):
    """Record approved staged mergeCandidate rows as listing events on their
    existing never-listed pin (active -> relisted, pending -> dropped 'under
    contract', so it folds into RECONCILE.pending). Nothing is appended."""
    from market_address import address_key
    from market_linkage import distance
    staged = {}
    for s in json.loads(Path(args.file).read_text()):
        if s['id'] in staged:
            raise SystemExit(f"FATAL: staged id {s['id']} repeats in {args.file}")
        staged[s['id']] = s
    trusted = set(getattr(args, 'trust_address', None) or [])
    if trusted - set(args.approve):
        raise SystemExit(f'FATAL: --trust-address ids not approved: {sorted(trusted - set(args.approve))}')

    def edit(html, data, state, chg, earlier):
        single, ambiguous, _, _ = _prior_observations(earlier + [chg], None)
        lines, used = [], {}
        for sid in args.approve:
            s = staged.get(sid)
            if s is None:
                raise SystemExit(f'REFUSED: {sid} not in {args.file}')
            pin = s.get('mergeCandidate')
            if not pin:
                raise SystemExit(f'REFUSED: {sid} has no mergeCandidate — it is new; use apply_staged.py')
            d = data.get(pin)
            if d is None:
                raise SystemExit(f'REFUSED: {sid} mergeCandidate {pin} is not in DATA')
            if state.get(pin):
                raise SystemExit(f'REFUSED: {pin} already carries listing state {state[pin][0]!r}; har owns it')
            if type_free_key(s['a']) != type_free_key(d['a']):
                raise SystemExit(f"REFUSED: {sid} ({s['a']}) is not the address of {pin} ({d['a']})")
            # HAR coordinates can sit a block off; an exact address tolerates that
            exact = address_key(s['a']) == address_key(d['a'])
            if sid in trusted and not exact:
                raise SystemExit(f'REFUSED: --trust-address {sid} needs an exact address match with {pin}')
            limit = EXACT_LINK_METERS if exact else LOOSE_LINK_METERS
            if sid not in trusted and distance(s['data'], d) > limit:
                raise SystemExit(f'REFUSED: {sid} sits {distance(s["data"], d):.0f} m from {pin}')
            if pin in used:
                raise SystemExit(f'REFUSED: {pin} is already linked to {used[pin]} in this run')
            mls = s['mls']
            if mls in ambiguous or single.get(mls, pin) != pin:
                raise SystemExit(f'REFUSED: MLS {mls} already continues {ambiguous.get(mls) or single[mls]}')
            used[pin] = sid
            prod = s['data'].get('prod')
            ty = (('split' if prod == 'Split Lot' else 'single') if prod else
                  'split' if d.get('ty') == 'active_split' or d.get('prod') == 'Split Lot' else 'single')
            status = 'pending' if 'pending' in s['seed']['tags'] else 'active'
            if status == 'pending':
                chg.setdefault('dropped', []).append(dict(id=pin, a=d['a'], ty=ty, disposition='under contract',
                                                          har_status=s['har_status'], mls=mls, close_date=None))
                chg['counts']['dropped'] += 1
            else:
                chg.setdefault('relisted', []).append(dict(id=pin, a=d['a'], ty=ty, mls=mls))
                chg['counts']['relisted'] += 1
            chg.setdefault('identity_resolutions', []).append(dict(
                member=pin, address=s['a'], mls=mls, status=status, har_status=s['har_status'],
                method='staged_merge_candidate', staged_id=sid))
            news = [n for n in chg.get('new', []) if n.get('mls') == mls and n.get('mergeCandidate') == pin]
            if len(news) > 1:
                raise SystemExit(f'FATAL: MLS {mls} has {len(news)} new entries in the changelog')
            for n in news:
                n.update(staged=False, id=pin, applied=True, linked=True)
            lines.append(f"{sid} -> {pin} {'pending' if status == 'pending' else 'relist ' + ty} "
                         f"(MLS {mls} {s['har_status']}; {d['a']})")
        return html, set(), lines

    return _changelog_edit(args, html_path, 'link_staged', edit)


def cmd_archive_duplicates(args, html_path):
    """Retire DATA records that duplicate another pin's property identity (same
    address once street types drop, within LOOSE_LINK_METERS). The full record
    is kept in the changelog's archived_duplicates; every other DATA byte, the
    seed and LIFE stay as they are. CANONICAL may be <market>:<id> for a
    property that one market's zone guard owns."""
    from market_linkage import distance

    def edit(html, data, state, chg, earlier):
        archived = {e['record']['id'] for c in earlier + [chg]
                    for k in ('archived_duplicates', 'archived_out_of_zone') for e in c.get(k, [])}
        text, removed, lines = html, set(), []
        for dup, canonical in args.archive:
            if dup in archived or dup in removed:
                raise SystemExit(f'REFUSED: {dup} is already archived')
            d = data.get(dup)
            if d is None:
                raise SystemExit(f'REFUSED: {dup} is not in DATA')
            market, _, cid = canonical.rpartition(':')
            if market in ('', args.market):
                market, canonical, cdata, cstate = '', cid, data, state
            else:
                if market not in MARKETS:
                    raise SystemExit(f'REFUSED: unknown market in canonical {canonical}')
                other = load_html(os.path.join(ROOT, MARKETS[market]['html']))
                orec = json.loads(re.search(r'const RECONCILE=(\{.*?\});', other, re.S).group(1))
                cdata, cstate = har_state(other, (orec['off'], orec['relist'], orec['pending'], {}, {}))
            c = cdata.get(cid)
            if c is None:
                raise SystemExit(f'REFUSED: canonical {canonical} is not in DATA')
            if canonical == dup or cid in removed:
                raise SystemExit(f'REFUSED: {dup} cannot be archived onto {canonical}')
            if type_free_key(c['a']) != type_free_key(d['a']):
                raise SystemExit(f"REFUSED: {dup} ({d['a']}) and {canonical} ({c['a']}) are different addresses")
            if not all(r.get(k) for r in (c, d) for k in ('lat', 'lng')):
                raise SystemExit(f'REFUSED: {dup} or {canonical} has no coordinates')
            if distance(c, d) > LOOSE_LINK_METERS:
                raise SystemExit(f'REFUSED: {dup} sits {distance(c, d):.0f} m from {canonical}')
            if state.get(dup) and not cstate.get(cid):
                raise SystemExit(f'REFUSED: {dup} carries listing state {state[dup][0]!r} that '
                                 f'{canonical} does not hold; move the state first')
            text = _remove_data_record(text, dup)
            removed.add(dup)
            chg.setdefault('archived_duplicates', []).append(dict(record=d, canonical=canonical, reason=args.reason))
            lines.append(f"{dup} ({d['a']}) -> {canonical} ({c['a']}, {distance(c, d):.0f} m)")
        return text, removed, lines

    return _changelog_edit(args, html_path, 'archive', edit)


def cmd_archive_out_of_zone(args, html_path):
    """Retire DATA records whose coordinates fail the market's own zone guard
    (the boundary the page's render-side guard draws from). Only pins without
    listing state qualify; the full record is kept in the changelog's
    archived_out_of_zone with the guard's reason."""
    from combined_market_ingest import zone_guard

    def edit(html, data, state, chg, earlier):
        archived = {e['record']['id'] for c in earlier + [chg]
                    for k in ('archived_duplicates', 'archived_out_of_zone') for e in c.get(k, [])}
        guard = zone_guard(html, args.market)
        text, removed, lines = html, set(), []
        for rid in args.ids:
            if rid in archived or rid in removed:
                raise SystemExit(f'REFUSED: {rid} is already archived')
            d = data.get(rid)
            if d is None:
                raise SystemExit(f'REFUSED: {rid} is not in DATA')
            if not all(isinstance(d.get(k), (int, float)) for k in ('lat', 'lng')):
                raise SystemExit(f'REFUSED: {rid} has no coordinates')
            why = guard(d['a'], d['lng'], d['lat'])
            if why is None:
                raise SystemExit(f"REFUSED: {rid} ({d['a']}) is inside the {args.market} zone")
            if state.get(rid):
                raise SystemExit(f'REFUSED: {rid} carries listing state {state[rid][0]!r}; '
                                 f'resolve the listing before archiving')
            text = _remove_data_record(text, rid)
            removed.add(rid)
            chg.setdefault('archived_out_of_zone', []).append(dict(record=d, zone=why, reason=args.reason))
            lines.append(f"{rid} ({d['a']}) {why} at {d['lat']:.5f},{d['lng']:.5f}")
        return text, removed, lines

    return _changelog_edit(args, html_path, 'archive_ooz', edit)


def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--market', default='heights', choices=sorted(MARKETS),
                        help='which market to service (default: heights)')
    common.add_argument('--html', default=None,
                        help="override the market's html file (default: per --market)")
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    dispositions=sub.add_parser('dispositions',parents=[common])
    dispositions.add_argument('--date',required=True)
    dispositions.add_argument('--input',nargs='+',required=True)
    dispositions.add_argument('--apply',action='store_true')
    h = sub.add_parser('har', parents=[common],
                       help='four-file HAR status refresh (active, pending, sold, terminated); dry run by default')
    h.add_argument('--date', required=True)
    for role in HAR_ROLES:
        h.add_argument('--' + role, required=True, help=f'HAR {role} export (CSV, header row)')
    h.add_argument('--runtime', help='browser runtime capture (required for heights)')
    h.add_argument('--out', help='ledger / dry-run directory (default pulls/har_<market>_<date>)')
    h.add_argument('--apply', action='store_true')
    hs = sub.add_parser('har-split',
                        help='cut zip-wide HAR exports into per-market har inputs (writes pulls/ only)')
    hs.add_argument('--date', required=True)
    for role in HAR_ROLES:
        hs.add_argument('--' + role, required=True, help=f'zip-wide HAR {role} export (CSV, header row)')
    hs.add_argument('--out', help='slice directory (default pulls/har_split_<date>)')
    hs.set_defaults(market='heights', html=None)
    d = sub.add_parser('diff', parents=[common], help='diff HAR exports against DATA actives')
    d.add_argument('--date', required=True)
    d.add_argument('single_csv')
    d.add_argument('split_csv')
    d.add_argument('--write', action='store_true', help='write the changelog (default: dry run)')
    g = sub.add_parser('generate', parents=[common],
                       help="splice RECONCILE block into the market's html from the changelog")
    g.add_argument('--skip-pull', action='store_true', help='skip git pull --ff-only (tests only)')
    sub.add_parser('csv', parents=[common],
                   help="regenerate the market's off_market csv from changelog + DATA")
    sub.add_parser('life-sync', parents=[common],
                   help='sync LIFE s/note from changelog dispositions')
    p = sub.add_parser('pull-edits', parents=[common],
                       help='fetch off-market table corrections from the '
                       'shared edits store; --apply folds dispositions into changes/')
    p.add_argument('--apply', action='store_true',
                   help='fold proposed disposition updates into changes/ (default: dry run)')
    ls = sub.add_parser('link-staged', parents=[common],
                        help='record approved staged mergeCandidate rows as relist/pending on their pin')
    ls.add_argument('--date', required=True, help='changelog date the listing events belong to')
    ls.add_argument('--file', required=True, help='staging proposed_<date>.json')
    ls.add_argument('--approve', nargs='+', required=True, help='staged ids to link')
    ls.add_argument('--trust-address', nargs='+', default=[],
                    help='approved ids whose HAR coordinates are reviewed as wrong: exact address, no distance guard')
    ls.add_argument('--apply', action='store_true')
    ls.add_argument('--skip-pull', action='store_true', help='skip git pull --ff-only (tests only)')
    ar = sub.add_parser('archive-duplicates', parents=[common],
                        help='retire DATA records that duplicate another pin (kept in the changelog)')
    ar.add_argument('--date', required=True, help='changelog date to record the archive in')
    ar.add_argument('--archive', nargs=2, action='append', required=True, metavar=('DUPLICATE', 'CANONICAL'),
                    help='DATA id to retire and the id ([market:]id) that keeps the property')
    ar.add_argument('--reason', required=True)
    ar.add_argument('--apply', action='store_true')
    ar.add_argument('--skip-pull', action='store_true', help='skip git pull --ff-only (tests only)')
    az = sub.add_parser('archive-out-of-zone', parents=[common],
                        help="retire DATA records outside the market's zone guard (kept in the changelog)")
    az.add_argument('--date', required=True, help='changelog date to record the archive in')
    az.add_argument('--ids', nargs='+', required=True, help='DATA ids to retire')
    az.add_argument('--reason', required=True)
    az.add_argument('--apply', action='store_true')
    az.add_argument('--skip-pull', action='store_true', help='skip git pull --ff-only (tests only)')
    args = ap.parse_args()
    set_market(args.market)
    html = args.html or DEFAULT_HTML
    if args.cmd=='dispositions':
        cmd_dispositions(args,html)
        return
    if args.cmd == 'har':
        cmd_har(args, html)
        return
    if args.cmd == 'har-split':
        cmd_har_split(args)
        return

    if args.cmd == 'generate':
        cmd_generate(html, skip_pull=args.skip_pull)
        return
    if args.cmd == 'csv':
        cmd_csv(html)
        return
    if args.cmd == 'life-sync':
        cmd_life_sync(html)
        return
    if args.cmd == 'pull-edits':
        cmd_pull_edits(html, apply_=args.apply)
        return
    if args.cmd == 'link-staged':
        cmd_link_staged(args, html)
        return
    if args.cmd == 'archive-duplicates':
        cmd_archive_duplicates(args, html)
        return
    if args.cmd == 'archive-out-of-zone':
        cmd_archive_out_of_zone(args, html)
        return

    if args.cmd == 'diff':
        chg = run_diff(args.date, [('Single Lot', args.single_csv),
                                   ('Split Lot', args.split_csv)], html)
        print(json.dumps(chg['counts']))
        for sec in ('dropped', 'relisted', 'new', 'excluded'):
            for e in chg[sec]:
                print(f"  {sec[:4].upper()}  {e.get('id', '-'):34s} {e.get('a', '')}")
        if args.write:
            fn = write_changelog(chg)
            print(f'wrote changes/{fn} + index.json')
            if chg['new']:
                stage_new(chg, [('Single Lot', args.single_csv),
                                ('Split Lot', args.split_csv)], html)
        else:
            print('(dry run — nothing written)')


if __name__ == '__main__':
    main()
