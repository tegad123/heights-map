#!/usr/bin/env python3
"""
permit_pull.py — automated Houston eGov sold-permits pull, scoped by zip.
=====================================================================
Companion to scrape_inspections.py: same Playwright approach, different
city portal. Drives the WebFOCUS 'soldpermits' app that the hand-pulled
per-zip CSVs came from:
    https://cohtora.houstontx.gov/approot/soldpermits/online_permit.htm

RECON FACTS (probed 2026-07-31 on the mini)
  - Form: SELTD radio (ZC = search by Zip Code), SRH = search term,
    BDT/EDT = Date From/To (DEFAULT EMPTY — no date window), edit4/edit5 =
    valuation min/max, PTYPE = discipline select (Structural covers
    building permits). No auth, no captcha; anti-tamper hidden fields are
    irrelevant when driving the real UI.
  - DATE WINDOW (probed 2026-08-10): BDT/EDT (#edit2/#edit3) WORK but accept
    YYYYMMDD ONLY. MM/DD/YYYY (and other formats) return the misleading
    "This selection is under Maintenance" wedge — that is a date-format
    rejection, not actual maintenance. A 30-day window cuts 77008 from
    ~35k records to ~1k and the pull from minutes to seconds. Use --from/--to.
  - Results open in a popup as a WebFOCUS ACTIVE REPORT. OBSOLETE (pre
    2026-08-05): the entire result set used to ship client-side and
    ibiApiReportObj.getColumnValues worked. The portal update switched to
    server-side chunked loading — see EXTRACTION REWRITE below.
  - Output columns match the historical hand-pulled CSVs byte-for-byte:
    PROJECT_NO, PERMIT_DESC, OWNER_OCCUPANT, Address, PROJECT_DESC,
    CURRENT_VALUATION, PERMIT_TYPE.

USAGE (on the mini, same venv as the inspections scraper)
  source ~/insp-venv/bin/activate
  python3 permit_pull.py --zip 77018 --out permits_77018.csv
  python3 permit_pull.py --zip 77092 --ptype Structural --show
=====================================================================
"""
import argparse
import csv
import html as htmllib
import json
import os
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None  # pull needs it; --ingest --from-csv does not

URL = 'https://cohtora.houstontx.gov/approot/soldpermits/online_permit.htm'
HDR = ['PROJECT_NO', 'PERMIT_DESC', 'OWNER_OCCUPANT', 'Address',
       'PROJECT_DESC', 'CURRENT_VALUATION', 'PERMIT_TYPE']

# EXTRACTION REWRITE (2026-08-10): the 08-05 portal update broke
# ibiApiReportObj.getColumnValues — it now returns only the first ~1k-row
# server chunk, duplicated 4x, regardless of paging (setLinesPerPage /
# setCurrentPage don't refresh it). The report now lazy-loads rows from a
# session-scoped WebFOCUS cache via POST IBIF_ex=c1che AR_CFUNC=GETDATA
# with AR_CSTART/AR_CEND row offsets. We fetch that endpoint from inside
# the popup (same session cookies) and parse its payload:
#   ARstrings=[...]  -> deduplicated string pool
#   T_cont[NumOfTable]=[[ [poolIdx,poolIdx,flag] x7, ...meta ], ...] -> rows
# Response self-reports "NUMBER OF RECORDS IN TABLE=" in a trailing comment.
import ast

C1CHE_BODY = ('IBIF_webapp=/ibi_apps&IBIC_server=EDASERVE&IBIWF_msgviewer=OFF'
              '&IBIAPP_app=soldpermits&&IBIF_ex=c1che&AR_COUNTCOL=F07'
              '&AR_COLS=F01%20F02%20F03%20F04%20F05%20F06%20F07%20&AR_SCOL=F07'
              '&AR_CSTART={start}&AR_CFUNC=GETDATA&IBIF_wfdescribe=OFF'
              '&AR_WCOND=&AR_SORDER=&AR_CACHEMAS=REPS_PAID_PERMITS_MV'
              '&AR_CACHEMODE=0&AR_CACHEFMT=BINARY&AR_CACHESTR=c1cheS'
              '&AR_CACHEFEX=c1che&AR_HAVEHIGH=NO&AR_HACHEFEX=c1cheh'
              '&AR_CEND={end}&AR_RAND=12345')

FETCH_JS = """async (body) => {
  const r = await fetch('/ibi_apps/WFServlet.ibfs', {method: 'POST',
    headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body});
  return await r.text();
}"""


