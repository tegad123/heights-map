"""Assign a HAR row to one live market and apply the shared listing filters.

A market with a boundary matches by point-in-polygon. A market without one
(West University) matches by coordinate box, and by ZIP when the row
actually carries one. A boundary hit wins over a box hit. Two boundary
hits stay unresolved.

Heights is recognized so those rows can be reported, then withheld. The
Heights snapshot is owned by sold_ingest.py and active_ingest.py.
"""
import re
from pathlib import Path

from deed_ingest import in_boundary
from market_config import HAR_MARKETS, MARKETS
from sold_classification import MIN_LOT_SQFT, MIN_YEAR_BUILT, classify_lot, lot_floor_reason
from sold_ingest import money

ROOT = Path(__file__).resolve().parent

PENDING_STATUS = {
    'pending', 'option pending', 'pending continue to show',
    'active under contract', 'under contract',
}
TERMINATED_STATUS = {
    'terminated', 'expired', 'withdrawn', 'terminated-relisted',
}


def row_zip(address):
    match = re.search(r'\b(77\d{3})\b', str(address or ''))
    return match.group(1) if match else None


def zone_pattern(html):
    match = re.search(r'const OUT_OF_ZONE=/(.*?)/i;', html)
    if not match:
        raise ValueError('missing OUT_OF_ZONE')
    return re.compile(match.group(1), re.I)


def load_zones(names=None):
    """Every configured market, including permit-disabled Spring Valley."""
    wanted = list(names) if names is not None else list(MARKETS)
    zones = {}
    for name in wanted:
        cfg = MARKETS[name]
        html = (ROOT / cfg['html']).read_text()
        boundary = None
        if cfg['boundary']:
            import json
            boundary = json.loads((ROOT / cfg['boundary']).read_text())
        zones[name] = dict(
            cfg=cfg,
            boundary=boundary,
            zone=zone_pattern(html),
            html_path=ROOT / cfg['html'],
        )
    return zones


def in_box(cfg, lat, lng):
    bottom, top, left, right = cfg['coord_box']
    return bottom <= lat <= top and left <= lng <= right


def assign_market(lat, lng, address, zones):
    """Return (market, reason, detail). reason is None when the row is in one market.

    OUT_OF_ZONE and the Heights east cutoff are attributed to that market.
    AMBIGUOUS_MARKET and OUT_OF_MARKET have no market. detail lists the
    boundary names when more than one polygon contains the point. A Heights
    hit is returned as market='heights' with HEIGHTS_SEPARATE_PIPELINE
    after the zone guards, so the caller can count it without writing.
    """
    if lat is None or lng is None or not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return None, 'INVALID_COORDINATES', None
    polygons = []
    boxes = []
    for name, zone in zones.items():
        cfg = zone['cfg']
        zipcode = row_zip(address)
        if zone['boundary'] is not None:
            if in_boundary(zone['boundary'], lng, lat):
                polygons.append(name)
        elif in_box(cfg, lat, lng) and (zipcode is None or zipcode in cfg['zips']):
            boxes.append(name)
    if len(polygons) > 1:
        return None, 'AMBIGUOUS_MARKET', ','.join(sorted(polygons))
    if len(polygons) == 1:
        chosen = polygons[0]
    elif len(boxes) == 1:
        chosen = boxes[0]
    elif len(boxes) > 1:
        return None, 'AMBIGUOUS_MARKET', ','.join(sorted(boxes))
    else:
        return None, 'OUT_OF_MARKET', None
    zone = zones[chosen]
    cfg = zone['cfg']
    if cfg['east_lng'] is not None and lng > cfg['east_lng']:
        return chosen, 'OOZ_EAST', None
    if zone['zone'].search(address or ''):
        return chosen, 'OOZ_REGEX', None
    if chosen == 'heights':
        return chosen, 'HEIGHTS_SEPARATE_PIPELINE', None
    return chosen, None, None


def status_bucket(row, kind):
    """active, sold, pending, or terminated. None when the file and status disagree.

    Pending and terminated are evidence. They are not Off Market.
    """
    status = (row.get('Status') or '').strip().lower()
    if status in PENDING_STATUS:
        return 'pending' if kind == 'active' else None
    if status in TERMINATED_STATUS:
        return 'terminated'
    if kind == 'active' and status == 'active':
        if (row.get('Close Price') or '').strip() or (row.get('Close Date') or '').strip():
            return None
        return 'active'
    if kind == 'sold' and status == 'sold':
        return 'sold'
    return None


def listing_reason(row, kind):
    """None when the row may be kept. Year and lot rules run for every bucket."""
    year = money(row.get('Year Built'))
    floor = lot_floor_reason(row.get('Lot Size'))
    if year is None:
        return 'MISSING_YEAR_BUILT'
    if year < MIN_YEAR_BUILT:
        return 'YEAR_BEFORE_MIN'
    if floor:
        return floor
    bucket = status_bucket(row, kind)
    if bucket is None:
        return 'NOT_ACTIVE_EXPORT' if kind == 'active' else 'NOT_SOLD_EXPORT'
    if bucket in ('active', 'pending'):
        ask = money(row.get('List Price'))
        original = money(row.get('Original List Price'))
        dom = money(row.get('DOM'))
        if ask is None or ask <= 0:
            return 'MISSING_CURRENT_PRICE'
        if original is None or original <= 0:
            return 'MISSING_ORIGINAL_PRICE'
        if dom is None or dom < 0:
            return 'INVALID_REQUIRED_FIELD'
    return None


def product_for(row):
    return classify_lot(row.get('Lot Size'))


def writable_markets():
    return list(HAR_MARKETS)
