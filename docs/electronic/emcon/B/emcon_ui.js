// EMCON_B Commit D — profile-derived controls mounted inside the existing MAP_E menu.
const EMCON_B_ALL_RADIATION_MEMORY=new Map();
const EMCON_B_CATEGORY_LABEL=Object.freeze({AIR_SEARCH:'대공 탐색',SURFACE_SEARCH:'수상 탐색',NAV:'항해 레이더',FIRE_CONTROL:'사격 통제',ECM:'전자전 방사'});
const EMCON_B_REASON_LABEL=Object.freeze({CATEGORY_RADIATE:'범주 방사 허용',CATEGORY_SILENT:'범주 침묵',OVERRIDE_RADIATE:'장비 강제 방사',OVERRIDE_SILENT:'장비 강제 침묵',MASTER_SILENT:'전체 레이더 침묵',NETWORK_SILENT:'함대 공동 침묵',EQUIPMENT_DISABLED:'기존 장비 OFF',DAMAGE:'손상',SHIP_OFFLINE:'함정 장비 정지',REGISTERED_INACTIVE:'비활성 등록',NOT_INSTALLED:'미장착'});
function emconUiOwnerB(){return (typeof fleetOwnerG==='function'?fleetOwnerG():null)??ACTIVE_SHIP_RUNTIME;}
function emconUiOwnerLabelB(r){return (r===ACTIVE_SHIP_RUNTIME?'자함':r.role==='ALLY'&&r.faction==='FRIENDLY'?'아군함':r.role==='NEUTRAL'?'중립함':'비우호 함정')+' · '+r.profileId;}
function emconUiMasterSilentB(r){return r===ACTIVE_SHIP_RUNTIME?!!emconActive:!!observerC(r).emcon;}
function emconUiEcmLevelB(r){
  if(r===ACTIVE_SHIP_RUNTIME)return ownEcmLevelE();
  const e=prepareElectronicF(r);return e.auto&&(e.noiseRequested||e.deceptionRequested)?'FULL':'OFF';
}
function emconUiEcmCommandB(r,level){
  if(!['OFF','JAM','FULL'].includes(level))return {ok:false,reason:'ECM_LEVEL'};
  if(r===ACTIVE_SHIP_RUNTIME)return ownEcmCommandE(level);
  if(r.role!=='ALLY'||r.faction!=='FRIENDLY')return {ok:false,reason:'FRIENDLY_OWNER_REQUIRED'};
  const on=level!=='OFF';return electronicCommandF(r.entityId,{auto:on,noiseRequested:on,deceptionRequested:on,autoAim:true});
}
function emconUiDetailCommandB(r,command){return emconCommandB(r?.entityId,command,'OPERATOR');}
function emconUiAllSilentB(r){return emconUiMasterSilentB(r)&&emconStateViewB(r).categoryPolicy.ECM==='SILENT';}
function emconAllRadiationMacroB(r){
  if(!r||r!==ACTIVE_SHIP_RUNTIME&&(r.role!=='ALLY'||r.faction!=='FRIENDLY'))return {ok:false,reason:'FRIENDLY_OWNER_REQUIRED'};
  const id=r.entityId,state=emconStateViewB(r),silent=emconUiAllSilentB(r);
  if(!silent){
    const memory={masterSilent:emconUiMasterSilentB(r),ecmPolicy:state.categoryPolicy.ECM,revision:state.revision};
    const detail=emconUiDetailCommandB(r,{category:'ECM',policy:'SILENT'});if(!detail.ok)return detail;
    const master=fleetCommandG(id,{action:'EMCON',enabled:true});
    if(!master.ok){emconUiDetailCommandB(r,{category:'ECM',policy:memory.ecmPolicy});return master;}
    EMCON_B_ALL_RADIATION_MEMORY.set(id,memory);return {ok:true,mode:'SILENT',memory:{...memory}};
  }
  const memory=EMCON_B_ALL_RADIATION_MEMORY.get(id)??{masterSilent:false,ecmPolicy:'RADIATE'};
  const priorPolicy=state.categoryPolicy.ECM,detail=emconUiDetailCommandB(r,{category:'ECM',policy:memory.ecmPolicy});if(!detail.ok)return detail;
  const master=fleetCommandG(id,{action:'EMCON',enabled:memory.masterSilent});if(!master.ok){emconUiDetailCommandB(r,{category:'ECM',policy:priorPolicy});return master;}
  EMCON_B_ALL_RADIATION_MEMORY.delete(id);return {ok:true,mode:'RESTORED',memory:{...memory}};
}
function emconUiChipSnapshotB(){
  const r=emconUiOwnerB(),registry=shipEmitterRegistryA(r),radar=EMCON_B_RADAR_CATEGORIES.filter(category=>registry?.entries?.some(q=>q.category===category)),active=radar.filter(category=>emconCategoryAllowsB(r,category)).length,
    ecm=(registry?.entries??[]).find(q=>q.category==='ECM'),decision=ecm?emconEquipmentDecisionB(r,ecm.id):null,master=emconUiMasterSilentB(r),ecmCode=decision?.emissionActive?'TX':decision?.ecm?.requestActive?'REQ':'OFF';
  return {ownerEntityId:r.entityId,masterSilent:master,activeRadarCategories:active,totalRadarCategories:radar.length,ecmCode,
    text:'M:'+(master?'SIL':'ON')+' C:'+active+'/'+radar.length+'\nECM:'+ecmCode,
    title:emconUiOwnerLabelB(r)+' · RADAR MASTER '+(master?'SILENT':'ACTIVE')+' · 활성 레이더 범주 '+active+'/'+radar.length+' · ECM '+(decision?.emissionActive?'실제 방출':decision?.ecm?.requestActive?'기법 요청 / 방출 없음':'꺼짐')+' · 통신 링크는 별도'};
}
function emconCreatePolicyUiB(){
  const root=document.createElement('section');root.id='mapEmconPolicyB';root.className='map-emcon-policy-b';
  const owner=document.createElement('select');owner.id='mapEmconOwnerB';owner.setAttribute('aria-label','EMCON 조작 함정');
  const summary=document.createElement('small');summary.className='map-emcon-summary-b';const categories=document.createElement('div');categories.className='map-emcon-categories-b';
  const linkNote=document.createElement('small');linkNote.className='map-emcon-link-note-b';linkNote.textContent='통신 링크는 별도 정책이며 레이더 EMCON의 영향을 받지 않음';root.append(owner,summary,categories,linkNote);
  let ownerKey='',registryKey='',rows=new Map();
  owner.addEventListener('change',()=>{fleetSelectG(owner.value);ownerKey='';refresh();});
  function friendlyCommandAllowed(r){return r===ACTIVE_SHIP_RUNTIME||r.role==='ALLY'&&r.faction==='FRIENDLY';}
  function rebuild(r){
    const registry=shipEmitterRegistryA(r),allowed=friendlyCommandAllowed(r);categories.replaceChildren();rows=new Map();
    for(const category of SHIP_EMITTER_CATEGORIES_A){
      const entries=(registry?.entries??[]).filter(q=>q.category===category),box=document.createElement('section');box.className='map-emcon-category-b';box.dataset.emconCategoryB=category;
      const head=document.createElement('div');head.className='map-emcon-category-head-b';const label=document.createElement('strong');label.textContent=EMCON_B_CATEGORY_LABEL[category]??category;
      const button=document.createElement('button');button.type='button';button.id='mapEmconCategoryB_'+category;button.className='ui-button-a';button.disabled=!allowed||entries.length===0;button.addEventListener('click',()=>{const current=emconStateViewB(r).categoryPolicy[category];emconUiDetailCommandB(r,{category,policy:current==='RADIATE'?'SILENT':'RADIATE'});refresh();});head.append(label,button);box.append(head);
      const equipment=[];
      if(!entries.length){const empty=document.createElement('small');empty.textContent='등록 장비 없음';empty.dataset.emconEmptyB=category;box.append(empty);}
      for(const entry of entries){const line=document.createElement('div');line.className='map-emcon-equipment-b';line.dataset.emconEquipmentB=entry.id;const name=document.createElement('span');name.textContent=entry.system??entry.nato??entry.id.replaceAll('_',' ');name.title=entry.id;
        const select=document.createElement('select');select.id='mapEmconEquipmentB_'+entry.id.replace(/[^A-Za-z0-9_-]/g,'_');select.setAttribute('aria-label',entry.id+' 장비 방사 덮어쓰기');for(const [value,text]of [['INHERIT','상속'],['FORCE_RADIATE','강제 방사'],['FORCE_SILENT','강제 침묵']])select.add(new Option(text,value));
        const inactive=entry.installed===false||entry.physicalEmission===false||entry.outputKind==='REGISTERED_INACTIVE';select.disabled=!allowed||inactive;select.addEventListener('change',()=>{emconUiDetailCommandB(r,{equipmentId:entry.id,override:select.value});refresh();});
        const status=document.createElement('small');status.className='map-emcon-equipment-state-b';line.append(name,select,status);box.append(line);equipment.push({entry,select,status});}
      categories.append(box);rows.set(category,{button,equipment,entries});
    }
  }
  function refresh(){
    const members=typeof fleetMembersG==='function'?fleetMembersG():[ACTIVE_SHIP_RUNTIME],selected=emconUiOwnerB(),nextOwnerKey=members.map(r=>r.entityId+':'+r.profileId+':'+r.role).join('|');
    if(nextOwnerKey!==ownerKey){owner.replaceChildren();for(const r of members)owner.add(new Option(emconUiOwnerLabelB(r),r.entityId));ownerKey=nextOwnerKey;}owner.value=selected.entityId;
    const registry=shipEmitterRegistryA(selected),nextRegistryKey=selected.entityId+':'+registry?.registryId+':'+(registry?.entries?.map(q=>q.id).join('|')??'');if(nextRegistryKey!==registryKey){rebuild(selected);registryKey=nextRegistryKey;}
    const state=emconStateViewB(selected),allowed=friendlyCommandAllowed(selected);let active=0,total=0;
    for(const [category,row]of rows){const policy=state.categoryPolicy[category];row.button.textContent=policy==='RADIATE'?'방사 허용':'침묵';row.button.setAttribute('aria-pressed',String(policy==='RADIATE'));row.button.disabled=!allowed||row.entries.length===0;if(EMCON_B_RADAR_CATEGORIES.includes(category)&&row.entries.length){total++;if(emconCategoryAllowsB(selected,category))active++;}
      for(const q of row.equipment){const decision=emconEquipmentDecisionB(selected,q.entry.id);q.select.value=state.equipmentOverride[q.entry.id];q.status.textContent=(decision.emissionActive?'실제 방출':decision.allowed?'방사 대기':'차단')+' · '+(EMCON_B_REASON_LABEL[decision.reason]??decision.reason);if(category==='ECM')q.status.textContent+=' · 기법 '+(decision.ecm?.requestActive?'요청':'없음');}}
    const ecm=(registry?.entries??[]).find(q=>q.category==='ECM'),ecmDecision=ecm?emconEquipmentDecisionB(selected,ecm.id):null;summary.textContent='RADAR MASTER '+(emconUiMasterSilentB(selected)?'SILENT':'ACTIVE')+' · 범주 '+active+'/'+total+' · ECM '+(ecmDecision?.emissionActive?'실제 방출':ecmDecision?.ecm?.requestActive?'요청 / 미방출':'꺼짐');
  }
  function snapshot(){return {ownerEntityId:owner.value,categories:[...rows].map(([category,row])=>({category,policy:row.button.textContent,disabled:row.button.disabled,equipment:row.equipment.map(q=>({id:q.entry.id,override:q.select.value,disabled:q.select.disabled,status:q.status.textContent}))}))};}
  if(!document.getElementById('emconBPolicyStyle')){const style=document.createElement('style');style.id='emconBPolicyStyle';style.textContent=`#mapEmconMenuE{box-sizing:border-box;width:min(350px,calc(100vw - 8px));max-width:min(350px,calc(100vw - 8px));max-height:min(76dvh,620px);overflow:auto}.map-emcon-policy-b{display:flex;flex-direction:column;gap:4px;border-top:1px solid #45606b;border-bottom:1px solid #45606b;padding:4px 0}.map-emcon-policy-b select{box-sizing:border-box;min-height:36px!important;background:#102c3b;color:#e0eef4;border:1px solid #527787;font:11px/1.3 monospace}.map-emcon-categories-b{display:flex;flex-direction:column;gap:3px}.map-emcon-category-b{display:flex;flex-direction:column;gap:2px;padding:3px;border:1px solid #38515b}.map-emcon-category-head-b{display:grid;grid-template-columns:minmax(0,1fr) minmax(86px,auto);align-items:center;gap:4px}.map-emcon-category-head-b button{min-height:36px!important}.map-emcon-equipment-b{display:grid;grid-template-columns:minmax(0,1fr) 96px;gap:2px 4px;align-items:center}.map-emcon-equipment-state-b{grid-column:1/-1;color:#a9c6d1!important}.map-emcon-summary-b{color:#9edfff!important}.map-emcon-link-note-b{color:#d8bd80!important}`;document.head.append(style);}
  refresh();return Object.freeze({root,refresh,snapshot});
}
window.__EMCON_B_UI__=Object.freeze({owner:()=>emconUiOwnerB().entityId,chip:emconUiChipSnapshotB,allRadiation:()=>emconAllRadiationMacroB(emconUiOwnerB()),memory:id=>structuredClone(EMCON_B_ALL_RADIATION_MEMORY.get(id)??null)});
