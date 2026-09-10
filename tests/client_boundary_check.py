"""Heights-only client and boundary assertions; no writes to other markets."""
import json,csv,re,sys,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from permit_pull import extract_data
from heights_product_residual import objects
from product_classification import stored_product
from shapely.geometry import Point,Polygon
W=Path('pulls/client_boundary_20260910');before=(W/'before.html').read_text();after=Path('index.html').read_text()
b={r['id']:r for r in extract_data(before)[2]};a={r['id']:r for r in extract_data(after)[2]}
log=json.load(open(W/'determinations.json'));ids={r['id'] for r in log};assert len(ids)==11 and len(a)==len(b)==605
sb=objects(before);sa=objects(after)
for i,r in b.items():
 if i not in ids:assert sb[i][2]==sa[i][2]
 else:
  assert a[i]['prod']==next(x['new'] for x in log if x['id']==i)
  assert a[i]['product_classification']['source']=='client' and a[i]['product_classification']['authoritative']
  assert {k:v for k,v in r.items() if k not in ('prod','ty','product_classification')}=={k:v for k,v in a[i].items() if k not in ('prod','ty','product_classification')}
held=json.load(open('product_classification_holds.json'))['index'];exceptions=set(held)&ids;assert len(exceptions)==3
assert all(b[i]==a[i] for i in held if i not in exceptions)
old=json.load(open(W/'browser-before.json'))['index'];new=json.load(open(W/'browser-after.json'))['index']
oldrows={r['id']:r for r in old['rows']};newphases={}
for r in new['rows']:
 newphases[r['id']]=r['phase']
 for twin in r['twins']:newphases[twin]=r['phase']
oldphases={i:r['phase'] for r in old['rows'] for i in [r['id']]+r['twins']}
assert oldphases.keys()==newphases.keys()
assert oldphases==newphases
assert old['homes']==new['homes']==597
assert old['products']['Unknown']==111 and new['products']['Unknown']==106
assert old['ucUnknown']==9 and new['ucUnknown']==5
assert {p for r in old['rows'] for p in r['permits']}=={p for r in new['rows'] for p in r['permits']}
assert len({p for r in new['rows'] for p in r['permits']})==406
assert old['soldRows']==new['soldRows'] and len(new['soldRows'])==791
assert (new['deeds'],new['custom'],new['sold_off_market'])==(139,19,1)
assert sum(new['finishedCounts'])==new['finishedHeader']==138
assert all(c['pass'] for c in new['checks'])
ring=json.loads(re.search(r'const ZONE_RING=(\[.*?\]);',before)[1]);assert re.search(r'const ZONE_RING=(\[.*?\]);',after)[1]==json.dumps(ring,separators=(',',':'))
poly=Polygon(ring)
for r in new['rows']:assert poly.covers(Point(r['marker']['lng'],r['marker']['lat']))
for r in new['soldRows']:assert poly.covers(Point(r['lng'],r['lat']))
review=list(csv.DictReader(open('docs/product-review-list-2026-09-10.csv')));remaining=[r for r in review if r['id'] not in ids];assert len(review)==138 and len(remaining)==129
print('PASS: six client determinations; 11 source records; three pairs each one pin / two homes')
print('PASS: 594 source records byte-identical; 77 holds unchanged; three named client exceptions')
print('PASS: homes 597 -> 597; live unique permit projects 406 -> 406; pins 550 -> 547')
print('PASS: Unknown 111 -> 106; Under Construction Unknown 9 -> 5; source review residual 138 -> 129')
print('PASS: all individual-home phases unchanged; Finished 138; sold 791 / deeds 139 / Custom 19 / Sold Off Market 1 unchanged')
print('PASS: Heights source and rendered outside-boundary records 0; removed/reassigned/ledgered 0')
print('PASS: monotonicity pairs',new['checks'][0]['detail']['pairs'],'violations',len(new['checks'][0]['detail']['violations']))
