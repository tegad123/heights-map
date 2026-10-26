#!/usr/bin/env python3
"""Replace Heights displayed comps; keep historical sale evidence separate."""
import argparse, csv, hashlib, json, re
from collections import Counter
from datetime import date,timedelta
from pathlib import Path
from combined_market_ingest import load
from deed_ingest import span,encode
from market_address import address_key
import market_status_ingest as legacy
from sold_ingest import metrics_for, money, refresh_derived
ROOT=Path(__file__).resolve().parent
HEIGHTS_SOLD_COMP_MIN_LOT_SQFT = 2200
ABSENT_SOURCE_REASON = 'absent from source export, cause unconfirmed'
INCREMENTAL_COVERAGE = 'Incremental refresh; complete market coverage not independently established'
# A sold export whose earliest close falls this close to the window start is
# treated as covering the whole trailing window.
FULL_WINDOW_SLACK_DAYS = 31
RETIREMENT_FIELDS = ['MLS','ADDRESS','CLOSE_DATE','REASON','EVIDENCE',
                     'SOURCE_SHA256','POLICY_JSON','INPUT_ROW','INPUT_RAW_JSON','HISTORICAL_JSON']

def lot_exclusion(lot):
    lot=money(lot)
    if lot is None or lot<=0:
        return 'MISSING_OR_INVALID_LOT_SIZE'
    if lot<HEIGHTS_SOLD_COMP_MIN_LOT_SQFT:
        return 'BELOW_COMP_MIN_LOT_SQFT'
    return None

def replace_once_or_already(text, old, new):
    if text.count(new)==1 and old not in text:
        return text
    if text.count(old)!=1 or new in text:
        raise ValueError('Comp UI anchor missing or ambiguous')
    return text.replace(old,new,1)

