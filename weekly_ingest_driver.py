#!/usr/bin/env python3
"""Weekly auto-ingest driver — per-market (multi-market since 2026-08-27).

Wraps permit_pull.ingest() — does NOT reimplement any filter/geocode logic.
ingest()'s insertable rows already satisfy the confidence rule (S.F. RES /
Building Pmt filter, proj+addr dedupe, OOZ regex + polygon + coord box,
geocode status OK). This driver:
  1. loads market_config, points permit_pull's market-scoped globals at the
     requested market (boundary ring reload included)
  2. runs ingest dry-run, capturing the (rows, flagged) return + stdout
  3. quarantines flagged rows (GEOCODE-*/COORD_RANGE/ID_COLLISION) and OOZ
     rows — EXCEPT OOZ-POLY rows that fall inside another enabled market's
     boundary (zip overlap 77019/77008), which are counted as skip
     'other_market', not quarantined
  4. enforces the anomaly cap (> CAP clean rows -> apply NOTHING, exit 3)
     unless --no-cap (manual backfill runs, reviewed by eye)
  5. otherwise applies the clean rows via ingest(apply=True)
  6. writes pulls/ingest_summary.json + pulls/ingest_report.txt for the
     shell wrapper (git/curl/Discord live there, not here)

Exit codes: 0 = ok (applied or nothing new), 3 = anomaly cap tripped,
1 = error. Dedupe / not-SFRES / old-project skips are counted, not
quarantined — they are definitively-not-new, not uncertain.

usage: weekly_ingest_driver.py [--market NAME] [--no-cap] [--dry-run] <pull.csv> ...
"""
import csv, io, json, os, re, sys
from contextlib import redirect_stdout
from datetime import date

REPO = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO)
import permit_pull as pp
from market_config import MARKETS

CAP = 15
OOZ_RE = re.compile(r'^\s*(OOZ-EAST|OOZ-POLY)\s*\(([^)]*)\):\s*(\S+)\s+(.*)$')


def set_market(name):
    cfg = MARKETS[name]
    pp.PERMITS_JSON_NAME = cfg['permits_json']
    pp.COORD_BOX = tuple(cfg['coord_box'])
    pp.LNG_EAST_MAX = cfg['east_lng']
    if cfg['boundary']:
        pp.BOUNDARY_GEOJSON = os.path.join(REPO, cfg['boundary'])
        pp._BOUNDARY_RING = pp._load_boundary_ring()
        if pp._BOUNDARY_RING is None:
            sys.exit(f"FATAL: boundary {cfg['boundary']} failed to load")
    else:
        pp._BOUNDARY_RING = None      # zip + coord-box guard only (westu)
    return cfg


def other_market_rings(name):
    rings = {}
    for mk, cfg in MARKETS.items():
        if mk == name or not cfg['enabled'] or not cfg['boundary']:
            continue
        g = json.load(open(os.path.join(REPO, cfg['boundary'])))
        rs = []
        for f in g['features']:
            geom = f['geometry']
            if geom['type'] == 'Polygon':
                rs.append(geom['coordinates'][0])
            elif geom['type'] == 'MultiPolygon':
                rs.extend(p[0] for p in geom['coordinates'])
        rings[mk] = rs
    return rings


def in_rings(rings, lng, lat):
    for ring in rings:
        inside = False
        j = len(ring) - 1
        for i in range(len(ring)):
            xi, yi = ring[i][0], ring[i][1]
            xj, yj = ring[j][0], ring[j][1]
            if (yi > lat) != (yj > lat) and lng < (xj - xi) * (lat - yi) / (yj - yi) + xi:
                inside = not inside
            j = i
        if inside:
            return True
    return False


def run_dry(csvs, html):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rows, flagged = pp.ingest(csvs, html, 25, False)
    out = buf.getvalue()
    # skipped counts live only in the printed line; recover them
    m = re.search(r'skipped: (\{.*\})', out)
    skipped = eval(m.group(1), {'__builtins__': {}}) if m else {}
    ooz = [{'proj': mo.group(3), 'addr': mo.group(4).strip(),
            'reason': mo.group(1), 'detail': mo.group(2)}
           for mo in (OOZ_RE.match(l) for l in out.splitlines()) if mo]
    return rows, flagged, skipped, ooz, out


