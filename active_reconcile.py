#!/usr/bin/env python3
"""Read captured runtime state and produce an audit. Never changes map statuses."""
import argparse,csv,io,json
from collections import defaultdict,Counter
from pathlib import Path
from active_ingest import ROOT,INPUTS,address_key
from deed_ingest import span


def run(baseline, output):
    b=json.loads(Path(baseline).read_text());html=(ROOT/'index.html').read_text();raw=span(html,'DATA')[2]
    rawids={r['id']:r for r in raw};sold=defaultdict(list);sources=defaultdict(list)
    for s in b['sold']:sold[address_key(s['a'])].append(s)
    for f,_ in INPUTS:
        for a in csv.DictReader((ROOT/f).open(encoding='utf-8-sig')):sources[address_key(a['Address'])].append(a)
    lookup=defaultdict(list);members={}
    for r in b['rows']:
        members[r['id']]=[r]+([r['_twin']] if r.get('_twin') else [])
        for c in members[r['id']]:lookup[address_key(c['a'])].append((r,c))
    table=[];classes={x:[] for x in ['A','B_active','B_sold','B_neither','C','D_absent','D_off_active','E_building','E_contradictory','E_unknown']}
    for r in b['rows']:
        cs=members[r['id']];acts=[a for c in cs for a in sources[address_key(c['a'])]];sales=[s for c in cs for s in sold[address_key(c['a'])]]
        flags=[]
        for c in cs:
            key=address_key(c['a']);aa=sources[key];ss=sold[key]
            tags=r['tags'] if c['id']==r['id'] else b['seed'].get(c['id'],{}).get('tags',[])
            pend='pending' in tags or c['id'] in b['reconcile']['pending'] or (c.get('st')=='pending' and c['id'] not in b['reconcile']['off'])
            off=c['id'] in b['reconcile']['off'] or any(t.startswith('off_market') for t in tags)
            detail=dict(address=c['a'],id=c['id'],pin=r['id'],pin_address=r['a'],sold=[dict(mls=s['id'][1:],date=s['cd'],year_built=s.get('yb')) for s in ss],active_mls=[a['MLS Number'] for a in aa],tags=tags,weight=r['weight'],in_supply=r['id'] in b['supply'])
            if pend and ss:classes['A'].append(detail);flags.append('A')
            if (('listed' in tags or 'market' in tags or (c.get('kind')=='active' and c.get('v') is not None and c.get('st')!='pending')) and not aa):classes['D_absent'].append(detail);flags.append('D absence (unconfirmed)')
            if off and not pend and aa:classes['D_off_active'].append(detail);flags.append('D off/active')
        if r['phase']=='complete':
            detail=dict(address=r['a'],id=r['id'],homes=r['weight'],members=[c['a'] for c in cs],active=[a['Address'] for a in acts],sold=[s['a']+' ('+s['cd']+')' for s in sales])
            if acts:classes['B_active'].append(detail)
            if sales:classes['B_sold'].append(detail)
            if not acts and not sales:classes['B_neither'].append(detail);flags.append('B neither (availability unverified)')
        table.append(dict(address=r['a'],MLS='; '.join(a['MLS Number'] for a in acts) or '—',construction_status=r['phase'] or 'no evidenced stage',listing_status='; '.join(t for t in r['tags'] if t in ['market','listed','pending','active_single','active_split','built'] or t.startswith('off_market')) or 'none',active_in_export=bool(acts),sold_comp_exists=bool(sales),sold_close_date='; '.join(s['a']+': '+s['cd'] for s in sales) or '—',CONFLICT='; '.join(sorted(set(flags))) or 'none',id=r['id'],represented_homes=r['weight'],paired_addresses='; '.join(c['a'] for c in cs[1:])))
    active_table=[]
    for f,prod in INPUTS:
        for a in csv.DictReader((ROOT/f).open(encoding='utf-8-sig')):
            matches=lookup[address_key(a['Address'])];ss=sold[address_key(a['Address'])]
            row=dict(address=a['Address'],MLS=a['MLS Number'],matches=[dict(pin=r['id'],member=c['id'],address=r['a'],phase=r['phase'],inspection_phase=r.get('inspectionPhase'),tags=r['tags']) for r,c in matches],sold=[dict(address=s['a'],MLS=s['id'][1:],date=s['cd']) for s in ss])
            active_table.append(row)
            if not matches:classes['C'].append(dict(**row,assessment='Explicit OUT_OF_ZONE street exclusion; not a Heights coverage gap' if a['Address']=='1822 W 23rd Street' else 'Recent build; coverage gap requires review',year_built=a['Year Built']))
            for r,c in matches:
                if r['phase'] in ['sitework','foundation','framing','dried_in','exterior','finishing']:
                    classes['E_contradictory' if 'market' in r['tags'] else 'E_building'].append(row)
                elif r['phase']!='complete':classes['E_unknown'].append(row)
    complete_units=[]
    for r in b['rows']:
        if r['phase']!='complete':continue
        cs=members[r['id']]
        for c in cs:
            aa=sources[address_key(c['a'])];ss=sold[address_key(c['a'])]
            complete_units.append(dict(address=c['a'],pin=r['id'],active=bool(aa),sold=bool(ss),category='active' if aa else 'sold' if ss else 'neither',inferred=False))
        for n in range(max(0,r['weight']-len(cs))):
            complete_units.append(dict(address='Unidentified inferred companion '+str(n+1)+' of '+r['a'],pin=r['id'],active=False,sold=False,category='neither',inferred=True))
    classes['B_neither_units']=[r for r in complete_units if r['category']=='neither']
    removed=sorted({x['pin'] for x in classes['A'] if x['in_supply']})
    added=sum(x['homes'] for x in classes['B_neither'])
    parcel_ids=set()
    metadata=json.loads((ROOT/'heights_deed.data.json').read_text())
    for pull in metadata['pulls']:
        for r in pull['properties']:
            if r.get('apn'):parcel_ids.add(r['id'])
    permits=[r for r in raw if r.get('permits')]
    result=dict(complete_units=complete_units,complete_unit_counts=dict(Counter(r['category'] for r in complete_units)),baseline=dict(raw_records=len(raw),runtime_records=len(b['rows']),represented_homes=sum(r['weight'] for r in b['rows']),sold=len(b['sold']),deed=b['deed'],phase_breakdown=b['breakdown'],supply=len(b['supply']),permit_records=len(permits),permit_external_apn=sum(r['id'] in parcel_ids for r in permits)),active_matches=active_table,classes=classes,table=table,impact=dict(current=len(b['supply']),A_supply_pins=removed,A_adjustment=-len(removed),B_neither_pins=len(classes['B_neither']),B_neither_homes=added,result_record_basis=len(b['supply'])-len(removed)+len(classes['B_neither']),result_mixed_home_scenario=len(b['supply'])-len(removed)+len(classes['B_neither_units']),current_supply_homes=sum(r['weight'] for r in b['rows'] if r['id'] in b['supply']),result_home_basis=sum(r['weight'] for r in b['rows'] if r['id'] in b['supply'])-len(removed)+len(classes['B_neither_units'])))
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    (output/'active-reconciliation-2026-09-08.json').write_text(json.dumps(result,indent=2)+'\n')
    buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=list(table[0]));w.writeheader();w.writerows(table);(output/'active-reconciliation-2026-09-08.csv').write_text(buf.getvalue())
    lines=['# Heights active listings reconciliation — 2026-09-08','', 'Read-only diagnosis. No status or supply computation has been changed. Original List Price is not current asking price. Export absence and historical sale matches do not establish present availability. Paired pin stage may reflect combined inspection evidence; it is not a separate certification for each unit.','', '## Executed baseline','```json',json.dumps(result['baseline'],indent=2),'```','', '## All 41 source listings','| Address | MLS | Construction / matched pin | Sold close date |','|---|---|---|---|']
    for r in active_table:lines.append('| '+ ' | '.join([r['address'],r['MLS'],'; '.join((m['phase'] or 'no evidenced stage')+' / '+m['address'] for m in r['matches']) or 'Unmatched / excluded','; '.join(s['date'] for s in r['sold']) or 'None'])+' |')
    lines+=['','## Full reconciliation table','One row per visible property/project pin. Paired addresses and represented-home counts are retained in the CSV; sold/active evidence can concern different members of the same pair.','| Address | MLS | Construction status | Stored/runtime listing tags | Active in export? | Sold comp? | Sold close date | CONFLICT |','|---|---|---|---|---|---|---|---|']
    for r in table:lines.append('| '+' | '.join(str(r[k]).replace('|','/') for k in list(r)[:8])+' |')
    for k,rs in classes.items():
        lines+=['','## Class '+k+' — '+str(len(rs))+' members','']
        for r in rs:lines.append('- '+json.dumps(r,ensure_ascii=False))
    lines+=['','## Supply impact','```json',json.dumps(result['impact'],indent=2),'```','The current algorithm counts project/pin records, whereas the stage panel counts represented homes. Use result_record_basis for arithmetic consistent with the existing counter. The mixed-home scenario adds all represented homes and is labeled separately. Neither scenario proves immediate availability; no sold comp in a finite archive is not proof of unsold status. A pin representing multiple homes cannot safely be fully retired because one member sold.','']
    (output/'active-reconciliation-2026-09-08.md').write_text('\n'.join(lines))
    print(json.dumps(dict(baseline=result['baseline'],classes={k:len(v) for k,v in classes.items()},complete_unit_counts=result['complete_unit_counts'],impact=result['impact'],matched=sum(bool(a['matches']) for a in active_table)),indent=2))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('baseline');p.add_argument('--output',default='docs');a=p.parse_args();run(a.baseline,a.output)
