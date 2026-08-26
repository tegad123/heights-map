#!/usr/bin/env python3
"""Diff HCAD parcel geometry across vintages to detect real lot SPLITs and
ASSEMBLies inside the Heights zone.

SIGNAL GENERATION ONLY. This script never writes index.html, the DATA array,
the RECONCILE markers, or any classify_* script. Its sole output is
refresh/parcel_events.json plus a terminal report.

Why it exists: the live Split-vs-Single label is inferred indirectly (permit
chain markers, address unit letters, lot size). classify_v6/v9 read an HCAD
legal like "LTS 6 & 7 BLK 40" as "spans 2 lots -> Split", but in the Heights
the original plat lots are ~25 ft, so two of them assembled is ONE full 50 ft
lot -- the opposite of a split. Comparing parcel polygons between vintages
settles it directly: one polygon becoming two IS a split; two becoming one IS
an assembly.

Method: centroid (representative-point) containment plus an area-sum test.
For each old parcel, find the new parcels whose representative point falls
inside it; if 2+ children sum to the parent within tolerance, that is a SPLIT.
The mirror pass over new parcels yields ASSEMBLY.

Sources (~/hcad-gis):
    Parcels_2024_Oct.zip   shapefile   HCAD_PDATA/Parcels/Parcels.shp
    Parcels_2025_Oct.zip   shapefile   Parcels_2025_Oct/Parcels.shp
    Parcels.zip            File GDB    Parcels/Parcels.gdb  (needs one-time
                                       ogr2ogr conversion -- see --help-gdb)

All vintages are EPSG:2278 (NAD83 StatePlane TX South Central, US survey
feet), so polygon area is already square feet.
"""
import argparse
import json
import os
import pickle
import re
import shutil
import statistics
import struct
import sys
import zipfile
from pathlib import Path

import shapefile  # pyshp
from pyproj import Transformer
from shapely import wkb as shapely_wkb
from shapely.geometry import Polygon, shape as shapely_shape
from shapely.strtree import STRtree

HOME = Path.home()
HCAD_DIR = HOME / 'hcad-gis'
CACHE_DIR = HCAD_DIR / '.parcel_diff_cache'
REPO = Path(__file__).resolve().parent.parent
INDEX_HTML = REPO / 'index.html'
OUT_JSON = Path(__file__).resolve().parent / 'parcel_events.json'

# EPSG:2278 = NAD83 / Texas South Central (ftUS). Areas come out in sq ft.
CRS_PARCEL = 2278
CRS_WGS84 = 4326

# Eastern boundary: lng > -95.370 is out of zone (east of the I-45 North
# Freeway corridor -- Near Northside / Northside Village). CLAUDE.md rule;
# ZONE_RING alone extends past it to -95.356.
EAST_CUT_LNG = -95.370

# Area-sum tolerance for calling a split/assembly.
AREA_TOL = 0.10

# Sanity gate. These two are full-lot single builds that the current
# classifier wrongly labels Split; they must NOT come out of a geometric
# diff as SPLIT. Located by COORDINATE, not by account -- a genuine split
# reissues the HCAD_NUM, so an account lookup would miss exactly the case
# being guarded against.
CONTROLS = [
    ('614 E 26th St', -95.391867, 29.81042),
    ('629 E 26th St', -95.3912309, 29.8107923),
]

VINTAGES = [
    # (name, archive path, shapefile stem inside archive or None to autodetect)
    ('2024_Oct', HCAD_DIR / 'Parcels_2024_Oct.zip', 'HCAD_PDATA/Parcels/Parcels'),
    ('2025_Oct', HCAD_DIR / 'Parcels_2025_Oct.zip', 'Parcels_2025_Oct/Parcels'),
    ('2026_Jul', HCAD_DIR / 'Parcels_2026_Jul', None),
]

GDB_SOURCE = HCAD_DIR / 'Parcels.zip'
GDB_CONVERTED = HCAD_DIR / 'Parcels_2026_Jul'

