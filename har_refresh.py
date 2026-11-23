#!/usr/bin/env python3
"""Refresh sold comps, active pins, under-contract pins, and market-status prices.

One active CSV, one sold CSV, and one pending CSV. Rows are assigned with
har_markets and written per market. Dry run by default.

    python3 har_refresh.py --active markets_active.csv --sold markets_sold.csv --pending pending.csv --as-of 2026-11-23
    python3 har_refresh.py --pending exports/pending.csv --as-of 2026-11-23 --apply

An address is in only one of Active, Under Contract, and Sold. A pending
address is removed from the active snapshot, so a home that goes under
contract moves instead of disappearing. Pending rows are not Off Market
and they are not sold comps.

Heights active and sold stay on active_ingest.py and sold_ingest.py.
Heights under-contract rows from the pending export are written to
heights_pending.data.json. A pending-only run leaves sold comps and
market-status files as they are.
"""
import argparse
import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

from active_ingest import market_key
from deed_ingest import load_overrides, normalize, span
from har_markets import (
    assign_market, listing_reason, load_zones, product_for, status_bucket, writable_markets,
)
from market_address import address_key
from market_config import MARKETS
from sold_classification import MIN_LOT_SQFT, MIN_YEAR_BUILT, lot_floor_reason
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
    record = dict(
        mls=blank(row.get('MLS Number')),
        address=blank(row.get('Address')),
        address_key=address_key(row.get('Address')),
        original_list_price=money(row.get('Original List Price')),
        current_list_price=money(row.get('List Price')),
        dom=money(row.get('DOM')),
        lot_sqft=lot,
        product=product_for(row),
        builder=blank(row.get('Builder Name')),
        list_agent='',
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
    if bucket == 'pending':
        # The under-contract popup names the listing agent and links to HAR.
        # Active and sold records still leave list_agent empty.
        record['sqft'] = money(row.get('Building SqFt'))
        record['list_agent'] = blank(row.get('List Agent Full Name'))
        record['har_url'] = 'https://www.har.com/search/dosearch?mlsnum=' + record['mls']
    return record


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
        la='',
        ba='',
        coh='nc',
    )
    if original:
        record['svl'] = round((price - original) / original, 4)
    if dom == 0:
        record['p'] = 1
    return record


def scrub_sale(row):
    """Agent names are not stored. Builder and school stay."""
    row['la'] = ''
    row['ba'] = ''
    return row


def pinned_markets():
    """market_key -> markets whose DATA already shows that address."""
    found = defaultdict(set)
    pages = [(name, cfg['html']) for name, cfg in MARKETS.items()]
    if 'springvalley' not in MARKETS:
        pages.append(('springvalley', 'springvalley.html'))
    for name, html_name in pages:
        for row in span((ROOT / html_name).read_text(), 'DATA')[2]:
            key = market_key(row.get('a'))
            if key:
                found[key].add(name)
    return found


def preferred_market(address, candidates, pinned, overrides):
    """One map for an address. None when the candidates still disagree."""
    owners = pinned.get(market_key(address), set()) & set(candidates)
    if len(owners) == 1:
        return next(iter(owners))
    override = overrides.get(normalize(address))
    if override in candidates:
        return override
    if len(candidates) == 1:
        return next(iter(candidates))
    return None


def merge_sold(existing, incoming, as_of):
    """Keep the trailing year. This week's export adds and refreshes; it does not erase older comps."""
    today = date.fromisoformat(as_of)
    start = today - timedelta(days=365)
    by_id = {}
    for row in existing:
        by_id[row['id']] = scrub_sale(dict(row))
    added = updated = 0
    for row in incoming:
        scrub_sale(row)
        if row['id'] in by_id:
            updated += 1
        else:
            added += 1
        by_id[row['id']] = row
    kept, aged = [], []
    for row in by_id.values():
        closed = date.fromisoformat(row['cd'])
        if closed < start or closed > today:
            aged.append(dict(id=row['id'], address=row.get('a'), reason='OUTSIDE_365_DAY_COMP_WINDOW'))
            continue
        floor = lot_floor_reason(row.get('lot'))
        if floor:
            aged.append(dict(id=row['id'], address=row.get('a'), reason=floor))
            continue
        kept.append(row)
    return refresh_derived(kept, today), added, updated, aged


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


def load_active_listings(name):
    path = ROOT / (name + '_active.data.json')
    if not path.exists():
        return []
    return json.loads(path.read_text()).get('listings') or []


def load_sold_comps(name):
    path = ROOT / (name + '_sold.data.json')
    if not path.exists():
        return []
    return json.loads(path.read_text()).get('comps') or []