def main():
    args = sys.argv[1:]
    market, no_cap, dry_only = 'heights', False, False
    while args and args[0].startswith('--'):
        a = args.pop(0)
        if a == '--market':
            market = args.pop(0)
        elif a == '--no-cap':
            no_cap = True
        elif a == '--dry-run':
            dry_only = True
        else:
            sys.exit(f'unknown flag {a}')
    csvs = args
    if not csvs:
        sys.exit('usage: weekly_ingest_driver.py [--market NAME] [--no-cap] '
                 '[--dry-run] <pull.csv> ...')
    if market not in MARKETS:
        sys.exit(f'unknown market {market}')
    cfg = set_market(market)
    html = os.path.join(REPO, cfg['html'])
    today = date.today().isoformat()

    rows, flagged, skipped, ooz, dry_out = run_dry(csvs, html)

    # cross-market suppression: OOZ-POLY inside another market's ring is that
    # market's row, not an anomaly here
    others = other_market_rings(market)
    kept_ooz = []
    for q in ooz:
        owner = None
        if q['reason'] == 'OOZ-POLY':
            try:
                lat, lng = (float(v) for v in q['detail'].split(','))
                owner = next((mk for mk, rs in others.items()
                              if in_rings(rs, lng, lat)), None)
            except ValueError:
                pass
        if owner:
            skipped['other_market'] = skipped.get('other_market', 0) + 1
        else:
            kept_ooz.append(q)

    quarantined = kept_ooz + [{'proj': f[0], 'addr': f[1],
                               'reason': f[2], 'detail': str(f[3] or '')}
                              for f in flagged]
    cap_tripped = (not no_cap) and len(rows) > CAP
    applied = []

    if cap_tripped:
        quarantined += [{'proj': r['permits'][0]['proj'], 'addr': r['a'],
                         'reason': 'CAP_EXCEEDED_NOT_APPLIED',
                         'detail': f'{len(rows)} clean > cap {CAP}'}
                        for r in rows]
    elif rows and not dry_only:
        dry_ids = {r['id'] for r in rows}
        buf = io.StringIO()
        with redirect_stdout(buf):
            arows, _ = pp.ingest(csvs, html, 25, True)
        applied = [{'id': r['id'], 'a': r['a'],
                    'proj': r['permits'][0]['proj']} for r in arows]
        if {r['id'] for r in arows} != dry_ids:
            print(buf.getvalue())
            sys.exit(f"FATAL: applied ids differ from dry-run ids: "
                     f"{sorted({r['id'] for r in arows} ^ dry_ids)}")

    qcsv = ''
    if quarantined and not dry_only:
        qcsv = os.path.join(REPO, 'pulls', f'quarantine_{today}.csv')
        new_file = not os.path.exists(qcsv)
        with open(qcsv, 'a', newline='') as f:
            w = csv.writer(f)
            if new_file:
                w.writerow(['MARKET', 'PROJECT_NO', 'ADDRESS', 'REASON', 'DETAIL'])
            for q in quarantined:
                w.writerow([market, q['proj'], q['addr'], q['reason'], q['detail']])

    summary = {'date': today, 'market': market, 'inputs': csvs,
               'skipped': skipped, 'clean': len(rows), 'cap': CAP,
               'cap_tripped': cap_tripped, 'applied': applied,
               'quarantined': quarantined, 'quarantine_csv': qcsv}
    with open(os.path.join(REPO, 'pulls', 'ingest_summary.json'), 'w') as f:
        json.dump(summary, f, indent=1)

    # human-readable report -> Discord body
    L = []
    if cap_tripped:
        L.append(f'🚨 {market} ANOMALY CAP TRIPPED: {len(rows)} clean candidates '
                 f'> {CAP}. NOTHING applied — everything quarantined. '
                 f'Normal weekly volume is 0-5; check upstream.')
    elif applied:
        L.append(f'{market} ingest {today}: {len(applied)} pin(s) added:')
        L += [f'  + {a["a"]} (proj {a["proj"]})' for a in applied]
    elif dry_only and rows:
        L.append(f'{market} DRY-RUN {today}: {len(rows)} clean candidate(s), '
                 f'nothing written.')
    else:
        L.append(f'{market} ingest {today}: nothing new.')
    if quarantined:
        L.append(f'{market} quarantined {len(quarantined)}'
                 + (f' (see {os.path.basename(qcsv)})' if qcsv else '') + ':')
        L += [f'  ? {q["addr"]} — {q["reason"]} {q["detail"]}'.rstrip()
              for q in quarantined[:15]]
        if len(quarantined) > 15:
            L.append(f'  … and {len(quarantined) - 15} more')
    L.append(f'{market} skips (normal): {skipped}')
    with open(os.path.join(REPO, 'pulls', 'ingest_report.txt'), 'w') as f:
        f.write('\n'.join(L) + '\n')

    print(dry_out)
    print('\n'.join(L))
    sys.exit(3 if cap_tripped else 0)


if __name__ == '__main__':
    main()
