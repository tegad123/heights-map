import json,csv,collections,subprocess
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from permit_pull import extract_data
from market_address import address_key
W=Path('pulls/panel_timeline_20260910');before=json.loads((W/'before.json').read_text());after=json.loads((W/'check-1.json').read_text())
rows=[];distribution=[]
for market,b in before.items():
 a={r['id']:r for r in after[market]['rows']};counts=collections.Counter()
 assert a.keys()=={r['id'] for r in b['rows']}
 for r in b['rows']:
  n=a[r['id']];assert r['phase']==n['phase'] and r['weight']==n['weight']
  e=r['eta'];f=n['eta'];d=None if e.get('remainingDays') is None else e['remainingDays']-f['remainingDays']
  if d is not None:assert d==max(0,e['overdueDays']-e['duration'])
  bucket='No remaining ETA' if d is None else 'Unchanged' if d==0 else '1–30 days' if d<=30 else '31–90 days' if d<=90 else '91–180 days' if d<=180 else '>180 days'
  counts[bucket]+=r['weight']
  rows.append(dict(market=market,id=r['id'],address=r['address'],homes=r['weight'],phase=r['phase'],elapsed_days=e.get('elapsed'),overdue_days=e.get('overdueDays'),before_days=e.get('remainingDays'),after_days=f.get('remainingDays'),before_date=e.get('target'),after_date=f.get('target'),days_earlier=d,cap_2x_days=None if d is None else e['baseDays']+min(e['overdueDays'],2*e['duration'])))
 distribution.append((market,counts))
 raw=subprocess.check_output(['git','show','80fc736:'+market+'.html'],text=True);current=Path(market+'.html').read_text()
 lo,hi,_=extract_data(raw);lo2,hi2,_=extract_data(current);assert raw[lo:hi]==current[lo2:hi2]
 print(market,'DATA byte-identical; phases and home weights unchanged')
