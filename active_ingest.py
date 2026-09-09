#!/usr/bin/env python3
"""HAR active snapshot, independent of hand-authored DATA. Dry run by default.
Original List Price is not current asking price. Missing exports never imply sold.
"""
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter
from pathlib import Path
from sold_ingest import money
from sold_classification import classify_lot
from deed_ingest import in_boundary

ROOT = Path(__file__).resolve().parent
INPUTS = [('heights_active_single_lots0908.csv', 'Single Lot'),
          ('heights_active_split_lots0908.csv', 'Split Lot')]


def address_key(address):
    """Keep unit/fraction identity; canonicalize directional placement on numbered streets."""
    s = str(address).lower().split(',')[0]
    s = re.sub(r'\b(?:houston|tx|texas|77\d{3})\b.*', '', s)
    s = re.sub(r'\b(?:unit|apt)\s*#?\s*|#', ' ', s)
    s = re.sub(r'(?<=\d)-?([a-f])\b', r' \1', s)
    s = re.sub(r'\b(\d+)\s+(st|nd|rd|th)\b', r'\1\2', s)
    s = re.sub(r'[^a-z0-9/ ]', ' ', s)
    aliases = dict(street='st',avenue='ave',lane='ln',drive='dr',road='rd',court='ct',place='pl',boulevard='blvd',east='e',west='w',north='n',south='s')
    w = [aliases.get(x,x) for x in s.split()]
    if len(w)>2 and w[0].isdigit() and w[1] in 'abcdef' and len(w[1])==1 and w[1] not in ('e','w'):
        w.append(w.pop(1))
    if len(w)>3 and w[1] in ('e','w','n','s') and re.match(r'^\d',w[2]):
        w.append(w.pop(1))
    w = [x for i,x in enumerate(w) if not (i and x == w[i-1] and x in ('st','ave','ln','dr','rd','ct','pl','blvd'))]
    return ' '.join(w)


def run(as_of, apply=False):
    html=(ROOT/'index.html').read_text()
    zone=re.compile(re.search(r'const OUT_OF_ZONE=/(.*?)/i;',html).group(1),re.I)
    geo=json.loads((ROOT/'heights_boundary.geojson').read_text())
    path=ROOT/'heights_active.data.json'
    old=json.loads(path.read_text()) if path.exists() else {'listings':[]}
    existing={r['mls']:r for r in old['listings']}
    listings=[];ledger=[];summaries=[];seen=set();seen_addresses=set();mismatches=[]
    for name,expected in INPUTS:
        payload=(ROOT/name).read_bytes();digest=hashlib.sha256(payload).hexdigest()
        reader=csv.DictReader(io.StringIO(payload.decode('utf-8-sig')))
        required={'MLS Number','Address','Latitude','Longitude','Lot Size','DOM','Original List Price','Year Built','Builder Name','List Agent Full Name','Close Price','Close Date'}
        if not required.issubset(reader.fieldnames or []):raise ValueError('Missing columns: '+name)
        rows=list(reader)
        if not rows:raise ValueError('Empty export: '+name)
        summary=dict(file=name,read=len(rows),added=0,updated=0,unchanged=0,excluded=Counter(),classification_matches=0)
        for line,row in enumerate(rows,2):
            mls=(row.get('MLS Number') or '').strip();a=(row.get('Address') or '').strip()
            lot=money(row.get('Lot Size'));prod=classify_lot(lot)
            if prod==expected:summary['classification_matches']+=1
            else:mismatches.append(dict(file=name,row=line,address=a,derived=prod,expected=expected))
            lat=money(row.get('Latitude'));lng=money(row.get('Longitude'));price=money(row.get('Original List Price'));dom=money(row.get('DOM'));yb=money(row.get('Year Built'))
            reason=None;k=address_key(a)
            if not mls or not a or any(v is None for v in (lot,price,dom,yb)) or lot<=0 or price<=0 or dom<0:reason='INVALID_REQUIRED_FIELD'
            elif row.get('Close Price') or row.get('Close Date'):reason='NOT_ACTIVE_EXPORT'
            elif lat is None or lng is None or not (-90<=lat<=90 and -180<=lng<=180):reason='INVALID_COORDINATES'
            elif zone.search(a):reason='OOZ_REGEX'
            elif lng> -95.370:reason='OOZ_EAST'
            elif not in_boundary(geo,lng,lat):reason='OOZ_POLY'
            elif prod!=expected:reason='CLASSIFICATION_MISMATCH'
            elif mls in seen or k in seen_addresses:reason='DUP_INPUT'
            if reason:
                summary['excluded'][reason]+=1
                ledger.append(dict(FILE=name,SHA256=digest,ROW=line,MLS=mls,ADDRESS=a,REASON=reason,RAW_JSON=json.dumps(row,sort_keys=True)))
                continue
            seen.add(mls);seen_addresses.add(k)
            r=dict(mls=mls,address=a,address_key=k,original_list_price=price,dom=dom,lot_sqft=lot,product=prod,builder=row['Builder Name'].strip(),list_agent=row['List Agent Full Name'].strip(),year_built=yb,lat=lat,lng=lng,status='active',as_of=as_of,source_file=name,source_row=line,source_sha256=digest)
            prior=existing.get(mls)
            summary['unchanged' if prior==r else 'updated' if prior else 'added']+=1
            listings.append(r)
        summaries.append(summary)
    result=dict(as_of=as_of,scope='Two supplied HAR exports; absence is not proof of off-market status. Price is Original List Price, not verified current asking price.',listings=sorted(listings,key=lambda r:r['mls']))
    contents=json.dumps(result,indent=2,ensure_ascii=True)+'\n'
    buf=io.StringIO(newline='');writer=csv.DictWriter(buf,fieldnames=['FILE','SHA256','ROW','MLS','ADDRESS','REASON','RAW_JSON'],lineterminator='\n');writer.writeheader();writer.writerows(ledger)
    ledger_path=ROOT/'pulls'/('dropped_active_'+as_of+'.csv')
    outputs={path:contents,ledger_path:buf.getvalue()}
    changed=[str(p.relative_to(ROOT)) for p,s in outputs.items() if not p.exists() or p.read_text()!=s]
    report=dict(files=summaries,total=len(listings),crosscheck_mismatches=mismatches,ledger_rows=len(ledger),changed_files=changed)
    print(json.dumps(report,indent=2))
    if mismatches:raise ValueError('Classification mismatch; refusing apply')
    if apply:
        for p,s in outputs.items():
            if not p.exists() or p.read_text()!=s:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
    return report


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--as-of',default='2026-09-08');ap.add_argument('--apply',action='store_true');args=ap.parse_args();run(args.as_of,args.apply)
