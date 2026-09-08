#!/usr/bin/env python3
"""DealMachine deed exports -> existing map records and parcel cross-references.

Run: python3 deed_ingest.py export.csv [--dry-run] [--market heights]
The selected market is the source market; rows route to any configured market.
No network, geocoding, stage inference, contact import, commits, or deployment.
DATA is never serialized: only individual changed objects and insertions are
spliced into the original text. All files are validated before any writes.
"""
import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from market_config import MARKETS
from permit_pull import write_dropped_ledger

ROOT = Path(__file__).resolve().parent
DECODER = json.JSONDecoder()
SUFFIXES = dict(zip(
    'STREET AVENUE LANE DRIVE ROAD COURT PLACE BOULEVARD NORTH SOUTH EAST WEST'.split(),
    'ST AVE LN DR RD CT PL BLVD N S E W'.split()))


def encode(value):
    """JSON safe inside a script element, including untrusted CSV text."""
    return json.dumps(value, ensure_ascii=True, allow_nan=False,
                      separators=(',', ':')).replace('<', '\\u003c')


def normalize(address):
    text = str(address or '').upper().split(',')[0]
    text = re.sub(r'\b(?:HOUSTON|TX|TEXAS|77\d{3})\b.*', '', text)
    text = re.sub(r'\bUNIT\s*#?\s*|#\s*', ' UNIT ', text)
    return ' '.join(SUFFIXES.get(w, w) for w in
                    re.sub(r'[^A-Z0-9/ ]', ' ', text).split())


def parcel(value):
    return re.sub(r'[^A-Z0-9]', '', str(value or '').upper())


def number(value):
    text = str(value or '').replace('$', '').replace(',', '').strip()
    if not text:
        return None
    result = float(text)
    if not math.isfinite(result):
        raise ValueError('non-finite number')
    return result


def span(text, name):
    matches = list(re.finditer(r'\b' + re.escape(name) + r'\s*=\s*([\[{])', text))
    if len(matches) != 1:
        raise ValueError(f'{name}: expected exactly one JSON assignment')
    start = matches[0].start(1)
    value, length = DECODER.raw_decode(text[start:])
    return start, start + length, value


def elements(text, start, end):
    """Read exact element/member spans without changing whitespace or order."""
    is_array = text[start] == '['
    cursor = start + 1
    result = []
    while cursor < end - 1:
        while text[cursor].isspace() or text[cursor] == ',':
            cursor += 1
        if cursor == end - 1:
            break
        key = None
        if not is_array:
            key, length = DECODER.raw_decode(text[cursor:])
            cursor += length
            while text[cursor].isspace():
                cursor += 1
            if text[cursor] != ':':
                raise ValueError('invalid object member')
            cursor += 1
            while text[cursor].isspace():
                cursor += 1
        value, length = DECODER.raw_decode(text[cursor:])
        result.append((key, cursor, cursor + length, value))
        cursor += length
    return result


def patch(text, name, key, value):
    """Replace one value or append one entry; never serialize a container."""
    start, end, container = span(text, name)
    for member, a, b, old in elements(text, start, end):
        identity = old['id'] if isinstance(container, list) else member
        if identity == key:
            if old == value:
                return text
            # Preserve every existing field's spelling/spacing where possible.
            if isinstance(old, dict) and isinstance(value, dict) and old.keys() == value.keys():
                for field, x, y, prior in reversed(elements(text, a, b)):
                    if prior != value[field]:
                        text = text[:x] + encode(value[field]) + text[y:]
                return text
            return text[:a] + encode(value) + text[b:]
    addition = encode(value) if isinstance(container, list) else encode(key) + ':' + encode(value)
    return text[:end - 1] + (',' if container else '') + addition + text[end - 1:]


