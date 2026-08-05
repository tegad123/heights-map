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
  - Results open in a popup as a WebFOCUS ACTIVE REPORT: the ENTIRE result
    set ships client-side (77018 Structural = 33,478 records back to 1995)
    with a JS API (ibiApiReportObj.getColumnValues etc.). No server
    pagination, no row cap observed.
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
import re
import sys

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("Playwright not installed — run inside ~/insp-venv (see scrape_inspections.py).")

URL = 'https://cohtora.houstontx.gov/approot/soldpermits/online_permit.htm'
HDR = ['PROJECT_NO', 'PERMIT_DESC', 'OWNER_OCCUPANT', 'Address',
       'PROJECT_DESC', 'CURRENT_VALUATION', 'PERMIT_TYPE']

# Confirmed working signature (probed live 2026-07-31):
#   ibiApiReportObj.getNumOfRecords(0)            -> total record count
#   ibiApiReportObj.getColumnValues(0, '<NAME>')  -> array of chunk-arrays
COL_JS = """(col) => {
  const r = window.ibiApiReportObj;
  if (!r) return {err: 'no ibiApiReportObj'};
  let chunks;
  try { chunks = r.getColumnValues(0, col); }
  catch(e) { return {err: 'getColumnValues(0,' + col + '): ' + String(e).slice(0,120)}; }
  const flat = [];
  for (const c of chunks) {
    if (Array.isArray(c)) flat.push(...c); else flat.push(c);
  }
  return {vals: flat};
}"""


def clean(v):
    s = htmllib.unescape(re.sub(r'<[^>]+>', '', str(v if v is not None else '')))
    return s.replace('\xa0', ' ').strip()


def pull(zip5, ptype, headless):
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

        cols = {}
        for name in HDR:
            res = None
            for variant in (name, name.upper()):
                res = pop.evaluate(COL_JS, variant)
                if not res.get('err'):
                    break
            if res.get('err'):
                sys.exit(f'FATAL: column {name!r} extraction failed: {res["err"]}')
            cols[name] = res['vals']
            # ADDITION 4: hard assert per column — a short pull that looks
            # clean is the failure mode to avoid. No silent truncation.
            if n_api is not None and len(cols[name]) != n_api:
                sys.exit(f'FATAL: column {name!r} extracted {len(cols[name])} values '
                         f'but getNumOfRecords(0) = {n_api} — refusing truncated pull')
        b.close()
    rows = list(zip(*[cols[h] for h in HDR]))
    rows = [[clean(c) for c in row] for row in rows]
    rows = [r for r in rows if r and r[0] != 'PROJECT_NO']
    if n_api is not None and len(rows) != n_api:
        sys.exit(f'FATAL: assembled {len(rows)} rows vs getNumOfRecords(0) = {n_api}')
    return rows, n_api if n_api is not None else declared


def main():
    ap = argparse.ArgumentParser(description='Pull Houston sold permits for a zip -> CSV')
    ap.add_argument('--zip', required=True)
    ap.add_argument('--ptype', default='Structural',
                    help='PTYPE discipline (default Structural = building permits)')
    ap.add_argument('--out', default='')
    ap.add_argument('--show', action='store_true')
    args = ap.parse_args()
    out = args.out or f'permits_{args.zip}.csv'

    rows, declared = pull(args.zip, args.ptype, headless=not args.show)
    with open(out, 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(HDR)
        w.writerows(rows)
    print(f'wrote {len(rows)} rows -> {out} (report declared {declared})')


if __name__ == '__main__':
    main()