def pending_document(name, rows, as_of, source_name):
    return dict(
        as_of=as_of,
        scope=(
            'Current HAR under-contract snapshot for %s. Status is Pending, '
            'Option Pending, or Pend Cont to Show. List Price is the asking price '
            'on the export date. Year built >= %s; lot size >= %s sqft. '
            'An address in this list is not in the active snapshot and not in sold comps. '
            'Source: %s.'
            % (name, MIN_YEAR_BUILT, MIN_LOT_SQFT, source_name)
        ),
        listings=sorted(rows, key=lambda row: row['mls']),
    )


def assert_pending_exclusive(name, active_rows, pending_rows, sold_rows):
    """A home is in only one of Active, Under Contract, and Sold."""
    active_keys = {row.get('address_key') or address_key(row.get('address') or '') for row in active_rows}
    pending_keys = {row['address_key'] for row in pending_rows}
    sold_keys = {address_key(row.get('a') or '') for row in sold_rows}
    overlap = {
        'active_pending': sorted(key for key in active_keys & pending_keys if key),
        'pending_sold': sorted(key for key in pending_keys & sold_keys if key),
    }
    bad = {key: values for key, values in overlap.items() if values}
    if bad:
        raise ValueError(
            '%s listing is in more than one of Active / Under Contract / Sold: %s'
            % (name, json.dumps(bad))
        )


