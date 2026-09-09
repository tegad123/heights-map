"""Independent market identity/history; never writes HTML or construction state."""
import hashlib
import inspect
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from market_address import address_key
from active_ingest import address_key as legacy_address_key
from deed_ingest import span

PRIORITY = {'sold': 4, 'pending': 3, 'active': 2, 'terminated': 1}


def distance(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, [a['lat'], a['lng'], b['lat'], b['lng']])
    q = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 12742000 * math.asin(min(1, math.sqrt(q)))


def mls_key(value):
    return re.sub(r'[^0-9]', '', str(value or ''))


class Matcher:
    def __init__(self, source, runtime):
        self.source = source
        self.members = {}
        for pin in runtime['raw']:
            for member in [pin] + ([pin['_twin']] if pin.get('_twin') else []):
                self.members[member['id']] = (pin['id'], member)
        self.addresses, self.mls = defaultdict(list), defaultdict(list)
        # Retain hidden identities. A historical sold flag cannot erase a join.
        for r in source:
            self.addresses[address_key(r['a'])].append(r)
            for k in ('mls', 'mls_number', 'MLS Number'):
                if r.get(k): self.mls[mls_key(r[k])].append(r)

    def match(self, rec):
        method = 'mls'
        candidates = self.mls[mls_key(rec['mls'])]
        if not candidates:
            method = 'address'
            candidates = self.addresses[address_key(rec['address'])]
        if len(candidates) > 1:
            return dict(method=None, member=None, pin=None, issue='AMBIGUOUS_IDENTITY', candidates=[r['id'] for r in candidates])
        if candidates:
            row = candidates[0]
            if method == 'mls' and address_key(row['a']) != address_key(rec['address']):
                return dict(method=None, member=None, pin=None, issue='MLS_ADDRESS_CONFLICT', candidates=[row['id']])
            pin = self.members.get(row['id'], (None, None))[0]
            return dict(method=method, member=row['id'], pin=pin,
                        issue=None if pin else 'HIDDEN_LEGACY_SOLD' if row.get('st') == 'sold' else 'HIDDEN_REVIEW', candidates=[])
        near = [r for r in self.source if r.get('lat') and r.get('lng') and distance(rec, r) <= 25]
        if len(near) == 1:
            row = near[0]
            # Exactly one nearby lot is necessary, not sufficient. Different
            # numbers, directionals, fractions or units are explicit conflicts.
            identity = lambda a: [x for x in address_key(a).split() if x not in ('st','ave','ln','dr','rd','ct','pl','blvd')]
            if identity(row['a']) == identity(rec['address']):
                return dict(method='coordinate', member=row['id'], pin=self.members.get(row['id'], (None,None))[0], issue=None, candidates=[])
            issue = 'COORDINATE_IDENTITY_CONFLICT'
        else:
            issue = 'AMBIGUOUS_COORDINATE' if near else 'NOT_TRACKED'
        return dict(method=None, member=None, pin=None, issue=issue,
                    candidates=[dict(id=r['id'], address=r['a'], meters=round(distance(rec,r),2)) for r in near])


def resolve(records):
    """Current source statuses outrank undated failed history; never infer dates from DOM."""
    rows = sorted(records, key=lambda r: (PRIORITY[r['status']], r.get('close_date') or r.get('status_date') or '', r['mls']), reverse=True)
    current = rows[0]
    tied = [r for r in rows if r['status'] == current['status'] and
            (r.get('close_date') or r.get('status_date') or '') == (current.get('close_date') or current.get('status_date') or '')]
    return dict(status=current['status'], current=current, history=rows[1:],
                failed_listings=[dict(mls=r['mls'], dom=r['dom']) for r in rows if r['status']=='terminated'],
                ordering_issue='SAME_STATUS_DATES_UNAVAILABLE' if len(tied)>1 else None,
                chronology='Status precedence; non-sold event dates absent from export')


