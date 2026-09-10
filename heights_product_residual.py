"""Apply reviewed Heights-only split evidence and publish the residual ledger.

Input is the durable full-record fetch from hcad_product_review.py --review.
Default is report-only. --apply permits nine gap fills and the three named
fixture corrections, with byte-preserving edits to individual JSON fields.
"""
import argparse
import collections
import csv
import json
from pathlib import Path
from permit_pull import extract_data
from product_classification import classify, context_signals, stored_product, parcel_evidence
ROOT=Path(__file__).resolve().parent
WORK=ROOT/'pulls/product_residual_20260910'
FIXTURES={'pmt_308-e-28th-st-77008','pmt_1125-e-24th-st-77009','pmt_1121-e-24th-st-77009'}

def objects(html):
    start,end,rows=extract_data(html)
    # Locate each object through the JSON decoder, preserving all whitespace.
    decoder=json.JSONDecoder();pos=start+1;result={}
    while pos<end:
        while html[pos].isspace() or html[pos]==',':pos+=1
        if html[pos]==']':break
        row,stop=decoder.raw_decode(html,pos);result[row['id']]=(pos,stop,html[pos:stop]);pos=stop
    assert len(result)==len(rows)
    return result

def patch_fields(raw,fields):
    decoder=json.JSONDecoder();pos=1;spans={}
    while True:
        while raw[pos].isspace() or raw[pos]==',':pos+=1
        if raw[pos]=='}':break
        key,stop=decoder.raw_decode(raw,pos);pos=stop
        while raw[pos].isspace() or raw[pos]==':':pos+=1
        _,stop=decoder.raw_decode(raw,pos);spans[key]=(pos,stop);pos=stop
    edits=[];extra={}
    for key,value in fields.items():
        if key in spans:edits.append((*spans[key],json.dumps(value,ensure_ascii=False)))
        else:extra[key]=value
    for start,end,value in sorted(edits,reverse=True):raw=raw[:start]+value+raw[end:]
    if extra:raw=raw[:-1]+', '+json.dumps(extra,ensure_ascii=False)[1:]
    assert all(json.loads(raw)[k]==v for k,v in fields.items())
    return raw

