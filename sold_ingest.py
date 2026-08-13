#!/usr/bin/env python3
"""
sold_ingest.py — HAR Matrix sold-comps CSVs -> single-line JS emit (sold_emit.txt).
=====================================================================
Market-parameterized like permit_pull.py; Heights first. Reads the two
pre-filtered HAR exports (sold, trailing 365d, $500k+, 1500sqft+, Heights
polygon), merges + dedupes on MLS Number, tags cohort (nc = 2025 file,
resale = 2024 file), applies the market zone guard (OUT_OF_ZONE regex
lifted from the market HTML + lng east cutoff), computes per-row derived
fields and precomputed aggregates, and emits:

    const SOLD_DATA=[...];      (one line, compact short-key row objects)
    const SOLD_METRICS={...};   (one line, precomputed aggregates)

NO geocoding — HAR Longitude/Latitude used directly.
This script NEVER touches index.html. Splicing is a separate manual step.

USAGE
  python3 sold_ingest.py                 # heights, writes sold_emit.txt
  python3 sold_ingest.py --market heights
=====================================================================
"""
import argparse
import csv
import json
import re
import sys
from datetime import date, datetime
from statistics import median

MARKETS = {
    'heights': {
        'html': 'index.html',
        'out': 'sold_emit.txt',
        # (path, cohort) — nc file listed first so an MLS in both keeps nc
        'csvs': [('HAR_Export_2025_heights.csv', 'nc'),
                 ('HAR_Export_2024-heights.csv', 'resale')],
        'lng_east_max': -95.370,   # east of I-45 North Fwy corridor = out of zone
    },
}

BANDS = ['<800k', '800k-1.3M', '1.3M-2M', '2M+']
WINS = ['0-30', '30-60', '60-90', '90-180', '180-365']
SPLIT_LOT_MAX = 3500


def load_zone_regex(html_path):
    """Single source of truth: lift the OUT_OF_ZONE regex from the market HTML."""
    with open(html_path, encoding='utf-8') as f:
        html = f.read()
    m = re.search(r'const OUT_OF_ZONE=/(.+?)/i;', html)
    if not m:
        sys.exit('FATAL: OUT_OF_ZONE regex not found in ' + html_path)
    return re.compile(m.group(1), re.I)


def money(s):
    s = str(s or '').replace('$', '').replace(',', '').strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def intval(s):
    v = money(s)
    return int(round(v)) if v is not None else None


def parse_close(s):
    s = str(s or '').strip()
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y'):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def band_of(cp):
    if cp < 800_000: return '<800k'
    if cp < 1_300_000: return '800k-1.3M'
    if cp < 2_000_000: return '1.3M-2M'
    return '2M+'


def win_of(days):
    if days <= 30: return '0-30'
    if days <= 60: return '30-60'
    if days <= 90: return '60-90'
    if days <= 180: return '90-180'
    return '180-365'