def run(args):
    html=(ROOT/'index.html').read_text();today=date.fromisoformat(args.as_of)
    split='const SOLD_EVIDENCE=' in html
    evidence=span(html,'SOLD_EVIDENCE' if split else 'SOLD_DATA')[2]
    before=span(html,'SOLD_DATA')[2]
    records,ledger,profile=load(Path(args.input),html,args.as_of)
    source_sha256=hashlib.sha256(Path(args.input).read_bytes()).hexdigest()
    source_by_id={'s'+r['mls']:r for r in records}
    if len(source_by_id)!=len(records):
        raise ValueError('Duplicate input MLS; resolve before comp refresh')
    decisions={rid:r['exclusion'] for rid,r in source_by_id.items()}
    accepted=[];seen=set()
    for rec in records:
        if rec['exclusion']:continue
        reason=None
        if rec['status']!='sold':reason='NOT_SOLD'
        elif not today-timedelta(days=365)<=date.fromisoformat(rec['close_date'])<=today:reason='OUTSIDE_365_DAYS'
        elif rec['year_built'] not in (2024,2025,2026):reason='OUTSIDE_CLIENT_NEW_CONSTRUCTION_EXPORT'
        elif lot_exclusion(rec['lot_sqft']):reason=lot_exclusion(rec['lot_sqft'])
        elif rec['address_key'] in seen:reason='DUP_NORMALIZED_ADDRESS'
        decisions['s'+rec['mls']]=reason
        if reason:
            ledger.append(dict(FILE=rec['source_file'],SHA256=rec['source_sha256'],ROW=rec['source_row'],MLS=rec['mls'],ADDRESS=rec['address'],REASON=reason,RAW_JSON=json.dumps(rec['raw'],sort_keys=True)))
        else:accepted.append(rec);seen.add(rec['address_key'])
    legacy.AS_OF=args.as_of
    comps,merged_report=legacy.merge_sales([],accepted)
    assert not merged_report['conflicts']
    for row in comps:row['coh']='nc' # Explicit client new-construction export, including its 2024 builds.
    comps.sort(key=lambda r:(r['cd'],r['id']),reverse=True)
    counts=Counter();by_id={r['id']:r for r in evidence};extended=list(evidence)
    for row in comps:
        prior=by_id.get(row['id'])
        if prior and address_key(prior['a'])!=address_key(row['a']):raise ValueError('MLS address conflict '+row['id'])
        if not prior:prior=next((r for r in evidence if address_key(r['a'])==address_key(row['a']) and r['cd']==row['cd']),None)
        if prior:counts['already_held']+=1
        else:extended.append(row);counts['new']+=1
    if any(lot_exclusion(row.get('lot')) for row in comps):
        raise ValueError('Comp lot policy validation failed')
    metrics=metrics_for(comps,today)
    metrics['basis']=(
        'Displayed comps only: client HAR new-construction sold export, '
        f'trailing 365 days, lot size >= {HEIGHTS_SOLD_COMP_MIN_LOT_SQFT:,} sqft. '
        'Includes 2024-built new homes. Historical/resale sale evidence '
        'is separate and excluded from these metrics.')
    policy=dict(
        kind='new_construction_trailing_365',
        as_of=args.as_of,
        start=(today-timedelta(days=365)).isoformat(),
        end=args.as_of,
        source=Path(args.input).name,
        min_lot_sqft=HEIGHTS_SOLD_COMP_MIN_LOT_SQFT)
    candidate=html
    if not split:
        pos=candidate.index('const SOLD_DATA=')
        candidate=candidate[:pos]+'const SOLD_EVIDENCE='+encode(extended)+'; // Historical sales: evidence only, never rendered as comps.\nconst SOLD_COMP_POLICY='+encode(policy)+';\n'+candidate[pos:]
    for name,value in [('SOLD_EVIDENCE',extended),('SOLD_COMP_POLICY',policy),('SOLD_DATA',comps),('SOLD_METRICS',metrics)]:
        a,b,old=span(candidate,name)
        if old!=value:candidate=candidate[:a]+encode(value)+candidate[b:]
    candidate=replace_once_or_already(
        candidate,
        'Closed-sales archive · in-zone · source export coverage varies.',
        "New-construction sold comps · trailing 365 days · in-zone · "
        "lots at least '+SOLD_COMP_POLICY.min_lot_sqft.toLocaleString()+' sqft.")
    candidate=replace_once_or_already(
        candidate,
        'Product: Single Lot = lot >=4000 sqft; Split Lot = positive lot '
        '<4000 sqft; Unknown = missing, nonpositive or unparseable lot.',
        "Comp eligibility: lot >= '+SOLD_COMP_POLICY.min_lot_sqft+' sqft; "
        "missing or invalid lots are excluded from displayed comps only. "
        "Product: Single Lot = lot >=4000 sqft; Split Lot = eligible lot "
        "<4000 sqft. Historical evidence and construction eligibility "
        "are unchanged.")
    for name in ['DATA','RECONCILE']:
        a,b,_=span(html,name);c,d,_=span(candidate,name);assert html[a:b]==candidate[c:d]
    outputs={ROOT/'index.html':candidate,ROOT/f'pulls/dropped_sold_comp_{args.as_of}.csv':legacy.csvtxt(ledger,['FILE','SHA256','ROW','MLS','ADDRESS','REASON','RAW_JSON'])}
    comp_ids={r['id'] for r in comps};retired=[]
    before_by_id={r['id']:r for r in before}
    retirement_path=ROOT/f'pulls/retired_sold_comps_{args.as_of}.csv'
    historical_facts={}
    if retirement_path.exists():
        with retirement_path.open(newline='') as stream:
            for entry in csv.DictReader(stream):
                if entry.get('HISTORICAL_JSON'):
                    facts=json.loads(entry['HISTORICAL_JSON'])
                    rid='s'+entry['MLS']
                    if facts.get('id')!=rid:
                        raise ValueError('Retirement historical identity mismatch')
                    historical_facts[rid]=facts

    policy_json=json.dumps(policy,sort_keys=True,separators=(',',':'))
    for row in extended:
        if row['id'] in comp_ids:continue
        rid=row['id']
        facts=before_by_id.get(rid,historical_facts.get(rid,row))
        current=source_by_id.get(rid)
        if current is not None:
            reason=decisions[rid]
            if reason is None:
                raise ValueError('Accepted source MLS missing from comps: '+rid)
            if current['status']=='sold':
                facts=dict(
                    facts,a=current['address'],cd=current['close_date'],
                    lot=current['lot_sqft'],yb=current['year_built'],
                    cp=current['close_price'])
        elif not policy['start']<=facts['cd']<=policy['end']:
            reason='OUTSIDE_365_DAY_COMP_WINDOW'
        elif facts.get('coh')=='resale':
            reason='RESALE_NOT_COMP'
        else:
            reason=lot_exclusion(facts.get('lot')) or ABSENT_SOURCE_REASON
        retired.append(dict(
            MLS=rid.removeprefix('s'),
            ADDRESS=facts['a'],
            CLOSE_DATE=facts['cd'],
            REASON=reason,
            EVIDENCE='Retained in SOLD_EVIDENCE',
            SOURCE_SHA256=source_sha256,
            POLICY_JSON=policy_json,
            INPUT_ROW=current['source_row'] if current else '',
            INPUT_RAW_JSON=(
                json.dumps(current['raw'],sort_keys=True) if current else ''),
            HISTORICAL_JSON=json.dumps(facts,sort_keys=True)))
    fields=[
        'MLS','ADDRESS','CLOSE_DATE','REASON','EVIDENCE',
        'SOURCE_SHA256','POLICY_JSON','INPUT_ROW','INPUT_RAW_JSON',
        'HISTORICAL_JSON']
    retirement_text=legacy.csvtxt(retired,fields)
    outputs[retirement_path]=retirement_text
    audit_hash=hashlib.sha256(retirement_text.encode()).hexdigest()
    audit_path=(
        ROOT/f'pulls/retired_sold_comps_{args.as_of}'/f'{audit_hash}.csv')
    if audit_path.exists() and audit_path.read_bytes()!=retirement_text.encode():
        raise ValueError('Retirement audit snapshot conflict')
    outputs[audit_path]=retirement_text
    changed=[str(p.relative_to(ROOT)) for p,text in outputs.items() if not p.exists() or p.read_text()!=text]
    report=dict(display_retirements=len(retired),retirement_reasons=dict(Counter(r['REASON'] for r in retired)),profile=profile,counts=dict(counts),excluded=len(ledger),reasons=dict(Counter(r['REASON'] for r in ledger)),comps_before=len(before),comps_after=len(comps),evidence_before=len(evidence),evidence_after=len(extended),legacy_resale_before=sum(r.get('coh')=='resale' for r in before),retired_resale_pins=sum(r.get('coh')=='resale' and r['id'] not in {c['id'] for c in comps} for r in before),reclassified_2024_new_builds=sum(r.get('coh')=='resale' and r['id'] in {c['id'] for c in comps} for r in before),unknown_product=sum(r['prod']=='Unknown' for r in comps),median_price=metrics['overall']['med_price'],changed_files=changed)
    report['new_display_retirements']=len(set(before_by_id)-comp_ids)
    report['evidence_only_total']=len(retired)
    if args.apply:
        for p,text in outputs.items():
            if str(p.relative_to(ROOT)) in changed:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
    if args.output:Path(args.output).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));return report

