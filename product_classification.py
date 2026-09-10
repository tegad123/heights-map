"""Shared v9 product decisions and conservative, provenance-bearing ingest policy.

legacy_rows/legacy_label preserve the review tool exactly. classify() is the
production guard: insufficient evidence never becomes a confident stored label.
"""
import csv, re, sys
from functools import lru_cache
from collections import defaultdict
from pathlib import Path
ORIG=["HOUSTON HEIGHTS","SUNSET HEIGHTS","SHADY ACRES","STUDES","WOODLAND TERRACE",
 "WEST HEIGHTS","MILROY PLACE","WOODSON PLACE","GOSTICK","QUENSELL LAWN",
 "BARTHOLOMEW PLACE","HARDING HEIGHTS","WOODLAND HEIGHTS","NORHILL","BROOKE SMITH",
 "RIDGEWOOD","INDEPENDENCE HEIGHTS","J AUSTIN","USENER","BOVA","SHADYWOOD","MILROY","WOODSON"]
RP=re.compile(r'\bR/P\b|\bREPLAT\b',re.I)
TOK=re.compile(r'[\s&,]*(?:(THRU|THROUGH|-)\s*)?(\d+[A-Z]?|[A-Z])(?=[\s&,]|$)')
PFX=re.compile(r'\b(LTS?|TRS?)\s+')
UNI=re.compile(r'\b(?:unit\s*#?\s*)?([a-f])\b\s*$',re.I)
DIRS={"west":"w","east":"e","north":"n","south":"s"}
SFX=re.compile(r'\b(street|st|ave|avenue|dr|drive|rd|road|ln|lane|blvd|way|ct|pl)\b\.?',re.I)
FULL_DEPTH=100
def pa(a):
    s=(a or "").split(",")[0].strip().lower(); s=re.sub(r'\bunit\s*#\s*','unit ',s)
    m=re.match(r'^(\d+)\s+(.*)$',s)
    if not m: return None,"",""
    n,rest=int(m.group(1)),m.group(2); u=""
    um=UNI.search(rest)
    if um: u=um.group(1).upper(); rest=rest[:um.start()].strip()
    return n," ".join(DIRS.get(t,t) for t in SFX.sub(" ",rest).split()).strip(),u
def sub_name(l):
    up=" ".join((l or "").upper().split())
    m=re.search(r'\bBLK\s+\S+\s+(.*)$',up)
    if m: return m.group(1).strip()
    m=re.match(r'^(?:LTS?|TRS?|RES)\s+[\dA-Z\s&,]*?\s+([A-Z].*)$',up)
    return m.group(1).strip() if m else up
def counts(l):
    up=" ".join((l or "").upper().split()); w=p=0
    for pm in PFX.finditer(up):
        isl=pm.group(1).startswith("LT"); pos=pm.end(); prev=None
        while True:
            m=TOK.match(up,pos)
            if not m: break
            rng,tok=m.group(1),m.group(2)
            tk=[str(n) for n in range(prev+1,int(tok)+1)] if (rng and prev is not None and tok.isdigit()) else [tok]
            for t in tk:
                if t.isdigit():
                    if isl: w+=1
                    else: p+=1
                else: p+=1
            prev=int(tok) if tok.isdigit() else None; pos=m.end()
    return w,p
def family(legal):
    if not legal: return None,"no legal"
    up=legal.upper()
    if re.search(r'\bRES\s+[A-Z]\b',up): return "Split","reserve/replat"
    sd=sub_name(legal)
    if not(any(sd.startswith(x) for x in ORIG) and not RP.search(up)): return "Split","replat child"
    w,p=counts(legal)
    # An HCAD legal spanning 2+ WHOLE original lots means the parcel was
    # ASSEMBLED, not subdivided: Heights/Sunset Heights plat lots are ~25 ft,
    # so "LTS 6 & 7 BLK 40" is one 50 ft lot carrying one house. This rule used
    # to return Split and mislabelled 13 full-lot builds (614/629 E 26th among
    # them). Verified against the HCAD parcel diff (refresh/parcel_diff.py):
    # all 13 parcels are geometrically unchanged across 2024/2025/2026.
    # Route to review and let unit-count / geometry signals decide instead.
    if w>=2: return "Review",f"assembled {w} lots -> needs_review"
    if w==1 and p: return "Split","lot + fragment"
    if w==1: return "Single","one whole lot"
    if p: return "Split","fragment only"
    return None,"unparsed"

def legacy_label(fam, units, ms, depth):
    if fam is None and units<2: lab=""
    elif fam=="Review" and units<2: lab=""   # assembled lots != subdivision
    elif units>=3 or (ms and ms>=3): lab="Common Driveway"
    elif units==2 or ms==2:
        lab="Common Driveway" if (depth is not None and depth<FULL_DEPTH) else "Split Lot"
    elif fam=="Split":
        lab="Common Driveway" if (depth is not None and depth<FULL_DEPTH) else "Split Lot"
    else: lab="Single Lot"
    return lab

