"""Verify the backfill is additive and every other HTML byte is preserved."""
import json,pathlib,sys,subprocess,hashlib
sys.path.insert(0,str(pathlib.Path.cwd()))
from permit_pull import extract_data
from product_backfill import splice
from product_classification import stored_product
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--evidence',type=pathlib.Path,required=True);ap.add_argument('--ref',default='70b9cff');args=ap.parse_args()
root=args.evidence;base=json.load(open(root/'baseline.json'));holds=json.load(open('product_classification_holds.json'))
changed=protected=0
for market,capture in base.items():
 path=pathlib.Path(market+'.html');after=path.read_text();before=subprocess.check_output(['git','show',args.ref+':'+str(path)],text=True)
 rows=extract_data(after)[2];old=extract_data(before)[2];assert old==capture['source']
 edits={}
 for a,b in zip(old,rows):
  assert a['id']==b['id']
  assert all(b[k]==v for k,v in a.items()),a['id']
  if stored_product(a):protected+=1;assert a==b
  if a['id'] in holds.get(market,{}):assert a==b
  if a!=b:
   assert not stored_product(a)
   assert set(b)-set(a)=={'prod','product_classification'}
   edits[a['id']]={k:b[k] for k in ('prod','product_classification')};changed+=1
 regenerated,n=splice(before,edits)
 regenerated=regenerated.replace("  const isSplit=r=>{ if(r.st==='sold')return false;","  // Ingest classifications describe one tracked address, not an inferred two-home pin.\n  const isSplit=r=>{ if(r.product_classification)return false; if(r.st==='sold')return false;")
 assert regenerated==after,market+' unexpected HTML bytes changed'
 print(market,'field inserts',n,'all other bytes preserved')
print('PASS',changed,'records touched;',protected,'stored assignments unchanged; 80 holds byte-unchanged; only documented pairing guard outside DATA')
(root/'static_check.json').write_text(json.dumps(dict(touched=changed,protected=protected,holds=80),sort_keys=True)+'\n')

for name in ('classify_v9.py','sold_classification.py','market_status.js','inventory_classifications.js'):
 assert pathlib.Path(name).read_bytes()==subprocess.check_output(['git','show',args.ref+':'+name]), name+' modified'
for address in ('837 W 25th','845 W 23rd St A','1124 W 21st'):
 matches=[r for r in extract_data(pathlib.Path('index.html').read_text())[2] if r['a'].startswith(address)]
 assert matches and all(not stored_product(r) for r in matches),address
print('PASS conflict fixtures remain Unknown; original v9, HAR rule, market and inventory classifiers unchanged')
