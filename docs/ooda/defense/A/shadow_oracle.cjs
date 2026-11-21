#!/usr/bin/env node
'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const { chromium } = require('playwright');

const [productPath, url, outputPath] = process.argv.slice(2);
if (!productPath || !url || !outputPath) {
  console.error('usage: shadow_oracle.cjs PRODUCT URL OUTPUT');
  process.exit(2);
}
const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');
const stable = value => JSON.stringify(value, (_key, item) => item && typeof item === 'object' && !Array.isArray(item)
  ? Object.fromEntries(Object.entries(item).sort(([a], [b]) => a.localeCompare(b))) : item);
function differencePaths(left, right, path='$', out=[]) {
  if (out.length >= 40 || Object.is(left, right)) return out;
  if (!left || !right || typeof left !== 'object' || typeof right !== 'object') { out.push({path,left,right});return out; }
  const keys=new Set([...Object.keys(left),...Object.keys(right)]);for(const key of [...keys].sort()){differencePaths(left[key],right[key],path+'.'+key,out);if(out.length>=40)break;}return out;
}
function deterministicView(scenes) {
  const command=q=>q?{provider:q.provider,ownerEntityId:q.ownerEntityId,inputStep:q.inputStep,inputRevision:q.inputRevision,trackOrder:q.trackOrder,priorityTrackIds:(q.priorities??[]).map(x=>x.trackId),salvoOverrides:q.salvoOverrides,advisoryHold:q.advisoryHold,deferUntilStep:q.deferUntilStep,reason:q.reason}:null;
  const diagnostics=q=>q?{provider:q.provider,mode:q.mode,builds:q.builds,shadowComparisons:q.shadowComparisons,allowedShadowDifferenceCount:q.allowedShadowDifferenceCount,shadowMismatchCount:q.shadowMismatchCount,validationFailures:q.validationFailures,rngMismatchCount:q.rngMismatchCount,truthAuditFailures:q.truthAuditFailures,lastStep:q.lastStep,lastCommand:command(q.lastCommand)}:null;
  return scenes.map(scene=>({result:{profileIndex:scene.result.profileIndex,own:scene.result.own,ally:scene.result.ally,provider:scene.result.provider,fixture:scene.result.fixture,samples:scene.result.samples.map(q=>({step:q.step,ownTrackIds:q.ownInput?.tracks.map(x=>x.trackId),allyTrackIds:q.allyInput?.tracks.map(x=>x.trackId),ownOoda:q.ownOoda,allyOoda:q.allyOoda,ownDiagnostics:diagnostics(q.ownDiagnostics),allyDiagnostics:diagnostics(q.allyDiagnostics),control:{revision:q.control.revision,step:q.control.step,recommendations:q.control.recommendations.map(x=>({...x}))}})),manualHold:scene.result.manualHold,engineSelfTest:scene.result.engineSelfTest,localDefense:scene.result.localDefense},consoleErrors:scene.consoleErrors,pageErrors:scene.pageErrors}));
}