def _labels(text):
    return [x for x in re.split(r', | and ',text) if x]

def _join(labels):
    return labels[0] if len(labels)==1 else ', '.join(labels[:-1])+' and '+labels[-1]

def window_scope(close_min, as_of):
    """'full' only when the export's earliest close reaches back to the window start."""
    start=date.fromisoformat(as_of)-timedelta(days=365)
    if close_min and date.fromisoformat(close_min)<=start+timedelta(days=FULL_WINDOW_SLACK_DAYS):
        return 'full'
    return 'incremental'

def rolling(html, records, as_of, evidence, scope):
    """Displayed comps from one dated sold export under the run() policy.
    'incremental' keeps prior in-window comps the export does not repeat; 'full'
    replaces the set as run() does. Comps that leave the set retire to evidence."""
    today=date.fromisoformat(as_of);start=today-timedelta(days=365)
    label=today.strftime('%B ')+str(today.day)
    prior_policy=span(html,'SOLD_COMP_POLICY')[2]
    if prior_policy.get('kind')!='new_construction_trailing_365' or prior_policy.get('min_lot_sqft')!=HEIGHTS_SOLD_COMP_MIN_LOT_SQFT:
        raise ValueError('Unexpected SOLD_COMP_POLICY; refusing rolling comp refresh')
    if prior_policy['as_of']>=as_of:
        raise ValueError('SOLD_COMP_POLICY already at or after '+as_of)
    hashes={r['source_sha256'] for r in records}
    if len(hashes)!=1:raise ValueError('Rolling comp refresh takes exactly one sold export')
    source_sha256=hashes.pop()
    before=span(html,'SOLD_DATA')[2]
    kept=[dict(r) for r in before if r['cd']>=start.isoformat()] if scope=='incremental' else []
    holder={address_key(r['a']):r for r in kept}
    accepted=[];ledger=[];decisions={}
    for rec in records:
        rid='s'+rec['mls']
        if rec['exclusion']:
            decisions[rid]=rec['exclusion'];continue
        reason=None;held=holder.get(rec['address_key'])
        if rec['status']!='sold':reason='NOT_SOLD'
        elif not start<=date.fromisoformat(rec['close_date'])<=today:reason='OUTSIDE_365_DAYS'
        elif rec['year_built'] not in (2024,2025,2026):reason='OUTSIDE_CLIENT_NEW_CONSTRUCTION_EXPORT'
        elif lot_exclusion(rec['lot_sqft']):reason=lot_exclusion(rec['lot_sqft'])
        elif held and held['id']!=rid and held['cd']!=rec['close_date']:reason='DUP_NORMALIZED_ADDRESS'
        decisions[rid]=reason
        if reason:
            ledger.append(dict(FILE=rec['source_file'],SHA256=rec['source_sha256'],ROW=rec['source_row'],MLS=rec['mls'],ADDRESS=rec['address'],REASON=reason,RAW_JSON=json.dumps(rec['raw'],sort_keys=True)))
        else:
            accepted.append(rec);holder.setdefault(rec['address_key'],dict(id=rid,cd=rec['close_date']))
    kept=[r for r in kept if not decisions.get(r['id'])]
    legacy.AS_OF=as_of
    comps,merged=legacy.merge_sales(kept,accepted)
    if merged['conflicts']:raise ValueError(merged['conflicts'])
    for row in comps:row['coh']='nc' # Explicit client new-construction export, including its 2024 builds.
    comps=refresh_derived(comps,today)
    if any(lot_exclusion(row.get('lot')) for row in comps):
        raise ValueError('Comp lot policy validation failed')
    extended=list(evidence);by_id={r['id']:r for r in evidence};counts=Counter()
    for row in comps+[r for r in before if r['id'] not in {c['id'] for c in comps}]:
        prior=by_id.get(row['id'])
        if prior and address_key(prior['a'])!=address_key(row['a']):raise ValueError('MLS address conflict '+row['id'])
        if prior or any(address_key(r['a'])==address_key(row['a']) and r['cd']==row['cd'] for r in evidence):counts['already_held']+=1
        else:extended.append(row);by_id[row['id']]=row;counts['new_evidence']+=1
    if scope=='incremental':
        m=re.fullmatch(r'(.+?) \+ (.+) incremental sales',prior_policy['source'])
        base,labels=(m[1],_labels(m[2])) if m else (prior_policy['source'],[])
        if label not in labels:labels.append(label)
        source=f'{base} + {_join(labels)} incremental sales'
        basis=(f'Displayed eligible new-construction comps, trailing 365 days, lots >={HEIGHTS_SOLD_COMP_MIN_LOT_SQFT:,} sqft. '
               f'Incremental merge of {base} with {_join(labels)} sales; not a new full-year census.')
        coverage=INCREMENTAL_COVERAGE
    else:
        closes=sorted(r['close_date'] for r in records if r['close_date'])
        source=f'{label} full-window sold export'
        basis=('Displayed comps only: client HAR new-construction sold export, '
               f'trailing 365 days, lot size >= {HEIGHTS_SOLD_COMP_MIN_LOT_SQFT:,} sqft. '
               'Includes 2024-built new homes. Historical/resale sale evidence '
               'is separate and excluded from these metrics.')
        coverage=f'Single export spanning the trailing window (closes {closes[0]}..{closes[-1]})'
    metrics=metrics_for(comps,today);metrics['basis']=basis
    policy=dict(kind='new_construction_trailing_365',as_of=as_of,start=start.isoformat(),end=as_of,
                source=source,min_lot_sqft=HEIGHTS_SOLD_COMP_MIN_LOT_SQFT,coverage=coverage)
    policy_json=json.dumps(policy,sort_keys=True,separators=(',',':'))
    source_by_id={'s'+r['mls']:r for r in records}
    comp_ids={r['id'] for r in comps};retired=[]
    for row in before:
        if row['id'] in comp_ids:continue
        current=source_by_id.get(row['id'])
        reason=(decisions.get(row['id']) or
                ('OUTSIDE_365_DAY_COMP_WINDOW' if row['cd']<start.isoformat() else ABSENT_SOURCE_REASON))
        retired.append(dict(
            MLS=row['id'].removeprefix('s'),ADDRESS=row['a'],CLOSE_DATE=row['cd'],REASON=reason,
            EVIDENCE='Retained in SOLD_EVIDENCE',SOURCE_SHA256=source_sha256,POLICY_JSON=policy_json,
            INPUT_ROW=current['source_row'] if current else '',
            INPUT_RAW_JSON=json.dumps(current['raw'],sort_keys=True) if current else '',
            HISTORICAL_JSON=json.dumps(row,sort_keys=True)))
    before_ids={r['id'] for r in before}
    report=dict(
        scope=scope,before=len(before),after=len(comps),
        added=[r['id'].removeprefix('s') for r in comps if r['id'] not in before_ids],
        updated=merged['updated'],
        retired_outside_window=['s'+r['MLS'] for r in retired if r['REASON']=='OUTSIDE_365_DAY_COMP_WINDOW'],
        retired_other={'s'+r['MLS']:r['REASON'] for r in retired if r['REASON']!='OUTSIDE_365_DAY_COMP_WINDOW'},
        start=start.isoformat(),coverage=coverage,evidence=dict(counts),
        excluded=dict(Counter(r['REASON'] for r in ledger)))
    return dict(comps=comps,metrics=metrics,policy=policy,evidence=extended,
                ledger=ledger,retired=retired,report=report)

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--input',required=True)
    p.add_argument('--as-of',required=True)
    p.add_argument('--apply',action='store_true')
    p.add_argument('--output')
    run(p.parse_args())
