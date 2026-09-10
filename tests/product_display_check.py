"""Heights product presentation provenance; stored fields must not change."""
import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];live='--live' in sys.argv;shared=json.load(open('/tmp/product_shared.json'))
with sync_playwright() as pw:
 b=pw.chromium.launch();p=b.new_page()
 def route(r):
  if r.request.method!='GET':r.abort()
  elif 'script.google' in r.request.url:r.fulfill(json=shared)
  elif not live and r.request.url.split('?')[0].endswith('/index.html'):r.fulfill(body=(ROOT/'index.html').read_text(),content_type='text/html')
  elif not live and r.request.url.split('?')[0].endswith('/market_status.js'):r.fulfill(body=(ROOT/'market_status.js').read_text(),content_type='application/javascript')
  else:r.continue_()
 p.route('**/*',route);p.goto('https://tangerine-sorbet-eca5f5.netlify.app/index.html?product-display=20260910',wait_until='networkidle');p.wait_for_function('INSP_LOADED && MARKET_VIEW.ready')
 result=p.evaluate('''()=>{
 const before=JSON.stringify({DATA,SOLD_DATA,tracked:MARKET_VIEW.tracked});
 const counts={marketGeometry:0,marketClient:0,marketProvisional:0,geometryLabelConflicts:0,geometryCardsWithoutCurrentListing:0,soldGeometry:0,soldClient:0,soldProvisional:0};
 const affected=[];
 for(const pin of DATA)for(const m of marketMembers(pin)){
  const e=marketEvidence(m),c=constructionProductDisplay(m);
  if(e.current){const k=c?(c.source==='client determination'?'marketClient':'marketGeometry'):'marketProvisional';counts[k]++;if(c&&c.source!=='client determination'&&c.product!==e.current.product)counts.geometryLabelConflicts++;
   const html=marketFacts(pin);if(c&&c.source!=='client determination') {const doc=document.createElement('div');doc.innerHTML=html;const block=doc.querySelector('[data-market-member="'+m.id+'"]');if(!block.textContent.includes(marketProductDisplay(m,e.current)))throw Error(m.id);}
   affected.push({kind:'market',id:m.id,address:m.a,display:marketProductDisplay(m,e.current)});
  }else if(c&&c.source!=='client determination')counts.geometryCardsWithoutCurrentListing++;
 }
 for(const r of SOLD_DATA){const display=soldProductDisplay(r);counts[display.includes('provisional')?'soldProvisional':display.includes('client determination')?'soldClient':'soldGeometry']++;if(!soldCardHTML(r,false).includes(esc(display)))throw Error(r.id);affected.push({kind:'sold',id:r.id,address:r.a,display});}
 if(before!==JSON.stringify({DATA,SOLD_DATA,tracked:MARKET_VIEW.tracked}))throw Error('stored values changed');
 const member=DATA.flatMap(r=>marketMembers(r)).find(m=>m.id==='pmt_606-link-rd-f-77009');const label=marketProductDisplay(member,{product:'Split Lot'});if(!label.startsWith('Common Driveway')||label.includes('Split Lot'))throw Error(label);
 return {counts,affected,probe:label,unchanged:true,finished:finishedRows().reduce((n,r)=>{n[r.status]=(n[r.status]||0)+1;return n;},{})};}''')
 Path('/tmp/product-display-audit.json').write_text(json.dumps(result,indent=2));print(('LIVE ' if live else '')+'PASS',json.dumps({k:v for k,v in result.items() if k!='affected'}));b.close()
