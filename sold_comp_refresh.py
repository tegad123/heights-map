#!/usr/bin/env python3
"""Replace Heights displayed comps; keep historical sale evidence separate."""
import argparse, json
from collections import Counter
from datetime import date,timedelta
from pathlib import Path
from combined_market_ingest import load
from deed_ingest import span,encode
from market_address import address_key
import market_status_ingest as legacy
from sold_ingest import metrics_for
ROOT=Path(__file__).resolve().parent

def run(args):
    html=(ROOT/'index.html').read_text();today=date.fromisoformat(args.as_of)
    split='const SOLD_EVIDENCE=' in html
    evidence=span(html,'SOLD_EVIDENCE' if split else 'SOLD_DATA')[2]
    before=span(html,'SOLD_DATA')[2]
    records,ledger,profile=load(Path(args.input),html,args.as_of)
    accepted=[];seen=set()
    for rec in records:
        if rec['exclusion']:continue
        reason=None
        if rec['status']!='sold':reason='NOT_SOLD'
        elif not today-timedelta(days=365)<=date.fromisoformat(rec['close_date'])<=today:reason='OUTSIDE_365_DAYS'
        elif rec['year_built'] not in (2024,2025,2026):reason='OUTSIDE_CLIENT_NEW_CONSTRUCTION_EXPORT'
        elif rec['address_key'] in seen:reason='DUP_NORMALIZED_ADDRESS'
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
    metrics=metrics_for(comps,today)
    metrics['basis']='Displayed comps only: client HAR new-construction sold export, trailing 365 days. Includes 2024-built new homes. Historical/resale sale evidence is separate and excluded from these metrics.'
    policy=dict(kind='new_construction_trailing_365',as_of=args.as_of,start=(today-timedelta(days=365)).isoformat(),end=args.as_of,source=Path(args.input).name)
    candidate=html
    if not split:
        pos=candidate.index('const SOLD_DATA=')
        candidate=candidate[:pos]+'const SOLD_EVIDENCE='+encode(extended)+'; // Historical sales: evidence only, never rendered as comps.\nconst SOLD_COMP_POLICY='+encode(policy)+';\n'+candidate[pos:]
    for name,value in [('SOLD_EVIDENCE',extended),('SOLD_COMP_POLICY',policy),('SOLD_DATA',comps),('SOLD_METRICS',metrics)]:
        a,b,old=span(candidate,name)
        if old!=value:candidate=candidate[:a]+encode(value)+candidate[b:]
    for name in ['DATA','RECONCILE']:
        a,b,_=span(html,name);c,d,_=span(candidate,name);assert html[a:b]==candidate[c:d]
    outputs={ROOT/'index.html':candidate,ROOT/f'pulls/dropped_sold_comp_{args.as_of}.csv':legacy.csvtxt(ledger,['FILE','SHA256','ROW','MLS','ADDRESS','REASON','RAW_JSON'])}
    comp_ids={r['id'] for r in comps};retired=[]
    for row in extended:
        if row['id'] in comp_ids:continue
        reason='RESALE_NOT_COMP' if row.get('coh')=='resale' else 'OUTSIDE_365_DAY_COMP_WINDOW' if row['cd']<policy['start'] else 'NOT_IN_CLIENT_COMP_EXPORT'
        retired.append(dict(MLS=row['id'].removeprefix('s'),ADDRESS=row['a'],CLOSE_DATE=row['cd'],REASON=reason,EVIDENCE='Retained in SOLD_EVIDENCE'))
    outputs[ROOT/f'pulls/retired_sold_comps_{args.as_of}.csv']=legacy.csvtxt(retired,['MLS','ADDRESS','CLOSE_DATE','REASON','EVIDENCE'])
    changed=[str(p.relative_to(ROOT)) for p,text in outputs.items() if not p.exists() or p.read_text()!=text]
    report=dict(display_retirements=len(retired),retirement_reasons=dict(Counter(r['REASON'] for r in retired)),profile=profile,counts=dict(counts),excluded=len(ledger),reasons=dict(Counter(r['REASON'] for r in ledger)),comps_before=len(before),comps_after=len(comps),evidence_before=len(evidence),evidence_after=len(extended),legacy_resale_before=sum(r.get('coh')=='resale' for r in before),retired_resale_pins=sum(r.get('coh')=='resale' and r['id'] not in {c['id'] for c in comps} for r in before),reclassified_2024_new_builds=sum(r.get('coh')=='resale' and r['id'] in {c['id'] for c in comps} for r in before),unknown_product=sum(r['prod']=='Unknown' for r in comps),median_price=metrics['overall']['med_price'],changed_files=changed)
    if args.apply:
        for p,text in outputs.items():
            if str(p.relative_to(ROOT)) in changed:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
    if args.output:Path(args.output).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',default='heightsnewconstructionsold365.csv');p.add_argument('--as-of',default='2026-09-10');p.add_argument('--apply',action='store_true');p.add_argument('--output');run(p.parse_args())
