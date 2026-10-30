// Scenario state is separate from immutable profiles and sensor knowledge.
const DEPLOYMENT_POLICY_F=Object.freeze({schema:'AEGIS_DEPLOYMENT_MULTI_SHIP_F_1',allyId:'SHIP_SCENARIO_ALLY_F',enemyId:'SHIP_SCENARIO_ENEMY_A',enemyMinM:10000,enemyMaxM:30000});
function normalizeDeploymentE(input){
  const legacy=input.schema!==DEPLOYMENT_POLICY_F.schema;
  return {schema:DEPLOYMENT_POLICY_F.schema,targetShip:input.targetShip,enemyProfileId:input.enemyProfileId,
    allyProfileId:legacy?null:input.allyProfileId,enemyAircraftEnabled:input.schema==='AEGIS_DEPLOYMENT_MULTI_SHIP_A_1'&&input.enemyAircraftEnabled==null?true:input.enemyAircraftEnabled,
    placementSeed:legacy?1831565813:input.placementSeed,allyEmcon:legacy?false:input.allyEmcon,enemyEmcon:legacy?false:input.enemyEmcon};
}
function validateDeploymentA(input){
  const errors=[];
  if(!input||typeof input!=='object'||Array.isArray(input))return {ok:false,errors:['DEPLOYMENT_OBJECT']};
  const legacy=['AEGIS_DEPLOYMENT_MULTI_SHIP_A_1','AEGIS_DEPLOYMENT_MULTI_SHIP_E_1'].includes(input.schema),q=normalizeDeploymentE(input);
  if(!legacy&&input.schema!==DEPLOYMENT_POLICY_F.schema)errors.push('DEPLOYMENT_SCHEMA');
  if(!['NONE','HULK'].includes(q.targetShip))errors.push('DEPLOYMENT_TARGET');
  for(const key of ['enemyProfileId','allyProfileId'])if(q[key]!==null&&(typeof q[key]!=='string'||!Object.hasOwn(SHIP_PROFILE_REGISTRY,q[key])))errors.push('DEPLOYMENT_'+key);
  for(const key of ['enemyAircraftEnabled','allyEmcon','enemyEmcon'])if(typeof q[key]!=='boolean')errors.push('DEPLOYMENT_'+key);
  if(!Number.isSafeInteger(q.placementSeed)||q.placementSeed<0||q.placementSeed>4294967295)errors.push('DEPLOYMENT_SEED');
  const allowed=legacy?['schema','targetShip','enemyProfileId','enemyAircraftEnabled']:['schema','targetShip','enemyProfileId','allyProfileId','enemyAircraftEnabled','placementSeed','allyEmcon','enemyEmcon'];
  if(Object.keys(input).some(k=>!allowed.includes(k)))errors.push('DEPLOYMENT_UNKNOWN_FIELD');
  return {ok:!errors.length,errors};
}
function syncDeploymentUiA(){
  const q=MULTISHIP_DEPLOYMENT_STATE_A.draft;
  for(const root of document.querySelectorAll('[data-deployment-a]')){
    for(const [key,value]of Object.entries({'target-choice':q.targetShip,'enemy-choice':q.enemyProfileId??'NONE','ally-choice':q.allyProfileId??'NONE','enemy-aircraft-choice':q.enemyAircraftEnabled?'ON':'OFF','ally-emcon':q.allyEmcon?'SILENT':'ACTIVE','enemy-emcon':q.enemyEmcon?'SILENT':'ACTIVE'}))root.querySelector('[data-'+key+']').value=value;
  }
}
function mountDeploymentUiA(parent,before=null){
  if(parent.querySelector('[data-deployment-a]'))return;
  const root=document.createElement('fieldset');root.dataset.deploymentA='';root.style.cssText='margin:8px 0 14px;padding:12px;border:1px solid #376277;border-radius:4px;font:13px sans-serif;';
  const select=(key,label,options)=>'<label style="flex:1;min-width:155px">'+label+'<select data-'+key+' aria-label="'+label+'" style="box-sizing:border-box;display:block;width:100%;margin-top:6px;padding:10px;background:#102c3b;color:#e0eef4;border:1px solid #527787">'+options+'</select></label>',none='<option value="NONE">없음</option>',radar='<option value="ACTIVE">탐색 레이더 ON</option><option value="SILENT">EMCON · 레이더 침묵</option>';
  root.innerHTML='<legend>해상 배치</legend><div style="display:flex;flex-wrap:wrap;gap:12px">'+select('target-choice','시험 표적함','<option value="HULK">기존 시험 표적함</option>'+none)+select('ally-choice','아군함',none)+select('enemy-choice','적함',none)+select('ally-emcon','아군 초기 방사',radar)+select('enemy-emcon','적군 초기 방사',radar)+select('enemy-aircraft-choice','적 항공기 스폰','<option value="ON">ON · 생성</option><option value="OFF">OFF · 생성 안 함</option>')+'</div><p style="margin:10px 0 0;color:#a8c5d3;line-height:1.6">아군은 자함 근처, 적군은 10~30km 해상에 배치됩니다. 각 함정은 독립적으로 탐색·방어·전자전 대응을 수행합니다. 적 위치는 탐지된 정보로 확인합니다.</p>';
  for(const key of ['ally-choice','enemy-choice'])for(const p of SHIP_STARTUP_CATALOG){const o=document.createElement('option');o.value=p.id;o.textContent=p.hullNumber+' · '+p.name;root.querySelector('[data-'+key+']').appendChild(o);}
  root.addEventListener('change',()=>{const value=k=>root.querySelector('[data-'+k+']').value;setDeploymentDraftA({...MULTISHIP_DEPLOYMENT_STATE_A.draft,allyProfileId:value('ally-choice')==='NONE'?null:value('ally-choice'),enemyProfileId:value('enemy-choice')==='NONE'?null:value('enemy-choice'),targetShip:value('target-choice'),enemyAircraftEnabled:value('enemy-aircraft-choice')==='ON',allyEmcon:value('ally-emcon')==='SILENT',enemyEmcon:value('enemy-emcon')==='SILENT'});});
  parent.insertBefore(root,before);syncDeploymentUiA();
}
function placeScenarioShipF(r,config,others){
  const nav=r.navigation,origin=ACTIVE_SHIP_RUNTIME.navigation.positionWorld,rng={state:rfSeedWip13A2('PLACEMENT_F:'+config.placementSeed+':'+r.entityId),spare:null};
  let placed=false;
  for(let attempt=0;attempt<192;attempt++){
    let bearing,range;
    if(r.role==='ALLY'){bearing=shipNav.heading+Math.atan2(attempt%2?-350:350,450);range=Math.hypot(450,350)+Math.floor(attempt/2)*200;nav.heading=shipNav.heading;}
    else {bearing=observerRandomC(rng)*TAU;range=DEPLOYMENT_POLICY_F.enemyMinM+observerRandomC(rng)*(DEPLOYMENT_POLICY_F.enemyMaxM-DEPLOYMENT_POLICY_F.enemyMinM);nav.heading=observerRandomC(rng)*TAU;}
    Object.assign(nav.positionWorld,{x:origin.x+metersToWorld(Math.cos(bearing)*range),y:origin.y+metersToWorld(Math.sin(bearing)*range)});
    if(shipTerrainCollisionAhead(0,0,r)||others.some(q=>navalOverlapB(navalFootprintB(r),navalFootprintB(q))))continue;
    placed=true;break;
  }
  if(!placed)throw Error('SCENARIO_F_NO_OPEN_WATER');
  nav.previousPositionWorld={...nav.positionWorld};nav.previousHeadingWorld=nav.heading;nav.vx=mpsToWorldSpeed(nav.speed*Math.cos(nav.heading));nav.vy=mpsToWorldSpeed(nav.speed*Math.sin(nav.heading));
}
function prepareDeploymentA(input){
  const v=validateDeploymentA(input);if(!v.ok)throw Error(v.errors.join(','));const config=normalizeDeploymentE(input),prepared={config,ally:null,enemy:null},placed=[ACTIVE_SHIP_RUNTIME];
  for(const [key,role,id]of [['ally','ALLY',DEPLOYMENT_POLICY_F.allyId],['enemy','ENEMY',DEPLOYMENT_POLICY_F.enemyId]]){
    const pid=config[key+'ProfileId'];if(!pid)continue;
    const r=preparePhysicalShipB(createPreparedShipRuntimeA(SHIP_PROFILE_REGISTRY[pid],{entityId:id,role}));placeScenarioShipF(r,config,placed);r.initialEmconF=config[key+'Emcon'];prepared[key]=r;placed.push(r);
  }
  return prepared;
}
function applyDeploymentA(prepared){
  if(!prepared.config.enemyAircraftEnabled){targetPool.length=0;SPAWN.timer=0;}
  for(const id of [DEPLOYMENT_POLICY_F.allyId,DEPLOYMENT_POLICY_F.enemyId])if(ENGAGEMENT_RUNTIME.ships.has(id))destroyShipRuntime(id);
  for(const r of [prepared.ally,prepared.enemy].filter(Boolean)){ENGAGEMENT_RUNTIME.ships.set(r.entityId,r);activatePhysicalShipB(r);prepareElectronicF(r);}
  MULTISHIP_DEPLOYMENT_STATE_A.draft={...prepared.config};MULTISHIP_DEPLOYMENT_STATE_A.committed={...prepared.config};MULTISHIP_DEPLOYMENT_STATE_A.revision++;
  ENGAGEMENT_RUNTIME.lifecycle={revision:(ENGAGEMENT_RUNTIME.lifecycle.revision||0)+1,lastEvent:'FACTION_FLEET_ACTIVE_F'};syncDeploymentUiA();
}
function restorePreparedPhysicalFleetB(prepared,fleet){
  for(const r of [prepared.ally,prepared.enemy].filter(Boolean)){
    const q=fleet.ships.find(q=>q.entityId===r.entityId);if(!q)continue;
    restoreOnePhysicalFleetF({enemy:r},{ships:[q]});r.restoredElectronicF=q.ew??null;
  }
}