def in_ring(ring, lng, lat):
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        cross = (lng - x1) * (y2 - y1) - (lat - y1) * (x2 - x1)
        if abs(cross) < 1e-12 and min(x1, x2) <= lng <= max(x1, x2) and min(y1, y2) <= lat <= max(y1, y2):
            return True
        if (y1 > lat) != (y2 > lat) and lng < (x2 - x1) * (lat - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def in_boundary(geojson, lng, lat):
    for feature in geojson['features']:
        geometry = feature['geometry']
        if geometry['type'] not in ('Polygon', 'MultiPolygon'):
            raise ValueError('unsupported boundary geometry')
        polygons = [geometry['coordinates']] if geometry['type'] == 'Polygon' else geometry['coordinates']
        for polygon in polygons:
            if in_ring(polygon[0], lng, lat) and not any(in_ring(hole, lng, lat) for hole in polygon[1:]):
                return True
    return False


def load_markets():
    markets = {}
    for name, cfg in MARKETS.items():
        if not cfg['enabled']:
            continue
        path = ROOT / cfg['html']
        text = path.read_text()
        data = span(text, 'DATA')[2]
        if not data or len({r['id'] for r in data}) != len(data):
            raise ValueError(f'{name}: empty DATA or duplicate IDs')
        for symbol in ('SEED_POINTS', 'LIFE', 'DEED_PULL'):
            span(text, symbol)
        match = re.search(r'const OUT_OF_ZONE=/(.*?)/i;', text)
        if not match:
            raise ValueError(f'{name}: missing zone guard')
        metadata_path = ROOT / (name + '_deed.data.json')
        metadata = json.loads(metadata_path.read_text()) if metadata_path.exists() else {'market': name, 'pulls': []}
        if metadata['market'] != name:
            raise ValueError(f'{name}: metadata market mismatch')
        markets[name] = dict(cfg=cfg, path=path, original=text, text=text, data=data,
                             zone=re.compile(match[1], re.I),
                             boundary=json.loads((ROOT / cfg['boundary']).read_text()) if cfg['boundary'] else None,
                             metadata_path=metadata_path, metadata=metadata,
                             permits=json.loads((ROOT / cfg['permits_json']).read_text()), additions=[])
    return markets


def assign(markets, address, zipcode, lng, lat):
    matches = []
    east = False
    excluded_street = False
    for name, market in markets.items():
        cfg = market['cfg']
        bottom, top, left, right = cfg['coord_box']
        geographic = (in_boundary(market['boundary'], lng, lat) if market['boundary']
                      else zipcode[:5] in cfg['zips'] and bottom <= lat <= top and left <= lng <= right)
        if not geographic:
            continue
        if cfg['east_lng'] is not None and lng > cfg['east_lng']:
            east = True
            continue
        if market['zone'].search(address):
            excluded_street = True
            continue
        matches.append(name)
    if len(matches) > 1:
        return None, 'AMBIGUOUS_MARKET', ','.join(matches)
    if matches:
        return matches[0], None, None
    if east:
        return None, 'OOZ_EAST', f'Heights lng {lng} > -95.370; no other tracked market'
    if excluded_street:
        return None, 'OOZ_REGEX', 'matches destination street exclusions; no other tracked market'
    return None, 'OUT_OF_MARKET', 'outside all tracked market boundaries'


def validate(original, result, expected):
    actual = span(result, 'DATA')[2]
    if actual != expected or len({r['id'] for r in actual}) != len(actual):
        raise ValueError('DATA round-trip or unique-ID validation failed')
    for symbol in ('SEED_POINTS', 'LIFE', 'DEED_PULL'):
        span(result, symbol)
    # Prove everything outside the four explicitly editable JSON values is identical.
    masked = []
    for text in (original, result):
        ranges = sorted((span(text, s)[:2] for s in ('DATA', 'SEED_POINTS', 'LIFE', 'DEED_PULL')), reverse=True)
        for a, b in ranges:
            text = text[:a] + '<UNCHANGED-CONTAINER-LOCATION>' + text[b:]
        masked.append(text)
    if masked[0] != masked[1]:
        raise ValueError('unexpected change outside deed data (including RECONCILE)')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv_path', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--market', default='heights', choices=sorted(MARKETS))
    args = parser.parse_args()
    source = args.csv_path.read_bytes()
    digest = hashlib.sha256(source).hexdigest()
    with args.csv_path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        required = {'property_address_line_1', 'property_address_full', 'property_address_zipcode',
                    'property_lat', 'property_lng', 'sale_date', 'owner_1_name', 'apn_parcel_id',
                    'assd_total_value', 'lot_square_feet', 'property_type'}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError('missing CSV columns: ' + ', '.join(sorted(required - set(reader.fieldnames or []))))
        rows = list(reader)
    if not rows:
        raise ValueError('empty input; refusing to write')
    markets = load_markets()
    by_address, by_parcel = defaultdict(set), defaultdict(set)
    for name, market in markets.items():
        for record in market['data']:
            by_address[normalize(record['a'])].add((name, record['id']))
        ids = {r['id'] for r in market['data']}
        for pull in market['metadata']['pulls']:
            for record in pull['properties']:
                apn = parcel(record.get('apn'))
                if apn and record['id'] in ids:
                    by_parcel[apn].add((name, record['id']))
    dispositions, dropped, overlaps = [], [], []
    counts, per_market = Counter(), defaultdict(Counter)
    seen_parcels, seen_addresses = set(), set()
    today = date.today().isoformat()
    for row_number, row in enumerate(rows, 2):
        address = row['property_address_line_1'].strip()
        normalized, apn = normalize(address), parcel(row['apn_parcel_id'])
        destination, reason, detail = None, None, None
        try:
            sale_date = date.fromisoformat(row['sale_date'].strip()).isoformat()
        except ValueError:
            reason, detail = 'MALFORMED_DATE', 'sale_date must be YYYY-MM-DD'
        try:
            lat, lng = number(row['property_lat']), number(row['property_lng'])
            if lat is None or lng is None:
                raise ValueError('missing coordinates')
            if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                raise ValueError('coordinates outside valid range')
        except ValueError as error:
            reason, detail = reason or 'MISSING_OR_BAD_GEOCODE', detail or str(error)
        if not normalized:
            reason, detail = 'MISSING_ADDRESS', 'empty street address'
        elif row['property_type'].strip().lower() != 'single family':
            reason, detail = 'NOT_SINGLE_FAMILY', row['property_type']
        if not reason:
            destination, reason, detail = assign(markets, address, row['property_address_zipcode'], lng, lat)
        # Report permit overlaps even for excluded source rows.
        permit_hits = []
        for name, market in markets.items():
            for permit in market['permits']:
                if normalized and normalize(permit.get('address')) == normalized:
                    permit_hits.append(f"{name}:#{permit['proj']}")
            for record in market['data']:
                if normalized and normalize(record['a']) == normalized and (record.get('permits') or record.get('kind') == 'permit'):
                    permit_hits.append(f"{name}:pin={record['id']}")
        if permit_hits:
            overlaps.append(address + ': ' + ', '.join(sorted(set(permit_hits))))
        if not reason and ((apn and apn in seen_parcels) or normalized in seen_addresses):
            reason, detail = 'DUP_INPUT', 'parcel/address repeated within this input'
        if not reason:
            seen_addresses.add(normalized)
            if apn:
                seen_parcels.add(apn)
            matches = by_parcel.get(apn, set()) or by_address.get(normalized, set())
            if len(matches) > 1:
                reason, detail = 'AMBIGUOUS_MATCH', 'multiple existing pins: ' + repr(sorted(matches))
            elif matches and next(iter(matches))[0] != destination:
                reason, detail = 'MARKET_CONFLICT', 'existing pin in another market: ' + repr(sorted(matches))
        if not reason:
            market = markets[destination]
            records = {r['id']: r for r in market['data']}
            identifier = next(iter(matches))[1] if matches else (row.get('property_id') or 'deed_' + (apn or normalized.replace(' ', '-'))).strip()
            existing = records.get(identifier)
            if existing and not matches and normalize(existing['a']) != normalized:
                reason, detail = 'ID_COLLISION', identifier
            elif existing and existing.get('sd') and existing.get('kind') != 'active' and existing['sd'] > sale_date:
                reason, detail = 'STALE_TRANSFER', 'older than existing sale_date ' + existing['sd']
            else:
                try:
                    assessed = number(row['assd_total_value'])
                    lot = number(row['lot_square_feet'])
                    year = number(row.get('year_built'))
                except ValueError as error:
                    reason, detail = 'MALFORMED_NUMBER', str(error)
        if reason:
            detail = f'deed sha256={digest}; row={row_number}; parcel={apn}; {detail}'
            dropped.append(('', address, reason, detail))
            counts['excluded'] += 1
            dispositions.append(f'{row_number:02d} EXCLUDE {address} | {reason}: {detail.split("; ")[-1]}')
            continue
        incoming = dict(id=identifier, a=row['property_address_full'].strip() or address,
                        llc=row['owner_1_name'].strip() or None,
                        v=f'${assessed:,.0f}' if assessed is not None else None,
                        sd=sale_date, lot=f'{lot:g}' if lot is not None else None,
                        f=row.get('property_flags', '').strip() or None,
                        u=row.get('dealmachine_url', '').strip() or None,
                        lat=lat, lng=lng, c=None)
        if existing:
            updated = dict(existing)
            # Existing listing fields mean list price/date, not assessment/deed.
            # Preserve them and attach the acquisition in the existing notes.
            if existing.get('kind') != 'active':
                updated.update(sd=sale_date, v=incoming['v'], llc=incoming['llc'])
            action = 'updated' if updated != existing else 'unchanged'
            market['text'] = patch(market['text'], 'DATA', identifier, updated)
            market['data'][market['data'].index(existing)] = updated
        else:
            updated = incoming
            action = 'added'
            market['text'] = patch(market['text'], 'DATA', identifier, updated)
            market['data'].append(updated)
            note = f'Lifecycle: Deed transfer {sale_date} · {incoming["llc"] or "Unknown entity"}'
            market['text'] = patch(market['text'], 'LIFE', identifier, {'s': 'deed', 'note': note})
            market['text'] = patch(market['text'], 'SEED_POINTS', identifier, {'notes': note, 'tags': ['deed']})
        prior_events = [r for pull in market['metadata']['pulls'] for r in pull['properties']]
        event_exists = any(r['id'] == identifier and r.get('sale_date') == sale_date and
                           r.get('v') == incoming['v'] and parcel(r.get('apn')) == apn for r in prior_events)
        if not event_exists:
            metadata = {k: incoming[k] for k in ('id', 'a', 'llc', 'v', 'lot', 'lat', 'lng', 'f', 'u', 'c')}
            metadata.update(sale_date=sale_date, apn=row['apn_parcel_id'].strip() or None,
                            year_built=int(year) if year is not None else None)
            market['additions'].append(metadata)
            market['text'] = patch(market['text'], 'DEED_PULL', identifier, date.fromisoformat(today).strftime('%b %d, %Y'))
            if existing:
                seed = dict(span(market['text'], 'SEED_POINTS')[2].get(identifier, {'notes': '', 'tags': []}))
                note = f'Deed transfer {sale_date} · {incoming["llc"] or "Unknown entity"} · assessed {incoming["v"] or "unknown"}'
                if note not in (seed.get('notes') or ''):
                    seed['notes'] = ((seed.get('notes') or '') + '\n' + note).strip()
                market['text'] = patch(market['text'], 'SEED_POINTS', identifier, seed)
                if action == 'unchanged':
                    action = 'updated'
        by_address[normalized].add((destination, identifier))
        if apn:
            by_parcel[apn].add((destination, identifier))
        counts[action] += 1
        per_market[destination][action] += 1
        dispositions.append(f'{row_number:02d} {action.upper()} {address} -> {destination} | id={identifier}' + (' | permit overlap' if permit_hits else ''))
    writes = {}
    for name, market in markets.items():
        validate(market['original'], market['text'], market['data'])
        if market['text'] != market['original']:
            writes[market['path']] = market['text']
        if market['additions']:
            dates = [r['sale_date'] for r in market['additions']]
            market['metadata']['pulls'].append(dict(pulled_date=today, window_start=min(dates), window_end=max(dates),
                source_file=args.csv_path.name, source='DealMachine export', property_count=len(market['additions']),
                properties=market['additions']))
            writes[market['metadata_path']] = json.dumps(market['metadata'], indent=1, ensure_ascii=True, allow_nan=False) + '\n'
    ledger = ROOT / 'pulls' / ('dropped_' + today + '.csv')
    prior = set()
    if ledger.exists():
        with ledger.open(newline='') as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != ['MARKET', 'PROJECT_NO', 'ADDRESS', 'REASON', 'DETAIL']:
                raise ValueError('incompatible dropped ledger header')
            prior = {tuple(r[k] for k in reader.fieldnames) for r in reader}
    ledger_new = [r for r in dropped if (args.market,) + r not in prior]
    print(('DRY RUN' if args.dry_run else 'APPLY') + f' | source={args.csv_path.name} | rows read={len(rows)}')
    print('Rule: configured polygons; Heights street guard + lng <= -95.370; route across enabled markets.')
    print('\n'.join(dispositions))
    print(f"TOTAL read={len(rows)} accepted={len(rows)-counts['excluded']} added={counts['added']} updated={counts['updated']} unchanged={counts['unchanged']} excluded={counts['excluded']}")
    for name, summary in sorted(per_market.items()):
        print(f'MARKET {name}: ' + ' '.join(f'{k}={summary[k]}' for k in ('added', 'updated', 'unchanged')))
    print('EXCLUSIONS ' + json.dumps(dict(Counter(r[2] for r in dropped)), sort_keys=True))
    print('PERMIT OVERLAPS ' + str(len(overlaps)))
    for overlap in overlaps:
        print('  ' + overlap)
    print('FILES ' + (', '.join(p.name for p in writes) or '(none)'))
    print(f'LEDGER {ledger.relative_to(ROOT)}: excluded={len(dropped)} new_entries={len(ledger_new)}')
    if counts['added'] + counts['updated'] + counts['unchanged'] + counts['excluded'] != len(rows):
        raise ValueError('row conservation failed')
    if args.dry_run:
        print('No files written.')
        return
    # Detect concurrent edits before writing any of the planned HTML files.
    for market in markets.values():
        if market['path'].read_text() != market['original']:
            raise ValueError('HTML changed during ingest; rerun')
    for path, text in writes.items():
        path.write_text(text)
    if ledger_new:
        write_dropped_ledger(str(ledger), args.market, ledger_new)
    print(f'WROTE {len(writes)} files; ledger rows appended={len(ledger_new)}')


if __name__ == '__main__':
    main()
