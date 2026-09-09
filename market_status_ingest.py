#!/usr/bin/env python3
"""Dated HAR market evidence and read-only construction reconciliation.

Dry run by default. --apply writes a separate snapshot, audit, dropped ledger,
and SOLD_DATA/SOLD_METRICS only. DATA and RECONCILE remain byte-identical.
Runtime capture must come from tests/timeline_browser.py with raw/points added.
"""
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from market_address import address_key
from deed_ingest import span, encode, in_boundary
from sold_classification import classify_lot
from sold_ingest import money, parse_close, refresh_derived, metrics_for, OPTIONAL, TEXT

ROOT = Path(__file__).resolve().parent
AS_OF = '2026-09-09'
INPUTS = [
    ('heightsactivesinglelots909.csv', 'active', 'Single Lot'),
    ('heightsactivesplitlots909.csv', 'active', 'Split Lot'),
    ('heightspendingsinglelots909.csv', 'pending', 'Single Lot'),
    ('heightspendingsplitlots909.csv', 'pending', 'Split Lot'),
    ('heightssoldsinglelotslast180days.csv', 'sold', 'Single Lot'),
    ('heightssoldsplitlotslast180days.csv', 'sold', 'Split Lot'),
    ('Heightsterminatedsinglelots909.csv', 'terminated', 'Single Lot'),
    ('heightsterminatedsplitlots909.csv', 'terminated', 'Split Lot'),
    ('HeightsActiveLast365dayssinglelots.csv', 'active', 'Single Lot'),
    ('HeightsActivelast365dayssplitlots.csv', 'active', 'Split Lot'),
]


def jsontxt(value):
    return json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + '\n'


def csvtxt(rows, fields):
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def load_inputs(html):
    zone = re.compile(re.search(r'const OUT_OF_ZONE=/(.*?)/i;', html)[1], re.I)
    boundary = json.loads((ROOT / 'heights_boundary.geojson').read_text())
    records, ledger, summaries = [], [], []
    seen = set()
    seen_properties = set()
    for filename, status, expected in INPUTS:
        payload = (ROOT / filename).read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        reader = csv.DictReader(io.StringIO(payload.decode('utf-8-sig')))
        required = {'MLS Number', 'Address', 'Lot Size', 'Longitude', 'Latitude',
                    'Original List Price', 'Close Price', 'Close Date', 'DOM',
                    'Builder Name', 'Year Built', 'Building SqFt'} | set(TEXT.values()) | set(OPTIONAL.values())
        if not required.issubset(reader.fieldnames or []):
            raise ValueError('Missing columns: ' + filename)
        rows = list(reader)
        if not rows:
            raise ValueError('Empty input: ' + filename)
        summary = dict(file=filename, sha256=digest, read=len(rows), accepted=0,
                       classification_matches=0, excluded=Counter())
        for line, raw in enumerate(rows, 2):
            lot = money(raw['Lot Size'])
            product = classify_lot(lot)
            if product != expected:
                raise ValueError(f'Lot classification mismatch: {filename}:{line}')
            summary['classification_matches'] += 1
            mls, address = raw['MLS Number'].strip(), raw['Address'].strip()
            lat, lng = money(raw['Latitude']), money(raw['Longitude'])
            close = parse_close(raw['Close Date'])
            key = address_key(address)
            reason = None
            if not mls or not address or lat is None or lng is None or not (-90 <= lat <= 90 and -180 <= lng <= 180):
                raise ValueError(f'Invalid identity/coordinates: {filename}:{line}')
            if money(raw['Original List Price']) is None or money(raw['DOM']) is None:
                raise ValueError(f'Missing numeric evidence: {filename}:{line}')
            if status == 'sold' and (not close or close > date.fromisoformat(AS_OF) or not money(raw['Close Price'])):
                raise ValueError(f'Invalid closing: {filename}:{line}')
            if status != 'sold' and (close or raw['Close Price'].strip()):
                raise ValueError(f'Unexpected closing in {status}: {filename}:{line}')
            if zone.search(address): reason = 'OOZ_REGEX'
            elif lng > -95.370: reason = 'OOZ_EAST'
            elif not in_boundary(boundary, lng, lat): reason = 'OOZ_POLY'
            identity = (mls, status, close.isoformat() if close else '')
            property_identity = (key, status, close.isoformat() if close else '')
            if identity in seen: reason = 'DUP_INPUT'
            seen.add(identity)
            seen_properties.add(property_identity)
            rec = dict(mls=mls, status=status, address=address, address_key=key,
                       original_list_price=money(raw['Original List Price']),
                       current_list_price=None, close_price=money(raw['Close Price']),
                       close_date=close.isoformat() if close else None,
                       dom=money(raw['DOM']), lot_sqft=lot, product=product,
                       builder=raw['Builder Name'], year_built=money(raw['Year Built']),
                       building_sqft=money(raw['Building SqFt']), lat=lat, lng=lng,
                       agents={k: v for k, v in raw.items() if 'Agent' in k or 'Office' in k or 'Team' in k},
                       as_of=AS_OF, source_file=filename, source_row=line,
                       source_sha256=digest, exclusion=reason, raw=raw)
            records.append(rec)
            if reason:
                summary['excluded'][reason] += 1
                ledger.append(dict(FILE=filename, SHA256=digest, ROW=line, MLS=mls,
                                   ADDRESS=address, REASON=reason, RAW_JSON=json.dumps(raw, sort_keys=True)))
            else: summary['accepted'] += 1
        assert summary['read'] == summary['accepted'] + sum(summary['excluded'].values())
        summaries.append(summary)
    return records, ledger, summaries


