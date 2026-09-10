/* Market evidence is independent of construction certification and its forecast. */
const MARKET_VIEW={ready:false,available:false,properties:{},tracked:[],byMember:new Map(),error:null};
const MARKET_LABELS={active:'Active',pending:'Pending',sold:'Sold',terminated:'Terminated / Expired',no_record:'No Market Record'};
const MARKET_PAGE=document.currentScript.dataset.market;
const PANEL_RESTRUCTURED=MARKET_PAGE==='heights';
function marketMembers(r){return r._twin?[r,r._twin]:[r];}
function marketEvidence(member){
  const evidence=MARKET_VIEW.byMember.get(member.id);
  return evidence||{member:member.id,address:member.a,status:'no_record',current:null,history:[],historical_sales:[]};
}
function marketRows(){
  const rows=[];
  for(const pin of DATA){
    if(inventoryCategory(pin.id))continue;
    const members=marketMembers(pin);
    for(const member of members){const evidence=marketEvidence(member);rows.push({...evidence,pin:pin.id,phase:homePhase(pin.id),product:evidence.current?.product||prodKeyR(member)||'Unknown'});}
    for(let i=members.length;i<UW(pin.id);i++)rows.push({pin:pin.id,member:null,status:'no_record',phase:homePhase(pin.id),product:prodKeyR(pin)||'Unknown'});
  }
  return rows;
}
// Presentation only: never replace stored construction or HAR product fields.
function constructionProductDisplay(member){
  const c=member.product_classification,p=member.prod;
  if(!p||p==='Unknown')return null;
  if(c?.source==='client')return {product:p,source:'client determination'};
  const parcel=c?.evidence?.parcel;
  if(c?.confidence==='high'&&c.product===p&&parcel?.account&&parcel?.source&&Number.isFinite(parcel.depth_ft))return {product:p,source:'parcel-backed construction classification'};
  return null;
}
function marketProductDisplay(member,current){
  const construction=constructionProductDisplay(member);
  return construction?construction.product+' · '+construction.source:(current?.product||'Unknown')+' · provisional (lot size)';
}
function soldProductDisplay(sale){
  if(!PANEL_RESTRUCTURED)return sale.prod||'Unknown';
  const matches=[];
  for(const pin of DATA)for(const member of marketMembers(pin)){
    const e=marketEvidence(member),c=constructionProductDisplay(member);
    if(c&&((e.current?.status==='sold'&&'s'+e.current.mls===sale.id)||e.archive_current?.id===sale.id))matches.push(c);
  }
  if(matches.length===1)return matches[0].product+' · '+matches[0].source;
  return (sale.prod||'Unknown')+' · provisional (lot size)';
}
function marketFacts(r){
  let h='<section class="market-facts" style="font-size:12px;line-height:1.5;margin:12px 0;padding:10px;border:1px solid #67826a;border-radius:8px"><div class="lbl">Market status'+(MARKET_VIEW.asOf?' · '+esc(MARKET_VIEW.asOf):'')+'</div>';
  for(const member of marketMembers(r)){
    const e=marketEvidence(member), c=e.current;
    const displayProduct=PANEL_RESTRUCTURED?constructionProductDisplay(member):null;
    h+='<div data-market-member="'+esc(member.id)+'" style="margin-top:8px"><b>'+esc(member.a)+'</b><br><strong>'+MARKET_LABELS[e.status]+'</strong>';
    if(displayProduct||c)h+='<br>Product: '+esc(PANEL_RESTRUCTURED?marketProductDisplay(member,c):c.product);
    if(c){
      if(c.har_status)h+='<br>HAR status: '+esc(c.har_status);
      h+='<br>MLS '+esc(c.mls)+(PANEL_RESTRUCTURED?'':' · '+esc(c.product));
      h+='<br>Original list price: $'+Number(c.original_list_price).toLocaleString()+' · DOM: '+c.dom+' days';
      if(c.close_date)h+='<br>Closed '+esc(c.close_date)+' · $'+Number(c.close_price).toLocaleString();
      else h+='<br>Observed '+esc(c.as_of)+' · status-change date not supplied';
    }else if(e.archive_current)h+='<br>Closed '+esc(e.archive_current.cd)+' · $'+Number(e.archive_current.cp).toLocaleString()+' · MLS '+esc(e.archive_current.id.slice(1));
    else h+='<br>'+(MARKET_VIEW.available?'No matching evidence in the supplied exports; availability unverified.':'No market-status export supplied for this market.');
    if(e.identity_note)h+='<div class="pmeta">'+esc(e.identity_note)+'</div>';
    if(e.history?.length){
      h+='<details open class="listing-history"><summary>'+(e.ordering_issue?'Listing history · order unverified':'Prior listing history')+' · '+e.history.length+'</summary>';
      for(const old of e.history)h+='<div>'+esc(old.har_status||MARKET_LABELS[old.status])+' · MLS '+esc(old.mls)+' · '+old.dom+' DOM'+(old.close_date?' · closed '+esc(old.close_date):' · event date unavailable')+'</div>';
      h+='</details>';
    }
    if(e.ordering_issue)h+='<div class="pmeta">Multiple '+esc(MARKET_LABELS[e.status])+' listings lack event dates. Latest MLS order requires review; displayed MLS is a reference.</div>';
    if(e.historical_sales?.length)h+='<details><summary>Sale archive · '+e.historical_sales.length+'</summary>'+e.historical_sales.map(s=>'<div>'+esc(s.cd)+' · MLS '+esc(s.id.slice(1))+' · $'+Number(s.cp).toLocaleString()+'</div>').join('')+'</details>';
    h+='</div>';
  }
  h+='<div class="pmeta" style="margin-top:8px">Original list price is not a verified current asking price. Historical event dates are unavailable for non-sold listings.'+(r._twin?' Construction evidence below belongs to the paired project.':'')+'</div></section>';
  return h;
}
const marketOriginalPopup=popupHTML;
popupHTML=function(r){
  const original=marketOriginalPopup(r);if(!MARKET_VIEW.ready)return original;
  const doc=document.createElement('div');doc.innerHTML=original;
  const card=doc.querySelector('.card');if(!card)return original;
  card.querySelectorAll('.lbl').forEach(el=>{const replacements={'Tags':'Prior stored tags · may be stale','Notes':'Stored notes · historical','List price':'Prior stored list price','Listed':'Prior stored listing date'};if(replacements[el.textContent])el.textContent=replacements[el.textContent];});
  const llc=card.querySelector('.llc');if(llc&&/active listing/i.test(llc.textContent))llc.textContent='Property record';
  card.querySelectorAll('.addr').forEach(el=>{if(el.style.color&&/active|pending|off market/i.test(el.textContent))el.remove();});
  if(PANEL_RESTRUCTURED&&!homePhase(r.id)){const badge=card.querySelector('.phasechip');if(badge)badge.textContent='No permit record';}
  const anchor=card.querySelector('.phasehead')||card.querySelector('.grid');
  if(anchor)anchor.insertAdjacentHTML('beforebegin',marketFacts(r));else card.insertAdjacentHTML('beforeend',marketFacts(r));
  return doc.innerHTML;
};
// Finished is a display partition; construction certification and forecasts are unchanged.
const FINISHED_LABELS=PANEL_RESTRUCTURED?{active:'Finished on Market',pending:'Finished Pending',terminated:'Finished Terminated',no_record:'Finished No Market Record'}:{active:'Finished on Market',pending:'Finished Pending',sold:'Finished Sold',terminated:'Finished Terminated',no_record:'Finished, No Market Record'};
const FINISHED_COLORS={active:'#006B4F',pending:'#26A269',sold:'#74C69D',terminated:'#456B58',no_record:'#B7E4C7'};
function finishedPinColor(id){
  if(!MARKET_VIEW.ready||inventoryCategory(id)||!finishedPlacement(byId[id]))return null;
  const statuses=marketMembers(byId[id]).map(m=>marketEvidence(m).status).filter(s=>!PANEL_RESTRUCTURED||s!=='sold');
  if(!PANEL_RESTRUCTURED&&UW(id)>statuses.length)statuses.push('no_record');
  if(!statuses.length)return null;
  const selected=[...activeF].filter(k=>k.startsWith('F:')).map(k=>k.split(':')[1]);
  const status=selected.find(s=>statuses.includes(s))||['sold','pending','active','terminated','no_record'].find(s=>statuses.includes(s));
  return FINISHED_COLORS[status||'no_record'];
}
function otherMarketMatch(tags,key,id){
  if(inventoryCategory(id))return false;
  const phase=homePhase(id),statuses=marketMembers(byId[id]).map(m=>marketEvidence(m).status);
  if(key==='O:pending')return (!PANEL_RESTRUCTURED||!!phase)&&phase!=='complete'&&(statuses.includes('pending')||(tags.includes('pending')&&statuses.includes('no_record')));
  if(key==='O:unverified')return (tags.some(t=>t==='off_market_single'||t==='off_market_split')||(PANEL_RESTRUCTURED&&!phase&&tags.includes('pending')))&&statuses.includes('no_record');
  if(key==='O:unphased')return !phase&&statuses.some(s=>s!=='no_record');
  return false;
}
function finishedPlacement(r){
  if(!r||inventoryCategory(r.id))return false;
  const phase=homePhase(r.id);
  return phase==='complete'||(PANEL_RESTRUCTURED&&!phase&&marketMembers(r).some(m=>marketEvidence(m).status!=='no_record'));
}
function soldInventoryPin(id){
  if(!PANEL_RESTRUCTURED||!MARKET_VIEW.ready||inventoryCategory(id))return false;
  const members=marketMembers(byId[id]);
  return members.length>=UW(id)&&members.every(m=>marketEvidence(m).status==='sold');
}
function finishedRows(){
  return marketRows().filter(r=>finishedPlacement(byId[r.pin])&&(!PANEL_RESTRUCTURED||(r.member!=null&&r.status!=='sold'))).map(r=>({...r,product:typeKeyOf(r.pin)||'Unknown'}));
}

