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
// Only the explicitly approved Complete-and-Active subset belongs in the phase list.
function finishedOnMarketMembers(id){
  const pin=byId[id];
  return pin&&!inventoryCategory(id)&&homePhase(id)==='complete'
    ?marketMembers(pin).filter(member=>marketEvidence(member).status==='active'):[];
}
const marketOriginalMatch=matchSel;
matchSel=function(tags,key,id){
  if(key.endsWith('|finished_on_market'))return typeKeyOf(id)===TY2K[key.split('|')[0]]&&finishedOnMarketMembers(id).length>0;
  return marketOriginalMatch(tags,key,id);
};
// Further Layers hierarchy changes require explicit user approval.
const marketOriginalLegend=renderLegend;
renderLegend=function(){
  marketOriginalLegend();
  const legend=document.getElementById('legend');
  legend.querySelector('[data-grp="mkt"]')?.remove();
  for(const [ty] of TYPES){
    const complete=legend.querySelector('.leafrow[data-sel="'+ty+'|complete"]');
    if(!complete)continue;
    const key=ty+'|finished_on_market';
    const count=DATA.filter(r=>typeKeyOf(r.id)===TY2K[ty]).reduce((n,r)=>n+finishedOnMarketMembers(r.id).length,0);
    const row=document.createElement('div');
    row.className='leafrow'+sOn(key);row.dataset.sel=key;
    row.title='Complete construction and currently Active; included in Complete above';
    row.innerHTML='<span class="mbox'+sOn(key)+'"></span><span class="sw" style="background:'+GROUP_C.act+'"></span><span class="nm">Finished on Market</span><span class="ct2">'+count+'</span>';
    row.addEventListener('click',ev=>{ev.stopPropagation();activeF.has(key)?activeF.delete(key):activeF.add(key);renderLegend();refresh();});
    complete.after(row);
  }
  // Preserve the existing 14-home Single Lot overlapping filter, in Other.
  // Move its original node so its existing selection handlers remain intact.
  const onMarket=legend.querySelector('.leafrow[data-sel="active_single|onmkt"]');
  const other=legend.querySelector('[data-grp="other"]');
  legend.querySelectorAll('.leafrow[data-sel$="|onmkt"]').forEach(row=>row.remove());
  if(onMarket&&other){
    onMarket.title='Existing Single Lot on-market/building filter; overlaps construction phases';
    other.querySelector('.grp-body').appendChild(onMarket);
    other.querySelector('.grp-h > .ct2').textContent=other.querySelectorAll('.grp-body > .leafrow').length;
  }
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
