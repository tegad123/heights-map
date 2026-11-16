#!/usr/bin/env python3
"""Merge a status-bearing HAR export; dry run by default. DATA is never rewritten."""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
import market_status_ingest as legacy
from market_address import address_key
from market_linkage import Matcher, resolve
from deed_ingest import span, encode, in_boundary
from sold_classification import classify_lot
from sold_ingest import money, parse_close, metrics_for

ROOT = Path(__file__).resolve().parent
STATUS = {'Sold':'sold', 'Active':'active', 'Pending':'pending', 'Terminated':'terminated',
          'Expired':'terminated', 'Withdrawn':'terminated', 'Terminated-Relisted':'terminated'}


def load(path, html, as_of):
    payload=path.read_bytes(); digest=hashlib.sha256(payload).hexdigest()
    reader=csv.DictReader(payload.decode('utf-8-sig').splitlines())
    rawrows=list(reader)
    if not rawrows: raise ValueError('Empty export')
    zone=re.compile(re.search(r'const OUT_OF_ZONE=/(.*?)/i;',html)[1],re.I)
    boundary=json.loads((ROOT/'heights_boundary.geojson').read_text())
    records=[]; ledger=[]; seen=set()
    for line,raw in enumerate(rawrows,2):
        status=STATUS[raw['Status'].strip()]; mls=raw['MLS Number'].strip(); address=raw['Address'].strip()
        lat,lng=money(raw['Latitude']),money(raw['Longitude']); lot=money(raw['Lot Size'])
        close=parse_close(raw['Close Date']); reason=None
        if not mls or not address or lat is None or lng is None: raise ValueError(f'Invalid identity at {line}')
        if status=='sold' and (not close or close>date.fromisoformat(as_of) or not money(raw['Close Price'])): raise ValueError(f'Invalid close at {line}')
        if status!='sold' and close: raise ValueError(f'Unexpected close at {line}')
        if mls in seen: reason='DUP_INPUT_MLS'
        elif zone.search(address): reason='OOZ_REGEX'
        elif lng>-95.370: reason='OOZ_EAST'
        elif not in_boundary(boundary,lng,lat): reason='OOZ_POLY'
        seen.add(mls)
        ask=money(raw.get('List Price'))
        if ask is None: ask=money(raw.get('Current Price'))
        rec=dict(mls=mls,status=status,har_status=raw['Status'].strip(),address=address,address_key=address_key(address),
                 original_list_price=money(raw['Original List Price']),current_list_price=ask,close_price=money(raw['Close Price']),
                 close_date=close.isoformat() if close else None,dom=money(raw['DOM']),lot_sqft=lot,product=classify_lot(lot),
                 builder=raw['Builder Name'],year_built=money(raw['Year Built']),building_sqft=money(raw['Building SqFt']),lat=lat,lng=lng,
                 agents={k:v for k,v in raw.items() if any(s in k for s in ('Agent','Office','Team'))},as_of=as_of,
                 source_file=path.name,source_row=line,source_sha256=digest,exclusion=reason,raw=raw)
        records.append(rec)
        if reason: ledger.append(dict(FILE=path.name,SHA256=digest,ROW=line,MLS=mls,ADDRESS=address,REASON=reason,RAW_JSON=json.dumps(raw,sort_keys=True)))
    closes=[r['close_date'] for r in records if r['close_date']]
    return records,ledger,dict(
        rows=len(rawrows),
        columns=len(reader.fieldnames),
        statuses=dict(Counter(r['Status'] for r in rawrows)),
        unique_mls=len(seen),
        lot_products=dict(Counter(r['product'] for r in records)),
        close_min=min(closes,default=None),
        close_max=max(closes,default=None))


def load_many(paths, html, as_of):
    paths=[Path(p) for p in paths]
    if not paths or len({p.resolve() for p in paths})!=len(paths):
        raise ValueError('Provide nonempty, distinct input paths')
    incoming=[]; ledger=[]; profiles=[]; seen={}
    for path in paths:
        records,dropped,profile=load(path,html,as_of)
        profiles.append(dict(file=str(path),**profile))
        for rec in records:
            if rec['mls'] in seen and seen[rec['mls']]!=path:
                raise ValueError(
                    'Cross-file MLS collision '+rec['mls']+
                    ': '+str(seen[rec['mls']])+' / '+str(path))
            seen[rec['mls']]=path
        incoming.extend(records)
        ledger.extend(dropped)
    return incoming,ledger,dict(
        files=profiles,rows=len(incoming),unique_mls=len(seen))


