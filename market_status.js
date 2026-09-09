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
      h+='<br>MLS '+esc(c.mls)+' · '+esc(c.product);
      h+='<br>Original list price: $'+Number(c.original_list_price).toLocaleString()+' · DOM: '+c.dom+' days';
      if(c.close_date)h+='<br>Closed '+esc(c.close_date)+' · $'+Number(c.close_price).toLocaleString();
      else h+='<br>Observed '+esc(c.as_of)+' · status-change date not supplied';
    }else if(e.archive_current)h+='<br>Closed '+esc(e.archive_current.cd)+' · $'+Number(e.archive_current.cp).toLocaleString()+' · MLS '+esc(e.archive_current.id.slice(1));
    else h+='<br>'+(MARKET_VIEW.available?'No matching evidence in the supplied exports; availability unverified.':'No market-status export supplied for this market.');
    if(e.history?.length){
      h+='<details open class="listing-history"><summary>'+(e.ordering_issue?'Listing history · order unverified':'Prior listing history')+' · '+e.history.length+'</summary>';
      for(const old of e.history)h+='<div>'+MARKET_LABELS[old.status]+' · MLS '+esc(old.mls)+' · '+old.dom+' DOM'+(old.close_date?' · closed '+esc(old.close_date):' · event date unavailable')+'</div>';
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
const marketOriginalMatch=matchSel;
matchSel=function(tags,key,id){
  if(!key.startsWith('MS:'))return marketOriginalMatch(tags,key,id);
  const [,status,product,phase]=key.split(':');
  return marketRows().some(r=>r.pin===id&&r.status===status&&(product==='all'||r.product===product)&&(!phase||r.phase===phase));
};
function marketButtons(rows,phase,scopeProduct){
  let h='';
  for(const [status,label] of Object.entries(MARKET_LABELS)){
    const group=rows.filter(r=>r.status===status),key='MS:'+status+':'+(scopeProduct||'all')+(phase?':'+phase:'');
    h+='<button type="button" data-market-filter="'+key+'" aria-pressed="'+activeF.has(key)+'" class="leafrow" style="width:100%;border:0;background:transparent;color:inherit;text-align:left"><span class="nm">'+label+'</span><span class="ct2">'+group.length+'</span></button>';
    for(const product of (phase?[]:['Single Lot','Split Lot','Common Driveway','Unknown'])){
      const count=group.filter(r=>r.product===product).length;if(!count&&!['Single Lot','Split Lot'].includes(product))continue;
      const k='MS:'+status+':'+product+(phase?':'+phase:'');
      h+='<button type="button" data-market-filter="'+k+'" aria-pressed="'+activeF.has(k)+'" class="leafrow" style="width:100%;padding-left:28px;border:0;background:transparent;color:inherit;text-align:left;font-size:11px"><span class="nm">'+product+'</span><span class="ct2">'+count+'</span></button>';
    }
  }
  return h;
}
function renderMarketLegend(){
  const el=document.getElementById('legend');if(!el)return;
  el.querySelectorAll('[data-market-axis],[data-market-complete]').forEach(e=>e.remove());
  // Supersede legacy market summaries based on stored tags, preserving construction rows.
  el.querySelector('[data-grp="mkt"]')?.remove();
  el.querySelectorAll('.leafrow[data-sel$="|onmkt"]').forEach(e=>e.remove());
  const rows=marketRows();
  let h='<div class="grp" data-market-axis><div class="grp-h"><span class="gn">Market Status</span><span class="ct2">'+rows.length+'</span></div>';
  if(!MARKET_VIEW.ready)h+='<div class="pmeta">'+esc(MARKET_VIEW.error||'Loading market evidence…')+'</div>';
  else h+=marketButtons(rows)+'<div class="pmeta" style="padding:8px 12px;font-size:10px;line-height:1.4;color:var(--muted)">'+(MARKET_VIEW.available?'HAR '+esc(MARKET_VIEW.asOf)+' · Counts are represented homes. Paired pins may overlap. Export coverage is limited; No Market Record is unverified.':'No market-status export supplied. No Market Record does not mean unlisted.')+'</div>';
  el.insertAdjacentHTML('afterbegin',h+'</div>');
  el.querySelectorAll('.leafrow[data-sel$="|complete"]').forEach(leaf=>{
    const ty=leaf.dataset.sel.split('|')[0],product=TY2K[ty];
    leaf.insertAdjacentHTML('afterend','<div data-market-complete>'+marketButtons(rows.filter(r=>r.phase==='complete'&&r.product===product),'complete',product)+'</div>');
  });
  el.querySelectorAll('[data-market-filter]').forEach(button=>button.addEventListener('click',()=>{const k=button.dataset.marketFilter;activeF.has(k)?activeF.delete(k):activeF.add(k);renderLegend();refresh();}));
}
const marketOriginalLegend=renderLegend;
renderLegend=function(){marketOriginalLegend();renderMarketLegend();};
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