# Field names differ per vintage (2025 dropped Shape_Area and added mail_*;
# the ogr2ogr conversion truncates names to 10 chars). Resolve by alias and
# fail loudly rather than silently defaulting.
FIELD_ALIASES = {
    'acct': ['HCAD_NUM', 'HCAD_NUM_1', 'LOWPARCELI', 'ACCOUNT', 'acct'],
    'addr': ['LocAddr', 'LOCADDR', 'SITUS_ADDR', 'situs_addr'],
    'zipc': ['zip', 'ZIP', 'LocZip'],
    'stacked': ['Stacked', 'STACKED'],
    'ptype': ['parcel_typ', 'PARCEL_TYP', 'parcel_type'],
}
REQUIRED_FIELDS = ['acct']


# --------------------------------------------------------------------------
# zone

def load_zone_ring():
    """Lift ZONE_RING out of index.html so this stays in sync with the map."""
    src = INDEX_HTML.read_text()
    m = re.search(r'const ZONE_RING\s*=\s*(\[\[.*?\]\])\s*;', src, re.S)
    if not m:
        sys.exit('FATAL: ZONE_RING not found in index.html')
    ring = json.loads(m.group(1))
    if len(ring) < 4:
        sys.exit(f'FATAL: ZONE_RING has only {len(ring)} points')
    return ring


def build_zone():
    ring_wgs = load_zone_ring()
    fwd = Transformer.from_crs(CRS_WGS84, CRS_PARCEL, always_xy=True)
    inv = Transformer.from_crs(CRS_PARCEL, CRS_WGS84, always_xy=True)
    poly = Polygon([fwd.transform(lng, lat) for lng, lat in ring_wgs])
    if not poly.is_valid:
        poly = poly.buffer(0)
    return poly, poly.bounds, inv, len(ring_wgs)


# --------------------------------------------------------------------------
# verify

def shx_count(path_or_zip, member=None):
    """Feature count from .shx length: (size - 100 header) / 8 bytes per record."""
    if member is not None:
        with zipfile.ZipFile(path_or_zip) as z:
            size = z.getinfo(member).file_size
    else:
        size = os.path.getsize(path_or_zip)
    return (size - 100) // 8


def find_shp_stem(directory):
    """Locate the parcels shapefile in a converted-GDB directory."""
    shps = sorted(Path(directory).glob('*.shp'))
    if not shps:
        return None
    for s in shps:  # prefer one that looks like parcels
        if 'parcel' in s.stem.lower():
            return s.with_suffix('')
    return shps[0].with_suffix('')


def verify():
    """Stage 1: archive validity, layer presence, feature count per vintage."""
    print('=' * 74)
    print('STAGE 1  input verification')
    print('=' * 74)
    results = []
    for name, path, stem in VINTAGES:
        if not path.exists():
            print(f'  {name:9}  MISSING          {path}')
            results.append((name, None, 'missing'))
            continue

        if path.is_dir():
            found = find_shp_stem(path)
            if not found:
                print(f'  {name:9}  NO SHAPEFILE     {path}')
                results.append((name, None, 'no shapefile'))
                continue
            n = shx_count(found.with_suffix('.shx'))
            print(f'  {name:9}  {n:>10,} features  dir  {found.name}.shp')
            results.append((name, n, 'ok'))
            continue

        try:
            with zipfile.ZipFile(path) as z:
                bad = z.testzip()
                if bad:
                    print(f'  {name:9}  CORRUPT at {bad}')
                    results.append((name, None, 'corrupt'))
                    continue
                names = z.namelist()
        except zipfile.BadZipFile:
            print(f'  {name:9}  NOT A ZIP        {path}')
            results.append((name, None, 'bad zip'))
            continue

        if stem is None or (stem + '.shp') not in names:
            gdbs = {n.split('.gdb/')[0] + '.gdb' for n in names if '.gdb/' in n}
            if gdbs:
                print(f'  {name:9}  FILE GEODATABASE {sorted(gdbs)[0]}')
                print(f'  {"":9}  -> not readable without GDAL; run --help-gdb')
                results.append((name, None, 'gdb'))
            else:
                print(f'  {name:9}  NO PARCELS LAYER in {path.name}')
                results.append((name, None, 'no layer'))
            continue

        n = shx_count(path, stem + '.shx')
        print(f'  {name:9}  {n:>10,} features  zip  {stem}.shp')
        results.append((name, n, 'ok'))

    counts = [n for _, n, s in results if s == 'ok']
    if len(counts) >= 2:
        med = statistics.median(counts)
        print(f'\n  median feature count: {med:,.0f}')
        drastic = False
        for name, n, s in results:
            if s != 'ok':
                continue
            dev = (n - med) / med
            flag = '  <-- DRASTIC' if abs(dev) > 0.10 else ''
            print(f'    {name:9} {n:>10,}  {dev:+6.2%}{flag}')
            if abs(dev) > 0.10:
                drastic = True
        if drastic:
            sys.exit('\nFATAL: a vintage deviates >10% from the median count. '
                     'Refusing to diff against a possibly truncated file.')
        print('  all vintages within 10% of median - OK')
    print()
    return results


