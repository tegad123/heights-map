"""Read-only reproduction of the pre-repair matcher against the captured baseline."""
import argparse
import inspect
import json
import math
import re
import statistics
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from active_ingest import address_key
from market_status_ingest import load_inputs
from deed_ingest import span
from market_linkage import distance


def run(output=None):
    html=(ROOT/'index.html').read_text();source=span(html,'DATA')[2]
    runtime=json.loads((ROOT/'docs/linkage-runtime-baseline-2026-09-09.json').read_text())['runtime']
    records,_,summaries=load_inputs(html)
    members=[(p,m) for p in runtime['raw'] for m in [p]+([p['_twin']] if p.get('_twin') else [])]
    phases={r['id']:r['phase'] for r in runtime['rows']}
    results=[]
    for r in records:
        matches=[(p,m) for p,m in members if address_key(m['a'])==address_key(r['address'])]
        source_matches=[p for p in source if address_key(p['a'])==address_key(r['address'])]
        near=sorted([(distance(r,m),p,m) for p,m in members if m.get('lat') and m.get('lng')],key=lambda x:x[0])
        within=[dict(meters=round(d,2),pin=p['id'],member=m['id'],address=m['a']) for d,p,m in near if d<=25]
        category='LINKED' if len(matches)==1 else 'AMBIGUOUS_ADDRESS' if matches else 'HIDDEN_LEGACY_SOLD' if source_matches and all(x.get('st')=='sold' for x in source_matches) else 'OTHER_HIDDEN' if source_matches else 'CONFLICTING_NEARBY_IDENTITY' if within else 'NOT_TRACKED'
        results.append(dict(file=r['source_file'],row=r['source_row'],mls=r['mls'],address=r['address'],status=r['status'],category=category,
                            matches=[dict(pin=p['id'],member=m['id'],phase=phases[p['id']]) for p,m in matches],
                            within25=within,nearest_meters=round(near[0][0],2),source_matches=[p['id'] for p in source_matches]))
    unlinked=[r for r in results if not r['matches']]
    summary=dict(rows=len(results),new_lot_matches=sum(s['classification_matches'] for s in summaries[-4:]),
                 taxonomy=dict(Counter(r['category'] for r in results)),
                 prior=dict(rows=119,linked=sum(bool(r['matches']) for r in results[:119]),with_phase=sum(any(m['phase'] for m in r['matches']) for r in results[:119])),
                 source_records=len(source),runtime_pins=len(runtime['raw']),runtime_members=len(members),mls_records=sum(any('mls' in k.lower() and bool(v) for k,v in p.items()) for p in source),parcel_records=sum(any(re.search('parcel|apn|account',k,re.I) and bool(v) for k,v in p.items()) for p in source),
                 proximity=dict(single=sum(len(r['within25'])==1 for r in unlinked),ambiguous=sum(len(r['within25'])>1 for r in unlinked),
                                nearest_distribution=dict(Counter('0-25m' if r['nearest_meters']<=25 else '25-50m' if r['nearest_meters']<=50 else '50-100m' if r['nearest_meters']<=100 else '>100m' for r in unlinked))),
                 active_mls_sets_equal={r['mls'] for r in records[:119] if r['status']=='active'}=={r['mls'] for r in records[225:]},
                 terminated_active_overlap=len({r['mls'] for r in records if r['status']=='terminated'}&{r['mls'] for r in records if r['status']=='active'}),
                 terminated_years=dict(Counter(r['year_built'] for r in records if r['status']=='terminated')),terminated_median_dom=statistics.median(r['dom'] for r in records if r['status']=='terminated'))
    assert summary['taxonomy']==dict(LINKED=230,HIDDEN_LEGACY_SOLD=22,CONFLICTING_NEARBY_IDENTITY=10,NOT_TRACKED=22)
    print(json.dumps(summary,indent=2))
    if output:Path(output).write_text(json.dumps(dict(summary=summary,rows=results,old_normalizer=inspect.getsource(address_key),old_join="lookup[address_key(member['a'])].append((pin, member))\nmatches = lookup[rec['address_key']]"),indent=2)+'\n')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output');args=ap.parse_args();run(args.output)
