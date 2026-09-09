#!/usr/bin/env python3
"""Merge Heights HAR closed sales. Dry run by default; --apply writes sold constants only.

MLS identifies a transaction. Address + close date is the fallback identity;
repeat sales on other dates remain separate transactions. No geocoding or deploy.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import re
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from statistics import median
from sold_classification import classify_lot

ROOT = Path(__file__).resolve().parent
INPUTS = [('Heightssoldsinglelotslast30days.csv', 'Single Lot'),
          ('Heightssoldsplitlotslast30days.csv', 'Split Lot')]
REQUIRED = ['MLS Number', 'Address', 'Latitude', 'Longitude', 'Close Price',
            'Building SqFt', 'Close Date']
OPTIONAL = {'lp': 'Original List Price', 'lot': 'Lot Size', 'dom': 'DOM',
            'yb': 'Year Built', 'har_psf': 'Price Sq Ft Sold'}
TEXT = {'bl': 'Builder Name', 'sch': 'School Elementary',
        'la': 'List Agent Full Name', 'ba': 'Selling Agent Full Name'}
BANDS = ['<800k', '800k-1.3M', '1.3M-2M', '2M+']
WINS = ['0-30', '30-60', '60-90', '90-180', '180-365', '365+']
PRODUCTS = ['Single Lot', 'Split Lot', 'Unclassified', 'Unknown']


def money(value):
    try:
        n = float(str(value or '').replace(',', '').replace('$', '').strip())
        return n if math.isfinite(n) else None
    except ValueError:
        return None


def parse_close(value):
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y'):
        try:
            return datetime.strptime(str(value or '').strip(), fmt).date()
        except ValueError:
            pass
    return None


def normalize_address(value):
    s = value.split(',')[0].lower().strip()
    s = re.sub(r'\b(?:unit|apt|suite)\s*#?\s*', ' ', s)
    s = re.sub(r'(?<=\d)([a-f])\b', r' \1', s)
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    aliases = dict(street='st', avenue='ave', road='rd', lane='ln', drive='dr',
                   boulevard='blvd', court='ct', place='pl', north='n', south='s',
                   east='e', west='w', terrace='ter')
    words = [aliases.get(w, w) for w in s.split()]
    if len(words) > 2 and words[0].isdigit() and words[1] in list('abcdef'):
        words.append(words.pop(1))
    return ' '.join(words)


def constant(html, name):
    matches = list(re.finditer(r'\bconst ' + name + r'=', html))
    if len(matches) != 1:
        raise ValueError(f'{name}: expected exactly one declaration')
    start = matches[0].end()
    value, length = json.JSONDecoder().raw_decode(html[start:])
    if html[start + length] != ';':
        raise ValueError(f'{name}: missing terminator')
    return value, start, start + length


def stats(rows):
    out = {'n': len(rows)}
    for key, target in [('psf', 'med_psf'), ('cp', 'med_price'), ('dom', 'med_dom')]:
        values = [r[key] for r in rows if r.get(key) is not None and not (key == 'dom' and r.get('p'))]
        if values: out[target] = round(median(values), 1)
    values = [r['svl'] for r in rows if r.get('svl') is not None]
    if values: out['avg_svl_pct'] = round(sum(values) / len(values) * 100, 2)
    if any(r.get('p') for r in rows): out['presold_n'] = sum(bool(r.get('p')) for r in rows)
    return out


def metrics_for(rows, today):
    result = {'as_of': today.isoformat(),
              'basis': 'HAR closed-sales archive: original 2025-08-12 to 2026-08-12 $500k+/1500sqft+ exports, plus incremental exports with their source filters; not a complete rolling-year census. nc = year built 2025+; resale = earlier.',
              'overall': stats(rows)}
    trailing = [r for r in rows if 0 <= (today - date.fromisoformat(r['cd'])).days <= 365]
    result['trailing_365'] = {**stats(trailing), 'absorption_per_month': round(len(trailing)/12, 1)}
    result['overall']['absorption_per_month'] = round(len(trailing)/12, 1)
    for name, keys in [('by_window', ['win']), ('by_band', ['band']),
                       ('by_product', ['prod']), ('by_cohort', ['coh']),
                       ('by_month', ['mo']), ('by_window_product', ['win', 'prod']),
                       ('cells', ['win', 'band', 'prod', 'coh'])]:
        groups = defaultdict(list)
        for r in rows: groups['|'.join(str(r[k]) for k in keys)].append(r)
        result[name] = {k: stats(v) for k, v in sorted(groups.items())}
        if name in ('by_band', 'by_product'):
            for key, group in groups.items():
                result[name][key]['absorption_per_month'] = round(sum(r in trailing for r in group)/12, 1)
    return result


def refresh_derived(rows, today):
    for r in rows:
        r['prod'] = classify_lot(r.get('lot'))
        r['ak'] = normalize_address(r['a'])
        r.pop('nr', None)
        if r['prod'] in ('Unclassified', 'Unknown'): r['nr'] = 1
        days = max(0, (today - date.fromisoformat(r['cd'])).days)
        r['win'] = next((w for w, upper in zip(WINS, [30,60,90,180,365,math.inf]) if days <= upper), '365+')
        r['band'] = BANDS[sum(r['cp'] >= b for b in [800000,1300000,2000000])]
        r['mo'] = r['cd'][:7]
    return sorted(rows, key=lambda r: (r['cd'], r['id']), reverse=True)


def in_ring(ring, lng, lat):
    inside = False
    for (x1,y1),(x2,y2) in zip(ring,ring[1:]):
        if (y1 > lat) != (y2 > lat) and lng < (x2-x1)*(lat-y1)/(y2-y1)+x1:
            inside = not inside
    return inside


def run(args):
    html_path = ROOT / 'index.html'
    html = html_path.read_text()
    existing, _, _ = constant(html, 'SOLD_DATA')
    rows = json.loads(json.dumps(existing))
    if not rows: raise ValueError('existing sold input is empty')
    today = date.fromisoformat(args.as_of) if args.as_of else date.today()
    zone_match = re.search(r'const OUT_OF_ZONE=/(.+?)/i;', html)
    if not zone_match: raise ValueError('missing OUT_OF_ZONE')
    zone_re = re.compile(zone_match[1], re.I)
    boundary = json.loads((ROOT / 'heights_boundary.geojson').read_text())
    polygons = []
    for feature in boundary['features']:
        geometry = feature['geometry']
        if geometry['type'] == 'Polygon': polygons.append(geometry['coordinates'])
        elif geometry['type'] == 'MultiPolygon': polygons.extend(geometry['coordinates'])
        else: raise ValueError('unsupported boundary geometry')
    if not polygons or any(not rings or any(len(ring) < 4 or ring[0] != ring[-1] for ring in rings) for rings in polygons): raise ValueError('invalid boundary')
    ids = {r['id']: r for r in rows}
    addresses = defaultdict(list)
    for r in rows: addresses[normalize_address(r['a'])].append(r)
    ledger, summaries, mismatches = [], [], []
    seen_ids, seen_closings = set(), set()
    for path, expected in INPUTS:
        source = ROOT / path
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        with source.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            missing = set(REQUIRED + ['Lot Size', 'Year Built']) - set(reader.fieldnames or [])
            if missing: raise ValueError(f'{path}: missing columns {sorted(missing)}')
            inputs = list(reader)
        if not inputs: raise ValueError(f'{path}: empty input')
        summary = {'file': path, 'read': len(inputs), 'added': 0, 'updated': 0, 'excluded': Counter(), 'crosscheck_matches': 0}
        for line, rec in enumerate(inputs, 2):
            reason = None
            prod = classify_lot(rec.get('Lot Size'))
            if prod != expected: mismatches.append({'file':path, 'line':line, 'address':rec.get('Address'), 'lot':rec.get('Lot Size'), 'derived':prod, 'expected':expected})
            else: summary['crosscheck_matches'] += 1
            mls, addr = (rec.get('MLS Number') or '').strip(), (rec.get('Address') or '').strip()
            cd = parse_close(rec.get('Close Date'))
            lat, lng = money(rec.get('Latitude')), money(rec.get('Longitude'))
            cp, sq = money(rec.get('Close Price')), money(rec.get('Building SqFt'))
            if not mls or not addr or cp is None or cp <= 0 or sq is None or sq <= 0: reason = 'MISSING_REQUIRED_FIELD'
            elif cd is None: reason = 'MALFORMED_DATE'
            elif cd > today: reason = 'FUTURE_DATE'
            elif lat is None or lng is None or not (-90 <= lat <= 90 and -180 <= lng <= 180) or not lat or not lng: reason = 'MISSING_GEOCODE'
            elif zone_re.search(addr) or lng > -95.370 or not any(in_ring(rings[0],lng,lat) and not any(in_ring(hole,lng,lat) for hole in rings[1:]) for rings in polygons): reason = 'OUT_OF_MARKET'
            rid = 's' + mls
            closing = (normalize_address(addr), cd.isoformat() if cd else '')
            if not reason and (rid in seen_ids or closing in seen_closings): reason = 'DUP_INPUT'
            if not reason:
                seen_ids.add(rid); seen_closings.add(closing)
                prior = ids.get(rid)
                if prior is None:
                    matches = [r for r in addresses[closing[0]] if r['cd'] == closing[1]]
                    if len(matches) > 1: reason = 'AMBIGUOUS_ADDRESS_MATCH'
                    elif matches: prior = matches[0]
                if not reason:
                    row = dict(prior or {})
                    row.update(id=prior['id'] if prior else rid, a=addr, lat=round(lat,7), lng=round(lng,7), cp=cp, sq=sq, cd=cd.isoformat(), psf=round(cp/sq,1))
                    for key, col in OPTIONAL.items(): row[key] = money(rec.get(col))
                    for key, col in TEXT.items(): row[key] = (rec.get(col) or '').strip()
                    row['coh'] = 'nc' if row.get('yb') is not None and row['yb'] >= 2025 else 'resale'
                    row.pop('p', None); row.pop('svl', None)
                    if row.get('dom') == 0: row['p'] = 1
                    if row.get('lp'): row['svl'] = round((cp-row['lp'])/row['lp'],4)
                    row = refresh_derived([row], today)[0]
                    if prior:
                        compare = refresh_derived([dict(prior)], today)[0]
                        if row == compare: reason = 'DUP_EXISTING'
                        else: prior.clear(); prior.update(row); summary['updated'] += 1
                    else:
                        rows.append(row); ids[rid] = row; addresses[closing[0]].append(row); summary['added'] += 1
            if reason:
                summary['excluded'][reason] += 1
                ledger.append({'SOURCE':'HAR sold','MARKET':'heights','FILE':path,'SHA256':digest,'ROW':str(line),'MLS':mls,'ADDRESS':addr,'REASON':reason,'RAW_JSON':json.dumps(rec,sort_keys=True)})
        summaries.append(summary)
    rows = refresh_derived(rows, today)
    metrics = metrics_for(rows, today)
    counts = {p: sum(r['prod'] == p for r in rows) for p in PRODUCTS}
    flagged = [{'id':r['id'],'address':r['a'],'lot':r.get('lot'),'product':r['prod']} for r in rows if r['prod'] in ('Unknown','Unclassified')]
    replacements = {'SOLD_DATA':rows,'SOLD_METRICS':metrics}
    candidate = html
    for name, value in replacements.items():
        _, start, end = constant(candidate, name)
        candidate = candidate[:start] + json.dumps(value,separators=(',',':'),ensure_ascii=True) + candidate[end:]
    for name, value in replacements.items(): assert constant(candidate,name)[0] == value
    # Only the two constant payloads can differ; DATA and RECONCILE stay byte-identical.
    skeletons = []
    for source in [html,candidate]:
        for name in replacements:
            _, start,end = constant(source,name);source = source[:start]+'null'+source[end:]
        skeletons.append(source)
    assert skeletons[0] == skeletons[1]
    report = {'mode':'APPLY' if args.apply else 'DRY RUN','as_of':today.isoformat(),'files':summaries,
              'old_total':len(existing),'new_total':len(rows),'products':counts,
              'crosscheck_mismatches':mismatches,'flagged':flagged,
              'html_changed':candidate != html,'ledger_rows':len(ledger)}
    print(json.dumps(report,indent=2))
    if mismatches: raise ValueError('export classification mismatch; refusing apply')
    if args.apply:
        # Dedicated sold ledger cannot overwrite permit/deed ledgers; unique keys make reruns stable.
        ledger_path = ROOT/'pulls'/f'dropped_sold_{today.isoformat()}.csv'
        ledger_path.parent.mkdir(exist_ok=True)
        old = list(csv.DictReader(ledger_path.open(newline=''))) if ledger_path.exists() else []
        keys = {(r['SHA256'],r['ROW'],r['REASON']) for r in old}
        additions = [r for r in ledger if (r['SHA256'],r['ROW'],r['REASON']) not in keys]
        if additions:
            buffer = io.StringIO(newline=''); writer = csv.DictWriter(buffer,fieldnames=list(additions[0]));writer.writeheader();writer.writerows(old+additions)
            ledger_path.write_text(buffer.getvalue())
        if candidate != html: html_path.write_text(candidate)
        emit = ''.join('const '+name+'='+json.dumps(value,separators=(',',':'))+';\n' for name,value in replacements.items())
        out = ROOT/'sold_emit.txt'
        if not out.exists() or out.read_text() != emit: out.write_text(emit)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--market', choices=['heights'], default='heights')
    mode = parser.add_mutually_exclusive_group(); mode.add_argument('--apply',action='store_true');mode.add_argument('--dry-run',action='store_true')
    parser.add_argument('--as-of',help='YYYY-MM-DD (defaults to local date)')
    run(parser.parse_args())


if __name__ == '__main__':
    main()