# --------------------------------------------------------------------------
# load + filter

def resolve_fields(field_names):
    """Map vintage-specific DBF field names onto our common schema."""
    lookup = {f.lower(): f for f in field_names}
    out = {}
    for key, aliases in FIELD_ALIASES.items():
        for a in aliases:
            if a.lower() in lookup:
                out[key] = lookup[a.lower()]
                break
    missing = [k for k in REQUIRED_FIELDS if k not in out]
    if missing:
        sys.exit(f'FATAL: required field(s) {missing} not found. '
                 f'DBF has: {sorted(field_names)}')
    return out


def extract_members(zip_path, stem, dest):
    """Pull just the four shapefile parts we need out of the archive."""
    dest.mkdir(parents=True, exist_ok=True)
    got = {}
    with zipfile.ZipFile(zip_path) as z:
        have = set(z.namelist())
        for ext in ('.shp', '.shx', '.dbf', '.prj'):
            member = stem + ext
            if member not in have:
                if ext == '.prj':
                    continue
                sys.exit(f'FATAL: {member} missing from {zip_path.name}')
            target = dest / (Path(stem).name + ext)
            with z.open(member) as src, open(target, 'wb') as fh:
                shutil.copyfileobj(src, fh, length=8 << 20)
            got[ext] = target
    return dest / Path(stem).name


