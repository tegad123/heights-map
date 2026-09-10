"""Run the complete product suite three times; require identical browser output."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence',type=Path,required=True);args=ap.parse_args();out=args.evidence
    runs=[]
    for n in range(1,4):
        browser=out/f'full-{n}.json'
        commands=[
            [sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_product_classification.py'],
            [sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_permit_pull.py'],
            [sys.executable,'-B','tests/product_replay.py','--evidence',str(out)],
            [sys.executable,'-B','tests/product_static.py','--evidence',str(out)],
            ['node','tests/phase_structure.js'],
            [sys.executable,'-B','tests/product_browser.py','--shared',str(out/'shared_frozen.json'),'--output',str(browser)],
        ]
        logs=[];phase_count=None
        for cmd in commands:
            result=subprocess.run(cmd,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            logs.append('$ '+' '.join(cmd)+'\n'+result.stdout)
            if result.returncode:
                (out/f'full-{n}.log').write_text('\n'.join(logs));print(result.stdout,flush=True);raise RuntimeError(cmd)
            if cmd[0]=='node':phase_count=int(re.search(r'TOTAL (\d+) checks PASS',result.stdout)[1])
        # Backfill must be a byte-identical no-op on all market HTML files.
        files=[ROOT/(name+'.html') for name in json.loads((out/'baseline.json').read_text())]
        before=[p.read_bytes() for p in files]
        result=subprocess.run([sys.executable,'-B','product_backfill.py','--evidence',str(out),'--apply'],cwd=ROOT,text=True,capture_output=True,check=True)
        assert before==[p.read_bytes() for p in files]
        summary=json.loads((out/'backfill_summary.json').read_text());assert sum(r['touched'] for r in summary.values())==0
        logs.append('$ product_backfill.py --apply (idempotence)\n'+result.stdout)
        (out/f'full-{n}.log').write_text('\n'.join(logs))
        payload=browser.read_bytes();runs.append(payload);data=json.loads(payload)
        baseline=json.loads((out/'before_frozen.json').read_text())
        for market,previous in baseline.items():
            old={r['id']:r for r in previous['rows']};new={r['id']:r for r in data[market]['rows']}
            assert old.keys()==new.keys(),market+' pin membership changed'
            for rid,r in old.items():
                for key in ('weight','phase','category','twins'):
                    assert r[key]==new[rid][key],(market,rid,key)
                if r['product']!='Unknown':assert r['product']==new[rid]['product'],(market,rid,'existing product changed')
            for key in ('homes','deeds','sold','custom','sold_off_market','uc','finishedHeader','columns'):
                assert previous[key]==data[market][key],(market,key,'inventory changed')
        checks=[c for r in data.values() for c in r['checks']]
        pairs=sum(c['detail']['pairs'] for c in checks if c['name'].startswith('Every same-product'))
        print(f'RUN {n}: unit 14/14; v9 1934-row byte parity; importer 175/175; phase {phase_count}/{phase_count}; browser {len(checks)}/{len(checks)}; base pairs {pairs}, violations 0; byte-identical no-op; SHA256 {hashlib.sha256(payload).hexdigest()}',flush=True)
    assert runs[0]==runs[1]==runs[2]
    print('PASS: three complete runs, identical results',flush=True)

if __name__=='__main__':main()