def run(active_path, sold_path, as_of, apply=False, markets=None, pending_path=None):
    date.fromisoformat(as_of)
    if bool(active_path) != bool(sold_path):
        raise ValueError('Active and sold exports are a pair')
    if not active_path and not pending_path:
        raise ValueError('Pass an active and sold export, a pending export, or all three')
    have_active = bool(active_path)
    have_sold = bool(sold_path)
    have_pending = bool(pending_path)
    write_markets = list(markets) if markets is not None else writable_markets()
    unknown = [name for name in write_markets if name not in MARKETS or name == 'heights']
    if unknown:
        raise ValueError('Refusing Heights or unknown market: ' + ', '.join(unknown))
    include_heights = markets is None
    zones = load_zones()
    overrides = load_overrides()
    pinned = pinned_markets()
    if have_active:
        actives_raw, active_digest, active_name = read_csv(active_path)
    else:
        actives_raw, active_digest, active_name = [], None, None
    if have_sold:
        solds_raw, sold_digest, sold_name = read_csv(sold_path)
    else:
        solds_raw, sold_digest, sold_name = [], None, None
    if have_pending:
        pendings_raw, pending_digest, pending_name = read_csv(pending_path)
    else:
        pendings_raw, pending_digest, pending_name = [], None, None
    pending_source = ' + '.join(name for name in (pending_name, active_name) if name) or 'pending export'
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
        market, geo_reason, detail = assign_market(lat, lng, address, zones, overrides)
        if geo_reason in ('AMBIGUOUS_MARKET', 'OUT_OF_MARKET', 'INVALID_COORDINATES', 'OVERRIDE_MARKET') or market is None:
            reason = geo_reason or 'OUT_OF_MARKET'
            unassigned[reason] += 1
            if reason == 'AMBIGUOUS_MARKET':
                ambiguous.append(dict(address=address, mls=mls, lat=lat, lng=lng, file=filename, markets=detail))
            ledger.append(dict(FILE=filename, SHA256=digest, ROW=line, MLS=mls, ADDRESS=address, MARKET='', REASON=reason))
            return
        bucket = status_bucket(row, kind)
        # Heights active and sold stay on their own pipeline. Under-contract
        # rows use the same year and lot filters, then land in the Heights
        # pending snapshot instead of being withheld.
        if geo_reason == 'HEIGHTS_SEPARATE_PIPELINE' and bucket == 'pending':
            reason = listing_reason(row, 'pending')
        else:
            reason = geo_reason or listing_reason(row, kind)
        if reason is None and bucket == 'sold':
            reason = sold_reason(row, as_of)
        if reason == 'HEIGHTS_SEPARATE_PIPELINE':
            per['heights']['dropped'][reason] += 1
            heights_rows.append(dict(address=address, mls=mls, file=filename, lot=row.get('Lot Size'), year=row.get('Year Built')))
            ledger.append(dict(FILE=filename, SHA256=digest, ROW=line, MLS=mls, ADDRESS=address, MARKET='heights', REASON=reason))
            return
        owners = pinned.get(market_key(address), set())
        if owners and market not in owners:
            per[market]['dropped']['ALREADY_ON_OTHER_MARKET'] += 1
            ledger.append(dict(FILE=filename, SHA256=digest, ROW=line, MLS=mls, ADDRESS=address, MARKET=market, REASON='ALREADY_ON_OTHER_MARKET'))
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

    for line, row in enumerate(pendings_raw, 2):
        take('pending', pending_name, pending_digest, line, row)
    for line, row in enumerate(actives_raw, 2):
        take('active', active_name, active_digest, line, row)
    for line, row in enumerate(solds_raw, 2):
        take('sold', sold_name, sold_digest, line, row)

    # One address on one market, even when two coordinates disagree.
    cross_market = []
    grouped = defaultdict(list)
    for name in write_markets:
        for kind in ('active', 'pending', 'terminated', 'sold'):
            for index, row in enumerate(per[name][kind]):
                address = row['a'] if kind == 'sold' else row['address']
                grouped[market_key(address)].append((name, kind, index, address))
    drop_at = defaultdict(set)
    for key, items in grouped.items():
        markets = {item[0] for item in items}
        if len(markets) < 2:
            continue
        keep = preferred_market(items[0][3], markets, pinned, overrides)
        for name, kind, index, address in items:
            if name == keep:
                continue
            drop_at[(name, kind)].add(index)
            cross_market.append(dict(address=address, kept=keep, dropped=name, kind=kind))
            per[name]['dropped']['ALREADY_ON_OTHER_MARKET'] += 1
    for (name, kind), indexes in drop_at.items():
        per[name][kind] = [row for index, row in enumerate(per[name][kind]) if index not in indexes]

    layer_names = list(write_markets) + (['heights'] if include_heights else [])
    if not have_active:
        for name in layer_names:
            per[name]['active'] = load_active_listings(name)
    elif include_heights:
        # Heights active is not rebuilt from the multi-market CSV. Seed it
        # so a pending address can be removed without wiping the snapshot.
        per['heights']['active'] = load_active_listings('heights')

    # Sold comps win over a pending row at the same address. Pending wins
    # over active: the active row is removed and reported as a move.
    for name in layer_names:
        sold_keys = {address_key(row.get('a') or '') for row in load_sold_comps(name)}
        if have_sold:
            sold_keys.update(address_key(row['a']) for row in per[name]['sold'])
        kept_pending = []
        for row in per[name]['pending']:
            if row['address_key'] in sold_keys:
                per[name]['dropped']['IN_SOLD_COMPS'] += 1
                ledger.append(dict(
                    FILE=row.get('source_file') or '', SHA256=row.get('source_sha256') or '',
                    ROW=row.get('source_row') or '', MLS=row.get('mls') or '',
                    ADDRESS=row.get('address') or '', MARKET=name, REASON='IN_SOLD_COMPS',
                ))
                continue
            kept_pending.append(row)
        per[name]['pending'] = kept_pending
    pending_keys = {row['address_key'] for name in layer_names for row in per[name]['pending']}
    pending_mls = {row['mls'] for name in layer_names for row in per[name]['pending']}
    moved_from_active = []
    for name in layer_names:
        seen_mls = set()
        for row in load_active_listings(name):
            key = row.get('address_key') or address_key(row.get('address') or '')
            if (key and key in pending_keys) or row.get('mls') in pending_mls:
                seen_mls.add(row.get('mls'))
                moved_from_active.append(dict(market=name, mls=row.get('mls'), address=row.get('address')))
        before_active = list(per[name]['active'])
        per[name]['active'] = [
            row for row in before_active
            if row.get('address_key') not in pending_keys and row.get('mls') not in pending_mls
        ]
        for row in before_active:
            if row.get('mls') in seen_mls:
                continue
            if row.get('address_key') in pending_keys or row.get('mls') in pending_mls:
                seen_mls.add(row.get('mls'))
                moved_from_active.append(dict(market=name, mls=row.get('mls'), address=row.get('address')))
        sold_rows = load_sold_comps(name)
        if have_sold:
            sold_rows = sold_rows + per[name]['sold']
        assert_pending_exclusive(name, per[name]['active'], per[name]['pending'], sold_rows)

    outputs = {}
    summaries = {}
    eyeballs = []
    markets_for_full_write = write_markets if have_active else []
    for name in markets_for_full_write:
        bucket = per[name]
        sold_file = ROOT / (name + '_sold.data.json')
        existing_sales = json.loads(sold_file.read_text())['comps'] if sold_file.exists() else []
        existing_sales = [row for row in existing_sales if not pinned.get(market_key(row.get('a')), set()) - {name}]
        sales, sold_added, sold_updated, aged = merge_sold(existing_sales, bucket['sold'], as_of)
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
            coverage='Trailing 365 days. This export adds and refreshes sales; it does not replace the prior year.',
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
        if have_pending:
            outputs[ROOT / (name + '_pending.data.json')] = json.dumps(
                pending_document(name, bucket['pending'], as_of, pending_source), indent=2) + '\n'
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
                incoming=len(bucket['sold']),
                added=sold_added,
                updated=sold_updated,
                aged=len(aged),
                single=sum(row['prod'] == 'Single Lot' for row in sales),
                split=sum(row['prod'] == 'Split Lot' for row in sales),
            ),
            pending=len(bucket['pending']),
            terminated=len(bucket['terminated']),
            dropped=dict(bucket['dropped']),
            linked=snapshot['coverage']['linked'],
            moved_from_active=sum(1 for row in moved_from_active if row['market'] == name),
        )
    if not have_active:
        for name in write_markets:
            bucket = per[name]
            current = load_active_listings(name)
            if current != bucket['active']:
                path = ROOT / (name + '_active.data.json')
                doc = json.loads(path.read_text()) if path.exists() else dict(as_of=as_of, scope='', listings=[])
                doc['listings'] = sorted(bucket['active'], key=lambda row: row['mls'])
                outputs[path] = json.dumps(doc, indent=2) + '\n'
            if have_pending:
                outputs[ROOT / (name + '_pending.data.json')] = json.dumps(
                    pending_document(name, bucket['pending'], as_of, pending_source), indent=2) + '\n'
            summaries[name] = dict(
                active=dict(
                    accepted=len(bucket['active']),
                    single=sum(row.get('product') == 'Single Lot' for row in bucket['active']),
                    split=sum(row.get('product') == 'Split Lot' for row in bucket['active']),
                ),
                sold=dict(accepted=len(load_sold_comps(name)), incoming=0, added=0, updated=0, aged=0, single=0, split=0),
                pending=len(bucket['pending']),
                terminated=len(bucket['terminated']),
                dropped=dict(bucket['dropped']),
                linked=0,
                moved_from_active=sum(1 for row in moved_from_active if row['market'] == name),
                note='Pending pass. Sold comps and market status were left as they were.',
            )
    if include_heights and have_pending:
        outputs[ROOT / 'heights_pending.data.json'] = json.dumps(
            pending_document('heights', per['heights']['pending'], as_of, pending_source), indent=2) + '\n'
        current = load_active_listings('heights')
        if current != per['heights']['active']:
            path = ROOT / 'heights_active.data.json'
            doc = json.loads(path.read_text())
            doc['listings'] = sorted(per['heights']['active'], key=lambda row: row['mls'])
            outputs[path] = json.dumps(doc, indent=2) + '\n'
    summaries['heights'] = dict(
        active=dict(
            accepted=len(per['heights']['active']) if not have_active else 0,
            single=0, split=0,
        ),
        sold=dict(accepted=0, single=0, split=0),
        pending=len(per['heights']['pending']),
        terminated=0,
        dropped=dict(per['heights']['dropped']),
        linked=0,
        moved_from_active=sum(1 for row in moved_from_active if row['market'] == 'heights'),
        note=(
            'Active and sold are not replaced. Under-contract rows are written to heights_pending.data.json.'
            if include_heights and have_pending else
            'Not written. Heights keeps the existing sold_ingest and active_ingest snapshot.'
        ),
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
        cross_market=cross_market,
        heights_withheld=heights_rows,
        eyeball=eyeballs,
        ledger_rows=len(ledger),
        moved_from_active=moved_from_active,
    )
    print(json.dumps(report, indent=2))
    protected = [
        ROOT / 'index.html',
        ROOT / 'heights_market_status.data.json',
    ]
    heights_active_path = ROOT / 'heights_active.data.json'
    heights_active_before = heights_active_path.read_bytes() if heights_active_path.exists() else None
    before = {path: path.read_bytes() for path in protected if path.exists()}
    if apply:
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        for path, text in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        ledger_path.write_text(ledger_buf.getvalue())
    for path, raw in before.items():
        if path.read_bytes() != raw:
            raise ValueError('Heights file changed: ' + path.name)
    if heights_active_before is not None:
        current = heights_active_path.read_bytes()
        if current != heights_active_before:
            old_doc = json.loads(heights_active_before)
            new_doc = json.loads(current)
            old_rows = {row['mls']: row for row in old_doc.get('listings') or []}
            new_rows = {row['mls']: row for row in new_doc.get('listings') or []}
            if set(new_rows) - set(old_rows):
                raise ValueError('Heights active gained listings')
            for mls, row in new_rows.items():
                if old_rows[mls] != row:
                    raise ValueError('Heights active listing changed: ' + mls)
            for mls, row in old_rows.items():
                if mls in new_rows:
                    continue
                key = row.get('address_key') or ''
                if key not in pending_keys and mls not in pending_mls:
                    raise ValueError('Heights active lost a listing that is not under contract: ' + row.get('address', mls))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--active', help='Active HAR export covering every market')
    parser.add_argument('--sold', help='Sold HAR export covering every market')
    parser.add_argument('--pending', help='Pending / under-contract HAR export (pending.csv)')
    parser.add_argument('--as-of', required=True, help='YYYY-MM-DD export date')
    parser.add_argument('--market', action='append', help='Limit to one writable market; repeatable. Heights is refused.')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    run(args.active, args.sold, args.as_of, apply=args.apply, markets=args.market, pending_path=args.pending)


if __name__ == '__main__':
    main()