def load_filtered(name, path, stem, zone_poly, zone_bbox, inv, use_cache=True):
    """Return Heights-zone parcels for one vintage, normalized."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache = CACHE_DIR / f'{name}.pkl'
    if use_cache and cache.exists():
        with open(cache, 'rb') as fh:
            recs = pickle.load(fh)
        print(f'  {name}: {len(recs):,} zone parcels (cached)')
        return recs

    tmp = CACHE_DIR / f'tmp_{name}'
    try:
        if path.is_dir():
            base = find_shp_stem(path)
            if base is None:
                sys.exit(f'FATAL: no shapefile in {path}')
        else:
            print(f'  {name}: extracting...', flush=True)
            base = extract_members(path, stem, tmp)

        # ogr2ogr writes ISO-8859-1 DBFs (it warns on UTF-8 -> ISO-8859-1);
        # HCAD's own shapefiles ship a .cpg. Honour the .cpg when present,
        # otherwise fall back to latin1, and never hard-fail on a stray byte.
        cpg = base.with_suffix('.cpg')
        enc = cpg.read_text().strip() if cpg.exists() else 'latin1'
        try:
            reader = shapefile.Reader(str(base), encoding=enc,
                                      encodingErrors='replace')
        except LookupError:
            reader = shapefile.Reader(str(base), encoding='latin1',
                                      encodingErrors='replace')
        fields = [f[0] for f in reader.fields[1:]]
        fmap = resolve_fields(fields)

        recs = []
        scanned = 0
        for sr in reader.iterShapeRecords(bbox=zone_bbox):
            scanned += 1
            geom = shapely_shape(sr.shape.__geo_interface__)
            if not geom.is_valid:
                geom = geom.buffer(0)
            if geom.is_empty:
                continue
            rp = geom.representative_point()
            if not zone_poly.contains(rp):
                continue
            lng, lat = inv.transform(rp.x, rp.y)
            if lng > EAST_CUT_LNG:
                continue
            rec = sr.record
            def get(key, default=''):
                f = fmap.get(key)
                if f is None:
                    return default
                v = rec[f]
                return v if v is not None else default
            recs.append({
                'acct': str(get('acct')).strip(),
                'addr': str(get('addr')).strip(),
                'zip': str(get('zipc')).strip(),
                'stacked': str(get('stacked')).strip().upper(),
                'ptype': str(get('ptype')).strip(),
                'area_sf': geom.area,      # computed, never StatedArea/Shape_Area
                'lng': lng, 'lat': lat,
                'wkb': geom.wkb,
            })
        reader.close()
        print(f'  {name}: {len(recs):,} zone parcels '
              f'({scanned:,} passed bbox prefilter)')
        with open(cache, 'wb') as fh:
            pickle.dump(recs, fh, protocol=4)
        return recs
    finally:
        if tmp.exists():
            shutil.rmtree(tmp, ignore_errors=True)


def hydrate(recs):
    """Attach shapely geometry + representative point to cached records."""
    out = []
    for r in recs:
        g = shapely_wkb.loads(r['wkb'])
        r = dict(r)
        r['geom'] = g
        r['rp'] = g.representative_point()
        out.append(r)
    return out


# --------------------------------------------------------------------------
# diff

def is_stacked(r):
    return r['stacked'] not in ('', '0', 'N', 'NO', 'FALSE', 'NONE')


def pct(a, b):
    return (a - b) / b if b else float('inf')


def diff_pair(old_recs, new_recs, label):
    """Centroid-containment diff. Returns (events, summary)."""
    old_live = [r for r in old_recs if not is_stacked(r)]
    new_live = [r for r in new_recs if not is_stacked(r)]
    n_stack = (len(old_recs) - len(old_live)) + (len(new_recs) - len(new_live))

    events = []
    summary = {'unchanged': 0, 'SPLIT': 0, 'ASSEMBLY': 0, 'RESHAPE': 0,
               'VANISHED': 0, 'PARTIAL': 0, 'stacked_skipped': n_stack}
    # index of old parcel -> event, for the sanity gate
    old_event = {}

    tree_new = STRtree([r['rp'] for r in new_live])
    tree_old = STRtree([r['rp'] for r in old_live])

    # ---- split pass: old parcel -> new parcels whose point falls inside it
    for i, o in enumerate(old_live):
        idx = tree_new.query(o['geom'], predicate='contains')
        kids = [new_live[j] for j in idx]
        if not kids:
            summary['VANISHED'] += 1
            old_event[i] = 'VANISHED'
            events.append(make_event('VANISHED', label, [o], []))
            continue
        tot = sum(k['area_sf'] for k in kids)
        d = pct(tot, o['area_sf'])
        if len(kids) == 1:
            if abs(d) <= AREA_TOL:
                summary['unchanged'] += 1
                old_event[i] = 'unchanged'
            else:
                summary['RESHAPE'] += 1
                old_event[i] = 'RESHAPE'
                events.append(make_event('RESHAPE', label, [o], kids))
        else:
            if abs(d) <= AREA_TOL:
                summary['SPLIT'] += 1
                old_event[i] = 'SPLIT'
                events.append(make_event('SPLIT', label, [o], kids))
            else:
                summary['PARTIAL'] += 1
                old_event[i] = 'PARTIAL'
                events.append(make_event('PARTIAL', label, [o], kids))

    # ---- assembly pass: new parcel containing 2+ old parcel points
    for n in new_live:
        idx = tree_old.query(n['geom'], predicate='contains')
        if len(idx) < 2:
            continue
        parents = [old_live[j] for j in idx]
        tot = sum(p['area_sf'] for p in parents)
        if abs(pct(tot, n['area_sf'])) <= AREA_TOL:
            summary['ASSEMBLY'] += 1
            events.append(make_event('ASSEMBLY', label, parents, [n]))

    return events, summary, old_live, old_event


def make_event(kind, vintage, parents, children):
    psum = sum(p['area_sf'] for p in parents)
    csum = sum(c['area_sf'] for c in children)
    pacc = [p['acct'] for p in parents]
    cacc = [c['acct'] for c in children]
    base, comp = (psum, csum) if kind != 'ASSEMBLY' else (csum, psum)
    return {
        'event': kind,
        'vintage': vintage,
        'parent_accts': pacc,
        'child_accts': cacc,
        'addresses': {
            'parent': [p['addr'] for p in parents],
            'child': [c['addr'] for c in children],
        },
        'areas': {
            'parent_sf': [round(p['area_sf'], 1) for p in parents],
            'child_sf': [round(c['area_sf'], 1) for c in children],
            'sum_parent_sf': round(psum, 1),
            'sum_child_sf': round(csum, 1),
            'delta_pct': round(pct(comp, base) * 100, 2) if base else None,
        },
        # recorded for review, never used to decide the event
        'acct_continuity': bool(set(pacc) & set(cacc)),
        'lng': round(parents[0]['lng'], 6) if parents else None,
        'lat': round(parents[0]['lat'], 6) if parents else None,
    }


# --------------------------------------------------------------------------
# sanity gate

def check_controls(pair_label, old_live, old_event):
    """Locate each control by coordinate and report the event it landed in."""
    fwd = Transformer.from_crs(CRS_WGS84, CRS_PARCEL, always_xy=True)
    rows, failed = [], []
    for name, lng, lat in CONTROLS:
        x, y = fwd.transform(lng, lat)
        from shapely.geometry import Point
        pt = Point(x, y)
        hit = None
        for i, o in enumerate(old_live):
            if o['geom'].contains(pt):
                hit = i
                break
        if hit is None:
            rows.append((name, 'NOT FOUND', '', ''))
            continue
        ev = old_event.get(hit, 'unchanged')
        o = old_live[hit]
        rows.append((name, ev, o['acct'], f"{o['area_sf']:,.0f} sf"))
        if ev == 'SPLIT':
            failed.append((name, o, pair_label))
    return rows, failed


# --------------------------------------------------------------------------

HELP_GDB = f"""
The 2026 vintage ships as a File Geodatabase, which needs GDAL. One-time:

    brew install gdal
    ogrinfo -so /vsizip/{GDB_SOURCE}/Parcels/Parcels.gdb
    ogr2ogr -f "ESRI Shapefile" {GDB_CONVERTED} \\
            /vsizip/{GDB_SOURCE}/Parcels/Parcels.gdb <LAYER>