def run(args):
    from market_status_ingest import ROOT, AS_OF, load_inputs, jsontxt, csvtxt, merge_sales, metrics_for, encode
    from datetime import date
    html = (ROOT/'index.html').read_text()
    runtime_file = json.loads(Path(args.runtime).read_text())
    runtime = runtime_file.get('index', runtime_file.get('runtime'))
    if not runtime or not runtime.get('raw'): raise ValueError('Fresh runtime with raw DATA required')
    source = span(html, 'DATA')[2]
    sold = span(html, 'SOLD_DATA')[2]
    records, dropped, summaries = load_inputs(html)
    sold, sold_merge = merge_sales(sold, records)
    if sold_merge['conflicts']: raise ValueError('Sold conflicts require review: '+json.dumps(sold_merge['conflicts']))
    assert len(records) == 284
    assert sum(s['classification_matches'] for s in summaries[-4:]) == 165
    assert {r['mls'] for r in records[:119] if r['status']=='active'} == {r['mls'] for r in records[225:]}
    matcher = Matcher(source, runtime)
    groups = defaultdict(list)
    links = []
    audit_ledger = []
    before = Counter()
    phases = {r['id']: r for r in runtime['rows']}
    for rec in records:
        link = matcher.match(rec)
        runtime_matches = [(pin, member) for pin, member in matcher.members.values() if legacy_address_key(member['a']) == legacy_address_key(rec['address'])]
        before['address'] += len(runtime_matches)==1
        before['with_phase'] += any(phases[p]['phase'] for p,m in runtime_matches)
        entry = dict(source_file=rec['source_file'], source_row=rec['source_row'], mls=rec['mls'], address=rec['address'], status=rec['status'], exclusion=rec['exclusion'], **link)
        links.append(entry)
        if link['issue']: audit_ledger.append(entry)
        if not rec['exclusion']:
            key = link['member'] or 'address:'+address_key(rec['address'])
            groups[key].append({k:v for k,v in rec.items() if k not in ('raw','agents')})
    properties = {key: resolve(rr) for key,rr in sorted(groups.items())}
    # Archive closes are secondary evidence. Old-structure resales stay history only.
    archive = defaultdict(list)
    for sale in sold: archive[address_key(sale['a'])].append(sale)
    tracked = []
    for member_id,(pin_id, member) in matcher.members.items():
        prop = properties.get(member_id)
        history = sorted(archive[address_key(member['a'])], key=lambda s:s['cd'], reverse=True)
        new_build = [s for s in history if (s.get('yb') or 0)>=2025]
        status = prop['status'] if prop else 'sold' if new_build else 'no_record'
        tracked.append(dict(member=member_id, pin=pin_id, address=member['a'], phase=phases[pin_id]['phase'],
                            product=prop['current']['product'] if prop else member.get('prod') or 'Unknown',
                            status=status, current=prop['current'] if prop else None,
                            history=prop['history'] if prop else [], historical_sales=history,
                            archive_current=new_build[0] if new_build and not prop else None,
                            ordering_issue=prop['ordering_issue'] if prop else None,
                            category=runtime['points'].get(pin_id,{}).get('classification',{}).get('category'),
                            in_supply=pin_id in runtime['supplyIds']))
    complete = [r for r in tracked if r['phase']=='complete' and not r['category']]
    for pin in runtime['raw']:
        if phases[pin['id']]['phase'] != 'complete' or runtime['points'].get(pin['id'],{}).get('classification'): continue
        for i in range(max(0, phases[pin['id']]['weight']-(2 if pin.get('_twin') else 1))):
            complete.append(dict(member=None,pin=pin['id'],address=f"Unidentified represented home {i+1} at {pin['a']}",phase='complete',product=pin.get('prod','Unknown'),status='no_record',inferred_weight=True))
    assert len(complete)==runtime['columns']['complete']
    counts = dict(Counter(r['status'] for r in complete))
    unavailable = [r for r in tracked if r['in_supply'] and r['status'] in ('terminated','pending','sold')]
    impact = dict(current=runtime['supply'], terminated_members_in_supply=sum(r['status']=='terminated' for r in unavailable),
                  pending_members_in_supply=sum(r['status']=='pending' for r in unavailable), sold_members_in_supply=sum(r['status']=='sold' for r in unavailable),
                  member_subtraction_scenario=runtime['supply']-len(unavailable), complete_active_addition=counts.get('active',0),
                  with_complete_actives_scenario=runtime['supply']-len(unavailable)+counts.get('active',0), unavailable_members=unavailable,
                  applied=False, note='Named-member arithmetic only; paired/unnamed availability requires review. No Market Record does not establish available supply.')
    fixture=properties['act_715-merrill']
    assert fixture['status']=='active' and fixture['current']['mls']=='88557637' and fixture['current']['dom']==8
    assert any(r['mls']=='50361472' and r['dom']==174 for r in fixture['history'])
    methods=Counter(r['method'] or 'unlinked' for r in links)
    report=dict(as_of=AS_OF,input_rows=284,classification_matches=284,new_classification_matches=165,files=summaries,
                before=dict(before),after=dict(methods),after_rendered=sum(bool(r['pin']) for r in links),
                with_phase=sum(bool(r['pin']) and bool(phases[r['pin']]['phase']) for r in links),
                links=links,ledger=audit_ledger,complete=complete,complete_counts=counts,
                residual_complete_no_record=[r for r in complete if r['status']=='no_record'],supply_impact=impact,
                properties_with_multiple_listings=sum(bool(p['history']) for p in properties.values()),
                unresolved_history_order=sum(bool(p['ordering_issue']) for p in properties.values()),
                terminated=dict(rows=sum(r['status']=='terminated' for r in records),properties=sum(any(r['status']=='terminated' for r in rr) for rr in groups.values()),
                                current=sum(p['status']=='terminated' for p in properties.values()),
                                resolved_other=dict(Counter(p['status'] for p in properties.values() if p['failed_listings'] and p['status']!='terminated'))),
                source_records=len(source),source_mls=sum(any('mls' in k.lower() and v for k,v in r.items()) for r in source),
                source_parcel=sum(any(re.search('parcel|apn|account',k,re.I) and v for k,v in r.items()) for r in source),
                sold_total=len(sold),deeds=runtime['deed'],matching_code=inspect.getsource(address_key),
                limitations=['Non-sold event dates and current asking price are absent. Status precedence is explicit; unknown chronology is flagged.',
                             'Hidden legacy-sold records remain hidden pending review. No record is removed or restored.',
                             '25m proximity rejects conflicting house/unit identities even with only one candidate.',
                             'Source identity linkage and inspection coverage are separate measurements.'])
    snapshot=dict(as_of=AS_OF,price_basis='Original List Price',records=[r for r in records if not r['exclusion']],properties=properties,
                  tracked=tracked,complete=complete,coverage=dict(source_rows=284,linked=sum(bool(r['member']) for r in links),rendered=sum(bool(r['pin']) for r in links)),conflicts=audit_ledger)
    outputs={ROOT/'heights_market_status.data.json':jsontxt(snapshot),ROOT/'docs/linkage-repair-2026-09-09.json':jsontxt(report),
             ROOT/'pulls/dropped_market_status_2026-09-09.csv':csvtxt(dropped,['FILE','SHA256','ROW','MLS','ADDRESS','REASON','RAW_JSON']),
             ROOT/'docs/linkage-review-2026-09-09.json':jsontxt(audit_ledger)}
    candidate=html
    for name,value in [('SOLD_DATA',sold),('SOLD_METRICS',metrics_for(sold,date.fromisoformat(AS_OF)))]:
        start,end,old=span(candidate,name)
        if old!=value: candidate=candidate[:start]+encode(value)+candidate[end:]
    for name in ['DATA','RECONCILE']:
        a,z,_=span(html,name); b,y,_=span(candidate,name); assert html[a:z]==candidate[b:y]
    outputs[ROOT/'index.html']=candidate
    changed=[str(p.relative_to(ROOT)) for p,s in outputs.items() if not p.exists() or p.read_text()!=s]
    summary={k:report[k] for k in ['input_rows','new_classification_matches','before','after','after_rendered','with_phase','complete_counts','properties_with_multiple_listings','unresolved_history_order','terminated','sold_total','deeds']}
    summary.update(changed_files=changed,accepted=len(snapshot['records']),excluded=len(dropped),supply={k:v for k,v in impact.items() if k!='unavailable_members'})
    if args.output:
        for p,s in outputs.items():
            dest=Path(args.output)/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(s)
    if args.apply:
        for p,s in outputs.items():
            if str(p.relative_to(ROOT)) in changed:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
    print(jsontxt(summary))
    return summary
