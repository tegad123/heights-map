#!/usr/bin/env python3
"""One pin per property, and no two pins drawn on the same point.

Same normalized street address inside one market is one property recorded
twice (a permit or listing pin plus an acquisition pin, or two deed rows).
Those records are merged. The surviving pin keeps both ids, permit rows,
sale facts, and notes. Distinct unit letters and distinct house numbers stay
separate even when a shared DealMachine id or a nearby coordinate makes them
look alike.

Pins within NEAR_M meters are the same map point (stacked units or geocode
noise). display_positions() spreads that cluster so the drawn markers do not
coincide. Neighbors farther apart than NEAR_M keep their coordinates.
"""
import math
import re
from collections import defaultdict

from deed_ingest import normalize, patch, span

NEAR_M = 0.70
SEP_M = 16.0
M_PER_DEG = 111320.0
# pinColor() checks `deed` before active_single, so adding the tag would
# recolor a listing or a staged build. Those pins keep the deed in notes.
STAGE_TAGS = {
    'active_single', 'active_split', 'market', 'listed', 'pending',
    'off_market_single', 'off_market_split', 'built', 'sitework',
    'foundation', 'framing', 'dried_in', 'exterior', 'finishing',
    'complete', 'mep_finals', 'interior', 'insulation', 'mep_roughs',
}


def meters(lat1, lng1, lat2, lng2):
    dx = (lat1 - lat2) * M_PER_DEG
    dy = (lng1 - lng2) * M_PER_DEG * math.cos(math.radians(lat1))
    return math.hypot(dx, dy)


def meaningful(value):
    return value not in (None, '', [], {})


def property_ids(record):
    """DealMachine property ids carried by a pin. Unit splits can share one."""
    found = []
    ident = str(record.get('id') or '')
    if ident.isdigit():
        found.append(ident)
    elif ident.startswith('tg_mig_') and ident[7:].isdigit():
        found.append(ident[7:])
    match = re.search(r'property\(id\)=(\d+)', str(record.get('u') or ''))
    if match and match.group(1) not in found:
        found.append(match.group(1))
    return found


def address_groups(records):
    groups = defaultdict(list)
    for record in records:
        key = normalize(record.get('a'))
        if key:
            groups[key].append(record)
    return {key: rows for key, rows in groups.items() if len(rows) > 1}


def same_address_ids(records):
    """Property ids that label two pins with one normalized address."""
    by_pid = defaultdict(list)
    for record in records:
        for pid in property_ids(record):
            by_pid[pid].append(record)
    bad = []
    for pid, rows in by_pid.items():
        keys = {normalize(row.get('a')) for row in rows}
        if len(rows) > 1 and len(keys) == 1:
            bad.append((pid, [row['id'] for row in rows]))
    return bad