Check the layer name from ogrinfo before converting -- do not assume
it is called "Parcels".

DO NOT add "-nlt POLYGON". The source layer is 3D Multi Polygon, and
forcing it to POLYGON silently keeps only ONE PART of every multipart
parcel: 0200870000001 came through as 39,062 sf instead of 86,958, and
0210050000019 as 245,958 instead of 478,249. That halves ~35 Heights
parcels and fabricates a wave of bogus 50% "half-split" events, all of
them landing in whichever pair uses the converted vintage. The plain
conversion above reproduces the source areas exactly. Shapefiles store
multipart polygons natively, so no -nlt is needed; the Z coordinate is
dropped on write anyway (harmless warning).
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--verify-only', action='store_true',
                    help='stop after the input verification stage')
    ap.add_argument('--pairs', default='all',
                    help='comma list e.g. 2024_Oct-2025_Oct, or "all"')
    ap.add_argument('--no-cache', action='store_true',
                    help='ignore the filtered-subset cache and re-read archives')
    ap.add_argument('--out', default=str(OUT_JSON))
    ap.add_argument('--help-gdb', action='store_true',
                    help='print the one-time geodatabase conversion recipe')
    args = ap.parse_args()

    if args.help_gdb:
        print(HELP_GDB)
        return 0

    results = verify()
    if args.verify_only:
        return 0

    ok = {name for name, n, s in results if s == 'ok'}
    if len(ok) < 2:
        print(HELP_GDB)
        sys.exit('FATAL: need at least two readable vintages to diff.')

    zone_poly, zone_bbox, inv, nring = build_zone()
    print('=' * 74)
    print('STAGE 2  load + filter to Heights zone')
    print('=' * 74)
    print(f'  ZONE_RING: {nring} points from index.html, '
          f'plus eastern cut lng > {EAST_CUT_LNG}')

    loaded = {}
    for name, path, stem in VINTAGES:
        if name not in ok:
            continue
        recs = load_filtered(name, path, stem, zone_poly, zone_bbox, inv,
                             use_cache=not args.no_cache)
        loaded[name] = hydrate(recs)
    print()

    order = [n for n, _, _ in VINTAGES if n in loaded]
    all_pairs = [(order[i], order[i + 1]) for i in range(len(order) - 1)]
    if args.pairs != 'all':
        want = set(args.pairs.split(','))
        all_pairs = [p for p in all_pairs if f'{p[0]}-{p[1]}' in want]
    if not all_pairs:
        sys.exit(f'FATAL: no vintage pairs selected (have {order})')

    print('=' * 74)
    print('STAGE 3  diff consecutive vintages')
    print('=' * 74)

    all_events, gate_rows, gate_failures = [], [], []
    for a, b in all_pairs:
        label = f'{a}->{b}'
        events, summary, old_live, old_event = diff_pair(loaded[a], loaded[b], label)
        all_events.extend(events)
        print(f'\n  {label}   {len(loaded[a]):,} -> {len(loaded[b]):,} parcels')
        for k in ('unchanged', 'SPLIT', 'ASSEMBLY', 'RESHAPE', 'PARTIAL',
                  'VANISHED', 'stacked_skipped'):
            print(f'      {k:16} {summary[k]:>6,}')
        rows, failed = check_controls(label, old_live, old_event)
        for nm, ev, acct, area in rows:
            gate_rows.append((label, nm, ev, acct, area))
        gate_failures.extend(failed)

    # ---- sanity gate BEFORE any write
    print()
    print('=' * 74)
    print('STAGE 4  sanity gate (614 + 629 E 26th must be ASSEMBLY or unchanged)')
    print('=' * 74)
    for label, nm, ev, acct, area in gate_rows:
        mark = 'FAIL' if ev == 'SPLIT' else 'ok'
        print(f'  [{mark:4}] {label:20} {nm:16} {ev:10} {acct:15} {area}')
    if gate_failures:
        print('\n' + '!' * 74)
        print('GATE FAILED - a control property came out as SPLIT.')
        for nm, o, label in gate_failures:
            print(f'  {nm} in {label}: acct {o["acct"]}, '
                  f'{o["area_sf"]:,.0f} sf, addr {o["addr"]}')
        print('NOT writing parcel_events.json.')
        print('!' * 74)
        return 2

    # ---- report
    print()
    print('=' * 74)
    print('STAGE 5  Heights event list')
    print('=' * 74)
    rank = {'SPLIT': 0, 'ASSEMBLY': 1, 'PARTIAL': 2, 'RESHAPE': 3, 'VANISHED': 4}
    for e in sorted(all_events, key=lambda e: (rank.get(e['event'], 9),
                                               e['vintage'],
                                               e['addresses']['parent'][:1])):
        if e['event'] in ('VANISHED', 'RESHAPE'):
            continue
        pa = ' + '.join(a or '?' for a in e['addresses']['parent'])
        ca = ' + '.join(a or '?' for a in e['addresses']['child'])
        print(f"  {e['event']:9} {e['vintage']:20} "
              f"{e['areas']['sum_parent_sf']:>9,.0f} -> "
              f"{e['areas']['sum_child_sf']:>9,.0f} sf "
              f"({e['areas']['delta_pct']:+.1f}%)")
        print(f"      parent: {pa}")
        print(f"      child : {ca}")

    counts = {}
    for e in all_events:
        counts[e['event']] = counts.get(e['event'], 0) + 1
    print(f'\n  totals: {counts}')

    out = Path(args.out)
    out.write_text(json.dumps(all_events, indent=1))
    print(f'\n-> {out}  ({len(all_events)} events)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
