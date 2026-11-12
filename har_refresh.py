#!/usr/bin/env python3
"""Refresh sold comps, active pins, and market-status prices for every non-Heights market.

One active CSV and one sold CSV. Rows are assigned with har_markets and
written per market. Dry run by default.

    python3 har_refresh.py --active markets_active.csv --sold markets_sold.csv --as-of 2026-11-12
    python3 har_refresh.py --active markets_active.csv --sold markets_sold.csv --as-of 2026-11-12 --apply

Heights is not written. Rows inside the Heights boundary are counted as
HEIGHTS_SEPARATE_PIPELINE. Pending rows are tagged pending. They are not
Off Market and they are not sold comps.
"""
import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

from deed_ingest import span
from har_markets import (
    assign_market, listing_reason, load_zones, product_for, status_bucket, writable_markets,
)
from market_address import address_key
from market_config import MARKETS
from sold_classification import MIN_LOT_SQFT, MIN_YEAR_BUILT
from sold_ingest import metrics_for, money, parse_close, refresh_derived

ROOT = Path(__file__).resolve().parent
LEDGER_FIELDS = ['FILE', 'SHA256', 'ROW', 'MLS', 'ADDRESS', 'MARKET', 'REASON']


def read_csv(path):
    payload = Path(path).read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    reader = csv.DictReader(io.StringIO(payload.decode('utf-8-sig')))
    required = {
        'MLS Number', 'Address', 'Latitude', 'Longitude', 'Status', 'List Price',
        'Original List Price', 'Close Price', 'Close Date', 'Building SqFt',
        'Lot Size', 'DOM', 'Year Built', 'Builder Name', 'School Elementary',
        'List Agent Full Name', 'Selling Agent Full Name',
    }
    missing = required - set(reader.fieldnames or [])
    if missing:
        raise ValueError('Missing columns in %s: %s' % (path, ', '.join(sorted(missing))))
    rows = list(reader)
    if not rows:
        raise ValueError('Empty export: ' + str(path))
    return rows, digest, Path(path).name


def sold_reason(row, as_of):
    closed = parse_close(row.get('Close Date'))
    price = money(row.get('Close Price'))
    sqft = money(row.get('Building SqFt'))
    today = date.fromisoformat(as_of)
    start = today - timedelta(days=365)
    if not closed or price is None or price <= 0:
        return 'INVALID_CLOSE'
    if closed < start or closed > today:
        return 'OUTSIDE_365_DAYS'
    if sqft is None or sqft <= 0:
        return 'MISSING_BUILDING_SQFT'
    original = money(row.get('Original List Price'))
    if original is None or original <= 0:
        return 'MISSING_ORIGINAL_PRICE'
    return None


def blank(value):
    return (value or '').strip()


def active_record(row, line, filename, digest, as_of, bucket):
    lot = money(row.get('Lot Size'))
    return dict(
        mls=blank(row.get('MLS Number')),
        address=blank(row.get('Address')),
        address_key=address_key(row.get('Address')),
        original_list_price=money(row.get('Original List Price')),
        current_list_price=money(row.get('List Price')),
        dom=money(row.get('DOM')),
        lot_sqft=lot,
        product=product_for(row),
        builder=blank(row.get('Builder Name')),
        list_agent=blank(row.get('List Agent Full Name')),
        year_built=money(row.get('Year Built')),
        lat=money(row.get('Latitude')),
        lng=money(row.get('Longitude')),
        status=bucket,
        har_status=blank(row.get('Status')),
        as_of=as_of,
        source_file=filename,
        source_row=line,
        source_sha256=digest,
    )


def sold_record(row, as_of):
    price = money(row.get('Close Price'))
    sqft = money(row.get('Building SqFt'))
    original = money(row.get('Original List Price'))
    dom = money(row.get('DOM'))
    record = dict(
        id='s' + blank(row.get('MLS Number')),
        a=blank(row.get('Address')),
        lat=round(money(row.get('Latitude')), 7),
        lng=round(money(row.get('Longitude')), 7),
        cp=price,
        sq=sqft,
        cd=parse_close(row.get('Close Date')).isoformat(),
        psf=round(price / sqft, 1),
        lp=original,
        lot=money(row.get('Lot Size')),
        dom=dom,
        yb=money(row.get('Year Built')),
        har_psf=None,
        bl=blank(row.get('Builder Name')),
        sch=blank(row.get('School Elementary')),
        la=blank(row.get('List Agent Full Name')),
        ba=blank(row.get('Selling Agent Full Name')),
        coh='nc',
    )
    if original:
        record['svl'] = round((price - original) / original, 4)
    if dom == 0:
        record['p'] = 1
    return record