const marketOriginalMatch=matchSel;
matchSel=function(tags,key,id){
  if(key.startsWith('O:'))return otherMarketMatch(tags,key,id);
  const complete=finishedPlacement(byId[id])&&(!PANEL_RESTRUCTURED||marketMembers(byId[id]).some(m=>marketEvidence(m).status!=='sold'));
  if(key==='G:finished')return complete;
  if(key.startsWith('F:')){
    if(!complete)return false;
    const [,status,product]=key.split(':');
    if(product&&(typeKeyOf(id)||'Unknown')!==product)return false;
    const members=marketMembers(byId[id]);
    return members.some(m=>marketEvidence(m).status===status)||(!PANEL_RESTRUCTURED&&status==='no_record'&&UW(id)>members.length);
  }
  if(PANEL_RESTRUCTURED&&soldInventoryPin(id))return false;
  if(key==='G:uc'||key.startsWith('UCT:')||(PANEL_RESTRUCTURED&&key.includes('|')))return !complete&&marketOriginalMatch(tags,key,id);
  return marketOriginalMatch(tags,key,id);
};
function constructionPanelCount(key){
  return DATA.reduce((n,r)=>n+(mById[r.id]&&matchSel(pt(r.id).tags,key,r.id)?UW(r.id):0),0);
}
ucCount=function(){return constructionPanelCount('G:uc');};
ucTypeCount=function(ty){return constructionPanelCount('UCT:'+ty);};
ucNCCount=function(){return constructionPanelCount('UCT:nc');};
function renderFinishedSection(){
  const rows=finishedRows(),root=document.createElement('div');
  root.className='grp'+(collapsed.has('finished')?' col':'');root.dataset.grp='finished';
  let html='<div class="grp-h'+sOn('G:finished')+'" data-col="finished"><span class="chev2">▼</span><span class="mbox'+sOn('G:finished')+'" data-sel="G:finished"></span><span class="gn">Finished</span><span class="ct2">'+rows.length+'</span></div><div class="grp-body">';
  for(const [status,label] of Object.entries(FINISHED_LABELS)){
    const statusRows=rows.filter(r=>r.status===status),key='F:'+status,col='finished:'+status;
    html+='<div class="subg'+(collapsed.has(col)?' col':'')+'"><div class="subg-h'+sOn(key)+'" data-col="'+col+'"><span class="chev2">▼</span><span class="mbox'+sOn(key)+'" data-sel="'+key+'"></span><span class="sw" style="background:'+FINISHED_COLORS[status]+'"></span><span class="sn">'+esc(label)+'</span><span class="ct2">'+statusRows.length+'</span></div><div class="subg-body">';
    const products=TYPES.map(([,label])=>label);
    if(PANEL_RESTRUCTURED||statusRows.some(r=>r.product==='Unknown'))products.push('Unknown');
    for(const product of products){
      const child=key+':'+product,count=statusRows.filter(r=>r.product===product).length;
      html+='<div class="leafrow'+sOn(child)+'" data-sel="'+child+'"><span class="mbox'+sOn(child)+'"></span><span class="sw" style="background:'+FINISHED_COLORS[status]+'"></span><span class="nm">'+esc(product==='Unknown'?'Product type unknown':product)+'</span><span class="ct2">'+count+'</span></div>';
    }
    html+='</div></div>';
  }
  root.innerHTML=html+'</div>';
  root.addEventListener('click',ev=>{
    const select=ev.target.closest('[data-sel]'),header=ev.target.closest('[data-col]');
    if(select){const key=select.dataset.sel;activeF.has(key)?activeF.delete(key):activeF.add(key);renderLegend();refresh();}
    else if(header){const key=header.dataset.col;collapsed.has(key)?collapsed.delete(key):collapsed.add(key);renderLegend();}
  });
  return root;
}
// Heights inventory placement; other markets retain their existing panel layout.
const marketOriginalLegend=renderLegend;
renderLegend=function(){
  marketOriginalLegend();
  const legend=document.getElementById('legend');
  legend.querySelector('[data-grp="mkt"]')?.remove();
  legend.querySelectorAll('[data-grp="uc"] .leafrow[data-sel$="|complete"]').forEach(row=>row.remove());
  legend.querySelector('[data-grp="uc"]').after(renderFinishedSection());
  // Preserve the existing Single Lot overlapping filter; Heights places it under construction.
  // Move its original node so its existing selection handlers remain intact.
  const onMarket=legend.querySelector('.leafrow[data-sel="active_single|onmkt"]');
  const other=legend.querySelector('[data-grp="other"]');
  legend.querySelectorAll('.leafrow[data-sel$="|onmkt"]').forEach(row=>row.remove());
  if(onMarket&&other){
    onMarket.title='Existing Single Lot on-market/building filter; overlaps construction phases';
    (PANEL_RESTRUCTURED?legend.querySelector('[data-grp="uc"]'):other).querySelector('.grp-body').appendChild(onMarket);

  }
  if(other){
    other.querySelectorAll('[data-sel="L:pending"],[data-sel="L:off_market_single"],[data-sel="L:off_market_split"]').forEach(e=>e.remove());
    const review=other.querySelector('[data-sel="L:needs_clarification"] .nm');
    if(review)review.textContent='Flagged for review';
    const rows=PANEL_RESTRUCTURED?[['O:pending','Pending, not Complete','#d6336c'],['O:unverified','Market status unverified','#8a8f98']]:[['O:pending','Pending, not Complete','#d6336c'],['O:unverified','Off market, status unverified','#8a8f98'],['O:unphased','Market evidence, no construction phase','#67826a']];
    for(const [key,label,color] of rows){
      const row=document.createElement('div');row.className='leafrow'+sOn(key);row.dataset.sel=key;
      row.innerHTML='<span class="mbox'+sOn(key)+'"></span><span class="sw" style="background:'+color+'"></span><span class="nm">'+esc(label)+'</span><span class="ct2">'+constructionPanelCount(key)+'</span>';
      row.addEventListener('click',()=>{activeF.has(key)?activeF.delete(key):activeF.add(key);renderLegend();refresh();});
      (PANEL_RESTRUCTURED&&key==='O:pending'?legend.querySelector('[data-grp="uc"]'):other).querySelector('.grp-body').appendChild(row);
    }
    if(PANEL_RESTRUCTURED){const foot=document.createElement('div');foot.className='pmeta';foot.style.padding='8px 12px';foot.textContent='Listed and pending rows overlap the construction phases above; do not add these flags to the phase total.';legend.querySelector('[data-grp="uc"] .grp-body').appendChild(foot);}
    const keys=[...other.querySelectorAll('.leafrow')].map(r=>r.dataset.sel);
    const count=DATA.reduce((n,r)=>n+(mById[r.id]&&keys.some(k=>matchSel(pt(r.id).tags,k,r.id))?UW(r.id):0),0);
    other.querySelector('.grp-h > .ct2').textContent=count;
    other.querySelector('.grp-h').title='Distinct represented homes; overlapping rows count once';
  }
  const unknown=legend.querySelector('[data-sel="UCT:nc"] .nm');if(unknown)unknown.textContent='Product type unknown';
  // Repaint after evidence arrives, shared edits merge, or a Finished filter changes.
  for(const marker of markers)marker.setStyle(mkStyle(marker._rec.id));
};
function activeMarketCounts(){
  const active=marketRows().filter(r=>r.member!=null&&r.status==='active');
  return {finished:active.filter(r=>finishedPlacement(byId[r.pin])).length,construction:active.filter(r=>!finishedPlacement(byId[r.pin])).length};
}
function marketSnapshot(months=12){
  const forecast=comingOnline(months),ids=new Set(forecast.homes.map(r=>r.id));
  const excluded=marketRows().filter(r=>ids.has(r.pin)&&r.status==='terminated');
  return {construction:forecast.count,terminated:excluded.length,available:forecast.count-excluded.length};
}
function marketSnapshotNote(snapshot){
  return snapshot.terminated+' terminated homes excluded from snapshot ('+snapshot.construction+' in construction forecast)';
}
const marketOriginalSupply=renderSupplyCard;
renderSupplyCard=function(){
  marketOriginalSupply();if(!MARKET_VIEW.ready||!MARKET_VIEW.available)return;
  const snapshot=marketSnapshot(),big=document.getElementById('sc-big'),foot=document.getElementById('sc-foot');
  if(big)big.textContent=snapshot.available;
  if(foot)foot.textContent+=' · '+marketSnapshotNote(snapshot);
};

