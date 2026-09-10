"""Repeat the market/backfill/browser acceptance checks with a fixed clock."""
import hashlib,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
outputs=[]
for n in range(1,4):
 path=ROOT/'pulls/market_backfill_20260910'/f'validation_{n}.json'
 command=[sys.executable,'-B','tests/backfill_browser.py','--checks','--output',str(path)]
 result=subprocess.run(command,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 path.with_suffix('.log').write_text('$ '+' '.join(command)+'\n'+result.stdout)
 if result.returncode:print(result.stdout);raise RuntimeError(f'Run {n} failed')
 payload=path.read_bytes();outputs.append(payload)
 print(f'BACKFILL RUN {n}: PASS SHA256 {hashlib.sha256(payload).hexdigest()}',flush=True)
assert outputs[0]==outputs[1]==outputs[2]
print('PASS: three market/backfill/display results byte-identical',flush=True)
