/* Market evidence is independent of construction certification and its forecast. */
const MARKET_VIEW={ready:false,available:false,properties:{},tracked:[],byMember:new Map(),error:null};
const MARKET_LABELS={active:'Active',pending:'Pending',sold:'Sold',terminated:'Terminated / Expired',no_record:'No Market Record'};
const MARKET_PAGE=document.currentScript.dataset.market;
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
function marketFacts(r){
  let h='<section class="market-facts" style="font-size:12px;line-height:1.5;margin:12px 0;padding:10px;border:1px solid #67826a;border-radius:8px"><div class="lbl">Market status'+(MARKET_VIEW.asOf?' · '+esc(MARKET_VIEW.asOf):'')+'</div>';
  for(const member of marketMembers(r)){
    const e=marketEvidence(member), c=e.current;
    h+='<div data-market-member="'+esc(member.id)+'" style="margin-top:8px"><b>'+esc(member.a)+'</b><br><strong>'+MARKET_LABELS[e.status]+'</strong>';
    if(c){
      if(c.har_status)h+='<br>HAR status: '+esc(c.har_status);
      h+='<br>MLS '+esc(c.mls)+' · '+esc(c.product);
      h+='<br>Original list price: $'+Number(c.original_list_price).toLocaleString()+' · DOM: '+c.dom+' days';
      if(c.close_date)h+='<br>Closed '+esc(c.close_date)+' · $'+Number(c.close_price).toLocaleString();
      else h+='<br>Observed '+esc(c.as_of)+' · status-change date not supplied';
    }else if(e.archive_current)h+='<br>Closed '+esc(e.archive_current.cd)+' · $'+Number(e.archive_current.cp).toLocaleString()+' · MLS '+esc(e.archive_current.id.slice(1));
    else h+='<br>'+(MARKET_VIEW.available?'No matching evidence in the supplied exports; availability unverified.':'No market-status export supplied for this market.');
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
  const anchor=card.querySelector('.phasehead')||card.querySelector('.grid');
  if(anchor)anchor.insertAdjacentHTML('beforebegin',marketFacts(r));else card.insertAdjacentHTML('beforeend',marketFacts(r));
  return doc.innerHTML;
};
// Finished is a display partition; construction certification and forecasts are unchanged.
const FINISHED_LABELS={active:'Finished on Market',pending:'Finished Pending',sold:'Finished Sold',terminated:'Finished Terminated',no_record:'Finished, No Market Record'};
const FINISHED_COLORS={active:'#006B4F',pending:'#26A269',sold:'#74C69D',terminated:'#456B58',no_record:'#B7E4C7'};
function finishedPinColor(id){
  if(!MARKET_VIEW.ready||inventoryCategory(id)||homePhase(id)!=='complete')return null;
  const statuses=marketMembers(byId[id]).map(m=>marketEvidence(m).status);
  if(UW(id)>statuses.length)statuses.push('no_record');
  const selected=[...activeF].filter(k=>k.startsWith('F:')).map(k=>k.split(':')[1]);
  const status=selected.find(s=>statuses.includes(s))||['sold','pending','active','terminated','no_record'].find(s=>statuses.includes(s));
  return FINISHED_COLORS[status||'no_record'];
}
function otherMarketMatch(tags,key,id){
  if(inventoryCategory(id))return false;
  const phase=homePhase(id),statuses=marketMembers(byId[id]).map(m=>marketEvidence(m).status);
  if(key==='O:pending')return phase!=='complete'&&(statuses.includes('pending')||(tags.includes('pending')&&statuses.includes('no_record')));
  if(key==='O:unverified')return tags.some(t=>t==='off_market_single'||t==='off_market_split')&&statuses.includes('no_record');
  if(key==='O:unphased')return !phase&&statuses.some(s=>s!=='no_record');
  return false;
}
function finishedRows(){
  return marketRows().filter(r=>r.phase==='complete').map(r=>({...r,product:typeKeyOf(r.pin)||'Unknown'}));
}
const marketOriginalMatch=matchSel;
matchSel=function(tags,key,id){
  if(key.startsWith('O:'))return otherMarketMatch(tags,key,id);
  const complete=!inventoryCategory(id)&&homePhase(id)==='complete';
  if(key==='G:finished')return complete;
  if(key.startsWith('F:')){
    if(!complete)return false;
    const [,status,product]=key.split(':');
    if(product&&(typeKeyOf(id)||'Unknown')!==product)return false;
    const members=marketMembers(byId[id]);
    return members.some(m=>marketEvidence(m).status===status)||(status==='no_record'&&UW(id)>members.length);
  }
  if(key==='G:uc'||key.startsWith('UCT:'))return !complete&&marketOriginalMatch(tags,key,id);
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
    if(statusRows.some(r=>r.product==='Unknown'))products.push('Unknown');
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
// Other cleanup approved with the 2026-09-10 market/backfill audit.
const marketOriginalLegend=renderLegend;
renderLegend=function(){
  marketOriginalLegend();
  const legend=document.getElementById('legend');
  legend.querySelector('[data-grp="mkt"]')?.remove();
  legend.querySelectorAll('[data-grp="uc"] .leafrow[data-sel$="|complete"]').forEach(row=>row.remove());
  legend.querySelector('[data-grp="uc"]').after(renderFinishedSection());
  // Preserve the existing 14-home Single Lot overlapping filter, in Other.
  // Move its original node so its existing selection handlers remain intact.
  const onMarket=legend.querySelector('.leafrow[data-sel="active_single|onmkt"]');
  const other=legend.querySelector('[data-grp="other"]');
  legend.querySelectorAll('.leafrow[data-sel$="|onmkt"]').forEach(row=>row.remove());
  if(onMarket&&other){
    onMarket.title='Existing Single Lot on-market/building filter; overlaps construction phases';
    other.querySelector('.grp-body').appendChild(onMarket);

  }
  if(other){
    other.querySelectorAll('[data-sel="L:pending"],[data-sel="L:off_market_single"],[data-sel="L:off_market_split"]').forEach(e=>e.remove());
    const review=other.querySelector('[data-sel="L:needs_clarification"] .nm');
    if(review)review.textContent='Flagged for review';
    const rows=[['O:pending','Pending, not Complete','#d6336c'],['O:unverified','Off market, status unverified','#8a8f98'],['O:unphased','Market evidence, no construction phase','#67826a']];
    for(const [key,label,color] of rows){
      const row=document.createElement('div');row.className='leafrow'+sOn(key);row.dataset.sel=key;
      row.innerHTML='<span class="mbox'+sOn(key)+'"></span><span class="sw" style="background:'+color+'"></span><span class="nm">'+esc(label)+'</span><span class="ct2">'+constructionPanelCount(key)+'</span>';
      row.addEventListener('click',()=>{activeF.has(key)?activeF.delete(key):activeF.add(key);renderLegend();refresh();});
      other.querySelector('.grp-body').appendChild(row);
    }
    const keys=[...other.querySelectorAll('.leafrow')].map(r=>r.dataset.sel);
    const count=DATA.reduce((n,r)=>n+(mById[r.id]&&keys.some(k=>matchSel(pt(r.id).tags,k,r.id))?UW(r.id):0),0);
    other.querySelector('.grp-h > .ct2').textContent=count;
    other.querySelector('.grp-h').title='Distinct represented homes; overlapping rows count once';
  }
  const unknown=legend.querySelector('[data-sel="UCT:nc"] .nm');if(unknown)unknown.textContent='Product type unknown';
  // Repaint after evidence arrives, shared edits merge, or a Finished filter changes.
  for(const marker of markers)marker.setStyle(mkStyle(marker._rec.id));
};
function marketSnapshot(){
  const forecast=comingOnline(12),ids=new Set(forecast.homes.map(r=>r.id));
  const excluded=marketRows().filter(r=>ids.has(r.pin)&&r.status==='terminated');
  return {construction:forecast.count,terminated:excluded.length,available:forecast.count-excluded.length};
}
const marketOriginalSupply=renderSupplyCard;
renderSupplyCard=function(){
  marketOriginalSupply();if(!MARKET_VIEW.ready||!MARKET_VIEW.available)return;
  const snapshot=marketSnapshot(),big=document.getElementById('sc-big'),foot=document.getElementById('sc-foot');
  if(big)big.textContent=snapshot.available;
  if(foot)foot.textContent+=' · '+snapshot.terminated+' terminated homes excluded from snapshot ('+snapshot.construction+' in construction forecast)';
};
async function loadMarketStatus(){
  try{
    if(MARKET_PAGE==='heights'){
      const response=await fetch('heights_market_status.data.json',{cache:'no-store'});if(!response.ok)throw Error('HTTP '+response.status);
      const data=await response.json();if(!data.tracked||!data.properties)throw Error('Invalid market snapshot');
      Object.assign(MARKET_VIEW,{available:true,asOf:data.as_of,properties:data.properties,tracked:data.tracked,coverage:data.coverage,byMember:new Map(data.tracked.map(r=>[r.member,r]))});
    }
    MARKET_VIEW.ready=true;
  }catch(e){MARKET_VIEW.error='Market evidence unavailable: '+e.message;}
  renderLegend();refresh();renderSupplyCard();
}
loadMarketStatus();