def display_positions(records):
    """Mirror of the dispLL block in every market page."""
    pts = [r for r in records if r.get('lat') is not None and r.get('lng') is not None]
    parent = list(range(len(pts)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            if abs(pts[i]['lat'] - pts[j]['lat']) > 0.00002 or abs(pts[i]['lng'] - pts[j]['lng']) > 0.00002:
                continue
            if meters(pts[i]['lat'], pts[i]['lng'], pts[j]['lat'], pts[j]['lng']) <= NEAR_M:
                parent[find(j)] = find(i)
    groups = defaultdict(list)
    for i, record in enumerate(pts):
        groups[find(i)].append(record)
    out = {}
    for group in groups.values():
        if len(group) == 1:
            record = group[0]
            out[record['id']] = (float(record['lat']), float(record['lng']))
            continue
        lat = sum(float(r['lat']) for r in group) / len(group)
        lng = sum(float(r['lng']) for r in group) / len(group)
        cos = math.cos(math.radians(lat)) or 1.0
        rad = (SEP_M / M_PER_DEG) / (2 * math.sin(math.pi / len(group)))
        for i, record in enumerate(group):
            ang = 2 * math.pi * i / len(group)
            out[record['id']] = (lat + rad * math.cos(ang), lng + rad * math.sin(ang) / cos)
    ids = list(out)
    for _ in range(6):
        moved = False
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                lat1, lng1 = out[ids[i]]
                lat2, lng2 = out[ids[j]]
                gap = meters(lat1, lng1, lat2, lng2)
                if gap >= NEAR_M:
                    continue
                if gap < 1e-9:
                    out[ids[j]] = (lat2 + NEAR_M / M_PER_DEG, lng2)
                else:
                    scale = (NEAR_M - gap) / gap
                    out[ids[j]] = (lat2 - (lat1 - lat2) * scale, lng2 - (lng1 - lng2) * scale)
                moved = True
        if not moved:
            break
    return out


def stacked_display(records):
    positions = display_positions(records)
    ids = list(positions)
    bad = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            lat1, lng1 = positions[ids[i]]
            lat2, lng2 = positions[ids[j]]
            gap = meters(lat1, lng1, lat2, lng2)
            if gap < NEAR_M:
                bad.append((ids[i], ids[j], gap))
    return bad


def _rank(record):
    ident = str(record['id'])
    score = 100 * len(record.get('permits') or [])
    if record.get('kind') == 'active':
        score += 80
    elif record.get('kind') == 'permit' and not ident.startswith('acq_'):
        score += 40
    if ident.startswith('act_'):
        score += 30
    elif ident.startswith('pmt_'):
        score += 20
    if record.get('product_classification'):
        score += 15
    if record.get('prod') and record.get('prod') != 'Deed Transfer':
        score += 10
    if record.get('ty'):
        score += 5
    return score


def choose_canonical(rows):
    """Prefer the pin that already carries permits, a listing, or a product."""
    def sort_key(record):
        ident = str(record['id'])
        # max() wins: higher rank, then a plain id over a "-2" twin, then the
        # shorter id, then alphabetical so the choice is stable.
        return (_rank(record), not ident.endswith('-2'), -len(ident), tuple(-ord(c) for c in ident))
    return max(rows, key=sort_key)


def _contact_key(person):
    return (person.get('n'), tuple(person.get('p') or []), tuple(person.get('e') or []))


def _union_contacts(current, incoming):
    people = []
    for value in (current, incoming):
        if isinstance(value, list):
            people.extend(person for person in value if isinstance(person, dict))
    seen, out = set(), []
    for person in people:
        key = _contact_key(person)
        if key in seen:
            continue
        seen.add(key)
        out.append(person)
    return out or current


def merge_records(canonical, others):
    """Fold duplicate pins into canonical without dropping their facts."""
    merged = dict(canonical)
    aliases = list(merged.get('listing_alias_ids') or [])
    notes = []
    for other in others:
        if other['id'] not in aliases and other['id'] != canonical['id']:
            aliases.append(other['id'])
        for alias in other.get('listing_alias_ids') or []:
            if alias not in aliases and alias != canonical['id']:
                aliases.append(alias)
        have = {str(permit.get('proj')) for permit in (merged.get('permits') or [])}
        extra = [permit for permit in (other.get('permits') or []) if str(permit.get('proj')) not in have]
        if extra:
            merged['permits'] = list(merged.get('permits') or []) + extra
        for field in ('a', 'llc', 'v', 'sd', 'lot', 'f', 'u', 'prod', 'ty', 'kind', 'bb', 'comp', 'st', 'mls', 'lat', 'lng'):
            if not meaningful(merged.get(field)) and meaningful(other.get(field)):
                merged[field] = other[field]
        if not merged.get('product_classification') and other.get('product_classification'):
            merged['product_classification'] = other['product_classification']
        contacts = _union_contacts(merged.get('c'), other.get('c'))
        if isinstance(contacts, list) and contacts != merged.get('c'):
            merged['c'] = contacts
        bits = [f"id {other['id']}"]
        if meaningful(other.get('llc')) and other.get('llc') != merged.get('llc'):
            bits.append(f"owner {other['llc']}")
        if meaningful(other.get('v')) and other.get('v') != merged.get('v'):
            bits.append(f"assessed {other['v']}")
        if meaningful(other.get('sd')) and other.get('sd') != merged.get('sd'):
            bits.append(f"sale {other['sd']}")
        if meaningful(other.get('lot')) and other.get('lot') != merged.get('lot'):
            bits.append(f"lot {other['lot']}")
        if other.get('lat') is not None and (other.get('lat') != merged.get('lat') or other.get('lng') != merged.get('lng')):
            bits.append(f"at {other['lat']},{other['lng']}")
        if meaningful(other.get('f')) and other.get('f') != merged.get('f'):
            bits.append(str(other['f']))
        notes.append('Merged duplicate pin ' + '; '.join(bits))
    if aliases:
        merged['listing_alias_ids'] = aliases
    return merged, notes


def _append_unique(notes, lines):
    text = notes or ''
    for line in lines:
        line = (line or '').strip()
        if line and line not in text:
            text = (text + '\n' + line).strip()
    return text


def _deed_style(record):
    return record.get('kind') not in ('permit', 'active') and not record.get('permits')


def drop_member(text, name, key):
    """Remove one DATA element or one object member. Missing keys are a no-op."""
    start, end, _container = span(text, name)
    items = _members(text, start, end)
    for index, (identity, left, right) in enumerate(items):
        if identity != key:
            continue
        if index + 1 < len(items):
            return text[:left] + text[items[index + 1][1]:]
        if index == 0:
            return text[:start + 1] + text[right:end] + text[end:]
        return text[:items[index - 1][2]] + text[right:]
    return text


def _members(text, start, end):
    """Identity plus the span that includes an object key, not just its value."""
    from deed_ingest import elements
    raw = elements(text, start, end)
    is_array = text[start] == '['
    bounds = []
    for index, (key, value_start, value_end, value) in enumerate(raw):
        identity = value['id'] if is_array else key
        left = value_start
        if not is_array:
            if index == 0:
                left = start + 1
                while text[left].isspace():
                    left += 1
            else:
                left = raw[index - 1][2]
                while left < value_start and text[left] in ' \t\r\n,':
                    left += 1
        bounds.append((identity, left, value_end))
    return bounds


def _object(text, name):
    try:
        return span(text, name)[2]
    except ValueError:
        return {}


def collapse_market(market):
    """Merge same-address pins inside one loaded market. Returns merge rows."""
    merges = []
    # Snapshot groups first; each pass edits market['data'].
    groups = list(address_groups(market['data']).items())
    reconcile = _object(market['text'], 'RECONCILE')
    watched = set()
    if isinstance(reconcile, dict):
        for value in reconcile.values():
            if isinstance(value, dict):
                watched.update(value)
    for address, rows in groups:
        rows = [row for row in rows if any(row['id'] == current['id'] for current in market['data'])]
        if len(rows) < 2:
            continue
        canonical = choose_canonical(rows)
        others = [row for row in rows if row['id'] != canonical['id']]
        blocked = [row['id'] for row in others if row['id'] in watched]
        if blocked:
            raise ValueError(f"{address}: retired ids are in RECONCILE: {blocked}")
        merged, fact_lines = merge_records(canonical, others)
        seeds = _object(market['text'], 'SEED_POINTS')
        lives = _object(market['text'], 'LIFE')
        pulls = _object(market['text'], 'DEED_PULL')
        seed = dict(seeds.get(canonical['id']) or {'notes': '', 'tags': []})
        tags = list(seed.get('tags') or [])
        extra = list(fact_lines)
        adopted = None
        for other in others:
            other_seed = seeds.get(other['id']) or {}
            for tag in other_seed.get('tags') or []:
                if tag == 'deed' and any(existing in STAGE_TAGS for existing in tags):
                    continue
                if tag not in tags:
                    tags.append(tag)
            extra.extend((other_seed.get('notes') or '').split('\n'))
            life = lives.get(other['id'])
            if not life:
                continue
            note = life.get('note') or ''
            if note:
                extra.append(note)
            if adopted is None and life.get('s') == 'deed' and _deed_style(merged) and canonical['id'] not in lives:
                adopted = {k: life[k] for k in life}
        brought_deed = False
        for other in others:
            other_tags = (seeds.get(other['id']) or {}).get('tags') or []
            if 'deed' in other_tags or (lives.get(other['id']) or {}).get('s') == 'deed':
                brought_deed = True
        if brought_deed and 'deed' not in tags and not any(tag in STAGE_TAGS for tag in tags):
            tags.append('deed')
        seed['notes'] = _append_unique(seed.get('notes'), extra)
        seed['tags'] = tags
        market['text'] = patch(market['text'], 'DATA', canonical['id'], merged)
        market['text'] = patch(market['text'], 'SEED_POINTS', canonical['id'], seed)
        if adopted is not None:
            market['text'] = patch(market['text'], 'LIFE', canonical['id'], adopted)
        if not pulls.get(canonical['id']):
            for other in others:
                if pulls.get(other['id']):
                    market['text'] = patch(market['text'], 'DEED_PULL', canonical['id'], pulls[other['id']])
                    break
        retired = []
        for other in others:
            for container in ('DATA', 'SEED_POINTS', 'LIFE', 'DEED_PULL'):
                market['text'] = drop_member(market['text'], container, other['id'])
            retired.append(other['id'])
        retired_ids = set(retired)
        market['data'] = [merged if row['id'] == canonical['id'] else row
                          for row in market['data'] if row['id'] not in retired_ids]
        merges.append(dict(address=address, canonical=canonical['id'], retired=retired))
    return merges


def audit(records):
    return {
        'addresses': [(key, [row['id'] for row in rows]) for key, rows in sorted(address_groups(records).items())],
        'property_ids': same_address_ids(records),
        'stacked': stacked_display(records),
    }


def unit_token(address):
    """Trailing unit letter, so 711 E 25th A and B stay different homes."""
    text = normalize(address)
    match = re.search(r'\bUNIT\s+([A-Z0-9]+)$', text)
    if match:
        return match.group(1)
    match = re.search(r'\b([A-Z])$', text)
    return match.group(1) if match else None


def cross_market_duplicates(pages):
    """Same property on two market maps.

    pages is (market name, DATA records). A shared DealMachine id is one
    property unless the pins carry distinct unit tokens. The same normalized
    address on two maps is one property even when the ids differ.
    """
    by_pid = defaultdict(list)
    by_addr = defaultdict(list)
    for market, records in pages:
        for record in records:
            address = normalize(record.get('a'))
            if address:
                by_addr[address].append((market, record['id']))
            for pid in property_ids(record):
                by_pid[pid].append((market, record['id'], address, unit_token(record.get('a'))))
    found = []
    for address, rows in sorted(by_addr.items()):
        markets = {market for market, _ in rows}
        if len(markets) > 1:
            found.append(('address', address, rows))
    for pid, rows in sorted(by_pid.items()):
        markets = {market for market, _, _, _ in rows}
        units = {unit for _, _, _, unit in rows}
        if len(markets) < 2:
            continue
        if len(units) > 1 and None not in units:
            continue
        found.append(('property', pid, [(market, ident, address) for market, ident, address, _ in rows]))
    return found


_MIGRATION_NOTE = 'Migrated from Heights page (Timbergrove-side).'


def _find_canonical(records, incoming):
    ids = set(property_ids(incoming))
    address = normalize(incoming.get('a'))
    hits = []
    for record in records:
        if ids & set(property_ids(record)) or (address and normalize(record.get('a')) == address):
            hits.append(record)
    if len(hits) > 1:
        raise ValueError('override destination has more than one pin for ' + incoming.get('a', ''))
    return hits[0] if hits else None


def enforce_market_overrides(markets, overrides):
    """Drop a pin that an override assigns to a different market.

    Unique facts are copied onto the destination pin first. The destination
    must already have that property; this does not invent a pin, and it does
    not delete the only copy.
    """
    foreign = []
    for name, market in markets.items():
        for record in market['data']:
            destination = (overrides or {}).get(normalize(record.get('a')))
            if destination and destination != name:
                foreign.append((name, record, destination))
    moves = []
    for name, record, destination in foreign:
        target = markets[destination]
        canonical = _find_canonical(target['data'], record)
        if canonical is None:
            raise ValueError(
                f"{record['id']} ({record.get('a')}) is on {name}, but {destination} has no pin to keep")
        merged, notes = merge_records(canonical, [record])
        source_seed = _object(markets[name]['text'], 'SEED_POINTS').get(record['id']) or {}
        extra = [line for line in notes if _MIGRATION_NOTE not in line]
        for line in (source_seed.get('notes') or '').split('\n'):
            if line.strip() and _MIGRATION_NOTE not in line:
                extra.append(line.strip())
        seeds = _object(target['text'], 'SEED_POINTS')
        seed = dict(seeds.get(canonical['id']) or {'notes': '', 'tags': []})
        seed['notes'] = _append_unique(seed.get('notes'), extra)
        seed['tags'] = list(seed.get('tags') or [])
        target['text'] = patch(target['text'], 'DATA', canonical['id'], merged)
        target['text'] = patch(target['text'], 'SEED_POINTS', canonical['id'], seed)
        pulls = _object(markets[name]['text'], 'DEED_PULL')
        if pulls.get(record['id']) and not _object(target['text'], 'DEED_PULL').get(canonical['id']):
            target['text'] = patch(target['text'], 'DEED_PULL', canonical['id'], pulls[record['id']])
        for container in ('DATA', 'SEED_POINTS', 'LIFE', 'DEED_PULL'):
            markets[name]['text'] = drop_member(markets[name]['text'], container, record['id'])
        markets[name]['data'] = [row for row in markets[name]['data'] if row['id'] != record['id']]
        target['data'] = [merged if row['id'] == canonical['id'] else row for row in target['data']]
        moves.append(dict(address=normalize(record.get('a')), market=destination,
                          canonical=canonical['id'], retired=record['id'], removed_from=name))
    return moves


# Kept identical in every market page. display_positions() is the Python mirror.
DISP_LL_JS = """// Spread pins that sit on the same point (NEAR_M=0.70m) so radius-6 markers do not coincide. SEP_M=16. Distinct addresses stay separate records.
const dispLL={};{
  const NEAR=0.70/111320, SEP=16/111320;
  const pts=DATA.filter(r=>r.lat!=null&&r.lng!=null);
  const parent=pts.map((_,i)=>i);
  const find=i=>{while(parent[i]!==i)i=parent[i]=parent[parent[i]];return i;};
  const gap=(a,b)=>{const dx=(a.lat-b.lat),dy=(a.lng-b.lng)*Math.cos(a.lat*Math.PI/180);return Math.hypot(dx,dy);};
  for(let i=0;i<pts.length;i++)for(let j=i+1;j<pts.length;j++){
    if(Math.abs(pts[i].lat-pts[j].lat)>0.00002||Math.abs(pts[i].lng-pts[j].lng)>0.00002)continue;
    if(gap(pts[i],pts[j])<=NEAR)parent[find(j)]=find(i);}
  const groups={};
  pts.forEach((r,i)=>{(groups[find(i)]=groups[find(i)]||[]).push(r);});
  for(const k in groups){const a=groups[k];
    if(a.length<2){dispLL[a[0].id]=[a[0].lat,a[0].lng];continue;}
    const lat=a.reduce((s,r)=>s+r.lat,0)/a.length, lng=a.reduce((s,r)=>s+r.lng,0)/a.length;
    const cl=Math.cos(lat*Math.PI/180)||1, rad=SEP/(2*Math.sin(Math.PI/a.length));
    a.forEach((r,i)=>{const ang=2*Math.PI*i/a.length;dispLL[r.id]=[lat+rad*Math.cos(ang),lng+rad*Math.sin(ang)/cl];});}
  const ids=Object.keys(dispLL);
  for(let n=0;n<6;n++){let moved=false;
    for(let i=0;i<ids.length;i++)for(let j=i+1;j<ids.length;j++){
      const A=dispLL[ids[i]], B=dispLL[ids[j]];
      const dx=(A[0]-B[0]), dy=(A[1]-B[1])*Math.cos(A[0]*Math.PI/180), d=Math.hypot(dx,dy);
      if(d>=NEAR)continue;
      if(d<1e-9)B[0]+=NEAR; else {const s=(NEAR-d)/d; B[0]-=dx*s; B[1]-=(A[1]-B[1])*s;}
      moved=true;}
    if(!moved)break;}}"""