def _scan_array(text, start):
    """Return end index (inclusive) of the bracketed array starting at text[start]=='['.
    Skips over single-quoted JS strings."""
    depth = 0; j = start
    while True:
        c = text[j]
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return j
        elif c == "'":
            j += 1
            while not (text[j] == "'" and text[j - 1] != '\\'):
                j += 1
        j += 1


def parse_c1che(text):
    """Parse one c1che GETDATA response -> list of 7-value rows."""
    if 'ARstrings=' not in text:
        snippet = re.sub(r'<[^>]+>', ' ', text[:300])
        sys.exit(f'FATAL: c1che response has no ARstrings — {snippet.strip()[:200]}')
    i = text.index('ARstrings=') + len('ARstrings=')
    pool = ast.literal_eval(text[i:_scan_array(text, i) + 1].replace('\\/', '/'))
    k = text.index('T_cont[NumOfTable]=') + len('T_cont[NumOfTable]=')
    raw_rows = json.loads(text[k:_scan_array(text, k) + 1])
    out = []
    for r in raw_rows:
        out.append([pool[c[0]] if isinstance(c, list) else c for c in r[:7]])
    return out


def clean(v):
    s = htmllib.unescape(re.sub(r'<[^>]+>', '', str(v if v is not None else '')))
    return s.replace('\xa0', ' ').strip()


def pull(zip5, ptype, headless, date_from='', date_to=''):
    with sync_playwright() as p:
        b = p.chromium.launch(headless=headless)
        ctx = b.new_context(ignore_https_errors=True)
        pg = ctx.new_page()
        pg.goto(URL, wait_until='networkidle', timeout=60000)
        pg.wait_for_timeout(1500)
        # ADDITION 2: discipline is ALWAYS set explicitly (page default is
        # Electrical) and asserted after selection — a silent default change
        # must not be able to corrupt a pull.
        # ORDER MATTERS (portal change seen 2026-08-05): checking SELTD_ZC now
        # sets #PTYPE display:none, so select the discipline while it is still
        # visible; the selection persists through the radio change (verified).
        pg.select_option('#PTYPE', label=ptype)
        pg.check('#SELTD_ZC')
        pg.fill('#SRH', str(zip5))
        # Date window: YYYYMMDD ONLY (any other format -> "under Maintenance" wedge)
        for fld, val in (('#edit2', date_from), ('#edit3', date_to)):
            if val:
                assert re.fullmatch(r'\d{8}', val), f'date {val!r} must be YYYYMMDD'
                pg.fill(fld, val)
        selected = pg.eval_on_selector('#PTYPE', 'el => el.selectedOptions[0].text.trim()')
        print(f'PTYPE selected: {selected!r}')
        assert selected == ptype, f'PTYPE mismatch: wanted {ptype!r}, got {selected!r}'
        with ctx.expect_page(timeout=90000) as pop_info:
            pg.click('#form1Submit')
        pop = pop_info.value
        pop.wait_for_load_state('domcontentloaded', timeout=180000)
        try:
            pop.wait_for_load_state('networkidle', timeout=180000)
        except Exception:
            pass
        pop.wait_for_timeout(6000)

        m = re.search(r'([\d,]+) of ([\d,]+) records',
                      pop.evaluate("() => document.body.innerText.slice(0,400)"))
        declared = int(m.group(2).replace(',', '')) if m else None
        n_api = pop.evaluate("() => window.ibiApiReportObj ? window.ibiApiReportObj.getNumOfRecords(0) : null")
        print(f'report declares {declared} records; getNumOfRecords(0) = {n_api}')
        total = n_api if n_api is not None else declared
        if not total:
            body0 = pop.evaluate("() => document.body.innerText.slice(0,300)")
            sys.exit(f'FATAL: no record count — popup says: {body0[:200]!r}')

        # chunked fetch via c1che GETDATA (see EXTRACTION REWRITE note above)
        STEP = 2000
        rows = []
        start = 1
        while len(rows) < total:
            body = C1CHE_BODY.format(start=start, end=start + STEP - 1)
            batch = parse_c1che(pop.evaluate(FETCH_JS, body))
            if not batch:
                sys.exit(f'FATAL: empty c1che batch at AR_CSTART={start} with '
                         f'{len(rows)}/{total} rows collected — refusing truncated pull')
            rows.extend(batch)
            print(f'  c1che rows {start}-{start + len(batch) - 1} fetched')
            start += len(batch)
        b.close()
    rows = [[clean(c) for c in row] for row in rows]
    rows = [r for r in rows if r and r[0] != 'PROJECT_NO']
    # ADDITION 4 (kept): hard assert — a short pull that looks clean is the
    # failure mode to avoid. No silent truncation.
    if len(rows) != total:
        sys.exit(f'FATAL: assembled {len(rows)} rows vs declared {total}')
    return rows, total


