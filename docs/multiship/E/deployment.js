const MULTISHIP_DEPLOYMENT_LEGACY_SCHEMA_E='AEGIS_DEPLOYMENT_MULTI_SHIP_A_1';
function normalizeDeploymentE(input){return {...input,schema:MULTISHIP_DEPLOYMENT_SCHEMA_A,enemyAircraftEnabled:input.schema===MULTISHIP_DEPLOYMENT_LEGACY_SCHEMA_E&&input.enemyAircraftEnabled==null?true:input.enemyAircraftEnabled};}
function validateDeploymentA(input){
  const errors=[];if(!input||typeof input!=='object'||Array.isArray(input))return {ok:false,errors:['DEPLOYMENT_OBJECT']};
  if(![MULTISHIP_DEPLOYMENT_SCHEMA_A,MULTISHIP_DEPLOYMENT_LEGACY_SCHEMA_E].includes(input.schema))errors.push('DEPLOYMENT_SCHEMA');
  if(!['NONE','HULK'].includes(input.targetShip))errors.push('DEPLOYMENT_TARGET');
  if(input.enemyProfileId!==null&&(typeof input.enemyProfileId!=='string'||!Object.hasOwn(SHIP_PROFILE_REGISTRY,input.enemyProfileId)))errors.push('DEPLOYMENT_ENEMY_PROFILE');
  if(typeof normalizeDeploymentE(input).enemyAircraftEnabled!=='boolean')errors.push('DEPLOYMENT_ENEMY_AIRCRAFT');
  if(Object.keys(input).some(k=>!['schema','targetShip','enemyProfileId','enemyAircraftEnabled'].includes(k)))errors.push('DEPLOYMENT_UNKNOWN_FIELD');
  return {ok:!errors.length,errors};
}
function enemyAircraftSpawnsEnabledE(){return deploymentConfigA().enemyAircraftEnabled===true;}
