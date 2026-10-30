// Stage 1/2: author a scenario before sailing; enemy execution is deferred.
const MULTISHIP_DEPLOYMENT_SCHEMA_A='AEGIS_DEPLOYMENT_MULTI_SHIP_A_1';
const MULTISHIP_DEPLOYMENT_DEFAULT_A=Object.freeze({schema:MULTISHIP_DEPLOYMENT_SCHEMA_A,targetShip:'HULK',enemyProfileId:null});
const MULTISHIP_DEPLOYMENT_STATE_A={draft:{...MULTISHIP_DEPLOYMENT_DEFAULT_A},committed:null,revision:0,appliedTarget:null};
function validateDeploymentA(input){
  const errors=[];
  if(!input||typeof input!=='object'||Array.isArray(input))return {ok:false,errors:['DEPLOYMENT_OBJECT']};
  if(input.schema!==MULTISHIP_DEPLOYMENT_SCHEMA_A)errors.push('DEPLOYMENT_SCHEMA');
  if(!['NONE','HULK'].includes(input.targetShip))errors.push('DEPLOYMENT_TARGET');
  if(input.enemyProfileId!==null&&(typeof input.enemyProfileId!=='string'||!Object.hasOwn(SHIP_PROFILE_REGISTRY,input.enemyProfileId)))errors.push('DEPLOYMENT_ENEMY_PROFILE');
  if(Object.keys(input).some(k=>!['schema','targetShip','enemyProfileId'].includes(k)))errors.push('DEPLOYMENT_UNKNOWN_FIELD');
  return {ok:!errors.length,errors};
}
function deploymentConfigA(){return {...(MULTISHIP_DEPLOYMENT_STATE_A.committed??MULTISHIP_DEPLOYMENT_STATE_A.draft)};}
function deploymentSnapshotA(){return {schema:MULTISHIP_DEPLOYMENT_SCHEMA_A,draft:{...MULTISHIP_DEPLOYMENT_STATE_A.draft},committed:MULTISHIP_DEPLOYMENT_STATE_A.committed?{...MULTISHIP_DEPLOYMENT_STATE_A.committed}:null,revision:MULTISHIP_DEPLOYMENT_STATE_A.revision,enemyExecution:'DEFERRED_STAGE_3_PLUS'};}
function setDeploymentDraftA(input){
  const validation=validateDeploymentA(input);if(!validation.ok)return validation;
  if(!['SELECTING','PREPARING'].includes(SHIP_STARTUP_STATE.phase))return {ok:false,errors:['DEPLOYMENT_LOCKED_AFTER_DEPARTURE']};
  MULTISHIP_DEPLOYMENT_STATE_A.draft={schema:input.schema,targetShip:input.targetShip,enemyProfileId:input.enemyProfileId};
  syncDeploymentUiA();return {ok:true,errors:[]};
}
function syncDeploymentUiA(){
  for(const root of document.querySelectorAll('[data-deployment-a]')){
    const q=MULTISHIP_DEPLOYMENT_STATE_A.draft;
    root.querySelector('[data-target-choice]').value=q.targetShip;
    root.querySelector('[data-enemy-choice]').value=q.enemyProfileId??'NONE';
  }
}
function mountDeploymentUiA(parent,before=null){
  if(parent.querySelector('[data-deployment-a]'))return;
  const root=document.createElement('fieldset');root.dataset.deploymentA='';
  root.style.cssText='margin:8px 0 14px;padding:12px;border:1px solid #376277;border-radius:4px;font:13px sans-serif;';
  root.innerHTML='<legend>해상 배치</legend><div style="display:flex;flex-wrap:wrap;gap:12px"><label style="flex:1;min-width:160px">표적함<select data-target-choice aria-label="표적함" style="display:block;width:100%;margin-top:6px;padding:10px;background:#102c3b;color:#e0eef4;border:1px solid #527787"><option value="HULK">기존 시험 표적함</option><option value="NONE">없음</option></select></label><label style="flex:1;min-width:160px">적함 준비<select data-enemy-choice aria-label="적함 준비" style="display:block;width:100%;margin-top:6px;padding:10px;background:#102c3b;color:#e0eef4;border:1px solid #527787"><option value="NONE">없음</option></select></label></div><p style="margin:10px 0 0;color:#a8c5d3;line-height:1.6">적함 선택은 독립 상태를 준비합니다. 실제 해상 배치·항해·교전은 다음 단계에서 적용됩니다.</p>';
  const picker=root.querySelector('[data-enemy-choice]');
  for(const select of root.querySelectorAll('select'))select.style.boxSizing='border-box';
  for(const p of SHIP_STARTUP_CATALOG){const option=document.createElement('option');option.value=p.id;option.textContent=p.hullNumber+' · '+p.name;picker.appendChild(option);}
  root.addEventListener('change',()=>setDeploymentDraftA({schema:MULTISHIP_DEPLOYMENT_SCHEMA_A,targetShip:root.querySelector('[data-target-choice]').value,enemyProfileId:picker.value==='NONE'?null:picker.value}));
  parent.insertBefore(root,before);syncDeploymentUiA();
}
function prepareDeploymentA(config){
  const validation=validateDeploymentA(config);if(!validation.ok)throw Error(validation.errors.join(','));
  const enemy=config.enemyProfileId?createPreparedShipRuntimeA(SHIP_PROFILE_REGISTRY[config.enemyProfileId],{entityId:'SHIP_SCENARIO_ENEMY_A',role:'ENEMY'}):null;
  return {config:{schema:config.schema,targetShip:config.targetShip,enemyProfileId:config.enemyProfileId},enemy};
}
function applyDeploymentA(prepared){
  const old=ENGAGEMENT_RUNTIME.ships.get('SHIP_SCENARIO_ENEMY_A');if(old)destroyShipRuntime(old.entityId);
  if(prepared.enemy){ENGAGEMENT_RUNTIME.ships.set(prepared.enemy.entityId,prepared.enemy);ENGAGEMENT_RUNTIME.lifecycle={revision:(ENGAGEMENT_RUNTIME.lifecycle.revision||0)+1,lastEvent:'SHIP_STATE_BOUND_INACTIVE'};}
  MULTISHIP_DEPLOYMENT_STATE_A.draft={...prepared.config};MULTISHIP_DEPLOYMENT_STATE_A.committed={...prepared.config};MULTISHIP_DEPLOYMENT_STATE_A.revision++;
  syncDeploymentUiA();
}
function validateOperationalDeploymentA(src,_ctx,errors){
  const result=validateDeploymentA(src.deployment);for(const code of result.errors)operationalErrorV48Wip11B(errors,code);
}
window.__AEGIS_DEPLOYMENT_A__=Object.freeze({snapshot:deploymentSnapshotA,validate:validateDeploymentA,setDraft:setDeploymentDraftA});