async function runScene(browser, profileIndex) {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const consoleErrors = [], pageErrors = [];
  page.on('console', message => {
    if (message.type() === 'error' && !/favicon\.ico|Failed to load resource.*404/i.test(message.text())) consoleErrors.push(message.text());
  });
  page.on('pageerror', error => pageErrors.push(String(error)));
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 120000 });
  await page.waitForFunction(() => window.__AEGIS_SHIP_STARTUP__?.catalog?.().length >= 2, null, { timeout: 120000 });
  const result = await page.evaluate(async index => {
    const catalog = window.__AEGIS_SHIP_STARTUP__.catalog(), own = catalog[index], ally = catalog[index === 0 ? 1 : 0];
    window.__AEGIS_DEPLOYMENT_A__.setDraft({schema:'AEGIS_DEPLOYMENT_MULTI_SHIP_F_1',targetShip:'NONE',enemyProfileId:null,allyProfileId:ally.id,neutralProfileId:null,enemyAircraftEnabled:false,placementSeed:481802,allyEmcon:false,enemyEmcon:false});
    window.__AEGIS_SHIP_STARTUP__.select(own.id);await window.__AEGIS_STARTUP_PROMISE__;
    const d=window.__NAVAL_SIM_DIAG__,api=window.__DEFENSE_DECISION_A1__;d.setSeed(481802);d.setBattlespaceSeed(481802);if(!window.__WIP125_DIAG__.confirmDeparture())throw Error('departure failed');d.ciwsB1Closure.setPaused(true);
    const ownId=window.__AEGIS_SHIP_STARTUP__.snapshot().entityId,allyId=d.multiShipSnapshotA().ships.find(q=>q.role==='ALLY')?.entityId??null;
    d.tacticalCommandH1(ownId,{enabled:true});d.wip119SetMode('AUTO');if(allyId)d.defenseCommandE(allyId,{mode:'AUTO'});
    const fixture=d.createTerminalAsmFixture({label:'Kh-35U',rangeKm:24,bearingDeg:0,altM:25,speedMps:260}),sampleSteps=[0,12,36,72,120],samples=[];
    const inputSummary=input=>input?{ownerEntityId:input.ownerEntityId,profileId:input.profileId,step:input.step,revision:input.revision,mode:input.mode,tracks:input.tracks.map(q=>({trackId:q.trackId,classification:q.identification?.classification,authority:q.identification?.engagementAuthority,ageS:q.measurement?.ageS,sourceCount:q.network?.sources?.length??0,fcsSource:q.network?.fcsSource}))}:null;
    const diagnosticSummary=q=>q?{provider:q.provider,mode:q.mode,builds:q.builds,shadowComparisons:q.shadowComparisons,allowedShadowDifferenceCount:q.allowedShadowDifferenceCount,shadowMismatchCount:q.shadowMismatchCount,validationFailures:q.validationFailures,rngMismatchCount:q.rngMismatchCount,truthAuditFailures:q.truthAuditFailures,lastStep:q.lastStep,lastCommand:q.lastCommand}:null;
    const controlSummary=q=>({revision:q.revision,step:q.step,recommendations:(q.recommendations??[]).map(r=>({trackId:r.trackId,assessment:r.assessment,weapon:r.weapon,salvo:r.salvo,recommendedRounds:r.recommendedRounds,salvoPolicy:r.salvoPolicy,fireStatus:r.firePlan?.status??null,fireReason:r.firePlan?.reason??null}))});
    for(const targetStep of sampleSteps){const previous=samples.at(-1)?.step??0;if(targetStep>previous)d.stepTicks(targetStep-previous);samples.push({step:targetStep,ownInput:inputSummary(api.input(ownId)),allyInput:inputSummary(api.input(allyId)),ownOoda:api.ooda(ownId),allyOoda:api.ooda(allyId),ownDiagnostics:diagnosticSummary(api.diagnostics(ownId)),allyDiagnostics:diagnosticSummary(api.diagnostics(allyId)),control:controlSummary(d.wip118ControlSnapshot())});}
    d.wip119ResetAutonomy();d.wip119SetMode('MANUAL');d.createTerminalAsmFixture({label:'Kh-35U',rangeKm:15,altM:15,speedMps:260});const beforeManual=d.interceptorAudit().length;d.wip119AutonomyTick(true);d.stepTicks(12);const afterManual=d.interceptorAudit().length;
    const beforeHold=allyId?(d.defenseSnapshotE().ships.find(q=>q.entityId===allyId)?.autonomy?.fireLog?.length??0):null,holdResult=allyId?d.defenseCommandE(allyId,{mode:'HOLD'}):null;d.stepTicks(12);const afterHold=allyId?(d.defenseSnapshotE().ships.find(q=>q.entityId===allyId)?.autonomy?.fireLog?.length??0):null;
    return {profileIndex:index,own:{id:ownId,profileId:own.id},ally:{id:allyId,profileId:ally.id},provider:{provider:api.provider,mode:api.mode,authority:api.authority,truthUsed:api.truthUsed,rngConsumed:api.rngConsumed},fixture,samples,manualHold:{manualMissileDelta:afterManual-beforeManual,holdResult,foreignFireDelta:beforeHold==null||afterHold==null?null:afterHold-beforeHold},engineSelfTest:api.engineSelfTest(),localDefense:d.localDefenseSelfTestH4A()};
  }, profileIndex);
  await page.close();
  return { result, consoleErrors, pageErrors };
}

