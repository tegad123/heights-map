"""Resumable, read-only HCAD review requests. Errors never masquerade as no-match."""
import argparse
import hashlib
import json
from pathlib import Path
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

BASE='https://arcweb.hcad.org/server/rest/services/public/public_query/MapServer/0'

class FetchError(RuntimeError):
    pass


def request_json(url, cache_dir, attempts=4, backoff=2, refresh=False):
    cache_dir=Path(cache_dir);cache_dir.mkdir(parents=True,exist_ok=True)
    key=hashlib.sha256(url.encode()).hexdigest();path=cache_dir/(key+'.json')
    if path.exists() and not refresh:
        saved=json.loads(path.read_text())
        assert saved['status']=='SUCCESS' and saved['url']==url
        return saved['payload']
    for attempt in range(1,attempts+1):
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'HeightsMap-product-review/1.0'})
            with urllib.request.urlopen(req,timeout=35,context=ssl.create_default_context()) as response:
                status=response.status;payload=json.load(response)
            if status!=200 or 'error' in payload:
                raise FetchError(f'HTTP {status}: {payload.get("error")}')
            if '/query?' in url and not isinstance(payload.get('features'),list):
                raise FetchError('HTTP 200 missing feature list')
            if payload.get('exceededTransferLimit') and not payload.get('features'):
                raise FetchError('Truncated response has empty page')
            saved=dict(status='SUCCESS',http_status=status,url=url,
                       retrieved=datetime.now(timezone.utc).isoformat(),payload=payload)
            tmp=path.with_suffix('.part');tmp.write_text(json.dumps(saved));tmp.replace(path)
            return payload
        except (OSError,ValueError,FetchError) as exc:
            with (cache_dir/'errors.jsonl').open('a') as f:
                f.write(json.dumps(dict(url=url,attempt=attempt,error_type=type(exc).__name__,error=str(exc),retrieved=datetime.now(timezone.utc).isoformat()))+'\n')
            if attempt==attempts:raise FetchError(f'Failed after {attempts} attempts: {exc}') from exc
            time.sleep(backoff*2**(attempt-1))


def query(where,cache_dir):
    features=[];offset=0
    while True:
        params=dict(f='json',where=where,outFields='*',returnGeometry='true',outSR='4326',resultOffset=offset,resultRecordCount=1000)
        payload=request_json(BASE+'/query?'+urllib.parse.urlencode(params),cache_dir)
        if 'features' not in payload:raise FetchError('Successful HTTP response missing features')
        batch=payload['features'];features.extend(batch)
        if not payload.get('exceededTransferLimit'):return features
        if not batch:raise FetchError('Truncated response has empty page')
        offset+=len(batch)


def review(cache):
    from collections import Counter
    from product_classification import parcel_evidence
    from permit_pull import extract_data, _norm_ret
    root=Path('pulls/product_residual_20260910')
    cohort=json.loads((root/'cohort.json').read_text())
    rows=extract_data((root/'before.html').read_text())[2]
    fixtures=['pmt_308-e-28th-st-77008','pmt_1125-e-24th-st-77009','pmt_1121-e-24th-st-77009']
    accounts=['0350790000007','0351020630023','0351020630027']
    targets=cohort+[dict(id=i,address=next(r['a'] for r in rows if r['id']==i),reason_code='AUTHORIZED_FIXTURE',parcel_account=a) for i,a in zip(fixtures,accounts)]
    order=['PARCEL_HISTORY_CONFLICT','AUTHORIZED_FIXTURE','DEPTH_BOUNDARY_UNCERTAIN','LEGAL_UNAVAILABLE','ASSEMBLED_REVIEW','UNVERIFIED_PLAT','HELD_TRIAGE']
    targets.sort(key=lambda r:order.index(r['reason_code']))
    import csv
    triage=list(csv.DictReader(Path('notes/clarification_triage.csv').open()))
    result=[]
    for r in targets:
        account=r.get('parcel_account');basis='prior exact-address account'
        if account:
            features=query("HCAD_NUM = '"+account+"'",cache)
        else:
            import re
            address=_norm_ret(r['address'].split(',')[0]);number=re.match(r'^(\d+)\b',address)
            features=query("address LIKE '"+number[1]+" %'",cache) if number else []
            features=[f for f in features if _norm_ret(f['attributes'].get('address',''))==address]
            basis='fresh exact normalized address'
        item=dict(**r,match_basis=basis,match_status='EXACT' if len(features)==1 else 'NO_MATCH' if not features else 'AMBIGUOUS',features=features)
        context_accounts={t['hcad_acct'] for t in triage if t.get('data_id')==r['id'] and t.get('hcad_acct')} if len(features)!=1 else set()
        item['context_records']=[dict(account=a,features=query("HCAD_NUM = '"+a+"'",cache),basis='prior human triage account; identity/parent status unverified') for a in sorted(context_accounts)]
        if len(features)==1 and _norm_ret(features[0]['attributes'].get('address',''))!=_norm_ret(r['address'].split(',')[0]):
            item['match_status']='MISMATCH'
        item['parcel']=parcel_evidence(features[0],source='HCAD full public record; '+basis) if item['match_status']=='EXACT' else {}
        result.append(item)
        (root/'records.json.part').write_text(json.dumps(result,indent=2));(root/'records.json.part').replace(root/'records.json')
        print(r['reason_code'],r['address'],item['match_status'],item['parcel'].get('depth_ft'),flush=True)
    for group in order:
        print('GROUP',group,dict(Counter(r['match_status'] for r in result if r['reason_code']==group)),flush=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache',required=True);ap.add_argument('--probe',action='store_true');ap.add_argument('--review',action='store_true');args=ap.parse_args()
    if args.review:review(args.cache)
    if args.probe:
        meta=request_json(BASE+'?f=pjson',args.cache,refresh=True)
        result=query("HCAD_NUM = '0350790000007'",args.cache)
        assert len(result)==1 and result[0].get('geometry',{}).get('rings')
        print('HCAD REACHABLE: metadata HTTP 200; known-account query 1 feature with polygon')
        print('FIELDS',[(x['name'],x.get('alias')) for x in meta['fields']])
        print('PROBE ATTRIBUTES',result[0]['attributes'])

if __name__=='__main__':main()