def main(apply=False):
    before=(WORK/'before.html').read_text();rows=extract_data(before)[2];byid={r['id']:r for r in rows}
    records=json.loads((WORK/'records.json').read_text());assert len(records)==150
    holds=json.loads((ROOT/'product_classification_holds.json').read_text())['index'];assert len(holds)==80
    signals=context_signals(rows);events=json.loads((ROOT/'refresh/parcel_events.json').read_text())
    prior={r['id']:r for r in json.loads((ROOT/'pulls/product_classification_20260910/decisions.json').read_text())['index']}
    changes={};review=[];all_details=[]
    needs={
      'DEPTH_BOUNDARY_UNCERTAIN':'Recorded dimensions/access plat distinguishing side-by-side lots from shared access; values and two-unit evidence do not settle access.',
      'LEGAL_UNAVAILABLE':'Verified HCAD account or recorded plat for this exact home; successful address query found no exact match.',
      'ASSEMBLED_REVIEW':'Human confirmation of house count and access on assembled original lots; legal lot count does not equal home count.',
      'UNVERIFIED_PLAT':'Original plat/replat and access verification; subdivision name alone does not prove subdivision of a parent parcel.',
      'HELD_TRIAGE':'Prior human hold: requires explicit re-review; no classification authorized this session.'}
    for r in records:
        group=r['reason_code'];parcel=r['parcel'];sig=signals[r['id']]
        # Held records are not passed to the classifier at all.
        decision=None if group=='HELD_TRIAGE' else classify(legal=parcel.get('legal',''),parcel=parcel,observed_split_override=True,**sig)
        eligible=group in ('PARCEL_HISTORY_CONFLICT','AUTHORIZED_FIXTURE','DEPTH_BOUNDARY_UNCERTAIN','LEGAL_UNAVAILABLE')
        if eligible and decision['product']!='Unknown':
            assert decision['confidence']=='high'
            assert not stored_product(byid[r['id']]) or r['id'] in FIXTURES
            fields={'prod':decision['product'],'product_classification':decision}
            if r['id'] in FIXTURES:fields['ty']='active_split'
            changes[r['id']]=fields
        attrs=r['features'][0]['attributes'] if len(r['features'])==1 else {}
        history=[e for e in events if parcel.get('account') in e['child_accts']]
        if group=='HELD_TRIAGE':recommendation='Not evaluated: human hold; '+holds[r['id']]['bucket']
        elif group=='ASSEMBLED_REVIEW':recommendation='Review Single Lot possibility; assembled legal lots alone cannot confirm one home'
        elif group=='UNVERIFIED_PLAT':recommendation='Unverified v9 candidate: '+decision['candidate']+'; retain Unknown pending plat/access review'
        elif r['id'] in changes:recommendation=decision['product']
        else:recommendation='Retain Unknown'
        context=[]
        for f in (r['features'] if len(r['features'])!=1 else []) + [f for c in r.get('context_records',[]) for f in c['features']]:
            pe=parcel_evidence(f,source='HCAD unverified contextual parcel');a=f['attributes']
            if any(c['parcel']['account']==pe['account'] for c in context):continue
            context.append(dict(parcel=pe,land_value=a.get('land_val'),improvement_value=a.get('impr_val'),history=[e for e in events if pe.get('account') in e['child_accts'] or pe.get('account') in e['parent_accts']]))
        oldparcel=prior.get(r['id'],{}).get('decision',{}).get('evidence',{}).get('parcel',{})
        row=dict(id=r['id'],address=r['address'],group=group,account=parcel.get('account',''),match_status=r['match_status'],
          legal=parcel.get('legal','Unavailable'),depth_ft=parcel.get('depth_ft',''),width_ft=parcel.get('width_ft',''),area_sf=parcel.get('area_sf',''),
          unit_letters=' / '.join(__import__('re').findall(r'\b(?:St|Dr|Rd|Ln) ([A-Z])\b',r['address'])),unit_count=sig['units'],master_size=sig['master_size'] or '',master_source=sig['master_source'],
          parcel_history=json.dumps(history,sort_keys=True),improvement_value=attrs.get('impr_val','Unavailable'),land_value=attrs.get('land_val','Unavailable'),
          recommendation=recommendation,blocking_reason='' if r['id'] in changes else needs[group],
          evidence_source='HCAD public/public_query/MapServer/0 full attributes + WGS84 polygon; observed history refresh/parcel_events.json',
          dimensions_source='EPSG:2278 minimum rotated rectangle, not recorded lot dimensions',
          prior_geometry=bool(oldparcel.get('depth_ft')),prior_legal=bool(oldparcel.get('legal')),prior_history=bool(oldparcel.get('parcel_history')),
          current_geometry=bool(parcel.get('depth_ft')),current_legal=bool(parcel.get('legal')),current_history=bool(history),
          unverified_context=json.dumps(context,sort_keys=True),context_queries=json.dumps(r.get('context_records',[]),default=str) if not context else 'See unverified_context')
        if group=='HELD_TRIAGE':row['blocking_reason']+=' '+holds[r['id']]['reason']
        all_details.append(row)
        if r['id'] not in changes:review.append(row)
    assert FIXTURES<=changes.keys() and all(changes[i]['prod']=='Split Lot' for i in FIXTURES)
    assert not (changes.keys() & holds.keys())
    assert len(changes)==12 and len(review)==138
    # Patch DATA only; all other text, fields and records remain byte-identical.
    spans=objects(before);after=before
    for rid,(start,end,raw) in sorted(spans.items(),key=lambda x:x[1][0],reverse=True):
        if rid in changes:after=after[:start]+patch_fields(raw,changes[rid])+after[end:]
    newrows={r['id']:r for r in extract_data(after)[2]};newspans=objects(after)
    for rid,row in byid.items():
        if rid not in changes:assert newspans[rid][2]==spans[rid][2]
        else:
            assert {k:v for k,v in row.items() if k not in changes[rid]}=={k:v for k,v in newrows[rid].items() if k not in changes[rid]}
    assert len(newrows)==len(rows)
    current=(ROOT/'index.html').read_text();assert current in (before,after),'Concurrent HTML edits: abort'
    if apply and current!=after:(ROOT/'index.html').write_text(after)
    rank={'DEPTH_BOUNDARY_UNCERTAIN':0,'ASSEMBLED_REVIEW':1,'UNVERIFIED_PLAT':2,'LEGAL_UNAVAILABLE':3,'HELD_TRIAGE':4}
    review.sort(key=lambda r:(rank[r['group']],not r['current_geometry'],r['address']))
    out=ROOT/'docs/product-review-list-2026-09-10.csv'
    with out.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(review[0]),lineterminator='\n');writer.writeheader();writer.writerows(review)
    counts=dict(collections.Counter(r['group'] for r in review))
    held=[r for r in review if r['group']=='HELD_TRIAGE']
    availability={k:sum(r[k] for r in held) for k in ('prior_geometry','prior_legal','prior_history','current_geometry','current_legal','current_history')}
    availability['new_geometry']=sum(r['current_geometry'] and not r['prior_geometry'] for r in held)
    availability['new_legal']=sum(r['current_legal'] and not r['prior_legal'] for r in held)
    availability['held_with_unverified_context']=sum(r['unverified_context']!='[]' for r in held)
    availability['unverified_context_with_history']=sum(any(c['history'] for c in json.loads(r['unverified_context'])) for r in held)
    availability['new_history']=sum(r['current_history'] and not r['prior_history'] for r in held)
    lines=['# Heights product review — 2026-09-10','',
      'Source cohort: 147 Unknown → 138. Nine gaps filled as Split Lot. Three explicitly authorized stored Single Lot fixtures corrected separately; all other stored labels and all 80 triage holds are unchanged.',
      '', 'The live/shared baseline has four held records already labeled Single Lot by remote edits: its 143 Unknown become 134. This list preserves all 138 unresolved source-cohort records, including those four human overrides.',
      '', 'HCAD reachability: metadata HTTP 200; account 0350790000007 returned one polygon and full legal/land/improvement attributes. Four sandbox DNS attempts failed and were logged separately; the outside-sandbox fetch succeeded. Successful responses are persisted individually; failures are never stored as zero features.',
      '', 'Dimensions below are measured geometry proxies, not deed/plat dimensions. Values are the current HCAD service values (valuation year not supplied by this layer); zero improvement value is not proof of no completed house. History is an observed polygon SPLIT/ASSEMBLY between cached HCAD vintages, not a title history or a newly fetched deed record. No lot-area threshold was used.',
      '', '## Applied observed-split decisions','', '| Address | Account | Depth ft | Prior group | Evidence |','|---|---|---:|---|---|']
    for r in all_details:
        if r['id'] in changes:lines.append(f"| {r['address']} | {r['account']} | {r['depth_ft']} | {r['group']} | {r['parcel_history']} |")
    lines+=['','## Residual groups','',str(counts),'','Held evidence availability versus the prior classification audit: `'+json.dumps(availability,sort_keys=True)+'`. The earlier human triage CSV did not record polygon payloads, so these comparisons do not assert what its reviewers personally saw. Held composition: 46 held Single candidates, four held Split candidates, 30 ambiguous. All 80 remain untouched.','',
      'Twelve boundary cases retain their ±0.01 ft abstention. Ten have observed split history; this confirms subdivision but does not independently establish common access or resolve the depth measurement. None has a three-or-more unit/master signal. 742 Allston has no exact match in the successful full-house-number query. Assembled and unverified-plat groups receive recommendations only.','',
      '## Per-record review (closest to decidable first)','']
    for n,r in enumerate(review,1):
        lines += [f"### {n}. {r['address']}",'',f"- ID: `{r['id']}`; group: **{r['group']}**; HCAD: `{r['account'] or 'unresolved'}`; match: {r['match_status']}.",
          f"- Legal: {r['legal']}. Measured depth × width: {r['depth_ft'] or 'unavailable'} × {r['width_ft'] or 'unavailable'} ft; area: {r['area_sf'] or 'unavailable'} sf.",
          f"- Unit letters: {r['unit_letters'] or 'none'}; verified unit count: {r['unit_count']}; master size: {r['master_size'] or 'unavailable'} (project {r['master_source']}).",
          f"- Land value: {r['land_value']}; improvement value: {r['improvement_value']}. Observed parcel history: `{r['parcel_history']}`.",
          f"- Unverified alternative/parent context (never used for assignment): `{r['unverified_context']}`.",
          f"- Recommendation: {r['recommendation']}. Blocking reason: {r['blocking_reason']}",'']
    (ROOT/'docs/product-review-list-2026-09-10.md').write_text('\n'.join(lines).rstrip()+'\n')
    summary=dict(applied=apply,changes={i:v['prod'] for i,v in changes.items()},gap_fills=9,authorized_corrections=3,unknown_before=147,unknown_after=138,residual=counts,held_availability=availability,unchanged_records=len(rows)-len(changes))
    (WORK/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');main(ap.parse_args().apply)