if(PANEL_RESTRUCTURED){
  const originalPipeline=inPipeline;
  inPipeline=function(r){return !soldInventoryPin(r.id)&&originalPipeline(r);};
  comboCount=function(a,b){return constructionPanelCount(a+'|'+b);};
  const originalSoldFiltered=soldFiltered;
  soldFiltered=function(){
    const inventorySales=new Set(finishedRows().flatMap(r=>(r.historical_sales||[]).map(s=>s.id)));
    return originalSoldFiltered().filter(r=>!inventorySales.has(r.id));
  };
  const originalRefresh=refresh;
  refresh=function(){
    originalRefresh();
    let removed=0;
    for(const marker of markers)if(soldInventoryPin(marker._rec.id)&&layer.hasLayer(marker)){
      removed+=marker._rec.units||1;layer.removeLayer(marker);
    }
    if(removed){const shown=document.getElementById('shown');shown.textContent=(Number(shown.textContent.replace(/,/g,''))-removed).toLocaleString();}
  };
}

// Authoritative MLS identity determinations move evidence, never duplicate it.
function applyClientMarketIdentities(){
  for(const pin of DATA)for(const member of marketMembers(pin)){
    const decision=member.market_identity;
    if(!decision||decision.source!=='client')continue;
    const target=MARKET_VIEW.byMember.get(member.id);
    const donors=[...MARKET_VIEW.byMember.values()].filter(e=>e.current?.mls===decision.mls);
    if(!target||donors.length!==1||donors[0]===target)continue;
    const donor=donors[0];
    if(target.current)continue; // Conflicting evidence requires explicit review.
    const current=donor.current;
    donor.current=null;donor.status='no_record';
    donor.identity_note='Current MLS '+decision.mls+' belongs to unit A by client determination. Any unsuffixed historical listing remains identity-unverified.';
    target.current=current;target.status=current.status;
    target.identity_note=decision.reason;
  }
}

async function loadMarketStatus(){
  try{
    if(MARKET_PAGE==='heights'){
      const response=await fetch('heights_market_status.data.json',{cache:'no-store'});if(!response.ok)throw Error('HTTP '+response.status);
      const data=await response.json();if(!data.tracked||!data.properties)throw Error('Invalid market snapshot');
      Object.assign(MARKET_VIEW,{available:true,asOf:data.as_of,properties:data.properties,tracked:data.tracked,coverage:data.coverage,byMember:new Map(data.tracked.map(r=>[r.member,r]))});
    }
    if(PANEL_RESTRUCTURED)applyClientMarketIdentities();
    MARKET_VIEW.ready=true;
  }catch(e){MARKET_VIEW.error='Market evidence unavailable: '+e.message;}
  renderLegend();refresh();renderSupplyCard();
}
loadMarketStatus();