def snapshot(records, sold, source, runtime, as_of):
    matcher=Matcher(source,runtime); groups=defaultdict(list); conflicts=[]
    for rec in records:
        link=matcher.match(rec)
        if link['issue']: conflicts.append(dict(mls=rec['mls'],address=rec['address'],**link))
        groups[link['member'] or 'address:'+address_key(rec['address'])].append({k:v for k,v in rec.items() if k not in ('raw','agents')})
    properties={k:resolve(v) for k,v in sorted(groups.items())}
    archive=defaultdict(list)
    for sale in sold: archive[address_key(sale['a'])].append(sale)
    phases={r['id']:r for r in runtime['rows']}; tracked=[]
    for member_id,(pin_id,member) in matcher.members.items():
        prop=properties.get(member_id); history=sorted(archive[address_key(member['a'])],key=lambda s:s['cd'],reverse=True)
        new_build=[s for s in history if (s.get('yb') or 0)>=2025]
        tracked.append(dict(member=member_id,pin=pin_id,address=member['a'],phase=phases[pin_id]['phase'],
                            product=prop['current']['product'] if prop else member.get('prod') or 'Unknown',
                            status=prop['status'] if prop else 'sold' if new_build else 'no_record',current=prop['current'] if prop else None,
                            history=prop['history'] if prop else [],historical_sales=history,archive_current=new_build[0] if new_build and not prop else None,
                            ordering_issue=prop['ordering_issue'] if prop else None,category=runtime['points'].get(pin_id,{}).get('classification',{}).get('category'),
                            in_supply=pin_id in runtime['supplyIds']))
    return dict(as_of=as_of,price_basis='Original List Price',records=records,properties=properties,tracked=tracked,
                complete=[r for r in tracked if r['phase']=='complete' and not r['category']],
                coverage=dict(source_rows=len(records),linked=sum(k in matcher.members for k in properties)),conflicts=conflicts)


