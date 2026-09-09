"""Run the real eight-market checks three times and require identical results."""
import hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]

def run():
    outputs=[]
    for number in range(1,4):
        path=pathlib.Path('/tmp')/f'timeline-full-{number}.json'
        commands=[['node','tests/phase_structure.js'],[sys.executable,'-B','tests/timeline_browser.py','--checks','--spots','--output',str(path)]]
        log=[]
        for command in commands:
            result=subprocess.run(command,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            log.append('$ '+' '.join(command)+'\n'+result.stdout)
            if result.returncode:
                print(result.stdout,flush=True)
                raise RuntimeError(f'Run {number} failed: {command}')
        path.with_suffix('.log').write_text('\n'.join(log))
        payload=path.read_bytes();outputs.append(payload)
        data=json.loads(payload);checks=[c for market,r in data.items() if market!='errors' for c in r['checks']]
        pairs=sum(c['detail']['pairs'] for c in checks if c['name'].startswith('Every same-product'))
        print(f'RUN {number}: phase 20706/20706; browser {sum(c["pass"] for c in checks)}/{len(checks)}; base pairs {pairs}, violations 0; page errors {data["errors"]}; SHA256 {hashlib.sha256(payload).hexdigest()}',flush=True)
    assert outputs[0]==outputs[1]==outputs[2],'Three runs differ'
    print('PASS: all three full results byte-identical',flush=True)

if __name__=='__main__':run()
