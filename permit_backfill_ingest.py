#!/usr/bin/env python3
"""Replay reviewed geocodes through the engine and apply an explicit finals cutoff.

Evidence files are local ignored artifacts. Never changes existing DATA rows.
"""
import argparse,contextlib,csv,io,json
from pathlib import Path
from collections import Counter
from unittest.mock import patch
import permit_pull as pp
ROOT=Path(__file__).resolve().parent

def run(args):
    evidence=ROOT/'pulls/round3'; out=ROOT/'pulls/market_backfill_20260910'; out.mkdir(exist_ok=True)
    cache={r['street']:r['result'] for r in map(json.loads,(evidence/'geocodes.jsonl').read_text().splitlines())}
    cutoffs={r['PROJECT_NO']:r for r in csv.DictReader((evidence/'candidate_cutoffs.csv').open())}
    if args.allston_census:
        matches=json.loads(Path(args.allston_census).read_text())['result']['addressMatches']
        assert len(matches)==1 and matches[0]['matchedAddress']=='742 ALLSTON ST, HOUSTON, TX, 77007'
        point=matches[0]['coordinates']
        cache['742 ALLSTON ST']=dict(status='OK',lat=point['y'],lng=point['x'])
        cutoffs['26018730']=dict(CUTOFF_DATE_USED='',PHASE='exterior')
    html_path=ROOT/'index.html'; html=html_path.read_text(); start,end,data=pp.extract_data(html)
    with patch.object(pp,'hcad_geocode',side_effect=lambda street:cache[street]),contextlib.redirect_stdout(io.StringIO()) as log:
        rows,flagged=pp.ingest([str(ROOT/'pulls'/f'backfill_{z}_20260909.csv') for z in ('77007','77008','77009')],str(html_path),args.min_proj_year,False)
    dropped=list(pp.LAST_DROPPED); selected=[]
    for r in rows:
        proj=r['permits'][0]['proj']; final=cutoffs[proj]['CUTOFF_DATE_USED']
        if final and final<args.finals_since: dropped.append((proj,r['a'],'FINALS_BEFORE_CUTOFF',final))
        else:
            if proj=='26018730':
                r['note']='Census exact address match 2026-09-10; street-interpolated, not an HCAD parcel centroid. HCAD has no matching address.'
            selected.append(r)
    phases=Counter(cutoffs[r['permits'][0]['proj']]['PHASE'] for r in selected)
    outputs={}; candidate=html
    if selected:
        close=end-1; prefix=html[:close]; body=prefix.rstrip(); ws=prefix[len(body):]
        candidate=body+',\n'+',\n'.join(json.dumps(r,separators=(', ',': ')) for r in selected)+ws+html[close:]
        parsed=pp.extract_data(candidate)[2]; assert parsed[:len(data)]==data and len(parsed)==len(data)+len(selected)
        assert candidate[:len(body)]==html[:len(body)]
    outputs[html_path]=candidate
    plist_path=ROOT/'heights_permits.json'; plist=json.loads(plist_path.read_text()); known={r['proj'] for r in plist}
    added=[dict(proj=r['permits'][0]['proj'],address=r['a']) for r in selected if r['permits'][0]['proj'] not in known]
    if added: outputs[plist_path]=json.dumps(plist+added,indent=1)
    insp_path=ROOT/'inspections.json'; insp=json.loads(insp_path.read_text()); original=dict(insp)
    evidence_ins={}
    for p in evidence.glob('candidate_inspections*.json'): evidence_ins.update(json.loads(p.read_text()))
    if args.allston_census:
        evidence_ins.update(json.loads((out/'allston_inspections.json').read_text()))
    for r in selected:
        proj=r['permits'][0]['proj']
        if proj not in insp: insp[proj]=evidence_ins[proj]
    if insp!=original: outputs[insp_path]=json.dumps(insp,indent=2)+'\n'
    changed=[str(p.relative_to(ROOT)) for p,t in outputs.items() if p.read_text()!=t]
    summary=dict(evidence='Reviewed 2026-09-09 HCAD responses replayed through current ingest engine',min_proj_year=args.min_proj_year,finals_since=args.finals_since,before_cutoff=len(rows),selected=len(selected),phase_distribution=dict(phases),flagged=len(flagged),excluded=dict(Counter(r[2] for r in dropped)),changed_files=changed)
    (out/('permit_apply.json' if args.apply else 'permit_preview.json')).write_text(json.dumps(dict(summary=summary,rows=selected),indent=2))
    (out/'permit_replay.log').write_text(log.getvalue())
    pp.write_dropped_ledger(str(out/'dropped_permits.csv'),'heights',dropped)
    if args.apply:
        for p,t in outputs.items():
            if str(p.relative_to(ROOT)) in changed:p.write_text(t)
    print(json.dumps(summary,indent=2)); return summary
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--min-proj-year',type=int,required=True);ap.add_argument('--finals-since',required=True);ap.add_argument('--allston-census');ap.add_argument('--apply',action='store_true');run(ap.parse_args())