# ---------------------------------------------------------------------------
# INGEST STAGE (added 2026-08-10) — makes this script self-sufficient:
# filter -> dedupe (proj + normalized address) -> HCAD geocode (unit-aware)
# -> zone guards (OUT_OF_ZONE regex from index.html + lng > -95.370 east
# boundary, CLAUDE.md) -> validated surgical splice into index.html DATA.
# Dry-run by default; --apply writes. Refuses on any validation failure.
# ---------------------------------------------------------------------------

LNG_EAST_MAX = -95.370   # east of I-45 North Fwy corridor = out of zone (CLAUDE.md, 723ccad)
HCAD_URL = 'https://arcweb.hcad.org/server/rest/services/public/public_query/MapServer/0'
# arcweb.hcad.org serves an incomplete SSL chain; public read-only data
_HCAD_CTX = ssl._create_unverified_context()
UNIT_RE = re.compile(r'\s*#?\s*(?:[A-F]|A&B|1/2)$')


def extract_data(html):
    """Locate the DATA array; return (start, end_exclusive, parsed_rows)."""
    m = re.search(r'\bDATA\s*=\s*\[', html)
    if not m:
        sys.exit('FATAL: DATA array not found in index.html')
    start = m.end() - 1
    depth = 0; i = start; in_str = False; esc = False
    while True:
        c = html[i]
        if in_str:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == '"': in_str = False
        else:
            if c == '"': in_str = True
            elif c == '[': depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0: break
        i += 1
    return start, i + 1, json.loads(html[start:i + 1])


def out_of_zone_re(html):
    """Single source of truth: lift the OUT_OF_ZONE regex from index.html."""
    m = re.search(r'const OUT_OF_ZONE=/(.+?)/i;', html)
    if not m:
        sys.exit('FATAL: OUT_OF_ZONE regex not found in index.html')
    return re.compile(m.group(1), re.I)


def norm_addr(a):
    a = a.upper()
    a = re.sub(r',?\s*HOUSTON.*$', '', a)
    a = re.sub(r'\s+7700\d\s*$', '', a)
    a = re.sub(r'[.,]', '', a)
    a = re.sub(r'\bSTREET\b', 'ST', a)
    a = re.sub(r'\b(AVENUE|AVE\.?)\b', 'AVE', a)
    a = re.sub(r'\b(DRIVE)\b', 'DR', a)
    a = re.sub(r'\b(BOULEVARD|BLVD\.?)\b', 'BLVD', a)
    a = re.sub(r'\b(LANE)\b', 'LN', a)
    a = re.sub(r'\b(ROAD)\b', 'RD', a)
    a = re.sub(r'\b(COURT)\b', 'CT', a)
    a = re.sub(r'\b(PLACE)\b', 'PL', a)
    a = re.sub(r'\b(UNIT|APT|#)\s*', '', a)
    return re.sub(r'\s+', ' ', a).strip()


def title_addr(street):
    out = []
    for w in street.split():
        if re.fullmatch(r'[NSEW]', w) or re.fullmatch(r'[A-F]', w):
            out.append(w)
        elif re.fullmatch(r'\d+(ST|ND|RD|TH)', w):
            out.append(w[:-2] + w[-2:].lower())
        else:
            out.append(w.capitalize())
    return ' '.join(out)


def _hcad_query(where):
    qs = urllib.parse.urlencode({'f': 'json', 'where': where,
                                 'outFields': 'address,legal_lines',
                                 'returnGeometry': 'true', 'outSR': '4326'})
    with urllib.request.urlopen(HCAD_URL + '/query?' + qs, timeout=30, context=_HCAD_CTX) as r:
        return json.load(r).get('features', [])


def _centroid(rings):
    ring = max(rings, key=len)
    a = cx = cy = 0.0
    for i in range(len(ring) - 1):
        x0, y0 = ring[i]; x1, y1 = ring[i + 1]
        cr = x0 * y1 - x1 * y0
        a += cr; cx += (x0 + x1) * cr; cy += (y0 + y1) * cr
    if abs(a) < 1e-12:
        xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
        return sum(ys) / len(ys), sum(xs) / len(xs)
    a *= 0.5
    return cy / (6 * a), cx / (6 * a)


def _norm_ret(s):
    # HCAD stores units as "1103 ERIN ST # B" — collapse '#' before comparing
    return re.sub(r'\s+', ' ', s.strip().upper().replace('#', ' ')).strip()


