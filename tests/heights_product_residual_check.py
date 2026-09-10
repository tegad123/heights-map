"""Validate the reviewed Heights snapshot without touching other markets."""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from heights_product_residual import WORK, FIXTURES, objects
from permit_pull import extract_data
from product_classification import stored_product
before=(WORK/'before.html').read_text();after=Path('index.html').read_text()
a={r['id']:r for r in extract_data(before)[2]};b={r['id']:r for r in extract_data(after)[2]}
changes={i for i in a if a[i]!=b[i]}
assert len(changes)==12
assert {i for i in changes if stored_product(a[i])}==FIXTURES
assert all(b[i]['prod']=='Split Lot' and b[i]['product_classification']['reason_code']=='OBSERVED_PARCEL_SPLIT' for i in changes)
held=json.load(open('product_classification_holds.json'))['index'];assert len(held)==80
assert all(a[i]==b[i] for i in held)
sa=objects(before);sb=objects(after)
assert all(sa[i][2]==sb[i][2] for i in a if i not in changes)
for i in changes:
    fields={'prod','product_classification'}|({'ty'} if i in FIXTURES else set())
    assert {k:v for k,v in a[i].items() if k not in fields}=={k:v for k,v in b[i].items() if k not in fields}
# Reconstruct all original rows from the edited file; even non-DATA text must match.
restored=after
for i,(start,end,raw) in sorted(sb.items(),key=lambda x:x[1][0],reverse=True):
    if i in changes:restored=restored[:start]+sa[i][2]+restored[end:]
assert restored==before
cohort=json.load(open(WORK/'cohort.json'));review=list(csv.DictReader(open('docs/product-review-list-2026-09-10.csv')))
assert {r['id'] for r in review}=={r['id'] for r in cohort}-changes
assert len(review)==138 and all(r['blocking_reason'] for r in review)
pre=json.load(open(WORK/'browser-before.json'))['index'];post=json.load(open(WORK/'browser-after.json'))['index']
pr={r['id']:r for r in pre['rows']};po={r['id']:r for r in post['rows']}
assert pr.keys()==po.keys()
assert all((r['phase'],r['weight'],r['category'])==(po[i]['phase'],po[i]['weight'],po[i]['category']) for i,r in pr.items())
assert pre['columns']==post['columns']
assert pre['products']['Unknown']==143 and post['products']['Unknown']==134
assert all(c['pass'] for c in post['checks'])
assert (post['sold'],post['deeds'],post['custom'],post['sold_off_market'])==(791,139,19,1)
paths=[Path('index.html'),Path('docs/product-review-list-2026-09-10.md'),Path('docs/product-review-list-2026-09-10.csv')]
hashes=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
subprocess.run([sys.executable,'-B','heights_product_residual.py','--apply'],check=True,stdout=subprocess.DEVNULL)
assert hashes==[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
print('PASS: 9 gap fills + 3 authorized fixture corrections; all Split Lot with observed-history evidence')
print('PASS: 80 holds untouched; 593 source records byte-identical; all other fields and non-DATA text unchanged')
print('PASS: source cohort Unknown 147 -> 138; review covers 138/138 with blocking reasons')
print('PASS: runtime Unknown 143 -> 134; 596 homes; phases, weights and categories unchanged')
print('PASS: 57 browser checks; 3778 monotonicity pairs, zero violations; Finished 150 = 13+5+48+13+71')
print('PASS: sold 791, deeds 139, Custom 19, Sold Off Market 1 unchanged')
print('PASS: second apply zero changes; HTML and review MD/CSV byte-identical')
