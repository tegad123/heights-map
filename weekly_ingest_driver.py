#!/usr/bin/env python3
"""Weekly auto-ingest driver for the Heights map.

Wraps permit_pull.ingest() — does NOT reimplement any filter/geocode logic.
ingest()'s insertable rows already satisfy the confidence rule (S.F. RES /
Building Pmt filter, proj+addr dedupe, OOZ regex + east-lng + polygon,
geocode status OK). This driver:
  1. runs ingest dry-run, capturing the (rows, flagged) return + stdout
  2. quarantines flagged rows (GEOCODE-*/COORD_RANGE/ID_COLLISION) and
     OOZ rows (parsed from stdout) to pulls/quarantine_<date>.csv
  3. enforces the anomaly cap: > CAP clean rows -> apply NOTHING,
     quarantine everything, exit 3
  4. otherwise applies the clean rows via ingest(apply=True)
  5. writes pulls/ingest_summary.json + pulls/ingest_report.txt for the
     shell wrapper (git/curl/Discord live there, not here)

Exit codes: 0 = ok (applied or nothing new), 3 = anomaly cap tripped,
1 = error. Dedupe / not-SFRES / old-project skips are counted, not
quarantined — they are definitively-not-new, not uncertain.
"""
import csv, io, json, os, re, sys
from contextlib import redirect_stdout
from datetime import date

REPO = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REPO)
import permit_pull as pp

CAP = 15
OOZ_RE = re.compile(r'^\s*(OOZ-EAST|OOZ-POLY)\s*\(([^)]*)\):\s*(\S+)\s+(.*)$')


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
    csvs = sys.argv[1:]
    if not csvs:
        sys.exit('usage: weekly_ingest_driver.py <pull.csv> ...')
    html = os.path.join(REPO, 'index.html')
    today = date.today().isoformat()

    rows, flagged, skipped, ooz, dry_out = run_dry(csvs, html)
    quarantined = ooz + [{'proj': f[0], 'addr': f[1],
                          'reason': f[2], 'detail': str(f[3] or '')}
                         for f in flagged]
    cap_tripped = len(rows) > CAP
    applied = []

    if cap_tripped:
        quarantined += [{'proj': r['permits'][0]['proj'], 'addr': r['a'],
                         'reason': 'CAP_EXCEEDED_NOT_APPLIED',
                         'detail': f'{len(rows)} clean > cap {CAP}'}
                        for r in rows]
    elif rows:
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
    if quarantined:
        qcsv = os.path.join(REPO, 'pulls', f'quarantine_{today}.csv')
        new_file = not os.path.exists(qcsv)
        with open(qcsv, 'a', newline='') as f:
            w = csv.writer(f)
            if new_file:
                w.writerow(['PROJECT_NO', 'ADDRESS', 'REASON', 'DETAIL'])
            for q in quarantined:
                w.writerow([q['proj'], q['addr'], q['reason'], q['detail']])

    summary = {'date': today, 'inputs': csvs, 'skipped': skipped,
               'clean': len(rows), 'cap': CAP, 'cap_tripped': cap_tripped,
               'applied': applied, 'quarantined': quarantined,
               'quarantine_csv': qcsv}
    with open(os.path.join(REPO, 'pulls', 'ingest_summary.json'), 'w') as f:
        json.dump(summary, f, indent=1)

    # human-readable report -> Discord body
    L = []
    if cap_tripped:
        L.append(f'🚨 ANOMALY CAP TRIPPED: {len(rows)} clean candidates > '
                 f'{CAP}. NOTHING applied — everything quarantined. '
                 f'Normal weekly volume is 0-5; check upstream.')
    elif applied:
        L.append(f'Heights weekly ingest {today}: {len(applied)} pin(s) added:')
        L += [f'  + {a["a"]} (proj {a["proj"]})' for a in applied]
    else:
        L.append(f'Heights weekly ingest {today}: nothing new this week.')
    if quarantined:
        L.append(f'Quarantined {len(quarantined)} (see {os.path.basename(qcsv)}):')
        L += [f'  ? {q["addr"]} — {q["reason"]} {q["detail"]}'.rstrip()
              for q in quarantined[:15]]
        if len(quarantined) > 15:
            L.append(f'  … and {len(quarantined) - 15} more')
    L.append(f'Skips (normal): {skipped}')
    with open(os.path.join(REPO, 'pulls', 'ingest_report.txt'), 'w') as f:
        f.write('\n'.join(L) + '\n')

    print(dry_out)
    print('\n'.join(L))
    sys.exit(3 if cap_tripped else 0)


if __name__ == '__main__':
    main()