def stats(rows):
    """Aggregate stat block for a list of processed rows."""
    if not rows:
        return {'n': 0}
    psf = [r['psf'] for r in rows if r.get('psf')]
    dom = [r['dom'] for r in rows if r.get('dom') is not None and not r.get('p')]
    svl = [r['svl'] for r in rows if r.get('svl') is not None]
    cp = [r['cp'] for r in rows]
    out = {'n': len(rows)}
    if psf: out['med_psf'] = round(median(psf), 1)
    if dom: out['med_dom'] = round(median(dom), 1)
    if svl: out['avg_svl_pct'] = round(sum(svl) / len(svl) * 100, 2)
    if cp: out['med_price'] = int(median(cp))
    pre = sum(1 for r in rows if r.get('p'))
    if pre: out['presold_n'] = pre
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--market', default='heights', choices=sorted(MARKETS))
    args = ap.parse_args()
    cfg = MARKETS[args.market]
    today = date.today()

    zone_re = load_zone_regex(cfg['html'])
    lng_max = cfg['lng_east_max']

    rows, seen, dupes = [], set(), 0
    excl_zone, excl_lng, bad = [], [], []
    for path, cohort in cfg['csvs']:
        with open(path, encoding='utf-8-sig', newline='') as f:
            for rec in csv.DictReader(f):
                mls = (rec.get('MLS Number') or '').strip()
                if not mls:
                    continue
                if mls in seen:
                    dupes += 1
                    continue
                seen.add(mls)
                addr = (rec.get('Address') or '').strip()
                lat = money(rec.get('Latitude'))
                lng = money(rec.get('Longitude'))
                cp = intval(rec.get('Close Price'))
                lp = intval(rec.get('Original List Price'))
                sq = intval(rec.get('Building SqFt'))
                cd = parse_close(rec.get('Close Date'))
                if not (addr and lat and lng and cp and sq and cd):
                    bad.append((mls, addr))
                    continue
                # zone guard, pipeline level (same as permit_pull.py)
                if zone_re.search(addr):
                    excl_zone.append(addr)
                    continue
                if lng > lng_max:
                    excl_lng.append(addr)
                    continue
                lot = intval(rec.get('Lot Size'))
                dom = intval(rec.get('DOM'))
                days = (today - cd).days
                if days < 0:
                    days = 0
                prod = ('Split Lot' if lot < SPLIT_LOT_MAX else 'Single Lot') if lot else 'Unclassified'
                row = {
                    'id': 's' + mls,
                    'a': addr,
                    'lat': round(lat, 7), 'lng': round(lng, 7),
                    'cp': cp, 'lp': lp, 'sq': sq,
                    'psf': round(cp / sq, 1),
                    'cd': cd.isoformat(), 'mo': cd.strftime('%Y-%m'),
                    'dom': dom, 'yb': intval(rec.get('Year Built')),
                    'coh': cohort, 'band': band_of(cp), 'win': win_of(days),
                    'prod': prod,
                }
                if lot: row['lot'] = lot
                if lp: row['svl'] = round((cp - lp) / lp, 4)
                if dom == 0: row['p'] = 1          # presold new construction — signal, not junk
                if not lot: row['nr'] = 1           # needs_review: no lot size, product unknown
                for k, col in (('bl', 'Builder Name'), ('sch', 'School Elementary'),
                               ('la', 'List Agent Full Name'), ('ba', 'Selling Agent Full Name')):
                    v = (rec.get(col) or '').strip()
                    if v: row[k] = v
                rows.append(row)

    rows.sort(key=lambda r: r['cd'], reverse=True)

    # ---- metrics ----
    def group(key):
        g = {}
        for r in rows:
            g.setdefault(r[key], []).append(r)
        return g

    metrics = {
        'as_of': today.isoformat(),
        'basis': 'HAR closed sales, trailing 365d, $500k+, 1500sqft+, in-zone; '
                 'nc = year-built 2025+ new construction, resale = 2024-and-earlier',
        'overall': {**stats(rows), 'absorption_per_month': round(len(rows) / 12, 1)},
        'by_window': {w: stats(g) for w, g in sorted(group('win').items(), key=lambda kv: WINS.index(kv[0]))},
        'by_band': {b: {**stats(g), 'absorption_per_month': round(len(g) / 12, 1)}
                    for b, g in sorted(group('band').items(), key=lambda kv: BANDS.index(kv[0]))},
        'by_product': {p: {**stats(g), 'absorption_per_month': round(len(g) / 12, 1)}
                       for p, g in sorted(group('prod').items())},
        'by_cohort': {c: {**stats(g), 'absorption_per_month': round(len(g) / 12, 1)}
                      for c, g in sorted(group('coh').items())},
        'by_month': {m: stats(g) for m, g in sorted(group('mo').items())},
    }
    # window x product marginal (answers e.g. "split lots sold last 30 days, median $/sqft")
    wp = {}
    for r in rows:
        wp.setdefault(r['win'] + '|' + r['prod'], []).append(r)
    metrics['by_window_product'] = {k: stats(g) for k, g in sorted(wp.items())}
    # full cells: window|band|product|cohort (non-empty only)
    cells = {}
    for r in rows:
        cells.setdefault('|'.join([r['win'], r['band'], r['prod'], r['coh']]), []).append(r)
    metrics['cells'] = {k: stats(g) for k, g in sorted(cells.items())}

    js = ('const SOLD_DATA=' + json.dumps(rows, separators=(',', ':'), ensure_ascii=True) + ';\n'
          + 'const SOLD_METRICS=' + json.dumps(metrics, separators=(',', ':'), ensure_ascii=True)
          + '; // generated by sold_ingest.py ' + today.isoformat() + '\n')
    # sanity: both lines must round-trip as JSON
    for line in js.strip().split('\n'):
        json.loads(re.sub(r'^const \w+=', '', line).rstrip(';').split('; //')[0].rstrip(';'))
    with open(cfg['out'], 'w', encoding='utf-8') as f:
        f.write(js)

    coh_n = {c: len(g) for c, g in group('coh').items()}
    prod_n = {p: len(g) for p, g in group('prod').items()}
    win_n = {w: len(g) for w, g in group('win').items()}
    print(f"rows emitted:     {len(rows)}")
    print(f"dupes dropped:    {dupes}")
    print(f"bad/incomplete:   {len(bad)} {bad[:5]}")
    print(f"zone-regex excl:  {len(excl_zone)} {excl_zone[:5]}")
    print(f"east-lng excl:    {len(excl_lng)} {excl_lng[:5]}")
    print(f"cohorts:          {coh_n}")
    print(f"products:         {prod_n}  (Unclassified = lot-size null, needs_review)")
    print(f"windows:          { {w: win_n.get(w, 0) for w in WINS} }")
    print(f"presold (DOM=0):  {sum(1 for r in rows if r.get('p'))}")
    print(f"emitted -> {cfg['out']} ({len(js)} bytes, {js.count(chr(10))} lines)")


if __name__ == '__main__':
    main()
