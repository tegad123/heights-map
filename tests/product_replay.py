"""Invoke original v9 parity and the real importer on the saved 175 arrivals.
Only temporary HTML and the requested evidence output directory are written.
"""
import argparse
import collections
import contextlib
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import permit_pull
from product_classification import context_signals,parcel_evidence


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence',type=Path,required=True);args=ap.parse_args();out=args.evidence
    baseline=json.loads((out/'baseline.json').read_text());matches=json.loads((out/'parcel_matches.json').read_text())
    inputs=[]
    for market,capture in baseline.items():
        signals=context_signals(capture['source'])
        for row in capture['source']:
            fs=matches[market].get(row['id'],[])
            p=parcel_evidence(fs[0]) if len(fs)==1 else {}
            inputs.append(dict(address=row['a'],legal_desc=p.get('legal','').replace('|',' '),
                               depth_ft=p.get('depth_ft') or '',ms_of=signals[row['id']]['master_size'] or ''))
    src=out/'parity_input.csv'
    with src.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(inputs[0]));w.writeheader();w.writerows(inputs)
    subprocess.run([sys.executable,'-B',str(ROOT/'classify_v9.py'),str(src)],check=True,capture_output=True)
    subprocess.run([sys.executable,'-B',str(ROOT/'product_classification.py'),str(src),'--out',str(out/'extracted_v9.csv')],check=True,capture_output=True)
    a=(out/'heights_review_v9.csv').read_bytes();b=(out/'extracted_v9.csv').read_bytes();assert a==b
    print('V9 BYTE PARITY:',len(inputs),'inputs;',len(a),'bytes; SHA256',hashlib.sha256(a).hexdigest())
    arrivals=json.loads((ROOT/'pulls/market_backfill_20260910/permit_first_apply.json').read_text())['rows'];ids={r['id'] for r in arrivals};assert len(ids)==175
    source=(ROOT/'index.html').read_text();start,end,data=permit_pull.extract_data(source)
    # Retain raw object strings; no DATA serialization, even in the fixture.
    decoder=json.JSONDecoder();pos=start+1;kept=[]
    for row in data:
        while source[pos].isspace() or source[pos]==',':pos+=1
        obj,stop=decoder.raw_decode(source,pos)
        if row['id'] not in ids:kept.append(source[pos:stop])
        pos=stop
    fixture=source[:start+1]+',\n'.join(kept)+source[end-1:]
    geocodes={};csvrows=[]
    for r in arrivals:
        p=r['permits'][0];address=permit_pull.hcad_address(r['a'].split(',')[0]);fs=matches['index'][r['id']]
        parcel=parcel_evidence(fs[0]) if len(fs)==1 else {'source':'previously verified Census coordinate; no HCAD parcel','legal':''}
        geocodes[address]=dict(status='OK',lat=r['lat'],lng=r['lng'],parcel=parcel,legal=parcel.get('legal',''))
        csvrows.append(dict(PROJECT_NO=p['proj'],PERMIT_DESC='Building Pmt',OWNER_OCCUPANT=p['owner'],Address=address+' '+r['a'][-5:],PROJECT_DESC=p['desc'],CURRENT_VALUATION=p['val'],PERMIT_TYPE=p['ptype']))
    with tempfile.TemporaryDirectory() as td:
        html=Path(td)/'index.html';html.write_text(fixture);cp=Path(td)/'arrivals.csv'
        with cp.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=permit_pull.HDR);w.writeheader();w.writerows(csvrows)
        log=io.StringIO()
        with patch.object(permit_pull,'hcad_geocode',side_effect=lambda a:geocodes[a]),contextlib.redirect_stdout(log):
            rows,flags=permit_pull.ingest([str(cp)],str(html),24,False)
        assert html.read_text()==fixture
        assert {r['id'] for r in rows}==ids,(len(rows),flags)
    (out/'permit_replay.log').write_text(log.getvalue());(out/'permit_replay.json').write_text(json.dumps(rows,indent=2)+'\n')
    decisions=json.loads((out/'decisions.json').read_text());expected={r['id']:r['decision']['product'] for r in decisions['index']}
    assert all(r['prod']==expected[r['id']] for r in rows)
    print('IMPORTER REPLAY: 175/175; no live writes;',dict(collections.Counter(r['prod'] for r in rows)))
    print('CONFIDENCE:',dict(collections.Counter(r['product_classification']['confidence'] for r in rows)))
    print('UNKNOWN REASONS:',dict(collections.Counter(r['product_classification']['reason_code'] for r in rows if r['prod']=='Unknown')))


if __name__=='__main__':main()