def run(args):
    html=(ROOT/'index.html').read_text(); old=json.loads((ROOT/'heights_market_status.data.json').read_text())
    runtime=json.loads(Path(args.runtime).read_text())['index']; source=span(html,'DATA')[2]; sale_store='SOLD_EVIDENCE' if 'const SOLD_EVIDENCE=' in html else 'SOLD_DATA'; sold=span(html,sale_store)[2]
    incoming,ledger,profile=load_many(
        [args.input] if isinstance(args.input,(str,Path)) else args.input,
        html,args.as_of)
    from sold_classification import MIN_YEAR_BUILT, lot_floor_reason
    from active_ingest import market_key, other_market_keys
    def blank_contact(raw):
        return {k: ('' if any(s in k.lower() for s in ('agent','team','owner','phone','email')) else v) for k,v in raw.items()}
    elsewhere=other_market_keys()
    for rec in incoming:
        if rec['exclusion']:
            continue
        if rec['year_built'] is None or rec['year_built']<MIN_YEAR_BUILT:
            rec['exclusion']='YEAR_BEFORE_MIN'
        else:
            floor=lot_floor_reason(rec['raw'].get('Lot Size'))
            if floor:
                rec['exclusion']=floor
            elif market_key(rec['address']) in elsewhere:
                rec['exclusion']='ALREADY_ON_OTHER_MARKET'
        rec['raw']=blank_contact(rec['raw'])
        rec['agents']={}
        if rec['exclusion']:
            ledger.append(dict(FILE=rec['source_file'],SHA256=rec['source_sha256'],ROW=rec['source_row'],MLS=rec['mls'],ADDRESS=rec['address'],REASON=rec['exclusion'],RAW_JSON=json.dumps(rec['raw'],sort_keys=True)))
    records={r['mls']:r for r in old['records']}; counts=Counter(); actions=[]; address_corrections=[]
    for rec in incoming:
        prior=records.get(rec['mls'])
        if prior and address_key(prior['address'])!=rec['address_key']:
            old_tokens=Counter(address_key(prior['address']).split())
            new_tokens=Counter(rec['address_key'].split())
            diff=(old_tokens-new_tokens)+(new_tokens-old_tokens)
            extra=list(diff)
            # Same MLS, same house number and street, one unit letter added or removed.
            if not (sum(diff.values())==1 and len(extra)==1 and len(extra[0])==1 and extra[0] in 'abcdef'):
                raise ValueError('MLS address conflict '+rec['mls'])
            address_corrections.append(dict(mls=rec['mls'], before=prior['address'], after=rec['address']))
        if rec['exclusion']: action='ledgered'
        elif prior==rec: action='held'
        else:
            action='updated' if prior else 'new'; records[rec['mls']]=rec
        counts[action]+=1; actions.append(dict(mls=rec['mls'],address=rec['address'],action=action,reason=rec['exclusion']))
    legacy.AS_OF=args.as_of
    # Retain historical resale facts as evidence only; the dedicated comp refresh owns displayed comps.
    retained_evidence={r['id']:r for r in sold if r.get('coh')=='resale'}
    sales_input=[r for r in incoming if 's'+r['mls'] not in retained_evidence and not any(address_key(s['a'])==r['address_key'] and s['cd']==r['close_date'] for s in retained_evidence.values())]
    # Cleanup refreshes may retain unmatched sales as evidence without new comps.
    policy=getattr(args,'sale_policy','all'); deferred_sales=[]
    if policy!='all':
        matcher=Matcher(source,runtime)
        kept=[]
        for rec in sales_input:
            existing=any(s['id']=='s'+rec['mls'] or (address_key(s['a'])==rec['address_key'] and s['cd']==rec['close_date']) for s in sold)
            linked=matcher.match(rec)['member'] in matcher.members
            if rec['status']!='sold' or rec['exclusion'] or existing or linked:kept.append(rec)
            else:deferred_sales.append(dict(mls=rec['mls'],address=rec['address'],reason='COMP_NOT_ADDED_POLICY',detail='Retained as market evidence; no new comp under '+policy,raw=rec['raw']))
        sales_input=kept
    merged,sale_report=legacy.merge_sales(sold,sales_input)
    if sale_report['conflicts']: raise ValueError(sale_report['conflicts'])
    assert all(next(s for s in merged if s['id']==k)==v for k,v in retained_evidence.items())
    snap=snapshot([records[k] for k in sorted(records)],merged,source,runtime,args.as_of)
    snap['refresh_scope']=('Active and sold exports as of '+args.as_of+'. Year built 2025 or later; lots under 2,200 sqft and blank lots are dropped. Missing records retain prior observations and are not automatically retired. Addresses already pinned on another market are not added.')
    fixture=snap['properties']['act_715-merrill']; assert fixture['status']=='active' and any(r['mls']=='50361472' for r in fixture['history'])
    candidate=html
    for name,value in ([(sale_store,merged)] if sale_store=='SOLD_EVIDENCE' else [('SOLD_DATA',merged),('SOLD_METRICS',metrics_for(merged,date.fromisoformat(args.as_of)))]):
        a,z,prior=span(candidate,name)
        if prior!=value: candidate=candidate[:a]+encode(value)+candidate[z:]
    for name in ('DATA','RECONCILE'):
        a,z,_=span(html,name); b,y,_=span(candidate,name); assert html[a:z]==candidate[b:y]
    for row in ledger:
        raw=json.loads(row['RAW_JSON'])
        row['RAW_JSON']=json.dumps({k: ('' if any(s in k.lower() for s in ('agent','team','owner','phone','email')) else v) for k,v in raw.items()}, sort_keys=True)
    outputs={ROOT/'index.html':candidate,ROOT/'heights_market_status.data.json':legacy.jsontxt(snap),
             ROOT/f'pulls/dropped_combined_market_{args.as_of}.csv':legacy.csvtxt(ledger,['FILE','SHA256','ROW','MLS','ADDRESS','REASON','RAW_JSON'])}
    changed=[str(p.relative_to(ROOT)) for p,t in outputs.items() if not p.exists() or p.read_text()!=t]
    before={address_key(p['current']['address']):p['status'] for p in old['properties'].values()}
    multi={address_key(r['address']) for r in incoming if sum(address_key(s['address'])==address_key(r['address']) for s in incoming)>1}
    changes=[dict(address=p['current']['address'],before=before.get(address_key(p['current']['address'])),after=p['status']) for p in snap['properties'].values() if address_key(p['current']['address']) in multi and before.get(address_key(p['current']['address']))!=p['status']]
    report=dict(sale_policy=policy,deferred_sales=deferred_sales,profile=profile,counts=dict(counts),exclusions=dict(Counter(r['REASON'] for r in ledger)),sold_before=len(sold),sold_after=len(merged),resale_evidence_preserved=len(retained_evidence),sales=sale_report,market_records=len(records),normalized_multilisting=len(multi),multilisting_status_changes=changes,address_corrections=address_corrections,finished=dict(Counter(r['status'] for r in snap['complete'])),changed_files=changed,actions=actions)
    if args.output:
        out=Path(args.output); out.mkdir(parents=True,exist_ok=True); (out/'report.json').write_text(legacy.jsontxt(report))
    if args.apply:
        for p,t in outputs.items():
            if str(p.relative_to(ROOT)) in changed:
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text(t)
    print(legacy.jsontxt({k:v for k,v in report.items() if k not in ('actions','multilisting_status_changes','sales','deferred_sales')}))
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',nargs='+',required=True)
    ap.add_argument('--runtime',required=True)
    ap.add_argument('--as-of',required=True)
    ap.add_argument('--output')
    ap.add_argument('--apply',action='store_true')
    ap.add_argument('--sale-policy',choices=['all','tracked'],default='all')
    run(ap.parse_args())