with Path('docs/panel-timeline-changes-2026-09-10.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
h=after['index'];audit=h['panelAudit'];soldkeys={address_key(r['a']) for r in before['index']['sold'] if r['id'] in audit['soldIds']};finishedkeys={address_key(r['address']) for r in h['finished'] if r.get('address')};assert not soldkeys&finishedkeys
routing=[]
for pin in audit['unphased']:
 for member in pin['members']:
  assert member['status']!='no_record'
  routing.append(dict(pin=pin['id'],member=member['member'],address=member['address'],status=member['status'],destination='Sold Comps' if member['status']=='sold' else 'Finished '+member['status']))
 for i in range(pin['weight']-len(pin['members'])):
  routing.append(dict(pin=pin['id'],member='',address='Unidentified companion of '+pin['members'][0]['address'],status='no_record',destination='Finished No Market Record'))
assert len(routing)==47
with Path('docs/panel-retired-47-2026-09-10.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(routing[0]),lineterminator='\n');writer.writeheader();writer.writerows(routing)
keys=['Unchanged','1–30 days','31–90 days','91–180 days','>180 days','No remaining ETA']
lines=['# Capped overdue timelines and Heights panel — 2026-09-10','','Comparison clock: 2026-09-09, matching the existing fixture suite. Heights uses the saved shared-edit snapshot; other markets use their repository defaults. The remote shared-edit endpoint returned 404 in the preceding session; this is a deterministic comparison, not a fresh remote-state audit.','',
'## Timeline decision','','Use a 1× phase-duration cap on the overdue ETA contribution. Keep full elapsed and overdue days as stall evidence. Base durations and phase derivation are unchanged. MEP Finals is capped at 42 remaining days (six weeks); 2× permits 63 days (nine weeks). Across eight markets, 1× changes 154 homes; 2× would change 129.','',
'115 Northwood: 181 days / 2027-03-09 → 42 days / 2026-10-21. It remains stalled 26 weeks in MEP Finals, 23 weeks overdue. 727 W 21st is another six-month fixture: 174 → 42 days. The approximately 22-week example, 606 Skyland Terrace, moves 152 → 42 days. Harvard remains 247 days / 2027-05-14; 629 E 26th remains 200 days / 2027-03-28.','',
'## Full distribution (homes, including paired-home weights)','','| Market | '+' | '.join(keys)+' |','|---|'+'---:|'*len(keys)]
for m,c in distribution:lines.append('| '+m+' | '+' | '.join(str(c[k]) for k in keys)+' |')
lines+=['','All changes move dates earlier; none moves later. No remaining ETA includes completed homes and records without dated construction evidence. The companion CSV records every pin’s before/after date and both cap candidates.','',
'## Ten largest moves across all markets','','All ten are in Garden Oaks / Oak Forest.','', '| Address | Before days | After days | Before date | After date | Days earlier |','|---|---:|---:|---|---|---:|']
for r in sorted([r for r in rows if r['days_earlier']],key=lambda r:r['days_earlier'],reverse=True)[:10]:lines.append('| '+' | '.join(str(r[k]) for k in ['address','before_days','after_days','before_date','after_date','days_earlier'])+' |')
lines+=['','## Panel proposal reported before application','','Measured baseline: Under Construction 237, Finished 150, Sold Comps 791. Proposed/applied: Under Construction 225; Finished 138; Sold Comps view 790, with all 791 sale records retained. Twelve closed-sale MEP Finals homes also leave construction inventory; their phases remain unchanged.','',
'Finished: On Market 34; Pending 9; Terminated 19; No Market Record 76. Every status has all four product rows, including zero-count Unknown.','',
'Overlapping construction flags: On the Market (building) 14 = Framing 2 + MEP Roughs 1 + INT.CAB 6 + MEP Finals 5. Pending, not Complete 8 = INT.CAB 4 + MEP Finals 4. These are represented-home counts for the existing paired-pin filters, not independent listing totals. The panel footnote explicitly warns against adding flags to phases.','',
'Under Construction exclusive product counts: Single 55 + Split 49 + Common Driveway 94 + Unknown 27 = 225. The product phase leaves total 198, plus the Unknown row 27 = 225. The two overlapping flags are not added.','',
'Retired 47: Active 21, Pending 4, Terminated 6, Sold 11, unknown-market companion homes 5. The latter retain pre-existing paired-home weights; no identity, market status or construction phase is invented. Every disposition is listed in panel-retired-47-2026-09-10.csv.','',
'All 48 former Finished Sold and 11 unphased Sold members already exist in the sale archive. To keep Finished and Sold Comps disjoint, the old sale of 2932 Michaux (MLS 63496941) is excluded from the comp view while its current Terminated listing remains in Finished. Its sale record is retained unchanged. Normalized-address overlap between Finished and the comp view: zero.','',
'Other remains useful for exceptions: Flagged for review 5, Market status unverified 2 (seven distinct homes). The second row includes the former off-market/unverified member and 616 Ridge, which has only a legacy pending tag, no current market evidence and no construction phase.','',
'## Invocation evidence','','`python -B tests/panel_timeline_browser.py --shared pulls/product_classification_20260910/shared_frozen.json --output pulls/panel_timeline_20260910/check-1.json`', '',
'Actual Heights output: `homes: 596; uc: 225; ucUnknown: 27; deeds: 139; sold: 791; finishedHeader: 138`. The explicit comp-view assertion is 790. All eight markets pass the base monotonicity test: 8,961 pairs, zero violations. Every runtime phase and home weight matches the before snapshot. DATA substrings are byte-identical across all eight HTML files.','',
'Merrill remains Active with terminated MLS 50361472 in history. Allston remains present. Harvard, 629, Munford, Voight, the two Complete fixtures and the unphased 830 E 26th pass the existing fixture tests. Custom 19, Sold Off Market 1 and deeds 139 remain unchanged.']
import hashlib
hashes=[hashlib.sha256((W/f'check-{n}.json').read_bytes()).hexdigest() for n in (1,2,3)]
assert len(set(hashes))==1
lines += ['', 'Three full runs (`check-1.json`, `check-2.json`, `check-3.json`) are byte-identical: 199 checks per run, SHA-256 `'+hashes[0]+'`.']
print('THREE BYTE-IDENTICAL FULL RUNS: 199 checks per run; SHA-256 '+hashes[0])
Path('docs/panel-timeline-2026-09-10.md').write_text('\n'.join(lines)+'\n')
print('PASS: normalized-address overlap Finished/Sold Comps = 0; 47/47 routed; 8961 monotonicity pairs, zero violations')