def merge_sales(existing, records):
    """Union transactions; preserve all existing resale/history records verbatim."""
    rows = json.loads(json.dumps(existing))
    updates, additions, overlaps, conflicts = [], [], [], []
    for rec in records:
        if rec['status'] != 'sold' or rec['exclusion']:
            continue
        rid = 's' + rec['mls']
        matches = [r for r in rows if r['id'] == rid]
        if not matches:
            matches = [r for r in rows if address_key(r['a']) == rec['address_key'] and r['cd'] == rec['close_date']]
        if len(matches) > 1:
            conflicts.append(dict(mls=rec['mls'], reason='AMBIGUOUS_EXISTING_CLOSING'))
            continue
        if matches:
            old = matches[0]
            if old['cd'] != rec['close_date'] or address_key(old['a']) != rec['address_key']:
                conflicts.append(dict(mls=rec['mls'], reason='MLS_IDENTITY_CONFLICT'))
                continue
            overlaps.append(rec['mls'])
            # Refresh source facts, retaining legacy fields and transaction identity.
            row = dict(old)
        else: row = dict(id=rid)
        raw = rec['raw']
        row.update(a=rec['address'], lat=round(rec['lat'], 7), lng=round(rec['lng'], 7),
                   cp=rec['close_price'], sq=rec['building_sqft'], cd=rec['close_date'],
                   psf=round(rec['close_price'] / rec['building_sqft'], 1) if rec['building_sqft'] else None)
        row.update({k: money(raw[v]) for k, v in OPTIONAL.items()})
        row.update({k: raw[v].strip() for k, v in TEXT.items()})
        row['coh'] = 'nc' if rec['year_built'] and rec['year_built'] >= 2025 else 'resale'
        if row.get('lp'): row['svl'] = round((row['cp'] - row['lp']) / row['lp'], 4)
        if row.get('dom') == 0: row['p'] = 1
        else: row.pop('p', None)
        row = refresh_derived([row], date.fromisoformat(AS_OF))[0]
        if matches:
            # Window aging alone must not rewrite historical sales.
            if all(old.get(k) == v for k, v in row.items() if k != 'win'):
                continue
            rows[rows.index(old)] = row
            updates.append(rec['mls'])
        else:
            rows.append(row)
            additions.append(rec['mls'])
    assert {r['id'] for r in existing}.issubset({r['id'] for r in rows})
    assert len({r['id'] for r in rows}) == len(rows)
    return rows, dict(added=additions, updated=updates, existing_matches=overlaps, conflicts=conflicts)



def run(args):
    from market_linkage import run as resolve
    return resolve(args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--runtime', required=True)
    parser.add_argument('--output')
    parser.add_argument('--apply', action='store_true')
    run(parser.parse_args())