def current_from_listing(listing, as_of):
    return dict(
        mls=listing['mls'],
        status=listing['status'],
        har_status=listing['har_status'],
        product=listing['product'],
        current_list_price=listing.get('current_list_price'),
        original_list_price=listing.get('original_list_price'),
        dom=listing.get('dom'),
        close_date=None,
        close_price=None,
        as_of=as_of,
        address=listing['address'],
    )


def current_from_sale(sale, as_of):
    return dict(
        mls=sale['id'][1:],
        status='sold',
        har_status='Sold',
        product=sale.get('prod'),
        current_list_price=None,
        original_list_price=sale.get('lp'),
        dom=sale.get('dom'),
        close_date=sale.get('cd'),
        close_price=sale.get('cp'),
        as_of=as_of,
        address=sale.get('a'),
    )


def build_snapshot(data_rows, actives, pendings, terminated, sales, as_of):
    """Link HAR evidence onto DATA pins. Does not invent Off Market tags."""
    by_key_active = {row['address_key']: row for row in actives}
    by_key_pending = {row['address_key']: row for row in pendings}
    by_key_terminated = {row['address_key']: row for row in terminated}
    sales_by_key = defaultdict(list)
    for sale in sales:
        sales_by_key[address_key(sale['a'])].append(sale)
    tracked = []
    properties = {}
    for record in data_rows:
        key = address_key(record.get('a') or '')
        if not key:
            continue
        active = by_key_active.get(key)
        pending = by_key_pending.get(key)
        ended = by_key_terminated.get(key)
        history = sorted(sales_by_key.get(key, []), key=lambda sale: sale['cd'], reverse=True)
        if not any((active, pending, ended, history)):
            continue
        if active:
            status, current = 'active', current_from_listing(active, as_of)
        elif pending:
            status, current = 'pending', current_from_listing(pending, as_of)
        elif history:
            status, current = 'sold', current_from_sale(history[0], as_of)
        else:
            status, current = 'terminated', current_from_listing(ended, as_of)
        entry = dict(
            member=record['id'], pin=record['id'], address=record.get('a'),
            status=status, current=current, history=[],
            historical_sales=[
                dict(id=sale['id'], cd=sale['cd'], cp=sale['cp'], a=sale['a'])
                for sale in history
            ],
            archive_current=None, ordering_issue=None,
        )
        tracked.append(entry)
        properties[record['id']] = dict(status=status, current=current)
    return dict(
        as_of=as_of,
        price_basis=(
            'List Price is the asking price on the export date; '
            'Original List Price is retained separately. '
            'Pending listings are tagged pending and are not Off Market.'
        ),
        properties=properties,
        tracked=tracked,
        coverage=dict(
            active=len(actives), pending=len(pendings), sold=len(sales),
            terminated=len(terminated), linked=len(tracked),
        ),
    )


def _bump(bucket, reason):
    bucket[reason] = bucket.get(reason, 0) + 1