def hcad_geocode(street_upper):
    """Parcel-centroid geocode. Returns dict with status OK/FAIL/AMBIG/MISMATCH.
    Unit-aware: '2412 TERRY ST B' also tried as HCAD's '2412 TERRY ST # B'."""
    clean = re.sub(r'\s+', ' ', street_upper.replace('(PVT)', ' ')).strip()
    base = UNIT_RE.sub('', clean)
    um = re.search(r'\s([A-F])$', clean)
    unit = um.group(1) if um else None
    esc = lambda s: s.replace("'", "''")
    feats = _hcad_query(f"address = '{esc(clean)}'")
    time.sleep(0.25)
    if not feats and unit:
        feats = _hcad_query(f"address = '{esc(base)} # {unit}'")
        time.sleep(0.25)
    if not feats:
        feats = _hcad_query(f"address LIKE '{esc(base)}%'")
        time.sleep(0.25)
        feats = [f for f in feats
                 if _norm_ret(f['attributes']['address']) == _norm_ret(clean)
                 or UNIT_RE.sub('', _norm_ret(f['attributes']['address'])) == base]
    if not feats:
        return {'status': 'FAIL'}
    num, rest = base.split(' ', 1)
    good = [f for f in feats if _norm_ret(f['attributes']['address']).startswith(num + ' ')
            and rest.split(' ')[0] in _norm_ret(f['attributes']['address'])]
    if not good:
        return {'status': 'MISMATCH', 'matched': feats[0]['attributes']['address']}
    exact = [f for f in good if _norm_ret(f['attributes']['address']) == _norm_ret(clean)]
    pick = exact or good
    if len({_norm_ret(f['attributes']['address']) for f in pick}) > 1:
        return {'status': 'AMBIG',
                'matched': sorted({_norm_ret(f['attributes']['address']) for f in good})[:4]}
    f0 = pick[0]
    lat, lng = _centroid(f0['geometry']['rings'])
    return {'status': 'OK', 'matched': f0['attributes']['address'].strip(),
            'legal': (f0['attributes'].get('legal_lines') or ''),
            'lat': round(lat, 7), 'lng': round(lng, 7)}


