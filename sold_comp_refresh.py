#!/usr/bin/env python3
"""Replace Heights displayed comps; keep historical sale evidence separate."""
import argparse, csv, hashlib, json
from collections import Counter
from datetime import date,timedelta
from pathlib import Path
from combined_market_ingest import load
from deed_ingest import span,encode
from market_address import address_key
import market_status_ingest as legacy
from sold_classification import MIN_LOT_SQFT, MIN_YEAR_BUILT, lot_floor_reason
from sold_ingest import metrics_for, money, refresh_derived
ROOT=Path(__file__).resolve().parent
HEIGHTS_SOLD_COMP_MIN_LOT_SQFT = MIN_LOT_SQFT
ABSENT_SOURCE_REASON = 'absent from source export, cause unconfirmed'

def lot_exclusion(lot):
    return lot_floor_reason(lot, HEIGHTS_SOLD_COMP_MIN_LOT_SQFT)

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
def merge_incremental(inputs, as_of, apply=False):
    """Merge a single/split sold export into the displayed comps and the evidence store.

    New MLS rows that pass the zone guards, year floor, and lot floor are added.
    Existing comps stay, including ones this short export does not repeat.
    Display comps older than the trailing 365 days leave SOLD_DATA and stay in
    SOLD_EVIDENCE. Absence from this export is not a retirement.
    """
    html=(ROOT/'index.html').read_text()
    today=date.fromisoformat(as_of)
    if 'const SOLD_EVIDENCE=' not in html or 'const SOLD_COMP_POLICY=' not in html:
        raise ValueError('incremental comp merge requires the split evidence/policy constants')
    evidence=span(html,'SOLD_EVIDENCE')[2]
    before=span(html,'SOLD_DATA')[2]
    policy=dict(span(html,'SOLD_COMP_POLICY')[2])
    records=[]; ledger=[]; summaries=[]; mismatches=[]; seen=set()
    for path, expected in inputs:
        path=Path(path)
        recs, _dropped, profile=load(path, html, as_of)
        summary=dict(file=path.name, read=profile['rows'], accepted=0, excluded=Counter(), classification_matches=0)
        for rec in recs:
            floor=lot_floor_reason(rec['raw'].get('Lot Size'))
            if floor or rec['product']==expected:
                summary['classification_matches']+=1
            else:
                mismatches.append(dict(file=path.name, row=rec['source_row'], address=rec['address'], derived=rec['product'], expected=expected))
            if not rec['exclusion']:
                if rec['year_built'] is None or rec['year_built']<MIN_YEAR_BUILT:
                    rec['exclusion']='YEAR_BEFORE_MIN'
                elif floor:
                    rec['exclusion']=floor
                elif not rec['building_sqft'] or rec['building_sqft']<=0:
                    rec['exclusion']='MISSING_BUILDING_SQFT'
                elif not today-timedelta(days=365)<=date.fromisoformat(rec['close_date'])<=today:
                    rec['exclusion']='OUTSIDE_365_DAYS'
                elif rec['mls'] in seen:
                    rec['exclusion']='DUP_INPUT'
            if rec['exclusion']:
                summary['excluded'][rec['exclusion']]+=1
                ledger.append(dict(FILE=path.name, SHA256=rec['source_sha256'], ROW=rec['source_row'], MLS=rec['mls'], ADDRESS=rec['address'], REASON=rec['exclusion'], RAW_JSON=json.dumps(rec['raw'], sort_keys=True)))
            else:
                seen.add(rec['mls']); summary['accepted']+=1; records.append(rec)
        summaries.append(summary)
    legacy.AS_OF=as_of
    evidence_rows, evidence_report=legacy.merge_sales(list(evidence), records)
    display_rows, display_report=legacy.merge_sales(list(before), records)
    if evidence_report['conflicts'] or display_report['conflicts']:
        raise ValueError({'evidence':evidence_report['conflicts'], 'display':display_report['conflicts']})
    start=today-timedelta(days=365)
    kept=[]; aged=[]
    accepted_ids={'s'+rec['mls'] for rec in records}
    for row in display_rows:
        reason=None
        closed=date.fromisoformat(row['cd'])
        if closed<start or closed>today:
            reason='OUTSIDE_365_DAY_COMP_WINDOW'
        else:
            reason=lot_floor_reason(row.get('lot'))
        if reason:
            if row['id'] in accepted_ids:
                raise ValueError('Accepted sale failed display policy: '+row['id']+' '+reason)
            aged.append(dict(MLS=row['id'].removeprefix('s'), ADDRESS=row['a'], CLOSE_DATE=row['cd'], REASON=reason))
        else:
            kept.append(row)
    aged.sort(key=lambda row: (row['CLOSE_DATE'], row['MLS']))
    kept=refresh_derived(kept, today)
    if any(lot_floor_reason(row.get('lot')) for row in kept):
        raise ValueError('Comp lot policy validation failed')
    metrics=metrics_for(kept, today)
    metrics['basis']=(
        'Displayed eligible new-construction comps, trailing 365 days, lots >=2,200 sqft. '
        f'Incremental merge of the September 14 baseline with later sales through {as_of}; '
        'not a new full-year census.')
    policy.update(as_of=as_of, start=start.isoformat(), end=as_of,
                  source='September 14 baseline + incremental sales through '+as_of,
                  min_lot_sqft=HEIGHTS_SOLD_COMP_MIN_LOT_SQFT,
                  coverage='Incremental refresh; complete market coverage not independently established')
    candidate=html
    for name,value in [('SOLD_EVIDENCE',evidence_rows),('SOLD_COMP_POLICY',policy),('SOLD_DATA',kept),('SOLD_METRICS',metrics)]:
        a,b,old=span(candidate,name)
        if old!=value:candidate=candidate[:a]+encode(value)+candidate[b:]
    for name in ['DATA','RECONCILE']:
        a,b,_=span(html,name);c,d,_=span(candidate,name);assert html[a:b]==candidate[c:d]
    before_ids={row['id'] for row in before}
    evidence_ids={row['id'] for row in evidence}
    aged_ids={'s'+row['MLS'] for row in aged}
    removed=before_ids-aged_ids-{row['id'] for row in kept}
    if removed:
        raise ValueError('Displayed comp removed for a reason other than the trailing window or lot floor: '+', '.join(sorted(removed)))
    if not evidence_ids <= {row['id'] for row in evidence_rows}:
        raise ValueError('Historical sale evidence was dropped')
    outputs={
        ROOT/'index.html':candidate,
        ROOT/f'pulls/dropped_sold_{as_of}.csv':legacy.csvtxt(ledger,['FILE','SHA256','ROW','MLS','ADDRESS','REASON','RAW_JSON']),
        ROOT/f'pulls/aged_sold_comps_{as_of}.csv':legacy.csvtxt(aged,['MLS','ADDRESS','CLOSE_DATE','REASON'])}
    changed=[str(p.relative_to(ROOT)) for p,text in outputs.items() if not p.exists() or p.read_text()!=text]
    products=Counter(row['prod'] for row in kept)
    report=dict(mode='APPLY' if apply else 'DRY RUN', as_of=as_of, files=summaries,
                crosscheck_mismatches=mismatches, comps_before=len(before), comps_after=len(kept),
                added=display_report['added'], updated=display_report['updated'],
                aged_out=aged, products=dict(products),
                evidence_before=len(evidence), evidence_after=len(evidence_rows),
                evidence_added=evidence_report['added'], ledger_rows=len(ledger), changed_files=changed)
    print(json.dumps(report, indent=2))
    if mismatches:
        raise ValueError('export classification mismatch; refusing apply')
    if apply:
        for path,text in outputs.items():
            if str(path.relative_to(ROOT)) in changed:
                path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--input',required=True)
    p.add_argument('--as-of',required=True)
    p.add_argument('--apply',action='store_true')
    p.add_argument('--output')
    run(p.parse_args())