def run(active_path, sold_path, as_of, apply=False, markets=None):
    date.fromisoformat(as_of)
    write_markets = list(markets) if markets is not None else writable_markets()
    unknown = [name for name in write_markets if name not in MARKETS or name == 'heights']
    if unknown:
        raise ValueError('Refusing Heights or unknown market: ' + ', '.join(unknown))
    zones = load_zones()
    actives_raw, active_digest, active_name = read_csv(active_path)
    solds_raw, sold_digest, sold_name = read_csv(sold_path)
    per = {name: dict(active=[], pending=[], terminated=[], sold=[], dropped=Counter()) for name in write_markets}
    per['heights'] = dict(active=[], pending=[], terminated=[], sold=[], dropped=Counter())
    unassigned = Counter()
    ledger = []
    ambiguous = []
    heights_rows = []
    seen = defaultdict(lambda: dict(mls=set(), address=set()))

    def take(kind, filename, digest, line, row):
        mls = blank(row.get('MLS Number'))
        address = blank(row.get('Address'))
        lat, lng = money(row.get('Latitude')), money(row.get('Longitude'))
        if not mls or not address:
            unassigned['INVALID_REQUIRED_FIELD'] += 1
            ledger.append(dict(FILE=filename, SHA256=digest, ROW=line, MLS=mls, ADDRESS=address, MARKET='', REASON='INVALID_REQUIRED_FIELD'))
            return
        market, geo_reason, detail = assign_market(lat, lng, address, zones)
        if geo_reason in ('AMBIGUOUS_MARKET', 'OUT_OF_MARKET', 'INVALID_COORDINATES') or market is None:
            reason = geo_reason or 'OUT_OF_MARKET'
            unassigned[reason] += 1
            if reason == 'AMBIGUOUS_MARKET':
                ambiguous.append(dict(address=address, mls=mls, lat=lat, lng=lng, file=filename, markets=detail))
            ledger.append(dict(FILE=filename, SHA256=digest, ROW=line, MLS=mls, ADDRESS=address, MARKET='', REASON=reason))
            return
        reason = geo_reason or listing_reason(row, kind)
        bucket = status_bucket(row, kind)
        if reason is None and bucket == 'sold':
            reason = sold_reason(row, as_of)
        if reason == 'HEIGHTS_SEPARATE_PIPELINE':
            per['heights']['dropped'][reason] += 1
            heights_rows.append(dict(address=address, mls=mls, file=filename, lot=row.get('Lot Size'), year=row.get('Year Built')))
            ledger.append(dict(FILE=filename, SHA256=digest, ROW=line, MLS=mls, ADDRESS=address, MARKET='heights', REASON=reason))
            return
        if market not in per:
            unassigned['MARKET_NOT_IN_PASS'] += 1
            ledger.append(dict(FILE=filename, SHA256=digest, ROW=line, MLS=mls, ADDRESS=address, MARKET=market, REASON='MARKET_NOT_IN_PASS'))
            return
        if reason:
            per[market]['dropped'][reason] += 1
            ledger.append(dict(FILE=filename, SHA256=digest, ROW=line, MLS=mls, ADDRESS=address, MARKET=market, REASON=reason))
            return
        slot = seen[market]
        address_id = address_key(address)
        if mls in slot['mls'] or (bucket in ('active', 'pending') and address_id in slot['address']):
            per[market]['dropped']['DUP_INPUT'] += 1
            ledger.append(dict(FILE=filename, SHA256=digest, ROW=line, MLS=mls, ADDRESS=address, MARKET=market, REASON='DUP_INPUT'))
            return
        slot['mls'].add(mls)
        if bucket in ('active', 'pending', 'terminated'):
            slot['address'].add(address_id)
            per[market][bucket].append(active_record(row, line, filename, digest, as_of, bucket))
        else:
            per[market]['sold'].append(sold_record(row, as_of))

    for line, row in enumerate(actives_raw, 2):
        take('active', active_name, active_digest, line, row)
    for line, row in enumerate(solds_raw, 2):
        take('sold', sold_name, sold_digest, line, row)

    outputs = {}
    summaries = {}
    eyeballs = []
    for name in write_markets:
        bucket = per[name]
        sales = refresh_derived(bucket['sold'], date.fromisoformat(as_of))
        if any(row.get('prod') not in ('Single Lot', 'Split Lot') for row in sales):
            raise ValueError(name + ': sold comp missing a lot class')
        metrics = metrics_for(sales, date.fromisoformat(as_of))
        label = name
        metrics['basis'] = (
            'Displayed new-construction comps, trailing 365 days, lot size >= %s sqft, '
            'year built >= %s. %s. Pending listings are excluded from comps.'
            % (f'{MIN_LOT_SQFT:,}', MIN_YEAR_BUILT, label)
        )
        policy = dict(
            kind='new_construction_trailing_365',
            as_of=as_of,
            start=(date.fromisoformat(as_of) - timedelta(days=365)).isoformat(),
            end=as_of,
            source=sold_name,
            min_lot_sqft=MIN_LOT_SQFT,
            coverage='HAR export assigned by market boundary or coordinate box',
        )
        active_doc = dict(
            as_of=as_of,
            scope=(
                'Current HAR active snapshot for %s. List Price is the asking price on '
                'the export date; Original List Price is retained separately. '
                'Year built >= %s; lot size >= %s sqft. Pending rows are not in this list.'
                % (name, MIN_YEAR_BUILT, MIN_LOT_SQFT)
            ),
            listings=sorted(bucket['active'], key=lambda row: row['mls']),
        )
        sold_doc = dict(as_of=as_of, policy=policy, metrics=metrics, comps=sales)
        html = (ROOT / MARKETS[name]['html']).read_text()
        data_rows = span(html, 'DATA')[2]
        if not data_rows:
            raise ValueError(name + ': DATA is empty; refusing to write market status')
        snapshot = build_snapshot(
            data_rows, bucket['active'], bucket['pending'], bucket['terminated'], sales, as_of)
        outputs[ROOT / (name + '_active.data.json')] = json.dumps(active_doc, indent=2) + '\n'
        outputs[ROOT / (name + '_sold.data.json')] = json.dumps(sold_doc, indent=2) + '\n'
        outputs[ROOT / (name + '_market_status.data.json')] = json.dumps(snapshot, indent=2) + '\n'
        for listing in bucket['active']:
            text = listing['address'].lower()
            if '43rd' in text or 'shepherd' in text:
                eyeballs.append(dict(market=name, address=listing['address'], kind='active'))
        for sale in sales:
            text = sale['a'].lower()
            if '43rd' in text or 'shepherd' in text:
                eyeballs.append(dict(market=name, address=sale['a'], kind='sold'))
        summaries[name] = dict(
            active=dict(
                accepted=len(bucket['active']),
                single=sum(row['product'] == 'Single Lot' for row in bucket['active']),
                split=sum(row['product'] == 'Split Lot' for row in bucket['active']),
            ),
            sold=dict(
                accepted=len(sales),
                single=sum(row['prod'] == 'Single Lot' for row in sales),
                split=sum(row['prod'] == 'Split Lot' for row in sales),
            ),
            pending=len(bucket['pending']),
            terminated=len(bucket['terminated']),
            dropped=dict(bucket['dropped']),
            linked=snapshot['coverage']['linked'],
        )
    summaries['heights'] = dict(
        active=dict(accepted=0, single=0, split=0),
        sold=dict(accepted=0, single=0, split=0),
        pending=0, terminated=0,
        dropped=dict(per['heights']['dropped']),
        linked=0,
        note='Not written. Heights keeps the existing sold_ingest and active_ingest snapshot.',
    )
    ledger_buf = io.StringIO(newline='')
    writer = csv.DictWriter(ledger_buf, fieldnames=LEDGER_FIELDS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(ledger)
    ledger_path = ROOT / 'pulls' / ('dropped_har_' + as_of + '.csv')
    report = dict(
        as_of=as_of,
        mode='APPLY' if apply else 'DRY RUN',
        markets=summaries,
        unassigned=dict(unassigned),
        ambiguous=ambiguous,
        heights_withheld=heights_rows,
        eyeball=eyeballs,
        ledger_rows=len(ledger),
    )
    print(json.dumps(report, indent=2))
    protected = [
        ROOT / 'index.html',
        ROOT / 'heights_active.data.json',
        ROOT / 'heights_market_status.data.json',
    ]
    before = {path: path.read_bytes() for path in protected}
    if apply:
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        for path, text in outputs.items():
            path.write_text(text)
        ledger_path.write_text(ledger_buf.getvalue())
    for path, raw in before.items():
        if path.read_bytes() != raw:
            raise ValueError('Heights file changed: ' + path.name)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--active', required=True, help='Active HAR export covering every market')
    parser.add_argument('--sold', required=True, help='Sold HAR export covering every market')
    parser.add_argument('--as-of', required=True, help='YYYY-MM-DD export date')
    parser.add_argument('--market', action='append', help='Limit to one writable market; repeatable. Heights is refused.')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    run(args.active, args.sold, args.as_of, apply=args.apply, markets=args.market)


if __name__ == '__main__':
    main()