def legacy_rows(rows):
    P={}; bynum=defaultdict(set); bystreet=defaultdict(set)
    for i,r in enumerate(rows,2):
        n,st,u=pa(r.get("address")); P[i]=(n,st,u)
        if n is not None: bynum[(st,n)].add(u or "_"); bystreet[st].add(n)
    chains={}
    for st,ns in bystreet.items():
        used={}
        for n in sorted(ns):
            grp=[n]; m=n
            while m+2 in ns and (m+2)%2==n%2: m+=2; grp.append(m)
            for g in grp: used.setdefault(g,set()).update(grp)
        chains[st]=used
    fn=list(rows[0].keys())
    for c in ["v9_label","v9_why","v9_units"]:
        if c not in fn: fn.append(c)
    tal=defaultdict(int)
    for i,r in enumerate(rows,2):
        n,st,u=P[i]
        units = max(len(bynum[(st,n)]), len(chains.get(st,{}).get(n,{n}))) if n is not None else 1
        try: ms=int(str(r.get("ms_of") or "").strip())
        except: ms=None
        try: depth=float(r.get("depth_ft"))
        except: depth=None
        fam,why=family(r.get("legal_desc"))
        lab=legacy_label(fam, units, ms, depth)
        r["v9_label"]=lab; r["v9_why"]=f"{why} | units={units}"; r["v9_units"]=units
        tal[lab or "undecided"]+=1
    return rows, fn, tal


def parcel_evidence(feature, source='HCAD exact-address parcel'):
    """Measure an unambiguous single polygon in EPSG:2278 US survey feet.

Multiple exterior rings, invalid shapes and missing dependencies fail closed.
The longest side of the minimum rotated rectangle is v9's parcel depth proxy.
No area threshold is used to assign a product.
"""
    import math
    attrs = feature.get('attributes', {})
    evidence = dict(source=source, account=attrs.get('HCAD_NUM'),
                    matched=attrs.get('address'), legal=attrs.get('legal_lines') or '',
                    depth_ft=None)
    rings = feature.get('geometry', {}).get('rings') or []
    try:
        from shapely.geometry import Polygon
        from shapely.ops import transform
        from pyproj import Transformer
        if not rings:
            raise ValueError('missing parcel rings')
        pieces = sorted((Polygon(r) for r in rings), key=lambda p: p.area, reverse=True)
        outer = pieces[0]
        if not outer.is_valid or any(not outer.contains(p) for p in pieces[1:]):
            raise ValueError('invalid or multipart parcel')
        polygon = Polygon(outer.exterior.coords,
                          [p.exterior.coords for p in pieces[1:]])
        if not polygon.is_valid:
            raise ValueError('invalid parcel holes')
        # Explicitly reject a response in a different spatial reference.
        if not (-96 < polygon.bounds[0] < -94 and 28 < polygon.bounds[1] < 31):
            raise ValueError('geometry is not Houston WGS84')
        project = Transformer.from_crs('EPSG:4326', 'EPSG:2278', always_xy=True)
        shape = transform(project.transform, polygon)
        corners = list(shape.minimum_rotated_rectangle.exterior.coords)
        sides = [math.hypot(b[0]-a[0], b[1]-a[1]) for a,b in zip(corners,corners[1:])]
        depth, width = max(sides), min(sides)
        if not all(math.isfinite(v) and v > 0 for v in (depth,width,shape.area)):
            raise ValueError('invalid parcel dimensions')
        evidence.update(depth_ft=round(depth, 4), width_ft=round(width,4),
                        area_sf=round(shape.area,2), geometry_crs='EPSG:2278',
                        depth_method='minimum rotated rectangle, longest side')
    except Exception as exc:  # Geometry failure must not abort an otherwise valid permit.

        evidence['geometry_error'] = str(exc)
    evidence['parcel_history'] = parcel_history(evidence.get('account'))
    return evidence


@lru_cache(maxsize=1)
def _parcel_events(source):
    import json
    return json.loads(Path(source).read_text())


def parcel_history(account):
    import json
    source = Path(__file__).resolve().parent / 'refresh/parcel_events.json'
    if not source.exists() or not account:
        return []
    events = _parcel_events(str(source))
    return [dict(event=e['event'], vintage=e['vintage'],
                 parents=e['parent_accts'], children=e['child_accts'],
                 source='refresh/parcel_events.json')
            for e in events if account in e['child_accts']]