function sceneChecks(scene) {
  const final=scene.result.samples.at(-1),owners=[['own',final.ownInput,final.ownOoda,final.ownDiagnostics],['ally',final.allyInput,final.allyOoda,final.allyDiagnostics]],commandKeys=['advisoryHold','deferUntilStep','inputRevision','inputStep','ownerEntityId','priorities','provider','reason','salvoOverrides','schema','trackOrder'];
  return {
    shadowProvider:scene.result.provider.provider==='LEGACY_H1'&&scene.result.provider.mode==='SHADOW',
    advisoryOnly:scene.result.provider.authority==='ADVISORY_ONLY'&&!scene.result.provider.truthUsed&&!scene.result.provider.rngConsumed,
    bothOwnersReady:owners.every(([_name,input,ooda,diag])=>input&&ooda?.phase==='READY'&&ooda.diagnostics.evaluated>=1&&diag?.builds>0),
    ownerLocal:owners.every(([_name,input,ooda])=>input.ownerEntityId===ooda.ownerEntityId&&input.profileId===ooda.profileId)&&final.ownOoda.ownerEntityId!==final.allyOoda.ownerEntityId,
    actualStayedLegacy:owners.every(([_name,_input,_ooda,diag])=>diag.lastCommand?.provider==='LEGACY_H1'),
    onlyAllowedDifferences:owners.every(([_name,_input,_ooda,diag])=>(diag.allowedShadowDifferenceCount??0)>0&&diag.shadowMismatchCount===0),
    noValidationRngTruthFallback:owners.every(([_name,_input,ooda,diag])=>diag.validationFailures===0&&diag.rngMismatchCount===0&&diag.truthAuditFailures===0&&ooda.diagnostics.fallback===0&&ooda.diagnostics.rejected===0),
    currentTrackOnly:owners.every(([_name,input,ooda])=>{const ids=new Set(input.tracks.map(q=>q.trackId));return ooda.rows.every(q=>ids.has(q.trackId));}),
    commandSchemaOnly:owners.every(([_name,_input,_ooda,diag])=>Object.keys(diag.lastCommand??{}).sort().join('|')===commandKeys.join('|')),
    manualHoldNoLaunch:scene.result.manualHold.manualMissileDelta===0&&scene.result.manualHold.foreignFireDelta===0&&scene.result.manualHold.holdResult?.ok===true,
    engineSelfTest:scene.result.engineSelfTest.pass===true,
    localCiwsIndependent:scene.result.localDefense.pass===true,
    noBrowserErrors:scene.consoleErrors.length===0&&scene.pageErrors.length===0,
  };
}

(async()=>{
  const product=fs.readFileSync(productPath),executablePath=process.env.AEGIS_CHROMIUM_EXECUTABLE||(fs.existsSync('/usr/bin/chromium')?'/usr/bin/chromium':undefined),browser=await chromium.launch({headless:true,...(executablePath?{executablePath}:{}),args:['--no-sandbox','--disable-dev-shm-usage']});
  try {
    const first=[],second=[];for(const index of [0,1])first.push(await runScene(browser,index));for(const index of [0,1])second.push(await runScene(browser,index));
    const firstDeterministic=deterministicView(first),secondDeterministic=deterministicView(second),checks={scenes:first.every(scene=>Object.values(sceneChecks(scene)).every(Boolean)),repeatExact:stable(firstDeterministic)===stable(secondDeterministic),profiles:first.map(q=>q.result.own.profileId).sort().join('|')==='CG_52_LATE_TICONDEROGA|DDG_119_LATE_FLIGHT_IIA'};
    const payload={schema:'AEGIS_DEFENSE_OODA_A_SHADOW_ORACLE_1',product:{file:productPath.split('/').at(-1),bytes:product.length,sha256:sha256(product)},browser:await browser.version(),playwright:require('playwright/package.json').version,seed:481802,checks,determinismScope:'OODA_COMMAND_DIGEST_QUEUE_AND_DISCRETE_LEGACY_OUTPUTS; diagnostic-only LEGACY_H1 floating priority score is reported but excluded',sceneChecks:first.map(scene=>sceneChecks(scene)),scenes:first,repeatDigest:sha256(Buffer.from(stable(secondDeterministic))),repeatDifferences:differencePaths(first,second)};payload.pass=Object.values(checks).every(Boolean);fs.writeFileSync(outputPath,JSON.stringify(payload,null,2)+'\n');console.log(JSON.stringify({pass:payload.pass,checks,sceneChecks:payload.sceneChecks,repeatDifferences:payload.repeatDifferences}));if(!payload.pass)process.exitCode=1;
  } finally { await browser.close(); }
})().catch(error=>{console.error(error.stack||error);process.exit(1);});