def ingest(csv_paths, html_path, min_proj_year, apply_changes):
    html = open(html_path).read()
    start, end, data = extract_data(html)
    ooz = out_of_zone_re(html)
    projs = {p['proj'] for r in data if r.get('permits') for p in r['permits']}
    norms = {norm_addr(r['a']) for r in data if 'a' in r}
    ids = {r.get('id') for r in data}

    cands, skipped = [], {'dup_proj': 0, 'dup_addr': 0, 'not_sfres': 0, 'old_proj': 0, 'ooz_addr': 0}
    seen = set()
    for cp in csv_paths:
        for row in csv.DictReader(open(cp)):
            proj = row['PROJECT_NO'].strip()
            if not proj or proj in seen:
                continue
            seen.add(proj)
            if row['PERMIT_DESC'].strip() != 'Building Pmt' or 'S.F. RES' not in row['PROJECT_DESC'].upper():
                skipped['not_sfres'] += 1; continue
            if int(proj[:2]) < min_proj_year:
                skipped['old_proj'] += 1; continue
            addr_raw = row['Address'].strip()
            zm = re.search(r'(7\d{4})\s*$', addr_raw)
            zipc = zm.group(1) if zm else ''
            street = re.sub(r'\s*7\d{4}\s*$', '', addr_raw).strip().upper()
            if proj in projs:
                skipped['dup_proj'] += 1; continue
            if norm_addr(street) in norms:
                skipped['dup_addr'] += 1; continue
            a_disp = f"{title_addr(re.sub(r'\s+', ' ', street.replace('(PVT)', ' ')).strip())}, Houston, TX {zipc}"
            if ooz.search(a_disp) or ooz.search(street):
                skipped['ooz_addr'] += 1; continue
            cands.append({'proj': proj, 'street': street, 'zip': zipc, 'a': a_disp,
                          'owner': row['OWNER_OCCUPANT'].lstrip('*').strip(),
                          'desc': row['PROJECT_DESC'].strip(),
                          'val': re.sub(r'[^0-9]', '', row['CURRENT_VALUATION']) or '0',
                          'ptype': row['PERMIT_TYPE'].strip()})
    print(f'candidates after filter+dedupe: {len(cands)}  skipped: {skipped}')

    rows, flagged = [], []
    for c in cands:
        g = hcad_geocode(c['street'])
        if g['status'] != 'OK':
            flagged.append((c['proj'], c['street'], g['status'], g.get('matched')))
            print(f"  GEOCODE-{g['status']}: {c['proj']} {c['street']} {g.get('matched') or ''}")
            continue
        if g['lng'] > LNG_EAST_MAX:
            skipped['ooz_addr'] += 1
            print(f"  OOZ-EAST (lng {g['lng']}): {c['proj']} {c['street']}")
            continue
        if not (29.70 < g['lat'] < 29.90 and -95.50 < g['lng'] < -95.30):
            flagged.append((c['proj'], c['street'], 'COORD_RANGE', (g['lat'], g['lng'])))
            continue
        rid = 'pmt_' + re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-',
                    (c['street'] + ' ' + c['zip']).lower())).strip('-')
        if rid in ids:
            flagged.append((c['proj'], c['street'], 'ID_COLLISION', rid)); continue
        ids.add(rid)
        rows.append({"id": rid, "a": c['a'], "llc": c['owner'], "kind": "permit",
                     "lat": g['lat'], "lng": g['lng'],
                     "permits": [{"owner": c['owner'], "desc": c['desc'], "val": c['val'],
                                  "ptype": c['ptype'], "proj": c['proj'],
                                  "permitDesc": "Building Pmt"}]})
    print(f'insertable: {len(rows)}  geocode-flagged: {len(flagged)}')
    for r in rows:
        print('  +', r['id'], r['a'], r['lat'], r['lng'])
    if not apply_changes:
        print('DRY RUN — no write. Re-run with --apply to splice.')
        return rows, flagged
    if not rows:
        print('nothing to insert.')
        return rows, flagged

    styled = ',\n'.join(json.dumps(r, separators=(', ', ': ')) for r in rows)
    # generic anchor: insert immediately before DATA's closing bracket
    close = end - 1
    assert html[close] == ']'
    prefix = html[:close]
    body = prefix.rstrip()
    ws = prefix[len(body):]          # preserve any whitespace before ']'
    assert body.endswith('}'), 'DATA does not end with an object'
    new_html = body + ',\n' + styled + ws + html[close:]
    _, _, arr = extract_data(new_html)
    assert len(arr) == len(data) + len(rows), f'{len(arr)} != {len(data)}+{len(rows)}'
    new_ids = {r['id'] for r in rows}
    assert new_ids <= {r.get('id') for r in arr}
    assert {r.get('id') for r in data} <= {r.get('id') for r in arr}, 'existing row lost'
    open(html_path, 'w').write(new_html)
    assert open(html_path).read() == new_html
    print(f'SPLICED {len(rows)} rows into {html_path}; DATA now {len(arr)} rows. '
          f'Review + commit manually (auto-push deploys on commit).')
    return rows, flagged


def main():
    ap = argparse.ArgumentParser(description='Pull Houston sold permits -> CSV; optional ingest into index.html DATA')
    ap.add_argument('--zip', help='single zip to pull (pull mode)')
    ap.add_argument('--ptype', default='Structural',
                    help='PTYPE discipline (default Structural = building permits)')
    ap.add_argument('--out', default='')
    ap.add_argument('--show', action='store_true')
    ap.add_argument('--from', dest='date_from', default='',
                    help='BDT date window start, YYYYMMDD (server-side filter)')
    ap.add_argument('--to', dest='date_to', default='',
                    help='EDT date window end, YYYYMMDD')
    ap.add_argument('--ingest', action='store_true',
                    help='ingest CSVs into index.html DATA (dry-run unless --apply)')
    ap.add_argument('--from-csv', action='append', default=[],
                    help='CSV(s) to ingest (repeatable); skips the Playwright pull')
    ap.add_argument('--html', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html'))
    ap.add_argument('--min-proj-year', type=int, default=25,
                    help='ignore PROJECT_NO years before this (2-digit, default 25)')
    ap.add_argument('--apply', action='store_true', help='actually splice (default dry-run)')
    args = ap.parse_args()

    if args.ingest:
        if not args.from_csv:
            sys.exit('--ingest needs --from-csv (run pull mode per zip first)')
        ingest(args.from_csv, args.html, args.min_proj_year, args.apply)
        return

    if not args.zip:
        sys.exit('--zip required in pull mode')
    if sync_playwright is None:
        sys.exit('Playwright not installed — run inside ~/insp-venv (see scrape_inspections.py).')
    out = args.out or f'permits_{args.zip}.csv'
    rows, declared = pull(args.zip, args.ptype, headless=not args.show,
                          date_from=args.date_from, date_to=args.date_to)
    with open(out, 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(HDR)
        w.writerows(rows)
    print(f'wrote {len(rows)} rows -> {out} (report declared {declared})')


if __name__ == '__main__':
    main()