def classify(legal='', units=1, master_size=None, parcel=None, hold=None,
             unit_source='one address', master_source='none', observed_split_override=False):
    """Return an auditable decision. Only high-confidence labels are applied.

The ordering of legacy guards is intentional (including Review/None before
master size). Street-number adjacency alone is NOT verified unit evidence.
"""
    import math
    parcel = parcel or {}
    depth = parcel.get('depth_ft')
    if depth is not None and (not math.isfinite(depth) or depth <= 0):
        depth = None
    # HCAD joins legal-description lines with |; review CSVs use spaces.
    legal = (legal or '').replace('|', ' ')
    fam, why = family(legal)
    candidate = legacy_label(fam, units, master_size, depth)
    topology = sorted((e for e in parcel.get('parcel_history', [])
                       if e['event'] in ('SPLIT', 'ASSEMBLY')), key=lambda e:e['vintage'])
    proven_split = bool(topology and topology[-1]['event'] == 'SPLIT')
    detail = (f'{why}; units={units} ({unit_source}); master_size={master_size} '
              f'({master_source}); depth_ft={depth}; geometry={parcel.get("source", "unavailable")}; '
              f'parcel={parcel.get("account", "unavailable")}; '
              f'parcel_history={topology[-1] if topology else "none"}')
    code = None
    if hold:
        code = 'HELD_TRIAGE'
        detail = str(hold) + '; ' + detail
    elif not candidate:
        code = 'ASSEMBLED_REVIEW' if fam == 'Review' else 'LEGAL_UNAVAILABLE'
    elif not parcel.get('account') or depth is None:
        # Missing depth is acceptable only when verified multi-unit evidence
        # settles Common Driveway; legal None/Review guards still apply.
        if not (candidate == 'Common Driveway' and (units >= 3 or (master_size or 0) >= 3)):
            code = 'DEPTH_UNAVAILABLE'
    if code is None and parcel.get('geometry_error'):
        code = 'GEOMETRY_INVALID'
    # A non-original subdivision name is not proof that a suburban full lot
    # was subdivided. v9 was written for Heights' named original plats.
    if code is None and why == 'replat child' and not RP.search(legal or '') and units < 2 and not master_size and not proven_split:
        code = 'UNVERIFIED_PLAT'
    split_override = False
    if code is None and candidate == 'Single Lot' and proven_split:
        if observed_split_override and depth > FULL_DEPTH + 0.01:
            candidate = 'Split Lot'
            split_override = True
            detail += '; observed child-producing SPLIT overrides original-plat lot count'
        else:
            code = 'PARCEL_HISTORY_CONFLICT'
    # Near the decision boundary, projection/coordinate quantization must not
    # choose between development forms. Exact legacy semantics remain above.
    depth_decides = units < 3 and (master_size or 0) < 3 and (units == 2 or master_size == 2 or fam == 'Split')
    if code is None and depth_decides and parcel.get('depth_method') and abs(depth - FULL_DEPTH) <= 0.01:
        code = 'DEPTH_BOUNDARY_UNCERTAIN'
        detail += '; measured depth within 0.01 ft of 100-ft boundary'
    if code is None and candidate == 'Single Lot' and units != 1:
        code = 'CONFLICTING_UNITS'
    return dict(product='Unknown' if code else candidate,
                confidence='unknown' if code else 'high',
                reason_code=code or ('OBSERVED_PARCEL_SPLIT' if split_override else 'V9_VERIFIED'), reason=detail,
                candidate=candidate or 'Unknown', version='v9-ingest-1',
                evidence=dict(parcel=parcel, units=units, master_size=master_size,
                              unit_source=unit_source, master_source=master_source, family=fam))


def context_signals(rows):
    """Use explicit address letters and permit master references, not adjacency."""
    import re
    from permit_pull import _norm_ret
    by_unit = defaultdict(set)
    masters, refs = {}, {}
    for r in rows:
        address = _norm_ret(r.get('a','').split(',')[0])
        # The geocoder already normalizes G/H and fractional streets.
        unit = re.fullmatch(r'(.+\b(?:ST|DR|RD|LN|AVE|CT|PL|WAY|BLVD))\s+([A-Z])', address)
        if unit:
            by_unit[unit[1]].add(unit[2])
        desc = ' | '.join(p.get('desc','') for p in r.get('permits',[]))
        sizes = [int(n) for n in re.findall(r'\bM(?:ST)?\s+OF\s+(\d+)',desc,re.I)]
        refs[r['id']] = re.findall(r'\bM\s*#\s*(\d{7,9})',desc,re.I)
        for p in r.get('permits',[]):
            proj = str(p.get('proj',''))
            if sizes:
                masters[proj] = max(sizes)
    result = {}
    for r in rows:
        address = _norm_ret(r.get('a','').split(',')[0])
        unit = re.fullmatch(r'(.+\b(?:ST|DR|RD|LN|AVE|CT|PL|WAY|BLVD))\s+([A-Z])',address)
        units = len(by_unit[unit[1]]) if unit else 1
        projects = [str(p.get('proj','')) for p in r.get('permits',[])]
        related = projects + refs[r['id']]
        sizes = [masters[p] for p in related if p in masters]
        master_size = max(sizes) if sizes else None
        result[r['id']] = dict(units=max(1,units), master_size=master_size,
                              unit_source='distinct address unit letters' if unit else 'one address',
                              master_source=','.join(p for p in related if p in masters) or 'none')
    return result


def stored_product(row):
    if row.get('prod') in ('Single Lot','Split Lot','Common Driveway'):
        return row['prod']
    return {'active_single':'Single Lot','active_split':'Split Lot'}.get(row.get('ty'))


def record_fields(decision):
    return {'prod': decision['product'], 'product_classification': decision}


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Exact v9 review CSV compatibility runner')
    parser.add_argument('csv')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    with open(args.csv, newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    rows, fields, tally = legacy_rows(rows)
    with open(args.out, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(dict(tally))


if __name__ == '__main__':
    main()
